---
layout: post
title: Using Data2MEM to Update Your Spartan 6 RAM Contents
date:   2019-10-28 00:00:00 -0700
categories:
---

# Introduction

Most of my FPGA designs contain an small CPU system to manage aspects that would be too tedious to do in hardware.

A good example is configuring the Chrontel chips that are used to drive the DVI and HDMI output interfaces of
my [Pano Logic G2 board](https://github.com/tomverbeure/panologic-g2): they are controlled through an I2C 
interface and require a lot of registers to be set with the right value before they start outputting that data. 
You could do that through a HW I2C master and some FSM that transmits all the right values, of course, but why 
would you? It's much easier to use [some C code](https://github.com/tomverbeure/panologic-g2/blob/master/spinal/sw/dvi.c)
that [bit-bangs](https://github.com/tomverbeure/panologic-g2/blob/master/spinal/sw/i2c.c) its way through the 
I2C transactions using some GPIO pins!

One critical advantage of doing things this way is rapid iteration: not only is it much easier to write and 
modify C code, with the right setup, you can also dramatically shorten the loop between writing that code and 
trying it out on your hardware.

The key to this system is being able to change the program of that little CPU without needing to resynthesize 
the whole design: the compiled/synthesized bitstream simply gets patches with new RAM initialization content. 
It's a process that take seconds instead of minutes.

Different FPGAs vendors have different way of doing this.

Intel's Quartus software has the built-in option to simply change the initial contents of the RAM. In most 
circumstances, it's a painless process. 

![Quartus Update Memory Initialization File]({{ "/assets/xilinx_data2mem/quartus_update_mem.png" | absolute_url }})

When you're using Lattice FPGAs that are supported by the open source Yosys tools and project IceStorm, the 
process is a bit weird. It consists of [initially loading the RAMs with random contents](https://github.com/tomverbeure/rv32soc/blob/673fed4f1b0a398c5675f98c4badae239d54cc9f/blackice2/Makefile#L31-L41), 
going through synthesis, place and route, and bitstream generation, and then [patching the bitstream
to replace those random contents with the contents that you initially wanted](https://github.com/tomverbeure/rv32soc/blob/673fed4f1b0a398c5675f98c4badae239d54cc9f/blackice2/Makefile#L16-L20). 
But once it's not hard to set up.

For Xilinx, the old ISE tools are using a separate utility called *data2MEM*. Vivado uses *updatemem*. The Pano 
Logic G1 and G2 are using Spartan 3E and Spartan 6 FPGAs respectively, both of which require ISE, so I needed
to set up *data2MEM*. It's much more complicated that for Quartus or IceStorm.

This blog post explains how to set up data2mem to update a bitstream with new CPU firmware content.

# SpinalHDL and Verilog RAMs with RTL

All my embedded CPU systems are using a RISC-V CPU (usually a VexRiscv), which means that I'm using 32-bit 
wide RAMs. But since I use these RAMs both for program and data storage, they need to have byte-level write enables.

The canonical way in SpinalHDL to create a RAM is to use the declare an object of the `Mem` class, and then
use the `readWriteSync` method to reads and writes. Like this:

```
  val ram = Mem(Bits(32 bits), onChipRamSize / 4)
  io.bus.rsp.valid := RegNext(io.bus.cmd.fire && !io.bus.cmd.write) init(False)
  io.bus.rsp.data := ram.readWriteSync(
    address = (io.bus.cmd.address >> 2).resized,
    data  = io.bus.cmd.data,
    enable  = io.bus.cmd.valid,
    write  = io.bus.cmd.write,
    mask  = io.bus.cmd.mask
```

The presence of the `mask` parameter above tells the SpinalHDL that I want a RAM with byte enables.

Some FPGAs have block RAMs that with built-in support for byte enables, but not all of the do. To ensure maximum 
compatibility across FPGA families, SpinalHDL simply creates one RAM per byte enable. As a result, that was
declared above results in the following generated Verilog code:

```
  reg [7:0] ram_symbol0 [0:2047];
  reg [7:0] ram_symbol1 [0:2047];
  reg [7:0] ram_symbol2 [0:2047];
  reg [7:0] ram_symbol3 [0:2047];
```

The Xilinx ISE synthesis tool treats those as 4 individual RAMs.

# Xilinx ISE Block RAM inferencing

Xilinx will read the Verilog code for the RAMs above and map them on block RAMs. By default, it will do so 
with a focus on maximum speed. In practice, this means that will try as hard as possible to avoid a discrete 
multiplexer at the output of each block RAM.

Let's see what happens for different configurations.

If we want our CPU to have 8KB of RAM in a 32-bit wide/4 byte enable configuration, our Verilog will contains 4 
RAMs with a size of 2048 addresses and 8 data bits. The Spartan 6 FPGA that I'm currently using has block RAMs 
that can be configured as 512x36 bits, 1024x18 bits, 2048x9 bits, all the way to 16384x1 bits.

So our 2048x8 bits RAM will maps straight to a single block RAM, for a total of 4 block RAMs:

![8KB RAM organization]({{ "/assets/xilinx_data2mem/data2mem-8KB.svg" | absolute_url }})

If we increase the amount of CPU from 8KB to 16KB, we'll need 4 RAMs with a logical configuration of 4096x8. 
Each such RAMs will requires 2 physical block RAMs. But instead of mapping them to 2 2048x8 block RAMs, Xilinx 
maps them to 2 4096x4 RAMs. The 2048x8 configuration would require an additional multiplexer to select between
the outputs of one of the 2 RAMs, while the 4096x4 configuration does not!

![16KB RAM organization]({{ "/assets/xilinx_data2mem/data2mem-16KB.svg" | absolute_url }})

Note how Xilinx has added as suffix to the RAM instance name: logical RAM symbol0 has now become 2 instances
names `symbol01` and `symbol02`. *(It annoys me way more than it should that Xilinx starts counting at 1...)*

The story stays the same when you increase the amount of CPU RAM from 16KB to 32KB to 64KB. 

In the 64KB configuration, you need 4 logical RAMs of 16384x8 size. Each of those gets mapped on the 8 block RAMs
in 16384x1 configuration. The total amount of block RAMs is now 32. There is still no discrete MUX required between 
the output of multiple RAMs!

![64KB RAM organization]({{ "/assets/xilinx_data2mem/data2mem-64KB.svg" | absolute_url }})

The Spartan 6 LX150 and LX100 FPGAs of the Pano Logic G2 are huge, and with 268 block RAMs, you could assign more 
than 512KB of embedded RAM to your CPU!

But once you transition from 64KB to 128KB, you will need an output multiplexer to select between RAMs. Xilinx
ISE uses the following arrangment:

![128KB RAM organization]({{ "/assets/xilinx_data2mem/data2mem-128KB.svg" | absolute_url }})

Note how the MSB of the address bus (bit 16) is used to select between one block RAM or the other.

In terms of notation, since single 8-bit wide logical RAM `symbol0` requires 16 block RAMs, ISE simply
numbers them from 1 to 16, with 1 and 2 assigned to bit 0, 3 and 4 assigned to bit 1 and so forth.

We end up with RAMs `symbol01` to `symbol016`, `symbol11` to `symbol116`, `symbol21` to `symbol216`, and
`symbol31` to `symbol316`.

*If there is a document that describes the rules and the naming convention by which it creates the RAM structure
and names them, I could not find it. To figure it out, I had to synthesize a design with the RAM, and use the planAhead
schematic tool to analyze how large RAMs were built up out of block RAMs.*

![BRAM 32Kx8 schematic]({{ "/assets/xilinx_data2mem/BRAM_32Kx8_schematic.png" | absolute_url }})

# Describing the RAM Organization in a .BMM File

With the information that we've gathered above, we can now create a .BMM file.

The .BMM file describes how logical RAMs are built up out of multiple block RAMs. They are not only the primary
input to the *data2mem* tool, they can also be used during the mapping and place-and-route process.

*It would lead too far to describe all use cases (you can read the 
[Data2MEM User Guide](https://www.xilinx.com/support/documentation/sw_manuals/xilinx11/data2mem.pdf) for that).
In this blog post, I only the describe the workflow that worked best for me.*




