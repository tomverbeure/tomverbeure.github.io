---
layout: post
title: Semihosting, a PC as Terminal and File Server for Your Embedded CPU
date:  2021-07-18 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Regular readers of my blog posts should know by now that I'm a big fan of adding a small
embedded CPU in my FPGA projects for overall management, 
[bit-banging](https://en.wikipedia.org/wiki/Bit_banging) slow protocols
such as [I2C](https://en.wikipedia.org/wiki/I²C), and some real-time operations with not too
stringent timing requirements. They'll also know that the 
[VexRiscv](https://github.com/SpinalHDL/VexRiscv) is the standard soft-core CPU in my
toolbox.

When running code on an embedded CPU, it's very often helpful to have an interface to a
PC to run some kind of console or terminal for control, debugging, and logging. A UART is obviously
very popular for this, but I often also use a [JTAG UART](2021/05/02/Intel-JTAG-UART.html), 
which can be easier to integrate if you already have a JTAG connection to for FPGA for 
other reasons.

But there's another option that many probably have never heard about. Instead of using
a dedicated HW block, it leverages the existing debug infrastructure of the CPU by adding a
peculiar software layer on top of the low level debug driver. 

It's called semihosting, and it allows the embedded CPU use the host PC as a server
for a variety of functions: STDIO read and write, access to the PC file system, time 
server etc.

Semihosting is definitely a bit of a hack, but it's a clever one, and I think there's 
something magical about a slow embedded CPU with 4KB of RAM commandeering a mighty
PC into reading and writing files on its file system.

# Semihosting and RISC-V

Semihosting is nothing new: I first used it in 1995 on a prehistoric ARM7TDMI CPU
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

The point is: ARM invented semihosting at least 26 years ago.

Let's have a look to the [ARM semihosting specification](https://developer.arm.com/documentation/100863/latest)
to see what it's really all about:

> Semihosting is a mechanism that enables code running on an ARM target or emulator 
> to communicate with and use the Input/Output facilities on a host computer. The host 
> must be running the emulator, or a debugger that is attached to the ARM target.

Semihosting is a powerful feature, because it can give a tiny embedded CPU that doesn't have any
generic IO capabilities to do things like accepting keystrokes, print out debug information to a debug
console, or even read and write from and to a file on the host PC.  It's up to the external debugger 
(OpenOCD in our case) to intercept a semihosting operation request from embedded CPU and perform the requested action.

The performance of semihosting commands is subject to the bandwidth of the communication interface
by which the embedded CPU is connected to the host PC. Most of the time, this will be JTAG,
so don't expect miracles!

Despite having existed for so long, I'm not aware of any other CPU family that has support for 
semihosting (I definitely can't find anything in the OpenOCD source code), except for RISC-V. In their
discussion of the EBREAK instruction (section 2.8 of the RISC-V Instruction Set Manual), semihosting
is only mentioned as a large-ish footnote, but that's sufficient because other than defining the 
RISC-V specific semihosting function call semantics, RISC-V simply adopted the ARM semihosting specification.
Smart!

![RISC-V specification section about semihosting](/assets/semihosting/riscv_specification_semihosting.png)

OpenOCD refactored the CPU agnostic part of the ARM semihosting support code into 
[`semihosting_common`](https://github.com/ntfreak/openocd/blob/master/src/target/semihosting_common.h),
making it easy to add semihosting support to RISC-V targets. Both the
[official OpenOCD repo](https://github.com/ntfreak/openocd/blob/master/src/target/riscv/riscv_semihosting.c) and
the [custom OpenOCD version for the VexRiscv CPU](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L143-L150)
support semihosting on RISC-V CPUs.

# System call overview

Exactly what kind of features does semihosting offer?

The spec defines 24 function calls that can be grouped in the following categories:

| Category | Calls | Description |
|----------|-------|------------|
| Time keeping | `SYS_CLOCK`  `SYS_ELAPSED`  `SYS_TICKFREQ`  `SYS_TIME` | The embedded CPU can ask the host for a time reference in case it doesn't have one.  Since communication usually happens over JTAG, the time accuracy won't be very high. |
|File IO | `SYS_OPEN`, `SYS_READ`, `SYS_CLOSE`, `SYS_FLEN`, `SYS_SEEK`, `SYS_WRITE`, `SYS_ISTTY`, `SYS_REMOVE`, `SYS_RENAME`, `SYS_TMPNAM` | All kinds of transactions on files that live on the host PC file system. | 
| Console IO | `SYS_READC`, `SYS_WRITEC`, `SYS_WRITE0` | The console IO (also called the debug channel) is the equivalent of a UART or JTAG UART. |
| System commands | `SYS_SYSTEM` | Allow the embedded CPU to execute operating system commands on the host PC. Things like `pwd` or `mkdir`. Or even `/bin/rm -fr /`, because why not? | 
| Program control and status | `SYS_EXIT`, `SYS_EXIT_EXTENDED`, `SYS_GET_CMDLINE` | Some functions to pass command line parameters to the embedded firmware, or to feed back-end with execution status and error conditions. |
| Status | `SYS_HEAPINFO`, `SYS_ISERROR`, `SYS_ERRNO` | Some functions to report back memory status of the embedded CPU or the status of earlier semihosting function calls. |


The specification assigns a 
[unique number](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/semihosting_common.h#L53-L76)
to each semihosting function call. 

In case it wasn't obvious: when enabled and left unchecked, semihosting offers the embedded CPU
an almost unlimited supply of opportunities to kill the host PC. The only things that prevent
an embedded CPU from deleting all files on a file system are carefull permission management
of the debug server and the `arm semihosting enable` command in OpenOCD.

# Under the hood

So how does semihosting work?

It's built on top of the software breakpoint mechanism that is traditionally used to halt a CPU while debugging:

1. The semihosting call that runs on the embedded CPU has a RISC-V EBREAK instruction
  that halts the CPU when a debugger is connected.
1. The host PC continuously polls the embedded CPU to check if it is halted.
1. When a halt is detected, the host PC checks if the EBREAK instruction is part of the following
  magic instruction sequence:

    ```
SLLI    x0, x0, 0x1f
EBREAK
SRAI    x0, x0, 0x07
    ```

    *The first and third instructions are dummies that don't do anything, because they use x0 as the 
    destination register. No sane compiler would ever generate this code sequence.*

    Here's the 
    [instruction sequence detection code](https://github.com/SpinalHDL/openocd_riscv/blob/f8c1c8ad9cd844a068a749532cfbc369e66a18f9/src/target/vexriscv.c#L853-L870)
    on the VexRiscv version of OpenOCD.

1. If the sequence is detected, the debugger treats the EBREAK as a semihosting call. 

    The value of register `a0` contains the semihosting system call number (one of the `SYS_` functions above), and register
    `a1` contains the system call parameter. 

    Semihosting calls can only pass 1 parameter through a register. For system calls that need to pass
    multiple pieces of data to the debugging host, the `a1` register is a pointer to a struct, located
    in the embedded CPU data memory, with further information.
    The debugging host gets the contents of the struct by issuing memory read commands with the same mechanism 
    that's normally used to access memory during regular debugging operations.

1. The debugging host, OpenOCD, executes the requested semihosting system call.
1. Upon completion, the debugging host stores the return value in register *a0*. 
1. The debugging host unhalts the embedded CPU. 

If the embedded CPU was halted without seeing the magic semihosting instruction sequence, then there 
must have been another reason for the halt: it might be caused by a regular software breakpoint, or
the firmware ran into some error condition and issued the EBREAK.

# Adding basic semihosting support to your program

Let's look at the practical aspects of adding semihosting to your program.

You need the magic sequence to trigger a semihosting call on in the debugger:

```c
static inline int __attribute__ ((always_inline)) call_host(int reason, void* arg) {
    register int value asm ("a0") = reason;
    register void* ptr asm ("a1") = arg;
    asm volatile (
        " .option push \n"
        // Force non-compressed RISC-V instructions
        " .option norvc \n"
        // Force 16-byte alignment to make sure that the 3 instructions fall
        // within the same virtual page. 
        // Note: align 4 means, align by 2 to the power of 4!
        " .align 4 \n"
        " slli x0, x0, 0x1f \n"
        " ebreak \n"
        " srai x0, x0, %[swi] \n"
        " .option pop \n"

        : "=r" (value) /* Outputs */
        : "0" (value), "r" (ptr), [swi] "i" (RISCV_SEMIHOSTING_CALL_NUMBER) /* Inputs */
        : "memory" /* Clobbers */
    );
    return value;
}
```

The code looks a bit gnarly, but it's really not too bad:

* The `reason` and `arg` parameters are forced into registers `a0` and `a1`.
* RISC-V compressed instructions are disabled to make sure that nobody converts the magic sequences
  into something different.
* The magic sequence is forced to reside inside a single page to prevent a page fault in the middle of
  the semihosting magic sequence.
* The magic sequence itself.
* The return value is forced inside a register.

There is some weird monkey business with the `swi` variable set to 7 that I don't quite understand, but
the end result of it is that the `srai x0, x0, 7` instruction gets generated and in the end that all
that matters.

With that in place, issuing specific semihosting calls is trivial:

```c
void sh_write0(const char* buf)
{
    // Print zero-terminated string
    call_host(SEMIHOSTING_SYS_WRITE0, (void*) buf);
}

void sh_writec(char c)
{
    // Print single character
    call_host(SEMIHOSTING_SYS_WRITEC, (void*)&c);
}

char sh_readc(void)
{
    // Read character from keyboard. (Blocking operation!)
    return call_host(SEMIHOSTING_SYS_READC, (void*)NULL);
}
```

The embedded CPU typically has a C library that wraps the semihosting calls into familiar C functions such 
as `printf()`, `fclose()`, `putchar()` etc.,

There is usually no need to implement all semihosting function calls in that embedded CPU library: in many cases, 
print related functions are be sufficient to output debug messages. Add a variant of `getchar()` and 
there's enough for a simple embedded terminal.

# Avoiding hangs when a debugger is not connected

We've seen that a semihosting system call gets issued by executing an EBREAK instruction,
followed by the debugger detecting a magic instruction sequence, performing the requested
action, and then letting the CPU to continue.

![EBREAK handling flow diagram without recovery](/assets/semihosting/Semihosting-EBREAK_handling_flow_no_recovery.svg)

There's a potential problem with that: an EBREAK is not something that's expected in a normal RISC-V program. In the
words of the RISC-V specification:

> EBREAK was primarily designed to be used by a debugger to cause execution to stop and fall back into the
> debugger. EBREAK is also used by the standard gcc compiler to mark code paths that should not be executed.

If a RISC-V CPU issues an EBREAK instruction, and a debugger is connected, CPU halts and it's up to the debugging 
host to deal with it. But when a debugger is not connected, the CPU issues a trap. When your code is not
expecting EBREAK-induced traps, chances are that the trap will just get into an endless loop, which 
hangs your program.

In other words: **running a program that issues semihosting calls when a debugger is not connected will result in a
hang!**

This is a well known behavior of using semihosting, and you can find plenty of cases where people
[complain](https://www.openstm32.org/forumthread2323) about 
[this behavior](https://stackoverflow.com/questions/16396067/bpkt-arm-instruction-freezes-my-embedded-application).

The general solution is to have a debug version of your program where semihosting is enabled, and a release
version where it's disabled.

But is that really the best we can do?

The answer is no: remember that the CPU jumps to a trap handler when a debugger is not connected. We can
add recovery code in the trap handler that detects that there was a semihosting call, ignore the call, and
return back to the regular program.

You need to be a bit careful because the code that made the semihosting call may expect not expect
that the call didn't go through.  For example, the `SYS_READC` call that's used to read a character from host
PC keyboard expects that a character is returned. You could return a value of -1 to indicate that the 
call didn't go through.

![EBREAK handling flow diagram with recovery](/assets/semihosting/Semihosting-EBREAK_handling_flow_with_recovery.svg)

Note that there is one case left when the CPU can still hang: if you first connect the debugger, the
CPU will be configured to halt upon seeing an EBREAK. If you then disconnect the debugger, e.g. by
unplugging the JTAG cable, the CPU will still halt when seeing an EBREAK, but there won't be any
debugger to deal with it.

# When does a CPU hang and when does it trap when seeing an EBREAK?

While working on this blog post, I wondered about the mechanism that determines whether the CPU traps
or halts upon seeing the EBREAK. Luke Wren 
[pointed me in the right direction](https://twitter.com/wren6991/status/1417042819877941251?s=20).

In the case of a RISC-V CPU that follows the official RISC-V Debug specification, the Debug Module (DM)
has a Debug Control and Status (dcsr) register with `ebreakm`, `ebreaks`, and `ebreaku` 
configuration registers. When set to 1, the CPU will enter "Debug Mode" upon seeing an EBREAK instruction.
The spec says that "Debug Mode is a special processor mode used only when a hart is halted for 
external debugging."

![DCSR.EBREAKx fields](/assets/semihosting/dcsr_ebreak.png)

In practice, when the CPU powers up, its `ebreak` debug configuration bits are set to 0, and the 
CPU will trap. But when a debugger such as OpenOCD gets connected to the CPU, it will program the value of 
the `ebreak` configuration bits to 1, and the CPU will halt. When you cleanly exit the debugger, 
you can expect that the configuration bits are set back to 0, but if you unplug the JTAG cable
in the middle of a debugging sessions, that's obviously not going to happen. So don't do that.

The VexRiscv CPU doesn't implement the RISC-V debug specification, but it's behavior is similar:
there is no programmable configuration bit in the debug hardware, but as soon as the debug
hardware detects debug related operations, an internal bit is toggled that will make the CPU
halt on seeing an EBREAK instruction. However, there is no way to reset the EBREAK behavior
back to trap mode.

# Trap Handler

Things may be harder for more complex system calls, what exactly should a `SYS_TICKFREQ` return
when there's no time reference, but, in practice, these kind of semihosting calls are
rarely used.

An example implementation looks like this 
[`trap()` function](https://github.com/tomverbeure/vexriscv_ocd_blog/blob/ee36fe568bbfa443ca972c147662b8fd7a84d7e9/sw_semihosting/trap.c#L15)

```c

```


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

* [What is Semihosting?](https://community.nxp.com/t5/LPCXpresso-IDE-FAQs/What-is-Semihosting/m-p/475390)
 
* [Official RISC-V OpenOCD semihosting code](https://github.com/riscv/riscv-openocd/blob/riscv/src/target/riscv/riscv_semihosting.c)
* [Embedded printf](https://github.com/mpaland/printf)

* [EBREAKM option](https://twitter.com/wren6991/status/1417042819877941251?s=20)


