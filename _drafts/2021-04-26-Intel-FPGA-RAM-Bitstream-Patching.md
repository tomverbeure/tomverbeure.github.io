---
layout: post
title: Updating RAM Initialization Contents of Intel FPGA Bitstreams
date:  2021-04-25 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The logic elements of FPGAs are configured with the desired values 
through a bitstream: lookup tables get their content, switches on interconnect 
networks create the desired routing topology, flip-flops are connected to the 
right clock network, etc. 

Most FPGAs also allow block RAMs to be given a non-zero content during
configuration.

This is an essential feature when the FPGA has a soft-core CPU, because it's
the easiest way to have boot core present after powering up. In my personal
designs, I often use tiny CPUs to implement controllers for all kinds of 
low speed protocols like I2C, SPI, Ethernet PHY MDIO etc. In those cases,
all the firmware is pre-baked in block RAMs.

Using tiny CPUs instead of hardware also allows very rapid iteration: if
you can avoid the process of synthesis and place-and-route, and replace
it by compile firmware and update bitstream, you can save minutes for
tiny design, or hours for large ones.

Which brings up to the question: how can you avoid that process?

In this blog post, I'll describe 2 techniques:

* the official one, which requires hand-instantiation of an Intel
  FPGA RAM model and using a HEX or a MIF file. 
* a hack that makes it possible to use standard inferred RAMs in Verilog
  and initialize them with `$readmem(...)`. This also makes the RTL of
  your design compatible across different FPGA families

# The Generic Way to Infer Initialized RAMs

The standard, generic way to add RAM to your FPGA design is something like this:

```verilog
    localparam mem_size_bytes   = 2048;
    localparam mem_addr_bits    = $clog2(mem_size_bytes);   // $clog2 requires Verilog-2005 or later...

    reg [7:0] mem[0:mem_size_bytes-1];

    wire                     mem_wr;
    reg [mem_addr_bits-1:0]  mem_addr;
    reg [7:0]                mem_rdata;
    reg [7:0]                mem_wdata;

    always @(posedge clk)
        if (mem_wr) begin
            mem[mem_addr]   <= mem_wdata;
            mem_rdata       <= mem_wdata;       // Some Intel FPGA RAMs require this...
        end
        else
            mem_rdata  <= mem[mem_addr];
```

Any competent FPGA synthesis tool will infer a 2KB block RAM from the code above.

If you want the RAM to be initialized with content, you just add the lines below:

```verilog
    initial begin
        $readmemh("mem_init_file.hex", mem);
    end
```

This method will work for simulation and, once again, most competent FPGA tool will
synthesize a bitstream that initializes the block RAM with content after configuration.

An important observation here is that during the whole process from RTL to bitstream, 
the FPGA tool will process teh `$readmemh()` statement during RTL analysis and
synthesis, which happens near the front of the whole process.

As a result,a dumb implementation will require restarting the process at that point
when you change the contents of `mem_init_file.hex`. At least, that's how it
is for Quartus...

There must be a better way...

# Manual Instantiation of Intel Block RAMs


I often want to exploit very specific features of a particular FPGA's block RAM.

A common cases is where I want to make sure that my block RAM has flip-flops both at the
input of the RAM (address, write data, write enable) and at the output (read data.)

This increases the read latency of the RAM from one to two cycles, but in many
designs, that's not an issue, and it can result in significant clock speed improvements.

For cases like this, FPGA RAM inference is often hit-and-miss: a good example
is when you have a case where there's a pipeline stage on the output of the RAM, which is then 
used as an operand of a multiplier:

```verilog
    reg [7:0] mem[0:mem_size_bytes-1];

    always @(posedge clk)
        if (mem_wr_p0) begin
            mem[mem_addr_p0] <= mem_wdata_p0;
            mem_rdata_p1     <= mem_wdata_p1;       // Some Intel FPGA RAMs require this...
        end
        else
            mem_rdata_p1     <= mem[mem_addr_p0];

    // Additional pipeline stage to break timing path between RAM and multiplier input
    always @(posedge clk)
        mem_rdata_p2    <= mem_rdata_p1;

    always @(posedge clk)
        result_p3       <= some_other_data_p2 * mem_rdata_p2;
```

*(The _px suffix indicates the pipeline stage number.)*

The synthesis tool has 2 options here about which flip-flops to use for `mem_rd_data_p2`: it could
use the output FFs of the RAM, or it could use the input FFs of the DSP block.

When I want fine control over which FF to use, I will instantiate the RAM by hand with an
Intel RAM primitive cell.  Like this:

```verilog
    // altsyncram is an Intel primitive for all synchronous RAMs.
    // It has tons of tweaking options...
    altsyncram u_mem(
        .clock0   (clk),
        .address_a(mem_addr)
        .wren     (mem_wr),
        .data_a   (mem_wdata),
        .q_a      (mem_rdata_p2)
    );

    defparam 
        u_mem.operation_mode    = "SINGLE_PORT",
        u_mem.width_a           = 8,
        u_mem.width_ad_a        = mem_addr_bits,
        u_mem.outdata_reg_a     = "REGISTERED";         // <<<<<<<<<<

    always @(posedge clk) begin
        result_p3 <= some_other_data_p2 * mem_rdata_p2;
    end
```

The marked line is key here: using "REGISTERED" enables the output FFs of the RAM and adds
the additional pipeline stage.

The code above can't be used with other FPGAs, and even simulating it is a hassle, because the 
simulation model is encrypted and only works with some commercial Verilog simulation tools. Or
you need to write your behavioral `altsyncrma` memory model.

My workaround for that is to have an `\ifdef` that selects regular Verilog for simulation,
and `altsyncram` for Synthesis.

Anyway, the method above allows allows the following parameter:

```verilog
    defparam 
        u_mem.operation_mode    = "SINGLE_PORT",
        u_mem.width_a           = 8,
        u_mem.width_ad_a        = mem_addr_bits,
        u_mem.outdata_reg_a     = "REGISTERED",
        u_mem.init_file         = "mem_init_file.mif";  // <<<<<<<<<<

```

MIF stands for "Memory Initialization File". It's an Intel proprietary text file format
to, well, initialize memories.

I use my own `create_mif.rb` tool to convert binary files into a MIF files.

It's even possible to use Verilog inferred RAMs with MIF files:

```verilog
    (* ram_init_file = "mem_init_file.mif" *) reg [7:0] mem[0:mem_size_bytes-1];
```

The problem with that method is that simulation is now even more problematic: no
simulator knows what to do with the `ram_init_file` attribute!

# Fast Bitstream Update after Changing a MIF File

The beauty of using an `altsyncram` and a MIF file is that you can easily update
bitstream after changing the MIF file **without starting out from scratch**.

Just perform the following steps:

* Change the MIF file with the new contents 
* Quartus GUI: go to ... -> Update Memory Initialization file  (XXX)

     This update the Quartus compiled design database with the new
     memory contents.

* Quartus Gui: ... -> Assemble (XXX)

    Create a bitstream from the Quartus compiled design database

Instead of using a GUI, I use a Makefile to do the 2 Quartus steps:

```makefile
QUARTUS_DIR = /home/tom/altera/13.0sp1/quartus/bin/

update_ram: sw 
	$(QUARTUS_DIR)/quartus_cdb <my_design> -c <my_design> --update_mif
	$(QUARTUS_DIR)/quartus_asm --read_settings_files=on --write_settings_files=off <my_design> -c <my_design>

sw:
	cd ../sw && make
```

The `sw` rule builds the latest firmware version and creates the new MIF files. `quartus_cdb` updates
the design database, and `quartus_asm` creates the new bitstream.

# Faster Bistream Update Usign Generic Instantiation

To update inferred RAMS that were initialized with `$readmemh()`, we need to hack
the Quartus design database ourselves. This is easier that you think: it turns
out that Quartus uses the MIF file format in that internal database!

The steps to update your inferred RAMs are as follows:

* find the MIF file in the database that's used for your RAM

    I do this by simply listing all the MIF file

    ```sh
    cd quartus/db
    ll *.mif
    ```

* create a MIF file for the inferred RAM

    In my firmware build makefile, I always build HEX file (for use 
    by `$readmemh` and MIF file.

* copy your create MIF file to the MIF files in the internal database

The last step is done by my Makefile:

```makefile
QUARTUS_DIR = /home/tom/altera/13.0sp1/quartus/bin/

U_MEM       = $(wildcard ./db/*u_mem*.mif)

update_ram: sw $(U_MEM)
	$(QUARTUS_DIR)/quartus_cdb <my_design> -c <my_design> --update_mif
	$(QUARTUS_DIR)/quartus_asm --read_settings_files=on --write_settings_files=off <my_design> -c <my_design>

$(U_MEM): ../sw/mem_inif_file.mif
	cp $< $@

sw:
	cd ../sw && make
```

1. the `sw` rule still first builds the latest firmware version, and creates a `../sw/mem_init_file.mif`.
1. the `U_MEM` variable contains the path the RAM MIF file in the design database.
1. the `$(U_MEM)` rule copies my MIF file to the one in the database.
1. the `update_ram` rule is the same as before: it creates the new bitstream.




