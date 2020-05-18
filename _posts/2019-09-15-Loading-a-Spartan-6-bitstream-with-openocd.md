---
layout: post
title: Loading a Xilinx Spartan 6 bitstream with OpenOCD
date:   2019-09-15 00:00:00 -1000
categories:
---

*This post is just the sequence that I use to get from nowhere to a JTAG dongle doing 
something useful. I always forget the details, so this is more for later personal
use than anything else.*

* TOC
{:toc}

# Goal 

I have the following JTAG dongles: 

* A Xilinx JTAG Programming USB cable clone
* A higher-end Altera USB Blaster clone
* A end dirt cheap low-end Altera USB Blaster clone
* A TerasIC Altera USB Blaster clone

Commerical tools like Vivado, Quartus and even ISE are usually pretty good at figuring
out which driver to apply, but when you're using OpenOCD, you're on your own.

In this exercise, I'm trying to get a bitstream loaded into my [RV901T](https://github.com/q3k/chubby75)
FPGA board. It uses a Xilinx Spartan-6 XC6SLX16, and OpenOCD has support for loading
bitstreams (in `.bit` format) through JTAG straight into the FPGA.

In other words: you don't need the Xilinx iMPACT tool to do so!

# Xilinx Compatible JTAG Dongle

On Linux, I get the USB details of the Xilinx JTAG cable as follows:

```bash
> lsusb

Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 045e:07a5 Microsoft Corp. Wireless Receiver 1461C
Bus 001 Device 002: ID 8087:0a2b Intel Corp. 
Bus 001 Device 006: ID 0403:6014 Future Technology Devices International, Ltd FT232H Single HS USB-UART/FIFO IC
```

The devices I care about is the Future Technology Devices International (FTDI) one.

`0403:6014` is the vendor_id/device_id combo of our device. Chances are that OpenOCD already knows about this device
and that there is a custom script for it that configures everything correctly.

I have OpenOCD installed under `/opt/openocd`, so let's see if we can find the right interface script for our device:

```bash
> cd /opt/openocd/share/openocd/scripts/interface
> grep 6014 *.cfg

grep: ftdi: Is a directory

> grep 6014 */*.cfg

ftdi/digilent-hs2.cfg:ftdi_vid_pid 0x0403 0x6014
ftdi/digilent_jtag_hs3.cfg:ftdi_vid_pid 0x0403 0x6014
ftdi/digilent_jtag_smt2.cfg:ftdi_vid_pid 0x0403 0x6014
ftdi/digilent_jtag_smt2_nc.cfg:ftdi_vid_pid 0x0403 0x6014
ftdi/ft232h-module-swd.cfg:ftdi_vid_pid 0x0403 0x6014
ftdi/um232h.cfg:ftdi_vid_pid 0x0403 0x6014
```

Good! There's a bunch of options!

Looking closer, my device says "Model: JTAG SMT2", so let's use `ftdi/digilent_jtag_smt2.cfg`

Device permissions are something I always have problems with. To bypass that, I simply run things as root:

```bash
> sudo /opt/openocd/bin/openocd -f /opt/openocd/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg

Open On-Chip Debugger 0.10.0+dev-00410-gf0767a3 (2018-05-15-21:46)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Error: An adapter speed is not selected in the init script. Insert a call to adapter_khz or jtag_rclk to proceed.
```

Apparently, an JTAG clock speed must always be specified for this dongle. Let's do just that. 

We can do this via our own custom configuration script, or we can simply add this command directly on the command line:

```bash
> sudo /opt/openocd/bin/openocd -f /opt/openocd/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg \
             -c "adapter_khz 1000"

Open On-Chip Debugger 0.10.0+dev-00410-gf0767a3 (2018-05-15-21:46)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
adapter speed: 1000 kHz
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : clock speed 1000 kHz
Error: session transport was not selected. Use 'transport select <transport>'
Error: Transports available:
Error: jtag
Error: swd
in procedure 'init' 
in procedure 'ocd_bouncer'
```

A Xilinx Spartan-6 FPGA has a JTAG port:

```bash
> sudo /opt/openocd/bin/openocd -f /opt/openocd/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg \ 
             -c "adapter_khz 1000; transport select jtag"

Open On-Chip Debugger 0.10.0+dev-00410-gf0767a3 (2018-05-15-21:46)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
adapter speed: 1000 kHz
jtag
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : clock speed 1000 kHz
Warn : There are no enabled taps.  AUTO PROBING MIGHT NOT WORK!!
Info : JTAG tap: auto0.tap tap/device found: 0x44002093 (mfg: 0x049 (Xilinx), part: 0x4002, ver: 0x4)
Warn : AUTO auto0.tap - use "jtag newtap auto0 tap -irlen 2 -expected-id 0x44002093"
Error: IR capture error at bit 2, saw 0x3FFFFFFFFFFFFFF5 not 0x...3
Warn : Bypassing JTAG setup events due to errors
Warn : gdb services need one or more targets defined
```

SUCCESS!

OpenOCD has been able to succesfully access send something through the JTAG interface, and, even better, it has
even been able to scan out device ID `0x44002093`, which it understands to be a Xilinx device!

It has also launched a telnet service on port 4444. We can use that to issue all kinds of OpenOCD commands through
the command line.

In a different terminal window:

```bash
> telnet localhost 4444

Trying 127.0.0.1...
Connected to localhost.
Escape character is '^]'.
Open On-Chip Debugger
> 
> scan_chain
   TapName             Enabled  IdCode     Expected   IrLen IrCap IrMask
-- ------------------- -------- ---------- ---------- ----- ----- ------
 0 auto0.tap              Y     0x44002093 0x00000000     2 0x01  0x03
```

In our case, we already know that we want to work with Xilinx Spartan-6 devices. OpenOCD has a long list
of devices of which it knows JTAG particulars. It also defines custom functions to extract information or
issue commands that are specific to this product.

Let's restart OpenOCD and load the Spartan-6 device file as well:

```bash
> sudo /opt/openocd/bin/openocd -d -f /opt/openocd/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg -f /opt/openocd/share/openocd/scripts/cpld/xilinx-xc6s.cfg -c "adapter_khz 1000"



Open On-Chip Debugger 0.10.0+dev-00410-gf0767a3 (2018-05-15-21:46)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : auto-selecting first available session transport "jtag". To override use 'transport select <transport>'.
xc6s_print_dna
adapter speed: 1000 kHz
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : clock speed 1000 kHz
Info : JTAG tap: xc6s.tap tap/device found: 0x44002093 (mfg: 0x049 (Xilinx), part: 0x4002, ver: 0x4)
Warn : gdb services need one or more targets defined
```

OpenOCD know reports that it has found an `xc6s`, or Spartan 6, JTAG TAP controller.

# Altera USB Blaster Compatible JTAG Dongle 

Same thing here:

```bash
> lsusb

Bus 002 Device 001: ID 1d6b:0003 Linux Foundation 3.0 root hub
Bus 001 Device 003: ID 045e:07a5 Microsoft Corp. Wireless Receiver 1461C
Bus 001 Device 002: ID 8087:0a2b Intel Corp. 
Bus 001 Device 028: ID 09fb:6001 Altera Blaster
```

I have 3 Altera USB-Blaster clones. They all have the same `09fb:6001` vendor ID/device ID, and they
can all use the same OpenOCD script:

```bash
> sudo /opt/openocd/bin/openocd -f /opt/openocd/share/openocd/scripts/interface/altera-usb-blaster.cfg

Open On-Chip Debugger 0.10.0+dev-00930-g09eb941 (2019-09-16-21:01)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : only one transport option; autoselect 'jtag'
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : usb blaster interface using libftdi
Info : This adapter doesn't support configurable speed
Warn : There are no enabled taps.  AUTO PROBING MIGHT NOT WORK!!
Info : JTAG tap: auto0.tap tap/device found: 0x44002093 (mfg: 0x049 (Xilinx), part: 0x4002, ver: 0x4)
Warn : AUTO auto0.tap - use "jtag newtap auto0 tap -irlen 2 -expected-id 0x44002093"
Error: IR capture error at bit 2, saw 0x3FFFFFFFFFFFFFF5 not 0x...3
Warn : Bypassing JTAG setup events due to errors
Warn : gdb services need one or more targets defined

```

This was much easier than for the Xilinx dongle: no need to specify a clock speed or transport protocol.

# Loading the bitstream

I'll load [this LED blink bitstream](https://github.com/q3k/chubby75/blink/ise/top.bit).

```bash
> sudo /opt/openocd/bin/openocd \ 
            -f /opt/openocd/share/openocd/scripts/interface/altera-usb-blaster.cfg \
            -f /opt/openocd/share/openocd/scripts/cpld/xilinx-xc6s.cfg \
            -c "adapter_khz 1000; init; xc6s_program xc6s.tap; pld load 0 ./ise/top.bit ; exit"

Open On-Chip Debugger 0.10.0+dev-00930-g09eb941 (2019-09-16-21:01)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
Info : only one transport option; autoselect 'jtag'
xc6s_print_dna
Info : usb blaster interface using libftdi
Info : This adapter doesn't support configurable speed
Info : JTAG tap: xc6s.tap tap/device found: 0x44002093 (mfg: 0x049 (Xilinx), part: 0x4002, ver: 0x4)
Warn : gdb services need one or more targets defined
```

If all goes well, OpenOCD will load the bitstream and then quit. And you'll have a blinking LED on your board.


