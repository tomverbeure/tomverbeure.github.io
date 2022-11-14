---
layout: post
title: Logic Primitive Transformations with Yosys Techmap
date:  2022-11-13 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

If you're reading this you probably already know that [Yosys](https://github.com/YosysHQ/yosys)
is an open source logic synthesis tool. You may also know that it's much more than that: in
my [earlier blog post about CXXRTL](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html)
I call it the *swiss army know of digital logic manipulation*. In most cases, using Yosys
means running pre-made scripts with commands: when I'm synthesizing RTL for an FPGA of the 
Lattice iCE40 family, the `synth_ice40` command is usually sufficient to convert my RTL
into a netlist that can be sent straight to `nextpnr` for place and route.

But sometimes you want to perform very particular operations that aren't part of a standard
sequence. My current version of Yosys has 232 commands, and many of these commands have an
impressive list of additional options. 

In this blog post, I'll talk about `techmap`, a particularly powerful command that allows
one to transform an instance of a given type to one or more different ones. 

# Mapping a multiplication to an FPGA DSP Cell

A very good example of a `techmap` operation is one where a generic multipication operation
is converted into a DSP block of an FPGA. For those who are unfamiliar with the technology,
FPGAs usually have only a few core logic primitives: lookup-table cells (LUTs) are used to construct
any kind of random logic, RAMs cells for, well, RAMs, and DSPs, larger cells that contain one
or more hardware multipliers, often in combination with an accumulator.

Let's say your Verilog code contains 10-bit x 10-bit multiplication into a 20-bit result:

```verilog
    ...
    wire [9:0]      op0, op1;
    wire [19:0]     result;
    ...
    assign result = op0 * op1;
    ...
```

Yosys will translate the multiplication operation into an internal `$mul` primitive.


```
    XXX fill in RTLIL code
```

This primitive must be converted into cell primitives of the target technology. Most FPGAs from the
iCE40 family have handful of DSPs. After running a appropriate `techmap` operation, you'll see
that the `$mul` primitive has been converted to an 
[`SB_MAC16` cell](https://www.google.com/url?sa=i&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=0CAMQw7AJahcKEwjgtM_Akq37AhUAAAAAHQAAAAAQAg&url=https%3A%2F%2Fwww.latticesemi.com%2F-%2Fmedia%2FLatticeSemi%2FDocuments%2FApplicationNotes%2FAD%2FDSPFunctionUsageGuideforICE40Devices.ashx&psig=AOvVaw3a9NdaElFY-9aVNE1-QX7H&ust=1668496907967676), 
the DSP primitive of the iCE40 family.

![SB_MAC16 internal block diagram](/assets/yosys_techmap/SB_MAC16_block_diagram.png)

In the block diagram above, you can see how an `SB_MAC16` DSP has a ton of data path and
configuration signals. The multiplier inputs can be up to 16-bit wide and the output can be 32-bits.
It's up to a `techmap` step to assign all the right value to the configuration signals, and to 
correctly tie down unused input data bits or ignore excess output bits so that it
performs the desired 10-bit x 10-bit multiplication.

All Yosys commands are written in C++, but in the case of `techmap`, the specific mapping
operations are described in... Verilog! It's a very neat system that makes it possible for
anyone perform their custom mapping operations without the need to touch a line of C++.




