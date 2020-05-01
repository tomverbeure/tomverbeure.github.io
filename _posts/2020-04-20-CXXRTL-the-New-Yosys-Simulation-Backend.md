---
layout: post
title: CXXRTL, a Yosys Simulation Backend
date:  2020-04-20 00:00:00 -0700
categories:
---

# The Open Source Simulation Status Quo

For my open source RTL projects, I've so far only used 2 Verilog simulators: Icarus Verilog and Verilator.

Icarus Verilog is a traditional event-driven simulator with support for most of the behavior Verilog constructs that
can be found in complex Verilog testbenches: delays, `repeat` statements, etc. If you can look past its simulation
speed (it's *very* slow), it does the job pretty well, and allows one to stay within a pure Verilog environment, just
like you would with commerical tools such as VCS, Modelsim etc.

Verilator is a completely different beast: it's a cycle based simulator that, with some exceptions, only takes
in synthesizable RTL, removes all notions of time or delays, and simulates from one cycle to the next. Cycle
based simulators are much faster than event driven simulators, and Verilator is one of the best in class that
routinely beats commerical simulators. Verilator compiles your Verilog design into a bunch of C++ files and
then into a linkable library. All you need to do is write a C++ wrapper (which can be very small) that
calls the library for each simulation step, and you're on your way. ZipCPU has [a very good Verilator
tutorial](XXX).

Verilator can easily be 100x faster than Icarus Verilog. When the simulation time of my projects gets too
long, I usually switch from Icarus to Verilator.

Icarus and Verilator aren't the only open source Verilog simulators, but they are the most popular by far, and
for good reason.  Wikipedia [lists](https://en.wikipedia.org/wiki/List_of_HDL_simulators#Free_and_open-source_simulators) a number
of alternatives, but one constant between them is the lack of support for modern Verilog features. I've
never seen anybody use them...

# CXXRTL, a New Simulation Backend

Yosys is the star of the open source synthesis world. It initially rose to prominence when the release of Project ICE Storm, 
where it provides an end-to-end open source RTL to bitstream flow for Lattice ICE40 FPGAs, but it's really much more than that.

Developed by Claire Wolff, Yosys is a swiss army knife that takes in a digital design through one of its so-called frontends 
(Verilog, blif, json, ilang), provides tons of different passes that transform the digital design one way or the other (e.g. 
remove redundant logic, map generic gates to specific technology gates), and whole bunch of backends that write the final design 
in some desired format (e.g. Verilog, Spice, json etc.)

CXXRTL is one of those backends: write out the design as a set of C++ classes, one for each remaining module after performing
all the transformation passes.

Just like with Verilator, these generated C++ classes form a cycle-based simulator of the design. And just like Verilator,
you need to provide a thing C++ wrapper that calls these classes to perform a step-by-step simulation.

CXXRTL is the brainchild of [@whitequark](XXX), a prolific author and contributor to a 
[open source projects](https://github.com/whitequark).
 
[Her lab notebook](https://lab.whitequark.org/) covers a wide range of fascinating topics, from using formal solvers to 
synthesize optimal code sequences for 8051 microcontrollers and CPLDs, to patching Nvidia drivers to support hot-unplug on Linux, 
to using a blowtorch to reflow PCBs (because... why not?).

She's also the main auther of nMigen, a Python framework that replaces Verilog as a language to write RTL. I highly recommend
checking out her work and sponsoring her work through [Patreon](https://www.patreon.com/whitequark/posts).

# From Verilog to Simulation

Going from Verilog to running a simulation is straight forward. 

`blink.v`:
```Verilog
module blink(input clk, output led);

    reg [7:0] counter = 0;

    always @(posedge clk)
        counter <= counter + 1'b1;

    assign led = counter[7];

endmodule
```

Step 1: Convertthe design above to a simulatable C++ class by calling `yosys -p "read_verilog blink.v; write_cxxrtl blink.cpp"`. 

`blink.cpp`:
```
#include <backends/cxxrtl/cxxrtl.h>

using namespace cxxrtl_yosys;

namespace cxxrtl_design {

// \cells_not_processed: 1
// \src: blink.v:2.1-11.10
struct p_blink : public module {
    // \src: blink.v:2.20-2.23
    value<1> p_clk;
    value<1> prev_p_clk;
    bool posedge_p_clk() const {
        return !prev_p_clk.slice<0>().val() && p_clk.slice<0>().val();
    }
    // \init: 0
    // \src: blink.v:4.15-4.22
    wire<8> p_counter {0u};
    // \src: blink.v:2.32-2.35
    wire<1> p_led;

    bool eval() override;
    bool commit() override;
}; // struct p_blink

bool p_blink::eval() {
    bool converged = false;
    bool posedge_p_clk = this->posedge_p_clk();
    // \src: blink.v:6.5-7.35
    // cell $procdff$4
    if (posedge_p_clk) {
        p_counter.next = add_uu<8>(p_counter.curr, value<1>{0x1u});
    }
    // connection
    p_led.next = p_counter.curr.slice<7>().val();
    return converged;
}

bool p_blink::commit() {
    bool changed = false;
    prev_p_clk = p_clk;
    changed |= p_counter.commit();
    changed |= p_led.commit();
    return changed;
}

} // namespace cxxrtl_design
```

Step 2: compile `blink.cpp` with simulation wrapper `main.cpp`: `clang++ -g -O3 -std=c++11 -I ~/tools/yosys/ main.cpp -o tb`

`main.cpp`:
```
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


Step 3: Execute `./tb`

```
cycle 127 - led: 1
cycle 255 - led: 0
cycle 383 - led: 1
cycle 511 - led: 0
cycle 639 - led: 1
cycle 767 - led: 0
cycle 895 - led: 1
```

# Under the Hood

CXXRTL is surprisingly lightweight. At the time of writing this, it stands at just 
[3500 lines of code](https://github.com/YosysHQ/yosys/tree/dc77563a6a0b0a812fa006a286e0ec6e091dbd3a/backends/cxxrtl).

This code includes a manual with description of the various options and example, the backend itself that transforms Yosys
internal design representation into C++ code, as well as `cxxrtl.h`, a C++ template library with support for variable length
bit vectors.

The reason why the code can be this small is because most of the heavy lifting is performed by Yosys:

* Parsing Verilog into an abstract syntax tree (AST)
* Conversion from the AST into the Yosys internal register transfer represention (RTLIL)
* Elaboration into a self-contained, linked hierarchical design
* Conversion of processes into multiplexers, flip-flops, and latches
* Various optimization and reduction passes, most of which are optional:
    * removal of unused logic
    * removal of redundant intermediate assigments
    * various optimizations

All of these are steps that need to happen for synthesis, but it turns out that these same steps are also useful
for a cycle based simulator.

CXXRTL expects a design, a graph, hierarchically flattend or not, of just logic operations and flip-flops. Yosys
already does that. All CXXRTL needs to do is to topologically short this graph in such a way that dependent
operations are performed in the optimal order (for optimal performance), and write out these operations as
C++ code.


Topics:

* What is CXXRTL?
* How is it implemented?
* Limitations
* Benefits
    * General backend -> could support many languages
    * Commerical version: compilation from SVA to simulation
* Comparison with Verilator and Icarus Verilog
* Benchmark
* Effect of compilation options
* Blackbox replacement
* Desired new features:
    * wave dumping
    * demangled name access
    * design introspection (e.g. find all signals with a certain name)
    * $display


References:

* [A Fast & Effective Heuristic for the Feedback Arc Set Problem](https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf)
