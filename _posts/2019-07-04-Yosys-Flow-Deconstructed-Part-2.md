---
layout: post
title: Yosys Deconstructed - A Walk through the Yosys Synthesis Flow - Part 2 - Coarse Optimization
date:   2019-07-04 10:00:00 -0700
categories:
---

* [Introduction](#introduction)

## Introduction

We left Part 1 of this series with a sea of cells that are a very close representation of the
RTL that was fed originally into Yosys.

No meaningful optimizations were performed and all functional blocks, other than hand-instantiated primitives,
are generic and relatively high-level. Operators are working on the signals and vectors that were
declared in the RTL. For example, an addition of 2 vectors is still represented by a single addition
operator instead of lower level individual cells.

Many operations can, and sometimes must, be performed at this higher abstraction level before
moving on the next step where the first technology-specific manipulations will be started.

All this operations are done during the `coarse` phase.

## Coarse: Technology Independent Optimizations

The `coarse` phase has 17 steps. 4 of those are `opt_clean`, which just removes cells and wires that aren't
used anymore: Yosys encourages that cleaning up is done as a separate pass after real work has been done. It
probably makes those 'real' passes easier to implement as well.

Some commands are repeated multiple times, such as `opt_expr`, and `opt`, and even `opt` itself is sequence
of re-running multiple optimization steps (including `opt_expr`!) in a while loop, until no more modifications
can be performed anymore.

The sequence of all the `coarse` commands seems to be less exact science and more of recipe that seems
to be get good results. (Not that there's anything wrong with that!) 

In this blog post, I'm looking specifically at the iCE40 synthesis flow, but Yosys supports a lot of other
technology targets (with varying levels of maturity).

All other flows use a generic `synth` command insteasd of one that's dedicated for iCE40. When using 
the default parameters, the `coarse` phases for the iCE40 and the common command differ as follows:

`./techlibs/ice40/synth_ice40.cc`:

```
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

`./techlibs/common/synth.cc`:
```
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

Of note is that fact that the `share` command is now done first, before doing some other transformations, instead
of the other way around.

For the longest time, `synth_ice40` command invoked the `coarse` phase of the generic `synth` command, but
that changed with [this recent commit](https://github.com/YosysHQ/yosys/commit/218e9051bbdbbd00620a21e6918e6a4b9bc07867)
which introduced support for automatic iCE40 DSP inference (a feature that is supported on the UltraPlus members of the
iCE40 family.)



