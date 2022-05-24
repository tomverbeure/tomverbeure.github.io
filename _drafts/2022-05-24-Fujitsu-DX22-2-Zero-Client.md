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



# References

* My [eeColor Color3 GitHub repo](https://github.com/tomverbeure/color3)
* My [Pano Logic G1 GitHub repo](https://github.com/tomverbeure/panologic)
* My [Pano Logic G2 GitHub repo](https://github.com/tomverbeure/panologic-g2)
* My [Racing the Beam Ray Tracer GitHub repo](https://github.com/tomverbeure/rt)
* [pano_progfpga GitHub repo](https://github.com/skiphansen/pano_progfpga)



