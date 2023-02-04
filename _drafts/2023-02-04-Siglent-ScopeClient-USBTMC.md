---
layout: post
title: Siglent SDS2304X Remote Control and USBTMC
date:  2023-02-04 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction


# USBTMC


# Linux and USBTMC

There are plenty of Windows tools that allow one to control USBTMC devices, but Linux is a different story.
It took a lot of googling around before I had a clear picture. Here's what I found. 

In general, there are 2 major ways to implement a specific USB class driver under Linux:

* a dedicated class driver that's part of the Linux kernel

    There is a usbtmc driver for the Linux kernel. Or better, there are a bunch of them: 
    a very old one that's not compatible with anything recent, one that was the official one
    until sometime 2018 which didn't have an API version, but let's call it version 1. And
    Version 2, backwards compatible with version 1, that can be found in kernels 4.20 and later.

* a user mode driver that uses generic USB device driver

    User mode drivers are typically implemented by using the `libusb` library.

    A major disadvantage of user mode drivers is that they are specific to a particular application.
    Sigrok is a good example of an application that has [its own USBTMC user mode driver](https://sigrok.org/gitweb/?p=libsigrok.git;a=blob;f=src/scpi/scpi_usbtmc_libusb.c).

A library like PyVISA, which hides the details of all kinds of interfaces, can use either the kernel driver
or a [user mode driver](https://github.com/pyvisa/pyvisa-py/blob/master/pyvisa-py/protocols/usbtmc.py).

# The Linux USBTMC Kernel Drivers

When you google for USBTMC kernel drivers, you can find articles and source code, but very often things
will just not work.

A good example is the ["USBTMC Kernel Driver Documentation"](https://www.keysight.com/upload/cmc_upload/All/usbtmc.htm?&cc=US&lc=eng) 
article on the Keysight website. It's the number one result for a "linux usbtmc" search on Google, yet
the information in it is almost completely obsolete. 
The most basic example works, but the moment IOCTL calls or usbtmc specific struct come into play, the code 
doesn't compile. It turns out that this article is about a kernel driver that was never part of the Linux 
kernel, but one that was[^2] downloadable from the Agilent (now Keysight) website. 

[^2]: "... *was* downloadable ..." because that the link to that code is dead.

There are 2 USBTMC drivers that are officially part of the Linux kernel: version 1 (all kernels before 4.20),
and version 2 (everything 4.20 and later). Version 2 is backwards compatible with version 1.

The most important differences:

* Version 1 has a fixed 5s timeout. Version 2 defaults to 5s, but the timeout is programmable.

    This is important for my Siglent scope because request for waveforms larger than 2.8M samples
    require a larger than 5s preparation time.

* Internal buffer of 2048 vs 4096 bytes

    Large USB bulk read requests get split up into smaller request with a size of this buffer.
    In theory, this is something that's entirely hidden from the user (who can issue read request
    for pretty much any size), but it turns out that bugs in the Siglent USBTMC USB device driver 
    result complete hang of this driver when reads are issued that are almost the size of this
    internal buffer size.
* More efficient read transfers
* Support for USBTMC-USB488 features
* Expanded support for the IVI library 
* A way to query the kernel API version 

    The original driver didn't support a way to detect the driver version.

# Linux, USBTMC, and the Siglent SDS2304X

Once I figured out that my Siglent oscilloscope only supports VXI-11 and not TCP/IP sockets or telnet,
controlling via Ethernet was relatively painless.

Getting it to work using USBTMC was a different story.

I first tested it on Windows 10, with the [National Instruments NI-VISA driver](https://www.ni.com/en-us/support/downloads/drivers/download.ni-visa.html#346210)
and Siglent's [EasyScopeX](https://siglentna.com/service-and-support/firmware-software/digital-oscilloscopes/), and
it worked fine.

However, I ran into issues with both using the usbtmc kernel driver (version 1) directly and with
PyVisa.

Eventually, I had to turn to Wireshark to observe exactly what was going on.

Let's first look at my test program:

```c
/* usbtmc_trivial.c */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>

// The scope has a maximum waveform capture size of 140M.
int buffer_size = 150000000;
char *buffer;

int query(int file, char *cmd)
{
    printf("Cmd: %s\n", cmd);
    write(file,cmd,strlen(cmd));

    int bytes_fetched=read(file,buffer,buffer_size);
    printf("Size: %d\n",bytes_fetched);
    buffer[bytes_fetched]=0;
    printf("Response:\n%s\n",buffer);

    return bytes_fetched;
}

int main(int argc, char **argv)
{
    buffer = (char *)malloc(buffer_size);

    int tmc_file=open("/dev/usbtmc0",O_RDWR);
    if(tmc_file>0)
    {
        query(tmc_file, "*IDN?");
        query(tmc_file, "C1:WF? DESC");
    }
}
```

When you run this, everything is great:
```
tom@thinkcenter:~/projects/siglent_remote/usbtmc$ sudo ./usbtmc_trivial 
Cmd: *IDN?
Size: 49
Response:
*IDN SIGLENT,SDS2304X,SDS2Xxxxxxxxxx,1.2.2.2 R19

Cmd: C1:WF? DESC
Size: 369
Response:
C1:WF DESC,#9000000346WAVEDESC
```

The `WF? DESC` comment returns a struct with all information about the waveform that was captured,
but not the waveform itself.

To do that, we need to add the following line to the case:

```c
        ...
        query(tmc_file, "C1:WF? DESC");
        query(tmc_file, "C1:WF? DAT2");             // Fetch actual waveform data
        ...
```

Run this, and here's the result:
```
tom@thinkcenter:~/projects/siglent_remote/usbtmc$ sudo ./usbtmc_trivial_hang 
Cmd: *IDN?
Size: 49
Response:
*IDN SIGLENT,SDS2304X,SDS2Xxxxxxxxxx,1.2.2.2 R19

Cmd: C1:WF? DESC
Size: 369
Response:
C1:WF DESC,#9000000346WAVEDESC

Cmd: C1:WF? DAT2
Size: -1
Response:
```

The `WF? DAT2` request timed out. But it gets better: if you now issue any USBTMC query to the scope, every single
request time out as well. And it will stay that way until your power cycle the scope! 

I checked out the behavior with [Wireshark](https://www.wireshark.org/) and found the Linux USBTMC driver splits
up the data request into request with a maximum size of 2048 (in line with 2048 buffer that gets allocated
in the USBTMC driver), and that USBTMC driver inserts messages for each additonal chunk. Windows doesn't have
that behavior.

I found 2 ways around that:

* Split up the waveform into chunks of less than 2048 bytes by using the `WFSU` command.

    This requires 2 SCPI calls per fetch of ~2000 bytes, which adds a considerable amount 
    of overhead.

* Issue consecutive reads to the TMC driver where each read request 2032 bytes or less.

    Why 2032 and not 2048? Beats me! Requesting 2033 is sufficient to trigger then denial
    of service behavior mentioned earlier!

```
XXX screenshot.
```

Here's the version that issues a bunch of reads with a size of 2032:

```c
void query(int file, char *cmd)
{
    printf("Cmd: %s\n", cmd);
    write(file,cmd,strlen(cmd));

    int max_bytes_per_req = 2032;
    int i = 0;
    int bytes_fetched, bytes_requested;
    do{
        bytes_requested = MIN(max_bytes_per_req, buffer_size-i);
        bytes_fetched = read(file, buffer+i, bytes_requested);
        printf("Size: %d\n",bytes_fetched);
        i += bytes_fetched;
    } while(bytes_fetched == bytes_requested);

    buffer[i]=0;
    printf("Response:\n%s\n",buffer);
}
```

```
tom@thinkcenter:~/projects/siglent_remote/usbtmc$ sudo ./usbtmc_multiple_reads 
Cmd: *IDN?
Size: 49
Response:
*IDN SIGLENT,SDS2304X,SDS2Xxxxxxxxxx,1.2.2.2 R19

Cmd: C1:WF? DESC
Size: 369
Response:
C1:WF DESC,#9000000346WAVEDESC
Cmd: C1:WF? DAT2
Size: 2032
Size: 2032
Size: 2032
Size: 2032
Size: 2032
Size: 2032
Size: 1832
Response:
C1:WF DAT2,#9000014000�
```

# Siglent udev rules

This is the rule that made it work for me. Change "tom" to your own user name...

```
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="f4ec", ATTRS{idProduct}=="ee3a", OWNER="tom", MODE="0660"
```

# Update Ubuntu 18.04 to newer kernel

* upgrade to later kernel: https://ubuntu.com/kernel/lifecycle

```
# This is the recommend way to upgrade. But after this, mouse and keyboard didn't work
# anymore
sudo apt-get install --install-recommends linux-generic-hwe-18.04 xserver-xorg-hwe-18.04 
# This solved the mouse and keyboard issue...
sudo apt-get install xserver-xorg-input-all
```

* Compile on Ubuntu 18.04.
    * Does not compile with 16.04.
* Change source code to point to local shaders in ./src/glscopeclient/main.c: ...chdir...
*

# Communication Standards for Test and Measurement Equipment

* LXI

    Lan eXtensions for Instrumentation

    Most LXI instruments use either VXI-11 or HiSLIP to communicate.

    * [List of LXI Ports, Protocols, and Services](https://www.lxistandard.org/About/LXI-Protocols.aspx)
    * [LXI Standard Revision 1.0](https://www.lxistandard.org/Documents/Specifications/LXI_Revision_1_0.pdf)

* PortMap
    * Port 111: RPC portmapper. PyVisa code: /home/tom/.local/lib/python3.7/site-packages/pyvisa-py/protocols/rpc.py

        [Remote Procedure Call and the portmapper daemon](http://ibgwww.colorado.edu/~lessem/psyc5112/usail/network/services/portmapper.html) :

        "It maps RPC program numbers to the TCP/IP ports on which their servers are listening. When an RPC server starts, it picks an available port, 
        and then registers that port and what RPC program numbers it will serve with the portmapper daemon. When a client program needs to access a 
        service, it first queries the portmapper on the RPC server's host which reports the TCP and UDP port on which the server is listening, and then 
        it contacts that port to request its service."

    * [portmap Protocol](https://docs.oracle.com/cd/E19683-01/816-1435/6m7rrfnab/index.html)
    * [RPC manpage](https://docs.oracle.com/cd/E19620-01/805-3175/6j31emp62/index.html)
    * [Linux Journal - Remote Procedure Calls](https://www.linuxjournal.com/article/2204)
    * [Siglent SDS1004X-E Bode Plot](https://github.com/4x1md/sds1004x_bode/blob/ec73af7c59d52f662f2d918d9a1239f6f69afae8/sds1004x_bode/awg_server.py#L124)

        This implements a VXI-11 *server* instead of a client.

        The goal is to fake a Siglent waveform generator.

    * Structure:

- SCPILxiTransport : public SCPITransport       (Similar to SCPISocketTransport)

```

/home/tom/.local/lib/python3.7/site-packages/vxi11/rpc.py: TCPClinet.__init__:

    calls pmap.get_port

/home/tom/.local/lib/python3.7/site-packages/vxi11/rpc.py: TCPClinet.get_port:

    mapping parameters: (prog = 395183, vers = 1, IPPROTO_TCP:6, 0)

    Per VXI11 spec: Core Channel = RPC program number 395183 / 0x607af, version 1, TCP

/home/tom/.local/lib/python3.7/site-packages/vxi11/rpc.py: make_call:
    Packs all RPC parameters 
        First default parameters (start_call)
        Then specific parameters (args)
    Does the RPC call
    Unpacks the parameters
    result is 9009: port number
```

    * [Discussion about an RPC VXI-11 call with C code](https://forums.ni.com/t5/Instrument-Control-GPIB-Serial/Does-VISA-have-VXI-11-Server-implement-to-serve-the-interrupt/td-p/546919?profile.language=en)
    * [VXI11 Ethernet Protocol for Linux](http://optics.eee.nottingham.ac.uk/vxi11/)

        * Code also on GitHub: https://github.com/applied-optics/vxi11
        * Lots of VXI-11 information here, but not about portmap

    * [VXI-11 RPC Programming Guide for the 8065 - An Introduction to RPC Programming](https://www.icselect.com/pdfs/ab80_3.pdf)

    


* HiSLIP

    [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol)

    More modern and faster alternative for VXI-11.

* USBTMC

    [USB Test and Measurement Class](https://sigrok.org/wiki/USBTMC).

    USB device class specification for measurement equipement.

* VISA

    [Virtual Instrument Software Architcture](https://en.wikipedia.org/wiki/Virtual_instrument_software_architecture).

    Generic software API to connect to instruments, using protocols like VXI-11, HiSLIP, USBTMC.

* IEEE 488.1 / GPIB

    Communication standard for T&M equipment that goes all the way back to the late 1960s.

    For a long time, this was *the* interface that could be found on pretty much all equipment, but it has
    since been replaced by USB and Ethernet.

* IEEE 488.2

    Specifies a standard command syntax to test and measurement equipment.

* SCPI ('skippy')

    [Standard Commands for Programmable Instruments](https://en.wikipedia.org/wiki/Standard_Commands_for_Programmable_Instruments).

    A set of standard commands for test and measurement equipment that uses the IEEE 488.2 syntax.

* VICP

    LeCroy Versatile Instrument Control Protocol

    [LAB_WM827 - Understanding VICP and the VICP Passport](https://teledynelecroy.com/doc/understanding-vicp-and-the-vicp-passport)

    Uses TCP/IP port 1861

    Seems to be similar to SCPI, but proprietary.
    
    

So the overall communications stack looks like this:

There are standardized commands that are understood by all devices due to SCPI. The syntax of these commands follows the
IEE 488.2 standards. The commands are issued by a program through the VISA API. The VISA API can work with pretty much
any low level communication protocol (VX-11/HiSLIP/USBTMC/...). These low level protocols sit on top of generic communication
standards such as TCP/IP, USB, GPIB etc.

# Siglent

All Siglent scopes are using SCPI commands. However, it seems like different Siglnet scope support different low-level transport protocols.

* SDS 2304X

    My SDS 2304X definitely supports VXI-11 over TCP/IP. It uses ports 111 and ports 9009. 
    (See [here](https://www.eevblog.com/forum/testgear/siglent-sds1000x-how-to-make-direct-ethernet-connection/msg1650191/#msg1650191).

    It seems to go as follows: a request to port 111 (portmapper) maps an RPC program number to TCP/IP port 9009 as a VXI-11 compatible port.

    * [Siglent - Programming Example: Using VXI11 (LXI) and Python for LAN control without sockets](https://int.siglent.com/resource-detail/10/)
    

* SDS 1104X-E

    In [this eevblog thread](https://www.eevblog.com/forum/testgear/siglent-sds1000x-how-to-make-direct-ethernet-connection/msg1648898/#msg1648898),
    the way to connect to an SDS 1104X-E is to telnet to port 5024. This doesn't work on the SDS 2304X.

    It uses standard TCP/IP sockets without a VXI-11 layer. You can use telnet with this.

    * [Siglent - Verification of a LAN connection using Telnet](https://int.siglent.com/resource-detail/13/)
    * [Code Example on Siglent website](https://siglentna.com/application-note/python-sdg-x-basics-lan/)


# VISA

VISA is the most generic API, so let's use that one.

# Github Repo

https://github.com/tomverbeure/siglent_remote

# Connecting with Python using USB

```
pip3 install python-usbtmc
```

(See http://alexforencich.com/wiki/en/python-usbtmc/readme)


Resources:

* [Connection with Python and VXI11](https://siglentna.com/application-note/programming-example-vxi11-python-lan/)
* [VXI-11 Specification](https://www.vxibus.org/specifications.html)
* [Siglent Remote Control Manual](https://siglentna.com/USA_website_2014/Documents/Program_Material/SIGLENT_Digital_Oscilloscopes_Remote%20Control%20Manual.pdf)
* [PyVisa](https://pyvisa.readthedocs.io/en/1.8/index.html)
* [Linux USBTMC Kernel driver 4.19](https://github.com/torvalds/linux/blob/v4.19/drivers/usb/class/usbtmc.c)
* [Linux USBTMC Kernel driver 4.20](https://github.com/torvalds/linux/blob/v4.20/drivers/usb/class/usbtmc.c)
* [High Speed LAN Instrument Protocol](https://en.wikipedia.org/wiki/High_Speed_LAN_Instrument_Protocol)



