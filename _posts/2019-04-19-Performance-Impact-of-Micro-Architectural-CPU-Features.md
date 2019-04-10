---
layout: post
title: Performance Impact of Micro-Architectural CPU Features
date:   2019-04-19 10:00:00 -0700
categories:
---

* [Introduction](#Introduction)

# Introduction

In the early nineteen eighties, the canonical [classic RISC pipeline](https://en.wikipedia.org/wiki/Classic_RISC_pipeline) was born.
It splits up the CPU in 5 pipeline stages: instruction fetch (F), instruction decode (D), execution (E), 
data memory access (M) and, finally, result writeback (WB).

Today, this architecture is still the basis for most CPU architecture courses.  Real RISC CPU implementations can deviate considerably from this pipeline: stages may be split up even more to increase
clock speed, others merges stages to reduce area, the execution of some instructions may be spread over multiple stages, 
superscalar CPUs have multiple parallel stages, even more complex ones can issue out of order, etc.

When implementing CPUs, decisions must be made that trade off architectural efficiency (instructions per clock or IPC) vs
area (number of gates) vs clock speed as well as higher level features (MMU, interrupt handling).

The standard way to evaluate architecture efficiency is to create a performance model (usually written in C and ideally
cycle accurate). It'd be even better if you could run your code straight on the actual implementation.

Most CPU RTL code is not very configurable, but one stands out: the VexRiscv's novel design methodology makes it
possible to easily move logic from one stage to the next, to drop stages, to add or remove instruction and functional
units.

In this blog post, I'll explore the impact of different CPU configuration on the performance of the ubiquitous CoreMark
benchmark. I will also look at their impact on resource usage, and the clock speed of the synthesized logic.

# Micro-Architecture Features

The VexRiscv CPU has tens of different configuration option. Some of them are major in that they change the number
of pipeline stages, others are much lower level. An lower level example determines whether or not barrel shifter
logic is performed in just the execute stage or spread over the execute and memory stage.

Here are the feature that will be covered:

* Pipeline configurations 

    The number of pipeline stages can have a major performance impact. In the absence of bypass paths, a higher
    number of stages can reduce the IPC considerably, because each additional stage can result in an additional
    stall cycle when there are depending instructions.

    * Tradiditonal 5 stage F/D/E/M/WB pipeline
    * 4 stage pipeline with M and WB stages merged
    * 3 stage pipeline with E, M and WB stages merged
    * 




