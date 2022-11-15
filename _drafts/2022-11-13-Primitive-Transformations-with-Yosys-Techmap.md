---
layout: post
title: Logic Primitive Transformations with Yosys Techmap
date:  2022-11-13 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

If you're reading this you probably already know that [Yosys](https://github.com/YosysHQ/yosys)
is an open source logic synthesis tool. You may also know that it's much more than that: in
my [earlier blog post about CXXRTL](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html)
I call it the *swiss army knife of digital logic manipulation*. 

In most cases, using Yosys
means running pre-made scripts with commands: when I'm synthesizing RTL for an FPGA of the 
Lattice iCE40 family, the `synth_ice40` command is usually sufficient to convert my RTL
into a netlist that can be sent straight to [nextpnr](https://github.com/YosysHQ/nextpnr)
for place, route, and bitstream creation.

But sometimes you want to perform very particular operations that aren't part of a standard
sequence. My current version of Yosys has 232 commands, and many of these commands have an
impressive list of additional options. 

In this blog post, I'll talk about `techmap`, a particularly powerful command that allows
one to transform an instance of a given type to one or more different ones. 

# Mapping a multiplication to an FPGA DSP Cell

A good example of a `techmap` operation is one where a generic multipication
is converted into a DSP block of an FPGA. For those who are unfamiliar with the technology,
FPGAs usually have only a few core logic primitives: lookup-table cells (LUTs) are used to construct
any kind of random logic circuit, RAMs cells for, well, RAMs, and DSPs, larger cells that contain one
or more hardware multipliers, often in combination with an accumulator.

Let's look at this Verilog module that multiplies two 10-bit x 10-bit values into a 20-bit result:

```verilog
module top(input [9:0] op0, input [9:0] op1, output [19:0] result);
    assign result = op0 * op1;
endmodule
```

When reading in the Verilog file, Yosys translates it into RTLIL (RTL Internal Language), 
the internal representation of the design. The multiplication operation becomes a `$mul` primitive:

```
module \top
  wire width 10 input 1 \op0
  wire width 10 input 2 \op1
  wire width 20 output 3 \result
  cell $mul $mul$mul.v:3$1
    parameter \A_SIGNED 0
    parameter \A_WIDTH 10
    parameter \B_SIGNED 0
    parameter \B_WIDTH 10
    parameter \Y_WIDTH 20
    connect \A \op0
    connect \B \op1
    connect \Y \result
  end
```

Yosys has the super useful `show` command that renders an RTLIL representation as a graph:

![top module as a graph with $mul instance](/assets/yosys_techmap/mul_rtlil.png)

This primitive must be converted into cell primitives of the target technology. Most FPGAs from the
iCE40 family have handful of DSPs. When you synthesize this module to the iCE40 technology with
`synth_ice40 -dsp`, you'll see that the `$mul` primitive has been converted to an 
`SB_MAC16` cell which is the DSP primitive of the iCE40 family.

![SB_MAC16 internal block diagram](/assets/yosys_techmap/SB_MAC16_block_diagram.png)

the `SB_MAC16` DSP has a ton of data path and configuration signals. The multiplier inputs can be 
up to 16-bit wide and the output can be 32-bits. It's up to a `techmap` step to assign all the right 
value to the configuration signals, and to correctly tie down unused input data bits or ignore excess 
output bits so that it performs the desired 10-bit x 10-bit multiplication.

After cleaning up some irrelevant cruft, the post-synthesis RTLIL looks like this:

```
module \top
  wire width 10 input 1 \op0
  wire width 10 input 2 \op1
  wire width 20 output 3 \result
  wire \result_SB_MAC16_O_ACCUMCO
  wire \result_SB_MAC16_O_CO
  wire width 12 \result_SB_MAC16_O_O
  wire \result_SB_MAC16_O_SIGNEXTOUT
  cell \SB_MAC16 \result_SB_MAC16_O
    parameter \A_REG 1'0
    parameter \A_SIGNED 0
    parameter \BOTADDSUB_CARRYSELECT 2'00
    parameter \BOTADDSUB_LOWERINPUT 2'10
    parameter \BOTADDSUB_UPPERINPUT 1'1
    parameter \BOTOUTPUT_SELECT 2'11
    parameter \BOT_8x8_MULT_REG 1'0
    parameter \B_REG 1'0
    parameter \B_SIGNED 0
    parameter \C_REG 1'0
    parameter \D_REG 1'0
    parameter \MODE_8x8 1'0
    parameter \NEG_TRIGGER 1'0
    parameter \PIPELINE_16x16_MULT_REG1 1'0
    parameter \PIPELINE_16x16_MULT_REG2 1'0
    parameter \TOPADDSUB_CARRYSELECT 2'11
    parameter \TOPADDSUB_LOWERINPUT 2'10
    parameter \TOPADDSUB_UPPERINPUT 1'1
    parameter \TOPOUTPUT_SELECT 2'11
    parameter \TOP_8x8_MULT_REG 1'0
    connect \A { 6'000000 \op0 }
    connect \ACCUMCI 1'x
    connect \ACCUMCO \result_SB_MAC16_O_ACCUMCO
    connect \ADDSUBBOT 1'0
    connect \ADDSUBTOP 1'0
    connect \AHOLD 1'0
    connect \B { 6'000000 \op1 }
    connect \BHOLD 1'0
    connect \C 16'0000000000000000
    connect \CE 1'0
    connect \CHOLD 1'0
    connect \CI 1'x
    connect \CLK 1'0
    connect \CO \result_SB_MAC16_O_CO
    connect \D 16'0000000000000000
    connect \DHOLD 1'0
    connect \IRSTBOT 1'0
    connect \IRSTTOP 1'0
    connect \O { \result_SB_MAC16_O_O \result }
    connect \OHOLDBOT 1'0
    connect \OHOLDTOP 1'0
    connect \OLOADBOT 1'0
    connect \OLOADTOP 1'0
    connect \ORSTBOT 1'0
    connect \ORSTTOP 1'0
    connect \SIGNEXTIN 1'x
    connect \SIGNEXTOUT \result_SB_MAC16_O_SIGNEXTOUT
  end
end
```

And here's the graphical representation. (*Click to enlarge*)

[![top module as a graph after synthesis](/assets/yosys_techmap/mul_ice40.png)](/assets/yosys_techmap/mul_ice40.png)

All Yosys commands are written in C++, but in the case of `techmap`, the specific mapping
operations are described in... Verilog! It's a very neat system that makes it possible for
anyone create their custom mapping operations without the need to touch a line of C++.

Let's see exactly how that works for our example, and look at the source code of the `synth_ice40` command.

Yosys places all the technology-specific operations under the [`techlibs`](https://github.com/YosysHQ/yosys/tree/master/techlibs) 
directory. The code for `synth_ice40` can be found in 
[`techlibs/ice40/synth_ice40.cc`](https://github.com/YosysHQ/yosys/blob/master/techlibs/ice40/synth_ice40.cc).
`synth_ice40` doesn't really have any smarts by itself, it's a macro command, a series of lower level
Yosys commands strung together into a recipe. The code is really easy to follow.

When you run `help synth_ice40` in Yosys, you'll see the following:

```
    -dsp
        use iCE40 UltraPlus DSP cells for large arithmetic
```

It's easy to see [which steps are activated in the source code](https://github.com/YosysHQ/yosys/blob/853f4bb3c695d9f5183ef5064ec4cf9cdd8b5300/techlibs/ice40/synth_ice40.cc#L329-L341) when DSP mapping is enabled:

```c
run("memory_dff" + no_rw_check_opt); // ice40_dsp will merge registers, reserve memory port registers first
run("wreduce t:$mul");
run("techmap -map +/mul2dsp.v -map +/ice40/dsp_map.v -D DSP_A_MAXWIDTH=16 -D DSP_B_MAXWIDTH=16 "
    "-D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2 -D DSP_Y_MINWIDTH=11 "
    "-D DSP_NAME=$__MUL16X16", "(if -dsp)");
run("select a:mul2dsp", "              (if -dsp)");
run("setattr -unset mul2dsp", "        (if -dsp)");
run("opt_expr -fine", "                (if -dsp)");
run("wreduce", "                       (if -dsp)");
run("select -clear", "                 (if -dsp)");
run("ice40_dsp", "                     (if -dsp)");
run("chtype -set $mul t:$__soft_mul", "(if -dsp)");
```

There's quite a bit going on here, but the most interesting command is this one:

```
    techmap -map +/mul2dsp.v -map +/ice40/dsp_map.v 
        -D DSP_A_MAXWIDTH=16 -D DSP_B_MAXWIDTH=16
        -D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2 -D DSP_Y_MINWIDTH=11
        -D DSP_NAME=$__MUL16X16
```

What we see here is that `techmap` is doing the `$mul` to `SB_MAC16` conversion in two steps:

1. convert `$mul` to a generic, technology independent DSP multiplier cell.
2. convert the generic multiplier DSP cell to an iCE40 DSP cell.

**Step 1: map2dsp.v**

Step 1 is done by [`map2dsp.v`](https://github.com/YosysHQ/yosys/blob/master/techlibs/common/mul2dsp.v).
The code is a bit convoluted, but it has the answer as to why this intermediate step was needed:

* it deals with cases where a single `$mul` operation requires more than one DSP.

    For example, a 32-bit x 32-bit to 64-bit multiplication is split into 4 
    16x16=32 multiplications and some additions.

* it doesn't do the conversion when the inputs of the multiplication are too small 

    This avoids wasting precious DSP resources on something that can be implemented with core logic.
  
The `-D ...` arguments of the `techmap` command specify Verilog defines that are passed to the techmap
file. It's used to parameterize the conversion process:

* `-D DSP_A_MAXWIDTH=16 -D DSP_B_MAXWIDTH=16` informs `mul2dsp` that the maximum input size of
  the DSP is 16 bits.
* `-D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2 -D DSP_Y_MINWIDTH=11` provides the minimum requirements
  that must be satisfied to do the conversion.
* `-D DSP_NAME=$__MUL16X16` provides the name of the generic multiplier cells that should be created.

We can run that first step by ourselves and check the result:

```
read_verilog mul.v
clean -purge
techmap -map +/mul2dsp.v -D DSP_A_MAXWIDTH=16 -D DSP_B_MAXWIDTH=16 -D DSP_A_MINWIDTH=2 -D DSP_B_MINWIDTH=2 -D DSP_Y_MINWIDTH=11 -D DSP_NAME=$__MUL16X16
clean -purge
show -width -signed -format png -prefix mul_mul2dsp
```

![top module after mul2dsp phase](/assets/yosys_techmap/mul_mul2dsp.png)

In case you were wondering, here's what this first step looks like for a 20-bit x 20-bit to 40-bit multiplier:

[![top module for $mul 20x20=40 after mul2dsp phase](/assets/yosys_techmap/large_mul_techmap.png)](/assets/yosys_techmap/large_mul_techmap.png)

Yosys can often creates very long internal labels which stretches the graphical representation, so
I zoomed the image to the part that counts. The 3 red rectangles are `__MUL16X16` cells that will be converted
to iCE40 DSPs. The blue rectangle is a `$__soft_mul` cell that will be converted into random logic
at a large stage, and the 3 green rectangles are `$add` cells to bring the results of the different multipliers
together.

**Step 2: ice40/dsp_map.v**

Step 2 of the `techmap` process, [`ice40/dsp_map.v`](https://github.com/YosysHQ/yosys/blob/master/techlibs/ice40/dsp_map.v) 
is trivial: it converts the generic `__MUL16X16` multiplier cell into an `SB_MAC16` cell, wires up the data path inputs and output,
and straps all the other configuration inputs so that the cell is configured as a straight 
multiplier.

```verilog
module \$__MUL16X16 (input [15:0] A, input [15:0] B, output [31:0] Y);
	parameter A_SIGNED = 0;
	parameter B_SIGNED = 0;
	parameter A_WIDTH = 0;
	parameter B_WIDTH = 0;
	parameter Y_WIDTH = 0;

	SB_MAC16 #(
		.NEG_TRIGGER(1'b0),
		.C_REG(1'b0),
		.A_REG(1'b0),
		.B_REG(1'b0),
		.D_REG(1'b0),
		.TOP_8x8_MULT_REG(1'b0),
		.BOT_8x8_MULT_REG(1'b0),
		.PIPELINE_16x16_MULT_REG1(1'b0),
		.PIPELINE_16x16_MULT_REG2(1'b0),
		.TOPOUTPUT_SELECT(2'b11),
		.TOPADDSUB_LOWERINPUT(2'b0),
		.TOPADDSUB_UPPERINPUT(1'b0),
		.TOPADDSUB_CARRYSELECT(2'b0),
		.BOTOUTPUT_SELECT(2'b11),
		.BOTADDSUB_LOWERINPUT(2'b0),
		.BOTADDSUB_UPPERINPUT(1'b0),
		.BOTADDSUB_CARRYSELECT(2'b0),
		.MODE_8x8(1'b0),
		.A_SIGNED(A_SIGNED),
		.B_SIGNED(B_SIGNED)
	) _TECHMAP_REPLACE_ (
		.A(A),
		.B(B),
		.O(Y),
	);
endmodule
```

# A Horribly Contrived Example Problem

Have a look at the following Verilog example code:

```verilog
module top_unsigned(input [5:0] op0, input [6:0] op1, output [63:0] sum);
    assign sum = op0 + op1;
endmodule
```

The graphical representation is as expected:

![top_unsigned original version](/assets/yosys_techmap/add_orig.png)

I sometimes use [CXXRTL](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html) to simulate my designs.
When I run `write_cxxrtl`, the generated file contains the following:

```c
bool p_top__unsigned::eval() {
	bool converged = true;
	p_sum0 = add_uu<64>(p_op0, p_op1);
	return converged;
}
```

This is exactly as expected, and there's nothing wrong with it. But one thing that bothers me is that CXXRTL 
uses 32-bit integer values ("chunks") for all its operations. In the code above, there's a 64-bit addition, and
CXXRTL implements those by 
[splitting things up into multiple 32-bit additions](https://github.com/YosysHQ/yosys/blob/853f4bb3c695d9f5183ef5064ec4cf9cdd8b5300/backends/cxxrtl/cxxrtl.h#L521-L532):

```c
   template<bool Invert, bool CarryIn>
   std::pair<value<Bits>, bool /*CarryOut*/> alu(const value<Bits> &other) const {
      value<Bits> result;
      bool carry = CarryIn;
      for (size_t n = 0; n < result.chunks; n++) {
         result.data[n] = data[n] + (Invert ? ~other.data[n] : other.data[n]) + carry;
         if (result.chunks - 1 == n)
            result.data[result.chunks - 1] &= result.msb_mask;
         carry = (result.data[n] <  data[n]) ||
                 (result.data[n] == data[n] && carry);
      }
      return {result, carry};
   }
```

It's a hand-crafted carry-ripple adder. Now, don't worry, things are really not as bad as it seems,
because all the variables that are used for the the `if` conditionals and the `for` loop are constants. Any
good C++ compiler will optimize the addition above into only a few assembler instructions.

If you know your binary adder basics, you see that the addition of a 7-bit and a 6 bit operand will result
at most in an 8-bit result. All higher bits will always be 0. It's overkill to have a 64-bit adder.

Yosys already has the `wreduce` command that reduces logic operations to just the number of bits that are
really needed.

We can see this when we run the following commands:

```
read_verilog add_orig.v
hierarchy -top top_unsigned
wreduce
clean -purge
```

![top_unsigned after wreduce](/assets/yosys_techmap/add_wreduce.png)

And the here's the relevant CXXRTL generated code:

```c
bool p_top__unsigned::eval() {
    bool converged = true;
    p_sum0.slice<7,0>() = add_uu<8>(p_op0, p_op1);
    p_sum0.slice<63,8>() = value<56>{0u,0u};
    return converged;
}
```

That looks better, but is that really true? The addition now returns an 8-bit value, but since
the smallest chunk is 32-bits, the `slice<7,0>` command now requires a read-modify-write.

What I really want is this:

```c
bool p_top__unsigned::eval() {
    bool converged = true;
    p_sum0.slice<31,0>() = add_uu<32>(p_op0, p_op1);    <<<<< 32 bits
    p_sum0.slice<63,32>() = value<32>{0u,0u};		<<<<< 32 bits
    return converged;
}
```

Unfortunately, Yosys doesn't have a command that does this for me, and I really don't
want to modify the [C++ code of the `wreduce` command](https://github.com/YosysHQ/yosys/blob/master/passes/opt/wreduce.cc)
to make it so.

# A Custom Techmap Module to the Rescue!

If you start Yosys, running `help techmap` will give you an exhaustive list of all the feature that
you might ever need. Instead of repeating everything in there, let's create an `add_reduce` techmap
file to solve the problem of the previous section.

