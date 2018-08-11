---
layout: post
title:  "Moving Away from Verilog - A First Look at SpinalHDL"
date:   2018-08-11 22:00:00 -0700
categories: RTL
---

Introduction
------------

Electronics in general and digital design is what I do. I love coming up with an new archticture for a major block. 
I love writing RTL. I love debugging my code up to the point where everything just works. It's what I do for a living
and I don't want to do anything else.

When I love it so much that I also want to do it in my spare time (though it needs to compete for attention with my
mountain bike...)

There only one problem: I also love to write and debug code efficiently, and it's very hard to match the tools of
a professional environment at home.

The Verboseness of Verilog
--------------------------

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
 

