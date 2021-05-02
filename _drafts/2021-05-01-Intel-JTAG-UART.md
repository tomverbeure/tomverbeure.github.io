---
layout: post
title: The Intel JTAG UART - A Console Interface without Extra Pins
date:  2021-05-01 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my previous blog post](/2021/04/25/Intel-FPGA-RAM-Bitstream-Patching.html) about updating the RAM 
initialization contents of Intel FPGAs, I mentioned how I include a small CPU in almost all my design
for things like low-speed interface control, register initialization, overall data flow management
etc.

I now want to take this one step further, and add another essential item of my design toolbox: the
JTAG UART.

Everybody is probably familiar with the regular UART, an interface that 
[dates back to somewhere in the seventies](https://en.wikipedia.org/wiki/Universal_asynchronous_receiver-transmitter#History)
but that's present in systems everywhere, from the lowest performance embedded microcontrollers to 
high level routers and servers, where it's used as a console interface to enter commands or to dump
logging messages.

It's a simple protocol too, that's easy to implement on FPGA too with just a handful of combinational logic
and flip-flops. 

And yet I almost never use it.

That's because, for all its simplicity, it still requires an extra cable from my FPGA board to my
host PC, and at least 2 pins of the FPGA too. If UARTs were the only way to quickly implement a
console in my designs, I would use it, but there's an alternative: the JTAG UART.

The JTAG UART offers all the benefits of a UART without the downside of requiring an additional
cable: it already uses the JTAG connects that's used to load new bitstreams into the FPGA or to
program the FPGA configuration flash.

JTAG UARTs can be added to all FPGAs that have a JTAG test access port (TAG), but they are
especially easy to use on Intel FPGAs. And since those are the FPGAs that I use for all my
project, that's what this blog post will be about.

# What's a JTAG UART?

To the CPU inside the FPGA, a JTAG UART behaves just the same as a regular UART: a block
with a handful of control and status registers to write bytes to a transmit FIFO and read bytes
from a receive FIFO, and to check if there those FIFOs are full or empty.

But on the other side, instead of a piece of logic that serialize the data to and from some
external IO pins, it's connected to the JTAG test access port (TAP) of the FPGA.

![CPU System with JTAG UART](/assets/jtag_uart/jtag_uart-cpu_system_with_jtag_uart.svg)

There'll be the usual low level driver to control the JTAG dongle, and some higher
level software that shifts out the right JTAG instruction and data registers to check
that status and transfer data.

**Advantages over a regular UART**

* No extra cable between FPGA board and PC required.
* Doesn't require additional functional IO pins.
* Multiple JTAG UARTs per FPGA possible, e.g. one per CPU core, all over the same JTAG connection.
* Potentially higher data transfer speeds, depending on the JTAG clock.

**Disadvantages**

* No JTAG UART standard.

    [Xilinx](https://www.xilinx.com/html_docs/xilinx2018_1/SDK_Doc/xsct/use_cases/xsdb_using_jtag_uart.html)
    and [Intel](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/ug/ug_embedded_ip.pdf#page=144)
    have a JTAG UART, but their implementations are very different and incompatible with each other.

* There is no JTAG UART protocol specification.

    The low-level JTAG instructions to talk to the JTAG UARTs aren't published. Because of this, you 
    can't write your own driver to talk the JTAG UART on your Xilinx or Intel FPGA. 

    And thus...

* Requires closed source tools to control.
    
    Intel and Xilinx provide tools to talk to the JTAG UART. I'm only familiar with the Intel tools, and
    the interactive terminal tool works well enough, but it's an incredible pain to interact with the
    JTAG UART by script.

For almost all my designs, I need a JTAG UART only to type some commands and get debug information, without
a need to script things. And for that, the Intel tools are totally sufficient.

# An Open Source JTAG UART?

If JTAG UART is so great, why isn't there are open source alternative?

It turns out, there is! It's called "JTAG Serial Port" in the OpenRisc OR1K system. 
It even has [official support in OpenOCD](https://github.com/ntfreak/openocd/blob/master/src/target/openrisc/jsp_server.c),
with support for the Intel Virtual JTAG TAP, the Xilinx BSCAN TAP, and the so-called "Mohor" TAP (I think it's 
a generic JTAG TAP that's implemented by Igor Mohor).

However, there's very little information about it, and while there must be RTL for this block
somewhere, I wasn't able to find it.

The availility of an officially software driver in OpenOCD is a big deal, though, so
if somebody wants to plug this hole in the open source FPGA ecosystem: go for it!

# The Intel's Virtual JTAG System 

Xilinx and some Lattice FPGAs have a way to link to the native JTAG TAP by instantiating
a particular JTAG primitive cell, but there's no general framework to add any random amount
of JTAG clients.

Intel's solution is completely different: it offers 
Virtual JTAG,
a system where up to 254 JTAG related clients can be attached to the native JTAG TAP. Each JTAG
client has its own instruction register and data registers.

![Intel Virtual JTAG](/assets/jtag_uart/intel_virtual_jtag.png)

All of this is part of Intel's System Level Debug (SLD) infrastructure. (When you're compiling
a design with Quartus, you might see modules being compiled that start with `sld_`. Chances
are that this is related to virtual JTAG.)

The virtual JTAG system has a central hub that offers discoverability features: you don't need 
to know up front and specify what kind of JTAG client are in the FPGA design, the Intel tools will 
figure that out by themselves by enumerating the clients that are connected to the hub.

![Intel SLD Hub](/assets/jtag_uart/intel_sld_hub.png)

Here are some examples of Intel's own clients:

* JTAG UART
* SignalTap
* In-System Sources and Probes
* Nios2 CPU debugger

A user can also design their own client for some custom JTAG functionatily. For example,
when added to an Intel FPGA, the OpenRisc JTAG Serial Port that I talked about earlier would
be custom virtual JTAG client.

It's out of the scope of this blog post to dive into the low level details. If you're interested,
you can find a lot of details in 
[Intel's Virtual JTAG User Guide](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/ug/ug_virtualjtag.pdf).

# Adding a JTAG UART to Your Design *without Using Platform Designer*

The most common way to add a JTAG UART to your design is adding one to your Nios2 SOC
system in Intel's Platform Designs (formerly known as Qsys.) In that case, it as simple as 
drag-and-drop, and the RTL, software driver and everything gets autogenerated for you.

But that's not what I will show here: it's one thing to tie your debug logic to use a proprietary 
feature, it's another to make your whole design depending on a proprietary CPU architecture.
I often develop my designs on Intel FPGAs because of the excellent debug features, but I still
want to be able to run the final, debugged result on a Lattice FPGA! With Qsys-based
Nios2 system, you can't do that.

Instead, I'll extend the VexRiscv-based [mini CPU design](http://localhost:4000/2021/04/25/Intel-FPGA-RAM-Bitstream-Patching.html#mini-cpu-a-concrete-design-example)
of my previous blog post with a JTAG UART.

