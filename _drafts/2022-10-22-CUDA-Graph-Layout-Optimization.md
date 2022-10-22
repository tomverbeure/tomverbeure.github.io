---
layout: post
title: Optimzing CUDA Graph Processing Performance by Modifying Memory Layout
date:  2022-10-22 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Ever since the introduction of the 8800 GTX in 2006, I've been fascinated by the
amount of raw compute power that resides inside GPUs, and I've always wanted to
do something 'real' with it: some kind of processing that would accelerate somebody's 
day-to-day job.

I work for Nvidia, so learning and using CUDA for this is an obvious choice. 
The first requirement to make something like this happen is ownership of an Nvidia
GPU. That's by far the easiest part, so over the years I've been the proud owner of
an 8600 GTS, a GTX 460, a GTX 770, a GTX 1060, and currently an 
[RTX 3070](https://www.nvidia.com/en-us/geforce/graphics-cards/30-series/rtx-3070-3070ti/). 
And believe it or not, other than using the GTX 460 to play Battlefield 3, all these GPUs were
bought with the intention of learning CUDA and giving them a healthy GPU compute workout.
But I never got any farther than running some of the CUDA SDK examples...

Learning is easier when you have an actual project. Digital logic simulation is a topic that 
closely matches my general hobby and work interests, so creating a GPU based logic simulator has
always been one of the things I've wanted to try. I've already played with the 
[Yosys CXXRTL backend](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html)
that converts a Verilog RTL design into a simulatable C++ model. Surely, this can be
converted over to a GPU?

Fast forward to a couple of months ago when Sylvain Lefebvre created a 
[Silixel](https://github.com/sylefeb/Silixel): 
a crude but functional GPU-based logic simulator. He had the same idea of leveraging Yosys, but
took a different route of compiling the design into a sea of only low-level 4-input LUTs 
and FFs. Silixel has a number of limitations that make it unqualified to use for anything 
practical, but it's still an awesome base on which to build various GPU compute experiments.

So rather than a grand goal of building a best-in-class RTL simulator, I decided to start
with Silixel, make incremental improvements and see where that got me:

* convert Silixel from OpenGL-based compute to CUDA
* analyze performance bottlenecks
* improve performance 

At least, that was the initial plan, but the whole exercise quickly veered into the
much narrower topic of studying memory traffic and optimizing memory access patterns on a 
GPU while processing nodes of a graph.

In this blog post, I'm writing down some of what's I've learned.

# Inside Silixel - Simulating Low Level Digital Logic on a GPU

You should check out the [Silixel README](https://github.com/sylefeb/Silixel) for a detailed explanation
of how it does gate-level simulation, but here's a summary:

* Silixel first uses Yosys to convert Verilog design into a network of flip-flops (FFs) and 
  4-input lookup tables (LUTs). u

    This conversion is a real synthesis step. Yosys writes out the synthesized netlist to a BLIF file, 
    after which Silixel take over.

* it reads the BLIF file into lists of LUTs and FFs.
* it merges LUTs and FFs into one single cell type that consists of a LUT and a FF. 

    The result is a directed graph where each node is a LUT/FF cell, and the edges of the graph
    are connections from a LUT/FF cell output to one of the 4 inputs of the next LUT/FF cell.

* it does a topological sort to determine the order in which cells must be evaluated so that
  each cell needs to be evaluated just once.

* it separates the graph into layers so that all LUT/FFs cell within the same layer can be
  calcaluted in parallel without dependencies between them.
* finally, it asks the GPU to calculate the output of each LUT/FF one graph layer at a time, until
  all layers have been updated. 

    Such a sequence corresponds to simulating one clock cycle.

During the digital design phase, digital logic is always structured hierarchically, with modules that
are interconnected by interfaces that have a limited amount of signals. The netlist that comes out of 
Yosys is flat, with all hierarchy removed, but that doesn't mean that the nature by which cells are 
interconnected has changed. It's just that the hierarchical structure isn't explicit anymore.

The graph of a netlist of LUTs is necessarily sparse: in our case, the number of inputs is fixed
at 4 inputs, so the number of nodes that can feed the next node is inherently limited to 4,
limiting the total number of graph edges of 4 times the number of graph nodes.

# Graphs Arranged in Memory as Arrays 

GPUs are exceptional at two things:

* executing the same operation in parallel
* having large amount of DRAM bandwidth

Due to the nature of DRAM, the only way to extract its bandwidth is
by presenting transactions in a DRAM friendly way. Internally, DRAM chip
have a hierarchy of atoms (a set of bytes), rows, and banks. Contrary
to SRAM, you can't just fetch bytes in a random order and expect maximum performance.
If you need to fetch just 1 byte from DRAM, the GPU memory controller must first
open a row in the bank in which it resides, and fetch a burst of 32 bytes. If
a byte from a different row in the same bank is needed next, the memory controller
must then close ("precharge") the previous row, and start all over again.
Opening and closing a row is overhead that can be hidden if the memory controller
can schedule transactions to different banks, but it should be clear that optimal 
effective memory bandwidth can be achieved if as many bytes as possible can be fetched 
from the same row in one go.

That's why GPU memory controllers have huge transaction sorters that queue up a whole
bunch memory requests and group together request from the same row so that they can be
executed on the DRAM together, requiring opening and closing the row only once for the
whole group.

There are multiple ways to store graphs in memory. A very naive way would be to allocated
memory for each node individually and, for each input, have a pointer to the node that's
connected to it. However, this would make it very awkward to randomly select a particular
node, and there'd be a lot of overhead just to manage the memory allocations for so many
nodes. It's a bit like linked lists: they're a basic building block that's extensively
covered in computer science, but hardly ever used in actual code. Similarly, graphs
are usually stored as arrays, with an input of a node at a particular index pointing to
a node with another index.

To process the layered graph of our netlist, all the nodes are grouped in this netlist
layer by layer. Since all nodes of the same layer can be processed in parallel without
interfering with eachother, this makes it extremely easy to pass along the nodes to the GPU:
you just indicate the start and the end index of the array to the GPU, and the GPU can
just process all the nodes that lay in between.

# The Basic Graph Update Algorithm

The most straightforward way to store the graph could be something like this:

```c
struct graph_node {
    int 	input_idx[4];
    bool 	comb_or_ff[4];
    uint16_t 	lut_config;
    bool 	comb_value;
    bool 	ff_value;
};

struct graph_node graph[number_of_nodes_in_graph];
```

And you'd simulate a single clock cycle with the following pseudo code:

First recalculate the combinatorial values for all layers:
```c
for(l=start_layer; l<=end_layer; ++l){
    for(node_idx=layer[l].start; node_idx<layer[l].end;++node_idx){
        node = graph[node_idx];
	lut_sel = 0;
	for(i=0; i<4; ++i){
	    input_node = graph[node.input_idx[i]];
            lut_sel |= (node.comb_or_ff[i] ? input_node.comb_value : input_node.ff_value) << i
	}
	graph.comb_value = node.lut_config >> lut_val;
    }
}
```

Then ripple copy over the combinatorial values to the flip-flop values:

```c
for(node_idx=0;node_idx<number_of_nodes_in_graph;++node_idx){
    graph[node_idx].ff_value = graph[node_idx].comb_value;
}
```

