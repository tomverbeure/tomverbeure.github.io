---
layout: post
title: Yosys Deconstructed - A Walk through the Yosys Synthesis Flow - Part 1 - Getting the Design Ready
date:   2019-07-02 10:00:00 -0700
categories:
---

* [Introduction](#introduction)
* [The Lattice iCE40 FPGA from Verilog to Bitstream](#the-lattice-ice40-fpga-from-verilog-to-bitstream)
* [Yosys and the ICE40 FPGA](#yosys-and-the-ice40-fpga)
* [Before We Start](#before-we-start)
* [Loading the Design](#loading-the-design)
* ["begin": Completing and Checking the Full Design](#begin-completing-and-checking-the-full-design)
* ["flatten": From Hierarchy to Blob of Cells](#flatten-from-hierarchy-to-blob-of-cells)
* [End of Part 1](#end-of-part-1)

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
very convoluted, and it'd be hard to isolate the concepts that I want to explain for different phases.

To work around that, I have a lot of very small Verilog design that each illustrate what happens in one or more
phases.

All of them can be found in my [yosys_deconstructed](https://github.com/tomverbeure/yosys_deconstructed) project on GitHub.

In the text below, I'll always be using `my_design` as the example design on which I'm operating, but keep in mind that
the design name will always be different.

All my example designs have been sent through the full ICE40 synthesis flow, and for each individual step, I've
dumped the internal database (in the form of an RTLIL file, see below) and in the form an SVG file with the internal
database rendered as a graph.

These files can be found in the same GitHub project.

## Loading the Design

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
will be reported. Similarly, the ports of instantiated modules haven't even been annotated with a port direction.
This will happen later in the process.

Here is a very simple design, [`add_ff_design.v`](https://github.com/tomverbeure/yosys_deconstructed/blob/master/add_ff_design.v),
which adds 2 4-bit inputs, stores the result in flip-flop (FF), and sends the result back to the output:

```Verilog
module add_ff_design(clk, reset_, a, b, z);

    input               clk;
    input               reset_;

    input       [3:0]   a;
    input       [3:0]   b;
    output  reg [3:0]   z;

    always @(posedge clk, negedge reset_)
        if (!reset_) begin
            z <= 0;
        end
        else begin
            z <= a + b;
        end

endmodule
```

After the reading in the Verilog, the [add_ff_design RTLIL](https://github.com/tomverbeure/yosys_deconstructed/blob/master/add_ff_design.0.read_verilog.0.read_verilog.il)
contains the same information but converted into RTLIL objects. The RTLIL graph looks like this:

![read_verilog]({{ "./assets/yosys_deconstructed/add_ff_design.0.read_verilog.0.read_verilog.svg" | absolute_url }})


## "begin": Completing and Checking the Full Design

```
begin:
	read_verilog -lib -D_ABC +/ice40/cells_sim.v
	...
```

It's very common for a design to instantiate FPGA-specific functional blocks such as PLLs, IO pads, memories, DSPs and more.

In [`sb_io_pads_design.v`](https://github.com/tomverbeure/yosys_deconstructed/blob/master/sb_io_pads_design.v), 
I instantiate only FPGA primitives, 2 `SB_IO` IO pads and 1 `SB_FF` flip-flop.

Here's one of the IO pads:
```
    ...
	SB_IO u_sb_in (
		.PACKAGE_PIN(sb_in),
		.LATCH_INPUT_VALUE(1'b1),
		.CLOCK_ENABLE(1'b0),
		.INPUT_CLK(clk),
		.OUTPUT_CLK(clk),
		.OUTPUT_ENABLE(1'b0),
		.D_OUT_0(1'b0),
		.D_OUT_1(1'b0),
		.D_IN_0(sb_in_from_pad),
		.D_IN_1()
	);
    ...
```

The definition of these primitives can be found in a library file. 

There are often different file types for the same library. Most common is a Verilog simulation model and a Liberty (.lib) file 
for synthesis.

Different library files can be used during different stages of the process: when reading in the whole design,
the simulation library may contain all FPGA primitives that can be instantiated in the FPGA, including those that can not be
automatically instantiated during technology mapping. 
Meanwhile, the mapping library will only contain those cells that should be used during the techmapping phase.

In this case, we are reading the [cells_sim.v](https://github.com/YosysHQ/yosys/blob/master/techlibs/ice40/cells_sim.v) library file. 

It contains cells that are compatible with the SiliconBlue cell library. SiliconBlue Technologies was a startup that was specialized 
in low power FPGAs. Lattice Semiconductor acquired them in 2011 and their technology became the basis of the Lattice iCE40 FPGA product line.

Some of the `cells_sim.v` cells are blackboxes that map directly to a hard cell in the FPGA for which there isn't even
simulation behavior: PLLs, oscillators, RGB LED driver, I2C and SPI unit, etc. They are annotated with the `(* blackbox *)`
Verilog attribute, which instructs Yosys to ignore these modules going forward and just keep them as-is during the
coming processing passes.

Most of the cells, however, have a simulation model attached to them, allowing the designer to verify a design with these cells
in simulation.

For our purposes though, the simulation model doesn't matter: `read_verilog` gets called with the `-lib` parameter. This 
tells Yosys to treat all modules in the Verilog file as black boxes except those that explicitly have the attribute 
`whitebox` or `lib_whitebox`.

```
begin:
	...
	hierarchy -check -auto-top
	...
```

When instantiating Verilog module, you can often specify module parameters. These parameters can influence the
way the RTL operates at instantiation. 

A good example can be found in [`hier_design.v`](https://github.com/tomverbeure/yosys_deconstructed/blob/master/hier_design.v):


```Verilog
module sub_design(clk, in, out);

    parameter INSERT_FF = 0;

    input           clk;

    input           in;
    output          out;

    generate if (INSERT_FF) begin
        // Insert FF between in and out
        reg out_ff;
        always @(posedge clk)
            out_ff <= in;
        assign out = out_ff;

    end else begin
        // Simply pass in to out.
        assign out = in;

    end endgenerate

endmodule
```

Depending on the value of the `INSERT_FF` parameter, an instance of the `sub_design` module will either
feed `in` straigth through to `out`, or it will insert a flip-flop in between.

The `hierarchy` command will create unique versions of these modules, one for each unique set of parameters.

You can see this here in the RTLIL versions of the module.

[Here](...) 
is the RTLIL for version without FF:

```
attribute \src "hier_design.v:8"
module \sub_design
  parameter \INSERT_FF
  attribute \src "hier_design.v:12"
  wire input 1 \clk
  attribute \src "hier_design.v:14"
  wire input 2 \in
  attribute \src "hier_design.v:15"
  wire output 3 \out
  connect \out \in
end
```

And [here]()
is the version with FF:

```
attribute \src "hier_design.v:8"
module $paramod\sub_design\INSERT_FF=1
  parameter \INSERT_FF
  attribute \src "hier_design.v:20"
  wire $0\out_ff[0:0]
  attribute \src "hier_design.v:12"
  wire input 1 \clk
  attribute \src "hier_design.v:14"
  wire input 2 \in
  attribute \src "hier_design.v:15"
  wire output 3 \out
  attribute \src "hier_design.v:19"
  wire \out_ff
  attribute \src "hier_design.v:20"
  process $proc$hier_design.v:20$9
    assign { } { }
    assign $0\out_ff[0:0] \in
    sync posedge \clk
      update \out_ff $0\out_ff[0:0]
  end
  connect \out \out_ff
end
```

The optional `-check` parameter will verify that the design is complete: all modules are defined, either as an RTL
design, or as a black box.

Finally, the `-auto-top` option will identify which module of the design is the top-level module. A top-level module is
a module that is not instantiated in any other module. When there are multiple top-level modules (which really
doesn't happen), Yosys uses a score based heuristic to determine which module is the most likely to be the top-level.

Before executing the `hierarchy` command, the graph for `hier_design.v` is uninspiring:

![hier before]({{"./assets/yosys_deconstructed/hier_design.1.begin.0.read_verilog.svg" | absolute_url }})

Notice how on the 2 `sub_design` instances ports aren't even annotated with a port name or port direction!

And here's what the graph looks like after running `hierarchy`:

![hier after]({{"./assets/yosys_deconstructed/hier_design.1.begin.1.hierarchy.svg" | absolute_url }})

Much better!

The instances have a port name and a port direction. And the module name of each instance also includes
the `INSERT_FF=1` parameter to indicate that one instance is not like the other. 


```
begin:
	...
	proc
```

The final step of importing a new design is the first one in a long series of RTLIL transformations. 

After reading in Verilog, the RTLIL still contains higher level `RTLIL:Process` objects. These contain
sub-objects related to case statements, flip-flops with resets, initialization values etc.

The `proc` statement goes through a number of sub-steps that replace all these concepts into multiplexers, 
flip-flops, and latches. It also identifies asynchronous resets, and removes dead code.

Before running `proc`:

![read_verilog]({{ "./assets/yosys_deconstructed/add_ff_design.1.begin.1.hierarchy.svg" | absolute_url }})

And after:

![read_verilog]({{ "./assets/yosys_deconstructed/add_ff_design.1.begin.2.proc.svg" | absolute_url }})

The higher level `PROC` object has been replaced with `$adff`, a generic register cell with asynchronous reset.


## "flatten": From Hierarchy to Blob of Cells

```
flatten:
	flatten
    ...
```

Until now, our design database was still fully hierarchical, but it's time to remove all that and convert everything into one
flat blob of logic and cells. Modules with the `blackbox` attribute aren't touched. 

Before:

![flatten before]({{"./assets/yosys_deconstructed/hier_design.1.begin.1.hierarchy.svg" | absolute_url }})

After:

[![flatten after]({{"./assets/yosys_deconstructed/hier_design.2.flatten.0.flatten.svg" | absolute_url }})]({{"./assets/yosys_deconstructed/hier_design.2.flatten.0.flatten.svg" | absolute_url }})

*(Click on image to enlarge)*

The `sub_design` instances are gone, and their internal logic has moved to the top-level.


```
flatten:
    ...
	tribuf -logic
    ...
```

In this day and age, tri-state buffers are only used for IO pads, but there was a time when it was common to have on-chip 
tri-state busses with multiple drivers per data line: instead of a potentially large MUX-tree for concentrate all the potential 
sources of a CPU read bus, there was such a wire with multiple drivers. This saved area, especially for large MUX trees.

[`tribuf_design.v`](https://github.com/tomverbeure/yosys_deconstructed/blob/master/tribuf_design.v)
contains some tri-state examples: a tri-state output IO pad, an internal wire with multiple
drivers. (It also contains an `inout` port, which will be used for the next step.)

```Verilog
module tribuf_design(clk, en_a, a, en_b, b, z0, z1, z2);

    input       clk;

    input       en_a, a;
    input       en_b, b;

    output      z0;
    output reg  z1;
    inout       z2;

    wire        bus;

    assign z0 = en_a ? a : 1'bz;

    assign bus = en_a ? a : 1'bz;
    assign bus = en_b ? b : 1'bz;

    always @(posedge clk)
        z1 <= bus;

    assign z2 = en_a ? a : 1'bz;

endmodule
```

Since the ICE40 FPGA architecture doesn't support internal tri-state busses, they need to be replaced by a MUX. 
And the tri-stated IO pad must be recoginized as such and replaced by a tri-state buffer.

That's exaclty what the `tribuf -logic` command does!

Before:

![tribuf before]({{"./assets/yosys_deconstructed/tribuf_design.2.flatten.0.flatten.svg" | absolute_url }})

We can see `1'z` values as input to the `$mux` cells. These need to go.

After:

![tribuf after]({{"./assets/yosys_deconstructed/tribuf_design.2.flatten.1.tribuf.svg" | absolute_url }})

The `1'z` values are gone: output `z0` is now driven by a `$tribuf` cell and a `$pmux` cell has replaced 
the `$mux` cells that had a `1'z` input.


Here's what the Yosys manual says about `$pmux` cells:

> The $pmux cell is used to multiplex between many inputs using a one-hot select signal. Cells of this type have
a \WIDTH and a \S_WIDTH parameter and inputs \A, \B, and \S and an output \Y. The \S input is \S_WIDTH
bits wide. The \A input and the output are both \WIDTH bits wide and the \B input is \WIDTH*\S_WIDTH
bits wide. When all bits of \S are zero, the value from \A input is sent to the output. If the n’th bit from
\S is set, the value n’th \WIDTH bits wide slice of the \B input is sent to the output. When more than one
bit from \S is set the output is undefined. Cells of this type are used to model “parallel cases” (defined by
using the parallel_case attribute or detected by an optimization).

The representation above won't materially change until much later, when it hits this command 
`opt -fast -mux_undef -undriven -fine`, and the graph changes into this:

![tribuf mux]({{"./assets/yosys_deconstructed/tribuf_design.5.map.0.opt.svg" | absolute_url }})

The internal tri-state bus has been completely transformed into a regular MUX, as expected.


```
flatten:
    ...
	deminout
```

The final step of this phase is the `deminout` command, which, under limited circumstances, replaces 
an `inout` port into either and `input` or `output` port.

Yosys has only limited support of `inout` ports and their usage should be avoided.

In the earlier `tribuf_design.v` file, you might have noticed this:

```Verilog
    ...
    inout       z2;

    assign z2 = a;
    ...
```

The `z2` bidirection port is only used as output.

Before the `deminout` step, the `z2` port of the design is declared in the RTLIL as follows:

```
module \tribuf_design
  ...
  attribute \src "tribuf_design.v:11"
  wire inout 8 \z2
  ...
```

After, it looks like this:

```
module \tribuf_design
  ...
  attribute \src "tribuf_design.v:11"
  wire output 8 \z2
  ...
```

`z2` has been changed from an `inout` to an `output` port.

This transformation only happens under pretty strict circumstances. It's usefulness isn't very clear to me.

## End of Part 1

We've arrived the end the first import phase of a synthesis flow. 

The design has been parsed and converted into a collection of well known primitives that can be
mapped onto hardware.

We are now ready for the second major phase: all kinds of technology independent conversions that will help
us later on with mapping the primitives onto the real hardware.

In part 2 of this series, I will take a look at this second phase.


