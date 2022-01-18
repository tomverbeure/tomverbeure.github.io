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
faster to iterate through different versions with some C code, and not needing to resynthesize can be a big
time saver too (if you know [how to update RAM contents efficiently](/2021/04/25/Intel-FPGA-RAM-Bitstream-Patching.html).)
That's why almost all my hobby FPGA projects have a small [VexRiscv RISC-V CPU](https://github.com/SpinalHDL/VexRiscv).

I recently wrote about how to [connect GDB to a VexRiscv CPU](/2021/07/18/VexRiscv-OpenOCD-and-Traps.html) that's running 
on the actual hardware by adding a JTAG interface. You can do something similar in simuation, by connecting
GDB to OpenOCD which talks to the simulation over a faked JTAG interface.  This blog post is not about that. 

Instead, I want to talk about simulating an RTL design that contains of soft CPU first, and then 
debugging the firmware that runs on that soft CPU **after the simulation has completed.**

I usually don't have a JTAG interface in my design: I'm often just too lazy to wire up a USB JTAG dongle 
to the FPGA board. But what I do all the time is to look at simulation waveforms and try to figure out what the 
CPU was doing at a particular point in the simulation. Or, the other way around, I try to figure out what the hardware 
was doing when the CPU was executing a particular line of code.

My traditional workflow was a follows: 

* look at a waveform file
* find the region of interest
* read the program counter (PC) of the VexRiscv CPU from the waveform
* look up that program counter in a disassembled version of my C code

It's a tedious process and it's near impossible to get a bigger view of what's going on in the CPU because there's no
easy way to dump the contents of the program call stack, variables, registers etc.

I was wondering how others handled this kind of debugging and fired off 
[the following Tweet](https://twitter.com/tom_verbeure/status/1455905689365217286):

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Question: you are simulating a RISC-V CPU that is running a C program. You are recording a VCD (or FST) trace. How do you correlate between the instruction address in the waveform and the line of C code?</p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1455905689365217286?ref_src=twsrc%5Etfw">November 3, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

There were a number useful suggestions:

* Use `addr2line`, part of the GCC toolchain, or `llvm-symbolizer` to translate the PC value straight 
  to the C source code file and line numberin-circuit .
* Expand the previous method by creating a GTKWave translate filter so that the file and line numbers
  are shown as a ASCII-encoded waveform in the waveform viewer itself.
* [Matthew Balance](https://twitter.com/bitsbytesgates) suggested a brilliant way to 
  [view the call stack in the waveform viewer](https://bitsbytesgates.blogspot.com/2021/01/soc-integration-testing-higher-level.html):
![Call stack in waveform viewer](/assets/gdbwave/call_stack.png)
* Somebody pointed out that Quartus' SignalTap has the option to show the active assembler instruction 
  of a Nios II soft CPU in the waveform. This would definitely have been useful back when I was using Nios CPUs. 
  It's also something that can be done for RISC-V CPUs with a translate filter, but it's not exactly 
  what I was looking for.
* [@whitequark](https://twitter.com/whitequark/status/1455918588502724613?s=20) suggested adding a GDB server
  to a CXXRTL simulation environment. This is a variant of connecting GDB to a live simulation through a 
  simulated JTAG interface, but it still requires an interactive session

That last suggestion gave me the idea to **feed the waveform trace into a GDB server**:

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Yes. But the end result of that is the same as using OpenOCD and jtag_vpi, right? How about a GDB server that reads in a VCD file?</p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1455919532506173442?ref_src=twsrc%5Etfw">November 3, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script> 

This was considered a cursed idea, a high mark of approval indeed!

Two months later, the result is GDBWave: a post-simulation waveform-based RISC-V GDB debugging server.

# What is a GDB Server, and how to create one?

In my [VexRiscv, OpenOCD, and Traps](/2021/07/18/VexRiscv-OpenOCD-and-Traps.html) blog post, I showed 
all the steps between a debugger IDE and an actual CPU. Let's just say that for GDBWave the picture
is less complicated:

![Debug Flow - IDE to CPU Data Flow vs GDBWave Data Flow](/assets/gdbwave/gdbwave-ide_to_cpu_data_flow.svg)

In a remote debug environment, GDB uses the GDB Remote Serial Protocol (RSP) to talk to an external
entity that is linked to the device under test. This external entity can come in two forms: 

* a GDB remote stub

    A GDB remote stub (or GDB stub) is a piece of debug code that is linked to the program that you want to 
    debug. The stub is usually  called when there's some kind of debug exception, interrupt, or trap, at 
    which point it takes over and starts communication with GDB.

    This is a common way to debug embedded systems that don't have an operating system and that don't have
    the ability to use hardware in-circuit debugging features of the CPU. (E.g. because the JTAG port of the CPU isn't
    available on the PCB.)

    See the [GDB Remote Stub](https://sourceware.org/gdb/onlinedocs/gdb/Remote-Stub.html) section in the 
    GDB manual.

* a GDB server

    A GDB server is a separate program that is not linked to be part of the program that must be debugged.
    It can be an intermediate program like OpenOCD that converts RSP commands to JTAG commands to control
    the hardware in-circuit debugging logic of the CPU, or it could be a separate process that uses operating 
    system features on the target machine to debug another program. At good example of the latter is the
    [ptrace](https://en.wikipedia.org/wiki/Ptrace) functionality in Unix-type operating systems. On these systems, 
    the system native GDB often comes standard with a `gdbserver`, which allows you to debug your Unix program 
    remotely.

    [Using the `gdbserver` Program](https://sourceware.org/gdb/onlinedocs/gdb/Server.html) has more about it.

From the point of view of the GDB client, a GDB stub and a GDB server behave identical: they 
receive high-level RSP requests such as "step", "continue", "read CPU registers", "write to memory", or 
"set breakpoint", adapt these requests to the environment in which the CPU is operating, and return requested 
data , if any. 

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
1. During the simulation, dump signals of the design to a waveform file. 
1. Tell GDBWave which signals in the design can be used to extract a processor state: the CPU program counter, 
   and, optionally, the contents of the CPU register file, and the transactions to memory.
1. Launch GDBWave as a GDB server that pretends to be a real running CPU system with debug capabilities.
1. Launch the standard RISC-V GDB debugger and connect to the GDBWave debug target
1. Issue GDB commands as if it were dealing with a real CPU: breakpoints, watchpoints, line stepping through the
   code, inspecting variables, you name it. You can even go back in time if you like.
1. Future bonus feature: link GDBWave to your GTKWave waveform viewer. When your GDBWave CPU hits a breakpoint, 
  automatically jump to that point in time in the waveform viewer!

Note that all of this is possible without the need of any hardware debugging features enabled in the simulated CPU: 
you can do this on a [picorv32](https://github.com/YosysHQ/picorv32) or the 
[award winning bit-serial SERV](https://github.com/olofk/serv)
RISC-V CPUs and it will still work. The only minimum requirement is that you can find the right signals
in the RTL and in the waveform file to extract the program counter value of instructions that have
been successfully executed and retired.[^3]

There are some things that GDBWave won’t allow you to do:

* You can’t change the flow of the program that’s under debug. This is an obvious first principles consequence 
  of running a debugger on prerecorded data.
* GDBWave currently only works with CPUs that have a single instruction, in-order execution pipeline. It's not 
  difficult to extend GDBWave support to more complex CPU architectures, but that's outside the scope of this 
  Christmas holiday project.

*This blog post talks about processor traces that are extracted from simulation waveforms, but you can also 
gather this data from real hardware if the CPU system in your design has instruction tracing capabilities such as 
those described in the [RISC-V Processor Trace specification](https://riscv.org/technical/specifications/).*

# The FST Waveform Format

In the hobby world, almost everybody dumps simulation waveforms as VCD files, a format standardized in the
Verilog specification that is supported by nearly all simulation and digital design debugging tools in existence.
GDBWave, however, doesn't support VCD directly.

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
in the GTKWave manual, goes a long way to describe the design goals and how they were achieved:

* Small file size

    In my example designs, FST files are roughly 50x smaller than equivalent VCD files. 

    This is because it uses a two-stage compression scheme: in the first stage, it encodes signal value changes 
    as delta values. During an optional second stage, the output of the first stage is compressed by the standard LZ4 or 
    GZIP method. 

* FST files are saved in multiple chunks 

    If you need to access data somewhere in the middle of a large simulation, it will only read in the chunks that 
    contain the desired data, and skip whatever came before. 

* Fast compression and decompression speed 

    Compression speed is very fast and slows the simulation down by only a small amount compared to dumping a VCD file. 
    The FST library comes even with multi-threading support. For very large designs that dump a lot of data,
    multiple chunks can compressed in parallel on different CPU cores. (Note that this is a bit slower on smaller cases. 
    It’s only helpful when you’re dumping hundreds of thousand of signals and more.)

* Fast opening of FST files

    You don't need to process the whole file before you can extract data from it.

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

    In practice, it wasn't too hard. I created 
    [`FstProcess`](https://github.com/tomverbeure/gdbwave/blob/main/src/FstProcess.cc), 
    a C++ class that has the limited functionality that I need to extract data from an FST file.

* No stand-alone FST library 

    There's no stand-alone FST library with individual version tracking etc. You're supposed to
    [extract the code from the GTKWave source tree](https://github.com/gtkwave/gtkwave/tree/master/gtkwave3-gtk3/src/helpers/fst).

    Since the relevant code already lives in its own directory, extracting the code is easy. But the lack of 
    versions makes it impossible to keep track of which 
    [bug fixes](https://github.com/gtkwave/gtkwave/commit/ee52b426351cb2a58af16b11bf401519ccba3ead#diff-5ceb02db973e525ddd64b68b28dcb4132a12d79ce7a4d083d756143f482a2109)
    been applied.

* No support for vectors with an LSB that is different than 0

    Inexplicably, FST doesn’t support vector signals that don’t start with bit 0: a vector that is defined as 
    `MySignal[31:2]` gets saved as `MySignal[29:0]`. This is not an issue for the vast majority of designs, 
    but considering that it would take just 1 additional parameter in the signal declaration, this omission
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

*This section goes into some of the implementation aspects of GDBWave. Some of this is for my own use so that
I don't forget why things were done a certain way. You can safely skip this if all you're interested in is using GDBWave 
for your own projects.*

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
of the clock and you can be certain that all signals will be stationary at the falling edge. You don't have to
worry about whether or not the clock was rising immediately before or after a functional signal changed. It just
makes things less error prone.

**Extracting Register File Writes**

Knowledge of CPU register file contents is essential if you want to track the value of local variables
that are never stored to memory. For example, chances are very high that the counter variable of a tight `for` 
loop only ever lives in a CPU register.

To know the state of the register file, it's sufficient to record only the writes to it, as long as
you know the initial state of the full register file at the start of the simulation. But even
not knowing the initial state is usually not a big deal, because most CPU startup code will initialize
its registers by writing an appropriate value.

For a VexRiscv CPU, the signals to observe are: 

* `lastStageRegFileWrite_valid`
* `lastStageRegFileWrite_payload_address`
* `lastStageRegFileWrite_payload_data`

The [code](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/RegFileTrace.cc#L21-L52) to
extract register file writes from the FST waveform is as straightforward as the one to extract
program counter changes.
https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub.cc#L1071-L1078
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
[read directly by the `MemTrace` object](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/MemTrace.cc#L113-L117)[^4]:

```c++
    if (!memInitFilename.empty()){
        printf("Loading mem init file: %s\n", memInitFilename.c_str());
        ifstream initFile(memInitFilename, ios::in | ios::binary);
        memInitContents = vector<char>((std::istreambuf_iterator<char>(initFile)), std::istreambuf_iterator<char>());
    }
```

In the future, I might extend GDBWave to read ELF files directly, but the current method works fine too.

Note that it's also possible to figure out the contents of the program RAM iteratively by observing
read transactions on the CPU instruction fetch bus. The only problem is that you can't disassemble sections
that have never been executed by the CPU. In practice, I don't think this would be a major issue:
looking at the low level assembly code in GDB isn't something I do very often, especially for code that never 
gets executed. Still, most of the time you'll have access to a program binary file, so I didn't go through the 
trouble, yet, to look at the instruction read transactions...

**Being a GDB server**

Once all the necessary data has been extacted, GDBWave can act like GDB server.

As soon as a TCP/IP connection with the GDB client has been established, the server sends a signal RSP packet to 
inform the client about the current execution state of the CPU. In GDBWave, that execution state is HALT. After
that, it enters an endless loop where it waits for RSP commands, and executes them as they arrive.

Many RSP commands are optional and not implemented. GDBWave only implements:

* `s` to execute/step a single assembler instruction on the CPU

    In GDB the "step" command moves to the next C instruction. In the RSP protocol, it executes just 1
    assembler instruction.

    Executing an instruction in GDB wave is a matter of 
    [moving the index in the program trace forward by 1](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub_sys.cc#L127),
    [updating the state of the register file](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub_sys.cc#L137),
    and asking to [send a TRAP signal to GDB](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub_sys.cc#L136).

    After receiving this trap, GDB always queries the contents of the register file, so it makes sense to
    already get this data ready after during a step.

    The state of the register file is derived by [replaying the register file write operations up to the point
    of the current instruction](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/RegFileTrace.cc#L91-L105).
    Right now, this code is super inefficient: after every instruction step, I replay the register writes for all registers from
    the start, time and time again. It's very easy to optimize this code.

* `c` to continue executing instructions on the CPU until a breakpoint is hit

    "continue" is the big brother of "step". In GDBWave, it
    [iterates through the program counter trace until the program counter matches an element in the breakpoint array](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub_sys.cc#L102-L111).

     After this, the behavior is just like "step": the register file state is updated, and a TRAP is sent upstream to GDB.

* `R` for CPU restart

    This resets the time step counter back to the first value.


* `Z` and `z` to set and clear breakpoints

    RSP breakpoints are used for more than just breakpoints that are explicitly set with the GDB breakpoint
    command. They are also used when you use the `next` command: GDB sets a temporary breakpoint at the next
    line of your program.

    But even explicity breakpoints are being set and cleared all the time. I'm not really clear why GDB does that, 
    but I assume it has to do with making things work with all kinds of weird embedded system configuration.

    GDB makes a distinction between software and hardware breakpoints. Hardware breakpoints are dedicated hardware
    resources inside the CPU. If any, there are usually only on a few of them, and GDB will only use them
    if you explicitly ask for it. A software breakpoint is usually achieved by replacing an regular instruction 
    with some kind of trap instruction in the instuction RAM. (In the case of RISC-V, it's the EBREAK instruction.) 
    Once this trap is triggered, the GDB server is expected to replace the trap instruction with the original instruction, 
    and execute it when it continues. You can have an unlimited number of software breakpoints. In practice,
    hardware breakpoints are only used when you're debugging code that's located in ROM.

    With all that said, when it asks to enable a software breakpoint, all GDB cares about is that the breakpoint
    is dealt with by the server. GDBWave maintains an 
    [associative array, indexed with the program counter](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub_sys.cc#L17), 
    with all active breakpoints. 

* `p` or `g` to read one or all CPU registers

    Whenever the CPU comes to a halt, GDB tries to read the CPU registers. The state of the register file
    was already updated after doing a step or continue operations, so it's must a matter or returning that
    data.

* `m` to read a section of memory

    Reading sections of memory is another very popular activity of GDB. In GDBWave, this is implemented
    very similar the way it's done for the register file: starting with the initial value that was loaded
    from the binary file, 
    [all memory writes are applied up to the time stamp of the current program counter](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/MemTrace.cc#L164-L177).

And that's really it! There are number of RSP commands for which GDBWave will reply with an 
[OK packet](https://github.com/tomverbeure/gdbwave/blob/d53d7891e7739787f902ce98090246613762ccb4/src/gdbstub.cc#L1071-L1078),
but everything else gets ignored.


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

[^3]: It's usually trivial to find the program counter of instructions that the CPU wants to execute: just look
      at the addresses on the bus that the CPU uses to read from instruction memory or cache. But those addresses
      are not necessary instructions that the CPU will execute to completion, because CPUs often fetch instructions
      that are later discarded after a mispredicted branch.

[^4]: This code is a greate example to illustrate how much C++ has changed in the last 2 decades. I copied the code
      from StackOverflow. While I can guess what's going on there, I definitely can't claim to understand it fully.

[1]: /assets/gdbwave/gtkwave_manual.pdf#page=137


