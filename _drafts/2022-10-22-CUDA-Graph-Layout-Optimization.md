---
layout: post
title: Optimizing CUDA Graph Processing Performance by Modifying Memory Layout
date:  2022-10-22 00:00:00 -1000
categories:
---

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    jax: ["input/TeX", "output/HTML-CSS"],
    tex2jax: {
      inlineMath: [ ['$', '$'], ["\\(", "\\)"] ],
      displayMath: [ ['$$', '$$'], ["\\[", "\\]"] ],
      processEscapes: true,
      skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
    //,
    //displayAlign: "left",
    //displayIndent: "2em"
  });
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_HTML" type="text/javascript"></script>

* TOC
{:toc}

# Introduction

Ever since the introduction of the 8800 GTX in 2006, I've been fascinated by the
amount of raw compute power that resides inside GPUs, and I've always wanted to
do something 'real' with it: some kind of processing that would accelerate one's 
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
been one of the things I've wanted to try. I've already played with the 
[Yosys CXXRTL backend](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html)
that converts a Verilog RTL design into a simulatable C++ model. Surely, this can be
converted over to a GPU?

Fast forward to a couple of months ago when [Sylvain Lefebvre](https://twitter.com/sylefeb) created a 
[Silixel](https://github.com/sylefeb/Silixel): 
a crude but functional GPU-based logic simulator. He had the same idea of leveraging Yosys, but
took a different route of compiling the design into a sea of only low-level 4-input LUTs 
and FFs. 

Here's an example of Silixel simulating the rendering of pixels for a video output:

![Silixel simulation](/assets/cuda_sim/silice_vga_test.gif)

The background shows the image being rendered during simulatio. The flickering black and white dots 
are the state of the logic that's been simulated, cycle-by-cycle.

Silixel has a number of limitations that make it unqualified for practical use, 
but it's still an awesome base on which to build various GPU compute experiments.

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
  4-input lookup tables (LUTs).

    This conversion is a real synthesis step. Yosys writes out the synthesized netlist to a BLIF file, 
    after which Silixel take over.

* it reads the BLIF file into lists of LUTs and FFs.
* it merges LUTs and FFs into one single cell type that consists of a LUT and a FF. 
  Let's call that a LUT/FF cell.

    ![LUT + FF cell](/assets/cuda_sim/LUT_FF_cell.svg)

    The result is a directed graph where each node is a LUT/FF cell, and the edges of the graph
    are connections from a LUT/FF cell output to one of the 4 inputs of the next LUT/FF cell.

    [![Network of LUT/FFs cells](/assets/cuda_sim/Network_of_LUTFF_cells.png)](/assets/cuda_sim/Network_of_LUTFF_cells.png)
    *(Click to enlarge)*

    In this graph, not all inputs and not all outputs of a LUT/FF cell are connected: if the initial
    Yosys synthesis had a LUT output only go to a FF and not directly to any other LUT, then the 
    merged logic won't have anything connected to the D output of the LUT/FF cell.

    The graph has feedback loops, but only Q outputs of a LUT/FF cells are allowed to point
    backwards, otherwise you get a combinational loop which is something that should be
    avoided when doing digital design.

    The benefit of having only a single primitive cell is that a GPU simulation kernel only has to 
    simulate 1 kind of cell: they all behave the same way. This makes execution on a SIMD machine
    more regular and, hopefully, more efficient.

* Silixel then does a topological sort to determine the order in which cells must be evaluated so that
  each cell needs to be evaluated just once.

    For the graph above, there are 9 cell, each with a number from 0 to 8 that has been randomly
    assigned.

    If you'd evaluate the cells in numbered order, you'd have to do execute multiple
    evaluation loops before the result converges. In the example, you can see how 
    cell 1 is dependent combinatorially on the outputs of cells 0 and cell 5. If you'd evaluate
    cell 1 and cell 2before cell 5, and the output of cell 5 changes, then you'd have to evaluate
    cell 1 again... which in turn may require to evaluate cell 2 again!

    Topological sorting avoids that.

    In the graph below, the cell numbers have been reassigned in topological order. In a real
    implementation though, you wouldn't reorder, but keep a data structure with the correct order.

    [![Sorted network of LUT/FFs cells](/assets/cuda_sim/Sorted_Network_of_LUTFF_cells.png)](/assets/cuda_sim/Sorted_Network_of_LUTFF_cells.png)
    *(Click to enlarge)*

    Pay attention to cells 7 and 6, marked in red. Cell 6 depends on the Q output of cell 7.
    Does this mean that the topological sort is in correct? Not if the simulation has
    2 main steps: evaluation, where the simulator looks at the inputs to the LUTs to determine the
    next values of D. And copy, where the simulator copies the new D value into the Q element.

    From an evaluation point of view, a cell with only the Q output is considered no different
    than a cell that only drives the outputs of the circuit. It has no topologically dependent
    cells.

    There isn't just one unique topologically sorted order. Cells can be swapped as long
    as the evaluation order is maintained. Cell 0, for example, is similar to cell 7 in that
    only its Q output is connected to anything. We could move cell 0 to the back to the line,
    and move all other cells up one position and we'd still have a topologically sorted
    graph.  

    Once we can ignore the topological dependency on Q, we can flatten the graph:
    
    [![Flattened network of LUT/FF cells](/assets/cuda_sim/Flattened_Network_of_LUTFF_cells.png)](/assets/cuda_sim/Flattened_Network_of_LUTFF_cells.png)
    *(Click to enlarge)*

    The graph above is identical to the one before in terms of dependency. The signals that are 
    sourced by a Q output are dashed now to indicate that they don't need to be considered
    for sorting.

* Silixel separates the graph into layers so that all LUT/FFs cells with the same depth below to
  the same layer.  

    From the previous graph, it should be clear now that this circuit has an evaluation
    depth of 3. Cells 0, 1, 2, 5, 6, and 7 have a depth of 1. Cells 3 and 8 have depth of 2,
    and cell 4 has a depth of 3.

    All cells with the same depth are independent of each other, and can be evaluated in
    parallel!

    There are 6 cells in layer 0, 2 cells in layer 1, and 1 cell in layer 2. 

    It's not a strict requirement that a cell with a given depth gets assigned to the lowest
    possible layer. In the diagram below, the some cells have been shuffled to a higher layer 
    to make the layers more balanced:

    [![Alternate flattened network of LUT/FF cells](/assets/cuda_sim/Flattened_Network_of_LUTFF_cells_alt.png)](/assets/cuda_sim/Flattened_Network_of_LUTFF_cells_alt.png)
    *(Click to enlarge)*

    Same network, but now the each layer has 3 LUT/FF cells! 

    In general, the number of cells of a given depth will go down with increasing depth. There may
    be 10,000 cells of depth 1, 3000 of depth 2, and, say, only 18 cells of depth 10. For
    a massively parallel machine like a GPU that has thousands of SIMD lanes ('threads' in CUDA
    parlance), launching a thread group with just 18 threads will keep most of the machine sit
    idle. So there can be performance benefit to balancing the cells in different layers.

    *Silixel does not do such balancing, and assigns each cell the lowest possible depth.*
    

* finally, it asks the GPU to calculate the output of each LUT/FF one graph layer at a time, until
  all layers have been updated. 

    Such a sequence corresponds to simulating one clock cycle.

During the digital design phase, digital logic is always structured hierarchically, with modules that
are interconnected by interfaces that have a limited amount of signals. A netlist that comes out of 
Yosys is flat, with all hierarchy removed, but that doesn't mean that the nature by which cells are 
interconnected has changed. It's just that the hierarchical structure isn't explicit anymore.

# A Graph as a Matrix

It's common to represent the topology of a graph in an [adjacency matrix](https://en.wikipedia.org/wiki/Adjacency_matrix),
a square matrix with a row and a colomn for each graph node. Rows are the source of
an edge, columns a destination.

But before we do that, let's first simplify our circuit a little bit, for adjacency matrix
reasons only, by treating a graph node as something where you store the simulation values of
both D and Q, and by merging D and Q output edges.

Our circuit converts into the following graph of nodes and edges:

[![Simplified graph with nodes and edges](/assets/cuda_sim/Flattened_Network_as_Graph.png)](/assets/cuda_sim/Flattened_Network_as_Graph.png)

Note that there are nodes for inputs and cells but not for outputs. That's because the value 
of an outputs will always be the same as the value D or Q value of a cell.

Here's the adjacency matrix of the graph:

$$
A = 
\left[\begin{array}{ccc:cccccccc}
%0   1   2   0   1   2   3   4   5   6   7   8
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & \textbf{1} & 0 & \textbf{1} & 0 \\  % I0
 0 & 0 & 0 & \textbf{1} & \textbf{1} & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\  % I1
 0 & 0 & 0 & 0 & \textbf{1} & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\  % I2
\hdashline
 0 & 0 & 0 & \textbf{1} & 0 & 0 & \textbf{1} & 0 & 0 & 0 & \textbf{1} & 0 \\  % C0
 0 & 0 & 0 & 0 & 0 & \textbf{1} & \textbf{1} & 0 & 0 & 0 & 0 & 0 \\  % C1
 0 & 0 & 0 & 0 & 0 & 0 & 0 & \textbf{1} & 0 & 0 & 0 & 0 \\  % C2
 0 & 0 & 0 & 0 & 0 & 0 & 0 & \textbf{1} & 0 & 0 & 0 & 0 \\  % C3
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\  % C4
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & \textbf{1} & 0 & \textbf{1} \\  % C5
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\  % C6
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & \textbf{1} & 0 & 0 \\  % C7
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & \textbf{1} & 0 & 0 & 0 \\  % C8
\end{array}\right]
$$

Let's digest this!

There are 3 rows and columns for inputs 0 to 2, and 9 rows and columns 
for cells C0 to C8. 

The first row, assigned to input 0, looks like this:

$$\left[\begin{array}{ccc:cccccccc}
 I0 & I1 & I2 & C0 & C1 & C2 & C3 & C4 & C5 & C6 & C7 & C8 \\
 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 1 & 0 & \\  % I0
\end{array}\right]
$$

Input 0 only goes to cells 5 and 7, so the columns for C5 and C7 have a one. Repeat
this process for all inputs and cells, and you get the 12x12 adjacency
matrix.

One very important characteristic is that **the adjacency matrix is extremely sparse**. It has
to be like this because the number of inputs for a cell is limited to 4. Because of this
the maximum number of ones in a column of the matrix is limited to 4 as well. 
And while it's possible for a cell output go to more than 4 LUT inputs, when it does so, 
it will reduce the number of input slots for those LUTs by one.

In our example, no cell has more than 2 inputs, and there are only 16 ones
out of 144 matrix elements. For large designs, the sparsity will only increase.

We'll get back to this matrix soon.

# Arranging the Circuit Graphs in Memory 

GPUs are exceptional at two things:

* executing the same instruction in parallel on multiple pieces of data
* having large amount of DRAM bandwidth

The only way to achieve peak bandwidth from a DRAM is by generating transactions in a DRAM 
friendly way. Internally, a DRAM chip has a hierarchy of atoms, a set of bytes (usually 32), 
rows, and banks. 

[![GPU DRAM Hierarchy](/assets/cuda_sim/GPU_DRAM_Hierarchy.png)](/assets/cuda_sim/GPU_DRAM_Hierarchy.png)
*(Click to enlarge)*

Contrary to SRAM, you can't just fetch bytes in a random order and expect maximum performance.
If you need to fetch just 1 byte from DRAM, its memory controller must first
open the row in the bank in which the atom resides, and then fetch a burst of 32 bytes. If
a byte from a different row in the same bank is needed next, the memory controller
must then close ("precharge") the previous row, and start all over again.

The overhead of Opening and closing a row can be hidden when the memory controller
can schedule transactions to different banks, but peak effective memory bandwidth 
can only be achieved when as many bytes as possible can be fetched from the same row 
in one go.

That's why GPU memory controllers have huge transaction sorters that queue up a
bunch memory requests and group together request from the same row so that they can be
executed on the DRAM together, requiring opening and closing the row only once for the
whole group.

[![DRAM Transaction Reordering](/assets/cuda_sim/Transaction_Reordering.png)](/assets/cuda_sim/Transaction_Reordering.png)
*(Click to enlarge)*

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

# The Basic Graph Update Algorithm and a Naive Memory Organization

When all LUT/FF cells have been assigned their proper layer so that each LUT only needs to
be evaluated once, the overall simulation algorithm can be reduced to this:

```c
    init_q_values();
    while(!end_of_simulation){
        for(l in layers){
            evaluate_layer(l);
        copy_d_to_q();
    }
```

In its most straightforward form, each cell has the following data associated with it:

```c
struct graph_node_s {
    uint32_t    input_indices[4];
    bool        d_or_q[4];
    uint16_t    lut_config;
    bool        d;
    bool        q;
};
```

All the cells are stored in a simple array:

```c
struct graph_node_s graph_nodes[number_of_nodes_in_graph];
```

And you'd simulate a single clock cycle with the following pseudo code:

First recalculate the combinatorial values for all layers:
```c
evaluate_layer(layer){
    for(node in layer){

        lut_sel = 0;
        for(i=0; i<4; ++i){
            input_node = graph_nodes[node.input_indices[i]];

            lut_sel |= (node.d_or_q[i] ? input_node.d : input_node.q) << i
        }

        node.d = node.lut_config >> lut_val;
    }
}
```

When all layers have been processed, the d values are copied over into the q values:

```c
copy_d_to_q(){
    for(node in graph_nodes){
        node.q = node.d
    }
}
```

One thing is clear: the actual calculation effort to evaluate the value of a cell is very low and little
more than a few shift operations. The heavy lifting consist of hauling data in an out of memory!  
Each cell has 24 byte of data. All this data must be read at least ones, and some of it, d and q,
must be written back as well.

What's worse is that the data isn't laid out in an access smart way. 

Fetching the information of graph nodes that are being evaluated is extremely efficient, because all the nodes
of a layer are processed in sequence. 

[![Naive graph memory allocation](/assets/cuda_sim/naive_graph_node_allocation.png)](/assets/cuda_sim/naive_graph_node_allocation.png)
*(Click to enlarge)*

But fetching the D and Q data from the input nodes is terrible even if the node under evaluation request 4
nodes that are located right next to each other. Remember that DRAM data must be accessed in atoms which are
at least 32 bytes in size. When fetching, the 4 D and Q values are needed to evaluate a single cell,
the CPU or GPU will need to fetch 96 bytes!

The issue here is a classic computer science issue: the memory access inefficiency of an *array of structs*.

Let's do something about it.

# A Struct of Arrays

We can easily modify the data structures so that memory gets accessed with better efficiency by organizing
things as a struct of arrays.

```c
struct graph_s {
    struct graph_node_static_s {
        uint32_t    input_indices[4];
        bool        d_or_q[4];
        uint16_t    lut_config;
    } static_info[number_of_nodes_in_graph];

    struct graph_node_dynamic_s {
        bool        d;
        bool        q;
    } dynamic_info[number_of_nodes_in_graph];
};
```

There are now 2 arrays: one has a struct with static information about the network: the inputs of a node,
whether to use the D or Q output of such an input cell, and the configuration of the LUT. And the other
array contains the D and Q values of each cell.

In memory, it looks like this:

[![Smarter graph memory allocation](/assets/cuda_sim/smarter_graph_node_allocation.png)](/assets/cuda_sim/smarter_graph_node_allocation.png)
*(Click to enlarge)*

Due to padding reasons, there are still 24 bytes allocated per cell for static information.

With the new organization, if the 4 input nodes are located right next to eachother, the processor can fetch 4 input values by fetching
just 1 instead of 3 32-byte atoms.

It gets better: the input nodes don't even have to right next to each other, as long as they're located in the same atom, they can
all be fetched together:

[![D and Q values in the same atom](/assets/cuda_sim/d_and_q_values_in_the_same_atom.png)](/assets/cuda_sim/d_and_q_values_in_the_same_atom.png)

*(Click to enlarge)*

Right now, we're still quite wasteful with memory.

* We only need 1 bit to select the D or the Q value of an input

* We are using one byte to store D and one to store Q.

    We can store both values in 1 byte.

The data structure now looks like this:

```c
struct graph_s {
    struct graph_node_static_s {
        uint32_t    input_indices[4];
        uint16_t    lut_config;
        uint8_t     d_or_q;
    } static_info[number_of_nodes_in_graph];

    struct graph_node_dynamic_s {
        uint8_t     d_and_q;
    } dynamic_info[number_of_nodes_in_graph];
};
```

That's 19 bytes, padded to 20 bytes, per node of static and 1 byte for dynamic information. 

[![Smart graph memory allocation](/assets/cuda_sim/smart_graph_node_allocation.png)](/assets/cuda_sim/smart_graph_node_allocation.png)
*(Click to enlarge)*

It's tempting to store 4 d/q pairs in a single byte, but this would introduce synchronization issues when multiple
GPU threads try to read and write the different bits within the same byte.

A DRAM fetch of a single 32-byte atom will now grab 32 d/q pairs. This relaxes the data allocation requirements once
more when shooting for optimal bandwidth efficiency. But it gets better once again: on a GPU, on a single streaming
multiprocessor, 32 threads are fetching data at the same time. And data that's being fetched by one thread can be 
accessed without penalty by another in the same thread group.

[![Thread group DQ fetch](/assets/cuda_sim/thread_group_dq_fetch.png)](/assets/cuda_sim/thread_group_dq_fetch.png)

*(Click to enlarge)*

In the example above, 12 threads, each with its own color, are fetching data from inputs that all happen to fall 
within the same 128 bytes. With a 32-byte atom, the GPU only needs to fetch 4 atoms to acquire all the d/q values.

And then there's the GPU cache hierarchy: modern GPUs have large L2 caches, 4GB on my RTX 3070, and an astonishing 
72MB on an RTX 4090, and pretty large L1 caches per SM as well. Even when LUT/FF cells have input nodes that are
directly adjacent, it's sufficient that they are located close enough to get decent performance.

