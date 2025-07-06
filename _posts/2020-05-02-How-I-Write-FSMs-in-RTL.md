---
layout: post
title: How I Write FSMs in RTL
date:  2020-05-01 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I sometimes browse the [FPGA subreddit](https://old.reddit.com/r/FPGA) so see what's going on in that world. 

One topic that comes up relatively often is about how to code FSMs in RTL. I read Reddit almost 
exclusively to kill time while on my phone. Typing out how to code an FSM on a phone is just no fun.

Instead of sitting on the sidelines forever, here's a short write-up about how I do it. There are people
who do it differently, but they are obviously doing it wrong. 

# My FSM Template

All of my FSMs follow this format:

```verilog
    localparam IDLE             = 0;
    localparam SETUP            = 1;
    localparam ACTIVE           = 2;

    reg [1:0] cur_state, nxt_state;

    reg comb_output;
    reg seq_output, seq_output_nxt;

    always @(*) begin
        nxt_state           = cur_state;

        // Default output assignments
        comb_output         = <default output value, this can be an equation>;
        seq_output_nxt      = seq_output;

        case(cur_state)
            IDLE: begin
                comb_output     = <non-default output>;
    
                if (start) begin
                    nxt_state       = SETUP;
                end
            end
    
            SETUP: begin
                if (setup_complete) begin
                    seq_output_nxt      = 1'b1;
    
                    nxt_state           = ACTIVE;
                end
            end
    
            ACTIVE: begin
                seq_output_nxt      = 1'b0;
    
                nxt_state           = IDLE;
            end
        endcase
    end

    always @(posedge clk) begin
        cur_state           <= nxt_state;
        seq_output          <= seq_output_nxt;

        if (!reset_) begin   
            cur_state       <= IDLE;
            seq_output      <= 1'b0;
        end
    end
```

# An FSM Always Consists of 2 Processes

Some people write their FSMs as one clocked process, and every once in a while, I catch myself starting out
doing the same thing. But as soon as you start adding complexity to it, that straightjacket inevitably
breaks down, and I have to convert it to 2 processes anyway.

With 2 processes, you can decide at will which outputs of the FSM become clocked or combinational, and you
can decide at will change one from one category to the other without impacting other code.

The sequential process contains all the FFs and the hard reset logic, but nothing more.

In the code above, I'm using a synchronous reset (it's the right thing to do for ASICs these days, because it's
less cross-talk glitch sensitive), but asynchronous is obviously fine as well (assuming you come out in a
synchronous way, of course!)

# The FSM Code is State Centric instead of Output Signal Centric

There are many people who write their FSM processes as just the inputs to a state changing diagram and
assign the outputs outside of the main FSM process. Like this:


```verilog
    always @(*) begin
        nxt_state           = cur_state;

        case(cur_state) 
            IDLE: begin
                if (start) begin
                    nxt_state       = SETUP;
                end
            end
    
            SETUP: begin
                if (setup_complete) begin
                    nxt_state           = ACTIVE;
                end
            end
    
            ACTIVE: begin
                nxt_state           = IDLE;
            end
        endcase
    end

    always @(posedge clk) begin
        cur_state           <= nxt_state;

        if (!reset_) begin   
            cur_state       <= IDLE;
        end
    end

    assign comb_output      = (cur_state == IDLE) ? <non-default output>  : <default output>;   
    assign seq_output_nxt   = (cur_state == SETUP) && setup_complete  ? 1'b1 :
                              (cur_state == ACTIVE)                   ? 1'b0 :
                              seq_output;
```

In other words, instead of focusing the code on the story of what the FSM does for which state, the story is signal oriented:
what does each signal do for all different states.

I've seen this kind of coding style used by highly competent RTL designers, but I just don't get the appeal.
How can you possibily keep track of what's happening to multiple signals at a time for different states? With an FSM that
focuses on the behavior per state, it's much easier to follow what happens from one step to the other. I usually only care
about what happens to `seq_output` during the `ACTIVE` state, not when my FSM is in the `IDLE` state. 

I sometimes go out of my way to embed assignments in the FSM itself. Imagine a design with `data_valid` output that is governed 
by an FSM and a `data` output that is not, but where `data` is only relevant when `data_valid` is active.

You could write it like this:
```verilog
    assign data     = <some calculation>;

    always @(*) begin
        data_valid      = 1'b0;

        case(cur_state) 
            ...
            ACTIVE: begin
                data_valid      = 1'b1;
            end
            ...
        endcase
    end
```

I might do the following instead:

```verilog
    assign data_int         = <some calculation>;
    ...
    always @(*) begin
        data_valid      = 1'b0;
        data            = data_int;             <<<<<<<<<<<<<

        case(cur_state) 
            ...
            ACTIVE: begin
                data_valid      = 1'b1;
                data            = data_int;     <<<<<<<<<<<<<
            end
            ...
        endcase
    end
```

Note that `data` gets a default assignment that is the same as the assignment in the `ACTIVE` state:
this ensures that no part of the FSM gets mixed into the value of `data` (which would cost extra
gates and reduce timing margin.)

But why?

First of all, it once again groups together all the action of a particular state and condition: the code makes it very explicity
that `data_valid` and `data` have meaning together in the `ACTIVE` state.

Second, when, later, it turns out that `data` can have different kinds of values depending on the state, it can simply add
that locally to that particular state.

Like this:

```verilog
    assign data_int         = <some calculation>;

    always @(*) begin
        data_valid      = 1'b0;
        data            = data_int;

        case(cur_state)
            ...
            ACTIVE1: begin
                data_valid      = 1'b1;
                data            = data_int;
            end
    
            ACTIVE2: begin
                data_valid      = 1'b1;
                data            = <some other value>;
            end
            ...
        endcase
    end
```

It also allows me to do the following:

```verilog
    ...
    always @(*) begin
        ...
        data_valid      = 1'b0;
        data            = {16{1'bx}};    <<<< Make data invalid when data_valid is 0
        ...
        case(cur_state)
            ...
            ACTIVE: begin
                data_valid      = 1'b1;
                data            = data_int;
            end
            ...
        endcase
    end
```

The change above makes it very easy to see on simulation waveforms when `data` is invalid. It can also help finding bugs in case
the downstream code uses `data` when `data_valid` is not asserted.

In some cases, I'll do the following:

```verilog
    always @(*) begin
        data_valid      = 1'b0;
`ifndef SYNTHESIS
        data            = {16{1'bx}};
`else
        data            = data_int;
`endif
        ...
        case(cur_state) 
            ...
            ACTIVE: begin
                data_valid      = 1'b1;
                data            = data_int;
            end
            ...
        endcase
    end
```

Doing so combines ease of debugging, yet ensures optimal and predictable synthesis results. (This is also important when doing formal
equivalence check between gatelevel and RTL.)

# Rigorous Naming Convention for Combinatorial and Sequential Outputs

A sequential output gets the `_nxt` suffix. No exceptions. When due to a design change the signal switches from combinatorial
to sequential or vice versa, all relevant signals get renamed.

*Note: this is not apply when writing SpinalHDL code, since SpinalHDL allows free mixing of combinatorial and sequential
code.*

Most waveform viewers sort signal names alphabetically. That's why I will always use suffixes instead of prefixes. When you
have a bunch of signals like `a`, `a_nxt`, `b`, `b_nxt`, `c`, `c_nxt` etc, I want all `a`-related signals to be grouped together.

(I personally hate embedding the port direction of a signal in the signal name, but if you really like it, at least use suffixes there
too. No prefixes. I want to see all signals of an interface grouped together. I don't want signal completely independent and unrelated 
interface signals to be grouped together just because they all start with `i_`.)


# No Explicit Stay-in-the-Same-State Assignments

I do this:

```verilog
    always @(*) begin
        nxt_state           = cur_state;

        case(cur_state)
            ...
            IDLE: begin
                if (start) begin
                    nxt_state       = SETUP;
                end
            end
            ...
        endcase
    end
```

Not this:

```verilog
    always @(*) begin
        nxt_state           = cur_state;

        case(cur_state)
            ...
            IDLE: begin
                if (start) begin
                    nxt_state       = SETUP;
                end
                else begin
                    nxt_state       = IDLE;     <<<<< Redundant
                end
            end
            ...
        endcase
    end
```

There is no point in stating the obvious, and when there are multiple nested if-else clauses you can get a bunch
of useless clutter quickly.

# Overriding Previous Default Assignments is Totally Fine

I prefer doing this:

```verilog
    always @(*) begin
        nxt_state           = cur_state;

        case(cur_state)
            ...
            DRIVE_BUS: begin
                data_valid_nxt      = 1'b1;         <<<<<
    
                if (data_ready) begin
                    data_valid_nxt      = 1'b0;     <<<<<
    
                    nxt_state           = IDLE
                end
            end
            ...
        endcase
    end
```

instead of this:

```verilog
    always @(*) begin
        nxt_state           = cur_state;

        case(cur_state)
            ...
            DRIVE_BUS: begin
                data_valid_nxt      = data_ready ? 1'b0 : 1'b1;     <<<<<
    
                if (data_ready) begin
                    nxt_state           = IDLE
                end
            end
            ...
        endcase
```

My argument here is the same as the one earlier on about the story that you want to tell:
I want the focus of the code to be on what happens on a group of signals under a particular condition,
not on what each signal does under a variety of conditions. 

In the case above, what's important to me is everything that happens when `data_ready` is high: 
both `data_valid_nxt` going low, and the FSM transitioning to `IDLE`.

When the code is as simple as here, it doesn't make a material difference, but it can be when 
the FSM is complex with many signal assignments.

# Regular vs One-Hot Encoding

One-hot encoding has some benefits in terms of timing and sometimes in terms of resource usage.

Whether I use regular or one-hot encoding, I prefer to the state numbering to be the same.

```verilog
    localparam IDLE             = 0;
    localparam SETUP            = 1;
    localparam ACTIVE           = 2;
```

For regular encoding, the case statement then looks like this:

```verilog
    case(cur_state)
        IDLE: begin 
            ... 
        end
        ...
    endcase

    ...
```

And for one-hot, it looks like this:

```verilog
    case(1'b1) // synthesis parallel_case
        cur_state[IDLE]: begin 
            ... 
        end
        ...
    endcase
```

This is one of the only cases where I'll ever use `synthesis parallel_case` in my code. I will never use `synthesis full_case`.


# No Mealy vs Moore BS

Something that comes up a lot on the FPGA Reddit subforum: How do I code a Mealy FSM? How do I code a Moore FSM?

The answer is simple and, based on the answers on the subreddit, pretty universal: it doesn't matter. Like learning about
[Karnaugh maps](https://en.wikipedia.org/wiki/Karnaugh_map) and 
[Quine-McCluskey optimization](https://en.wikipedia.org/wiki/Quine%E2%80%93McCluskey_algorithm), 
the existence of Mealy vs Moore should be forgotten the moment an engineer gets their degree and enters the professional world. 

I've seen some misguided redditors comment that they ask candidates about Mealy vs Moore during interviews. This should be a 
fireable offense for the interviewer.

That said: 2-process coding style is flexible enough to code any kind of FSM. If, for some weird reason, you want to stick
to Mealy vs Moore concept, go for it. Just keep quiet and don't bother anybody else with it. :-)

# Glitch-Free Outputs

When you want to make sure the output of your FSM is glitch-free, you have a few options.

If a particular output will only ever be high (or low) during 1 specific state of the FSM, you could tie the output
directly to the state vector of your FSM:

```verilog
    localparam IDLE             = 0;
    localparam SETUP            = 1;
    localparam ACTIVE           = 2;

    ... our 2 processes ...

    assign my_glitchfree_output = cur_state[ACTIVE];
```

This technique requires no additional FF, but it only works for one-hot FSMs, and it is no good when `my_glitchfree_output` can be 
high for multiple states. The code below could result in a glitch:

```verilog
    assign my_glitchfree_output = cur_state[SETUP] | cur_state[ACTIVE];
```

For everything else, one-hot or not doesn't really matter: you'll need an additional FF just for that output signal.

Creating that output signal can be done in different ways.

You could make that FF just another sequential output of the FSM:

```verilog
    ...
    always @(*) begin

        my_glitchfree_output_nxt        = my_glitchfree_output;

        case(cur_state)
            ...
            SETUP: begin
                if (setup_complete) begin
                    my_glitchfree_output_nxt    = 1'b1;
                    nxt_state                   = ACTIVE;
                end
            end

            ACTIVE: begin
                my_glitchfree_output_nxt    = 1'b0;
                nxt_state                   = IDLE
            end
        endcase
    end
    ...
```

The benefit of the code above is, once again, that everything related to a particular state and
condition is grouped together. However, if many FSM states transition into the `ACTIVE` state,
it may require a `my_glitchfree_output_nxt = 1'b1` statement for each of those transitions.

The alterative is to implement the FF outside of the FSM, and make use of the `nxt_state` signal.

Like this:

```verilog
    ...
        <FSM code>
    ...

    always @(posedge clk) begin
        my_glitchfree_output    <= (nxt_state == ACTIVE);
    end
```

# For Hobby Code: a State Signal to State Name Ascii Decoder

In the professional world, you'll probably ...hopefully... use a tool like Verdi which understands FSMs and will annotate state signals
with their state name. A Verilog/GTKWave-based debugging flow doesn't have this luxury.

For those cases, the 2-process flow gets one additional debug-only process which translates the state vector into
an ASCII string vector:

```verilog
`ifndef SYNTHESIS
    reg [255:0] cur_state_text;

    always @(*) begin
        case(cur_state)
            IDLE:   cut_state_text            = "IDLE";
            SETUP:  cut_state_text            = "SETUP";
            ACTIVE: cut_state_text            = "ACTIVE";
        endcase
    end
`endif
```

When you define a signal of type SpinalEnum in SpinalHDL, the generated Verilog will automatically include this kind of signal
to ASCII decoder for you!

Like almost all other waveform viewers, GTKWave supports displaying a random bit vector in ASCII format.



