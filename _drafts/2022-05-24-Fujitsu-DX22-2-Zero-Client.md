---
layout: post
title: Getting Started with the Pano Logic Compatible Fujitsu DZ22-2 Zero Client
date:  2022-05-24 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I started my hobby FPGA adventures by reverse engineering cheap FPGA boards. The first one was
the [eeColor Color3](/2018/04/08/Hacking-the-eeColor-Color3.html), but I soon transitioned to
the Pano Logic G1, on which I designed my 
[Racing the Beam Ray Tracer](/rtl/2018/11/26/Racing-the-Beam-Ray-Tracer.html)
project. 

The Pano Logic G1 is a great device with a capable FPGA and interface components that
are relatively easy to use, but its successor, the Pano Logic G2, is the true power house,
with a Spartan 6 LX150 or LX100 FPGA that's large even by today's hobby standards, 10 years
after its introduction.

I was able to get the DVI and Ethernet RX up and running, but eventually after lost interest 
in working with Pano blocks: there are just too many electronics projects to persue.

However, that doesn't mean that work on the Pano Logic completely fizzled away: Skip Hansen 
worked a bunch of Pano Logic related projects:

* [Panoman](https://github.com/skiphansen/pano_man) is a port of Pacman for the Pano G1.
* [pano Z80](https://github.com/skiphansen/pano_z80) converts the G1 into a Z80 CP/M computer.
* [panog1_opl3](https://github.com/skiphansen/panog1_opl3) is a port of OPL3 Yamaha
  FM synthesis sound chip for the G1.
* [panog2_opl3](https://github.com/skiphansen/panog1_opl3) does the OPL3 on the G2.
* [panog2_linx](https://github.com/skiphansen/panog2_linux) runs Linux on a G2. It abuses
  the DVI or HDMI DDC pins as serial port pins.
 
And last, but definitely not least, Skip also spend a huge amount of time reverse engineering
Pano Logic's updating tool. 

# The Pano Logic Updating Tool - A New Bitstream without JTAG Programmer

The core marketing point of Pano Logic was that the clients were zero management, because
they didn't have a CPU, and thus there was no way take over control with malignant software.
Instead, every thing is done with FPGA hardware: the TCP/IP protocol stack, the USB protocol
stack, everything. Whether or not that's a feature is up for debate, but it raises the question:
what happens if there's a bug in the bitstream that configure the FPGA? You want to be able
to flash a new bitstream, preferably without opening up the device.

Pano Logic added a way to the original bitstream to reflash the firmware over Ethernet, along
with **progfpga**, a bitstream flashing tool.

The details of the flash-over-Ethernet protocol haven't been reverse engineered, but Skip
used his [Ghidra](https://ghidra-sre.org/) skills to figure out how to modify progfpga
and trick it into reflashing G1 and G2 devices with a bitstream of your choice.
The result of this work can be found in this 
[pano_progfpga GitHub repo](https://github.com/skiphansen/pano_progfpga).

You should really go to the project page to get the detailed instructions, but here's the
summary:

* progfpga is an updating tool created by Pano Logic. There are version for the G1, the G2
  with LX150 and the G2 with the LX100 FPGA.
* the updated bitstream that's to be flashed into the Pano device is embedded in the
  progfpga binary.
* Skip's pano_progfpga project creates a tool, patch_progfpga, that, well, patches
  progfpga with a bitstream that you've created yourself.

# Spartan 6 Multiboot Operation

The Spartan 6 FPGA that's used in a Pano Logic G2 has this really cool feature that Xilinx calls "multiboot".
It allows user logic that's already running on the FPGA to ask the FPGA to reset itself and 
reconfigure itself with a bitstream that's located at a user specified location of the
SPI flash.

This makes it possible to select between multiple bitstream, depending on which feature
is required.  A typical use case would be the following:

* the FPGA first boots up with a bitstream that does a number of self-checks. 
* when self-check are passing, the FPGA reboots again, but this time with a bitstream
  that contains the actual, functional, application.

There's more to it thought: the Spartan 6 also has a fallback feature. When loading from SPI flash
fails (after a couple of retries), the FPGA goes into fallback mode and loads a so-called "golden"
bitstream.

All of this makes it possible to create a system for in-the-field updates, with fallback if things are going
wrong. For example, when the power goes down during the programming operation of a new bitstream, and
this new bitstream gets corrupted, there'll still be the golden bitstream as a fallback when power comes
back up.

The Pano Logic G2 makes use of this: its SPI flash contains a main, "multiboot", bitstream and 
a fallback, "golden", bitstream.  Both bitstream contains the necessary logic to support flashing 
a new bitstream image over Ethernet, so when progfpga fails, there's nothing to worry about.

But what if progfpga worked fine **and you used it to flash you own custom bitstream**? Well, 
unless you added yourself, your custom bitstream won't have SPI flashing functionality, or
a way to reboot with the Pano Logic golden bitstream, so your only way to flash the SPI again
is by using a JTAG connector. 

Or... you use [panog2_ldr](https://github.com/skiphansen/panog2_ldr), another great project by
Skip. Panog2_ldr replaces the original Pano Logic G2 updating infrastructure by a new, open
source one, and adds an additional booting step so that it's always possible to reflash your Pano
G2, even when it has your custom application bitstream!

The panog2_ldr boot sequence is as follows:

* Power up the Pano G2
* Configure the FPGA with the panog2_ldr bitstream that's stored at the multiboot location
* when an autoboot flag is set, stored in the SPI flash as well, and when the Pano button is
  NOT pressed, immediately load the application bitstream. 

The panog2_ldr bitstream constains a small open source RISC-V CPU system that borrows heavily
from other open source projects:

* the core SOC is UltraEmbedded's [fpga_test_soc](...)
* the Ethernet MAC comes from 
* 


The details are described in 
[Chapter 7 - Reconfiguration and Multiboot](/assets/panologic-g2/multiboot/xilinx_spartan6_config_ug380.pdf#page=127)
of the Spartan-6 FPGA Configuration User Guide (UG380).



# References

* My [eeColor Color3 GitHub repo](https://github.com/tomverbeure/color3)
* My [Pano Logic G1 GitHub repo](https://github.com/tomverbeure/panologic)
* My [Pano Logic G2 GitHub repo](https://github.com/tomverbeure/panologic-g2)
* My [Racing the Beam Ray Tracer GitHub repo](https://github.com/tomverbeure/rt)
* [pano_progfpga GitHub repo](https://github.com/skiphansen/pano_progfpga)



