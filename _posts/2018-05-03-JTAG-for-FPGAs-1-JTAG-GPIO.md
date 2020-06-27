---
layout: post
title:  "JTAG for FPGAs - Part 1: JTAG_GPIO"
date:   2018-05-04 00:00:00 -1000
categories: JTAG
---

* TOC
{:toc}

# Introduction

During the development of an FPGA project, you sometimes want to be able to control internal signals of the design from your
host PC, or observe internal state.

Even if you plan to have a real control interface on your final board (such as a USB to serial port), that interface
may not yet be ready. Or maybe you want to debug the functionality of that interface itself, and you need another
side band way to access your information.

When you're using Altera tools (or the Xilinx equivalent), you can use *In-System Sources and Probes*: with a small
amount of effort, you can create a block with a user specified number of control outputs and observability inputs, instantiate
that block in your design, and use a Quartus GUI or a TCL API to control and observe these points.

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

In this series of articles, we'll explore what it takes to get there.

We start by introduction a simple block, JTAG\_GPIO, that more or less mimics the Altera sources and probes tool. And
then we dive into the intrastructure that's need to operate this block from a host PC.

# JTAG_GPIO

The JTAG\_GPIO block has a very simple core functionality.

You instantiate the block in your design, connect it on one side to a JTAG TAP (Test Access Port) and
connect the gpio\_output signals to logic nodes you want to control, and the gpio\_input signals to nodes you want to observe.

You can find the source of this block in [`jtag_gpios.v`](https://github.com/tomverbeure/jtag_gpios/blob/master/rtl/jtag_gpios.v) 
on GitHub.

It has the following scan registers:

| Scan Register | IR activation | Size       | Bit            | Name        |
|---------------|---------------|------------|----------------|-------------|
| `scan_n`      | `SCAN_N`      | 1          | [0]            | `select`    |
| `config`      | `EXTEST`      | NR_GPIOS+1 | [NR_GPIOS-1:0] | `direction` |
|               |               |            | [NR_GPIOS]     | `update`    |
| `data`        | `EXTEST`      | NR_GPIOS+1 | [NR_GPIOS-1:0] | `value`     |
|               |               |            | [NR_GPIOS]     | `update`    |

It works as follows:

* There are 3 data scan registers: `scan_n`, `config` and `data`.
* The `scan_n` register is the active data scan register when the `SCAN_N` instruction is selected. `scan_n` determines which
  data register is active when the `EXTEST` instruction is active. In our particular case, `scan_n` is used to select between 
  `config` and `data`, so this register is only 1 bit.
* The `config` data register is used to determine whether or not a GPIO is input or output. A value of 0 is input, 1 is output.
  After a reset, all GPIOs are input. (This is a conservative choice to ensure that a GPIO isn't driving an outside driver after
  reset.)
* The `data` register is used to read back the value of the GPIO inputs or to program the value of GPIO outputs.

The number of GPIOs is a Verilog parameter, `NR_GPIOS`, of the jtag_gpio instance.

The `config` and `data` scan registers have one 1 additional `update` bit `update` bit: the JTAG TAP `UPDATE_DR` operation is only
executed when this bit is set. Otherwise, the new value that is shifted in through `TDI` has no effect at all.

Without such a bit it would be impossible to do read-modify-write operations, because a shift operation into the `data` or `config`
scan register would always execute `UPDATE_DR` as well.

# JTAG Usage

Let's assume that we have 3 GPIOs.

The JTAG\_GPIO block is used as follows:

Configure the direction of the GPIOs:
* `jtag_ir_scan(SCAN_N)`

    Set the `SCAN_N` instruction. This select the `scan_n` data scan register.

* `jtag_dr_scan(1'b0)`

    Set the `scan_n` scan register to 0 (=`config`)

* `jtag_ir_scan(EXTEST)`

    Set the `EXTEST` instruction. This, in combination with `scan_n` = 0, connects `config` as data scan register.

* `prev_config = jtag_dr_scan(4'b1011)`

    The MSB sets the `update` flag. The 3 lower bits set GPIO 0 and 1 to output, and GPIO 2 as input.
    The previous config value gets returned as `prev_config`. In this case, we don't use it.

Control and observe GPIO pins:
* `jtag_ir_scan(SCAN_N)`

    Set the `SCAN_N` instruction. This select the `scan_n` data scan register.

* `jtag_dr_scan(1'b1)`

    Set the `scan_n` scan register to 1 (=`data`)

* `jtag_ir_scan(EXTEST)`

    Set the `EXTEST` instruction. This, in combination with `scan_n` = 1, connects `data` as data scan register.

* `gpio_input = jtag_dr_scan(4'b1001)`

    Update the GPIO 0 and 1 outputs to 1 and 0. The value of all GPIOs is returned as `gpio_input`

* `gpio_input = jtag_dr_scan(4'b1010)`
	
    Toggle GPIO 0 from 1 to 0 and GPIO 1 from 0 to 1. Also get the `gpio_input` values.

* `gpio_input = jtag_dr_scan(4'b0010)`
	
    Get the `gpio_input` values *without updating the GPIO outputs*! This is because the MSB of the value that
    is being scanned in is 0.

# Coming up...

This part introduces a simple but usable JTAG controlled GPIO block. 

While it's good to know how to use this block in theory, we need to add it to a real design, and figure out
a way to sends the JTAG instructions to the hardware. The two most populare ways of doing that 
are [OpenOCD](http://openocd.org) and [UrJTAG](http://urjtag.org).

In the next installment of this series, we'll have a closer look at this.


