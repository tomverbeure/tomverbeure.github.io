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

It's also one of the few open source CPUs for which there's extensive debugger support. There's
a customized version of OpenOCD which acts as the glue between GDB and the VexRiscv in your
projects.

While there's some documentation available, there isn't much, and it left me wanting to know
more about it.

In this blog post, I'll set up a small VexRiscv design with debug support, I'll show how to make it 
work on real hardware, and how to use *semi-hosting*, an interesting debug feature that has been 
borrowed the ARM embedded CPU eco-system.

I will also discuss some low level technical details that might not be important for most users, 
but that will provide insight in case you need to dig deeper.

# Debug Flow Overview

When you only ever have debugged code that runs on your native PC, or on an embedded system for
which an IDE hides all the details, understanding all the components of an embedded debug system 
can be a bit confusing.

The figure below illustrates the different components of an end-to-end debug system. While
Vexriscv specific, the general concepts apply to any embedded debug system.

![Debug Flow - IDE to CPU Data Flow](/assets/vexriscv_ocd/vexriscv_ocd-ide_to_cpu_data_flow.svg)

We can see the following components from bottom to up:

* VexRiscv CPU

    The CPU that is running the code that we need to debug. 

* VexRiscv Debug Plugin

    Hardware plugins are an interesting concept that's specific to the VexRiscv design philosophy. You
    can read more about it in [this blog post](/rtl/2018/12/06/The-VexRiscV-CPU-A-New-Way-To-Design.html).

    DebugPlugin adds the necessary logic to the VexRiscv CPU to halt and start the CPU, to
    set hardware breakpoints (if there are any), and to insert random instructions into the CPU 
    pipeline. 

    The plugin also adds a new external SystemDebugBus to the CPU to control these debug operations.

* SystemDebugger

    This block is just a small layer that converts the relatively wide SystemDebugBus to a 
    lightweight SystemDebugRemoteBus.

* JtagBridge

    The JTAG bridge takes in the standard 4 JTAG IO pins, contains a JTAG test access port (TAP), 
    adds a number of debug scan registers, and has the logic talk to the SystemDebugRemoteBus.

* USB to JTAG Dongle

    The hardware that links the development PC to the hardware that's under debug.

    There are no major requirements here: as long as the dongle is supported by OpenOCD,
    you should be good.

* OpenOCD

    This is probably the most important piece of the whole debug flow. 

    OpenOCD has support for almost all common JTAG dongles, and provides a generic JTAG API
    to control them.

    The generic JTAG API is controlled by a VexRiscv specific *target* driver. The
    OpenOCD VexRiscv driver knows exactly what needs to be be sent over JTAG to transfer debug 
    commands through the JtagBridge to the debug logic of the CPU.

    At the top of the OpenOCD stack is a GDB server that supports the GDB remote target
    debug protocol.

    The overall operation of OpenOCD consists of receiving high-level debug requests from
    GDB, translating this into VexRiscv specific JTAG transactions, and sending these
    transactions to a specific JTAG dongle.

    **The VexRiscv debug infrastructure is not compatible with the standard 
    [RISC-V Debug Specification](https://riscv.org/technical/specifications/). 
    You need [`openocd-riscv`](https://riscv.org/technical/specifications/), 
    a custom version of OpenOCD with VexRiscv functionality that is not upstreamed to 
    the official OpenOCD repo!**

* GDB

    GDB is reponsible for loading code, managing breakpoints, starting and halting a CPU, 
    stepping to the next assembler instructions or the next line of code etc.

    When used in a remote debug configuration, as is the case here, GDB doesn't need to
    the know the low level specifics of the CPU that's under debug. All it needs to know is the
    CPU family (how many CPU registers, function calling conventions, stack management,
    etc.) The low level details are handled by OpenOCD instead. Because of this, you can use
    a RISC-V GDB that is part of a standard RISC-V GCC toolchain. There is no need for
    a VexRiscv-specific GDB version.

* IDE

    This can be an editor with built-in debug capabilties such as [Eclipse](https://www.eclipse.org/ide/) 
    or [VSCode](https://code.visualstudio.com), it can be stand-alone debugger gui such as
    [gdbgui](https://www.gdbgui.com), or it can be TUI, the GUI that's built into GDB
    itself.

    *The IDE is optional: you can just enter commands straight in the GDB command line.*


There's a lot going on while debugging a program on an embedded CPU!

Luckily, it's not necessary to understand all the details. Most of you are really only
interested in using the system. So let's start with that: get a mimimal design with a
CPU running on an FPGA, and try to a debug environment working.

# A Minimal CPU System

Let's demonstrate a VexRiscv with a debugger on a minimal design that
consists of a VexRiscv CPU (with debug plugin, of course), a bit of RAM for CPU instructions,
and data, and some registers to control LEDs and read back the value of button.

![Minimal CPU System Block Diagram](/assets/vexriscv_ocd/vexriscv_ocd-minimal_cpu_system.svg)

**VexRiscv Verilog**

I normally write all my hobby RTL code in SpinalHDL, but to make it easier for others
to use this design as an example, I wrote the toplevel in pure Verilog, and had
SpinalHDL create a stand-alone VexRiscvWithDebug.v Verilog file that contains the CPU
and the JTAG debug logic. As long as you don't feel the need to make changes to the
CPU configuration, you don't have to install SpinalHDL or anything .

**VexRiscv configuration**

The VexRiscv can be configured into a thousand different ways. The exact details
of the configuration used can be found [here XXX](), but a short summary is:

* 5-stage pipeline configuration for a good trade-off between clock speed and area
* Debug feature enabled (duh)
* Compressed instructions support 

    A trade-off between smaller instruction memory usage and increased core
    logic area.

* No HW multiplier/divide support

    I don't want to waste FPGA DSPs on a multiplier. The VexRiscv has an option
    for a serial multiplier.

* Lightweight one-bit-at-a-time shifter instead of a barrel shifter

* 64-bit RISC-V cycle counter support

    In most cases, I only use a timer for simply delays (e.g. "wait 100us"). A
    CPU internal timer is sufficient for that.

* trap on EBREAK enabled

    This is not necessary for basic debug support, but it will be useful for semi-hosting
    support. See later.

**Dual-ported CPU Memory**

In many FPGAs, all block RAMs are true dual-ported, and there's no extra cost to use them.
The VexRiscv has a traditional Harvard architecture with separate instruction and data bus.

In this design, I use one port of the RAM for the CPU instruction bus, and the other port 
for the CPU data bus.  This removes the need for arbitration logic that selects between iBus or
dBus requests to memory, because they can happen in parallel.

The 32-bit memory is implemented with 4 8-bit wide RAMs, one for each byte lane. This way, 
I don't rely on the synthesis tool having to infer byte-enable logic...

**Peripheral registers**

The peripheral section contains 1 control register to set the LED values, and 1 status
register to read back the value of a button.

There's also a status bit that indicates whether or not the CPU is running on real
HW or in simulation. I use this bit for cases when I want the same SW image to behave
slightly different between FPGA and testbench. In this case, I use to change
the speed at which LEDs toggle. 

**No interrupts or external timer**

The CPU is generated with external and timer interrupt support enabled, but the inputs
are strapped to 0 in this minimal example.

# System Setup with a Generic JTAG Debug Interface

In the most straigthforward setup, pins for the CPU debug JTAG interface are routed from
the FPGA to general purpose IO pins, as shown in the diagram below:

![System Setup with Generic JTAG](/assets/vexriscv_ocd/vexriscv_ocd-system_setup_generic.svg)

The disadvantage of this configuration is that you end up with two separate paths from your PC
to the FPGA board: one to load the bitstream into the FPGA and one to debug the CPU. GPIO pins 
are often precious and it's painful to waste 4 of them just for debugging.

![DECA FPGA board with 2 cable](/assets/vexriscv_ocd/deca_board_with_2_cables.jpg)

But it has the benefit of being completely generic and universal: it will work on any FPGA board and 
FPGA type.

There is an alternative: almost all FPGAs, the Lattice ICE40 family is one notable exception, 
have a way for the core programmable logic to tie into the JTAG TAP that's already part of the FPGA. Intel
has virtual JTAG infrastructure, Xilinx has the BSCANE primitive cell, and Lattice ECP5 has the JTAGG 
primitive cell. With a bit of additional logic and corresponding support in OpenOCD, it's possible to 
create a system with just one cable.

![System Setup with Native JTAG Extension](/assets/vexriscv_ocd/vexriscv_ocd-system_setup_shared_tap.svg)

The SpinalHDL and the VexRiscv version of OpenOCD have support for some of these options, but that's for
future blog posts... The remainder of this article will deal with the generic option only.

# Simulating the Design

A testbench is always helpful to simulate before going to hardware. So for completeness, I've included one here as well.
While not self-checking, it was very useful in tracking down [a bug](https://github.com/SpinalHDL/VexRiscv/issues/176) 
in the VexRiscv DebugPlugin that has since been fixed.

In the `./tb` directory, just type `make`:

```sh
iverilog -D SIMULATION=1 -o tb tb.v ../rtl/top.v ../spinal/ ../spinal/VexRiscvWithDebug.v
./tb
VCD info: dumpfile waves.vcd opened for output.
               48250: led0 changed to 0
               65250: led0 changed to 1
               65250: led1 changed to 0
               82150: led1 changed to 1
               82150: led2 changed to 0
```

`make waves` will bring up the GTKWave waveform viewer and load the `waves.vcd` file that was created during
the simulation.

![GTKWave screenshot](/assets/vexriscv_ocd/gtkwave.png)

In the testbench, I have the JTAG inputs signals strapped to a fixed value, so I'm not actually testing
the debug functionality. But the goal of the test was primarily to check that my own code was fine, and,
as you can see, the leds are indeed toggling in sequence.

# Building the Design for FPGA

For this project, I primarily used the Arrow DECA FPGA board. At $37, it's one of the best deals in town!
Check out my review of this board [here](/2021/04/23/Arrow-DECA-FPGA-board.html).

In addition to the Arrow DECA, I also have project files for 3 other boards:

* the very old, barebones, but still useful, EP2C5T144 board with an Intel Cyclone II EP2C5 FPGA
* the official Intel Max 10 Development board with a large Max10 10M50 FPGA
* the Colorlight i5 with a Lattice ECP5-25 FPGA

You can find the configuration files for each of these boards [here XXXX](XXXX).

The example design has the following external IOs:

* `clk`: an external clock input of preferably 50MHz. The design doesn't use any PLL to create a different clock.
* `led0`, `led1`, `led2`: the CPU will toggle these LEDs in sequence. 
* `button`: when pressed, the LEDs toggling sequence doubles in speed
* `jtag_tck`, `jtag_tms`, `jtag_tdi`, `jtag_tdo`: the generic JTAG interface

In addition to the project files, I've also provided ready-made bitstream so you can try things out right away.

# Debug Logic Resource Cost

Adding debug logic is not free, but the cost is very reasonable.

On the Intel Max 10 FPGA, resource usage for the complete design with JTAG debug enabled is 2285 logic cells and 1108 flip-flops.

![Quartus Resource Usage with JTAG Enabled](/assets/vexriscv_ocd/resource_usage_with_jtag_enabled.png)

When the JTAG IO input pins are strapped to constant value, and TDO is left dangling, Quartus does an excellent
job at optimizing all debug logic out, and the resource usage drops to 1952 logic cells and 1108 flip-flops.

![Quartus Resource Usage with JTAG IO Strapped](/assets/vexriscv_ocd/resource_usage_with_jtag_strapped.png)

The resource usage for a VexRiscv CPU, with or without DebugPlugin, is heavily dependent on which features
are enabled. A good example is CSR related functionality (these are special register inside a RISC-V
CPU to deal with interrupts, traps, instruction counters etc.) The logic behind these is often straightforward,
but they can consume a lot of FFs. The CPU I'm using here has trap exception support enabled, and that 
costs more than 100 FFs. 

Conclusion: adding debug logic increases the resource usage around 15%. That seems high, but it's more a testament to
how small the VexRiscv really is, especially a low performance configuration like this one. If you were to enable the 
HW multiplier and divider, the barrel shifter, instruction and data caches, MMU, the percentage of the debug related
logic would go descent into low single digits.

# Connecting to the JTAG TAP of the FPGA

It's now time to set everything up for SW debugging on a live FPGA system.

We first need to be able to access the debug JTAG TAP from our PC.

There are 3 things that need to be in place:

1. the JTAG pins of the dongle must be connected to the right FPGA pins

    Do that first, while the FPGA board is powered off.

1. the FPGA must have the bitstream loaded with the JTAG TAP logic

    Do that next. If you're using my example design, you should see 3 LEDs blinking
    one after the other.

1. an OpenOCD configuration file that loads the right JTAG dongle driver

I personally dread step number 3 the most: when everything has been set up correctly, you don't need to
use `sudo` when running OpenOCD, and hopefully you find the right driver, but it's never a sure thing.

Either way, I wrote a blog post in the past about 
[loading a Xilinx Spartan 6 bitstream with OpenOCD ](2019/09/15/Loading-a-Spartan-6-bitstream-with-openocd.html)
that explains the process.

In my case, I'm using a Xilinx Digilent JTAG SMT2 clone. This is the magic incantation:

```sh
/opt/openocd-vex/bin/openocd \ 
    -f /opt/openocd-vex/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg 
    -c "adapter speed 1000; transport select jtag" 
```

```
Open On-Chip Debugger 0.10.0+dev-01231-gf8c1c8ad-dirty (2021-03-07-17:49)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
jtag
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
Info : clock speed 1000 kHz
Warn : There are no enabled taps.  AUTO PROBING MIGHT NOT WORK!!
Info : JTAG tap: auto0.tap tap/device found: 0x10001fff (mfg: 0x7ff (<invalid>), part: 0x0001, ver: 0x1)
Warn : AUTO auto0.tap - use "jtag newtap auto0 tap -irlen 4 -expected-id 0x10001fff"
Warn : gdb services need one or more targets defined
```

OpenOCD found a JTAG device with an IDCODE of 0x10001fff. SpinalHDL choose that value for me.

Let's now also load the VexRiscv-specific configuration file:

```sh
/opt/openocd-vex/bin/openocd \ 
    -f /opt/openocd-vex/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg 
    -c "adapter speed 1000; transport select jtag" 
    -f "vexriscv_init.cfg"
```

```
Open On-Chip Debugger 0.10.0+dev-01231-gf8c1c8ad-dirty (2021-03-07-17:49)
Licensed under GNU GPL v2
For bug reports, read
	http://openocd.org/doc/doxygen/bugs.html
jtag
Info : set servers polling period to 50ms
Info : clock speed 1000 kHz
Info : JTAG tap: fpga_spinal.bridge tap/device found: 0x10001fff (mfg: 0x7ff (<invalid>), part: 0x0001, ver: 0x1)
Info : starting gdb server for fpga_spinal.cpu0 on 3333
Info : Listening on port 3333 for gdb connections
Halting processor
requesting target halt and executing a soft reset
Info : Listening on port 6666 for tcl connections
Info : Listening on port 4444 for telnet connections
```

Success! 

We were able to connect to the JTAG TAP and we were able to connect to the CPU and we were able to halt it.
On your FPGA development board, you should have noticed that the LEDs are not blinking anymore.

OpenOCD also opened a GDB server on port 3333. Soon, we'll be executing debug instructions to the CPU from
GDB through this TCP/IP port to OpenOCD which will translate them instead JTAG commands.

You can run the OpenOCD command above by running `make ocd` in the `./sw` directory.

# The vexriscv_init.cfg file

The `vexriscv_init.cfg` file in the `./sw` directory sets up parameters that are specific to the VexRiscv configuration 
of our design.

# Debugging the Software


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

# Semihosting

Since the beginning of time, ARM has supported semihosting, a feature that allows the DUT CPU (IOW, the ARM CPU) to issue commands to the host
PC to which it is connected. In the words of the [ARM semihosting specification](https://static.docs.arm.com/100863/0200/semihosting.pdf): 

> Semihosting is a mechanism that enables code running on an ARM target or emulator 
> to communicate with and use the Input/Output facilities on a host computer. The host 
> must be running the emulator, or a debugger that is attached to the ARM target.

Semihosting is an extremely powerful feature, since it can give a tiny embedded CPU that doesn't have any
generic IO capabilities to do things like accepting keystrokes, print out debug information to a debug
console, or even read and write from and to a file on the host PC!

*The performance of these semihosting commands is subject to the bandwidth of the communication interface
by which the embedded CPU is connected to the host PC, so don't expect miracles here in the case of JTAG.*

It's up to the external debugger (OpenOCD in our case) to intercept semihosting operation request from DUT CPU and perform
the requested action.

Here's a list of the actions that are defined in the specification, and in the 
[OpenOCD source code](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/semihosting_common.h#L53-L76):

```c
	SEMIHOSTING_SYS_CLOSE = 0x02,
	SEMIHOSTING_SYS_CLOCK = 0x10,
	SEMIHOSTING_SYS_ELAPSED = 0x30,
	SEMIHOSTING_SYS_ERRNO = 0x13,
	SEMIHOSTING_SYS_EXIT = 0x18,
	SEMIHOSTING_SYS_EXIT_EXTENDED = 0x20,
	SEMIHOSTING_SYS_FLEN = 0x0C,
	SEMIHOSTING_SYS_GET_CMDLINE = 0x15,
	SEMIHOSTING_SYS_HEAPINFO = 0x16,
	SEMIHOSTING_SYS_ISERROR = 0x08,
	SEMIHOSTING_SYS_ISTTY = 0x09,
	SEMIHOSTING_SYS_OPEN = 0x01,
	SEMIHOSTING_SYS_READ = 0x06,
	SEMIHOSTING_SYS_READC = 0x07,
	SEMIHOSTING_SYS_REMOVE = 0x0E,
	SEMIHOSTING_SYS_RENAME = 0x0F,
	SEMIHOSTING_SYS_SEEK = 0x0A,
	SEMIHOSTING_SYS_SYSTEM = 0x12,
	SEMIHOSTING_SYS_TICKFREQ = 0x31,
	SEMIHOSTING_SYS_TIME = 0x11,
	SEMIHOSTING_SYS_TMPNAM = 0x0D,
	SEMIHOSTING_SYS_WRITE = 0x05,
	SEMIHOSTING_SYS_WRITEC = 0x03,
	SEMIHOSTING_SYS_WRITE0 = 0x04,
```

The embedded CPU typically has a C library that translates these semihosting operations into functions such 
as `printf`, `sys_close()` etc.

While originally defined for ARM, there's little that prevents anyone to use it for their own CPU. OpenOCD
has made it particularly easy by isolating generic semihosting handling code from ARM specific files.

Yet going by the OpenOCD source, only the VexRiscv implemented support for semihosting.


So how does semihosting work on the VexRiscv?

OpenOCD will poll the CPU and check if the CPU is currently hatled at a program location the contains
the [following instruction sequence](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L854-L859):

```
      slli    zero,zero,0x1f
      ebreak
      srai    zero,zero,0x7
```

*The first and third instructions are dummies (they use `zero` as the destination register), so they're
not the kind of thing that will ever be generated by a compiler.*

If the CPU was halted without seeing that sequence then there must have been another reason for the halt.
E.g. the user might have set their own breakpoint.

Otherwise, OpenOCD will fetch the semihosting parameters, and execute them on the host PC.


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


