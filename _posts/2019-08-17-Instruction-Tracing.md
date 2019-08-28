
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

* Introduction: a drawing showing the complete system: CPU, trace interface, encoder, transport medium, decoder and debugger with
  source code would be very helpful to set the stage.

* "Software, known as a decoder, will take this compressed branch trace...". How can you talk about a decoder when the word
  encoder hasn't been mentioned yet? And suddenly we're dealing something that's compressed without ever saying who
  was involved in this compression?

* The introduction goes to much in detail to quickly: the part that that is RISC-V specific about no conditional instructions is a
  lower level detail that should be moved to section 2.1.1: sequential instructions.

* 1.0.1 Nomenclature: there is definition of decoder, but not a definition of encoder.

* 1.0.1 "The approach relies on an offline copy..." ... "There is no need for either assembly or high-level source code to be
  available." Now which one is it???

* The numbering of section 2 makes no sense. It starts with 2.1. There is no 2.2. There is also no justification about
  the contents of sections 2.1.1, 2.1.2, etc.

* 2.1 instruction delta tracing: "Instruction trace delta modes provide ...". What is a delta mode? It appears out of nowhere.

* Before section 2.1.1, there should be a paragraphs that says "In the remainder of this section, we will discuss the behavior
  and contents of an instruction delta trace for different types of instructions" or something like that.

* 2.1.1: "This characteristic means that there is no need to report them via the trace, ..." Which trace is meant here: the interface
  between CPU and encoder, or between encoder and decoder? I assume it's the latter, but it's not obvious. The spec needs precision
  and clear definitions.

* 2.1.1: shouldn't it be mentioned here that the trace might (or should?) also contain the number of sequential instructions that
  were retired?

* 2.1.3: "an indirect jump is an uninferable PC discontinuity". This is in contradiction with 3.1.1 where some indirect jumps
  are inferable if the register is loaded by AUIPC or LUI.

* 2.1.4: "... in order to instruct the trace decoder to classify the instruction as an indirect jump even if it is not". Isn't this
  an encoder specific implementation detail? Instead of "classify", it's more correct to say "treat it similar to an indirect jump..."

* 2.1.5: in 2.1.4, an interrupt or exception is said to be treated as an indirect jump. Here it is said to be treated as a
  synchronization as well. Does this mean that the trace needs to contain both? I understand that the trace must indicate that it
  is now in an interrupt/exception context, so that's different than an indirect jump, but since a synchronization contains that
  information, then isn't the indirect jump redundant?

* 2.1.6: "The following modes are optional". The spec should start by saying that there are different operating modes before saying
  which ones are optional.

* 2.1.6: "The active run-time options must be reported in the te_support packet..." Aaaaah! There are packets! A new concept that was
  never introduced earlier.

* 2.1.6.1: "All packet formats apart from format 3 output addresses in differential form by default." What is "format 3"? Actually, what are
  packet formats?

  In general: section 2 starts out by describing the kind of information that an encoder should include in a trace in order implement
  a working system. But starting with 2.1.6, it suddenly veers off course by going into gory details about an actual encoder implementations.
  That doesn't belong in this part of the spec and should be moved to section that expliclty mention that it is just a potential
  implementation and not a normative part of the spec.

* 2.1.6.3 Implict return: remove mention of "te_inst" packet and use generic terms that are not encoder implementation specific.

* 2.1.6.4 "branch map" is not defined earlier but is used here as if everybody is supposed to know what it is and how it works. In fact,
  googling for "branch map" (with quotes included) results in an UltraSOC presentation, but nothing more authoritive.

* 2.1.6.4: the branch predictor type is again an implementation detail. This should be made more clear.

* 2.1.6.4: Branch predictor states need more explanation. Does "predict 0" mean: predict no branch taken?

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

Existing: This works by tracking execution from a known start address and sending messages about the deltas
taken by the program. These deltas are typically introduced by jump, call, return and branch type
instructions, although interrupts and exceptions are also types of deltas.

Conceptually, the system has the following fundamental components (see figure ...):

* A CPU with an instruction trace interface that contains all relevant information to successfully
  create a processor branch trace and more. This is a high bandwidth interface: in most implementations,
  it will supply a large amount of data on each CPU execution clock cycles.
* A hardware encoder that takes in the CPU instruction trace and compresses it into a lower bandwidth
  trace packets.
* A transmission channel that is used to transmit or a memory to store
  these trace packets.
* A decoder, usually software on an external PC, that takes in the trace packets and, with knowledge of
  the program binary that's running the originating CPU, reconstructs the program flow. This decoding
  step can be done off-line or in real-time while the CPU is executing.

The primary goal of this document is to specify the instruction trace interface between a RISC-V CPU and an
encoder. It establishes a standard for CPU designers to follow such that they can interface with encoders
from various IP providers.

In addition, this document also details an example of a compressed branch trace algorithm and a packet format
to encapsulate the compressed branch trace information. However, this is not a normative
part of the specficiation.

...

< When an interrupt or exception occurs, or the processor is halted, the final instruction executed beforehand must be traced.
> When an interrupt or exception occurs, or the processor is halted, the final instruction executed beforehand must be included in the trace.


1.0.1 Nomenclature

An encoder is a piece of hardware that takes in RISC-V instruction data on its ingress port and transforms it into
trace packets.

A decoder is a piece of software that takes the trace packets and reconstructs the execution flow of the code
executed in the RISC-V core.

2.1 Instruction Delta Tracing

...

An instruction delta trace of an instruction sequence can be encoded efficiently by exploiting the deterministic
way in which the processor executes a known program. However, since the decoder relies on an offline copy of the program binary
that is being executed, it is generally unsuitable for dynamic (self-modifying) programing or for cases where access
to the program binary is prohibited.

While the program binary is sufficient, access to the assembly or high-level source code will improve the ability
of the decoder to present the decoded trace, e.g. by annotating the instructions with source code labels, variable
names etc.

...

2.2 Contents of an Instruction Delta Trace


2.2.1 Sequential Instructions

2.2.2 Uninferable PC Discontinuities

An uninferable program counterin discontinuity is a program counter change that can not be inferred from the
execution binary alone. For these cases, the instruction delta trace must include a destination address: the
address of the next valid instruction.

Examples of this are indirect jumps, where the address of the next instruction is determined by the contents of a register
rather than a constant that is embedded in the program binary.

2.2.3 Branches

For RISC-V, a branch is an instruction where the jump is conditional on the value of a register. In order to be able
to follow program flow, the trace must include include whether or not a branch was taken or not. For a direct branch,
no further information is required. The RISC-V ISA does not support indirect branches where the branch address is stored
in a register.

2.2.4 Interrupts and Exceptions

Since interrupts can occur while executing a regular instruction sequence that otherwise wouldn't result in an
instruction delta packet, the trace must include the address where normal program flow ceased, as well as give
an indication of the asynchronous destination address, which may be as simple as reporting the exception type.

<paragraph after this is weird.>

2.2.5 Synchronization

...


2.3 Optional and Run-Time Configurable Modes

An instruction trace encoder may support multiple tracing modes. To make sure that the decoder treats the
incoming packets correctly, it needs to be informed of the currently active mode. The active run-time mode
must be reported by packet that is issued by the encoder whenever the encoder configuration is changed.

Here are common configuration mode examples:

* delta address mode

    Program counter discontinuities are encoded as delta.

* full address mode

    Program counter discontinuities are encoded as absolute address values.

* implicit exception option

    Destination addresses of CPU exceptions are assumed to be known by the decoder, and thus not encoded
    in the trace.

* implicit return option

    The destination address of function call returns is derived from a call stack, and thus not encoded
    in the trace.

* branch prediction option

    Branches that are predicted correctly by an encoder branch predictor (and an identical copy in the decoder)
    are not encoded as taken/non-taken, but as a more efficient branch count number.

2.3.1 Delta Address Mode

   This is the default mode, where non-sequential program counter changes are encoded as the difference between
   the previous and the current address. These difference almost always require less bits than the full address,
   and thus result in higher compression ratios.

2.3.2 Full Address Mode

    When this option is enabled, all addresses in the trace are encoded as full addresses instead of delta form.
    This kind of encoding is less efficient, but it can be a useful debugging aid for software decoder
    developers.

2.3.3 Implicit Exception Option

    The RISC-V Priviledged ... specifies exception handler base addresses in the utvec/stvec/mvec CSR registers.
    In some RISC-V implementations, the lower address bits are specified in the ucause/scause/mcause CSR registers.
    By default, both these values are reported by the trace encoder when an exception or interrupt occurs.

    The implicit exception option omits the trap handler address from the trace, and thus improve encoding efficiency.
    This option can only be used if the decoder can infer the address of the trap handler using just the exception
    cause.

2.3.4 Implicit Return Option

    ...

    Returns can only be treated as inferable if the associated call had already been reported as such in an
    earlier packet. The encoder must ensure that this is that case.


# Resources

* [RISC-V Processor Trace GitHub Repo](https://github.com/riscv/riscv-trace-spec)
* [RISC-V Processor Trace Spec](https://github.com/riscv/riscv-trace-spec/raw/master/riscv-trace-spec.pdf)
* [SOC Level Analytics, Trace & Debug for RISC-V Designs - UltraSOC](https://content.riscv.org/wp-content/uploads/2019/05/UltraSoC-PPT.pdf)
* [Trace Debugging in lowRISC](https://riscv.org/wp-content/uploads/2016/07/Tue1200_TracelowRISC_WeiSong.pdf)

* [ELFIO](http://elfio.sourceforge.net)
* [Dissecting and exploiting ELF files](https://0x00sec.org/t/dissecting-and-exploiting-elf-files/7267)
* [RISC-V ELF psABI specification](https://github.com/riscv/riscv-elf-psabi-doc/blob/master/riscv-elf.md)
