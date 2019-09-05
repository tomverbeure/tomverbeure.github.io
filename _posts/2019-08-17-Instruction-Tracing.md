
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

# Various

Spec comments:


* 3.1 It is not clear how often data needs to be exchanged between the CPU and the encoder over this interface. Is it per clock cycles?
  Or anything one or more instructions are retired? Or only when important events happen (jumps, conditional branches ...)
  Only in 3.2 is it mentioned that this interface is active everytime instructions are retired.

* 3.1 Are there cases where an instruction_address is *not* passed only on this interface? The current list seems pretty exhaustive.

* itype: there is an exception and an interrupt, but there's only an exception return and no irq return?

* 3.1 says that instruction type is required for *retired instructions for jumps with a target that cannot be inferred from the source code*.
  In 2.1.2, it mentions indirect jumps. But what about LUIPC/JALR and AUIPC/JALR combinations? In this case, address can be inferred from
  the source code, even if that need the value before that? This seems to be confirmed by 3.1.1 which declares an inferable jump as one
  where a register has received a value through AUIPC or LUI. However, it doesn't say anything about how the CPU should determine whether or
  not a register contains a constant. Shall it only do so when the instruction before a jump was AUIPC/LUIPC? Or is it supposed to contain
  a status bit for each register in the register file that remembers whether or not the last store to that register was doing with LUI/AUIPC?

* 3.1 lists the kind of instrutions for which instruction type is mandatory, including jumps with a target that cannot be inferred from
  the source code. In the list with instruction types, there are inferrable/uninferrable pairs for multiple classes. Since those class
  encodings are not mandatory, what kind of type should they be given in a minimal implementation? "other uninferrable jump"?

* If we assume a minimal mandatory implementation, does this mean that the only types supported should be: 0 (everything else),
  3 (return from exception), 5 (taken branch), and 14 (other uninferable jump) ?

* There is no definition of a co-routine swap anywhere. And given that google doesn't come up with anything either, it's probably not
  a bad idea to go in a bit more detail about that.

* 3.1.1  I'd prefer if the actual instructions that determine a certain jump class were written out in full.
  e.g. "jal x1, <offset>" instead of "jal x1".

* table 3.1 tval: currently, it only lists one example under "e.g." which implies that there are more? If not, it should be more explicit
  that there is currently only 1 tval type.

* table 3.8: never referenced in the text, only exists as a table.

* 3.2 For which values of itype is context_type valid?

* 5: This section constantly refers to packet formats, which are defined in section 6? Why not swap them around?

* 5.2: lots of talk about branch maps etc, but still no clear explanation about what a branch map is.

* 6: this chapter, like most others, lack top down clarity. It immediately throw low level concepts at the readers without first
  providing an overview. It'd be much better if it simply started with explaining that there are 3 kinds of packet formats, and
  explain in a qualitative way what they do. And then you dive into lower level details.

* 6: ’sign based compression ... An example of how this technique is used to choose between address formats is given in Section 5.1.'.
  There is no such example. There is also no clear explanation of sign based compression.

* Table 6.1: names such "updiscon" should be defined as "uninferrable PC discontinuity" again, even if they were defined earlier.

* Table 6.4: add horizontal line between address and branch_fmt?

* Table 6.4: updiscon: references 'bpfail' which is the only time this name is used in the entire document.

* 6.1.1 Format 3 branch field: the format 3 packet hasn't even been defined yet, but it immediately talk about a field of it.
  This is caused by Latex placing tables more or less at random, but it'd make more sense if there's be a text introduction about what kind
  of packet exist, and then refer to the table.

* 6.1.2 Format 1/2 updiscon field: it makes no sense that format 3 fields are explained before format 1/2 fields.

* There is a decoder implementation, but no encoder implementation.



Calls:

JAL jumps to pc+offset, and stores pc+4 in the given register.

x1/ra and x5/t0 are the return address and the temporary/alternate link register. So when those registers
are specified as rd, it suggests that it's a function call with a return address.

Since destination address is based on a constant offset, this instruction is inferable.

    jal x1, <offset>
    jal x5, <offset>

JALR jumps to rs1 + imm1, and stores pc+4 in the given register.

    jalr x1, t1, 8

In combination with LUI, JALR can be used to create a jump to any absolute address:

    // This sequence jumps to address 0x2000_0010
    lui  t1, 0x20000
    jalr x1, t1, 0x10

In combination with AUIPC, JALR can be used to create very large position independent jumps:

    // This sequence jumps to PC + 0x2000_0010
    auipc t1, 0x20000
    jalr x1, t1, 0x10

Whether or not JALR is an inferable instruction depends on whether or not the value of the RS1 can be derived
from the context.

# Edits

# Resources

* [RISC-V Processor Trace GitHub Repo](https://github.com/riscv/riscv-trace-spec)
* [RISC-V Processor Trace Spec](https://github.com/riscv/riscv-trace-spec/raw/master/riscv-trace-spec.pdf)
* [SOC Level Analytics, Trace & Debug for RISC-V Designs - UltraSOC](https://content.riscv.org/wp-content/uploads/2019/05/UltraSoC-PPT.pdf)
* [Trace Debugging in lowRISC](https://riscv.org/wp-content/uploads/2016/07/Tue1200_TracelowRISC_WeiSong.pdf)

* [ELFIO](http://elfio.sourceforge.net)
* [Dissecting and exploiting ELF files](https://0x00sec.org/t/dissecting-and-exploiting-elf-files/7267)
* [RISC-V ELF psABI specification](https://github.com/riscv/riscv-elf-psabi-doc/blob/master/riscv-elf.md)
