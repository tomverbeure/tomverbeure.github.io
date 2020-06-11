---
layout: post
title: CXXRTL, a Yosys Simulation Backend
date:  2020-04-20 00:00:00 -1000
categories:
---

* TOC
{:toc}

# The Open Source Simulation Status Quo

For my open source RTL projects, I've so far only used 2 Verilog simulators: 
[Icarus Verilog](http://iverilog.icarus.com/) and [Verilator](https://www.veripool.org/wiki/verilator).

Icarus Verilog is a traditional event-driven simulator with support for most of the behavioral Verilog constructs that
can be found in complex Verilog testbenches: delays, `repeat` statements, etc. If you can look past its simulation
speed (it's *very* slow), it does the job pretty well, and allows one to stay within a pure Verilog environment, just
like you would with commercial tools such as VCS, Modelsim etc.

Verilator is a completely different beast: it's a cycle based simulator that, with some exceptions, only takes
in synthesizable RTL, removes all notions of time or delays, and simulates from one cycle to the next. Cycle
based simulators are much faster than event driven simulators, and Verilator is one of the best in class that
routinely beats commercial simulators. Verilator compiles your Verilog design into a bunch of C++ files and
then into a linkable library. All you need to do is write a C++ wrapper (which can be very small) that
calls the library for each simulation step, and you're on your way. ZipCPU has [a very good Verilator
tutorial](https://zipcpu.com/blog/2017/06/21/looking-at-verilator.html).

Verilator can easily be 100x faster than Icarus Verilog. When the simulation time of my projects gets too
long, I usually switch from Icarus to Verilator.

Icarus and Verilator aren't the only open source Verilog simulators, but they are the most popular by far, and
for good reason.  Wikipedia [lists](https://en.wikipedia.org/wiki/List_of_HDL_simulators#Free_and_open-source_simulators) a number
of alternatives, but one constant between them is the lack of support for modern Verilog features. I've
never seen anybody use them...

# Yosys, the Swiss Army Knife of Digital Logic Manipulation

Yosys is the star of the open source synthesis world. It initially rose to prominence with the release of 
[Claire Wolff](http://www.clifford.at/)'s [Project IceStorm](http://www.clifford.at/icestorm/), in 
which it's the synthesis component of an end-to-end open source RTL to bitstream flow for Lattice ICE40 FPGAs. 

But Yosys is much more than that.

It's a swiss army knife of digital logic manipulation that takes in a digital design through one of its so-called frontends 
(Verilog, blif, json, ilang, even VHDL for the commerical version), provides tons of different passes that transform 
the digital logic one way or the other (e.g. flatten a hierarchy, remove redundant logic, map generic gates to 
specific technology gates, check formal equivalence), and a whole bunch of backends that write the final design in 
some desired format (e.g. Verilog, Spice, json etc.)

If you have a blob of digital logic and you need to perform some kind of transformation, chances are that Yosys
already supports it.

Yosys commands are relatively well documented, but, unfortunately, the documentation snapshots on 
[the official Yosys website](http://www.clifford.at/yosys/documentation.html) are often woefully behind. 

To get the latest and greatest list of commands, it's best to just compile Yosys and use the `help` function.

*The amount of information can be overwhelming (there are a large amount of commands that I don't quite understand
myself), but, luckily, it's not necessary to understand most of the commands: in many cases, it's sufficient to use
ready-made recipes to go from RTL to a synthesized gate-level netlist.*

# CXXRTL, a New Simulation Backend

[CXXRTL](https://github.com/YosysHQ/yosys/tree/master/backends/cxxrtl) is a new Yosys backend. It writes out 
the digital logic inside Yosys as a set of C++ classes, one for each remaining module, after performing whichever 
transformation pass you want to apply.

In combination with a single C++ [`cxxrtl.h`](https://github.com/YosysHQ/yosys/blob/master/backends/cxxrtl/cxxrtl.h)
include file with template classes that implements variable width bitvector arithmetic, the C++ classes become a 
simulation model of the digital design.

Just like with Verilator, the simulation model is cycle-based. And just like Verilator, you need to provide a thin
C++ wrapper that calls these classes to perform a step-by-step simulation.

# CXXRTL's Origin

CXXRTL is the brainchild of [@whitequark](https://twitter.com/whitequark), a prolific author and contributor to all
kinds of [open source projects](https://github.com/whitequark).
 
[Her lab notebook](https://lab.whitequark.org/) covers a wide range of fascinating topics, from using formal solvers to 
[synthesize optimal code sequences for 8051 microcontrollers](https://lab.whitequark.org/notes/2020-04-06/synthesizing-optimal-8051-code/), 
to [patching Nvidia drivers to support hot-unplug on Linux](https://lab.whitequark.org/notes/2018-10-28/patching-nvidia-gpu-driver-for-hot-unplug-on-linux/), 
to [using a blowtorch to reflow PCBs](https://lab.whitequark.org/notes/2016-04-28/smd-reflow-with-a-blowtorch/) (because... why not?).

In addition to she's the main author of [nMigen](https://github.com/m-labs/nmigen) (a Python framework that replaces Verilog as a 
language to write RTL), the maintainer of [Solvespace](http://solvespace.com/index.pl) (a parametric 2d/3d CAD tool), 
and she has countless Yosys contributions to her name.

I highly recommend checking out her work, her battles with cursed technologies, and sponsoring her work 
through [Patreon](https://www.patreon.com/whitequark/posts).

# From Verilog to Simulation

Going from Verilog to running a simulation is straightforward. 

1. Create an example design `blink.v`:

    ```verilog
    module blink(input clk, output led);
    
        reg [7:0] counter = 0;
    
        always @(posedge clk)
            counter <= counter + 1'b1;
    
        assign led = counter[7];
    
    endmodule
    ```

1. Convert the design above to a simulatable C++ class 

    `yosys -p "read_verilog blink.v; write_cxxrtl blink.cpp"`. 

1. Create a simulation wrapper

    `main.cpp`:

    ```c
    #include <iostream>
    #include "blink.cpp"
    
    using namespace std;
    
    int main()
    {
        cxxrtl_design::p_blink top;
    
        int prev_led = 0;
    
        top.step();
        for(int i=0;i<1000;++i){
    
            top.p_clk = value<1>{0u};
            top.step();
            top.p_clk = value<1>{1u};
            top.step();
    
            int cur_led = top.p_led.curr.data[0];
    
            if (cur_led != prev_led)
                cout << "cycle " << i << " - led: " << cur_led << endl;
    
            prev_led = cur_led;
        }
    }
    ```

1. Compile `blink.cpp` and main.cpp` to a simulation executable

    `clang++ -g -O3 -std=c++14 -I ~/tools/yosys/ main.cpp -o tb`

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

# Under the Hood

CXXRTL is surprisingly lightweight. At the time of writing this 
(Yosys commit [072b14f1a](https://github.com/YosysHQ/yosys/tree/072b14f1a945d096d6f72fc4ac621354aa636c70)), 
it stands at around [4500 lines of code and copious comments](https://github.com/YosysHQ/yosys/tree/072b14f1a945d096d6f72fc4ac621354aa636c70/backends/cxxrtl).

This code includes a manual with description of the various options and some examples, the backend that transforms Yosys
internal design representation into C++ code, `cxxrtl.h`, a C++ template library with support for variable length
bit vectors, as well as a C API and a VCD debug support.

It's tempting to compare this against the 105000 lines of code of Verilator, but that's incredibly
unfair because a lot of the heavy lifting to create a CXXRTL simulator is performed by the generic
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

All of these are steps that need to happen for synthesis, but it turns out that the same steps are also useful
for a cycle based simulator.

CXXRTL expects a design, hierarchically flattened or not, as a graph of logic operations and flip-flops. Yosys
already does that. All CXXRTL needs to do is to topologically sort this graph so that dependent
operations are performed in the optimal order (for best performance), and write out these operations as
C++ code.

# CXXRTL Manual

CXXRTL is still in heavy development and moving fast. This blog post had to be updated multiple times due to 
new features being added all the time.

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

* Black-boxing of select submodules

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

* Black-box templates

    This is a subfeature of black-boxing, but one that I find interesting just
    for the sake of it.
    
    Black box Verilog modules with parameters are converted into templated
    C++ classes, where the parameter becomes the template parameter. 

* Design introspection

    CXXRTL uses C++ objects to store values, wires, and memories across the whole
    design hierarchy.

    By default, it's also has a debug data structure that maps the hierarchical names
    of the source code to these objects.

    It's trivial to write some C++ code to iterate through this data structure, explore
    which signals exists, and look into their current simulation value. 

    This opens up all kinds of possibilities. For example, one could embed a CXXRTL model in
    GUI wrapper that allows the user to interactively browse through the design variables,
    inspect values etc.

* VCD Waveform Generation

    A simulator isn't worth much when it doesn't support dumping debug waveforms.

    The design introspection makes it really easy to implement just that, and it's included
    standard with CXXRTL. The decision to dump signal values or not after a simulation
    timing step is up to the programmer of the wrapper, so there's slightly more effort
    required than what would be required in a regular Verilog simulator, but it's also
    much more flexibility: it'd be trivial to decide to dump waves based on some internal
    design condition, for example.
    
    The [VCD waveform writer](https://github.com/YosysHQ/yosys/blob/master/backends/cxxrtl/cxxrtl_vcd.h) 
    is only around 200 lines of C++ code and serves as a great example for those who want to write similar 
    tools, such as support for different waveform dump file formats.

* Simplicity

    One of the most attractive points of CXXRTL is the simplicity of the code. The 
    Yosys backend is small. The generated code is understandable. The execution model is
    straightforward. It uses a single bit vector data representation and C++ templates to 
    implement Yosys digital logic primitives.

    It may not have the performance of Verilator (which has seen more than 20 years of
    performance optimizations), but if you had to implement some new feature, like 
    adding support for a new waveform format, it'd be trivial compared to adding that
    to Verilator.

* Automatically benefits from Yosys front-end improvements

    Whenever Yosys gains a new front-end feature, such as support for a new SystemVerilog
    construct, CXXRTL will automatically gain that support as well.

    A very good example here is the commercial version of Yosys, which supports
    the Verific SystemVerilog and VHDL frontends. With the commercial version of Yosys, 
    CXXRTL is a great way to create license-free mixed-language simulation models.

* Simulation Speed

    CXXRTL is orders of magnitude faster than Icarus Verilog.

    But see below...

# Disadvantages

* Simulation Speed 

    My current benchmark is a small VexRiscv CPU running a C program that toggles 3 LEDs.

    In the fastest settings, CXXRTL is about 8x slower than single-threaded Verilator.

    When speed is your first and foremost concern, CXXRTL is currently not for you.

* Compilation Speed

    A CXXRTL model relies on C++ templates for nearly everything. Templates are hard work   
    for a C++ compiler. Compilation time is the price you pay.

    With highest performance flags, my VexRiscv benchmark takes 66s to build with CXXRTL 
    vs 9s on Verilator, or about 7 times longer.

    The ratio will increase for larger models, because Verilator splits up a
    design in multiple C++ files that can be compiled in parallel, whereas CXXRTL
    dumps out 1 flat file. So nothing about compiling the model can be done in parallel.

* No Support for some Verilog $ functions

    I like to spinkle my code with debug `$display` statements. Since these are 
    non-synthesizable constructs, Yosys simply ignores as if they were never there.

    Verilator keeps them around.

    There are hacks possible to do something similar: you could peek from the enclosing
    wrapper into some lower level hierarchical trigger signal and print out some
    diagnostics, but that could be a very tall order when your Verilog code has tons
    of such $display statements.

# Compilation Options - Speed vs Debug

While the `write_cxxrtl` command has quite a number of options,  in most cases, you only
have to decide between adding `-Og` or not.

With the `-Og` option, CXXRTL will go out of its way to retain most, if not all, signals
that were present in the Verilog. Doing so reduces the ability for some optimizations, and,
as a result, the simulation will be slower even when no waveforms are being dumped.

# Waveform Dumping Levels

Within the C++ wrapper, it's up to the user to decide which signals are included in the
VCD file.



Topics:

* How is it implemented?
* Comparison with Verilator and Icarus Verilog
* Benchmark
* Blackbox replacement
* Desired new features:
    * $display
* use hierarchy -top "top" to make sure only necessary modules are dumped, and
  mark outputs in a certain way.



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

Foundational paper:
* [A Fast & Effective Heuristic for the Feedback Arc Set Problem](https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf)
