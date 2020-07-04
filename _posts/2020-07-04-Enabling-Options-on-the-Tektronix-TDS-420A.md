---
layout: post
title: Enabling Options on the Tektronix TDS 420A
date:   2020-07-04 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction


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
