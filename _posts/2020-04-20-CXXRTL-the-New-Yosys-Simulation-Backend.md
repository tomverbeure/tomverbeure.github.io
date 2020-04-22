---
layout: post
title: CXXRTL, a Yosys Simulation Backend
date:  2020-04-20 00:00:00 -0700
categories:
---

# The Open Source Simulation Status Quo

For my open source RTL projects, I've so far only used 2 Verilog simulators: Icarus Verilog and Verilator.

Icarus Verilog is a traditional event-driven simulator that supports most of the behavior Verilog constructs that
can be found in complex Verilog testbenches: delays, `repeat` statements, etc. If you can look past its simulation
speed (it's very slow), it does the job pretty well, and allows on to stay within a pure Verilog environment, just
like you would with commerical tools such as VCS, Modelsim etc.

Verilator is a completely different beast: it's a cycle based simulator that (with some exceptions) only takes
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

Yosys is the star of the open source synthesis world. Developed by Claire Wolff, it's now the basis for :q
:



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

