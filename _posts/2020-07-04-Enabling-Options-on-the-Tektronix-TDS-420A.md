---
layout: post
title: Option Hacking on the Tektronix TDS 420A
date:   2020-07-08 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

In [earlier](/2020/06/27/In-the-Lab-Tektronix-TDS420A.html#the-tektronix-tds-420a-in-brief), I
already mentioned that the TDS 400 series of oscilloscopes has a bunch of optional features:

* Option 05: Video Trigger 
* Option 13: RS-232/Centronics Hardcopy Interface
* Option 1F: File System/Floppy
* Option 2F: Advanced DSP Math
* Option 1M: 120k waveform sample points

Most scopes, including mine, come with options 13 and 1F already enabled. But the remaining
ones are less common.

The video trigger and advanced DSP math are software functions, but even the 120k sample
points option sweemed like something that could be enabled with a software hack, since
the signal acquisition board has the 512KB of RAM available to store the data.

In this blog post, I'll describe how the TDS 400 series manages option enablement, and
how you can hack the scope into getting them to work.

# How a TDS400 Oscilloscope Manages Hardware Features

Using Ghidra and the debug console, I figured out how the scope manages hardware
features: it has a function called `hwAccountantQuery` that has a single
parameter which I'll call the 'feature ID'.

`hwAccountantQuery` will return an integer value for that feature ID. These values
can be boolean in nature ("Is a certain feature present or not") or can be the
amount of DSP memory etc.

Here's a very non-exhaustive list of codes that I've been able to identify:

```
0x20d: number of scope channels
0x20f: size of acquisition RAM
0x216: ProbeD2MemSize
0x248: CPU clock period
0x255: InstrumentNameStringPtr
0x271: hwProbeSpecialDiagModeActive
0x2a0: hwProbeSpecialDiagLoopCount
0x2a1: hwProbeSpecialDaigSeqId
0x2b8: 30000 points -> value when 1M option is not possible
0x2bf: TDS420A
0x2d2: RS232 Debug uart present
0x317: MathPak
0x461: Floppy drive present
0x537: flashRomDateStringPtr
0x54c: TDS410A
0x560: TDS430A
0x700: hwProbeTvTrigPresent
```

`hwAccountantQuery` calls on `hwAccountantGetValue`. The first part of the function looks liks this:

![hwAccountantGetValue](/assets/tds420a/hwAccountantGetValue.png)

It's a large `if-then-else` or `case` statement that calls a dedicated function for a particular
feature ID. 

# The Key to Enabling Option 05 - Video Triggering

Did you see `_hwProbeTvTrigPresent()`? That's the function that checks
if the video triggering feature is enabled:

![hwProbeTvTrigPresent](/assets/tds420a/hwProbeTvTrigPresent.png)

And there we have it! To enable "Option 05 - Video Triggering", all you need to do
is store a non-zero value in non-volatile RAM location 7 !

*This is not a shocking new discovery: plenty of online sources already confirmed this,
but it's great to confirm this from first principles, but going to the source.*

# The Key to Enabling Option 2F - Advanced DSP Math

Internally, the Advanced Math DSP is called "MathPak". Just like for video triggering, 
the `hwAccountGetValue` function issues a call to `hwProbeMathPakPresent()`:

![hwProbeMathPakPresent](/assets/tds420a/hwProbeMathPakPresent.png)

Option 2F simply relies on a non-zero value in NVRAM location 9!

# Options 05 and 2F Enabled!

It's now just a matter of issuing following 2 commands on the debug console:

```
libManagerWordAtPut 0x50007, 1
libManagerWordAtPut 0x50009, 1
```

My scope booted up with this image:

![Options 05 and 2F enabled](xxxx)

Success! I'm now the proud owner of a scope that supports an entirely obsolete video triggering
mode, and a FFT math option!




Unfortunately, the `case` statement is only a small part of `hwAccountGetValue`: most
feature checking functions are performed by looping through an array with structs that
have the feature ID and a function pointer to the checking function.




There's quite a bit of chatter online about enabling options on the TDS 400 series. The
general, with the general concensus that options 05 and 2F can be easily be enabled, but
option 1M, the most interesting one, being elusive.

In this forum post, somebody mentions how it's possible to enable options on the
TDS420 with the `libManagerWordAtPut` function.

Using the [RS-232 debug console](/2020/07/03/TDS420A-Serial-Debug-Console-Symbol-Table-Ghidra.html),
I first dumped the values of all 16 locations that work with the `libManagerWordAt` function:

```
-> libManagerWordAt(0x50000)
value = 0 = 0x0
-> libManagerWordAt(0x50001)
value = 0 = 0x0
-> libManagerWordAt(0x50002)
value = 0 = 0x0
-> libManagerWordAt(0x50003)
value = 0 = 0x0
-> libManagerWordAt(0x50004)
value = 0 = 0x0
-> libManagerWordAt(0x50005)
value = 0 = 0x0
-> libManagerWordAt(0x50006)
value = 0 = 0x0
-> libManagerWordAt(0x50007)
value = 0 = 0x0
-> libManagerWordAt(0x50008)
value = 0 = 0x0
-> libManagerWordAt(0x50009)
value = 0 = 0x0
-> libManagerWordAt(0x5000a)
value = 0 = 0x0
-> libManagerWordAt(0x5000b)
value = 0 = 0x0
-> libManagerWordAt(0x5000c)
value = 0 = 0x0
-> libManagerWordAt(0x5000d)
value = 0 = 0x0
-> libManagerWordAt(0x5000e)
value = 0 = 0x0
-> libManagerWordAt(0x5000f)
value = 0 = 0x0
```



![hwProbe1MOption](/assets/tds420a/hwProbe1MOption.png)

http://www.ko4bb.com/getsimple/index.php?id=enable-tds754d-options

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
