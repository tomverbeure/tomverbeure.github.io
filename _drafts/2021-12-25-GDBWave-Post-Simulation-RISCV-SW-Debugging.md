---
layout: post
title: GDBWave - A Post-Simulation Waveform-Based RISC-V GDB Debugging Server
date:  2021-12-25 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction


A small soft core CPU is a great way to add control and management operations to your FPGA design. It's much
faster to iterate through different versions with some C code, and not needing to resynthesize is a big
time saver too (if [you know how to update RAM contents efficiently](/2021/04/25/Intel-FPGA-RAM-Bitstream-Patching.html).)
That's why almost all my hobby FPGA projects have a small [VexRiscv RISC-V CPU](https://github.com/SpinalHDL/VexRiscv).

I recently wrote about how to [connect GDB to a VexRiscv CPU](/2021/07/18/VexRiscv-OpenOCD-and-Traps.html) that's running 
on the actual hardware by adding a JTAG interface. You do something similar in simuation, by connecting
GDB to OpenOCD which talks to the simuluation over a simulated JTAG interface.  This blog post is not about that. 

Instead, I want to talk about simulating an RTL design that contains of soft CPU first, and then 
**debugging the firmware that runs on that soft CPU after the simulation has completed.**

I usually don't have a JTAG interface in my design: I'm often just too lazy to wire up a USB JTAG dongle 
to the FPGA board. But what I do all the time is to look at simulation waveforms and try to figure out what the 
CPU was doing at a particular point in the simulation. Or, the other way around, try to figure out what the hardware 
was doing when the CPU was executing a particular line of code.

My traditional workflow was a follows: 

* look at a waveform file
* find the region of interest
* check out the program counter (PC) of the VexRiscv CPU
* look up that program counter in a disassembled version of my C code

It's a tedious process and it's near impossible to get a bigger view of what's going on in the CPU: no
easy way to dump the contents of the program call stack, variables, registers etc.

I was wondering how others handled this kind of debugging and fired off 
[the following Tweet](https://twitter.com/tom_verbeure/status/1455905689365217286):

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Question: you are simulating a RISC-V CPU that is running a C program. You are recording a VCD (or FST) trace. How do you correlate between the instruction address in the waveform and the line of C code?</p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1455905689365217286?ref_src=twsrc%5Etfw">November 3, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

There were a number useful suggestions:

* Use the `addr2line`, part of the GCC toolchain, or `llvm-symbolizer` tools to translate the PC value straight 
  to the C source code file and line number.
* Expand the previous method by creating a GTKWave translate filter so that the file and line numbers
  are shown as a ASCII-encoded waveform in the waveform viewer itself.
* [Matthew Balance](https://twitter.com/bitsbytesgates) suggested a brilliant way to 
  [view the call stack in the waveform viewer](https://bitsbytesgates.blogspot.com/2021/01/soc-integration-testing-higher-level.html):
![Call stack in waveform viewer](/assets/gdbwave/call_stack.png)
* Tangentially related, somebody pointed out that the Quartus SignalTap has the option show the active
  assembler instruction of a Nios II soft CPU in the waveform. There was a time when I used Nios II CPUs
  a lot. This would definitely have been useful.
* [@whitequark](https://twitter.com/whitequark/status/1455918588502724613?s=20) suggested adding a GDB server
  to a CXXRTL simulation environment, which is a similar but more direct way of connecting GDB to a 
  live simulation through a simulated JTAG interface.

That last suggestion gave me the idea to **feed the waveform trace into a GDB server**:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Yes. But the end result of that is the same as using OpenOCD and jtag_vpi, right? How about a GDB server that reads in a VCD file?</p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1455919532506173442?ref_src=twsrc%5Etfw">November 3, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

This was considered a cursed idea, a high mark of approval indeed!

Two months later, the result is GDBWave: a post-simulation waveform-based RISC-V GDB debugging server.

# What is a GDB Server, and how to create one?

In my [VexRiscv, OpenOCD, and Traps](/2021/07/18/VexRiscv-OpenOCD-and-Traps.html) blog post, I showed 
all the steps between a debugger IDE and an actual CPU. Let's just say that for GDBWave the picture
is a little less complicated:

![Debug Flow - IDE to CPU Data Flow vs GDBWave Data Flow](/assets/gdbwave/gdbwave-ide_to_cpu_data_flow.svg)

In a remote debug environment, GDB uses the GDB Remote Serial Protocol (RSP) to talk to an external
entity that is linked to the device under test. This external entity can come in two forms: 

* a GDB remote stub

    A GDB remote stub (or GDB stub) is a piece of debug code that is linked to the program that you want to 
    debug. The stub is typically set up to be called when there's some kind of debug exception or trap, at 
    which point it takes over to start communication with the GDB.

    This is a common way to debug embedded systems that don't have an operating system and that don't have
    the ability to use hardware debugging features of the CPU. (E.g. because the JTAG port of the CPU isn't
    available on the PCB.)

    See the [GDB Remote Stub](https://sourceware.org/gdb/onlinedocs/gdb/Remote-Stub.html) section in the 
    GDB manual.

* a GDB server

    A GDB server is a separate program that is not linked to be part of the program that must be debugged.
    It can be an intermediate program like OpenOCD that converts RSP commands to JTAG commands, or it could
    be a separate prcoess that uses operating system features on the target machine to debug another program.

    On Unix systems, the system native GDB often comes standard with a `gdbserver`, which allows you debug
    your Unix program remotely.

    [Using the `gdbserver` Program](https://sourceware.org/gdb/onlinedocs/gdb/Server.html) has more about it.

From the point of view of the GDB client, both a GDB stub and a GDB server behave identical: their task is to 
receive high-level RSP requests such as "step", "continue", "read CPU registers", "write to memory", or 
"set breakpoint", adapt these request to the environment in which the CPU is operating, and return requested 
data (if any.) 

If you want to make GDB believe that your recorded CPU simulation waveform is an actually running CPU under 
debug, you need write your own GDB server:

* Create a socket and accept incoming connections.[^1]
* Parse the RSP protocol compliant requests from the client
* Fetch the requested data from the recorded trace
* Transform the data into an RSP conforming reply packet
* Send the reply back over the socket

There is quite a generic boilerplate in there, and there are tons of open source GDB stubs that you can 
modify to your taste.[^2]

I wanted to write GDBWave in C++ for a couple of reasons: the FST library, written in C, doesn’t have any 
bindings to popular scripting languages, but I also just wanted to get a taste of some of the new C++ features 
that have been added to language since I last used it, more than 15 years ago...

I settled on [mborgerson/gdbstub](https://github.com/mborgerson/gdbstub), a lightweight implementation that’s 
designed to make it easy to support your own CPU architecture. It’s so minimal that it doesn’t even support 
breakpoints, but those were very easy to add. 

# GDBWave in a Nutshell

The overall flow to use GDBWave is pretty straightforward:

![GDBWave overall flow](/assets/gdbwave/gdbwave-overall_flow.svg)

1. Simulate a design that contains an embedded soft core RISC-V CPU such as the VexRiscv.
1. During the simulation, dump the signals of the design to a waveform file.
1. Tell GDBWave which signals in the design can be used to extract a processor trace: the CPU program counter, 
   and, optionally, the contents of the CPU register file, and the transactions to memory.
1. Launch GDBWave as a GDB server that pretends to be a real running CPU system with debug capabilities.
1. Launch the standard RISC-V GDB debugger and connect to the GDBWave debug target
1. Issue GDB commands as if it were dealing with a real CPU: breakpoints, watchpoints, line stepping through the
   code, inspecting variables, you name it. You can even go back if time if you'd like.
1. Future bonus feature: link GDBWave to your GTKWave waveform viewer. When your GDBWave CPU hits a breakpoint, 
  automatically jump to that point in time in the waveform viewer!

Note that all of this is possible without the need of any hardware debugging features enabled in the simulated CPU: 
you can do this on a [picorv32](https://github.com/YosysHQ/picorv32) or the 
[award winning bit-serial SERV](https://github.com/olofk/serv)
RISC-V CPUs and it will still work. The only minimum requirement is that you can find the right signals
in the RTL and the waveform file to extract the program counter value of instructions that have
been successfully executed and retired.

There are some things that GDBWave won’t allow you to do:

* You can’t change the flow of the program that’s under debug. This is an obvious first principles consequence 
  of running a debugger on prerecorded data.
* GDBWave currently only works with CPUs that have a single instruction, in-order pipeline. It’s not difficult to 
  extend support for more complex CPU architectures, but that’s outside the scope of this Christmas holiday project.

*This blog post talks about processor traces that are extracted from simulation waveforms, but you can also 
gather this data from real hardware if the CPU system in your design has instruction tracing capabilities such as 
those described in the [RISC-V Processor Trace specification](https://riscv.org/technical/specifications/).*

# The FST Waveform Format

In the hobby world, almost everybody dumps simulation waveforms as VCD files, a format standardized in the
Verilog specification that is supported by nearly all simulation and digital design debugging tools in existence.
Except GDBWave, which doesn't support VCD directly.

There’s a good reason for that: being universally supported is about the only good characteristic of what is 
otherwise a terrible waveform format.

* VCD is disk space hog with little or no compression. 
* It requires you to read in the full file even if you want to extract the values of a signal out of thousands 
or more signals.
* You also can’t extract values for a give time range without first processing the values of 
all time steps before that. 

When you work for a company that can afford it, you're probably using Synopsys Verdi to debug digital designs.
Verdi comes with the FSDB waveform format which has none of the VCD disadvantages. Unfortunately, that format is 
proprietary and, to my knowledge, hasn’t been reverse engineered. If you want to write tools that extract data 
from FSDB files, you need to link a precompiled binary library that comes with the Verdi installation.

Luckily, there’s an open source alternative: the FST format was developed by Tony Bybell, the author of GTKWave. 
It fixes all the flaws of the VCD format. There is no formal specification of the FST file format, but 
["Implementation of an Efficient Method for Digital Waveform Compression"][1], a paper that is included
in the GTKWave manual, goes a long way to describe the design goals and how they were achieved.

Here are some of those features:

* Small file size

    In my example designs, FST files are roughly 50x smaller than equivalent VCD files. 

    This is because it uses a two-stage compression scheme: in the first stage, it encodes signal value changes 
    as delta values. I didn’t try to figure out the exact details from the source code (which has the same peculiar 
    coding standards as GTKWave), but it is supposedly based in the method described in this paper. 

    During the second stage, the output of the first stage is compressed by the standard LZ4 or GZIP method (or 
    it is bypassed.)

* Fast compression and decompression speed 

    Compression speed is very fast and slows down the simulation by a small amount compared to dumping a VCD file. 
    The FST library comes even with multi threading support, for very large designs that dump a lot of data, so that 
    multiple chunks can compressed in parallel. (Note that this is a bit slower on smaller cases. It’s only helpful 
    when you’re dumping hundreds of thousand of signals and more.)

* Fast opening of FST files

    You don't need to process the whole file before you can extract data from it.

* FST files are saved in multiple chunks 

    If you need to access data somewhere in the middle of a large simulation, it will only read in the chunks that 
    contain the desired data, and skip whatever came before. 

* FST files can be read while the database is still being written

    This is really useful if you are running a very long running simulation and you want to quickly
    check if everything is still behaving as planned. 

    This feature is direct consequence of data being written out in separate chunks.


The FST format isn’t perfect: 

* No formal format specification

    There is no formal format specification, and, based on [a discussion on the GTKWave GitHub
    project](https://github.com/gtkwave/gtkwave/issues/70#issuecomment-907984622), one shouldn't expect there to
    ever be one.  Other documentation only exists in the form of comments in the source code, or comments by the author 
    on other GitHub issues. 

* No FST library API documentation

    There is a library to read and write FST files, but there's no documentation on how to use it.
    You're expected to figure out how things work 
    [by checking out existing utilities](https://github.com/gtkwave/gtkwave/issues/70#issuecomment-902463200) that
    read and write FST files.

    In practice, I didn't find using it too hard, and I created 
    [`FstProcess`](https://github.com/tomverbeure/gdbwave/blob/main/src/FstProcess.cc), 
    a C++ class that has the limited functionality that I needed to extract data from an FST file.

* No stand-alone FST library 

    There's no stand-alone FST library with individual version tracking etc. You're supposed to
    [extract the code from the GTKWave source tree](https://github.com/gtkwave/gtkwave/tree/master/gtkwave3-gtk3/src/helpers/fst).

    Since the relevant code already lives in its own directory, extracting the code is not hard at all. But the lack of 
    versions makes it impossible to keep track of which 
    [bug fixes](https://github.com/gtkwave/gtkwave/commit/ee52b426351cb2a58af16b11bf401519ccba3ead#diff-5ceb02db973e525ddd64b68b28dcb4132a12d79ce7a4d083d756143f482a2109)
    been applied.

* No support for vectors with an LSB that is different than 0

    Inexplicably, FST doesn’t support vector signals that don’t start with bit 0: a vector that is defined as 
    `MySignal[31:2]` gets saved as `MySignal[29:0]`. This is not an issue for the vast majority of design, 
    but considering that it would take just 1 additional parameter in the signal declaration, this things
    annoys me way more that it should.

Still, the benefits far outweigh the disadvantages, especially if you're dealing with huge waveform
databases.

Verilator and Icarus Verilog support FST out of the box. GTKWave does too, of course.

If your simulation tool can't generate FST files, you can always use the `vcd2fst` conversion utility
that comes standard with GTKWave.

**If you're using the FST format as part of a Verilator testbench, make sure to NOT call the
`flush()` method on the `VerilatedFstC` trace object after each simulation cycle. I did this in one of
my testbenches and 
[my simulation speed dropped by a factor of 20](https://github.com/verilator/verilator/issues/3168#issuecomment-951476317)
compared to using VCD!**


# GDBWave Internals

Internally GDBWave is pretty straightforward. This is the simplified flow chart:

![GDBWave program flow](/assets/gdbwave/gdbwave-gdbwave_program_flow.svg)

**Reading the FST waveform**

As mentioned earlier, I created [`FstProcess`](https://github.com/tomverbeure/gdbwave/blob/main/src/FstProcess.cc), 
a thin C++ wrapper around the native GTKWave `fstapi.h` library.

**Program Counter Extraction**

At the very minimum, GDBWave needs to know which instructions have been successfully executed by the CPU.
It does so by tracking the program counter.

In the case of the VexRiscv, I use 2 signals that are present in all VexRiscv configurations:

* `lastStagePc[31:0]` 
* `lastStageIsValid` 

When `lastStageIsValid` is asserted, `lastStagePc` contains the program counter value of an instruction that has 
completed execution. Perfect!

The code to extract the program counter is very simple.

First, I [save the most up-to-date value of these 2 signals](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/CpuTrace.cc#L25-L33) 
as I march through the waveform database:

```verilog
    if (signal->handle == cpuTrace->pcValid.handle){
        cpuTrace->curPcValidVal   = valueInt;
        return;
    }

    if (signal->handle == cpuTrace->pc.handle){
        cpuTrace->curPcVal    = valueInt;
        return;
    }
```

Second, when I see a falling edge of the clock, 
[I record the program counter if the `valid` signal is asserted](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/CpuTrace.cc#L35-L43).
All program counter values are stored in a vector array, along with the time stamp at which they changed.

```verilog
    if (signal->handle == cpuTrace->clk.handle && valueInt == 0){
        if (cpuTrace->curPcValidVal){
            PcValue     pc = { time, cpuTrace->curPcVal };
            cpuTrace->pcTrace.push_back(pc);
        }
    }
```

Why the falling edge of the clock? Because in a clean, synchronous design, all regular signals change at the rising edge 
of the clock. You can be certain that all signals will be stationary at the falling edge, and you don't have to
worry about whether or not the clock was rising immediately before or after a functional signal changed. It just
makes things less error prone.

**Extracting Register File Writes**

Knowledge of CPU register file contents is essential if you want to track the value of local variables
that are never stored to memory. For example, chances are very high the that counter variable of tight `for` 
loop only ever lives in a CPU register.

To know the state of the register file, it's sufficient to record only the writes to it, as long as
you know the initial state of the full register file at the start of the simulation. But even
not knowing the initial state is usually not a big deal, because most CPU startup code will initialize,
and thus write to, its registers with the appropriate value.

For a VexRiscv CPU, the relevant signals to observe are: 

* `lastStageRegFileWrite_valid`
* `lastStageRegFileWrite_payload_address`
* `lastStageRegFileWrite_payload_data`

The [code](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/RegFileTrace.cc#L21-L52) to
extract register file writes from the FST waveform is as straightforward as the one to extract
program counter changes.

**Extracting CPU Memory Writes**

Finally, there's the knowledge of the RAM contents on which the CPU operates. GDB issues memory reads for 
a couple of reasons: to know the value of variables that are stored in RAM, to inspect the call stack of a
running program, and to disassemble the code that it is debugging.

Memory contents can also be derived from the writes to memory, but, contrary to the register file, it's 
really important to know the initial state of the RAM as well. That's because the FPGA RAM that's used to
store the CPU instructions is usually preloaded after powering up and never written. 

For the VexRiscv, write operations can be extracted by observing the following signals:

* `dBus_cmd_valid`
* `dBus_cmd_ready`
* `dBus_cmd_payload_address`
* `dBus_cmd_payload_size`
* `dBus_cmd_payload_wr`
* `dBus_cmd_payload_data`

The code to extract the write operations can be found 
[here](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/MemTrace.cc#L40-L108).

To get the initial state of the RAM, my firmware `Makefile` 
[creates a binary file](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/test_data/sw_semihosting/Makefile#L56-L57)
with the contents of the RAM:

```makefile
progmem.bin: progmem.elf
	$(OBJCOPY) -O binary $< $@
``` 

This file is 
[read directly by the `MemTrace` object](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/MemTrace.cc#L113-L117):

```c++
    if (!memInitFilename.empty()){
        printf("Loading mem init file: %s\n", memInitFilename.c_str());
        ifstream initFile(memInitFilename, ios::in | ios::binary);
        memInitContents = vector<char>((std::istreambuf_iterator<char>(initFile)), std::istreambuf_iterator<char>());
    }
```

In the future, I might extend GDBWave to read ELF files directly, but the current method works fine too.

Note that it's also possible to figure out the contents of the program RAM iteratively, by observing
read transactions on the CPU instruction fetch bus. The only problem is that you can't disassemble sections
that have never been executed by the CPU. In practice, I don't think this would be a major issue:
looking at the low level assembly code in GDB isn't something I do very often, especially for code that never 
gets executed. Still, most of the time you'll have access to a program binary file, so I didn't go through the 
trouble, yet, to look at the instruction read transactions...

**Processing generic GDB RSP requests**





# GDBWave and the picorv32

# GDBWave and the award-winning SERV


# References

**Waveform Formats**

* [GTKWave User's Guide - Appendix F: Implementation of an Efficient Method for Digital Waveform Compression][1]

* [A novel approach for digital waveform compression](https://www.researchgate.net/publication/234793005_A_novel_approach_for_digital_waveform_compression/link/5462239b0cf2cb7e9da643c0/download)



**Open source GDB stubs**

* [mborgerson/gdbstub - A simple, dependency-free GDB stub that can be easily dropped in to your project](https://github.com/mborgerson/gdbstub)

    > A simple, dependency-free GDB stub that can be easily dropped in to your project. 

    GDBWave is based on this one.

* [bluespec/RISCV_gdbstub](https://github.com/bluespec/RISCV_gdbstub)

    > A gdbstub for connecting GDB to a RISC-V Debug Module.

* [daniel5151/gdbstub](https://github.com/daniel5151/gdbstub)

    > An ergonomic and easy-to-integrate implementation of the GDB Remote Serial Protocol in 
    > Rust, with full no_std support. 

* [avatarone/avatar-gdbstub](https://github.com/avatarone/avatar-gdbstub)

    > GDB stub that allows debugging of embedded devices.

**Open source GDB servers**

* [UoS-EEC/gdb-server](https://github.com/UoS-EEC/gdb-server)

    > GDB server implemented as a library in C++. To be hooked up to simulation/emulation targets.

* [bet4it/gdbserver](https://github.com/bet4it/gdbserver)

    > A tiny debugger implement the GDB Remote Serial Protocol. Can work on i386, x86_64, ARM and PowerPC.

* [embecosm/riscv-gdbserver](https://github.com/embecosm/riscv-gdbserver)

    > GDB Server for interacting with RISC-V models, boards and FPGAs

    Way too elaborate for what I needed.


**Various**

* [Debug memory errors with Valgrind and GDB](https://developers.redhat.com/articles/2021/11/01/debug-memory-errors-valgrind-and-gdb#using_valgrind_and_gdb_together)

    Not directly related to GDBWave, but it showed me how GDB can link to a remote target list this:
    `target remote | /usr/local/lib/valgrind/../../bin/vgdb`, which removes the requirement to first
    start GDBWave as a separate program.


# Footnotes

[^1]: A GDB stub doesn't have to communicate with GDB over a TCP/IP socket. A good counter example is the GDB
      version that you use to debug programs that run natively on your PC. But GDB also natively supports
      serial ports to communicate with a GDB stub. Check out the 
      [Connecting to a Remote Target](https://sourceware.org/gdb/onlinedocs/gdb/Connecting.html)
      section of the GDB manual for more.

[^2]: If you're wondering why I used a GDB stub instead of a GDB server as basis for GDBWave, it's because
      I only figured out the difference between a stub and a server well after I started writing this blog post, when
      almost all coding on GDBWave was complete. If I could redo everything from scratch, I'd probably use 
      [UoS-EEC/gdb-server](https://github.com/UoS-EEC/gdb-server).



[1]: /assets/gdbwave/gtkwave_manual.pdf#page=137


