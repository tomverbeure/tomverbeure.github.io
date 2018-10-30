---
layout: post
title:  "Multipliers"
date:   2018-08-11 22:00:00 -0700
categories: RTL
---

# CPU Multipliers

I've been working on my own RISC-V CPU to learn SpinalHDL and to get some hands on experience with
formal verification.

While doing that, I started thinking about the 32x32 bit multiplier that's part of some
of today's RISC-V cores.

There are different ways to go about this:

* No HW Multiplier

    If you're really area constraints, you simply don't implement it at all, and you let the C compiler
    call a multiplier library function.

* Iterative Multiplier

    If you want things to be a little faster, you implement an iterative multiplier which iterates
    through all the bits of one of the operands and conditionally adds a shifted version of the other
    operand. The picorv32 CPU code for that is [here](https://github.com/cliffordwolf/picorv32/blob/23d7bbdc8bb3ff97b4d3ccf9cc2eb9ee291039de/picorv32.v#L2127-L2246).
    And [here](https://github.com/SpinalHDL/VexRiscv/blob/25c0a0ff6fc4980e8ec8b5148fe213c24a245a56/src/main/scala/vexriscv/plugin/MulDivIterativePlugin.scala#L70-L85)'s 
    the equivalent VexRiscV code.

    In most cases, this kind of multiplier will do one bit at a time, but that's not really necessary. In
    the picorv32 code, you can specify this by setting the desired [STEP_AT_ONCE](https://github.com/cliffordwolf/picorv32/blob/23d7bbdc8bb3ff97b4d3ccf9cc2eb9ee291039de/picorv32.v#L2128)
    parameter, or the [mulUnrollFactor](https://github.com/SpinalHDL/VexRiscv/blob/25c0a0ff6fc4980e8ec8b5148fe213c24a245a56/src/main/scala/vexriscv/plugin/MulDivIterativePlugin.scala#L7)
    of the VexRiscV.

* Parallel Multiplier

    If you really want performance, you uses a parallel multiplier which takes in that 2 operands completely and spits out a result. The number of cycles
    between input and output is often more than 1, but on a reasonably efficient and pipelined CPU (and in the absense of pipeline stalls), this can result
    in 1 result per clock cycle.

    The picrov32 CPU has the [`fast_mul`](https://github.com/cliffordwolf/picorv32/blob/23d7bbdc8bb3ff97b4d3ccf9cc2eb9ee291039de/picorv32.v#L2248-L2343) module and the
    VexRiscV has the [`MulPlugin`](https://github.com/SpinalHDL/VexRiscv/blob/25c0a0ff6fc4980e8ec8b5148fe213c24a245a56/src/main/scala/vexriscv/plugin/MulPlugin.scala#L6-L104) for
    that.

When you're using a PicoRV32 or VexRiscv RISC-V CPU core, you can freely select which version to use.

I was mostly interested in the third option.

# RISC-V Multiply Instructions

The RISC-V 32-bit instruction set has 4 multiply instructions:

* `MUL rd, rs1, rs2`

    This multiplies operands *rs1* and *rs2* and stores the lower 32 bits of the result in *rd*.

    Note that there are no signed/unsigned variants: it doesn't matter whether rs1 and rs1 are signed or unsigned 
    because the result is the same.  You can quickly see this on a 2-bit x 2-bit example:

    ```
    Unsigned: 2'b11 x 2'b11 =  3 x  3 =  9 = 4'b1001 -> 2'b01
    Signed:   2'b11 x 2'b11 = -1 x -1 =  1 = 4'b0001 -> 2'b01
    ```

    ```
    Unsigned: 2'b01 x 2'b11 =  1 x  3 =  3 = 4'b0011 -> 2'b11
    Signed:   2'b01 x 2'b11 =  1 x -1 = -1 = 4'b1111 -> 2'b11
    ```

    When the result is truncated to the same number of bits as the size of the operands, the outcome is identical.

* `MULH rd, rs1, rs2`

    multiplies 2 *signed* operands rs1 and rs2 and stores the upper 32 bits in rd.

* `MULHU rd, rs1, rs2`

    multiplies 2 *unsigned* operands rs1 and rs2 and stores the upper 32 bits in rd.

* `MULHSU rd, rs1, rs2`

    multiplies *signed* operand rs1 and *unsigned* r operands2 and stores the upper 32 bits in rd.

For RISC-V, if you want to get the 64-bit result of a 32x32 bit multiplication, you need to use 2 instructions: 
MUL, and one of the MULH variants.

RTL Implementation on the PicoRV32
------------------------------

On the PicoRV32, when you strip away all the extraneous book keeping, the key part of [the implementation](https://github.com/cliffordwolf/picorv32/blob/23d7bbdc8bb3ff97b4d3ccf9cc2eb9ee291039de/picorv32.v#L2248-L2343)
is straightforward:

```
    rd <= $signed(rs1) * $signed(rs2);
    assign pcpi_rd = shift_out ? rd >> 32 : rd;
```

Of note is that `rs1` and `rs2` are 33-bit, not 32-bit, sized. As shown above in my 2x2 bit example, signed and unsigned operands 
require different multiplier behavior if you're interested in the full result. One can avoid having different 3 different multipliers (one for each
MULH variant) by expanding the operands with 1 bit additional MSB. This MSB is set to 0 for unsigned operands
or a copy of the sign bit for signed operands.

The code above requires a 33-bit x 33-bit to 64-bit multiplier, with a multiplexer at the end to select the upper or lower
32 bits.

RTL Implementation on the VexRiscv
----------------------------------

The relevant code can be found in [MulPlugin.scala](https://github.com/SpinalHDL/VexRiscv/blob/25c0a0ff6fc4980e8ec8b5148fe213c24a245a56/src/main/scala/vexriscv/plugin/MulPlugin.scala#L6-L104)

```
    execute plug new Area {
      ...
      val aULow = a(15 downto 0).asUInt
      val bULow = b(15 downto 0).asUInt
      val aSLow = (False ## a(15 downto 0)).asSInt
      val bSLow = (False ## b(15 downto 0)).asSInt
      val aHigh = (((aSigned && a.msb) ## a(31 downto 16))).asSInt
      val bHigh = (((bSigned && b.msb) ## b(31 downto 16))).asSInt
      insert(MUL_LL) := aULow * bULow
      insert(MUL_LH) := aSLow * bHigh
      insert(MUL_HL) := aHigh * bSLow
      insert(MUL_HH) := aHigh * bHigh
    }

    memory plug new Area {
      insert(MUL_LOW) := S(0, MUL_HL.dataType.getWidth + 16 + 2 bit) + (False ## input(MUL_LL)).asSInt + (input(MUL_LH) << 16) + (input(MUL_HL) << 16)
    }


    writeBack plug new Area {
      val result = input(MUL_LOW) + (input(MUL_HH) << 32)

      switch(input(INSTRUCTION)(13 downto 12)){
        is(B"00"){
          output(REGFILE_WRITE_DATA) := input(MUL_LOW)(31 downto 0).asBits
        }
        is(B"01",B"10",B"11"){
          output(REGFILE_WRITE_DATA) := result(63 downto 32).asBits
        }
      }
    }
```

This looks more convoluted, because the multiplication has been been split up into 4 smaller multipliers. If we ignore
the signed operations for a moment, we can split up a 32x32=64 operation into 4 16x16=32 operations:

```
    a[31:0] = { a1[15:0], a0[15:0] }
    b[31:0] = { b1[15:0], b0[15:0] }

    result = a * b = (a1<<16 + a0)(b1<<16 + b0) = a0*a0 + (a1*b0)<<16 + (a0*b1)<<16 + (a1*b1)<<32
                                                = a0*a0 + (a1*b0 + a0*b1)<<16       + (a1*b1)<<32
```

That's what's happening above.

The motivation of doing it this way is to spread the multiplication over multiple pipeline stages: the 4 16x16 multiplies happen
in the `execute` stage, the addition of the 3 multiplications that contribute to the lower 32-bits happen in the `memory` stage.
And the final addition (into the `result` signal) for the upper 32-bits happens in the `writeBack` stage.

Similar to the PicoRV32, 3 of the 4 16x16 multiplications are actually 17x17 bits to support both signed and unsigned operations. Most FPGAs
from Xilinx and Intel/Altera have hard 18x18 multiplier macros in their DSP blocks, so it makes no difference to use 16x16 or 17x17
operations: they're all mapped onto the same 18x18 hardware block anyway.

Multiplier Mapping onto FPGA
----------------------------

On relatively modern Altera FPGAs such as the
[Cyclone V series](https://www.intel.com/content/dam/altera-www/global/en_US/pdfs/literature/hb/cyclone-v/cv_5v2.pdf),
there are 2 18x18 multipliers per DSP. In the best possible case, we'd only need 2 DSPs.

If we assume that Altera knows best how to best map larger multipliers onto smaller ones, then we can use the PicoRV32 mapping
as an example on how to do things right.

After synthesis, what we see is that Quartus maps the logic to 3 DSPs instead of 2.

* One DSP is used in (18x18 + 18x18) mode, where the output of two multipliers are added to eachother. This is the `(a1*b0 + a0*b1)` term that is implemented 
  in discrete form on the VexRiscV.
* Two DSPs are used in 18x18-only mode.

For the VexRiscv, the 4 multipliers are mapped to 4 DSPs.

Optimizing for MUL but not MULH*
--------------------------------

In the vast majority of use cases, your C code will consist of int * int operations, where 2 32-bit integers are multiplied together and stores in a 32-bit integer as well. 
In other words: you'll be using the MUL instruction.

If DSP resources are tight but you still want a fast multiplication for the most common operation, it makes sense then to optimize for that, and incur a performance
penalty for MULH.

With `a[31:0] = { a1[15:0],a0[15:0] } = a1a0` and `b[31:0] = { b1[15:0],b0[15:0] } = b1b0`, the full multiplication looks like this sum:

```
a*b=
        a0b0
      a1b0
      a0b1
    a1b1
   +========

   (a1b1)<<32 + (a1b0+a0b1)<<16 + a0b0
```
Note that each term `axbx` is 32 bits wide in the notation above, so you have 16 overlapping bits in these two sums: `(a1b0+a0b1)<<16 + a0b0` and `(a1b1)<<32 + (a1b0+a0b1)<<16`.

If we only care about the bottom 32 bits of the result (MUL), it looks like this:

```
        |a0b0
      a1|b0
      a0|b1
    a1b1|
   +========
```

At the very minimum, we need 3 multiplications:

```
a0b0: 16x16 = 32 bits
a1b0: 16x16 = truncated to lower 16 bits
a0b1: 16x16 = truncated to lower 16 bits
```

And then we sum these 3 terms for the final 32 bit result.

So that's the smallest fast implementation: 1 16x16=32 multiplier and 2 16x16=16 multipliers.

For an FPGA, there is no difference between a 16x16=16 or 16x16=32 multiplier so there is no savings on the DSP side. However, the
final adder that sums the 3 terms together will only need to 32 bits. That's very likely to be result in area and timing savings.

Even if we only optimize for MUL, we may still want to support MULH in hardware. If an acceptable trade-off is for this MULH to
take 2 steps instead of 1, then it makes sense to first calculate the MUL with 3 16x16=32 bits operations in the first step, and calculate
a 50-bit sum.

Then, in a second step, take the upper 18 bits \[49:32\] of this sum and add them to the 32-bit result of a1*b1. 

We can reuse one of the 16x16 multipliers that were used in the first step, so the number of 16x16 multipliers is still 3 instead of the original 4.

For FPGAs that have hard 16x16 (or slightly larger) multipliers, that's about the best we can do if we need a single step MUL.

But when using ASICs or FPGAs that don't have hard multipliers (e.g. the Lattice iCE40 series), we can do better.

Reducing Logic Even More
------------------------

Let's imagine that we have 8x8 instead of 16x16 multipliers, and that

`a[31:0] = { a3[7:0],a2[7:0],a1[7:0],a0[7:0] } = a3a2a1a0` and `b[31:0] = { b3[7:0],b2[7:0],b1[7:0],b0[7:0] } = b3b2b1b0`

A full 32x32 multiplication now looks like this:

```
a*b=
                a0b0
              a1b0
            a2b0
          a3b0
              a0b1
            a1b1
          a2b1
        a3b1
            a0b2
          a1b2
        a2b2
      a3b2
          a0b3
        a1b3
      a2b3
    a3b3
```

Rearranged:
```
            |    a0b0
            |  a1b0
            |  a0b1
            |a2b0
            |a1b1
            |a0b2
          a3|b0
          a2|b1
          a1|b2
          a0|b3
            |
        a3b1|
        a2b2|
        a1b3|
      a3b2  |
      a2b3  |
    a3b3    |
```
For a 32x32=32 result, we once again only care about terms with bits to the right of the vertical line, which means
that the factors below the break are entirely not needed.

Using 16x16 multiplications, we could reduce the number of multiplications from 4 to 3 (-25%). When using 8x8
multiplications, we can reduce them from 16 down to 10 (-37.5%).

And if we still want to calculate MULH in 2 steps, then the result of the first step is 43 bits of which we can
discard the lower 32 bits and roll over 11 bits to the second step.

We can arrange it still different:
```
            |    a0b0
            |  a1b0
            |  a0b1
            |a1b1       < swapped
            |a2b0       <
            |a0b2
          a3|b0
          a2|b1
          a1|b2
          a0|b3
            |
        a3b1|
        a2b2|
        a1b3|
      a3b2  |
      a2b3  |
    a3b3    |
```

The first 4 terms are a 16x16=32 multiplier, so we can implement this as
1 16x16=32bit multiplier and 6 8x8=16bit multipliers. If these kind of multipliers
are available as a hard macro, this could be a solution.

Getting Ridiculous
------------------

If we can go from 16x16 to 8x8 multipliers, then we can also go even smaller, like 4x4=8, right? 

Yes, that's possible. But it's not very useful. For one, there are no FPGAs that have these kind of small hard multipliers, so the exercise is 
academic. And second, when you start going this small, the timing path will long have moved from the multiplier to the adders that sum all these
tiny terms together.

But for completeness, there's how it works out:

```
a[31:0]=a7a6a5a4a3a2a1a0
b[31:0]=b7b6b5b4b3b2b1b0

a*b =
                    |            a0b0
                    |          a1b0
                    |        a2b0
                    |      a3b0
                    |    a4b0
                    |  a5b0
                    |a6b0
                  a7|b0
                    |          a0b1
                    |        a1b1
                    |      a2b1
                    |    a3b1
                    |  a4b1
                    |a5b1
                  a6|b1
                    |        a0b2
                    |      a1b2
                    |    a2b2
                    |  a3b2
                    |a4b2
                  a5|b2
                    |      a0b3
                    |    a1b3
                    |  a2b3
                    |a3b3
                  a4|b3
                    |    a0b4
                    |  a1b4
                    |a2b4
                  a3|b4
                    |  a0b5
                    |a1b5
                  a2|b5
                    |a0b6
                  a1|b6
                  a0|b7

                a6b2|
              a7b2  |
                a7b1|
                a5b3|
              a6b3  |
            a7b3    |
                a4b4|
              a5b4  |
            a6b4    |
          a7b4      |
                a3b5|
              a4b5  |
            a5b5    |
          a6b5      |
        a7b5        |
                a2b6|
              a3b6  |
            a4b6    |
          a5b6      |
        a6b6        |
      a7b6          |
                a1b7|
              a2b7  |
            a3b7    |
          a4b7      |
        a5b7        |
      a6b7          |
    a7b7            |
```

The terms are already separated into those that contribute to the lower 32 bits and those that do not.

36 out of 64 4x4=8 multipliers matter, and 28 do not. A reduction of 43.75% compared to the single
step 32x32=64 bit multiplier.

As before, we could reduce some of those 4x4 terms into one 16x16=32 multiplier, and a number of 8x8=16 bit
multipliers.

It should be obvious by now that smaller multiplier building blocks will result in a lower amount of logic.
Taken to its logical conclusion, you can do this with 1x1 multipliers: the
number of multipliers decreases towards 50% of the ones needed for a full 64 bit result, however the number of
adders will go up.

If you'd want to code things up like this in RTL, using small multipliers building blocks is definitely not
the best approach: there are much better ways to build fast multipliers. Looks up "Booth encoding" and
"Wallace Tree." Those are outside the scope of this post, and mostly irrelevant for FPGAs, since they require
a lot of wiring and inefficient to map onto FPGA logic.

Expanding a Floating Points Multiplier to a 32-bit multiplier
-------------------------------------------------------------

Finally, let's have a quick look at floating point multipliers. Single precision FP32 has a one sign bit,
8 exponent bits, and 23 fraction bits. The 23 fraction bits have an implied MSB that is set to 1, so the
significand is really 24 bits. 

To multiply 2 FP32 numbers, you need a 24x24=24 multiplier.

If we look back at a 32x32=32 bit multiplier that is composed of 8x8 bit multipliers, and we don't care
about what's needed to get a 64-bit result, we had the following:

```
            |    a0b0
            |  a1b0
            |  a0b1
            |a2b0
            |a1b1
            |a0b2
          a3|b0
          a2|b1
          a1|b2
          a0|b3
```

If the input is only 24 bits instead of 32-bit, we can ignore the terms with a '3' in it:

```
            |    a0b0
            |  a1b0
            |  a0b1
            |a2b0
            |a1b1
            |a0b2
          a2|b1
          a1|b2

          a0|b3
          a3|b0
```

The most important take-away here is the following: if you already support FP32, the extra cost to support INT32, is just 2 additional 8x8=8 multipliers.

So if your integer and floating point operations are use the same building blocks of the ALU, the extra cost for a full 32x32 bit multiplier is not
super high.



