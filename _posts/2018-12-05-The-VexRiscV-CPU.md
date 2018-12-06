---
layout: post
title:  The VexRiscV CPU
date:   2018-12-05 17:00:00 -0700
categories: RTL
---

# Table of Contents

* [Introduction](#introduction)
* [Designing a CPU the Traditional Way](#designing-a-cpu-the-traditional-way)
* [The VexRiscV Plugin Architecture](#the-vexriscv-plugin-architecture)


# Introduction

In an earlier [blog post](/rtl/2018/08/12/SpinalHDL.html), I made a few references
to the VexRiscV, a RISC-V CPU that has been implemented completely in SpinalHDL. 

At some point, I created the [rv32soc](https://github.com/tomverbeure/rv32soc) project,
where I wanted to compare different RISC-V CPUs against eachother. I also used the
VexRiscV as a point of comparision against my own RISC-V CPU, the 
[MR1](/risc-v/2018/11/19/A-Bug-Free-RISC-V-Core-without-Simulation.html). The MR1
was no match for the VexRiscV by any possible metric.

In the process, I spent some time trying to understand the internal of the CPU, and
the way it was designed. I came back incredibly impressed. Not only does the
VexRiscV CPU provide a plethora of performance and functionality knobs, it
implements those in a way that truly shows the limits of traditional RTL languages
such as Verilog, SystemVerilog and VHDL.

The VexRiscV code demonstrates how one can write RTL that is at the same time as
efficient as the most optimized Verilog, yet at the same time extremely configurable.

That said: understanding the VexRiscV code base is not for the faint of heart. It leverages
all the features of a traditional objected programming language, Scala, to make the
magic happen. And because it does not follow the standard practices by which a CPU
is designed, it took me a while to really get it.

This goal of this article to explain why the VexRiscV design is so important and
innovative.

# Designing a CPU the Traditional Way

In order to understand the novelty of the VexRiscV design, it's helpful to contrast it
against traditional CPUs of the same class: a standard pipeline, in-order, single issue etc.

There are plenty of open source examples.

If you're reading this you probably have some understanding about the standard parts
of the traditional RISC cpu: instruction processing is split up into a number of so-called 
pipeline stages. Each pipeline is responsible for part of whole operation. The more
stages, the lower that amount of work that needs to be done per stage, which
reduces the depth of the logic per stage, which ultimately results in a design that
can run at a higher clock speed.

The original [RISC CPU](https://en.wikipedia.org/wiki/Classic_RISC_pipeline) had 5 stages, but
you can find RISC CPU with 2 to 11 (or more?) pipeline stages!

It should come as no surprise that the design of such CPUs matches this pipeline architecture:
if the CPU has a 'FETCH' stage, the RTL will have a corresponding 'FETCH' Verilog module
as well.

A good example of a well-designed open source RISC-V CPU is the [RI5CY CPU](https://github.com/pulp-platform/riscv)
of the pulp platform. If you looks at the [source code directory](https://github.com/pulp-platform/riscv/tree/master/rtl),
you can immediately see a lot of the expected functional blocks: there's riscv\_if\_stage.sv, 
riscv\_id.sv, riscv\_ex\_stage and so forth.

![RI5CY directory]({{ "/assets/vexriscv/00-ri5cy-directory.png" | absolute_url }})

All these traditional functional blocks are tied together in riscv\_core.sv.

Perfect, right?

Well, yes, it's not a bad way of doing things, but it does have a few issues: since everything
is grouped by pipeline stage, it is *not* grouped by functionality.

Take a multiplier, for example. The MUL instruction is decoded in the 
[`decoder`](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_decoder.sv#L88)
module which resides under `id`.
The result is [`mul_operator_ex_o`](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_id_stage.sv#L128),
along with a bunch of additional signals such as operands, and various control signals.

In riscv_core.sv, this signal is then connected from the `id` stage to the `ex`
stage which it enters as 
[`mult_operator_i`](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_ex_stage.sv#L67).
Inside the `ex` stage, it's then routed to 
the ['riscv_mult'](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_ex_stage.sv#L290-L320)
where the actual multiplication happens, with the `result_o` signal as output.

Inside riscv_ex.sv, it's connected to [`mult_result`](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_ex_stage.sv#L315)
where it enters a [multiplexer](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_ex_stage.sv#L210-L211)
that selects between different ALU results into the `regfile_alu_wdata_fw_o` signal which goes back to the
`id` block, where it's used to 
[write the result](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_id_stage.sv#L966)
back into the register file and in the [forwarding logic](https://github.com/pulp-platform/riscv/blob/0a5bb35a4fd63123838978c54d65c8aa5a446756/rtl/riscv_id_stage.sv#L636).

Phew! That's a lot hierarchy to travel. All these signals need to be assigned to ports, wired up etc. With 
more modern RTL languages like SystemVerilog, you can reduce the amount of wiring up by grouping
things into structs or interfaces.

But what's common everywhere is that 
**the implementation of a specific piece of functionality, a multiplication, is spread among many different files**.

![Simple Multiplier Traditional]({{ "/assets/vexriscv/VexRiscV-drawings-mul_simple_traditional.svg" | absolute_url }})

An FPGA often has hardware multiplication blocks that can run at very high clock speeds. However, 
those speeds can only be reached if the multiplier is surrounded by registers: one at the input, and one at the
output. 

If we want to maintain a throughput of one instruction per clock, but also spread the multiplication over 2 clock
cycles, we need to do something like this:

![Complex Multiplier 1 Traditional]({{ "/assets/vexriscv/VexRiscV-drawings-mul_complex_1_traditional.svg" | absolute_url }})

Furthermore, these multipliers are usuall restricted to 18x18 bits. If you need a 32x32 multiplier,
as is the case for most 32-bit CPUs, you need to construct them with [multiple 18x18 multiplier blocks](/rtl/2018/08/11/Multipliers.html).

To reach the desired clock speeds, that often means even more register stages. For example, like this:

![Complex Multiplier 2 Traditional]({{ "/assets/vexriscv/VexRiscV-drawings-mul_complex_2_traditional.svg" | absolute_url }})

In the 5 stage pipeline above, we're abusing the MEMORY and WRITEBACK stage to improve the clock speed of the CPU.
We also need to make changes to the FETCH and the DECODE stages to the forwarding and hazard checking logic.

The more we do this, the more files we need to touch, and the more ports need to be added.

That's not a huge deal if you have a very clear, well defined architecture in mind, but **it 
quickly becomes a maintenance nightmare if you want something highly configurable**: if the clock speed
requirements of the CPU are modest, you might want to have the multiplication located entirely in the EXECUTE
stage, while choosing the last option for a very fast one.

Which raises the question: is there a better way?

# The VexRiscV Plugin Architecture



