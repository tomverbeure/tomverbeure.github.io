---
layout: post
title:  "SpinalHDL Snippets"
date:   2018-10-14 00:00:00 -1000
categories: RTL
---

* TOC
{:toc}


# Introduction

Since I've started using SpinalHDL for my hobby projects, I've been running into many issues. A few of those where minor bugs of SpinalHDL itself,
but most of them are because Scala is a completely new language for me.

Initially, I've been using SpinalHDL as a pure RTL generator, a replacement of Verilog that requires less typing. In that case, you can get by
with a bare minimum of commands and Scala. But SpinalHDL can do much more: complex generators, testbench integration etc. And when you start
to get into that, lack of knowledge about Scala and the Scala development environment becomes a limitation quickly.

This blog post serves as a collection of development road blocks and methods on how to navitage past these road blocks.

It's a living document to which I'll keep adding more stuff as I get better at SpinalHDL.

# Split Testbench into Functional Sections

In general, the best practise seems to be to create a separate class per functional block. A good example of different tests is
[here](https://github.com/SpinalHDL/SpinalHDL/tree/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest).

You can either compile the DUT as part of a single test, or you can compile the dut once, and then use the compiled version for
all the tests. That's definitely more efficient.

Here's an example of doing a single DUT compile, and then having multiple tests using it:

* [Compile the DUT](https://github.com/SpinalHDL/SpinalHDL/blob/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest/SpinalSimPerfTester.scala#L30)

* [Create a test on the DUT](https://github.com/SpinalHDL/SpinalHDL/blob/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest/SpinalSimPerfTester.scala#L37)

To kick of all the tests of a Tester class, do the following: 

```bash
sbt "test-only <scala path to tester class>"
```

Like this:

```bash
sbt "test-only math.FpxxTester"
```

To run only 1 of the tests:

```bash
sbt "test-only math.FpxxTester -- -z FpxxAdd"
```

Note: running 1 test *only* works if you compile the DUT as part of the test itself. If you have a separate `compile` test, then it will not work.

# Optional Pipeline Stage

When `pipeline` is True, then a pipeline stage (with optional enable input) is instantiated, and the input signal is flopped. When False, it's a
straight wire.

[Definition](https://github.com/tomverbeure/math/blob/96c222e541adc4670dfe1929005a5ea14e2a7123/src/main/scala/math/Misc.scala#L95-L100):
```scala
object OptPipe {
    def apply[T <: Data](that : T, ena: Bool, pipeline : Boolean) : T = if (pipeline) RegNextWhen(that, ena) else that
    def apply[T <: Data](that : T, pipeline : Boolean) : T = apply(that, True, pipeline)
}
```

[Usage](https://github.com/tomverbeure/math/blob/96c222e541adc4670dfe1929005a5ea14e2a7123/src/main/scala/math/FpxxDiv.scala#L105-L112):
```scala
    // Only insert pipeline stage when configuration parameter asks for it
    val p4_pipe_ena     = pipeStages >= 2

    // When using an enable, it needs to ripple through the pipeline as well...
    val p4_vld          = OptPipe(p3_vld, p4_pipe_ena)

    val sign_p4         = OptPipe(sign_p3,       p3_vld, p4_pipe_ena)
    val x_mul_yhyl_p4   = OptPipe(x_mul_yhyl_p3, p3_vld, p4_pipe_ena)
    val recip_yh2_p4    = OptPipe(recip_yh2_p3,  p3_vld, p4_pipe_ena)
    val exp_full_p4     = OptPipe(exp_full_p3,   p3_vld, p4_pipe_ena)
```

# Leading Zeros Calculator

Implements the method of this [StackExchange question](https://electronics.stackexchange.com/questions/196914/verilog-synthesize-high-speed-leading-zero-count)
in a recursive and a generic way that works for any sized vector input:
[full code](https://github.com/tomverbeure/math/blob/96c222e541adc4670dfe1929005a5ea14e2a7123/src/main/scala/math/Misc.scala#L70-L93).


# Initialize a 32-bit wide Mem with the contents of binary file

* First pad the binary file to make it the desired size of the Mem.

    I have this in my Makefile:

```makefile
progmem8k.bin: progmem.bin
        cp $< $@
        dd if=/dev/zero of=$@ bs=1 count=0 seek=8192
```

* Then load it through the `initialContent` parameter when instantiating the Mem:

```scala
        import java.nio.file.{Files, Paths}

        val byteArray = Files.readAllBytes(Paths.get("sw/progmem8k.bin"))
        val cpuRamContent = for(i <- 0 until ramSize/4) yield {
                B( (byteArray(4*i).toLong & 0xff) + ((byteArray(4*i+1).toLong & 0xff)<<8) + ((byteArray(4*i+2).toLong & 0xff)<<16) + ((byteArray(4*i+3).toLong & 0xff)<<24), 32 bits)
        }

        val cpu_ram = Mem(Bits(32 bits), initialContent = cpuRamContent)
```

I have filed a [SpinalHDL GitHub Issue](https://github.com/SpinalHDL/SpinalHDL/issues/160) to provide a better way to do this.

# Using a Local SpinalHDL Version

Often, you only need to make minor changes to your `build.sbt` file to switch to the latest SpinalHDL released version or
to point to a local SpinalHDL version (e.g. to test some kind of patch.)

Here's such [a typical `build.sbt` file update](https://github.com/tomverbeure/panologic-g2/commit/62b029797217e01725214fc3c507e0e1edfbeb27#diff-61725fd45744f1491eb0f018762cb137):

* The Scala version may need to be updated to a later version
* You comment out the released SpinalHDL version and add `lazy val` statements that point to the local SpinalHDL version.

However, often, you need to update a bunch of other files as well:

* `project/build.properties` needs to point to the correct `sbt` release
* `project/plugins.sbt` might need to be updated to the latest plugins as well.

If you don't know what values need to be used for a particular SpinalHDL release, I always look at these files in latest
[VexRiscv](https://github.com/spinalHDL/VexRiscv) release. That one is almost always in sync with the latest SpinalHDL
release.

# VexRiscv

Run DhystoneBench for multiple CPU cores:
```bash
sbt "testOnly vexriscv.DhrystoneBench"
```

# To Delete Absolutely Everything

`sbt` has various places where it stores cached content. Sometimes, when, for example upgrading to a new version
of SpinalHDL, things don't work well.

The best way to proceed, then, is to remove all old Scala traces from your system.

Executed from within your project, this should do it:
```bash
sbt clean
rm -fr ~/.ivy2
rm -fr ~/.sbt
```

# Running Something from the SpinalHDL tree itself

This doesn't work:

```bash
cd projects/SpinalHDL
sbt "runMain  spinal.lib.com.i2c.Apb3I2cCtrl"
```

SpinalHDL is itself a multi-module project. So you need to do:

```bash
cd projects/SpinalHDL
sbt "lib/runMain  spinal.lib.com.i2c.Apb3I2cCtrl"
```
