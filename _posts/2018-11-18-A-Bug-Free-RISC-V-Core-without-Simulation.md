---
layout: post
title:  "A Bug-Free RISC-V Core without Simulation"
date:  2018-11-19 00:00:00 -1000
categories: RISC-V
---

* TOC
{:toc}


# Introduction

Earlier, I had a [quick look at SpinalHDL](/rtl/2018/08/12/SpinalHDL.html) as a candidate to replace Verilog for my hobby projects.

But as much as one can read the documentation and checkout some trivial tutorials, you need a real project to see if a language
fits your needs.

Since all the cool kids are designing their own RISC-V cores these days, I felt the need to write one myself 
as well: [the MR1 core](https://github.com/tomverbeure/mr1).

Verifying a CPU the traditional way is error prone and tedious. But with the arrival of
[SymbiYosys](https://symbiyosys.readthedocs.io/en/latest/), an open source formal verification tool, and with the existence of
[riscv-formal](https://github.com/cliffordwolf/riscv-formal), a RISC-V formal verification test suite, all the components
are in place to design a bug-free RISC-V core without the need to simulate anything.

So that was the plan.

*This project was completed about a month before the announcement of RISC-V design contest, which is probably a blessing. :-)*

# Goals

* Design my own minimal [RISC-V](https://riscv.org/specifications/) core

* Get hands-on experience with [SpinalHDL](https://spinalhdl.github.io/SpinalDoc-RTD/master/index.html)

* Use formal verification to ensure correctness

* Only use SpinalHDL Core

    SpinalHDL comes with a pretty elaborate library. I expicitly did not want to use any of that. One of the reasons
    is that I want to publish my code under an *Unlicense* license: the code is completely public domain
    and anyone can do whatever they want with it. The SpinalHDL Library is published under the MIT License and
    I'm not enough of lawyer to understand the practical consequences of that.

    The other reason is simply that I want to start with the very basics. As I get more proficient, I may
    start using more advanced features.

I imposed an explicit requirement to not simulate *anything* before getting a 100% PASS on all the formal tests.

There were some additional guidelines for what I wanted the RISC-V core to do:

* performance/cycle had to be better than the ubiquitous [picorv32 RISC-V core](https://github.com/cliffordwolf/picorv32)

    In practice, that's not a very difficult target: the picorv32 is mostly designed for clock speed, but its IPC
    is pretty bad, requiring at least 3 cycles per instructions and often quite a bit more.

* Get a PASS on *all* the riscv-formal tests

    The biggest consequence of this is that it needs a full instruction decoder. Not only does it need to execute instructions
    correctly, it also needs to NOT execute incorrect instructions. In terms of the riscv-formal test suite, this means that
    an incorrect instruction needs to be marked as a trap on the RVFI interface. (It does *not* mean that the functional
    CPU should support traps.)

* Focus on passing the riscv-formal test as quickly as possible

    In the first round, I didn't want to go out of my way to look at achievable clock speed, minimal area, or maximum IPC (as long
    as it was better than a picorv32.) Once I passed this milestone, I knew that I'd start iterating on one or more of those
    metrics, because optimizing stuff is fun.

* RV32I only at first

    This is a consequence of the previous point. I think compressed instruction support is essential if you want to use
    a RISC-V core for a small, embedded CPU core that replaces a complex control FSM in order to save memory. So it's high
    on the list of desirable features. But it adds a bit of complexity that detracts from the as-quickly-as-possible goal.

    Adding multiplication is really easy, but RV32IM support also implies HW support for DIV.
    I didn't want to bother with that just yet.

* No interrupts, halt, traps

    The riscv-formal test suite doesn't have tests for these, so they are out. I really want to support interrupts and halt eventually.

* No CSRs

    Same thing as for the previou point: when I started the project, there was not support for this in the test suite. Looking at the
    latest riscv-formal commits, support for these are being added.

# Some Early Design Decisions

* Split instruction and data bus

    The picorv32 has only one bus for both instructions and data. I hate it. :-) You can always go from split to joint if performance
    isn't critical, but you can't do the opposite.

    Since all hobby designs are using FPGAs, and since most FPGA have RAMs that are true dual-ported memories, you can connect one port
    ot the instruction bus and the other port to the data bus. You never need to join the busses, and you get the best possible performance.

* Separate request and response bus with their own valid/ready

    Initially, my design won't need it, I want to have the option to have multiple read requests in flight.

* 3 stage pipeline: Fetch, Decode, Execute

    In an FPGA, you'll probably want to use RAMs for the register file. These kind of RAMs are almost always synchronous
    and their output delay is often quite long, so you want to clock their outputs without too much logic because
    they'll become the critical path quickly.

    This naturally results in a 3 stage pipeline: issue the register file read in the Fetch stage, reflop the output in Decode,
    use the result in Execute.

    That said, for simplicity, initially I issued the register file read in Decode, so the output of the RAMs were not 
    reflopped before they were used in the Execute stage. This had a major clock speed impact on my first version. 

# Decoder

I started out with the decoder, where a 32-bit instruction word enters, gets classified into an instruction type (which more or less
corresponds to a 7-bit RISC-V opcode: AUIPC, LUI, ALU, ...), and an instruction format (R, I, J, ...) as defined in the RISC-V
specification.

This type/format combo gets passed on to the next stage, in addition the RVFI interface, which is the interface that's used by
the riscv-formal test suite to observe which instructions are being retired by the CPU, along with the register inputs, register
output, memory transactions, and status (halt, trap, intr, ...)

The CPU core is supposed to decorate the various fields of the RVFI structure as the instructions moves down the pipeline.

When the instruction has completed, the RVFI interface must have rvfi_valid asserted. This is the trigger for the formal suite to
perform various checks. When *all* tests are passing, you can consider the CPU verified.

When there's only a decoder, most of the RVFI fields are completely meaningless: there is no register file yet to fill in the rs1\_data
and rs2\_data fields, there is no ALU to fill in the rd\_data field, and there's no load/store unit to fill in the issued memory
tranactions and the result of them.

But what *can* be filled in is the `trap` field. When an illegal or unsupported instruction is encountered, the `rvfi_trap` field must
be asserted.

Out of the box, the testsuite has an example `complete` test that verifies that the decoder issues a `trap` when an invalid instruction
is not flagged as such by the decoder.

The first version of the design with only the decoder can be found [here](https://github.com/tomverbeure/mr1/tree/b61c3c7e43e5bd068304bd8c42c01024bcda0f6e/src/main/scala/mr1).
This code is clean enough to pass all SpinalHDL integrity checks (no mismatching vector widths, no combinational loops, ...) to
convert it into clean Verilog. But it doesn't have the RVFI interface to make a formal check possible.

That happens with [the next version](https://github.com/tomverbeure/mr1/tree/cfb3f6a161918586bd74ab4595afbff775b147da/src/main/scala/mr1).

It adds a pass-through Fetch block and, more important, adds
[the RVFI interface](https://github.com/tomverbeure/mr1/blob/cfb3f6a161918586bd74ab4595afbff775b147da/src/main/scala/mr1/Decode.scala#L191-L221).

With the RTL in place, all that was needed was an MR1 compatible version of the
[complete test](https://github.com/tomverbeure/riscv-formal/blob/5f0bb313217d69b79eb3a5d31796cc5a45c4a3ef/cores/mr1/complete.sv) and everything
was ready for the first formal test.

```bash
cd ~/projects/riscv-formal.tvb/core/MR1
sby -f complete.sby
```

With only 40-something instructions, an RV32I decoder is pretty straightforward, but there were obviously a bunch of bugs in my original RTL code,
and they were found immediately.

The `complete` test finishes in just a couple of seconds. When the test fails, the result is a VCD file of just a few clock cycles.

It took a little bit of time before I got comfortable with my debugging routine, but it ended up going like this:

* Check the log file for the offending assert.

* Run the `disasm.py` script on the VCD file to create a list of executed instructions.

    In order to understand the expected behavior, you need to know which instructions were running and which one failed.

    The first two weeks, I decoded the instruction words manually, with the RISC-V specification in hand. Turns
    out that the `disasm.py` script does all of that for you. I could have saved many hours by doing this right from the start.

* Compare the `rvfi_*` signals of the offending instruction with the expected value.

    In the case of the `complete` test, this mean comparing the `rvfi_trap` and `rvfi_valid` against `spec_valid` and `spec_trap`.
    For most other tests, you'll be comparing various rvfi and spec signals, guided by the failing assert.

* Once you see the difference, you can start digging in waveforms and RTL, and fix the bug.

* Rerun the test.

    This is where you hit one of the negative points of formal verification: it's sufficient to change on little thing in your design to
    end up with a completely different failing case, even if that little thing didn't actually fix your bug.

    When running simulations, you're often progressively peeling the onion: first it runs for a 100 cycles, then 110 cycles
    after fixing something simple, then it runs for 1000 cycles, then 10000, and so on until the test is fully passing.

    During this progression, the same test will usually send the same input stimuli, and as you debug the design, you get
    comfortable with the state of the design during that one test.

    With formal, this is not the case (unless you overconstrain the input with `assume` statements.) After each fix, you need to find your
    bearings again and figure out what's going wrong this time.

    This would be bad if it weren't for the fact that formal is much better at zeroing in on a bug very quickly: it can't simulate
    10000 cycles anyway, but for a design like a simply pipelined CPU, it will trigger the failing case in just a few cycles. That makes
    it much easier to figure out what's going wrong.


I spent an hour or two in evenings on this project. According to my git commit log, I had the decoder fully debugged after 3 evenings.

That work included setting up my first SpinalHDL project, baby steps in getting started writing my first RTL in SpinalHDL, 
figuring out how to set up and run riscv-formal on my own design, debugging the decoder.

The actual debug from first formal run to `complete` test fully passing only took about about an hour or so.

The amazing part is that formal essentially stress tests your design under all possible conditions with no corner cases were left unturned.

# Instructions and the Difference between Traditional and Formal Tests

With the decoder logic functional, it was time for some fun implementing individual operations.

This requires some basic infrastructure: register file, execute stage, and program counter (PC).

The riscv-formal test checks the progression of an instruction before and after, so even if you just want, say, a formal ADD instruction test
to pass, you still need the program counter to be correct.

And important thing to keep in mind is that all pure formal instruction tests rely on the RVFI interface to check the behavior
but don't really check what happens with the result during the next cycle.

For example: 

When it checks an ADD instructions, it will check that the RVFI_PC_WDATA field of the RVFI bus (the program counter
after the execution) is equal to RVFI_PC_RDATA + 4. It will similarly check that registers were read from the correct addresses 
through the RVFI_RS1_ADDR and RVFI_RS2_ADDR fields, it will use the values on RVFI_RS1_DATA and RVFI_RS2_DATA to check that the RVFI_RD_WDATA
field is correct etc.

However, it will *not* check that you were really fetching data from the right address of the register file. Or that you're writing
the data on RVFI_RD_WDATA back to the correct address in the register file. Or that the hardware will indeed use RVFI_PC_WDATA
as PC for the next instruction.

What I learned here is that each test in the riscv-formal suite only covers a very targeted subset of behavior. If you only pass the
ADD test, there are no guarantees at all that your CPU will successfully execute ADD instructions. For that, you need to pass
some very important other tests as well:

The `pc_fwd` and `pc_bwd` are used to prove the part where you check that the program counter gets updated for
real for all instructions. The `reg` check proves that register reads and writes are consistent from one instruction to the
next. And so forth.

The [riscv-formal Verificaton Procedure](https://github.com/cliffordwolf/riscv-formal/blob/master/docs/procedure.md) documentation 
sort of makes this clear, but it can still come as a surprise if you've never done formal verification before: when you write a 
test the traditional way, it's very common to not only explicitly cover the feature that you want to test, but also implicitly
a bunch of features that you didn't want to test.

For example:

In a traditional, directed ADD test, you might want to create a small assembler program that looks like this:
```
LD r1, <op1_address>
LD r2, <op2_address>
ADD r3, r1, r2
ST r3, <result_address>
```

When you simulate that on your DUT CPU, in addition to testing ADD, you will also cover your instruction fetcher, your program counter
update logic, your memory load and store logic. 

This is not the case for formal: it will feed all possible valid and nonsense instructions into the pipeline, then feed in the
ADD. As long as those initial instructions don't hang the pipe, it won't complain for that particular test.

The positive flip side of this is that you can verify a whole bunch of instructions despite that fact that there's no instruction
fetch, load/store unit, or register write-back: riscv-formal was simply feeding instructions straight into the decoder and checking 
what came out of the execute block.

Once the ADD test was passing, other ALU instructions were almost trivial, and the implementation speed was determined 
primarily by my lack of SpinalHDL skills.

It was time to start thinking about memory accesses.

# Fetch

Instruction fetching can be made really complicated. To make it manageable, I started with a fetcher that simply waits for
the instruction before issuing the next request.

In addition, the hazard logic was as simple as possible: if there's a conflict, just stall the pipe. No bypass paths of any kind.

Speaking about hazards: the bad part is that I feel like I made too many mistakes before getting it right. Probably too rushed
instead of first thinking things through. But the good part is that it's something where formal verification truly shines: no
matter how obscure the deadlock, the bug will be teased out in seconds or minutes, and waves will be waiting with a 
minimum repro case.

# LSU

Not complicated, or so I thought, and I was able to get my formal test pass quickly.

But it's also the case where I got truly burnt by not running a test... that didn't exist at the time: I had implemented RVFI interface
so that it'd match the behavior of the core. But the behavior of the core was wrong, and thus the RVFI interface was wrong as well.

Since the error only happened for non-word transactions, it didn't show up even after running the initial LED blink test and was only
unconvered after implementing the wrapper for and running `dmemcheck`.

Showing once again: a passing instruction test doesn't make the instruction works.

# Blinking LED

Less than 2 weeks after starting, all instructions were covered, the pipeline was fully in place, and I had a mini-design
with RAM and a GPIO. Time to fire up Quartus, synthesize the whole thing, and load it into that cute little Altera EP2C5
development board.

And...

SUCCESS! I had an LED blinking! A real, working CPU without running a single simulation!

I ran the same C program on a picorv32, which, based on the blinking frequency, ran about 1/3rd of the speed.

The other number weren't great though: 2182 LEs (mr1) vs 1582 (picorv32) and 50MHz vs 99MHz.

# Optimizations

Since my primary goal was to get something passing as quickly as possible, there were tons of optimization opportunities.
A fantastic rabbit hole!

I added an additional memory stage. ADD and SUB resources were merged. The same resources were used for compares as well.
Unnecessary conditionals were removed. Etc etc.

Eventually, I ended up with 1259 LEs (mr1) vs 1582 (picorv32) and 83MHz vs 99MHz, with the critical path in the instruction
fetch or LSU. I thought that was a decent trade-off.

All the time, riscv-formal was watching over me to make sure I didn't break things.

# A Bad Surprise

Every once in a while, I'd run the latest version on the FPGA. And suddenly, the LED didn't blink.

Since my formal tests were passing, I had to go in with a SignalTap (a logical analyzer on the FPGA, it's fantastic) to 
see what was going one. The CPU was hanging.

This shouldn't happen if the `liveliness` check is passing.

It tooks a while before I figured it out, but there was a bug in the wrapper code that instantiates the MR1 core in the
riscv-formal testbench. 

I forgot the exact details, but the net result was that, due to a typo, the formal test was accidentally guided into avoiding hangs. That's not a smart idea when checking for hangs.

# Runtime Issues

One of the negatives of using formal verification is that lack of feedback about the runtime. Instruction tests take
seconds to run, and most others have runtimes of a few minutes.

But the `pc_fwd` test was a mystery: initially, it'd finish in about 15 minutes, but as the design changed it started to take longer. On my latest version, I had it running for 1301 hours (yes, that's almost 3 months!) and it still didn't 
complete. (Once I started that run, some other project captured my attention, so I just kept it going.)

The problem is: there's just no way to know up front or while running how long it will still go. And, worse, I have no clue
why it suddenly started running much longer, and how to fix it.

# Epilogue

While I wasn't able to match the 99MHz of the picorv32, it felt pretty good about my effort. But just for fun, I decided to
see where the VecRiscv would end up compared to the MR1 and the picorv32.

I chose one of the smallest configurations without bypass logic or multiplier/divider but with barrel shifter, so 
very similar to the MR1.

Result:

* 106 MHz (VexRiscv) vs 82 MHz (mr1) vs 99MHz (picorv32)
* 991 LEs vs 1259 vs 1582

In other words: it's smaller, and it synthesizes faster, and has the same or better IPC than MR1. And it has a million 
configuration options to effortly raise the performance from 0.52 to 1.44 Dhrystone/MHz. 

# Conclusion

This was a lot of fun.

If you're planning to design your own RISC-V core, you'd be insane to not make use of riscv-formal. It's pretty easy to get going and pretty easy to make it work with your own core.

I like SpinalHDL enough to make it now my language of choice for hobby projects. It can be used as a better Verilog with less typing, and that's how it was used for this project, but I'm already starting to use more complex features.

Finally, if you're just looking for a small and fast RISC-V core for your own projects, use the VexRiscv. 

