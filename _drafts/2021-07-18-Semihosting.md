---
layout: post
title: Semihosting - Use a PC as Terminal and File Server for Your Embedded CPU
date:  2021-07-18 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Regular readers of my blog posts should know by now that I'm a bug fan of adding a small
embedded CPU in my FPGA projects for overall management, 
[bit-banging](https://en.wikipedia.org/wiki/Bit_banging) slow protocols
such as [I2C](https://en.wikipedia.org/wiki/I²C), and some real-time operations with not too
stringent timing requirements. They'll also know that the 
[VexRiscv](https://github.com/SpinalHDL/VexRiscv) is the standard soft-core CPU in my
toolbox.

When running code on an embedded CPU, it's very often helpful to have an interface to a
PC to run some kind of console for control, debugging, and logging. A UART is obviously
very popular for this, but I often also use a [JTAG UART](2021/05/02/Intel-JTAG-UART.html), 
which can be easier to integrate if you already have a JTAG connection to for FPGA for 
other reasons.

But there's another option that many probably have never heard about. Instead of using
a dedicated HW block, it leverages the existing debug infrastructure of the CPU by adding a
peculiar software layer to the low level debug driver on top of it. 

It's called semihosting, and it allows the embedded CPU use the host PC as a server
for a variety of functions: STDIO read and write, access to the PC file system, time 
server etc.

Semihosting is definitely a bit of a hack, but it's a clever one, and I think there's 
something magical about a slow embedded CPU with 4KB of RAM commandeering a mighty
PC into reading and writing files on its file system.

# Semihosting and RISC-V

Semihosting is nothing new: I first used semihosting in 1995 on a prehistoric ARM7TDMI CPU
that was embedded in the 
[Alcatel MTC-20276](http://static6.arrow.com/aropdfconversion/467166f711419cfece3c159c1fd6c2fc98bf586c/mtc-20276.pdf), 
an [ISDN](https://en.wikipedia.org/wiki/Integrated_Services_Digital_Network) ASIC that was 
going to take over the world... 

![ISDN chip with ARM7TDMI](/assets/semihosting/isdn_chip.png)

It did not take over the world at all, but it was great for our potential customers because
it gave them leverage over their existing ISDN chip supplier to lower their prices.

I remember semihosting to be very useful to observe various line state changes or to figure 
out when and why some echo cancellation filter was going off the rails.

*You're absolutely right to question the relevance of a 1995 ISDN chip in a 2021
blog post about semihosting, but it's just a wave of nostaligia crashing over me, and
it's not as if you can do anything about it.*

But the point is: ARM invented semihosting at least 26 years ago.

Let's have a look to the [ARM semihosting specification](https://developer.arm.com/documentation/100863/latest)
to see what it's really all about:

> Semihosting is a mechanism that enables code running on an ARM target or emulator 
> to communicate with and use the Input/Output facilities on a host computer. The host 
> must be running the emulator, or a debugger that is attached to the ARM target.

Semihosting is a powerful feature, because it can give a tiny embedded CPU that doesn't have any
generic IO capabilities to do things like accepting keystrokes, print out debug information to a debug
console, or even read and write from and to a file on the host PC.  It's up to the external debugger 
(OpenOCD in our case) to intercept semihosting operation request from embedded CPU and perform the requested action.

The performance of semihosting commands is subject to the bandwidth of the communication interface
by which the embedded CPU is connected to the host PC, so don't expect miracles here in the case of JTAG.

Despite having existed for so long, I'm not aware of any other CPU family that has support for 
semihosting (I definitely can't find anything in the OpenOCD source code), except for RISC-V. In their
discussion of the EBREAK instruction (section 2.8 of the RISC-V Instruction Set Manual), semihosting
is only mentioned as a large-ish footnote, but that's sufficient because other than defining the 
RISC-V specific semihosting function call semantics, RISC-V simply adopted the ARM semihosting specification.
Smart!

OpenOCD refactored the ARM semihosting support code into 
[`semihosting_common`](https://github.com/ntfreak/openocd/blob/master/src/target/semihosting_common.h) which
is CPU family agnostic, making it easy to add semihosting support to RISC-V targets. Both the
[official OpenOCD repo](https://github.com/ntfreak/openocd/blob/master/src/target/riscv/riscv_semihosting.c) and
the [custom OpenOCD version for the VexRiscv CPU](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L143-L150)
support semihosting.

# Semihosting Functionality

What exactly features does semihosting offer?

The spec defines 24 function calls that can be put in the following categories:

* Time keeping

    The embedded CPU can ask the host for a time reference in case it doesn't have one.
    Since communication usually happens over JTAG, the time accuracy won't be very high!

    `SYS_CLOCK`, `SYS_ELAPSED`, `SYS_TICKFREQ`, `SYS_TIME`

* File IO

    All kinds of transactions on files that live on the host PC file system.

    `SYS_OPEN`, `SYS_READ`, `SYS_CLOSE`, `SYS_FLEN`, `SYS_SEEK`, `SYS_WRITE`,
    `SYS_ISTTY`, `SYS_REMOVE`, `SYS_RENAME`, `SYS_TMPNAM`

* Console IO

    The console IO (also called the debug channel) is the equivalent of a UART or JTAG
    UART

    `SYS_READC`, `SYS_WRITEC`, `SYS_WRITE0`

* System commands

    Allow the embedded CPU to execute operating system commands on the host PC. Things like
    `pwd` or `mkdir`. Or even `/bin/rm -fr /`, because why not?

    `SYS_SYSTEM`

* Program control

    Some functions to pass command line parameters to the embedded firmware, or to feed back
    end of execution status and error conditions.

    `SYS_EXIT`, `SYS_EXIT_EXTENDED`, `SYS_GET_CMDLINE`

* Status

    Some functions to report back memory status of the embedded CPU or the status
    of earlier semihosting function calls.

    `SYS_HEAPINFO`, `SYS_ISERROR`, `SYS_ERRNO`

Each semihosting function call has a number that is defined in the specification. You can also 
look it up in the [OpenOCD source code](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/semihosting_common.h#L53-L76):

In case it wasn't obvious: when enabled, semihosting offers the embedded CPU
an almost unlimited supply of opportunities to kill the host PC. The only things that prevents
an embedded CPU from deleting all files on a file system are carefull permission management
of the debug server, so you may think twice about doing `sudo openocd` when you're having issues
the permissions of some JTAG device driver. (Guilty as charged!)

# Semihosting Under the Hood

So how does semihosting really work?

It's built on top of software breakpoints that are normally used to halt a CPU debugging:

* The semihosting call that runs on the embedded CPU has an EBREAK instruction
  that halts the CPU when a debugger is connected.
* The host PC polls the embedded CPU to check if the embedded CPU is halted.
* When a halt is detected, the host PC checks if the EBREAK is part of the following
  instruction sequence:

  ```
SLLI    x0, x0, 0x1f
EBREAK
SRAI    x0, x0, 0x07
  ```

  *The first and third instructions are dummies that don't do anything, because they use x0 as the 
  destination register, so this code sequence is not something would ever be  generated by a compiler.*

  Here's the 
  [instruction sequence detection code](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L853-L870)
  on the VexRiscv version of OpenOCD.

* If the sequence is detected, the debugger treats the EBREAK as a semihosting call. 

  The value of register *a0* contains semihosting sytem call (one of the SYS_* above), and register
  *a1* contains the system call parameter. 

  Semihosting calls can only pass 1 parameter through 
  a regiser. However, if multiple values need to be passed to the debugging host, the *a1*
  register will contain a pointer to data in the embedded CPU memory that contains these
  values. The debugging host can simply gets these values by issuing memory read commands
  through a normal memory access debug mechanism.

* The debugging host executes the required operation. 
* Upon completion, the debugging host stores the return value in register *a0*, unhalts the
  embedded CPU.


If the CPU was halted without seeing that semihosting instruction sequence then there must have been 
another reason for the halt. E.g. it might be caused by a regular software breakpoint, or
the firmware ran into some error condition and issued the EBREAK.

# Semihosting Library

The embedded CPU typically has a C library that wraps the semihosting calls into familiar C functions such 
as `printf`, `fclose()`, `putchar()` etc.


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


