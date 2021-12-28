---
layout: post
title: GDBWave - A Post-Simulation Waveform-Based RISC-V GDB Debugging Server
date:  2021-12-25 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction


A small soft core CPU is a great way to add control and management operations to your FPGA design. It's much
faster to iterate through different versions with some C code, and not needing to resynthesize is a big
time saver too (if [you know how to update RAM contents efficiently](/2021/04/25/Intel-FPGA-RAM-Bitstream-Patching.html).)
That's why almost all my hobby FPGA projects have a small [VexRiscv RISC-V CPU](https://github.com/SpinalHDL/VexRiscv).

I recently wrote about how to [connect GDB to a VexRiscv CPU](/2021/07/18/VexRiscv-OpenOCD-and-Traps.html) that's running 
on the actual hardware by adding a JTAG interface. You do something similar in simuation, by connecting
GDB to OpenOCD which talks to the simuluation over a simulated JTAG interface.  This blog post is not about that. 

Instead, I want to talk about simulating an RTL design that contains of soft CPU first, and then 
**debugging the firmware that runs on that soft CPU after the simulation has completed.**

I usually don't have a JTAG interface in my design: I'm often just too lazy to wire up a USB JTAG dongle 
to the FPGA board. But what I do all the time is to look at simulation waveforms and try to figure out what the 
CPU was doing at a particular point in the simulation. Or, the other way around, try to figure out what the hardware 
was doing when the CPU was executing a particular line of code.

My traditional workflow was a follows: 

* look at a waveform file
* find the region of interest
* check out the program counter (PC) of the VexRiscv CPU
* look up that program counter in a disassembled version of my C code

It's a tedious process and it's near impossible to get a bigger view of what's going on in the CPU: no
easy way to dump the contents of the program call stack, variables, registers etc.

I was wondering how others handled this kind of debugging and fired off 
[the following Tweet](https://twitter.com/tom_verbeure/status/1455905689365217286):

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Question: you are simulating a RISC-V CPU that is running a C program. You are recording a VCD (or FST) trace. How do you correlate between the instruction address in the waveform and the line of C code?</p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1455905689365217286?ref_src=twsrc%5Etfw">November 3, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

There were a number useful suggestions:

* Use the `addr2line`, part of the GCC toolchain, or `llvm-symbolizer` tools to translate the PC value straight 
  to the C source code file and line number.
* Expand the previous method by creating a GTKWave translate filter so that the file and line numbers
  are shown as a ASCII-encoded waveform in the waveform viewer itself.
* [Matthew Balance](https://twitter.com/bitsbytesgates) suggested a brilliant way to 
  [view the call stack in the waveform viewer](https://bitsbytesgates.blogspot.com/2021/01/soc-integration-testing-higher-level.html):
![Call stack in waveform viewer](/assets/gdbwave/call_stack.png)
* Tangentially related, somebody pointed out that the Quartus SignalTap has the option show the active
  assembler instruction of a Nios II soft CPU in the waveform. There was a time when I used Nios II CPUs
  a lot. This would definitely have been useful.
* [@whitequark](https://twitter.com/whitequark/status/1455918588502724613?s=20) suggested adding a GDB server
  to a CXXRTL simulation environment, which is a similar but more direct way of connecting GDB to a 
  live simulation through a simulated JTAG interface.

That last suggestion gave me the idea to **feed the waveform trace into a GDB server**:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Yes. But the end result of that is the same as using OpenOCD and jtag_vpi, right? How about a GDB server that reads in a VCD file?</p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1455919532506173442?ref_src=twsrc%5Etfw">November 3, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

This was considered a cursed idea, a high mark of approval indeed!

Two months later, the result is GDBWave: a post-simulation waveform-based RISC-V GDB debugging server.

# GDBWave in a Nutshell

The overall flow in which you use GDBWave is pretty straightforward:

![GDBWave overall flow](/assets/gdbwave/gdbwave-overall_flow.svg)

1. Simulate a design that contains an embedded soft core RISC-V CPU such as the VexRiscv.
1. During the simulation, dump the signals of the design to a waveform file.
1. Tell GDBWave which signals in the design can be used to extract a processor trace: the CPU program counter, 
   and, optionally, the contents of the CPU register file, and the transactions to memory.
1. Launch GDBWave as a GDB server that pretends to be a real running CPU system with debug capabilities.
1. Launch the standard RISC-V GDB debugger and connect to the GDBWave debug target
1. Issue GDB commands as if it were dealing with a real CPU: breakpoints, watchpoints, line stepping through the
   code, inspecting variables, you name it. You can even go back if time if you'd like.
1. Future bonus feature: link GDBWave to your GTKWave waveform viewer. When your GDBWave CPU hits a breakpoint, 
  automatically jump to that point in time in the waveform viewer!

Note that all of this is possible without the need of any hardware debugging features in the CPU: you can do this on
a [picorv32](https://github.com/YosysHQ/picorv32) or the [award winning bit-serial SERV](https://github.com/olofk/serv)
RISC-V CPUs and it will still work. The only minimum requirement is that you can find the right signals
in the RTL, and thus the dumped waveform file, to extract the program counter value of instructions that have
been successfully executed and retired.

There are some things that GDBWave won’t allow you to do:

* You can’t change the flow of the program that’s under debug. This is an obvious first principles consequence 
  of running a debugger on prerecorded data.
* GDBWave currently only works with CPU that has a single instruction, in-order pipeline. It’s not impossible to 
  extend support for more complex CPUs, but that’s outside the scope of this Christmas holiday project.

*This blog post talks about processor traces that are extracted from simulation waveforms, but you can also 
gather this data from real hardware, if the CPU system in your design has instruction tracing capabilities such as 
those described in the [RISC-V Processor Trace specification](https://riscv.org/technical/specifications/).*

# The FST Waveform Format

In the hobby world, almost everybody dumps simulation waveforms as VCD files, a format standardized in the
Verilog specification that is supported by nearly all simulation and digital design debugging tools in existence.
Except GDBWave, which doesn't support VCD directly.

There’s a good reason for that: being universally supported is about the only good characteristic of what is 
otherwise a terrible waveform format.

* VCD is disk space hog with little or no compression. 
* It requires you to read in the full file even if you want to extract the values of a signal out of thousands 
or more signals.
* You also can’t extract values for a give time range without first processing the values of 
all time steps before that. 

In the professional world, Synopsys Verdi is used for debugging digital designs... if your company can pay for it. 
Verdi comes with the FSDB waveform format which has none of the VCD disadvantages. Unfortunately, that format is 
proprietary and, to my knowledge, hasn’t been reverse engineered. If you want to write tools that extract data 
from FSDB files, you need to link a precompiled binary library that comes with the Verdi installation.

Luckily, there’s an open source alternative: the FST format was developed by Tony Bybell, the author of GTKWave. 
It fixes all the flaws of the VCD format. There is no formal specification of the FST file format, but 
["Implementation of an Efficient Method for Digital Waveform Compression"][1], a paper that is included
in the GTKWave manual, goes a long way to describe the design goals and how they were achieved.

Here are some of those features:

* Small file size

    In my example designs, FST files are roughly 50x smaller than equivalent VCD files. 

    This is because it uses a two-stage compression scheme: in the first stage, it encodes signal value changes 
    as delta values. I didn’t try to figure out the exact details from the source code (which has the same peculiar 
    coding standards as GTKWave), but it is supposedly based in the method described in this paper. 

    During the second stage, the output of the first stage is compressed by the standard LZ4 or GZIP method (or 
    it is bypassed.)

* Fast compression and decompression speed 

    Compression speed is very fast and slows down the simulation by a small amount compared to dumping a VCD file. 
    The FST library comes even with multi threading support, for very large designs that dump a lot of data, so that 
    multiple chunks can compressed in parallel. (Note that this is a bit slower on smaller cases. It’s only helpful 
    when you’re dumping hundreds of thousand of signals and more.)

* Fast opening of FST files

    You don't need to process the whole file before you can extract data from it.

* FST files are saved in multiple chunks 

    If you need to access data somewhere in the middle of a large simulation, it will only read in the chunks that 
    contain the desired data, and skip whatever came before. 

* FST files can be read while the database is still being written

    This is really useful if you are running a very long running simulation and you want to quickly
    check if everything is still behaving as planned. 

    This feature is direct consequence of data being written out in separate chunks.


The FST format isn’t perfect: 

* No Formal Format Specification

    There is no formal format specification, and, based on [a discussion on the GTKWave GitHub
    project](https://github.com/gtkwave/gtkwave/issues/70#issuecomment-907984622), one shouldn't expect there to
    ever be one.  Other documentation only exists in the form of comments in the source code, or comments by the author 
    on other GitHub issues. 

* No FST library API documentation

    There is a library to read and write FST files, but there's no documentation on how to use it.
    You're expected to figure out how things work 
    [by checking out existing utilities](https://github.com/gtkwave/gtkwave/issues/70#issuecomment-902463200) that
    read and write FST files.

    In practice, I didn't find using it too hard, and I created 
    [`FstProcess`](https://github.com/tomverbeure/gdbwave/blob/main/src/FstProcess.cc), 
    a C++ class that has the limited functionality that I needed to extract data from an FST file.

* No stand-alone FST library 

    There's no stand-alone FST library with individual version tracking etc. You're supposed to
    [extract the code from the GTKWave source tree](https://github.com/gtkwave/gtkwave/tree/master/gtkwave3-gtk3/src/helpers/fst).

    Since the relevant code already lives in its own directory, extracting the code is not hard at all. But the lack of 
    versions makes it impossible to keep track of which 
    [bug fixes](https://github.com/gtkwave/gtkwave/commit/ee52b426351cb2a58af16b11bf401519ccba3ead#diff-5ceb02db973e525ddd64b68b28dcb4132a12d79ce7a4d083d756143f482a2109)
    been applied.

* No support for vectors with an LSB that is different than 0

    Inexplicably, FST doesn’t support vector signals that don’t start with bit 0: a vector that is defined as 
    `MySignal[31:2]` gets saved as `MySignal[29:0]`. This is not an issue for the vast majority of design, 
    but considering that it would take just 1 additional parameter in the signal declaration, this things
    annoys me way more that it should.

Still, the benefits far outweigh the disadvantages, especially if you're dealing with huge waveform
databases.

Verilator and Icarus Verilog support FST out of the box. GTKWave does too, of course.

If your simulation tool can't generate FST files, you can always use conversion utilities such as
`vcd2fst` that come standard with GTKWave.

**If you're using the FST format as part of a Verilator testbench, make sure to NOT call the
`flush()` method on the `VerilatedFstC` trace object after each simulation cycle. I did this in one of
my testbenches and 
[my simulation speed dropped by a factor of 20](https://github.com/verilator/verilator/issues/3168#issuecomment-951476317)
compared to using VCD!**


# How GDBWave Works

At the very minimum, GDBWave needs to know which instructions have been successfully executed and completed 
(“retired”) by the CPU, by tracking the program counter.

In the easiest case, you can get this data from an instruction trace port: some CPUs have a trace port 
which allows on-chip hardware to capture instruction traces, compress it, and either store it somewhere 
(e.g. an on-chip trace buffer, or external DRAM) or transfer it off the chip through JTAG or some other protocol.

In my VexRiscv, OpenOCD, and Traps blog post, I showed all the steps between a debugger IDE and an actual 
CPU. For GDBWave, the relevant step in that chain of interaction modules is the one where GDB talks to 
OpenOCD through the GDB Remote Serial Protocol (RSP). In the GDB development documentation, OpenOCD is 
just another so called GDB stub: a piece of software that receives relatively high level CPU related 
requests from GDB and returns the desired data. A GDB stub is often called a GDB server, because that’s 
exactly what it is: GDB is the client that connects to the stub via a TCP/IP socket, and the stub serves
data that is requested by the client.

If you want to make GDB believe that your recorded CPU simulation waveform or trace is an actually running 
CPU under debug, you need write your own GDB stub:

* Create a socket and accept incoming connections
* Parse the RSP protocol compliant requests from the client
* Fetch the requested data from the recorded trace
* Transform the data into an RSP confirming reply
* Send the reply back over the socket

There is quite a generic boilerplate in there, and there are tons of open source GDB stubs that you can 
modify to your taste.

I wanted to write GDBWave in C++ because the FST library, written in C, doesn’t have any bindings to 
popular scripting languages, and because, after not having written C++ for almost 15 years, I simply 
wanted to get a taste of all the new C++ features that have been added to language. 
*(Hint: it’s almost an entirely new language…)*

I settled on gdbstub, a lightweight implementation that’s designed to make it easy to support your own 
CPU architecture. It’s so minimal that it doesn’t even support breakpoints, but those are very easy to add.

# Things a GDB stub is supposed to do


# GDBWave and the picorv32

# GDBWave and the award-winning SERV


# References

**Waveforms**

* [GTKWave User's Guide - Appendix F: Implementation of an Efficient Method for Digital Waveform Compression][1]

* [A novel approach for digital waveform compression](https://www.researchgate.net/publication/234793005_A_novel_approach_for_digital_waveform_compression/link/5462239b0cf2cb7e9da643c0/download)

**GDB stubs**

* [mborgerson/gdbstub - A simple, dependency-free GDB stub that can be easily dropped in to your project](https://github.com/mborgerson/gdbstub)

    > A simple, dependency-free GDB stub that can be easily dropped in to your project. 

    GDBWave is based on this one.

* [bluespec/RISCV_gdbstub](https://github.com/bluespec/RISCV_gdbstub)

    > A gdbstub for connecting GDB to a RISC-V Debug Module.

* [daniel5151/gdbstub](https://github.com/daniel5151/gdbstub)

    > An ergonomic and easy-to-integrate implementation of the GDB Remote Serial Protocol in 
    > Rust, with full no_std support. 

* [avatarone/avatar-gdbstub](https://github.com/avatarone/avatar-gdbstub)

    > GDB stub that allows debugging of embedded devices.


# Footnote

Blah Blah[^1]

[^1]: This is a footnote...


[1]: /assets/gdbwave/gtkwave_manual.pdf#page=137


