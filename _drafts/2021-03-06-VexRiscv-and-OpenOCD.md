---
layout: post
title: VexRiscv and OpenOCD
date:  2021-03-06 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Introduction

The VexRiscv is fantastic soft core RISC-V CPU: small, configurable, yet with a very decent
performance. It's perfect for FPGAs, and I use it in pretty much all my FPGA projects.

It's one of the few open source CPUs for which there's extensive debugger support. There's
a customized version of OpenOCD which acts as the glue between GDB and the VexRiscv in your
projects.

While there's some documentation available, there isn't much, and it left me wanting to know
more about it.

In this blog post, I'll go through setting up a small VexRiscv design with debug support, and
discuss how to make it work in simulation, and how to use it on real hardware. I will
also discuss low level technical details that might not be important for most users, but that
will provide insight in case you need to dig deeper.

# The VexRiscv Debug Plugin

In a [previous blog post](rtl/2018/12/06/The-VexRiscV-CPU-A-New-Way-To-Design.html) about the 
VexRiscv, I wrote about how the unique plug-in based architecture that is used to construct
a VexRiscv CPU configuration.

True to its overall design philosophy, adding debugger support to a VexRiscv is also a matter
of adding a `DebugPlugin` to the CPU configuration structure. Let's have a quick look at some
of the core elements of 
[its source code](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala).

The plugin adds a 
[`DebugExtensionBus`](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L36-L38) 
to parallel interface to the CPU, which consists of a 
[DebugExtensionCmdBus and DebugExtensionRspBus](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L18-L25).

```scala
case class DebugExtensionCmd() extends Bundle{
  val wr = Bool
  val address = UInt(8 bit)
  val data = Bits(32 bit)
}
case class DebugExtensionRsp() extends Bundle{
  val data = Bits(32 bit)
}
```

As you can see, the bus is a pretty generic 32-bit data bus with address, read and write data.

Scroll a bit down you can find 
[the code](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L225-L263) 
that implements an address decoder and the registers that can be accessed by the debug bus.

Ignoring the lower 2 bits of the address bit, we get the following major addresses:

* a write to [address 0x0](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L240-L247)
    is used to set a number of debug control bits:

    ```scala
  is(0x0) {
    when(io.bus.cmd.wr) {
      stepIt := io.bus.cmd.data(4)
      resetIt setWhen (io.bus.cmd.data(16)) clearWhen (io.bus.cmd.data(24))
      haltIt setWhen (io.bus.cmd.data(17)) clearWhen (io.bus.cmd.data(25))
      haltedByBreak clearWhen (io.bus.cmd.data(25))
      godmode clearWhen(io.bus.cmd.data(25))
    }
  }
    ```
* a write to [address 0x01](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L249-L254)
    kicks off an event on the `injectionPort`.

    ```scala
  injectionPort.payload := io.bus.cmd.data
  ...
  is(0x1) {
    when(io.bus.cmd.wr) {
      injectionPort.valid := True
      io.bus.cmd.ready := injectionPort.ready
    }
  }
    ```

    The injection port is in interface into the 
    [`Fetcher`](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/Fetcher.scala) 
    unit, a plugin that is responsible for instruction fetching, interface with branch predictors etc.

    Check out 
    [the code](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/Fetcher.scala#L346-L401) 
    for all the details, but a debug bus write to address 0x01 seems to force the written debug write
    data as an insruction into the CPU pipeline.

* a write to [addresses of 0x10 and higher](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L255-L261)
    sets up a configurable number of hardware breakpoints.

    ```scala
  for(i <- 0 until hardwareBreakpointCount){
    is(0x10 + i){
      when(io.bus.cmd.wr){
        hardwareBreakpoints(i).assignFromBits(io.bus.cmd.data)
      }
    }
  }
    ```

The read data bus returns the following:

* when [bit 2 of the address is asserted](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L227-L233): 
  value of the debug control bits.

    ```scala
  when(!RegNext(io.bus.cmd.address(2))){
    io.bus.rsp.data(0) := resetIt
    io.bus.rsp.data(1) := haltIt
    io.bus.rsp.data(2) := isPipBusy
    io.bus.rsp.data(3) := haltedByBreak
    io.bus.rsp.data(4) := stepIt
  }
    ```

    This returns the value of the bits that were written by writing to address 0x00.
    Some of these can be modified by other transactions that just writing to address 0x00.

* [all other addresses](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L221-L226): 
  the value of last data that was written into the CPU register file.

    ```scala
  val busReadDataReg = Reg(Bits(32 bit))
  when(stages.last.arbitration.isValid) {
    busReadDataReg := stages.last.output(REGFILE_WRITE_DATA)
  }
  ...
  io.bus.rsp.data := busReadDataReg
    ```

It will lead to far to go into the functional details of all these bits (though names like `haltIt`, `resetIt` etc. should
give you a hint), what's important is this:

* we have an external debug control interface 
* we can read and write debug control bits
* there are a bunch of hardware breakpoints
* we can insert any instruction into the CPU pipeline
* we can grab the execution result of the instruction that was was inserted into the CPU pipeline

This gives us a nice summary of the capabilities of the Debug plugin and how higher level software will
interact with it to give us traditional debug functionality:

**The debugger will insert instructions into the CPU pipeline to write to memory, read from memory,
perform jumps etc.**

This should be familiar to very old people, like me, who ever had the pleasure of working at the lowest level 
with the ARM7TDMI (in 1995!): it has an serial (JTAG connected) interface that could override the bus of the CPU.
When the debugger wanted to read data from memory, you'd apply a load instruction, have the CPU
execute it, and capture the result just the same.

![ARM7TDMI debug scan chains](/assets/vexriscv_ocd/arm7tdmi_debug_scan_chains.png)
*(Credit: [The ARM7TDMI Debug Architecture - Application Note 28](https://developer.arm.com/documentation/dai0028/a/))*

In addition to defining the generic 32-bit parallel debug bus, the Debug plugin also provides a number of
adapters to link to different bus protocols. Some are very thin wrappers to other parallel busses, such as 
ARM's [APB3](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L45-L61), 
Intel's [Avalon](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L63-L75),
SpinalHDL's [PipelineMemoryBus](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L77-L89),
[Bmb](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L91-L111), or
[SystemDebuggerMemBus](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L113-L123).
Others are IMO more interesting:
[Jtag](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L125-L137) and
[JtagInstructionCtrl](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L139-L152)
link to SpinalHDL's JTAG instructure.







# References

* [The ARM7TDMI Debug Architecture - Application Note 28](https://developer.arm.com/documentation/dai0028/a/)



