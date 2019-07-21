---
layout: post
title: Yosys Deconstructed - A Walk through the Yosys Synthesis Flow - Part 2 - Coarse Optimization
date:   2019-07-04 10:00:00 -0700
categories:
---

* [Introduction](#introduction)
* [Coarse: Technology Independent Optimizations](#coarse-technology-independent-optimizations)
* [opt_exr and opt_clean](#opt_expr-and-opt_clean)
* [check](#check)
* [opt](#opt)

## Introduction

We left [Part 1](/2019/07/02/Yosys-Flow-Deconstructed-Part-1.html) of this series with a sea of cells that 
are a very close representation of the Verilog RTL that was fed into Yosys.

No meaningful optimizations were performed and, other than hand-instantiated primitives, all functional blocks
are generic and relatively high-level. Operators are working on the signals and vectors that were
declared in the RTL. 

For example, an addition of 2 vectors is still represented by a single addition
operator instead of lower level individual cells.

Many operations can, and sometimes must, be performed at this level of abstraction before
moving on the next step where the first technology-specific manipulations will be started.

These operations are done during the `coarse` phase.

## Coarse: Technology Independent Optimizations

The `coarse` phase has 17 steps. 4 of those are `opt_clean`, which just removes cells and wires that aren't
used anymore: Yosys encourages that cleaning up is done as a separate pass after real work has been completed. It
probably makes those 'real' passes easier to implement as well.

Some commands, such as `opt_expr`, and `opt`, are repeated multiple times. Even `opt` itself is sequence
of re-running multiple optimization steps (including `opt_expr`!) in a while loop, until no more modifications
can be performed anymore.

The ordering of all the `coarse` commands seems to be less exact science and more a recipe that has been
shown to get good results. (Not that there's anything wrong with that!)

In this series of blog posts, I'm looking specifically at the iCE40 synthesis flow, but Yosys supports a lot of other
technology targets (with varying levels of maturity).

All other flows use a generic `synth` command, but iCE40 has a technology specific version. When using
the default parameters, the `coarse` phases for the iCE40 and the common command differ as follows:

[`./techlibs/ice40/synth_ice40.cc`](https://github.com/YosysHQ/yosys/blob/10524064e94b9fe21483092e2733b1b71ae60b4e/techlibs/ice40/synth_ice40.cc#L256-L276):

```
coarse:
	opt_expr
	opt_clean
	check
	opt
	wreduce
	peepopt
	opt_clean
>>> different
	share
	techmap -map +/cmp2lut.v -D LUT_WIDTH=4
	opt_expr
	opt_clean
	ice40_dsp       <--- if -dsp !
	alumacc
<<<
	opt
	fsm
	opt -fast
	memory -nomap
	opt_clean
```

[`./techlibs/common/synth.cc`](https://github.com/YosysHQ/yosys/blob/10524064e94b9fe21483092e2733b1b71ae60b4e/techlibs/common/synth.cc#L205-L230):
```
coarse:
	opt_expr
	opt_clean
	check
	opt
	wreduce
	peepopt
	opt_clean
>>> different
	techmap -map +/cmp2lut.v -D LUT_WIDTH=<-lut>
	alumacc
	share
<<<
	opt
	fsm
	opt -fast
	memory -nomap
	opt_clean
```

Of note is that fact that the `share` command is done first for ICE40, before doing some other transformations, 
instead of the other way around for the generic version.

For the longest time, `synth_ice40` command invoked the `coarse` phase of the generic `synth` command, but
that changed with [this recent commit](https://github.com/YosysHQ/yosys/commit/218e9051bbdbbd00620a21e6918e6a4b9bc07867)
which introduced support for automatic iCE40 DSP inference (a feature that is supported on the UltraPlus members of the
iCE40 family.)

Right now,  Yosys doesn't have DSP support for any other FPGA family.

Let's have a close look at the individual steps!

## opt_expr and opt_clean

```
coarse:
	opt_expr
	opt_clean
    ...
```

Let's the `opt_expr` help do the talking:

> This pass performs const folding on internal cell types with constant inputs.
It also performs some simple expression rewriting.

The [`add_const_design.v`](https://github.com/tomverbeure/yosys_deconstructed/blob/master/add_const_design.v)
shows a case where this optimization kicks in:

```Verilog
	always @(posedge clk)
		z <= a + b + (1'b1 - 1'b1);
```

Before `opt_expr`:

![add_const before opt_expr]({{"./assets/yosys_deconstructed/add_const_design.2.flatten.2.deminout.svg" | absolute_url }})

What's interesting about the graph above is that the `1'b1 - 1'b1` expression was already reduced to 4'b0000.
Tracing back, it turns out that this optimization was already performed at the very beginning during the
initial `read_verilog add_const_design.v` step!

And here's the design after `opt_expr`:

![add_const after opt_expr]({{"./assets/yosys_deconstructed/add_const_design.3.coarse.0.opt_expr.svg" | absolute_url }})

The `$pos` cell extracts a vector slice from an existing vector. In this case, it feeds through all 4 input bits
to the 4 bits output (you can see this by looking at the RTIL.) That's redundant, of course. And, indeed, when
the next step runs `opt_clean`, we get this:

![add_const after opt_clean]({{"./assets/yosys_deconstructed/add_const_design.3.coarse.1.opt_clean.svg" | absolute_url }})

## check

```
coarse:
	...
	check
    ...
```

The `check` step doesn't do any transformations but just checks for some common issues:

* combinatorial loops
* multiple drivers on the same wire
* used wires without a driver

There are a common checks in most synthesis flows.

Dealing with unconventional and often non-sensical RTL can be a huge rabbit hole, so in the design below, I just
show of these common design mistakes and see how Yosys deals with them:


```Verilog
module check_fails_design(clk, a, b, z0, z1, z2, z3, z4, z5, z6);

	input               clk;

	input               a;
	input               b;
	output              z0, z1, z2, z3, z4, z5, z6;

    // z0 is driven by FF 'a' and FF 'b'
    always @(posedge clk)
        z0 <= a;

    always @(posedge clk)
        z0 <= b;

    // z1 is driven by wire 'a' and wire 'b'
    assign z1 = a;
    assign z1 = b;

    // Combinational loop which includes 'a' as input
    wire   comb2;
    assign comb2 = !z2 & a;
    assign z2 = comb2;

    // Combinational loop without any input
    wire   comb3;
    assign comb3 = !z3;
    assign z3 = comb3;

    // Undriven signal used to create z4 and z5
    wire   undriven;
    assign z4 = undriven | b;
    assign z5 = undriven & b;

    assign z6 = b;

endmodule

```

At the end of the `flatten` phase, the RTLIL graph still exactly matches the design intent of the Verilog RTL:

![check_fails_design after flatten phase]({{"./assets/yosys_deconstructed/check_fails_design.2.flatten.2.deminout.svg" | absolute_url }})

However things start going off the rails after the first `opt_expr` command: 

![check_fails_design after opt_expr]({{"./assets/yosys_deconstructed/check_fails_design.3.coarse.0.opt_expr.svg" | absolute_url }})

The `z3` output, which used to be part of an inverting combinational loop is not inverting anymore!

And really weird stuff happens during the `opt_clean` command:

![check_fails_design after opt_clean]({{"./assets/yosys_deconstructed/check_fails_design.3.coarse.1.opt_clean.svg" | absolute_url }})

`z3` is now simply connected to `comb3`. In the graph, it seems as if `z3` has changed from an output to an input port, but this is
just a graphical misrepresentation: in the RTLIL, 'z3' and 'comb3' are declared as wires that are simply connected to each other.
There is no implied direction in connection, but the graphical representation makes it look like there is.

Because wires `a` and `b` where both assigned to wire `z1` in the original RTL, Yosys considers them all identical. As a result,
wherever `b` as input to a cell, this has now been optimized to `a` being used instead. As a result, `z1` is now simply
driven by `a` instead of both `a` and `b`. Similarly, the FF that used to have `b` as input now used `a` as input as well.

But we were really interested in the output of the `check` command.

That one looks like this:

```
28. Executing CHECK pass (checking for obvious problems).
checking module check_fails_design..
Warning: multiple conflicting drivers for check_fails_design.\a:
    module input a[0]
    module input b[0]
Warning: multiple conflicting drivers for check_fails_design.\z0:
    port Q[0] of cell $procdff$16 ($dff)
    port Q[0] of cell $procdff$17 ($dff)
Warning: Wire check_fails_design.\z3 is used but has no driver.
Warning: Wire check_fails_design.\undriven is used but has no driver.
Warning: found logic loop in module check_fails_design:
    cell $and$check_fails_design.v:23$4 ($and)
    cell $logic_not$check_fails_design.v:23$3 ($logic_not)
    wire $logic_not$check_fails_design.v:23$3_Y
    wire \z2
found and reported 5 problems.
```

Let's go over those one by one:

```
Warning: multiple conflicting drivers for check_fails_design.\a:
    module input a[0]
    module input b[0]
```

Yes, that's caused by 'a' and 'b' both being assigned to 'z1'.

```
Warning: multiple conflicting drivers for check_fails_design.\z0:
    port Q[0] of cell $procdff$16 ($dff)
    port Q[0] of cell $procdff$17 ($dff)
```

This one is due to the registered versions of 'a' and 'b' both being assigned to 'z0'.

```
Warning: Wire check_fails_design.\z3 is used but has no driver.
```

`z3` used to be assigned by a combinational loop. Because of the transformations during 'opt_expr' and 'opt_clean',
the combinational loop has become an undriven net.

```
Warning: Wire check_fails_design.\undriven is used but has no driver.
```

Check!

```
Warning: found logic loop in module check_fails_design:
    cell $and$check_fails_design.v:23$4 ($and)
    cell $logic_not$check_fails_design.v:23$3 ($logic_not)
    wire $logic_not$check_fails_design.v:23$3_Y
    wire \z2
```

What we see here, is that a combinational loop with external inputs does not get optimized away (yet).

There were 5 design mistakes in the Verilog code, and 5 issues were found by the `check` command. That's good.

But let's have a look at the final result of the whole synthesis run:

![check_fails_design final]({{"./assets/yosys_deconstructed/check_fails_design.10.check.2.check.svg" | absolute_url }})

Very little remains of the original design, and when Yosys finishes with the whole flow with a final `check` command,
only this remains:

```
Warning: multiple conflicting drivers for check_fails_design.\a:
    module input a[0]
    module input b[0]
found and reported 1 problems.
```

While Yosys does check for design issues, it is, by default, very forgiving about any mistakes.

The `check` command has the `-assert` option, which makes Yosys error out when issues are found. However, that
option is only available when running `check` as a stand-alone command. It is not possible to add it as a
parameter of the `synth_ice40` command.

Because of this, if you only run the `synth_ice40` command, you *have* go through the Yosys log file and
check for warnings.

Out of curiosity, I ran the same design through Intel's Quartus FPGA tool:

![check_fails_design Quartus]({{"./assets/yosys_deconstructed/check_fails_design_quartus.png" | absolute_url }})

While it doesn't issue a fatal error on undriven nets, it errors out on nets with multiple drivers.

I think that's a more sensible default solution.

## opt

Like the `proc` command which was used during one of the initial phases, the `opt` command is really a script
that executes a bunch of lower level commands.

As usual, the `opt` command has a lot of command line option, but when used as part of the default `synth_ice40`
command, it reduces to this:

```
    opt_expr
    opt_merge

    do
        opt_muxtree
        opt_reduce
        opt_merge
        opt_rmdff
        opt_clean
        opt_expr
    while <changed design>
```

We've already discussed `opt_expr` earlier. It's interesting that it is called again so quickly after the
previous invocation, especially since it's part of the loop that follows!

`opt_merge` finds and merges common expressions. Have a look at this code:

```Verilog
    always @(posedge clk, negedge reset_)
        if (!reset_) begin
            z0 <= 8'd0;
            z1 <= 8'd0;
        end
        else begin
            z0 <= a + b + 1'b1;
            z1 <= a + b + 1'b1;
        end
```

This code seems wasteful in having 2 instances of `a + b`, but I personally find myself writing code this way quite often:
the 2 instances may be separated quite a bit in more complex code, and declaring a common sub-expression explicitly can
make the code less readable. I simply count on the synthesis tool to be smart about it.

Before `opt_merge`, `a + b` is calculated twice:

![merge_design before merge]({{"./assets/yosys_deconstructed/merge_design.3.coarse.3.opt_expr.svg" | absolute_url }})

After `opt_merge`, there is only one such instance:

![merge_design after merge]({{"./assets/yosys_deconstructed/merge_design.3.coarse.4.opt_merge.svg" | absolute_url }})



	opt
	wreduce
	peepopt
	opt_clean
>>> different
	share
	techmap -map +/cmp2lut.v -D LUT_WIDTH=4
	opt_expr
	opt_clean
	ice40_dsp       <--- if -dsp !
	alumacc
<<<
	opt
	fsm
	opt -fast
	memory -nomap
	opt_clean
```
