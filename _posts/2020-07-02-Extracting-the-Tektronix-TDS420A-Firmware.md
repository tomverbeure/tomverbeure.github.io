---
layout: post
title: Extracting the Tektronix TDS 420A Firmware
date:   2020-07-02 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

In [my previous blog post](/2020/06/27/In-the-Lab-Tektronix-TDS420A.html#the-tektronix-tds-420a-in-brief) 
about the TDS 420A, I listed some of the optional features that weren't enabled on this oscilloscope.

Even if some of these features aren't particularly interesting, the idea that these could
be enabled with some configuration hacking was pretty intriguing. And there are plenty
of posts on forums (including the ones hosted on the Tektronix website!) that
describe how to go about enabling these optional features.

Of the 3 available options, video triggering, advanced DSP math, and 120K
sample points, the general online consensus is that the first two can enabled by 
writing a 1 into a strategically chosen location of the non-volatile RAM (NVRAM).

And while the 120K sample points option is the most interesting by far, one can 
still gain a lot of insight into how a product works internally by following a bunch 
of leads.

In the case of TDS oscilloscopes, there's a lot of information online to work
with: posts on different forums that talk about DIP switches to flip, GPIB connectors
to connect, and commands that need to be sent.

However, many posts are incomplete, with expired links, sometimes contradictory, often 
about scopes of a family that is very similar but different enough to matter, and every 
once in a while plain wrong.

I decided to start by trying to extract the TDS 420A firmware through the GPIB interface.
It doesn't require any major surgery or even disassembly, and it's thus unlikely to
cause any harm. Yet at the same time, it had the potential of uncovering a lot of
interesting scraps of information.

In what follows, I explain how to do that.

# Manipulating the TDS Oscilloscope Firmware and Configuration with Tektools

One thing that comes up quite a bit online is [`tektools`](https://github.com/ragges/tektools).

From the [README](https://github.com/ragges/tektools/blob/master/README.md):

> These are tools for backing up and restoring NVRAM, Flash and EEPROMs in certain 
> Tektronix oscilloscopes such as the TDS 5xx/6xx/7xx series

While not explicitly mentioned, it worked for me to read the TDS 420A firmware. Unlike
the TDS families listed above, TDS 4xx series scopes do not store configuration parameters
in EEPROM, but in static RAM that's been made non-volatile by a long lasting lithium
battery. I was not able to dump the contents of that NVRAM with `tektools`.

I had already [installed the Linux GPIB driver](/2020/06/27/Tektronix-TDS420A-Remote-Control-over-GPIB.html#installing-the-gpib-usb-hs-linux-kernel-driver),
and compiling `tektools` was trivial: just follow the instructions.

# Switching the TDS420A into Firmware Update Mode

Extracting the firmware is a bit more involved than just running the tool: at least on a TDS420A, 
you first need to flip 2 DIP switches inside the scope to put it in firmware update mode. 

The [service manual](https://www.tek.com/oscilloscope/tds420a-manual/tds420a-tds430a-tds460a-service-manual)
shows how to do this through one of the ventilation holes of the case. With a tiny screwdriver
and a flash light, changing the switches only takes a minute of your time.

![Switching into firmware update mode](/assets/tds420a/switching_into_firmware_update_mode.png)

Firmware update mode is a minimal operation mode that accepts a small set of GPIB commands
to read and write the flash ROMs[^1]. The oscilloscope isn't functional in any other way: the 
CRT is powered off, buttons don't work, the LEDs of the front panel are all switched on.

[^1] There may be other commands in firmware update mode, but I wasn't able to find any.

In normal operation, you can 
[set the GPIB address](/2020/06/27/Tektronix-TDS420A-Remote-Control-over-GPIB.html#set-the-gpib-device-address-on-the-tds-420a)
of the scope through the scope GUI. In firmware update mode, there is no such choice, and the 
GPIB address is hardcoded to 29. `tektools` automatically assumes this to be the case, so there's 
no need to do anything there, but this is something to keep in mind when you want to manually
issue GPIB commands to the scope while in firmware update mode. 

# Dumping a Section of the Address Map

Reading a section of the address space to a file is simple:

```
tektool --read <file_name.bin> --base <start address> --length <number of bytes>
```

However, there's a caveat: the 4GB address map of an early nineties product is obviously very
sparse, with the vast majority of address not used for anything. On my TDS oscilloscope, a
`tektool` access to a non-mapped address breaks accesses to *any* memory locations,
*including mapped ones*, until the next power cycle.

Here's an example:

1. This successfully dumps the boot ROM:

    ```
tektool --read boot_rom.bin --length 524288 --base 0x00000000
    ```

1. Address `0x04000000` is not mapped:

    ```
tektool --read dump_0x400.bin --length 524288 --base 0x04000000
read_memory: response reading failed
    ```

1. Reading the boot ROM again now fails:

    ```
tektool --read boot_rom.bin --length 524288 --base 0x00000000
read_memory: invalid response: +
    ```

When in firmware update mode, power cycling the scope is matter of seconds, so it's
not a huge deal once you know about it. 

# The TDS 420A Address Map as I Know It

I couldn't find a clear address map of the scope online. The table below was a matter 
of trial, error, and a lot of power cycles:

| Start Address |     Size (bytes)    |     Description    |                      Comments                     |
|---------------|:-------------------:|:------------------:|---------------------------------------------------|
| `0x0000_0000` |  524288             |      Boot ROM      |                                                   |
| `0x0100_0000` |  4194304            |    Main Firmware   |                                                   |
| `0x0500_0000` |  262144             |          ?         |                                                   |
| `0x0800_0000` |  524288             | Alternate Boot ROM | Contents not identical to boot ROM but close      |
| `0x0900_0000` |  524288             |          ?         | Data pattern that seems to repeat every 512 bytes |
| `0x0d00_0000` |  262144             |          ?         |                                                   |

When the boot ROM area is listed as 524288 bytes, that doesn't mean that the ROM is 512KB (a decent amount
back in 1991!) It simply means the number of bytes that can be read starting from the start address
that won't result in a bus error.

There were online reports about the address range at `0x0400_0000` being used for NVRAM, 
but it results in a bus error on the TDS420A. For a while, I thought that `0x0500_0000` was 
the option storage, but no amount of writing different values to that regions make any of 
the scope options to appear.

I ended up with something that turned out to be extremely valuable: a full binary dump of all the firmware.

# Strings in the Boot ROM

At this point, I wasn't interested just yet in exploring the firmware in depth, but a `strings` command
can always reveal interesting pieces of information. For example, I was wondering if it would expose some 
of the GPIB commands that are supported by the boot ROM.

The boot ROM strings are more or less what you'd expect:

* Copyright and identification notice

    ```
Copyright (c) Tektronix, Inc., 1990, 1991, 1994, 1995.  All rights reserved.
Bootrom Version - v2.0
    ```

* Lots of strings related to internal tests and checksums

    ```
...
Skipping Bootrom Checksum Test.
Kernel Diag Failure (Bootrom Test):  bad header checksum
Runtime checksum = 0x%x, stored checksum = 0x%x
        Bootrom Header Checksum passed.
Kernel Diag Failure (Bootrom Test):  bad 2nd checksum
        Bootrom Total Checksum passed.
...
    ```

* Low level CPU stuff

    ```
...
Bus Err
Addr Err
Ill Instr
Zero Div
CHK Trap
TRAPV Trap
Priv Viol
Trace Exc
Unimp Op 1010
Unimp Op 1111
Co-Proc Viol
Frmt Err
Uninit Intr
Spur Intr
PC:0x%08x
REGS:0x%x
...
    ```

* Messages related to flash ROM

    ```
...
Skipping Flashrom DSack Test.
        Flash Rom DSACK 0 failed: Read 0x%x, should be 0x%x
        Flash Rom DSACK 1 failed: Read 0x%x, should be 0x%x
Flashrom Header failed: Bad jumpcode = 0x%0x, should be 0x%x
...
    ```

In one of the online forums, there was some chatter about enabling TDS 4xx series 
options with GPIB commands, but I was not able to get this to work on my scope, not 
in firmware update mode nor in regular mode. 

There were no obvious strings related to these kind of GPIB commands in the boot ROM
(but that was also the case for the main firmware.)

While the binary contents of the alternate boot ROM address space were slightly
different that the boot ROM at address 0x0, the strings content was identical.

This can easily be explained if that 512KB address space space doesn't only contain 
ROM, but also some RAM, registers etc.

# Strings in the Main Firmware

Commercial firmware images normally contain text data that's used to interact with the user:
command strings, help messages, error and log messages. What you won't get are the program symbols.
These are stripped to reduce code size and, maybe, to avoid reverse engineering.

This is definitely not the case for the main TDS420A firmware. Running `strings main_fw.bin` resulted in a 
treasure trove of data!

* There are the expected copyright notices:

    ```
...
COPYRIGHT TEKTRONIX INC, 1989-1996
...
    ```

* Operating system identification strings

    ```
...
VxWorks (for %s) version %s.
...
    ```

    ... and logos

    ```
...
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]   
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]   
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]   
      ]]]]]]]]]]]  ]]]]     ]]]]]]]]]]       ]]              ]]]]          TM 
 ]     ]]]]]]]]]  ]]]]]]     ]]]]]]]]       ]]               ]]]]             
 ]]     ]]]]]]]  ]]]]]]]]     ]]]]]] ]     ]]                ]]]]             
 ]]]     ]]]]] ]    ]]]  ]     ]]]] ]]]   ]]]]]]]]]  ]]]] ]] ]]]]  ]]   ]]]]] 
 ]]]]     ]]]  ]]    ]  ]]]     ]] ]]]]] ]]]]]]   ]] ]]]]]]] ]]]] ]]   ]]]]   
 ]]]]]     ]  ]]]]     ]]]]]      ]]]]]]]] ]]]]   ]] ]]]]    ]]]]]]]    ]]]]  
 ]]]]]]      ]]]]]     ]]]]]]    ]  ]]]]]  ]]]]   ]] ]]]]    ]]]]]]]]    ]]]] 
 ]]]]]]]    ]]]]]  ]    ]]]]]]  ]    ]]]   ]]]]   ]] ]]]]    ]]]] ]]]]    ]]]]
 ]]]]]]]]  ]]]]]  ]]]    ]]]]]]]      ]     ]]]]]]]  ]]]]    ]]]]  ]]]] ]]]]] 
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]]   
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]]]       Development System  
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]]   
 ]]]]]]]]]]]]]]]]]]]]]]]]]]]       
...
    ```

    Yes, we get it, Tektronix, you're using VxWorks.

* There's something that looks like a file system

    ```
...
element /vobs/dpl/classes1/makeTemplates/makeHost /main/2kdso_inprogress/k2_inprogress/4
element /vobs/dpl/classes1/grammarMasters/Makefile.class /main/18
element /vobs/dpl/classes1/applications/Scope-Acquisitions/TwoKAcqManager/lib/makeLocal /main/2kdso_inprogress/k2_inprogress/1
# A bug in the build was that the symbolic link to taskNames was missing in the V1.0 release configuration
# (we could not tell until we started again in a new view)
element -dir /vobs/dpl/buildTDS/build /main/8
#probably makes no difference -- adds extern short hardcopyPort; 
...
    ```

* All kinds of application strings

    ```
...
Vertical Offset
Frame
Save Wfm
to File
(User Comp.
Values
(SAM3SpeedBias1A
Infinite
Persistence
RadiansPhase
(error in day argument
(%!PS-Adobe-3.0 EPSF-3.0
Ch4TrigBal
Insufficient V
Within
Ch1FinePos
BMP Mono
...
    ```

* Internal diagnostic messages

    ```
...
FAIL ++ 
pass -- 
**Error count in %d pu_diag seq passes:
.. %d = %s
Instrument was HOT
Instrument was COLD
...
    ```

* A help menu with console commands (promising!)

    ```
...
help                       Print this list
dbgHelp                    Print debugger help info
nfsHelp                    Print nfs help info
netHelp                    Print network help info
spyHelp                    Print task histogrammer help info
timexHelp                  Print execution timer help info
h         [n]              Print (or set) shell history
i         [task]           Summary of tasks' TCBs
ti        task             Complete info on TCB for task
sp        adr,args...      Spawn a task, pri=100, opt=0, stk=20000
taskSpawn name,pri,opt,stk,adr,args... Spawn a task
td        task             Delete a task
...
...
    ```

* But the most stunning part is what looks like a function symbol table with thousands
  of entries!

   ```
...
_libInvokeStartupFunction
_libLoadInitValues
_libLoadValues
_libManagerByteAt
_libManagerByteAtOffset
_libManagerByteAtOffsetPut
_libManagerByteAtPut
_libManagerDoubleAt
_libManagerDoubleAtOffset
_libManagerDoubleAtOffsetPut
_libManagerDoubleAtPut
_libManagerFloatAt
_libManagerFloatAtOffset
_libManagerFloatAtOffsetPut
_libManagerFloatAtPut
_libManagerLongAt
_libManagerLongAtOffset
_libManagerLongAtOffsetPut
_libManagerLongAtPut
_libManagerSizeAt
_libManagerWordAt
_libManagerWordAtOffset
_libManagerWordAtOffsetPut
_libManagerWordAtPut
_libNVFactoryValuesLoaded
_libRestoreScopeState
_libSaver
_libSaverPanic
_libTattle
_libVerifyExtendedCal
_libVerifyOrSave
_libraryCollection
_lineIncrementHwAction
_lineNeedsClip
_listen
_lkAddr
_lkup
...
    ```

    These symbol names must be there for a reason. If there's a way to link those symbol 
    names to memory addresses, that would be a huge help to disassemble and reverse engineer 
    the firmware, and maybe unlock some features.

# To Be Continued...

We have the firmware, we have interesting strings that point to a console. It's about
time to start getting our hands dirty.

# Relevant links

* [Utility to read/write memory on Tektronix scopes](https://forum.tek.com/viewtopic.php?t=137308)

    Introduction of `tektool` (aka `tekfwtool`) by original author on Tektronix forum.

* [tekfwtool](https://github.com/fenugrec/tekfwtool)

    Github repo of original `tekfwtool`. Dos and Windows only.

* [Announcement of improved `tektool`](https://www.eevblog.com/forum/repair/unified-tektool-released-!-(firmware-flash-tools-for-old-tds-series)/)

    * Supports different kinds of flash
    * Supports both TDS 5xx/6xx/7xx and TDS 4xx.
    * Works for Dos, Windows, Linux, macOS.

* [tektools](https://github.com/ragges/tektools)

    Github repo of improved `tektool`. Also includes the original `tekfwtool`.


