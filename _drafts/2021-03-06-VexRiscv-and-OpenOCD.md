---
layout: post
title: VexRiscv and OpenOCD
date:  2021-03-06 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Introduction

The [VexRiscv](https://github.com/SpinalHDL/VexRiscv) is fantastic soft core RISC-V CPU: 
small, configurable, yet with a very decent performance. It's perfect for FPGAs, and I 
use it in pretty much all my FPGA projects.

It's also one of the few open source CPUs for which there's extensive debugger support. There's
a [customized version of OpenOCD](https://github.com/SpinalHDL/openocd_riscv) 
which acts as the glue between GDB and the VexRiscv in your projects.

While there's some documentation available, there isn't much, and it left me wanting to know
more about it.

In this blog post, I'll set up a small VexRiscv design with debug support, I'll show how to make it 
work on real hardware, and how to use *semi-hosting*, an interesting debug feature that has been 
borrowed from the ARM embedded CPU eco-system.

I will also discuss some low level technical details that might not be important for most users, 
but that will provide insight in case you need to dig deeper.

# Debug Flow Overview

When you only ever have debugged code that runs on your native PC, or on an embedded system for
which an IDE hides all the details, understanding all the components of an embedded debug system 
can be a bit confusing.

The figure below illustrates the different components of an end-to-end debug system. While
Vexriscv specific, the general concepts apply to any embedded debug system.

![Debug Flow - IDE to CPU Data Flow](/assets/vexriscv_ocd/vexriscv_ocd-ide_to_cpu_data_flow.svg)

Bottom up, we encounter the following components:

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

    This block is a small layer that converts the lightweight SystemDebugRemoteBus above it
    into the wider SystemDebuggerBus. These busses are both VexRiscv specific.

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
    You have to use [`openocd-riscv`](https://riscv.org/technical/specifications/), 
    the custom version of OpenOCD with VexRiscv functionality. The changes of this custom
    version have not been upstreamed to the official OpenOCD repo!**

* GDB

    GDB is reponsible for loading code, managing breakpoints, starting and halting a CPU, 
    stepping to the next assembler instructions or the next line of code etc.

    When used in a remote debug configuration, as is the case here, GDB does not need to
    the know the low level specifics of the CPU that's under debug. All it needs to know is the
    CPU family: how many CPU registers, function calling conventions, stack management,
    etc. 

    The low level details are handled by OpenOCD instead. Because of this, you can use
    a RISC-V GDB that is part of a standard RISC-V GCC toolchain. There is no need for
    a VexRiscv-specific GDB version. I'm using the 
    [RISC-V toolchain from the SiFive Freedom Tools](https://github.com/sifive/freedom-tools/releases).

* IDE

    This can be an editor with built-in debug capabilties such as [Eclipse](https://www.eclipse.org/ide/) 
    or [VSCode](https://code.visualstudio.com). It can be stand-alone debugger gui such as
    [gdbgui](https://www.gdbgui.com). Or it can be TUI, the GUI that's built into GDB
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

You can find all the code for this blog post in my 
[`vexriscv_ocd_blog` repo](https://github.com/tomverbeure/vexriscv_ocd_blog) on GitHub.

**VexRiscv Verilog**

I normally write all my hobby RTL code in SpinalHDL, but to make it easier for others
to use this design as an example, I wrote the toplevel, 
[`top.v`](https://github.com/tomverbeure/vexriscv_ocd_blog/blob/main/rtl/top.v) in pure Verilog, 
and had SpinalHDL create a stand-alone 
[`VexRiscvWithDebug.v`](https://github.com/tomverbeure/vexriscv_ocd_blog/blob/main/spinal/VexRiscvWithDebug.v) 
Verilog file that contains the CPU and the JTAG debug logic. As long as you don't feel the need to make 
changes to the CPU configuration, you don't have to install SpinalHDL or anything .

**VexRiscv configuration**

The VexRiscv can be configured into a thousand different ways. The exact details of the CPU system
that's used in this example aren't very important, so to avoid this article to become too
long, you can read about them [here](https://github.com/tomverbeure/vexriscv_ocd_blog#vexriscv-configuration).

There's also [a functional testbench](https://github.com/tomverbeure/vexriscv_ocd_blog#simulating-the-design) 
to check that the basic design is sound.

# System Setup with a Generic JTAG Debug Interface

In the most straigthforward setup, pins for the CPU debug JTAG interface are routed from
the FPGA core logic to general purpose FPGA IO pins, as shown in the diagram below:

![System Setup with Generic JTAG](/assets/vexriscv_ocd/vexriscv_ocd-system_setup_generic.svg)

The disadvantage of this configuration is that you end up with two separate paths from your PC
to the FPGA board: one to load the bitstream into the FPGA and one to debug the CPU. Generic IO pins 
are often precious and it's painful to waste 4 of them just for debugging.

![DECA FPGA board with 2 cable](/assets/vexriscv_ocd/deca_board_with_2_cables.jpg)

But it has the benefit of being completely generic and universal: it will work on any FPGA board and 
FPGA type.

There is an alternative: with the notable exception of the Lattice ICE40 family, almost all FPGAs
have have a way for the core programmable logic to tie into the JTAG TAP that's already part of the FPGA. 
Intel has [virtual JTAG infrastructure](/2021/05/02/Intel-JTAG-UART.html#the-intels-virtual-jtag-system), 
Xilinx has the BSCANE primitive cell, and Lattice ECP5 has the JTAGG primitive cell. 
With a bit of additional logic and corresponding support in OpenOCD, it's possible to create a system with 
just one cable.

![System Setup with Native JTAG Extension](/assets/vexriscv_ocd/vexriscv_ocd-system_setup_shared_tap.svg)

The SpinalHDL and the VexRiscv version of OpenOCD have support for some of these options. The VexRiscv
repo even contains a [detailed description](https://github.com/SpinalHDL/VexRiscv/tree/master/doc/nativeJtag)
about how to do this for a Xilinx FPGA.

However, for the remainder of this article will deal with the generic option only.

# Building the Design for FPGA

For this project, I primarily used the [$37 Arrow DECA FPGA board](/2021/04/23/Arrow-DECA-FPGA-board.html) that
I reviewed earlier.  It's one of the best deals in town!

You can find the configuration files for the example project 
[here](https://github.com/tomverbeure/vexriscv_ocd_blog/tree/main/quartus_max10_deca).

The example design has the following external IOs:

* `clk`: an external clock input. 

    On the Arrow DECA, this clock is 50MHz. The design doesn't use any PLL to create a different clock.
    **Due to some internal VexRiscv design decisions, the CPU clock must be higher than the JTAG clock!**

* `led0`, `led1`, `led2`: the CPU will toggle these LEDs in sequence. 
* `button`: when pressed, the LEDs toggling sequence doubles in speed
* `jtag_tck`, `jtag_tms`, `jtag_tdi`, `jtag_tdo`: the generic JTAG interface

    The JTAG IOs are assigned to pins of the P9 connector of the DECA board, as seen in the
    closeup picture below:

    ![JTAG pins closeup](/assets/vexriscv_ocd/jtag_pins_closeup.jpg)

In addition to the project files, I've also provided ready-made 
[`vexriscv_ocd.sof`](https://github.com/tomverbeure/vexriscv_ocd_blog/tree/main/quartus_max10_deca/output_files)
bitstream so you can try things out right away.

# Debug Logic Resource Cost

Adding debug logic is not free, but the cost is very reasonable.

On the Intel Max 10 FPGA using Quartus Prime 20.1 Lite Edition, the resource usage for the complete design with JTAG debug 
enabled is 2382 logic cells and 1124 flip-flops.

![Quartus Resource Usage with JTAG Enabled](/assets/vexriscv_ocd/resource_usage_with_jtag_enabled.png)

When [JTAG is disabled](https://github.com/tomverbeure/vexriscv_ocd_blog/blob/main/rtl/top.v#L3-L4)
by strapping IO input pins constant value, and TDO is left dangling, Quartus does an excellent
job at optimizing all debug logic out, and the resource usage drops to 2054 logic cells and 858 flip-flops.

![Quartus Resource Usage with JTAG IO Strapped](/assets/vexriscv_ocd/resource_usage_with_jtag_strapped.png)

The resource usage for a VexRiscv CPU, with or without DebugPlugin, is heavily dependent on which features
are enabled. A good example is CSR related functionality (these are special register inside a RISC-V
CPU to deal with interrupts, traps, instruction counters etc.) The logic behind these is often straightforward,
but they can consume a lot of FFs. The CPU I'm using here has trap exception support enabled, and that 
costs more than 100 FFs. 

Conclusion: adding debug logic increases the resource usage around 16%. That seems high, but it's more a testament to
how small the VexRiscv really is. If you were to enable the HW multiplier and divider, instruction and data caches, and MMU, 
the percentage of the debug related logic would go descend into low single digits.

# Compiling the Custom OpenOCD Version

As mentioned earlier, you'll need a custom version of OpenOCD.

The instructions below worked on my Ubuntu 20.4 Linux distribution. Note also how I specify
an installation directory of `/opt/openocd_vex`. Change that to your own preferences...

```sh
sudo apt install libtool automake libusb-1.0.0-dev texinfo libusb-dev libyaml-dev pkg-config
git clone https://github.com/SpinalHDL/openocd_riscv
cd openocd_riscv
./bootstrap
./configure --prefix=/opt/openocd_vex --enable-ftdi --enable-dummy
make -j $(nproc)
sudo make install
```

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
[loading a Xilinx Spartan 6 bitstream with OpenOCD](/2019/09/15/Loading-a-Spartan-6-bitstream-with-openocd.html)
that explains the process.

In my case, I'm using a Xilinx Digilent JTAG SMT2 clone. This is the magic incantation:

```sh
/opt/openocd-vex/bin/openocd \ 
    -f /opt/openocd-vex/share/openocd/scripts/interface/ftdi/digilent_jtag_smt2.cfg 
    -c "adapter speed 1000; transport select jtag" 
    -f "./sw/vexriscv_init.cfg"
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

We were able to connect to the JTAG TAP, we were able to connect to the CPU, and we were able to halt it.
On your FPGA development board, you should have noticed that the LEDs are not blinking anymore.

OpenOCD also opened a GDB server on port 3333. Soon, we'll be executing debug instructions to the CPU from
GDB through this TCP/IP port to OpenOCD which will translate them instead JTAG commands.

You can run the OpenOCD command above by running `make ocd` in the `./sw` directory.

# The vexriscv_init.cfg file

Notice above that I added `-f ./sw/vexriscv_init.cfg` as a command line parameter when starting openocd.

The [`vexriscv_init.cfg`](https://github.com/tomverbeure/vexriscv_ocd_blog/blob/main/sw/vexriscv_init.cfg) 
file sets up parameters that are specific to the VexRiscv configuration of our design.

In addition to some standard OpenOCD commands that set up JTAG TAP configuration and debug targets, this file
also has some VexRiscv specific commands:

```
vexriscv readWaitCycles 10
...
vexriscv cpuConfigFile ../spinal/VexRiscvWithDebug.yaml
```

The custom OpenOCD version can be configured to deal with configuration that have multiple VexRiscv CPUs 
attached to a single JTAG TAP. It can also handle HW breakpoints, cache invalidation and more. But it needs
to know about this, and the `vexriscv` commands are used for that.

For this simple example, let's just ignore this and use some defaults that work.

# Debugging with Barebones GDB

OpenOCD should already be up and running in one terminal window. Open a second one to run GDB,
then do the following:

```sh
cd ./sw
make gdb
```

You should see something like this:

```
/opt/riscv64-unknown-elf-toolchain-10.2.0-2020.12.8-x86_64-linux-ubuntu14/bin/riscv64-unknown-elf-gdb -q \ 
        progmem.elf \
	-ex "target remote localhost:3333"
Reading symbols from progmem.elf...
Remote debugging using localhost:3333
0x000001e0 in wait_cycles (cycles=0) at lib.c:38
38	    while ((rdcycle64() - start) <= (uint64_t)cycles) {}
(gdb) 
```

We called GDB with the following parameters:

* `-q` to make it not print a GPL license header
* `progmem.elf` to give GDB information about the program that's currently running on the CPU
* `-ex "target remote localhost:3333"` to tell GDB to connect to the OpenOCD server that's running in our other terminal.

GDB complied with our request, and also showed the line in the C code where the CPU has been halted. The code 
spends the vast majority of its time until a timer expires, to slow down the LED toggle rate, so it's no
surprise to see `wait_cycles()` listed here.

You can now do bunch of GDB commands:

* Continue where GDB left off

```
(gdb) c
Continuing.
```

* Load the program binary again, set a breakpoint, reset the CPU, and rerun from start, continue after break:

```
(gdb) load
Loading section .text, size 0x202 lma 0x0
Start address 0x00000000, load size 514
Transfer rate: 4112 bits in <1 sec, 514 bytes/write.
(gdb) br main
Breakpoint 1 at 0x102: file main.c, line 55.
(gdb) monitor soft_reset_halt
requesting target halt and executing a soft reset
(gdb) c
Continuing.

Program stopped.
main () at main.c:55
55	    global_cntr = 0;
(gdb) c
Continuing.
```

If you've ever used GDB without GUI to debug programs on your PC, everything should be very
familiar. The only thing that doesn't work is `run`. For some reason, after doing `load`, you need
to do `monitor soft_reset_halt` and then `continue` instead.

# Debugging with GDBGUI




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


