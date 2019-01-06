---
layout: post
title:  A Closer Look at Formal Proof and Temporal Assertions
date:   2019-01-03 17:00:00 -0700
categories: RTL
---

# Table of Contents

# Why Formal Verification

Design verification has always been much more important for digital hardware than for software.
Most software has a very linear behavior where one instruction gets executed after the other and
behavior is purely data depending: given the same input, you'll usually get the same output. Things
get a bit more difficult when threads are involved, but even there the amount of things going on
in parallel can be counted on one hand.

Meanwhile, in digital hardware land, almost everything happens in parallel. Millions of flip
flops are toggling at the same time, and often interacting with the same limited resource:
arbiters can only serve one request at a time, RAMs typically have at most 2 read and write
ports etc.

So not only do you have the data dependent behavior of software, but you also have an extremely 
strong sensitivity to timing. A bus arbiter to access external DRAM might have 8 inputs, and your
simulation might stress cases where up to 7 of those inputs are requesting access to memory at
the same time and things are working great, but, wouldn't you know it, in that extremely rare
case where 8 inputs are active at the same cycle, a bug is triggered, and your design fails. 

In a production environment, that situation happens about once every two days, even if the arbiter
is running at 1GHz. In other words: it's something that will only happen once every 172E12 clock
cycles!

The reason might be a vector that countains the number of active inputs at any point in time which
was sized with 3 bits, good for 0 to 7 active agents, instead of 4 bits. One of those dreaded 
off-by-one bugs.


Good verification engineers are worth their weight in gold: they will identify a case like this up front. 
They will add a case in the test plan. They will add a cover point to the code. And they'll go 
over the coverage reports to make sure that said cover point has been triggered during one of the
simulations.

They will create a few targeted vectors that trigger the problem case, and they will guide the random
stimuli generator with constraints such that high input activity cases are more likely.

Without a human explicitly identifying this problem case, not many traditional tools will this kind
of vector overflow as an issue: at best, your RTL linting tool might warn that 8 one-bit
signals added together will require a 4 bit result. But that real warning will offen appear in a sea
of harmless false positives.

And, of course, the problem sketched here is actually a very simply one. One that triggers a bug when
8 orthogonal signals assert a exactly the same time, so not *that* complicated to identify up front
as a problem case to begin with.

Similar issues can hide in intricate pipelines for which problem conditions are much harder to imagine.

There must be a better way, and, luckily, there is.

The solution is formal verification.

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
    thing that they have in common is that they support a common input format: [SMT2](http://smtlib.cs.uiowa.edu/)

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

After running SymbiYosys on this, it will create, among others, the `design.ys`, `design_smt2.ys` and `design_smt2.smt` files.

`design.ys` converts the Verilog file into an RTLIL format:

```
# running in demo1/src/
read -formal demo1.sv
prep -top demo1

memory_nordff
async2sync
chformal -assume -early
chformal -live -fair -cover -remove
opt_clean
setundef -anyseq
opt -keepdc -fast
check
hierarchy -simcheck
write_ilang ../model/design.il
```

The most important statement above is the `chformal ... -remove` one: it determines the kind of operation will be performed
by the SAT solver. In this case, I opted for bounded model checking. As a result, checks for liveness, fairness, and cover are
removed.

In cover mode, the statement would have looked like this: 
```
...
chformal -live -fair -remove
...
```

The second script `design_smt2.ys` converts your Verilog file into an SMT2 file:

```
# running in demo1/model/
read_ilang design.il
stat
write_smt2 -wires design_smt2.smt2
```

It's not exactly clear why there are 2 steps instead of having just 1 script, but it doesn't really matter.

The [SMT2 language specification](http://smtlib.cs.uiowa.edu/papers/smt-lib-reference-v2.6-r2017-07-18.pdf)
is a 45 page document with tons of different commands, but the file that's generated by SymbiYosys uses exactly
3 of those: `declare-sort`,`declare-fun` and `define-fun`.

The SMT2 file is created by the Yosys smt2 backend, the source of which can be found 
[here](https://github.com/YosysHQ/yosys/blob/master/backends/smt2/smt2.cc). A quick look at this code shows
that generating an SMT2 file is a pretty lightweight operation: the original Verilog file was synthesized
into a limited set of boolean operations, which are then easily converted to SMT2. There are a few heavier
action to deal with embedded memories, but even those are pretty straightforward to follow.

The real heavy lifting in the process of formally proving a design is, unsurprisingly, done by the SAT solver.

The [manual](http://www.clifford.at/yosys/cmd_write_smt2.html) of the `write_smt2` command has a 
detailed description of the generated commands.


# Limitations of the current formal verification features

Great as they already are, compared to commercial tools, the open source version of 
Yosys is still severly limited in terms of supported features.

That's because the assume, cover, and assert property statements only accept a boolean expression,
whereas advanced tools support SystemVerilog temporal sequences.

In other words, the statement only allow checking things that happen in the current cycle, not
what happened over a sequence of clock cycles.

That doesn't mean that you can't verify sequences, but you need to design additional logic to do so.

Here's a very concrete example:

I recently designed a block that converts CPU reads and writes on an APB bus into ULPI transactions. (ULPI
is a standard interface to control USB PHY chips. It's similar in nature to MII interfaces for Ethernet
PHYs.)

To transmit a packet, the intended use case is the following:

* Write all packet bytes to a transmit FIFO.
* When done, write to a TX_START action bit.
* Wait until the FIFO is completely empty, which indicates that the packet has
  been transmitted.

One could write a traditional testbench to simulate such a case, but that's pretty boring.

It's much faster to use the formal `cover` statement to do this for you!

The [statement](https://github.com/tomverbeure/panologic-g2/blob/b6a174c3a6f69bd2ec3c80cf6d149dd2fedaf3ba/spinal/src/main/scala/pano/UlpiCtrl.scala#L446-L449) 
looks like this in SpinalHDL:

```scala
    cover(!initstate() && reset_
                && tx_data_fifo_level_reached
                && (ulpi_ctrl_regs.apb_regs.u_tx_data_fifo.io.pushOccupancy === 0)
```

That's it!

The cover statement has 4 terms:

    1. Boilerplate to ensure that you don't get some false positive during reset
    2. the transmit data FIFO much have reached a fill level of at least 20 values *at some point*
    3. the transmit data FIFO must be empty at this time on the push side

This very simple 4-line statement will generate a VCD waveform of ~45 clock cycles that will do every necessary
to satisfy the condition inside the cover parenthesis. It's truly a thing of magic!

I did not need to write an APB bus master. I did not have to write a for-loop to issue 20 APB write to the tx_data FIFO write
register. Neither did I have to issue a write to the TX_START register, or write a polling loop to check that the
FIFO was empty.

None of this was necessary because the only way to satisfy the cover condition is by doing those steps anyway, so
the formal tool had no other choice but to come up with those operations itself!

But there *is* an issue with this example: the second terms of the boolean equation is not something that's part
of the real design, but it's helper logic that was addes specifically to make this cover statement work:

```scala
    val tx_data_fifo_level_reached = RegInit(False) setWhen(ulpi_ctrl_regs.apb_regs.u_tx_data_fifo.io.pushOccupancy === 20)
```

`tx_data_fifo_level_reached` is a flip-flop that starts out at 0 and that goes 1 *and stays 1* when the tx data FIFO reaches the
desired fill level for the first time.

In this particular case, it's not a huge deal to add this statement, but nevertheless, it's a hack to work around the fact
that `cover` only supports pure boolean equations. As soon as temporal behavior needs to be check, you need
to improvise.

And those improvisations can get ugly pretty quickly. What if you want to write a cover case where you want to check
2 or more packets to be transmitted, using exactly the same operations that were mentioned above. Now you'll
need to implement some counter that goes up each time a level of 20 is reached. But maybe you want to transmit
20 bytes for the first packet and 1 byte for the second.

This would be totally acceptable if there were no better solutions, but, of course, better solution do exist.
They're just not available for open source tools.

# SystemVerilog Temporal Assertions

What we really want is support for temporal assertions.

SystemVerilog has had them for something like 15 years.

You can find a quick overview of what's supported on 
[this Doulos tutorial page](https://www.doulos.com/knowhow/sysverilog/tutorial/assertions/), 
but it's essentially a very compact way to describe sequences of events.

The example above could have been written like this:

```Verilog
    property p_fifo_tx;
        @(posedge clk)
            (ulpi_ctrl_regs.apb_regs.u_tx_data_fifo.io.pushOccupancy === 20) 
                ##[1:$] (ulpi_ctrl_regs.apb_regs.u_tx_data_fifo.io.pushOccupancy === 0);
    endproperty

    cover property(p_fifo_tx);
    
```

We define a particular property that contains a sequence, then we check that this property
gets covered at least once. *(Note: this code may not compile or execute correctly for a variety
of syntax or sematic reasons, because there is no open source tool to check them!)*

SystemVerilog sequences provide a rich set of operation to schedule events in succession, to
repeat such sequences, to wait for something to happen a certain amount of times etc.

In the simple example above, it waits for the FIFO to reach a level of 20, then the `##[1:$]` operations
tells it to wait between 1 and infinite amount of cycles before the FIFO empty condition is reached.

Of course, since we have now much better flexibility and control over things, it'd be a bit dumb to 
allow waiting for an infinite amount of time. So this would make more sense:

```Verilog
    (ulpi_ctrl_regs.apb_regs.u_tx_data_fifo.io.pushOccupancy === 20) 
            ##[1:30] (ulpi_ctrl_regs.apb_regs.u_tx_data_fifo.io.pushOccupancy === 0)
```

30 clock cycles after reaching a level of 20 should be more than sufficient to go back to empty.

# Rolling Your Own?

One of the key tenets of the open source world is to scratch an itch, to make for yourself that
which isn't available.

To prevent disappointment further down the line: I did not implement such a replacement!

But you need to understand the problem and a solution first before you can do so. And that's something
where I've made quite a bit of progress recently.

For something that works with the current tools, you'll still ultimately need to end up with 
standard Verilog that confirms to the restrictions of what currently exists. This means that you'll 
need a way to covert SystemVerilog temporal assertions (or something equivalent in another RTL
language) into plain synthesizable gates, just like I did earlier when I add the 
`tx_data_fifo_level_reached` flip-flop and supporting logic.

The way I often approach these kind of problems is by writing example cases which I then manually
covert to a potential solution. It's a intuitive bottom-up as opposed to top-down 
theoretical approach that suits me best.

# Some Simple Sequences

Let's start with implementation a simple sequence like this:

```Verilog
sequence b_after_a
    a ##3 b
endsequence
```

This sequence triggers when b goes high exactly 3 cycles after a. Here's a possible implementation:

```Verilog
    assign a_vec[3:0] = { a_dly[2:0], a };
    always @(posedge clk) begin
        a_dly[2:0] <= a_vec[2:0];
    end              

    assign trigger = a_vec[3] && b;
```
Easy!

A slightly more complicated sequence triggers when b goes high between 3 and 5
cycles after a:

```Verilog
sequence b_after_a
    a ##[3:5] b
endsequence
```
And the implementation:

```Verilog
    assign a_vec[5:0] = { a_dly[4:0], a };
    always @(posedge clk) begin
        a_dly[4:0] <= a_vec[4:0];
    end              

    assign trigger = |a_vec[5:3] && b;
```

How about repetitions? 

```Verilog
sequence b_after_a
    a ##1 b[*3]
endsequence
```

This sequence triggers when a is immediately followed by 3 times b.

```Verilog
    assign a_vec[3:0] = { a_dly[2:0], a };
    assign b_vec[2:0] = { b_dly[1:0], b };
    always @(posedge clk) begin
        a_dly[3:0] <= a_vec[3:0];
        b_dly[2:0] <= b_vec[2:0];
    end              

    assign trigger = a_vec[3] && (&b_vec[2:0]);
```
