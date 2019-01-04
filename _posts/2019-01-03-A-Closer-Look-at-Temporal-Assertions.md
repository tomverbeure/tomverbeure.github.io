---
layout: post
title:  A Closer Look at Formal Proof and Temporal Assertions
date:   2019-01-03 17:00:00 -0700
categories: RTL
---

# Table of Contents

* [Introduction](#introduction)

# Introduction

It has been said that writing things down is often one of the best ways to force oneselves
to structure thoughts and learnings, and to gain a deeper understanding in the processes.

After having played with formal verification to prove the correctness of my small and
very crappy MR1 RISC-V CPU, I wanted to understand what it was that made everything work.
I started looking into the source code of the various tools that were used. There were 
things that were immediately obvious, there were many other that were not so obvious
at all. In the process I also learned about and experimented with more advanced forms
of formal verification that what is available today. 

The process of figuring things out was not linear at all. I often jump between completely
unrelated projects. It's one of the fun parts of a hobby after all. But even when
specifically looking at formal, there were dead ends where I just couldn't figure out
what was going on, which were then picked up later after first dealing with other stuff.

In this blog post, I'm trying to structure what I've learned. It's mostly for my own
benefit: some parts were revised a couple of times because things became clearer as
I was writing it down.

But if it helps others getting a better understand as well: so much the better!

# Components of the SymbiYosys Formal Flow

n the past few years, one of the great steps forward for the open source hardware design community 
has been the emergence of formal design verification in the form 
of [SymbiYosys](https://symbiyosys.readthedocs.io/en/latest/). It's just one of the many tools
written by open source All-Star Clifford Wolf.

At its core, SymbiYosys is a middleware that links Verilog design which contains narrow set of formal 
commands to a SAT solver. SymbiYosys itself is a script around Yosys.

Let's quickly go over the various components:

* SAT solver

    A tool that is used to prove that there exists a solution to a boolean formula.

    The pure boolean equations obviously map directly to combinatorial logic gates (AND, OR etc). But they can also 
    can contain state elements that can be assigned new values that become active the next cycle.
    These obviously map directly to flip-flops.

    The SAT solver can prove that, all while observing the constraints of the design, a particlar
    rule will always be satisfied, or it can figure out which inputs need to be applied to a boolean network
    to make a particular equation true.

    There are a bunch of different open source SAT solvers, each with the own strength and weaknesses. One
    thing that they have in common is that they support a common input format: SMT2. 

* Yosys

    Yosys is an open source synthesis tool by the same author as SymbiYosys. It is very modular, with different 
    frontends to read in new designs (Verilog, blif, json, Synopsys liberty, ...) that ultimately
    compile the design to an RTLIL (RTL Intermediate Language). 

    It has a ton of transformational passes that convert one RTLIL design into a different RTLIL design. 

    And, finally, there are bunch of backends that covert the final RTLIL design into the desired format.
    One of these supported format is SMT2.

    Yosys is under very active development. New optimization passes are being added all the time, 
    technology libraries are being created or improved. Bugs are being fixed in frontends, error
    message become more descriptive.

* SymbiYosys

    With Yosys really doing all the heavy lifting, SymbiYosys is a collection of Python scripts that make it 
    easier to get a formal verification run going. It defines a configuration file format that
    allows one to gather various options and the different files that will be needed. It creates
    the necessary directories, copies around files, launches Yosys and the SAT solver and provides clean
    feedback to the user.
    
    While extremely useful for somebody who wants to practice formal verification, SymbiYosys isn't particularly
    interesting for what this blog post will be about.

# Synthesizing a Design with Formal Verification Statements

Let's start with a very simple design:

```Verilog
module demo1(
    input clk
    );

    reg reset_;

    initial reset_ = 1'b0;
    always @(posedge clk) reset_ <= 1'b1;

    reg [1:0] cntr;
    always @(posedge clk) begin

        if (cntr == 2)
            cntr <= 0;
        else
            cntr <= cntr + 1;

        if (reset_) begin
            cntr <= 0;
        end
    end

    assert property(!reset_ || cntr != 3);

endmodule
```

After running SymbiYosys on this, it will create the `design_smt2.smt` file, the input to the
SAT solver.



