---
layout: post
title: VexRiscv DebugPlugin Under the Hood
date:  2021-07-18 00:00:00 -1000
categories:
---

* TOC
{:toc}



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


# An Overview of the GDB - OpenOCD - SOC - CPU Pipeline

# Running Your First VexRiscv - GDB Session

# Murax - An Included Hardware Example

* [Murax.scala](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/demo/Murax.scala)

[Murax Toplevel](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/demo/Murax.scala#L155-L171)

```scala
case class Murax(config : MuraxConfig) extends Component{
  import config._

  val io = new Bundle {
    //Clocks / reset
    val asyncReset = in Bool
    val mainClk = in Bool

    //Main components IO
    val jtag = slave(Jtag())

    //Peripherals IO
    val gpioA = master(TriStateArray(gpioWidth bits))
    val uart = master(Uart())

    val xip = ifGen(genXip)(master(SpiXdrMaster(xipConfig.ctrl.spi)))
  }
```

Check out the JTAG IO port.

Further down:

[JTAG IO pins are connected to the DebugPlugin](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/demo/Murax.scala#L251-L254):

```scala
  case plugin : DebugPlugin         => plugin.debugClockDomain{
    resetCtrl.systemReset setWhen(RegNext(plugin.io.resetOut))
    io.jtag <> plugin.io.bus.fromJtag()
  }
```

The [`fromJtag`](https://github.com/SpinalHDL/VexRiscv/blob/75bbb28ef62636dd0d4d3741c6e559a911fc85af/src/main/scala/vexriscv/plugin/DebugPlugin.scala#L125-L137)
contains the following:

```scala
  def fromJtag(): Jtag ={
    val jtagConfig = SystemDebuggerConfig(
      memAddressWidth = 32,
      memDataWidth    = 32,
      remoteCmdWidth  = 1
    )
    val jtagBridge = new JtagBridge(jtagConfig)
    val debugger = new SystemDebugger(jtagConfig)
    debugger.io.remote <> jtagBridge.io.remote
    debugger.io.mem <> this.from(jtagConfig)

    jtagBridge.io.jtag
  }
```

This code instantiates 2 blocks: a `JtagBridge` and a `SystemDebugger`.

The [`JtagBridge`](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebugger.scala#L57-L84)
interfaces the JTAG IO pins to a SpinalHDL-specific [`SystemDebuggerRemoteBus`](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebuggerBundles.scala#L12-L25).

It instantiates a traditional [JTAG TAP](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebugger.scala#L79)
and [adds 3 scan chain operations](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebugger.scala#L80-L82)
 to it:
* a 32-bit ID code
* a write register to transmit serialized commands from that JTAG port to the CPU.
* a read register to read back from the CPU to the JTAG port

The [`SystemDebugger`](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebugger.scala#L145-L155)
converts the `SystemDebuggerRemoteBus` (which still transmit commands one bit at a time) to a 
[`SystemDebuggerBus`](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebuggerBundles.scala#L27-L42)
by [converting the serialized command bus bits into a parallel one](https://github.com/SpinalHDL/SpinalHDL/blob/adf552d8f500e7419fff395b7049228e4bc5de26/lib/src/main/scala/spinal/lib/system/debugger/SystemDebugger.scala#L151).

The `SystemDebuggerBus` can be connected straight to the debug bus of the Debug plugin.

When everything is said and one, we have SOC design that contains our VexRiscv, a JTAG port, and all the glue logic to link that JTAG port to the debug port of the CPU.

# Running firmware

# OpenOCD VexRiscv Specific Code

**Low level CPU interactions**

* [`vexriscv_memory_cmd`](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L1127-L1179)

    Prepares a JTAG DR chain command to issue a SystemDebugger command.

    This is the core command to create DebugBus transactions that's used by pretty much all other higher level
    commands to make the VexRiscv do something in debug mode.

* [`vexriscv_pushInstruction`, `vexriscv_setHardwareBreakpoint`, ...](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L1394-L1440)

    Slightly higher level commands that interact with the debug bus registers of the VexRiscv.

* [`vexriscv_write_regfile`](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L240-L256)

    Set the value of a register of the CPU register file by executing a mix of `LUI`, `ADDI`, and `ORI` instructions.

    The exact instruction(s) to execute depends on the value that needs to be written to the register file.

* [`vexriscv_read_memory`](https://github.com/SpinalHDL/openocd_riscv/blob/riscv_spinal/src/target/vexriscv.c#L1234-L1269)

    Reads an array of data from memory that's attached to the VexRiscv.

    It does this by doing the following sequence:
    
    * [Load register `x1`](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L1245) 
       with the memory address that must be read.
    * [Execute a `LW`, `LHU`, `LBU` instruction](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L1250)
       to load the requested data from memory.
    * [Read back the data](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L1251).

        We saw earlier that the debug plugin captures the data that is last written to a register file.

* [`vexriscv_save_context'](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L687-L728)

    When the Vexriscv has stopped running (e.g. because it encountered an `EBREAK` instruction or because the program counter
    triggered an hardware breakpoint), when whoever uses OpenOCD (this can be you on the command line, or a program like GDB)
    can interact with the CPU to extract data.

    To make sure this happens cleanly without destroying the state of the CPU, OpenOCD will first save the CPU context so
    that it can be restored later when the CPU should go back to executing.

    One of the most important context to save are the registers in the register file.

    On the VexRiscv, this is done by issuing an `ADDI x0, x?, 0` instruction for each register. This will
    read the value from the register file, add 0, and store it back to register 0, which gets ignored.

    However, the debug hardware always remembers the last value that was sent to the register file, and makes it
    available for read-back over the debug bus.

* 


# References

* [The ARM7TDMI Debug Architecture - Application Note 28](https://developer.arm.com/documentation/dai0028/a/)
* [ARM semihosting specification](https://static.docs.arm.com/100863/0200/semihosting.pdf)
* [Introduction to ARM Semihosting](https://interrupt.memfault.com/blog/arm-semihosting)
* [RISC-V: Creating a spec for semihosting](https://groups.google.com/a/groups.riscv.org/g/sw-dev/c/M7LDRtBtxrk)
* [Github: enabled semihosting on vexriscv](https://github.com/SpinalHDL/openocd_riscv/pull/7)
* [SaxonSoc openocd settings](https://github.com/SpinalHDL/SaxonSoc/blob/dev-0.2/bsp/digilent/ArtyA7SmpLinux/openocd/usb_connect.cfg#L19)
* [linker script tutorial](https://interrupt.memfault.com/blog/how-to-write-linker-scripts-for-firmware)
* [Semihosting implementation](https://gitlab.com/iccfpga-rv/iccfpga-eclipse/-/tree/master/xpacks/micro-os-plus-semihosting)
    * on [GitHub](https://github.com/micro-os-plus/semihosting-xpack)
    * [micro-OS Plus](http://micro-os-plus.github.io)
* [VEXRISCV 32-bit MCU](https://thuchoang90.github.io/vexriscv.html)
* [PQVexRiscv](https://github.com/mupq/pqriscv-vexriscv)
* [Litex VexRiscv Configuration](https://github.com/litex-hub/pythondata-cpu-vexriscv/blob/master/pythondata_cpu_vexriscv/verilog/src/main/scala/vexriscv/GenCoreDefault.scala)

* [Semihosting causes crash when not running in the debugger...](https://www.openstm32.org/forumthread2323)
* [bpkt ARM instruction freezes my embedded application](https://stackoverflow.com/questions/16396067/bpkt-arm-instruction-freezes-my-embedded-application)
* [What is Semihosting?](https://community.nxp.com/t5/LPCXpresso-IDE-FAQs/What-is-Semihosting/m-p/475390)
 
* [Official RISC-V OpenOCD semihosting code](https://github.com/riscv/riscv-openocd/blob/riscv/src/target/riscv/riscv_semihosting.c)
* [Embedded printf](https://github.com/mpaland/printf)


