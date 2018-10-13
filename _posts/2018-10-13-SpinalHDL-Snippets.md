---
layout: post
title:  "SpinalHDL Snippets"
date:   2018-10-13 22:00:00 -0700
categories: RTL
---

# Split Testbench into Functional Sections

* [Compile the DUT](https://github.com/SpinalHDL/SpinalHDL/blob/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest/SpinalSimPerfTester.scala#L30)

* [Create a test on the DUT](https://github.com/SpinalHDL/SpinalHDL/blob/a172df4d6e95ae5f21bbeb1989c7bcd1498b2675/tester/src/test/scala/spinal/tester/scalatest/SpinalSimPerfTester.scala#L37)

* Kick off one particular test: `sbt "test-only *.MyScalaUnitTest"`

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



