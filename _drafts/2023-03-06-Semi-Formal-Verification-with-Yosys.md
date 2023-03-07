---
layout: post
title: Semi-Formal Verification with Yosys
date:   2023-03-06 00:00:00 -0700
categories:
---

* TOC
{:toc}


# Introduction 

I have written a couple of formal verification blog posts in the past.
[A Bug-Free RISC-V Core without Simulation](/risc-v/2018/11/19/A-Bug-Free-RISC-V-Core-without-Simulation.html)
tells the tale of designing a working, if very crappy, RISC-V CPU without running a single
simulation by using the open source [riscv-formal](...) formal verification test suite with SymbiYosys
as the driver behind it.  In [Under the hood of Formal Verification](/rtl/2019/01/04/Under-the-Hood-of-Formal-Verification.html),
I discussed how Yosys, SymbiYosys and a bunch of third part formal solves make formal
verification a reality. And 
[The Case of the Phantom Packets - A Formal Debugging Posterchild](/2019/12/14/A-Formal-Debugging-Posterchild.html)
shows how a formal verification saved the day in finding a hard to find bug.

The examples in those blog posts where using pure formal verification, in the sense that
there was no simulation involved at all: constraints were specified with `assume` statements, 
`assert` statements instructed the formal solver engines to check the validity of a claim,
and `cover` statements told the solver to find cases where a condition could be reached.

In all those cases, you need to tell the formal solver how many steps to run when trying to find
whether the `assert` or `cover` gets triggered or not. And that's a serious limitation: many designs
have legitimate conditions that will only trigger after thousands or even millions of clock cycles.
When a verifying the conditions of even smaller design can take seconds, it's impossible for a formal 
solver to run that long!

The following simple example:

```verilog
module blink(input clk, output led);

    reg [15:0] counter = 0;

    always @(posedge clk) 
        counter <= counter + 1'b1;

    assign led = counter[15];

endmodule
```

It's a simply blinky

