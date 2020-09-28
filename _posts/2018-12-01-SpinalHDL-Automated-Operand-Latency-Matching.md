---
layout: post
title:  SpinalHDL Automated Operand Latency Matching
date:   2018-12-01 00:00:00 -1000
categories: RTL
---

# SpinalHDL Automated Operand Latency Matching

Imagine you're doing the following calculation:

```
q = a + b + c
```

However, all your math functional blocks only accept 2 operands. No problem, just split it up:

```
p = a + b
q = p + c
```

That's easy to do when you write C or maybe use high-level synthesis language (HLS).

But when you write RTL and when each operation take a number of cycles, you need to be
careful: if your pipeline accepts a new input each clock cycle, you need to make
sure that the operands for all functional blocks are aligned!

For example: if the adder take 2 clock cycles, the result `p` will emerge
after 2 clock cycles *and you need to delay `c` by 2 clock cycles to align it to 'p'* before
you can apply both operands to the adder that calculats 'q'.

My parameterizable precision [fpxx](https://github.com/tomverbeure/math) library has tons 
of flexilibity in terms of pipeline depth. The FpxxAdd block can be configured to take between 
zero and 5 pipeline stages. You select the amount depending on your clock frequency needs. 

The adder is declared like [this](https://github.com/tomverbeure/math/blob/2d9fbf27218d7574083fee5c417021c707ce4d8c/src/main/scala/math/FpxxAdd.scala#L8-L15):

```scala
case class FpxxAddConfig(
    pipeStages      : Int = 1
    ){
}

class FpxxAdd(c: FpxxConfig, addConfig: FpxxAddConfig = null) extends Component {

    def pipeStages      = if (addConfig == null) 1 else addConfig.pipeStages
...
}
```

And [here](https://github.com/tomverbeure/math/blob/2d9fbf27218d7574083fee5c417021c707ce4d8c/src/test/scala/math/FpxxAddTester.scala#L24) is
how to instantiate an adder with 5 pipeline stages:
```scala
    val fp_op = new FpxxAdd(config, FpxxAddConfig(pipeStages = 5))
```

Other blocks have similar levels of configurability.

Larger functional blocks such as 
[ray/sphere intersection](https://github.com/tomverbeure/rt/blob/29070b46fa30c290d7e530f7700b9ea1ef45a3eb/src/main/scala/rt/Sphere.scala#L17-L402)
have tons of different operations that are both cascaded sequentially and working in parallel.

![Sphere Intersection Pipeline]({{ "/assets/rt/RtBRT-Sphere Intersect.svg" | absolute_url }})

Even if the latencies through each core math block were fixed, it'd still be a real pain
to ensure that all operands to all blocks were correctly latency aligned.

Comes to the rescue: the [SpinalHDL LatencyAnalysis](https://spinalhdl.github.io/SpinalDoc/spinal/lib/utils/#special-utilities)
function!

Its function is a simple as it is brilliant: given a set of signals that are connected to each other
through a string of combinatorial and sequential logic, it returns the minimum number of clock
cycles to travel through all nodes.

The `fpxx` library has a `op_vld` input `result_vld` output for each core operation, which
ultimately strings all operations together, from the input of the pipeline to the output.

Now check out this [helper function](https://github.com/tomverbeure/rt/blob/29070b46fa30c290d7e530f7700b9ea1ef45a3eb/src/main/scala/rt/RT.scala#L13-L30):
```scala
object MatchLatency {

    // Match arrival time of 2 signals with _vld
    def apply[A <: Data, B <: Data](common_vld: Bool, a_vld : Bool, a : A, b_vld : Bool, b : B) : (Bool, A, B) = {

        val a_latency = LatencyAnalysis(common_vld, a_vld)
        val b_latency = LatencyAnalysis(common_vld, b_vld)

        if (a_latency > b_latency) {
            (a_vld, a, Delay(b, cycleCount = a_latency - b_latency) )
        }
        else if (b_latency > a_latency) {
            (b_vld, Delay(a, cycleCount = b_latency - a_latency), b )
        }
        else {
            (a_vld, a, b)
        }
    }
}
```

This function accepts a common/root valid and 2 valid/value pairs A and B. It calculates the latency
the common valid to the 2 A and B pairs and then inserts pipeline delays for either the A or the B pair
so that they are now aligned to each other.

Here's [an example](https://github.com/tomverbeure/rt/blob/29070b46fa30c290d7e530f7700b9ea1ef45a3eb/src/main/scala/rt/Sphere.scala#L109-L123)
how this is used in the code:
```scala
    val (common_dly_vld, tca_tca_dly, c0r0_c0r0_dly) = MatchLatency(
                                                io.op_vld,
                                                tca_tca_vld,   tca_tca,
                                                c0r0_c0r0_vld, c0r0_c0r0)

    val d2_vld = Bool
    val d2     = Fpxx(c.fpxxConfig)

    val u_d2 = new FpxxSub(c.fpxxConfig, Constants.fpxxAddConfig)
    u_d2.io.op_vld <> common_dly_vld
    u_d2.io.op_a   <> c0r0_c0r0_dly
    u_d2.io.op_b   <> tca_tca_dly

    u_d2.io.result_vld <> d2_vld
    u_d2.io.result     <> d2
```

Thanks to MatchLatency and LatencyAnalysis, `tca_tca_dly` and `c0r0_c0r0_dly` are now latency
aligned, with a `common_dly_vld` as their common valid signal!

I can change the pipeline depth of each math operation at will, and the the whole pipeline
adjust automatically, inserting delays as needed.

LatencyAnalysis is absolutely brilliant and is a life saver when you design a pipeline that,
in my case, ended up to have more than 100 stages.

Further improvements are possible: right now, I have a separate `_vld` signal for the operations. A more 
canonical SpinalHDL way would be to wrap operands in a generic `Flow` object. But that's an improvement
for later.


