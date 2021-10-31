---
layout: post
title: Rolling Your Own MAX 10 FPGA Remote System Update
date:  2021-10-31 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The most important (and only?) advantage of an FPGA over an ASIC is the ability to 
change a design as needed without having to go through a costly silicon spin: just reprogram
the flash, and you're good to go.

That's not only great for development, it can even be used to update products in the field.

Intel calls it Remote System Update, and they have of documentation about how to do it.
Their [Remote Update Intel FPGA IP User Guide](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/ug/ug_altremote.pdf)
is a good starting point. As described, it's still a pretty convoluted process that with a lot of steps 
and procedures to follow. One of the complicating factors is that the FPGA manages the 
upgrade procedure all by itself, without an external microcontroller. Intel adds 
one of their own Nios2 CPUs on the FPGA to perform all the steps.

In today's complex system designs, it's rare to not have some kind of external microcontroller
on the board. With a little bit of planning ahead, the process can be simplified a lot. What's
even better is that it's possible to procedure the board without the need to flash the FPGA
as a separate step: it's just a part of the boot up procedure of the system.

All of this is especially true for MAX1 FPGAs. Contrary to most other FPGAs, they have flash
storage embedded on the FPGA die itself. 

# System Overview

The overall system is pretty simple. We have:

* a microcontroller (uC)
* general purpose flash storage

  This could be flash that's embedded in the microcontroller itself, an external SPI flash PROM, an SDcard etc.

* a MAX 10 FPGA
* uC GPIOs that can be used by the microcontroller to drive the `tck`, `tms`, and `tdi` JTAG pins of the FPGA.
* a uC GPIO to reset the FPGA. 
 
  If uC pins are scarce, this pin can be omitted and replaced by shifting in a
  PULSE_NCONFIG instruction through the JTAG pins.

* an FPGA status channel back to the microcontroller.
* a JTAG connector to connect a USB Blaster JTAG dongle. 

  This is not required, but most FPGA board will have such a connector, or at least test pins, to allow board debugging.

![System diagram](/assets/max10_remote_system_upgrade/remote_system_upgrade-system_overview.svg)

At the very minimum, the FPGA status channel must allow the uC to check that the FPGA has been loaded 
with a working bitstream, but it's even better if it can read back a user defined bitstream revision code. 

If the system already requires a communication channel between the uC and the FPGA over, say, a UART or
I2C, then adding a bitstream revision code should be easy. If not, such a status channel could
be created by [adding a user JTAG scan chain](/2021/10/30/Intel-JTAG-Primitive.html)
to the FPGA TAP controller, and report back the revision number via the JTAG `tdo` pin.

# Remote System Update Procedure

The system bootup procedure is straightforward:

![Remote system upgrade bootup procedure](/assets/max10_remote_system_upgrade/remote_system_upgrade-bootup_procedure.svg)

* After uC bootup, the uC forces an FPGA configuration. There are many different ways to do this:
    * Drive the FPGA `nCONFIG` IO pin low, then high. 
    * Cycle the power rail of the FPGA.
    * Send the `PULSE_NCONFIG` instruction to the FPGA JTAG controller
    * ...
* After waiting long enough for the FPGA to configure itself, the uC checks if the FPGA
  has been configured with a valid bitstream. There are once again multiple ways to do this. My
  way was to simply wait long enough and then try to communicate with the FPGA. If you don't 
  have a dedicated communication channel, you could do it through the JTAG interface.

# JTAG Trace Preparation

* http://www.clifford.at/libxsvf/
* https://github.com/margro/jam-stapl

* JAM vs SVF
* Remove verification stuff
* Set the right clock speed
* RLE coding


* [Embedded Programming using the 8051 and Jam Byte-Code](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/an/an111.pdf)
