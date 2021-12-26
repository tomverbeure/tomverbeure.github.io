---
layout: post
title: GDBWave - A Post-Simulation Waveform-Based RISC-V GDB Debugging Server
date:  2021-12-25 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Almost all my hobby FPGA projects contain a soft core RISC-V CPU, usually a VexRiscv. 

It started with [the following Tweet](https://twitter.com/tom_verbeure/status/1455905689365217286):

![Tweet: Question: you are simulating a RISC-V CPU that is running a C program.  You are recording a 
VCD (or FST) trace. How do you correlate between the instruction address in the waveform and the line of C code?](/assets/gdbwave/tweet.png)


Gdbwave

A small soft CPU is a great way to add control operations to your design yet also iterate quickly between different versions.

I recently wrote about how to add a JTAG interface to your design so that you can control the CPU with GDB. In my example, I connected GDB to the real hardware, the actual FPGA, but there also ways to connect GDB to a running RTL simulation. This blog post is not about that. 

Instead, I want to talk about GDBWave, a little tool that I wrote that allows you to connect to GDB to your CPU **after the fact**. 

That’s right: if you record the right amount of data during a simulation run, you can set breakpoints, watchpoints, steps through the design line by line, and inspect the value of variables just as if you’ve connected GDB to a real running CPU. You can even go back in time if you’d like! You don’t even need a JTAG interface or debug logic in the CPU: with little or no modifications, GDBWave should work with almost any RISC-V CPU.

There’s even the option of using GDBWave after the fact with data gathered from real hardware, if you design had instruction tracing capabilities, but that’s not really the focus of this blog post.

# GDBWave in a Nutshell

The most straightforward use case of GDBWave is as follows:

* Simulate a design that contains an embedded soft core RISC-V CPU.
* During the simulation, dump the signals of the design to a waveform file.
* Tell GDBWave which signals in the waveform file allow it to extract the CPU program counter, the contents of the CPU register file, and the transactions to memory.
* Launch GDBWave as a GDB server that pretends to be a real running CPU system with debug capabilities.
* Use the standard RISC-V GDB version to connect to GDBWave and issue GDB commands as if it were dealing with a real CPU.
* Bonus feature: link GDBWave to your GTKWave waveform viewer. When your GDBWave CPU hits a breakpoint, automatically jump to that point in time in the waveform viewer!

There are some things that GDBWave won’t allow you to do:
* You can’t change the flow of the program that’s under debug. This is an obvious first principles consequence of running a debugger on recorded data.
* GDBWave currently only works with CPU with an single instruction, in-order pipeline. It’s not impossible to adjust the design to make it support that, but that’s outside the scope of a Christmas holiday project.

# The FST Waveform Format

In the hobby world, almost everybody dumps simulation waveforms to VCD files. It’s a Verilog standard format that is supported by nearly all simulation and digital design debugging tools in existence.

GDBWave does not support VCD directly. 

There’s a good reason for that: being universally supported is about the only good characteristic of what is otherwise a terrible waveform format.

* VCD is disk space hog with little or no compression. 
* It requires you to read in the full file even if you want to extract the values of a signal out of thousands or more signals. 
* You also can’t extract values for a give time range without first processing the values of all time steps before that. 

In the professional world, Synopsys Verdi is used for debugging digital designs (if your company can pay for it) and with it comes the FSDB waveform format that has none of the VCD disadvantages. Unfortunately, that format is proprietary and, to my knowledge, hasn’t been reverse engineered. If you want to write tools that extract data from FSDB files, you need to link the precompiled binary library that comes as part of the Verdi installation.

Luckily, there’s an open source alternative: the FST format was developed by Tony Bybell, the author of GTKWave. It fixes all the flaws of the VCD format. 

* In my example designs, FST files are roughly 50x smaller than equivalent VCD files. This is because it uses a two-stage compression scheme: in the first stage, it encodes signal value changes as delta values. I didn’t try to figure out the exact details from the source code (which has the same peculiar coding standards as GTKWave), but it is supposedly based in the method described in this paper. During the second stage, the output of the first stage is compressed by the standard LZ4 or GZIP method (or it is bypassed.)
* FST files are saved in multiple chunks. If you need to access data somewhere in the middle of a large simulation, it will only read in the chunks that contain the desired data, and skip whatever came before. 
* Compression speed is very fast and slows down the simulation by a small amount compared to dumping a VCD file. The FST library comes even with multi threading support, for very large designs that dump a lot of data, so that multiple chunks can compressed in parallel. (Note that this is a bit slower on smaller cases. It’s only helpful when you’re dumping hundreds of thousand of signals and more.)

The FST format isn’t perfect. There is no official specification, and other documentation only exists in the form of comments by the author on GitHub issues. The library to read and write FST files, with undocumented but relatively straightforward API,  must be manually extracted from GTKWave source tree as well. Inexplicably, FST doesn’t support vector signals that don’t start with bit 0: a vector that is defined as MySignal[31:2] gets saved as MySignal[29:0], which annoys me way more that it should.

Still, the benefits far outweigh the disadvantages, and adding FST support to GDBWave was easy.

Verilator and Icarus Verilog support FST out of the box. GTKWave does too, of course.

If you want to use GDBWave on a VCD trace, you can use the vcd2fst conversion utility that comes standard with GTKWave.

# How GDBWave Works

At the very minimum, GDBWave needs to know which instructions have been successfully executed and completed (“retired”) by the CPU, by tracking the program counter.

In the easiest case, you can get this data from an instruction trace port: some CPUs have a trace port which allows on-chip hardware to capture instruction traces, compress it, and either store it somewhere (e.g. an on-chip trace buffer, or external DRAM) or transfer it off the chip through JTAG or some other protocol.



# Footnote

Blah Blah[^1]

[^1]: This is a footnote...


