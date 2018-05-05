---
layout: post
title:  "JTAG for FPGAs - Part 1: JTAG_GPIO"
date:   2018-05-03 22:00:00 -0700
categories: JTAG
---

# Introduction

During the development of an FPGA project, you sometimes want to be able to control design internal nodes from your
host PC, or observe internal state.

Even if you plan to have a real control interface on your final board (such as a USB to serial port), that interface
may not yet be ready. Or maybe you want to debug the functionality of that interface itself, and you need another
side band way to access your information.

When you're using Altera tools (or the Xilinx equivalent), you could use In-System Sources and Probes: with a small
amount of effort, you can create a block with a user specified number of control and observability points, instantiate
that block in your design, and use a Quartus GUI to control and observe, or you can bypass the GUI and control and observe
the nodes through a TCL API.

The communication between the design and the host PC happens over JTAG.

You could also add a SignalTap logic analyzer to really see what's going on in the design.
Or add a Nios2 processor with a JTAG UART to transfer data from the PC to the FPGA and back.

The problem with all of this is that it's all very proprietary.

Altera doesn't publish the protocol by which it transfers various kinds of data over JTAG. It works great in their development 
environment, but it's often not practical to install their development tools on different PC.

And what if you want to make the same design work on Altera, Xilinx, and Lattice FPGAs?  Or what if you want to make your own JTAG 
controlled block in our design? Maybe you create your own little CPU and want an way to download binaries to the CPU memory? 
Maybe you've even want to make your CPU debuggable over GDB?

For reasons like this, it may be useful to roll your own JTAG debug infrastructure.

If you want to go that route, one of the immediate questions that follows is: how will I control those JTAG capable block in my design from
my host PC?

This is what this series of articles is trying to address.


# JTAG_GPIO

To make things easy, let's us a really simply JTAG block, one that is essentially a copy of the Altera In-System
Sources and Probes block: `JTAG_GPIO`. 

You instantiate the block in your design, connect it on one side to a JTAG TAP (Test Access Port) and
connect the gpio\_output signals to logic nodes you want to control, and the gpio\_input signals to nodes you want to observe.

You can find the source of this block in [`jtag_gpios.v`](https://github.com/tomverbeure/jtag_gpios/blob/master/rtl/jtag_gpios.v) 
on GitHub.

It works as follows:

* There are 3 data (scan) registers: `scan_n`, `config` and `data`.
* The `scan_n` register is the active data scan register when the `SCAN_N` instruction is selected. `scan_n` determines which
  data register is active when the `EXTEST` instruction is active. In our particular case, `scan_n` is used to select between 
  `config` and `data`, so this register is only 1 bit.
* The `config` data register is used to determine whether or not a GPIO is input or output. A value of 0 is input, 1 is output.
  After a reset, all GPIOs are input. (This is a conservative choice to ensure that a GPIO isn't driving an outside driver after
  reset.)
* The `data` register is used to read back the value of the GPIO inputs or to program the value of GPIO outputs.

You provide the number of GPIOs as a parameter, `NR_GPIOS`, of the jtag_gpio instance.

You'd expect the size of `config` and the `data` shift registers to be the length of the number of GPIOs. But that is not the case!
It's actually `NR_GPIOS+1`.

There is really good reason for this. To understand that, let's see what happens when doing a JTAG scan operation. 

It always happens in the following order:

* `CAPTURE_DR`: during this clock cycle, some parallel value is captured into the data scan register.
* `SHIFT_DR`: this is where the contents that were captured in the previous cycle are shifted out and where a new value
  is shifted in via the `TDI` input.
* `UPDATE_DR`: when a new value has been fully shifted into the data scan regiser, this state is used to apply the value one
  way or the other.

It is impossible to scan an internal value out and a new value in without going through the `CAPTURE_DR` or `UPDATE_DR` states.

Let's now look at an operation where you want to change the input/output configuration of the JTAG_GPIO block.

* `CAPTURE_DR`: load the current configuration
* `SHIFT_DR`: shift the current configuration out, shift the new configuration
* `UPDATE_DR`: apply the new configuration

*Without special precautions, you can not do a read-modify-write operation!*


