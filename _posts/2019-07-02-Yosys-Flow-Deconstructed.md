---
layout: post
title: Yosys Deconstructed - A Walk through the Yosys Synthesis Flow
date:   2019-07-02 10:00:00 -0700
categories:
---

## Introduction

Not too many years ago, the only way to play with RTL synthesis, the mapping of a digital design from Verilog or VHDL to gates, was 
through the use of commercial tools. Some of them were (and are!) incredibly expensive (think Synopsys Design Compiler), so of them 
were free, as in beer, and included in commercial FPGA synthesis packages. None were open source.

[Yosys](http://www.clifford.at/yosys/documentation.html) changed all that. 

Yosys, short for "Yosys Open SYnthesis suite", is a swiss army knife of logic manipulation tools that covers RTL parsing, logic
design manipulation, technology mapping, equivalence checking, and much more. It was initially written by 
[Clifford Wolf](http://www.clifford.at/), and still under active development through the Yosys [GitHub](https://github.com/YosysHQ/yosys)
page.

Yosys comes with a 194 page [manual](http://www.clifford.at/yosys/files/yosys_manual.pdf) that describes the internal 
architecture and data structures, as well as all the different commands that are supported.

It's required reading if you want to understand the full scope of the software, covering the basic principles of synthesis,
the low level internal data structures and cell library, information about how to program your own extensions, Verilog
parsing, and optimization and technology mapping steps. It also has an extensive reference manual with all supported
commands.

What's lacking is a story that walks a reader through a concrete example from Verilog input, through all the steps towards the 
output, a gate-level netlist that can be used by the target place and route tool.

Examples are often a very intuitive way to learn how things work, so this blog post does that: show all the transformations
that happen along the way on a small design.  By writing things down for public consumption, I force myself to dig deeper to 
avoid major mistakes. I hope other will benefit from it as well.

## The Lattice iCE40 FPGA from Verilog to Bitstream

Lattice iCE40 FPGAs were the first FPGAs for which the bitstream has been fully reverse engineered. This has enabled
the creation of [Project IceStorm](http://www.clifford.at/icestorm/), an end-to-end design flow from Verilog RTL to a 
functional bitstream.

Yosys handles the translation from Verilog to cells from the ICE40 primitives library. 
[Arachne P&R](https://github.com/YosysHQ/arachne-pnr) or [nextpnr](https://github.com/YosysHQ/nextpnr)
take it from there and places and routes all the cells and wires. Finally, Project IceStorm converts the placed database
and converts it to a bitstream.

A good example of the whole flow can be seen in [this project](https://github.com/mystorm-org/BlackIce-II/tree/master/examples/sram)
that maps a Verilog design with an external SRAM to an ICE40 on a BlackIce-II FPGA board.

## Yosys and the ICE40 FPGA

Synthesizing a design with Yosys for an ICE40 FPGA couldn't be easier. It consists of the 
following commands:

```
read_verilog my_design.v
synth_ice40
write_verilog my_design.syn.v
```

That's it!

The `synth_ice40` command is a script that's embedded in the Yosys C++ code. It calls many lower level Yosys commands.
And while the command has plenty of options, in this blog post I'll walk through the default flow in which no additional options are specified.

You can find the code of the `synth_ice40` command 
[here](https://github.com/YosysHQ/yosys/blob/de263281308c112891ef330536bd228460a0f85f/techlibs/ice40/synth_ice40.cc#L238-L398). When you assume 
all the defaults, the code can be reduced to the following sequence of commands:

```
begin:
	read_verilog -lib -D_ABC +/ice40/cells_sim.v
	hierarchy -check -auto-top
	proc

flatten:
	flatten
	tribuf -logic
	deminout

coarse:
	opt_expr
	opt_clean
	check
	opt
	wreduce
	peepopt
	opt_clean
	share
	techmap -map +/cmp2lut.v -D LUT_WIDTH=4
	opt_expr
	opt_clean
	alumacc
	opt
	fsm
	opt -fast
	memory -nomap
	opt_clean

bram:
	memory_bram -rules +/ice40/brams.txt
	techmap -map +/ice40/brams_map.v
	ice40_braminit

map:
	opt -fast -mux_undef -undriven -fine
	memory_map
	opt -undriven -fine

map_gates:
	techmap -map +/techmap.v -map +/ice40/arith_map.v
	ice40_opt

map_ffs:
	dffsr2dff
	dff2dffe -direct-match $_DFF_*
	techmap -D NO_LUT -map +/ice40/cells_map.v
	opt_expr -mux_undef
	simplemap
	ice40_ffinit
	ice40_ffssr
	ice40_opt -full

map_luts:
	techmap -map +/ice40/latches_map.v
	abc -dress -lut 4
	clean

map_cells:
	techmap -map +/ice40/cells_map.v"
	clean

check:
	hierarchy -check
	stat
	check -noinit

blif:

edif:

json:

```

The `synth_ice40` command is split up into multiple phases. With the `-run <from_label:to_label>` parameter, you
can restrict the commands to execute only those phases that you're interested in. 

We're not doing that, but the labels serve as useful documentation that help understanding which higher 
level steps are performed to get from initial RTL code to final gates.

Let's walk through the whole process!

## Before We Start

There are many different design constructs that must be treated in different ways during synthesis: mapping a Verilog
memory to an FPGA block RAM is very different from mapping a logical AND to the LUT primitive of an FPGA.

While it's possible to have all these constructs present in a single design, such a design would quickly become
very convoluted, and it's be hard to isolate the concepts that I want to explain for different phases.

So different designs will be used to illustrate different concepts.

All of them can be found in my [yosys_deconstructed](https://github.com/tomverbeure/yosys_deconstructed) project on GitHub.

In the text below, I'll always be using `my_design` as the example design on which I'm operating, but keep in mind that
the graphs or generated code may come from some different example.

## Loading the Whole Design

Before calling `synth_ice40`, you need a design to synthesize. To do that, you can use one
of the many Yosys design front-ends. The most common one is the Verilog language front-end.

```
read_verilog my_design.v
```

Reading in the Verilog kicks off a complex process that parses the Verilog, and converts it to an abstract syntax tree (AST).
It already resolves some functions, splits the design into sequential and combinatorial statements etc.

Finally, it generates an RTLIL (RTL Intermediate Language) representation of the design: the core representation used by 
Yosys as input and as output of all the different passes. 

Various Verilog operators and function have been transformed into functional cells such as `$add`, `$mul`, `$shift`, `$logic_not`, 
`$reduce_and`, `$concat`, `$memrd`, `$memwr`, and many more. (See [rtlil.cc](https://github.com/YosysHQ/yosys/blob/master/kernel/rtlil.cc))

At any point in time, it's possible to export the RTLIL representation to a file. It's also possible to read in such files
with the RTLIL front-end.

While the `read_verilog` command can understand virtually all synthesizable Verilog constructs, it's important to know that
it can be extremely liberal in the way it parses Verilog. It will freely read Verilog that wouldn't compile correctly 
with common Verilog simulators.

One should always do some sanity checks on the design by simulating it, or by running it through some linting tool (e.g.
by running Verilator in linting mode.)

The result for `read_verilog` is a loose collection of design modules on which no consistency checking has been performed.
For example, if one module instantiates a submodule and connects a port that doesn't exist on the submodule, no error
will be reported. This will happen later in the process...

Here is a very simple design, [`simple_design.v`](https://github.com/tomverbeure/yosys_deconstructed/blob/master/simple_design.v):

```Verilog
module simple_design(clk, reset_, a, b, z);

	input clk;
	input reset_;

	input [7:0] a;
	input [7:0] b;
	input [7:0] z;

	always @(posedge clk, negedge reset_)
		if (!reset_)
			z <= 0;
		else
			z <= a + b;

endmodule
```

After the reading the Verilog, the [simple_design RTLIL](https://github.com/tomverbeure/yosys_deconstructed/blob/master/simple_design.0.read_verilog.il)
contains the same information but converted into high level RTLIL objects.

Yosys has the ability to dump the contents of the internal representation as a connected graph. That often makes it much
easier to understand that contents of the RTLIL representation:

![read_verilog]({{ "./assets/yosys_deconstructed/simple_design.0.read_verilog.svg" | absolute_url }})


# "begin": Loading and Checking the Whole Design

```
begin:
	read_verilog -lib -D_ABC +/ice40/cells_sim.v
	...
```


It's very common for a design to instantiate FPGA-specific functional blocks such as PLLs, IO pads, memories, DSPs and more.

The definition of these primitives can be found in some kind of library file. 

There are often different file types for the same library. Most common is a Verilog simulation model and a Liberty (.lib) file 
for synthesis.

In addition, different library files can be used during different stages of the process: when reading in the whole design,
the cell library may contain all FPGA primitives that can be instantiated in the FPGA, including those that can't be
automatically instantiated during techmapping (the process of converting the logic onto FPGA specific primitives.) The
mapping library will then only contain those cells that should be used during the techmapping phase.

In this case, we are reading the `cells_sim.v` file. It contains cells that are compatible with the SiliconBlue cell library.
SiliconBlue Technologies was a startup that was specialized on low power FPGAs.Lattice Semiconductor acquired them in
2011 and transformed their technology into the Lattice iCE40 FPGA product line.

Some of the `cells_sim.v` are blackboxes that map directly to a hard cell in the FPGA for which there isn't even
simulation behavior: PLLs, oscillators, RGB LED driver, I2C and SPI unit, ... They are annotated with the `(* blackbox *)`
Verilog attribute, which instructs Yosys to ignore these modules going forward and just keep them as-is during the
coming processing passes.

Most of the cells, however, have a simulation model attached to them, allowing the designer to verify a design with special cells
in simulation as well.

However, in this case, the simulation model doesn't matter: `read_verilog` gets called with the `-lib` parameter. This 
tells Yosys to treat all modules in the Verilog file as black boxes except those that explicitly have the attribute 
`whitebox` or `lib_whitebox`.

```
begin:
	...
	hierarchy -check -auto-top
	...
```

When instantiating Verilog module, you can often specify module parameters. These parameters can influence the
way the RTL operates. A good example can be seen below:

<XXX>

When the same module is instantiated in the design multiple times with different parameter values, the hierarchy
command will create unique versions of these modules, one for each unique set of parameters.

You can see this here in the RTLIL version of the module:

<XXX>

The optional `-check` parameter will verify that the design is now complete: all modules are defined, either as an RTL
design, or as a black box.

Finally, the `-auto-top` option will identify which module of the design is the top-level module. A top-level module is
a module that is not instantiated in any other module. When there are multiple top-level modules (which really
doesn't happen), Yosys uses a score based heuristic and selects the one with the highest score.

```
begin:
	...
	proc
```

The final of importing a new design is the first one in a long series of RTLIL transformation steps. 

After reading in Verilog, the RTLIL still contains higher level object called a `RTLIL:Process`. These contain
sub-objects related to case statements, flip-flops with resets, initialization values etc.

The `proc` statement goes through a number of sub-steps that replace all these concepts into multiplexers, 
flip-flops, and latches. It also identifies asynchronous resets, and removes dead code.

# Flatten

```
flatten:
	flatten
	tribuf -logic
	deminout
```

Right now, our design database is still fully hierarchical. Now is the time to remove all that hierachy into one
flat blob of logic and cells. Modules with the `blackbox` attribute aren't touched. (It's possible to apply different
synthesis recipes to different parts of your design. One way to do this is to manually attach the `blackbox` attribute
to a submodule if you don't want to it be touched.)

The `tribuf` command converts $mux cells with a 'z' input into tristate buffers. This makes it possible to 
instantiate tristate output pads in a design in a generic way, without explicitly instantiating a technology-specific
tristate capable IO pad. The '-logic` option converts internal-only tri-state buffers into regular logic: internal
tri-state buffers were once common in ASICs, but have disappeared by the end of the nineties.

Finally, the `deminout` command goes over all inout ports and replaces them by input-only or output-only ports 

