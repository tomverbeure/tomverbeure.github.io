---
layout: post
title: Write Your Own C and Python Clients for the Intel JTAG UART
date:  2021-05-08 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my previous blog post](/2021/05/02/Intel-JTAG-UART.html), I wrote about Intel's JTAG UART, an important
component of my set of debugging tools, and how to integrate it in your own Verilog code, outside of Intel's 
Platform Designer.

I also [mentioned](/2021/05/02/Intel-JTAG-UART.html#communicating-to-the-jtag-uart-with-a-script) how it's 
a pain to communicate with the JTAG UART with anything other than nios2-terminal.

After publishing that blog post, somebody on Reddit offered some very interesting pointers to a
solution: the Quartus tools are using shared libraries (there's 862 of them in the Quartus 20.1 installation!),
and 2 of them are of particular interest: `libjtag_client.so` is a large library that's used for all
interactions with the Quartus `jtagd` daemon, and `libjtag_atlantic.so`, a much smaller library, is layered
on top of `jtag_client` and handles all the JTAG UART specifics.

You can find these shared librares in the `$QUARTUS_ROOTDIR/linux64` directory:

![Quartus JTAG shared libraries](/assets/jtag_uart/jtag_shared_libraries.png)

With a little bit of effort, you can use these libraries for yourself and let Intel's code do
all the hard work.

# How to Use an Unknown Shared Library

*Skip ahead to the next section if you're only interested in the final result.*

If you ever find yourself in the position of needing to use a shared library without having any source
code or include file at hand, you'll have to do some amount of reverse engineering but you can get
a huge headstart by just dumping the contents of all its publicly advertised symbols, functions and 
variables.

The `nm` command does that for you:

```sh
nm libjtag_atlantic.so | c++filt
```

`c++filt` takes in the mangled symbol names and converts them to something that's almost ready to be
used as a C `#include` header.

Here's a partial extract of the result:

```
...
000000000000259a T jtagatlantic_read(JTAGATLANTIC*, char*, unsigned int)
                 U aji_access_overlay(AJI_OPEN*, unsigned int, unsigned int*)
                 U aji_get_checkpoint(AJI_OPEN*, unsigned int*)
                 U aji_get_error_info()
                 U aji_set_checkpoint(AJI_OPEN*, unsigned int)
0000000000001fab T jtagatlantic_close(JTAGATLANTIC*)
0000000000002456 T jtagatlantic_flush(JTAGATLANTIC*)
00000000000023f6 T jtagatlantic_write(JTAGATLANTIC*, char const*, unsigned int)
                 U aji_access_dr_repeat(AJI_OPEN*, unsigned int, unsigned int, unsigned int, unsigned int, unsigned char const*, unsigned int, unsigned int, unsigned char*, unsigned char const*, unsigned char const*, unsigned char const*, unsigned char const*, unsigned int)
0000000000001b15 t lookup_cable_warning(char const*, AJI_CHAIN*)
0000000000002326 T jtagatlantic_get_info(JTAGATLANTIC*, char const**, int*, int*)
0000000000001be7 T jtagatlantic_get_error(char const**)
000000000000249d T jtagatlantic_wait_open(JTAGATLANTIC*)
                 U aji_get_watch_triggered(AJI_OPEN*, bool*)
00000000000039f5 T jtagatlantic_scan_thread(JTAGATLANTIC*)
0000000000001c02 T jtagatlantic_cable_warning(JTAGATLANTIC*)
0000000000001bfd T jtagatlantic_is_setup_done(JTAGATLANTIC*)
0000000000001c06 T jtagatlantic_bytes_available(JTAGATLANTIC*)
                 U aji_lock(AJI_OPEN*, unsigned int, AJI_PACK_STYLE)
                 U aji_flush(AJI_OPEN*)
                 U operator delete[](void*)
                 U operator delete(void*)
00000000000056fc b last_error
0000000000005698 d default_lock
0000000000001ab0 t GetTickCount()
0000000000005690 d last_error_info
0000000000003ab0 r jtagatlantic_claims
00000000000025bc t JTAGATLANTIC::queue_scan(JTAGATLANTIC::SCANBATCH&, unsigned int, unsigned int)
0000000000002cca t JTAGATLANTIC::test_speed(unsigned int, unsigned int)
0000000000002910 t JTAGATLANTIC::finish_scan(JTAGATLANTIC::SCANBATCH&, bool)
00000000000030d8 t JTAGATLANTIC::set_overlay(JTAGATLANTIC::INSTR)
00000000000024ac t JTAGATLANTIC::cable_warning()
000000000000353e t JTAGATLANTIC::calc_poll_rate()
0000000000003128 t JTAGATLANTIC::setup_hardware()
00000000000035e8 t JTAGATLANTIC::enable_watching(unsigned int)
```

In front of the symbols, there's also the address (we don't care about that), and a symbol type.

`t` and `T` are symbols that are located in the `.text` section of the library, and they are almost
always functions or class methods. According to the `nm` manpage, a lowercase symbol signifies a local symbol, while
uppercase is global. 

`U` symbols are undefined. The linker will need to resolve them by including other libraries. 
In our case, that library will be `jtag_client`. A quick check shows that the `U` symbols in `jtag_client`
are all functions of the C standard library, so, thankfully, the dependency list stops there.

I don't know the reason behind it, but `T` seems to be used for ordinary functions, while `t` is used 
for C++ class methods. 

*The functions are still using C++-style name mangling though, so you need to call them as C++ functions!*

Let's not bother with the methods. Here are all the functions:

```sh
nm libjtag_atlantic.so | c++filt | grep " T "
```

```
0000000000003a28 T _fini
00000000000016b0 T _init
00000000000022ef T jtagatlantic_open(char const*, int, int, char const*)
0000000000001fc4 T jtagatlantic_open(char const*, int, int, char const*, LOCK_HANDLER*)
000000000000259a T jtagatlantic_read(JTAGATLANTIC*, char*, unsigned int)
0000000000001fab T jtagatlantic_close(JTAGATLANTIC*)
0000000000002456 T jtagatlantic_flush(JTAGATLANTIC*)
00000000000023f6 T jtagatlantic_write(JTAGATLANTIC*, char const*, unsigned int)
0000000000002326 T jtagatlantic_get_info(JTAGATLANTIC*, char const**, int*, int*)
0000000000001be7 T jtagatlantic_get_error(char const**)
000000000000249d T jtagatlantic_wait_open(JTAGATLANTIC*)
00000000000039f5 T jtagatlantic_scan_thread(JTAGATLANTIC*)
0000000000001c02 T jtagatlantic_cable_warning(JTAGATLANTIC*)
0000000000001bfd T jtagatlantic_is_setup_done(JTAGATLANTIC*)
0000000000001c06 T jtagatlantic_bytes_available(JTAGATLANTIC*)
```

It's not defined separately in the `nm` list, but `JTAGATLANTIC*` is a pointer to a struct with internal
information. You can treat it as a handle without the need to know anything more about it. 

*On Windows, `dumpbin /exports jtag_atlantic.dll` will give you a similar result.*

To use the functions above in your own code, you must figure out the meaning of the function call 
parameters. It wouldn't be very hard to do, but it's even easier when others have already
done it before you! Check out [`jtag_atlantic.h`](https://github.com/tomverbeure/alterajtaguart/blob/master/software/jtag_atlantic.h)
from the [`thotypous/alterajtaguart`](https://github.com/thotypous/alterajtaguart) project on GitHub:

```c
#ifndef _JTAGATLANTIC_H
#define _JTAGATLANTIC_H

/* For the library user, the JTAGATLANTIC is an opaque object. */
struct JTAGATLANTIC;

/* jtagatlantic_open: Open a JTAG Atlantic UART.
 * Parameters:
 *   cable:    Identifies the USB Blaster connected to the device (e.g. "USB-Blaster [3-2]").
 *             If NULL, the library chooses at will.
 *   device:   The number of the device inside the JTAG chain, starting from 1 for the first device.
 *             If -1, the library chooses at will.
 *   instance: The instance number of the JTAG Atlantic inside the device.
 *             If -1, the library chooses at will.
 * Returns:
 *   Pointer to JTAGATLANTIC instance.
 */
JTAGATLANTIC *jtagatlantic_open(char const *cable, int device, int instance, char const *progname);

/* jtagatlantic_get_info: Get information about the UART to which we have actually connected.
 * Parameters:
 *   atlantic: The JTAGATLANTIC.
 *   cable:    Pointer to a variable which will receive a pointer to the cable name.
 *             Memory is managed by the library, do not free the received pointer.
 *   device:   Pointer to an integer which will receive the device number.
 *   instance: Pointer to an integer which will receive the instance number.
 *   progname: Name of your program (used to inform a lock on the UART).
 */
void jtagatlantic_get_info(JTAGATLANTIC *atlantic, char const **cable, int *device, int *instance);

...
```

# A C Program that Talks to My JTAG UART Example

With `jtag_atlantic.h` in place, creating a program to talk to my design example becomes easy. 

This is a minimum program to send an 'r' to my JTAG UART (to reverse the LED toggle direction)
and print out all the replies:

```c
void main(int argc, char **argv)
{
    JTAGATLANTIC *atlantic = jtagatlantic_open(NULL, -1, -1, argv[0]);
    jtagatlantic_write(atlantic, "r", 1);
    while(1) {
        int buf_len = jtagatlantic_read(atlantic, buf, sizeof(buf));
        if(buf_len < 0)
            break;
        fwrite(buf, buf_len, 1, stdout);
        usleep(10000);
    }
    jtagatlantic_close(atlantic);
}
```

My final example, [`jtag_uart_send_cmd.c`](https://github.com/tomverbeure/jtag_uart_example/blob/master/c_client/jtag_uart_send_cmd.cpp),
is based on the [code in the `alterajtaguart` project](https://github.com/tomverbeure/alterajtaguart/tree/master/software),
but I added the ability to specify on the command line which USB cable, device, and instance number to use, and which string to
send to the JTAG UART.

Here I send `hr` to my design, for 'help' and 'reverse LEDs':

```sh
./jtag_uart_send_cmd hr
Connected to cable 'Arrow MAX 10 DECA [1-12.3]', device 1, instance 0

Unplug the cable or press ^C to stop.

Sending command: 'hr'.
2 character(s) sent to JTAG UART.
Command: h
r:     reverse LED toggle sequence

Command: r
Reversing LED sequence...
^CMakefile:15: recipe for target 'run' failed
make: *** [run] Interrupt
```

# A JTAG UART Python Package

It's a waste of time to write low performance tooling like this in C, so I created 
the [`intel_jtag_uart` Python module](https://github.com/tomverbeure/intel_jtag_uart)
and went the extra mile to package it as [my first project on PyPi](https://pypi.org/project/intel-jtag-uart/).

Installing the package is as easy as:

```sh
pip3 install intel-jtag-uart
```

Communicating with the JTAG UART goes as follows:

```python
#! /usr/bin/env python3
import time
import intel_jtag_uart

try:
    ju = intel_jtag_uart.intel_jtag_uart()

except Exception as e:
    print(e)
    sys.exit(0)

ju.write(b'r')
time.sleep(1)
print("read: ", ju.read())
```

# Final Words

A few years ago, I had to extract a large amount of debug data out of an FPGA, but didn't have the tools
to do this over JTAG UART. I ended up exfiltrating the data by bitbanging an SPI protocol on some 
GPIO pins, and recording the result with a Saleae logic analyzer.

I could have saved myself a lot of time if Intel had provided a convenient API to script things
with a language other than TCL. This Python package fills that gap.

What's frustrating is that the shared library technique described here isn't new: 
[this discussion on the official Altera forum](https://community.intel.com/t5/Programmable-Devices/DE1-board-to-PC-communication/td-p/31708?profile.language=en)
dates from 2009! But one way or the other, I was never able to Google myself towards the
right solution.

With a little bit of luck, this blog post puts an end to that.

# References


* [Bypass-nios2-terminal](https://github.com/hyliu1989/Bypass-nios2-terminal)

    Python Jypiter workbook about how to jtag_atlantic with Python

* [DE1 board to PC communication](https://community.intel.com/t5/Programmable-Devices/DE1-board-to-PC-communication/td-p/31708?profile.language=en)

    Discussion on Intel message board about jtag_atlantic. Many broken links, but some attachment work.

* [thotypous alterajtaguart](https://github.com/thotypous/alterajtaguart)

    Primary purpose of this project is to implement a JTAG UART in BlueSpec, but it also has a working example
    of using jtag_atlantic.

* [High Speed Image Download Demo](https://community.intel.com/t5/FPGA-Wiki/High-Speed-Image-Download-Demo/ta-p/735576)
* [How to Create a Python Wrapper for C/C++ Shared Libraries](https://betterprogramming.pub/how-to-create-a-python-wrapper-for-c-c-shared-libraries-35ffefcfc10b)
* [`intel-jtag-uart` package on PyPi](https://pypi.org/project/intel-jtag-uart/)
* [`intel_jtag_uart` repo on GitHub](https://github.com/tomverbeure/intel_jtag_uart)
* [`jtag_uart_example` repo on GitHub](https://github.com/tomverbeure/jtag_uart_example)

