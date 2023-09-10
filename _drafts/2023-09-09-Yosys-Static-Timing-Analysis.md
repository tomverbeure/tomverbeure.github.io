---
layout: post
title: Basic Area and Logic Level Depth Reporting with Yosys
date:   2023-09-09 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Recently I was playing with Galois multipliers and needed to information about
the number of gates and logic level depth to get a feel of the general design complexity.
These kind of characteristics are often quoted in scientif papers that compare different
implementations.

The idea was the following:

* create such a multiplier with nothing but XOR and AND operators
* use Yosys to convert the design actual XOR and AND gates
* report the number of XOR of AND gates
* report the logic depth

While commerical synthesis tools like Synopsys Design Compiler have extensive report generation
commands, Yosys is definitely lacking. Reporting the number of cells is possible, but since it's
not a timing driven synthesis engine, you need an external tool for timing analysis. 

Or so I thought...

After some googling around, I discovered the `sta` command:

```
yosys> help sta

    sta [options] [selection]

This command performs static timing analysis on the design. (Only considers
paths within a single module, so the design must be flattened.)
```

With only a little bit of effort, I was able to get the reports that I wanted. This blog
posts describes the steps so that I don't need to reinvent that wheel the next time. 

# The STA command

While it's great to have a static timing analysis (STA) tool in Yosys, it's important to
temper expectations: there's only the bare minimum, which makes sense for a command
that's currenlty implemented in 
[just 315 lines of code](https://github.com/YosysHQ/yosys/blob/master/passes/cmds/sta.cc),
and that's with plenty of comments and whitespace.

To make things work, you'll need the following:

* design converted to basic cells
* a Verilog model for each basic cell that contains timing arc information,
  provided with Verilog `specify ... endspecify` clauses

The command will bail when there are cells without timing information.

The output of the `sta` command is the longest timing path and a histogram for all
timing end points.

There is no way to specify a clock, or input/output deloays. There's also no support for 
multi-cycle or false paths.

# The Design 

Let's try things on a 4-bit Galois field multiplier.

[`gf16_mul.v`](/assets/yosys_sta/gf16_mul.v)
```verilog
module gf16_mul(
    input            clk,
    input      [3:0] poly_a,
    input      [3:0] poly_b,
    output reg [3:0] poly_out,
    output     [3:0] poly_out_comb
    );

    reg  [3:0] a;
    reg  [3:0] b;
    wire [3:0] r;

    always @(posedge clk) begin
        a <= poly_a;
        b <= poly_b;
    end

    wire m_1_1 = a[0];
    wire m_1_2 = (a[1] ^ a[3]);
    wire m_1_3 = (a[2] ^ a[3]);
    wire m_2_1 = a[3];
    wire m_2_2 = (m_1_1 ^ m_1_3);
    wire m_2_3 = (m_1_2 ^ m_1_3);
    wire m_3_1 = m_1_3;
    wire m_3_2 = (m_2_1 ^ m_2_3);
    wire m_3_3 = (m_2_2 ^ m_2_3);

    assign r[0] = (a[0] & b[0]) ^ (a[3] & b[1]) ^ (m_1_3 & b[2]) ^ (m_2_3 & b[3]);
    assign r[1] = (a[1] & b[0]) ^ (m_1_1 & b[1]) ^ (m_2_1 & b[2]) ^ (m_3_1 & b[3]);
    assign r[2] = (a[2] & b[0]) ^ (m_1_2 & b[1]) ^ (m_2_2 & b[2]) ^ (m_3_2 & b[3]);
    assign r[3] = ^{(a[3] & b[0]), (m_1_3 & b[1]), (m_2_3 & b[2]), (m_3_3 & b[3]) };

    always @(posedge clk) begin
        poly_out <= r;
    end

    assign poly_out_comb = r;

endmodule
```

The design only uses XOR and AND operations, with a bunch of flip-flops
thrown in to make things a bit more interesting.

# Convert to Gates

The first step is to read in the design, specify the top level, and convert
everything in an `always` block to internal gates.

```
read_verilog gf16_mul.v
hierarchy -top gf16_mul
flatten
proc
```

In this case, there's only one module, so I could have used `hierarchy -auto-top`
instead. The same is true for `flatten`: it squishes a hierarchical design
into 1 flat blob of logic.

At this point in the process, the Verilog code has been converted into 
a netlist of high-level cells. There hasn't been any mapping to gates yet.

You can see this when you run the `stat` command. It should show something like this:

```
=== gf16_mul ===

   Number of wires:                 52
   Number of wire bits:             82
   Number of public wires:          17
   Number of public wire bits:      38
   Number of memories:               0
   Number of memory bits:            0
   Number of processes:              0
   Number of cells:                 35
     $and                           16
     $dff                            3
     $reduce_xor                     1
     $xor                           15
```

Note how there's `$reduce_xor` cell in there. That's caused by the `assign r[3] = ...`
statement. The input of `$reduce_xor` cell can have a variable width. That's not something
you have in a real gate-level netlist of actual cells.

The next step is to convert the high level cells into generic low level cells:

```
techmap
clean
```




