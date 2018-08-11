---
layout: post
title:  "Moving Away from Verilog - A First Look at SpinalHDL"
date:   2018-08-11 22:00:00 -0700
categories: RTL
---

# Introduction

Electronics in general and digital design is what I do. I love coming up with an new archticture for a major block. 
I love writing RTL. I love debugging my code up to the point where everything just works. It's what I do for a living
and I don't want to do anything else.

When I love it so much that I also want to do it in my spare time (though it needs to compete for attention with my
mountain bike...)

There only one problem: I also love to write and debug code efficiently, and it's very hard to match the tools of
a professional environment at home.

# The Verboseness of Verilog

The biggest problem by far is Verilog. Especially the way modules need to be connected together.

We've all been here:

```Verilog


    wire        mem_cmd_valid;
    wire        mem_cmd_ready;
    wire        mem_cmd_instr;
    wire        mem_cmd_wr;
    wire [31:0] mem_cmd_addr;
    wire [31:0] mem_cmd_wdata;
    wire [3:0]  mem_cmd_be;
    wire        mem_rsp_ready;
    wire [31:0] mem_rsp_rdata;

    wire mem_rsp_ready_gpio;
    wire [31:0] mem_rsp_rdata_gpio;

    ...

    vexriscv_wrapper cpu (
        .clk            (clk),
        .reset_         (reset_),
        .mem_cmd_valid  (mem_cmd_valid),
        .mem_cmd_ready  (mem_cmd_ready),
        .mem_cmd_wr     (mem_cmd_wr),
        .mem_cmd_instr  (mem_cmd_instr),
        .mem_cmd_addr   (mem_cmd_addr),
        .mem_cmd_wdata  (mem_cmd_wdata),
        .mem_cmd_be     (mem_cmd_be),
        .mem_rsp_ready  (mem_rsp_ready),
        .mem_rsp_rdata  (mem_rsp_rdata),
        .irq            (irq        )
    );

    ...

    gpio #(.NR_GPIOS(8)) u_gpio(
            .clk        (clk),
            .reset_     (reset_),
    
            .mem_cmd_sel    (mem_cmd_sel_gpio),
            .mem_cmd_valid  (mem_cmd_valid),
            .mem_cmd_wr     (mem_cmd_wr),
            .mem_cmd_addr   (mem_cmd_addr[11:0]),
            .mem_cmd_wdata  (mem_cmd_wdata),
    
            .mem_rsp_ready  (mem_rsp_ready_gpio),
            .mem_rsp_rdata  (mem_rsp_rdata_gpio),
    
            .gpio_oe(gpio_oe),
            .gpio_do(gpio_do),
            .gpio_di(gpio_di)
        );
```

Now there are a couple of ways to work around this, but all of them have disadvantages that are disqualifying. (This is
obviously very subjective!)

## Verilog-mode

One of the common recommendations is to use Emacs [verilog-mode](https://www.veripool.org/projects/verilog-mode/wiki/Examples).

Verilog mode will analyze your code and expand some commented magic words into signal lists.

The net result is something like this:

```Verilog
module autosense (/*AUTOARG*/
                  // Outputs
                  out, out2,
                  // Inputs
                  ina, inb, inc
                  );
   
   input        ina;
   input        inb;
   input        inc;
   output [1:0] out;
   output       out2;
   
   /*AUTOREG*/
   // Beginning of automatic regs (for this module's undeclared outputs)
   reg [1:0]    out;
   reg          out2;
   // End of automatics
```

I heard for friends in the industry that it's used quite a bit in professional environments, so I gave it a try.

* it didn't do as much as I wanted it to do
* what it was supposed to do, didn't always work
* it's visually really ugly
* the indenting rules were inconsistent

verilog-mode is tool that can save a lot of time, but ultimately, it's a bit of an ugly hack. It just rubbed me the wrong way.
Two months after trying it the first time, I gave it a second chance only to drop it soon after again. It's just not for me.

## SystemVerilog

SystemVerilog has records and interfaces and they are a fantastic way to remove a large part of the verboseness, so that's 
where I looked next.

The main issue there is that it's just not supported very well if you're doing this as a hobbyist.

The only tool that supports a decent amount of features is [Verilator](https://www.veripool.org/wiki/verilator). But 
neither [Icarus Verilog](http://iverilog.icarus.com) nor [Yosys](http://www.clifford.at/yosys/) support records or interfaces. 
And even if you're using the free (as in beer) versions of commerical tools, then you're often out of luck. 
The old [Xilinx ISE](https://www.xilinx.com/products/design-tools/ise-design-suite.html) 
(which I use for my [Pano Logic project](https://github.com/tomverbeure/panologic)) has plenty of limitations and outright bugs for
plenty of regular Verilog constructs, so SystemVerilog is completely out of the question. The same is true for 
[Lattice iCEcube2](http://www.latticesemi.com/iCEcube2): you have to use Synplify Pro for the synthesis part.

A minimal SystemVerilog to Verilog translator could be a solution, at some point I started working on exactly that, but right now
it doesn't exist. 

And even SystemVerilog doesn't have features that could be really useful.

## What I Really Want

What I really want is a system where a zero fanout signal down deep in your design hierarchy automatically
ripples through all the way to an upper hierachy levels until it finds a signal of the same name. One where I can use regular expressions to
rename whole clusters of signals with one line. One where you have hundreds of plugins to write FSMs with all kinds of verification
features enabled by default. One where the most elaborate parameterized multi-threaded FIFO with rewind can be instantiated 
with a few lines of code. One where I don't even have to type the name of the module at the top of the file, because it's inferred
from the file name.



