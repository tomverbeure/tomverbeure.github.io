---
layout: post
title: Simulation Save/Restore Checkpointing with CXXRTL
date:  2020-09-25 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In my [initial blog post about CXXRTL](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html), I
wrote about how the underlying data model of CXXRTL allow for 
[design introspection](2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html#design-introspection), and
how this could be used for save the design state to a file, and later restore it.

I wanted to try this out on a real example, so that's what I'll be discussing here.

The design is not a toy example, in that it contains a VexRiscv CPU with memories, LEDs, and a UART to
print out status messages.

# The CXXRTL Data Model

Creating a design checkpoint requires an understanding of how a CXXRTL model stores the data of all
state holding objects.

All of this can be derived from the [`cxxrtl.h`](https://github.com/YosysHQ/yosys/blob/master/backends/cxxrtl/cxxrtl.h).
At the lowest level, CXXRTL has 
[`value`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L84), 
[`wire`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L639), 
and [`memory`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L682) classes.
These are the basic primitives that contain simulated data values.

* `value`

    Used for objects that contain  a single simulation value.

    A `value` is always used to represent a combinatorial signal in your design (but not all
    combinatorial signals are represented by a `value`!)

* `wire`

    For objects that contain the current simulation value, and the next simulation value.

    In most cases, this will be an object that is used to store the contents of a flip-flop
    or a latch, but there are some cases where a `wire` is used for a combinatorial signal.
    The most common case for this is an output signal of a module.

* `memory`

    Self-explanatory: when using Verilog, this would be used to store an object that's declared
    as in `reg [7:0] memory[0:1023]`.

While one could use these objects directly when accessing the internal simulation values of a design,
it's not very partical: they don't have the same base class, and the way they store the simulation
data differs per class.

But that's ok, because there's a better way: the 
[`debug_item`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L826)
class exists specifically to allow external code to access the simulation values in a uniform way.

A `debug_item` exposes the following aspects of the simulation data holding objects:

* [`type`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L80)

    Whether the item is a `value`, `wire`, `memory`, or an `alias` (which maps one netlist item to another one
    with identical value.)

* [`flags`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L127)

    Contains all kind of attributes of the simulation object. The direction of module ports, whether or not a wire is
    driven by a storage cell, etc. 

* [`width`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L195), 
   and [`lsb_at`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L198)

    The size, in bits, of the value, and the bit number of the LSB.

    These values are essential to interpret the simulation data values.

* [`depth`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L201), 
    and [`zero_at`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L204)

    For memories, these indicates the amount of memory locations in the memory, and index of the first word.

    It's important that these have a meaningful value for  a `wire` or `value`: they're set to 1 and 0 resp.
    Since a `debug_item` has a uniform interface for all simulation data, one doesn't need to have special
    case to access data between the 3 storage classes: you can all assume them to be memories, but with only 1 location.

* [`curr`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L217),
    and [`next`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L218)

    These contain the actual simulation data!

    For a `wire` and `memory`, `next` is a null pointer.

    One can see that `curr` and `next` are stored as a `uint32_t` pointer. That's because the C++ classes ultimately
    use that as the way to store simulation data. 

    It's all pretty straifhtforward: the LSB of a vector is stored at bit 0 of the first uint32 word, and as many uint32 words
    are allocated to store all the bits of a vector.


