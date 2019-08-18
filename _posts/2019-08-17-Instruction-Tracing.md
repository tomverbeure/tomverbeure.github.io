
layout: post
title: RISC-V Instruction Tracing
date:   2019-08-17 10:00:00 -0700
categories:
---

* [Introduction](#introduction)

# Introduction

# PicoRV32

The [PicoRV32](https://github.com/cliffordwolf/picorv32) is a well known tiny CPU core that's often used by hobbyists who want
to get some hands-on experience with RISC-V.

One feature that's mentioned in the documentation, but doesn't get a lot of attention is the presence of a 
[trace interface](https://github.com/cliffordwolf/picorv32/blob/d124abbacd655e449becb9a05cb70ff45c50fa9b/picorv32.v#L157-L159?):

```Verilog
module picorv32 #(
    ...
	parameter [ 0:0] ENABLE_TRACE = 0,
    ...
) (
	input clk, resetn,
	output reg trap,

	output reg        mem_valid,
	output reg        mem_instr,
	input             mem_ready,

	output reg [31:0] mem_addr,
	output reg [31:0] mem_wdata,
	output reg [ 3:0] mem_wstrb,
	input      [31:0] mem_rdata,

    ...

	// Trace Interface
	output reg        trace_valid,
	output reg [35:0] trace_data
);
```

Here's what the documentations says about it:

> **ENABLE_TRACE (default = 0)**
>
> Produce an execution trace using the `trace_valid` and `trace_data` output ports. For a demontration of this 
> feature run `make test_vcd` to create a trace file and then run `python3 showtrace.py testbench.trace firmware/firmware.elf` to decode it.

This is where the documentation ends, but the inner workings are easy to derive from the source code:

The upper 4 bits describe the kind of contents of the trace word:
```
    ...
	localparam [35:0] TRACE_BRANCH = {4'b 0001, 32'b 0};
	localparam [35:0] TRACE_ADDR   = {4'b 0010, 32'b 0};
	localparam [35:0] TRACE_IRQ    = {4'b 1000, 32'b 0};
    ...
```

Multiple bits can be set at the same time!

* `TRACE_IRQ`: whenever the picorv32 is IRQ mode, bits 35 is set to 1.
* `TRACE_BRANCH`: the current trace word is a branch. The lower 32 bits contain the destination address.
* `TRACE_ADDR`: the current trace word contains the address of a load or a store to memory operation.
* Otherwise: the current trace word contains any kind of data that was calculated or fetched by the current instruction

When the picorv32 executes, the information on the trace interface can be used to reconstruct major parts of how
a program executed instruction by instruction on the CPU.

Let's see how that works:

* Clone the picorv32 repo on GitHub and follow all the installation instructions.

    If you're starting from scratch, this will take quite a while, since it includes compiling a full
    RISC-V GCC toolchain.

* Create a trace by running `make test_vcd`.

    This will run a simulation that executes some instruction tests as well as some simple benchmark.
    The end result are the `testbench.vcd` and `testbench.trace` files. The latter contains the 36-bit`trace_data`
    vectors that we're interested in.

* Convert the trace file to a readable format: `python3 showtrace.py testbench.trace firmware/firmware.elf > testbench.ins`


The `testbench.trace` file looks like with this:

```
0ffffffff   -> ignore data until first branch
8xxxxxxxx   -> Switch from normal mode to interrupt mode. 
8xxxxxxxx   -> Instruction result unknown
800000000   -> Instruction result 0x00000000
800000160   -> Instruction result 0x00000160
800000008   -> Instruction result 0x00000008      
a00000160   -> Load or store to address 0x00000160
800000008   -> Instruction result 0x00000008
8xxxxxxxx   -> Instruction result unknown
a00000164   -> Load or store to address 0x00000164
...
8xxxxxxxx
100000008   -> Switch interrupt mode to normal mode. Branch to address 0x00000008
1000003e0   -> Jump to address 0x000003e0
000000000
```

Not super informative! But the `showtrace.py` command uses that data 
*in combination with the disassembled code* to create `testbench.ins`:

```
    =ffffffff ** SKIPPING DATA UNTIL NEXT BRANCH **
IRQ =00000000 | 00000010 | 0200a10b | 0x200a10b
IRQ =00000000 | 00000014 | 0201218b | 0x201218b
IRQ =00000000 | 00000018 | 000000b7 | lui ra,0x0
IRQ =00000160 | 0000001c | 16008093 | addi ra,ra,352 # 160 <irq_regs>
IRQ =00000008 | 00000020 | 0000410b | 0x410b
IRQ @00000160 | 00000024 | 0020a023 | sw sp,0(ra)
IRQ =00000008 | 00000024 | 0020a023 | sw sp,0(ra)
IRQ =00000000 | 00000028 | 0001410b | 0x1410b
IRQ @00000164 | 0000002c | 0020a223 | sw sp,4(ra)

... skip 218 lines ...
IRQ =00000000 | 00000158 | 0001410b | 0x1410b
    >00000008 ** UNEXPECTED BRANCH DATA FOR INSN AT 0000015c! **
    >00000008 | 0000015c | 0400000b | 0x400000b
    >000003e0 | 00000008 |     aee1 | j 3e0 <irq_stack>
    =00000000 | 000003e0 | 00000093 | li ra,0
    =00000000 | 000003e4 | 00000113 | li sp,0
    =00000000 | 000003e8 | 00000193 | li gp,0
    =00000000 | 000003ec | 00000213 | li tp,0
    =00000000 | 000003f0 | 00000293 | li t0,0
    =00000000 | 000003f4 | 00000313 | li t1,0
    =00000000 | 000003f8 | 00000393 | li t2,0
    =00000000 | 000003fc | 00000413 | li s0,0
...

```

There is a one-to-one relationship between the trace data and decoded instruction stream.

Let's see what kind of information we have access to:

```
IRQ =00000000 | 00000018 | 000000b7 | lui ra,0x0
```

* `IRQ`: the `TRACE_IRQ` bit was set. 
* `=`:  the trace data contained the result of an instruction.
* `>`: the CPU executed a branch operation to the given address.
* `@`: the CPU did a load or store operation from or to memory.

* `00000018` is the address of the instruction that was just executed.
* `000000b7` is the instruction opcode.
* `lui ra,0x0` is the decoded instruction opcode.

Notice how the trace data does not contain the program counter for each executed instruction. This is not necessary:
*as long as instructions don't branch, the next program counter value can be derived from the assembler code*!



# Resources

* [RISC-V Trace Spec](https://github.com/riscv/riscv-trace-spec)
* [Trace Debugging in lowRISC](https://riscv.org/wp-content/uploads/2016/07/Tue1200_TracelowRISC_WeiSong.pdf)

* [ELFIO](http://elfio.sourceforge.net)
* [Dissecting and exploiting ELF files](https://0x00sec.org/t/dissecting-and-exploiting-elf-files/7267)
* [RISC-V ELF psABI specification](https://github.com/riscv/riscv-elf-psabi-doc/blob/master/riscv-elf.md)
