---
layout: post
title: Hacking the Tektronix TDS 420A Oscilloscope
date:   2020-07-03 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

In my previous blog post about the TDS 420A, I listed some of the optional features 
that weren't enabled on this oscilloscope.

Most of these features aren't particularly interesting to me except for the 120K 
samples points option.

And since the acquisition board has sufficient SRAM to support this many sample
points, trying to enable this seemed like a worthy goal.

The first steps are always to gather information: for a product this old, surely there
must be plenty of material online to work with. And there are quite a number of
posts on different forums that talk about DIP switches to flip, GPIB connectors
to connect, and commands that need to be sent.

However, in a lot of cases, the posts are incomplete, with expired links, sometimes 
contradictory, often about scopes of a family that is very similar but different enough 
to matter, and every once in a while plain wrong.

In the end, the only way to really get somewhere was to dive in myself and see
where it'd get me.

# How TDS Family Options are Stored

Tektronix oscilloscopes of the mid nineties (TDS4xx, TDS5xx, TDS6xx, TDS7xx) use
non-volatile RAM (NVRAM) to remember which options are enabled.

For the TDS5xx and up, this NVRAM is some kind of EEPROM or flash ROM. There are
places that talk about how to dump the contents of this NVRAM, restore it etc.

Unfortunately, the TDS4xx does not work that way: its CPU PCB has section of SRAM with
a battery voltage controller, and a long lasting battery that can last for many
years (decades!). What's very peculiar is that this logic is encased in some kind
of transparent glue. It's not clear why this is done, but at the very least, it makes
it impossible to probe the pins of these SRAMs.

It also has the major issue that you will lose all the options when the battery
stops working. [^1]

[^1] The scope actually has 2 such NVRAM configurations: the one on the CPU board is
used to store options, the other one is used to remember scope calibration values.

You can find instructions online that tell you how to set options for different
TDS families, including the TDS4xx, but one way or the other, I wasn't able to make
any of that work.

# Tektool - Dumping the TDS420A Firmware

One thing that comes up quite a bit online is [`tektool`](https://github.com/ragges/tektools).

`tektool` connects to your scope through GPIB and allows to read or write the firmware.

Unfortunately, it's a bit more involved than that: at least on a TDS420A, you first need to
flip 2 DIP switches inside the scope to put it in firmware update mode. The service manual
shows how to do through one of the ventilation holes of the case, but since I was about
to open up the scope anyway, I did it that way.

In normal operation, you can program the GPIB address of the scope through the scope GUI.
In firmware update mode, there is no such choice, and the GPIB address is hardcoded to 29. 
`tektool` automatically assumes this to be the case, so there's no need to do anything there,
but this is something to keep in mind when you want to do your communication with the
scope while in firmware update mode.

I couldn't find a clear address map of the scope, so I simply did some trial and error. This
takes more work that you'd think: when you use `tektool` to access an unmapped region of memory,
there will be a bus error of some sort inside the scope, and all further `tektool` request
will fail until the next power cycle. So you end up doing a lot of power cycles!

Here is what I came up with:

| Start Address |     Size (bytes)    |     Description    |                      Comments                     |
|---------------|:-------------------:|:------------------:|-------------------------------------------------|
| `0x0000_0000`   |  `0x08_0000 / 524288` |      Boot ROM      |                                                   |
| `0x0100_0000`   |  `0x40_0000 / 4194304` |    Main Firmware   |                                                   |
| `0x0500_0000`   |  `0x04_0000 / 262144` |          ?         |                                                   |
| `0x0800_0000`   |  `0x08_0000 / 524288` | Alternate Boot ROM | Differs from main boot ROM                        |
| `0x0900_0000`   |  `0x08_0000 / 524288` |          ?         | Data pattern that seems to repeat every 512 bytes |
| `0x0d00_0000`   |  `0x04_0000 / 262144`  |          ?         |                                                   |

The address ranges at `0x0400_0000` has been reported to be used for NVRAM, but results in a bus error
on the TDS420A. For a while, I though that `0x500_0000` was the option storage, but no amount of writing
different values to that regions make any of the scope options to appear.

In the end, I ended up with something that turned out to be extremely valuable: a full binary dump
of all the firmware.

# The Strings Content of the Main Firmware

Commercial firmware images normally contain text data that's used to interact with the user:
command strings, help messages, error and log messages. What you won't get are the program symbols.
These are stripped to reduce code size and, maybe, to avoid reverse engineering.

This is definitely not the case for the TDS420A firmware!  Running `strings main_fw.bin` resulted in a 
tresure trove of data!

Here's just a small sample:
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

Here are literally thousands of strings with function call names.

There's also this:
```
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
```

And look here:
```
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
ts        task             Suspend a task
tr        task             Resume a task
d         [adr[,nwords]]   Display memory
m         adr              Modify memory
mRegs     [task]           Modify a task's registers interactively
d0-d7,a0-a7,sr,pc  [task]  Display a register of a task
version                    Print VxWorks version info, and boot line
iam       "user"[,"passwd"]  Set user name and passwd
whoami                     Print user name
devs                       List devices
cd        "path"           Set current working path
pwd                        Print working path
ls        ["path"[,long]]  List contents of directory
ll        ["path"]         List contents of directory - long format
rename    "old","new"      Change name of file
copy      ["in"][,"out"]   Copy in file to out file (0 = std in/out)
ld        [syms[,noAbort][,"name"]] Load stdin, or file, into memory
                             (syms = add symbols to table:
                              -1 = none, 0 = globals, 1 = all)
lkup      ["substr"]       List symbols in system symbol table
lkAddr    address          List symbol table entries near address
checkStack  [task]         List task stack sizes and usage
printErrno  value          Print the name of a status value
period    secs,adr,args... Spawn task to call function periodically
repeat    n,adr,args...    Spawn task to call function n times (0=forever)
diskFormat  "device"       Format disk
diskInit  "device"         Initialize file system on disk
squeeze   "device"         Squeeze free space on RT-11 device
NOTE: arguments specifying 'task' can be either task id or "name"
Type <CR> to continue, Q<CR> to stop: 
...
```

This is all extremely promising, especially the `lkup` and `lkAddr` commands,
since mapping addresses to symbols would be a huge help in reverse
engineering the firmware, if it came to that.

# Connecting to TDS420A RS-232 Debug Console Port

My TDS420A has an external RS-232 port (Option XXX), that can only be used to connect
some ancient printer to the scope and dump screenshots.

But that's not the only RS-232 port! Next to the firmware update switches
on the CPU PCB, you can find a 10-pin connector that carries the RS-232 port
for the debug and diagnostic console. Tektronix used to sell a cable
to convert the 10-pin header into a DB9 serial port connector, but I had a
better idea (or so I thought):

The external RS-232 DB9 connector *also* goes to a 10-pin header. So I decided
to just remove that the IO PCB, remove that 10-pin to DB9 cable, and voila!,
I'd be able to connect the debug console straight to a regular DB9 serial cable.

Because, surely, the Tektronix wouldn't be so dumb to have different pinouts for
the external RS-232 to DB9 cable and the internal one?

Well, I tried that, and it didn't work, because Tektronix was indeed *that* dumb.
The debug console cable is rotated by 180 degrees compared to the external cable.

After wasting a perfectly good half hour on this, I connected the thing up with some
flimsy wires, and after swapping TX/RX, and configuring a serial terminal on my
PC at 9600 baud, the following characters rolled on the screen when booting up
the scope:

```
	Bootrom Header Checksum passed.
	Bootrom Total Checksum passed.
	BootRom Check Sum passed.
	Bus Error Timeout test passed.
	Bus Error Write to Bootrom passed.
	GPIB Test passed.
Kernel Diagnostics Complete.

Calling SDM (monitor) Routine.

SDM (monitor) not enabled.
	Enabling Bus Control register. Value = 0x2
	Flashrom Programming Voltage is OFF.
	Flashrom DSACK and JumpCode test passed.
	Flashrom Checksums passed.
Bootrom Diagnostics Complete.

Transferring control to the Flashrom.
sysDramControllerInit
sysDramByteStrobeTest
sysDramTest
bcopy(<Idata>)
bzero(<bss>)
intVecBaseSet(getVbr())
sysDevDramTest
0x0 bytes of development dram found
validateDataSpace
Outer Kernel DSACK Test
Pending Interrupt Test
Walk IPL to Zero Test
Timer Int Test
usrInit()
cacheEnables()
bzero(&edata,&end - &edata)
intVecBaseSet()
excVecInit()
bzero(&end,sysMemTop() - &end )
sysHwInit()
ioGlobalStdSet({STD_IN,STD_OUT,STD_ERR})
xcInit()
logInit()
sigInit()
dbgInit()
pipeDrv()
stdioInit()
dosFsInit()
ramDrv()
floatInit()
mathSoftInit()
spyStop()
timexInit()
selectInit()
symTblCreate(standAlone)
symTblCreate(stat)
sysStarSut(a
            rtni Pcopower-On Diag Sequence
hwAccountant probe routines
  Probe for unexpected pending ints
  Real time clk present
  Dsp Instr mem size
  Dsp D2 mem size
  Dsp D1 mem size
  Dsy Vect0 mem size
  Dsy Vect1 mem size
  Dsy Wfm0 mem size
  Dsy Wfm1 mem size
  Dsy Text0 mem size
  Dsy Text1 mem size
  Acq number of digitizers
  Acq mem size
>   Cpu timer interval uSec
  Cpu Dram size
  NvRam mem size
  Opt Math Package presence
  Opt RS232/ Cent presence
  Acq 8051 presence
  Acq ADG209C presence
  Opt 1M presence
  Acq record length size
  Opt TvTrig presence
  Dsy color presence
  Opt floppy drive presence
dsyWaitClock ................... pass
clockCalVerify ................. pass
cpuDiagBatTest ................. pass
cpuDiagAllInts ................. pass
cpuEEromLibDiag ................ pass
calLibDefaultCk ................ pass
dspForcedBus ................... pass
dsp68kD2MemTest ................ pass
optRS232DuartIO ................ pass
dsp68kMemTest .................. pass
dspRunVerify ................... pass
dspBusRequestTest .............. pass
dspImplicitBusAccess ........... pass
dspTristarMemTest .............. pass
dspDsyToDspInts ................ pass
dspAcqToDspInts ................ pass
nvLibrariansDiag ............... pass
dsyDiagResetReg ................ UNTESTED
atBusTest ...................... pass
dsyDiagResetReg ................ UNTESTED
dsyDiagVscReg .................. pass
dsyDiagPPRegMem ................ pass
dsyDiagRasRegMem ............... pass
dsyDiagRegSelect ............... pass
dsyDiagRamdacRegMem ............ pass
dsyDiagAllMem .................. pass
dsySeqYTModeV0Intens ........... pass
dsyDiagSeqXYModeV1 ............. pass
dsyRastModeV0Walk .............. pass
dsyRastModeV1Attrib ............ pass
dsyWaitClock ................... pass
attn8051testResult ............. pass
attnDACReadback ................ pass
dsyWaitClock ................... pass
acq8051testResult .............. pass
adgRegDiag ..................... pass
dsyWaitClock ................... pass
adgMemTestDiag ................. pass
trigComparatorTest ............. pass
trigDBERunsAfter ............... pass
tbiRampTest .................... pass
acqRampDiagAll ................. pass
dsyWaitClock ................... pass
fpDiagConf ..................... pass
et not started, either there was trouble or the devnet is missing
floppyDriverStartup()
can't open input 'fd0:/startup.bat'
  errno = 0x13 (S_errno_ENODEV)

/Thu May 9 11:26:15 PDT 1996/k2_vu/paulkr

Smalltalk/V Sun Version 1.12
Copyright (C) 1990 Object Technology International Inc.
0x2ff4684 (V main): 
brTriesMax:         1 busRequestCount: 1 busRequestGranted: 0
```

I was in business!!!

# The VxWorks Operating System

Earlier, I already came across the VxWorks logo in the main firmware dump.

[VxWorks](https://en.wikipedia.org/wiki/VxWorks) is a real-time operating system (RTOS) that's
very popular for embedded systems with real-time constraints. An oscilloscope is a very good
example of that.

It's supported on a large amount of CPUs (the TDS420A has a Motorola 68020), has a preemptive 
multitasking kernel, supports file systems, network protocol stacks etc.

On the oscilloscope, it has runs a number of parallel tasks, though I didn't really dive
into it.

But one of the key features is a console shell that allows calling any function that is
declared in the symbol table as if it's just a console shell command.

You have no idea how useful that is to hack a system: all the functions that I found through the
`strings main_fw.bin` command can be called and executed on a live working system.

Here's a good example: there is `ringBell()` function in the firmware. When I type `ringBell`
on the console... the bell rings.

In combination with a symbol table, VxWorks rolls out the red carpet for firmware reverse
engineers.

# Enabling Option 05 and Option 2F 

In this forum post, somebody mentions how it's possible to enable options on the
TDS420 with the `libManagerWordAtPut` function.

I first dumped the values of all 16 locations that work with the `libManagerWordAt` function:
they all came back 0.

After issuing: 
```
libManagerWordAtPut 0x50007, 1
libManagerWordAtPut 0x50009, 1
```

My scope booted up with this image:

![Options 05 and 2F enabled](xxxx)

Success! I'm now the proud owner of a scope that supports an entirely obsolete video triggering
mode, and a dreadfully slow FFT math option!


# Creating a Full Symbol Table

The most useful function of all is `lkUp`: it checks if a given string matches any part
of the strings in the symbol table, and prints out these matching symbols with their corresponding
address. 

For example, `lkUp _a` give the following list:

```
_atBusAddrTest  0x0117dba8 text
_activateElement 0x0119b820 text
_attnDecadeDivCh1 0x0115464e text
_acquiredWfms   0x02e98380 bss
_auxDescBuf     0x02e55af0 bss
_set_if_addr    0x011f1032 text
_attnSigPathCh4 0x011543d4 text
_arpinput       0x011eff26 text
_asctime        0x0119adba text
_m_adj          0x011f57e8 text
_adgMemShortDiag 0x01185528 text
_atBusTest      0x0117ddd0 text
_attnSigPathCh1 0x01154344 text
_aliasNameBufList 0x02e56450 bss
_asciiPoint     0x02e577c0 bss
...
_xdr_attrstat   0x011e5750 text
...
```

*Note how the list includes `_xdr_attrstat`. That's because it has `_a` in the middle*

The next step was to dump all the symbols in the binary. Instead of dumping them all at once,
I went from `_a` to `_z` and from `_A` to `_Z`. The end results were 5000+ symbols and their
address.



How about this: 

```
> hwProbe1MOption
0
```

Here's a reminder: the 1M option is the option that increases the number of sample points from 30K to 120K.

# Various links

* [Hacking my TDS460A to have options 1M/2F?](https://www.eevblog.com/forum/testgear/hacking-my-tds460a-to-have-options-1m2f/)

* [TDS 420 Debug Serial Port](https://forum.tek.com/viewtopic.php?t=138100)

* [TDS420 Options Possible?](https://forum.tek.com/viewtopic.php?t=140268)

* [Upgrade Tektronix: FFT analyzer](http://videohifi17.rssing.com/chan-62314146/all_p49.html)

    Story about upgrading the CPU board from 8MB to 16MB on a TDS420 (not 420A?) and then FFT in the
    NVRAM.

* [Enabling FFT option in Tektronix TDS 540A oscilloscope](https://www.youtube.com/watch?v=iJt2O5zaLRE)

    Not very useful: enables FFT by copying NVRAM chip.

* [tekfwtool](https://github.com/fenugrec/tekfwtool)

    Dos and Windows only

* [tektools](https://github.com/ragges/tektools)

    Also has Linux and macOS support

* [Utility to read/write memory on Tektronix scopes](https://forum.tek.com/viewtopic.php?t=137308)

* [TDS420 with lost options](https://www.eevblog.com/forum/testgear/tds420-with-lost-options/)

* [RS232 Connector](https://forum.tek.com/viewtopic.php?f=568&t=139046#p281757)
