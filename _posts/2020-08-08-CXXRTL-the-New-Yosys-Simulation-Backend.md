---
layout: post
title: CXXRTL, a Yosys Simulation Backend
date:  2020-08-08 00:00:00 -1000
categories:
---

* TOC
{:toc}

# The Open Source Simulation Status Quo

For my open source RTL projects, I've so far only used 2 Verilog simulators: 
[Icarus Verilog](http://iverilog.icarus.com/) and [Verilator](https://www.veripool.org/wiki/verilator).

Icarus Verilog is a traditional event-driven simulator with support for most of the behavioral Verilog constructs that
can be found in complex Verilog testbenches: delays, `repeat` statements, etc. If you can look past its simulation
speed (it's *very* slow), it does the job pretty well, and allows one to stay within a pure Verilog environment just
like you would with commercial tools such as VCS, Modelsim etc.

Verilator is a completely different beast: it's a cycle based simulator that, with some exceptions, only takes
in synthesizable RTL, removes all notions of time or delays, and simulates from one cycle to the next. Cycle
based simulators are much faster than event driven ones, and Verilator is one of the best in class that
routinely beats commercial simulators. Verilator compiles your Verilog design into a bunch of C++ files and
then into a linkable library. All you need to do is write a C++ wrapper (which can be very small) that
calls the library for each simulation step, and you're on your way. ZipCPU has [a very good Verilator
tutorial](https://zipcpu.com/blog/2017/06/21/looking-at-verilator.html).

Verilator can be 500x faster than Icarus Verilog. When the simulation time of my projects gets too
long, I usually switch from Icarus to Verilator.

Icarus and Verilator aren't the only open source Verilog simulators, but they are the most popular by far. And
for good reason: Wikipedia [lists](https://en.wikipedia.org/wiki/List_of_HDL_simulators#Free_and_open-source_simulators) a number
of alternatives, but one constant between them is the lack of support for modern Verilog features. I've
never seen anybody use them...

# Yosys, the Swiss Army Knife of Digital Logic Manipulation

Yosys is the star of the open source synthesis world. It initially rose to prominence with the release of 
[Claire Wolff](http://www.clifford.at/)'s [Project IceStorm](http://www.clifford.at/icestorm/), 
where it's the synthesis component of an end-to-end open source RTL to bitstream flow for Lattice ICE40 FPGAs. 

But Yosys is much more than that.

It's a swiss army knife of digital logic manipulation that takes in a digital design through one of its so-called frontends 
(Verilog, blif, json, ilang, even VHDL and SystemVerilog for the commercial version), provides tons of different passes that transform 
the digital logic one way or the other (e.g. flatten a hierarchy, remove redundant logic, map generic gates to 
specific technology gates, check formal equivalence), and a whole bunch of backends that write the final design in 
some desired format (Verilog, Spice, json, SMT2, etc.)

If you have a blob of synthesizable digital logic and you need to perform some kind of transformation, chances are that Yosys
already supports it.

Yosys' commands are relatively well documented, but, unfortunately, the documentation snapshots on 
[the official Yosys website](http://www.clifford.at/yosys/documentation.html) are often woefully behind. 

To get the latest and greatest list of commands, it's best to just compile Yosys and use the `help` function
from the command line of the tool.

*The amount of information can be overwhelming (there are a large amount of commands that I don't quite understand
myself), but, luckily, it's not necessary to understand most of the commands: in many cases, it's sufficient to use
ready-made recipes to go from RTL to a synthesized gate-level netlist.*

# CXXRTL, a New Simulation Backend

[CXXRTL](https://github.com/YosysHQ/yosys/tree/master/backends/cxxrtl) is a new Yosys backend. It writes out 
the digital logic inside Yosys as a set of C++ classes, one for each remaining module, after performing whichever 
transformation pass you want to apply.

In combination with [`cxxrtl.h`](https://github.com/YosysHQ/yosys/blob/master/backends/cxxrtl/cxxrtl.h),
a single C++ include file with template classes that implement variable width bitvector arithmetic, the C++ classes become a 
simulation model of the digital design.

Just like with Verilator, the simulation model is cycle-based. And just like Verilator, you need to provide a thin
C++ wrapper that calls these classes to perform a step-by-step simulation.


# Quick Start: From Verilog to Simulation

Going from Verilog to running a simulation is straightforward. 

1. Create an example design `blink.v`:

    ```verilog
    module blink(input clk, output led);
    
        reg [11:0] counter = 12'h0;
    
        always @(posedge clk) 
            counter <= counter + 1'b1;
    
        assign led = counter[7];
    
    endmodule
    ```

1. Convert the design above to a simulatable C++ class 

    `yosys -p "read_verilog blink.v; write_cxxrtl blink.cpp"`

1. Create a simulation wrapper

    `main.cpp`:

    ```c
    #include <iostream>
    #include "blink.cpp"
    
    using namespace std;
    
    int main()
    {
        cxxrtl_design::p_blink top;
    
        bool prev_led = 0;
    
        top.step();
        for(int cycle=0;cycle<1000;++cycle){
    
            top.p_clk.set<bool>(0);
            top.step();
            top.p_clk.set<bool>(1);
            top.step();
    
            bool cur_led        = top.p_led.get<bool>();
            uint32_t counter    = top.p_counter.get<uint32_t>();
    
            if (cur_led != prev_led){
                cout << "cycle " << cycle << " - led: " << cur_led << ", counter: " << counter << endl;
            }
            prev_led = cur_led;
        }
    }
    ```

1. Compile `blink.cpp` and main.cpp` to a simulation executable

    ```clang++ -g -O3 -std=c++14 -I `yosys-config --datdir`/include main.cpp -o tb```

1. Execute!

    ```
    > ./tb
    cycle 127 - led: 1
    cycle 255 - led: 0
    cycle 383 - led: 1
    cycle 511 - led: 0
    cycle 639 - led: 1
    cycle 767 - led: 0
    cycle 895 - led: 1
    ```

You can find the files above in the [`blink_basic`](https://github.com/tomverbeure/cxxrtl_eval/tree/master/blink_basic) project on GitHub.
example of my [`cxxrtl_eval`](https://github.com/tomverbeure/cxxrtl_eval) project on GitHub.


# CXXRTL Manual

CXXRTL is very new and moving fast. This blog post had to be updated multiple times due to new features being added.

For an up-to-date state of features, it's best to bring up the CXXRTL manual from within Yosys:

```
> yosys
...
yosys> help write_cxxrtl

    write_cxxrtl [options] [filename]

Write C++ code that simulates the design. The generated code requires a driver
that instantiates the design, toggles its clock, and interacts with its ports.

The following driver may be used as an example for a design with a single clock
driving rising edge triggered flip-flops:

    #include "top.cc"
...
```


# Features and Options

* Black-boxing of submodules deep in the design hierarchy

    When you black-box a module in CXXRTL, you replace it with your own C++ class.

    This can be useful for a variety of reasons. 

    A very good example would be the replacement of a hardware UART with a C++ 
    class that calls the serial port of the computer on which the simulator
    is running. Or replacing JTAG debug hardware with a software bridge to GDB.

    Another common simulation speedup tactic is to replace the hardware
    model of a CPU by a behavioral call to the C code that would otherwise
    need to be simulated assembler instruction by assembler instruction on the
    hardware model of other CPU. 
   
    The CXXRTL manual contains a black-box example.

* Parameterized Black-Boxes through C++ Templates

    This is a subfeature of black-boxing, but one that I find interesting just
    for the sake of it.
    
    Black box Verilog modules with parameters are converted into templated
    C++ classes, where the parameter becomes the template parameter. 

    The manual once again gives a good example of this.

* VCD Waveform Generation

    A simulator isn't worth much when it doesn't support dumping debug waveforms.

    The [VCD waveform writer](https://github.com/YosysHQ/yosys/blob/master/backends/cxxrtl/cxxrtl_vcd.h) 
    is only around 200 lines of C++ code and serves as a great example for those who want to write similar 
    tools, such as support for different waveform dump file formats.

    An example is provided below.

* Design introspection

    Design introspection allows the testbench itself to go through the whole design 
    *at run time* and discover and interact with all objects that contain a value or state.

    The VCD waveform generation uses this feature to come up with all the storage elements
    (signals, memories) that need to be dumped, but introspection opens up all kinds of other 
    possibilities that are discussed futher below.

* Implementation Simplicity

    One of the most attractive points of CXXRTL is the simplicity of the implementation. 

    The Yosys backend is small. The generated code is understandable (to a point). The execution 
    model is straightforward. It uses a single bit vector data representation and C++ templates to 
    implement Yosys digital logic primitives.

    It may not have the performance of Verilator (which has seen more than 20 years of
    performance optimizations), but if you had to implement some new feature, like 
    adding support for a new waveform format, it'd be trivial compared to adding that
    to Verilator.

    When writing this blog post, I often needed to dive into the code to clarify some details,
    and other than the complexity that's inherent to C++ templates, I found the whole
    experience relatively painless.

    I consider this a major plus for an open source project.

* Automatically benefits from Yosys front-end improvements

    Whenever a new front-end feature gets added to Yosys, CXXRTL benefits from that
    as well.

    SystemVerilog is a good example of this: while the pure open source version of Yosys only
    covers to small subset of SystemVerilog language features, 
    [new](https://github.com/YosysHQ/yosys/commit/7e83a51fc96495c558a31fc3ca6c1a5ba4764f15)
    [ones](https://github.com/YosysHQ/yosys/commit/76c499db71fd6aaae8d2c5436c648d81cc8233f5#diff-a35fa64b9752ff3a146b31489cba6514)
    [are](https://github.com/YosysHQ/yosys/commit/f482c9c0168a6857383e7d9360c8ca1df36ba2bc#diff-a35fa64b9752ff3a146b31489cba6514)
    [slowly](https://github.com/YosysHQ/yosys/commit/0b6b47ca670b9219bcb81ab7d3599267c2ef7571#diff-a35fa64b9752ff3a146b31489cba6514)
    [being](https://github.com/YosysHQ/yosys/commit/ecc22f7fedfa639482dbc55a05709da85116a60f#diff-a35fa64b9752ff3a146b31489cba6514)
    [added](https://github.com/YosysHQ/yosys/commit/50f86c11b2bb9e561f5a0cf10e053b1aa4918abd#diff-a35fa64b9752ff3a146b31489cba6514).

    Similarly, the [ghdl-yosys-plugin](https://github.com/ghdl/ghdl-yosys-plugin) project has
    been working towards adding Yosys VHDL support.

    Since all these front-ends compile to the same intermediate data representation that
    is used by CXXRTL, this improved simulation feature support to automatic!

    Once the Yosys gHDL integration stabilize, CXXRTL will be the only open source simulator
    with mixed Verilg/VHDL language support!

* Simulation Speed

    CXXRTL is orders of magnitude faster than Icarus Verilog.

    But see below...

# Disadvantages

* Simulation Speed 

    My current benchmark is a small VexRiscv CPU running a C program that toggles 3 LEDs.

    In the fastest settings, CXXRTL is about 8x slower than single-threaded Verilator.

    You can find my benchmarking results [here](https://github.com/tomverbeure/cxxrtl_eval/blob/master/README.md).

    One should not rely on just one benchmark, and others have reported simulation speed
    differences that aren't as large. Verilog coding style differences, or the type of
    logic could play a major role here.

    My personal opinion is that CXXRTL is fast enough for what I need, and its features
    and ease of use are sufficient to prefer it over Verilator.

    But when speed is your first and foremost concern, CXXRTL is currently not for you.

* Compilation Speed

    A CXXRTL model relies on C++ templates for all data types and operations. It also uses
    a single storage model for everything, whether it's a bit, a 32-bit vector, a
    1024-bit vector, or a memory. This makes the run-time include file very clean and 
    small.

    Meanwhile, Verilator reduces data types to the best matching C storage type. If 
    something can fit in a `char`, then that's what will be used. There are no templated
    to be seen.

    Templates are hard work for a C++ compiler. Compilation time is the price you pay. 

    Furthermore, Verilator splits models into multiple C++ files that can be compiled
    in parallel. CXXRTL dumps out 1 flat file, so nothing about compiling the model can 
    be done in parallel.

    With highest performance flags, my VexRiscv benchmark takes 66s to build with CXXRTL 
    vs 9s on Verilator, or about 7 times longer.

    The ratio increases for larger models when multiple compilations are launched at the
    same time.

* No Support for some Verilog $ functions

    I like to spinkle my code with debug `$display` statements. Since these are 
    non-synthesizable constructs, Yosys currently just ignores them as if they were never 
    there.

    Verilator keeps them around.

    There are hacks possible to do something similar: you could peek from the enclosing
    wrapper into some lower level hierarchical trigger signal and print out some
    diagnostics, but that could be a very tall order when your Verilog code has tons
    of such `$display` statements.

    There's currently a [feature request](https://github.com/YosysHQ/yosys/issues/2310)
    to add support for `$display` in Yosys.

# Dumping VCD Waveforms

Dupming signal values into a waveform requires knowledge and access to the
internal signals and memories.

Design introspection provides all that, and makes it really easy to implement
a simple waveform dumper. CXXRTL comes standard with `cxxrtl_vcd.h` which adds
VCD support.

The decision to dump signal values or not after a simulation timing step is up to the 
programmer of the C testbench, and requires slightly more effort than for a traditional
Verilog simulator, but it's also more flexible: it'd be trivial to only start dumping waves 
based on some internal design condition, for example.
    
[`blink_vcd`](https://github.com/tomverbeure/cxxrtl_eval/tree/master/blink_vcd) 
has a minimal example on how to dump a VCD file. Check
out the comments in [`main.cpp`](https://github.com/tomverbeure/cxxrtl_eval/blob/master/blink_vcd/main.cpp)
for explanations.

If all goes well, you should be greeted with the following image after running `make`:

![blink_vcd waveform](/assets/cxxrtl/blink_vcd_waves.png)

# Design Introspection

*This section talks about a more advanced topic that requires some knowledge about
how CXXRTL stores data under the hood. If you're only interested in CXXRTL as
a replacement for your regular Verilog simulator, don't let this section scare
you away: you can safely skip it! Design introspection is something that's mostly useful
for tool makers, not for regular simulator users.*

CXXRTL uses C++ objects to store values, wires, and memories across the whole
design hierarchy. These objects by themselves are sufficient to run the simulation, 
and a C++ testbench can access these objects by reaching straight into the object
hierarchy by calling `set` and `get` methods on the object, as shown earlier in
the [`blink_basic`](https://github.com/tomverbeure/cxxrtl_eval/blob/561d514f3dbb6bc89a80cac11201b4f6c59a4688/blink_basic/main.cpp#L21-L22) 
example:

```c++
        bool cur_led        = top.p_led.get<bool>();
        uint32_t counter    = top.p_counter.get<uint32_t>();
```

This is the straightforward, C++ way to interact with the simulation model.

However, it requires knowledge of the existence of the `top.p_led` and `top.p_counter`
objects at testbench compile time.

That's fine when the whole point of your C++ testbench is to interact with these
objects, but there are cases where some functionality of your C++ testbench is
generic: something that can be used for different designs irrespective of what
kind of signals and memories they contain. (A waveform dumper is an excellent
example!)

This is where the CXXRTL debug data structure comes into play: it maps all the
known and retained (after Yosys optimization) hierarchical names of the source 
code to information of hierarchical name (its type such as wire or memory, bit width, ...)
as well as the current simulation value.

With this debug data structure, the testbench can travers through the design,
look at and interact with all the values that the design contains, all without knowing
which values exist at compile time.

This opens up all kinds of possibilities. For example, one could embed a CXXRTL model in
GUI wrapper that allows the user to interactively browse through the design variables,
inspect values etc.

Or it could be used for checkpointing, where the state of a long-running simulation
is saved to file and restored later on, e.g. to bypass a long simulated initialization 
sequence that never changes between different test cases.

In the [`blink_introspect`](https://github.com/tomverbeure/cxxrtl_eval/tree/master/blink_introspect)
example, the code below shows how one can list the information of all signals and memories in a design:

```c++
void dump_all_items(cxxrtl::debug_items &items)
{
    cout << "All items:" << endl;
    for(auto &it : items.table)
        for(auto &part: it.second)
            cout << setw(20) << it.first 
                 << ": type = " << part.type 
                 << ", width = " << setw(4) << part.width 
                 << ", depth = " << setw(6) << part.depth 
                 << ", lsb_at = " << part.lsb_at 
                 << ", zero_at = " << part.zero_at << endl;
    cout << endl;
}
```

On my small design, the code above prints out the following:

```
                     clk : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0
                     led : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0
                     mem : type = 2 ; width =   40 ; depth =     11 ; lsb_at =   0 ; zero_at =   0
             u_blink clk : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0
         u_blink counter : type = 1 ; width =   64 ; depth =      1 ; lsb_at =   0 ; zero_at =   0
             u_blink led : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0
    u_blink non_zero_lsb : type = 0 ; width =   33 ; depth =      1 ; lsb_at =  11 ; zero_at =   0
```

Printing the value of a signal is a bit more complicated since it requires understanding
how CXXRTL stores values internally. That model is pretty simple: all values are stored in an array
of as many so-called chunks needed. CXXRTL uses a 32-bit integer as a chunk. (This might change
in the future, but it's unlikely.)

When your Verilog code has a 5-bit register, it will use a single chunk to store its value.
When there's a 33-bit register, it will use 2 chunks.

Memory are stored just the same, with multiple values tightly packed in memory.

The function below from the same example prints out the current value of a simulation item:

```c++
void dump_item_value(cxxrtl::debug_items &items, std::string path)
{
    cxxrtl::debug_item item = items.at(path);

    // Number of chunks per value
    const size_t nr_chunks = (item.width + (sizeof(chunk_t) * 8 - 1)) / (sizeof(chunk_t) * 8);

    cout << "\"" << path << "\":"  << endl;

    for (size_t index = 0; index < item.depth; index++) {
        if (item.depth > 1)
            cout << "location[" << index << "] : "; 

        for(size_t chunk_nr = 0; chunk_nr < nr_chunks; ++chunk_nr){
            cout << item.curr[nr_chunks * index + chunk_nr];
            cout << (chunk_nr == nr_chunks-1 ? "\n" : ",  ");
        }
    }
}
```

When the value of the `counter` is 201, and you run `dump_item_value(all_debug_items, "u_blink counter");`, 
you get the following:

```
"u_blink counter":
    word[0] = 201
    word[1] = 0
```

In the example, the Verilog code declares and initializes `mem` as follows:

```
    reg [39:0] mem[10:0];

    initial begin
        mem[0]  = 0;
        mem[4]  = 3;
        mem[7] = (1<<33);
    end
```

When dumping the value of the memory, you'll get this:

```
"mem":
location[0] : 0,  0
location[1] : 0,  0
location[2] : 0,  0
location[3] : 0,  0
location[4] : 3,  0
location[5] : 0,  0
location[6] : 0,  0
location[7] : 0,  2
location[8] : 0,  0
location[9] : 0,  0
location[10] : 0,  0
```

You can see how for location 7 bit 1 of the second chunk is set to 1. This corresponds to the
assigned value of `(1<<33)`.

# Compilation Options - Speed vs Debug

While the `write_cxxrtl` command has quite a number of options, in most cases, you only
have to decide between adding `-Og` or not.

With the `-Og` option, CXXRTL will go out of its way to retain most, if not all, signals
that were present in the Verilog. Doing so reduces the ability for some optimizations, and,
as a result, the simulation will be slower even when no waveforms are being dumped.

There are other options that will impact the simulation speed, but for the vast majority of
use cases, it's best to just use the default values.

# The CXXRTL Code Base

CXXRTL is surprisingly lightweight. At the time of writing this 
(Yosys commit [072b14f1a](https://github.com/YosysHQ/yosys/tree/072b14f1a945d096d6f72fc4ac621354aa636c70)), 
it stands at around [4500 lines of heavily commented code](https://github.com/YosysHQ/yosys/tree/072b14f1a945d096d6f72fc4ac621354aa636c70/backends/cxxrtl).

This code includes a manual with description of the various options and some examples, the backend that transforms Yosys
internal design representation into C++ code, the aforementioned `cxxrtl.h` library for variable length
bit vector operations, as well as a C API and a VCD waveform dumping support.

It's tempting to compare this against the 105000 lines of code of Verilator, but that'd be very
unfair because most of the heavy lifting to create a CXXRTL simulator is performed by the generic
blocks of Yosys:

* Parsing Verilog into an abstract syntax tree (AST)
* Conversion from the AST into the Yosys internal register transfer represention (RTLIL)
* Elaboration into a self-contained, linked hierarchical design
* Conversion of processes into multiplexers, flip-flops, and latches
* Various optimization and reduction passes, most of which are optional:
    * removal of unused logic
    * removal of redundant intermediate assigments
    * flattening of hierarchy
    * ...

All of these are steps that need to happen for synthesis, but they also happen to be useful
for a cycle based simulator.

CXXRTL expects a design, hierarchically flattened or not, as a graph of logic operations and flip-flops. Yosys
already does that. All CXXRTL needs to do is to topologically sort this graph so that dependent
operations are performed in the optimal execution order, for best performance, and write out these operations as
C++ code.

# CXXRTL's Author

CXXRTL is the brainchild of [@whitequark](https://twitter.com/whitequark), a prolific author and contributor to all
kinds of [open source projects](https://github.com/whitequark).
 
[Her lab notebook](https://lab.whitequark.org/) covers a wide range of fascinating topics, from using formal solvers to 
[synthesize optimal code sequences for 8051 microcontrollers](https://lab.whitequark.org/notes/2020-04-06/synthesizing-optimal-8051-code/), 
to [patching Nvidia drivers to support hot-unplug on Linux](https://lab.whitequark.org/notes/2018-10-28/patching-nvidia-gpu-driver-for-hot-unplug-on-linux/), 
to [using a blowtorch to reflow PCBs](https://lab.whitequark.org/notes/2016-04-28/smd-reflow-with-a-blowtorch/) (because... why not?).

In addition to CXXRTL, she's the main author of [nMigen](https://github.com/m-labs/nmigen) (a Python framework that replaces Verilog as a 
language to write RTL), the maintainer of [Solvespace](http://solvespace.com/index.pl) (a parametric 2d/3d CAD tool), 
and she has countless Yosys contributions to her name.

I highly recommend checking out her work, her battles with cursed technologies, and sponsoring her work 
through [Patreon](https://www.patreon.com/whitequark/posts).

# Conclusion

It's still early days for CXXRTL. It was started less than a year ago, and the first merge into the main Yosys
tree was only happened in April of this year.

And yet it's already one of the best open source simulators, it's fast, lightweigh, and the easiest by far to extend
with new features.

It's already my default simulator for my hobby projects. Give it a try!

# References

Relevant whitequark tweets:
* [Size of VCD file compared to Verilator](https://twitter.com/whitequark/status/1269968987682672642)
* [Zero-cost CXXRTL debug information thread](https://twitter.com/whitequark/status/1269951285106823168)
* [Poll about zero-cost addition of debug probes](https://twitter.com/whitequark/status/1269889811973844994)
* [CAPI](https://twitter.com/whitequark/status/1269473985097543680)
* [VCD emitter](https://twitter.com/whitequark/status/1269352227002552320)
* [Python using CAPI](https://twitter.com/whitequark/status/1269284773840719872)
* [CXXRTL and WASM](https://twitter.com/whitequark/status/1269241340711272450)
* [debug information exposed through CAPI](https://twitter.com/whitequark/status/1269226589356724224)
* [Initial black box support](https://twitter.com/whitequark/status/1251429512732012552)
* [CXXRTL 70% faster](https://twitter.com/whitequark/status/1252615261934534656)
* [Initial announcement](https://twitter.com/whitequark/status/1201014573547040769)

GitHub:
* [GitHub Initial pull request](https://github.com/YosysHQ/yosys/pull/1562)

Libre-soc discussion:
* [CXXRTL discussion on libre-soc](https://bugs.libre-soc.org/show_bug.cgi?id=276)

Foundational paper about operation scheduling:
* [A Fast & Effective Heuristic for the Feedback Arc Set Problem](https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf)


