---
layout: post
title: Building Multiport Memories with Block RAMs
date:   2019-06-24 10:00:00 -0700
categories:
---

* [Introduction](#introduction)
* [Multiple-Read, Single-Write RAMs](#multiple-read-single-write-rams)
* [Flip-Flop RAMs](#flip-flop-rams)

# Introduction

On-chip memories are one of the key ingredients of digital design.

In an ASIC design environment, you are typically offered a library of various configurations:
single read/write port, single read/single write ports, sometimes dual read/write ports.

Once you go beyond that, you enter the realm of custom RAMs: whatever you need gets hand crafted
by your RAM design team. An expensive proposition, so you better
have a really good reason to need one!

It's unusual to have a conceptual RAM like the one below readily available: one with 2 independent write ports
and 2 independent read ports.

![Highlevel View]({{ "/assets/multiport_memories/xor_memory-Highlevel_View.svg" | absolute_url }})

In FPGA land, things are more limited: you get to use what the FPGA provides and that is that.

If we ignore RAMs that are constructed out of repurposed LUTs and registers, most FPGAs
have so-called block RAMs (BRAMs) that have at least a single read and a single, separate,
write port. FPGAs from Intel and Xilinx usually have 2 full read/write ports, but the Lattice
iCE40, popular in the open source world, only has one read and one write port.

Unfortunately, not all design problems can map to the standard BRAMs of the FPGA of your
choice.

The register file of a simple CPU will almost certainly require at least 2 read ports and
1 write port, a number that increases for multiple issue CPU architectures. And all those
ports need to be serviced at the same time.

In this blog post, I go over the some common ways in which multiple read and write port
memories can be constructed out of standard BRAMs. I then describe a really interesting
way in which they can be designed without any major restrictions other than the number
of BRAMs in your FPGA.

All RAMs will have the following behavior:

* synchronous reads only: a read operation will return the result one clock cycle later
* single direction ports only: most of the techniques discussed here can be expanded to bidirectional
  ports as well, but it would expand the scope of this post too much.
* reads and writes to the same address during the same clock cycle return the newly written value
* multiple writes through different ports to the same address result in undefined behavior, even
  if the same value is written on both ports.

Translated to an example waveform:

![RAM Behavior Waveform]({{ "/assets/multiport_memories/ram_behavior.svg" | absolute_url }})


This blog post is *heavily* based on the
[Composing Multi-Ported Memories on FPGAs](http://people.csail.mit.edu/ml/pubs/trets_multiport.pdf)
paper by [Eric LaForest](https://twitter.com/elaforest), Zimo Li, Tristan O’Rourke, Ming G. Liu, and J. Gregory Steffan.
Images from this paper have been used with permission. Eric's website has a [whole section](http://fpgacpu.ca/multiport/index.html)
dedicated to just this topic!


# Multiple-Read, Single-Write RAMs

Register files or RAMs with multiple read ports and only a single write port are very common in small CPUs
that can only retire one instruction per second: multiple read ports to gather the operands
for an instruction, yet you only need 1 write port to write back the result of the instruction.

The implementation on FPGA is simple: you use 1 BRAMs per read port and you connect the write ports
of all BRAMs together.

![3 Read - 1 Write]({{ "/assets/multiport_memories/xor_memory-3r_1w.svg" | absolute_url }})

Coincident reads and writes to the same address can often be dealt with by the memory generator
of your FPGA. For example, the Intel Stratix 10 has the
[Coherent Read](https://www.intel.com/content/www/us/en/programmable/documentation/vgo1439451000304.html#jrz1522207840091)
feature.

If not, you may have to design forwarding logic yourself. In the words of the paper:

> Forwarding logic bypasses a BRAM such that, if a write and a read
operation access the same location during the same cycle, the read will return the new
write value instead of the old stored value. To remain compatible with the expected
behavior of a one-cycle read-after-write latency, we register the write addresses and
data to delay them by one cycle.

The coincident read/write problem is not specific to having multiple read ports: it's
something to be aware of whenever you use dual-ported memories.

Personally, whenever I use dual-ported memories, I simply try to avoid coincident read/writes.
Either by making them impossible at the architectural level, or by imposing a requirement
on the user to never do such a thing. (Don't hold it that way!)

# Flip-Flop RAMs

The trivial solution to create memories with multiple read and write ports is not use any RAMs at
all, and use flip-flops instead.

It's a solution that is often used when implementing registers files of CPUs that have more than one write
port.

On a RISC-V CPU with 32 32-bit registers, it will cost you 1024 FFs.

For M write ports and N read ports, you'll also need an M-to-1 multiplexer and an N-to-1 multiplexer
for each storage bit. And a truckload of wiring wiring to connect everything together!

This doesn't have to be a problem: the [SWeRV](https://tomverbeure.github.io/2019/03/13/SweRV.html) CPU
has a dual-issue pipeline that can retire 2 instructions per clock cycles. And since instructions
typically require 2 operands, it requires a register file with 4 read ports and 2 write ports.

This translates into 1024 FFs, 1024 2-to-1 write and 1024 4-to-1 read MUXes, yet if you look at the
ASIC layout, the register file, the orange region below marked *ARF*, only takes about 9% of the total CPU core area.

![SweRV Core Physical Design]({{ "/assets/swerv/slides/13 - SweRV - SweRV Core Phyiscal Design.png" | absolute_url }})

The important caveat is that the SWeRV was designed for an ASIC process, where metal layers are
plentiful and dense rats nets of wires are usually not a problem.

Translate this design to an FPGA, which often have routing wires as a constrained resource, and you'll
run into trouble very quickly! Not only will the memory be difficult to place and route, it may
also quickly become a critical path of your overall design. Still, as Eric's paper shows, for a
register file of such a small size, pure FFs are usually the way to go.

Note though that 4 read and 2 write ports isn't particularly high for a modern CPU: The 512 x 64 bits
register file of the ancient Alpha 21464 CPU had 16 read and 8 write ports, with an area cost that was 5x
the area of the 64KB data cache!

# Banking

With banking, you split one large memory into multiple smaller ones. Each memory bank stores
only its fraction of the total memory.

For example, if you need 2 write ports, you could store the data for all even addresses to
bank M0 and the data for all odd addresses to bank M1.

As long as you can guarantee that the 2 concurrent writes will consist of a write to an even address
and a write to an odd address, you will reach a peak write bandwidth of 2 writes per clock cycle.

The problem with this is that this can't always be guaranteed: 2 writes that go to the same bank
will result in a so-called *bank conflict*, and you will be forced to serialize the 2 writes over
2 clock cycles and stall the pipeline.

You can reduce the chance of a banking conflict by increasing the number of banks. They don't have to equal
to the number of write ports. For uniformly spread write addresses, a higher number of banks will lower
the chance of a bank conflict.

The memory below has 2 write ports, 1 read port, and 4 banks. Notice how the read data output
multiplexer is controlled the 2 LSBs of `rd0_addr`, and how there is a signal for each write port
to stall the transaction.

![Banked Memory]({{ "/assets/multiport_memories/xor_memory-banked_mem_2w_1r_4b.svg" | absolute_url }})

Alternatively, when the writes come in bursts with idle cycles in between, you could add a FIFO to buffer
serialized writes and avoid stalls, but then you'd also need to logic to check that reads don't fetch data
that's temporarily stored in that pending-write FIFO.

In a CPU that supports out-of-order issue, you could also try to schedule instructions such that
coincident writes to the same bank are avoided as much as possible. Or you might even create an
optimizing compiler that orders instructions such that banking conflicts are reduced!

Banking is not only a potential solution for multiple write ports, but for multiple read ports as well.
[This blog post](https://devblogs.nvidia.com/using-shared-memory-cuda-cc/) on shared memories in Nvidia
GPUs has a section on bank conflicts and how to avoid them.

Either way, things will get complex very quickly. And sometimes your design is such that stalling
the write pipeline is impossible, yet banking conflicts can't be avoided.

A different solution is needed.

# Live Value Table

# XOR-Based Approach

# References

* [Multi-Ported Memories for FPGAs](http://fpgacpu.ca/multiport/)

    Overview of research in this field

* [Efficient Multi-Ported Memories for FPGAs](http://www.eecg.toronto.edu/~steffan/papers/laforest_fpga10.pdf) (LaForest, 2010)
* [Multi-Ported Memories for FPGAs via XOR](http://fpgacpu.ca/multiport/FPGA2012-LaForest-XOR-Paper.pdf) (LaForest, 2012)
* [Composing Multi-Ported Memories on FPGAs](http://people.csail.mit.edu/ml/pubs/trets_multiport.pdf) (LaForest, 2014)
* [A Scalable Unsegmented Multiport Memory for FPGA-Based Systems](https://www.hindawi.com/journals/ijrc/2015/826283/) (Kevin R. Townsend, 2015)

* [Banked Multiported Register Files for High-Frequency Superscalar Microprocessors](https://pdfs.semanticscholar.org/d3f7/adf7eb46fbb405dcb3cd77fc87cbddb2341c.pdf) (Tseng, 2003)
