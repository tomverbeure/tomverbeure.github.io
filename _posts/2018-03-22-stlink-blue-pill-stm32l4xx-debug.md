---
layout: post
title: STLink v2 + STM32F103C8T6 Blue Pill Board + STM32L4xxx Debug
date:   2018-03-22 00:00:00 -1000
categories: 
---

# Table of Contents

* TOC
{:toc}

I want to use my [BlackIce-II FPGA board](https://github.com/mystorm-org/BlackIce-II) as a development and 
debug board for designs that can later on be moved to an FPGA-only design, where the STM32 provides a bunch 
of support features.

For example, the STM32 could be used to load a new bitstream, be a JTAG master to the FPGA (when you put a 
TAP in the FPGA), drive QSPI if you need the transfer speed, etc.

To make that work, it's really necessary to be able to use GDB during the STM32 development.

# STLink Dongle

For that, you need an STLink v2 dongle that supports the Serial Wire Debug (SWD) protocol. 

Turns out: STLink v2 clones are dirt cheap. You can get them on AliExpress for as low as $1.80 if you can 
stomach a 30 day shipping delay. 

![STLink v2 Clone](/assets/blackice/STlinkv2-clone.jpg)

While looking for those, I also noticed an abundance of ridiculously cheap STM32F103 development boards, also
known as the [STM32 Blue Pill](https://stm32-base.org/boards/STM32F103C8T6-Blue-Pill.html).
They go for $2.50 on AliExpress as well. (These boards are also advertised on eBay for the same price, but 
they *also* take more than a month to arrive.)

I didn't want to wait that long, so I bought the STLink + STM32F108 board for $12 or so on Amazon. $8 extra meant 
I had the thing at my doorstep 2 days later.

# STM32F108 Blue Pill Development Board

Why the STM32F108? Because I already have a pile of microcontroller boards. Why not have one more? 

But also: there are plenty of tutorials on the web on how to get that board working with the STLink dongle 
and OpenOCD. So for just a few dollars more, I can replicate exactly the same configuration before I move on 
to great things.

I'm glad that I did.

I followed [these instructions](https://github.com/rogerclarkmelbourne/Arduino_STM32/wiki/Programming-an-STM32F103XXX-with-a-generic-%22ST-Link-V2%22-programmer-from-Linux) 
and, after swapping two wires, I had the thing going and was able to dump the contents of the STM32 flash 
contents. I'm currently not all that interested in getting C code to work on that one, but it should be pretty 
trivial, I think.

My drawer has a bunch of ATmega1280 boards from a previous life, an Adafruit Feather board with an ATmega and BLE, 
an LPC\<something\> board that I bought to see if it was still possible to an ARM7TDMI up and running (no issue 
with today's open source tools BTW), an Nvidia Jetson TK1 board, and some others that I'm forgetting. 

But none of them are as cheap as this little thing. And it way faster than ATmega based products. If you want 
get into this kind of tinkering, and you want to do it cheap, these STM32 Blue Pills are absolutely the way to go.

Anyway...

Next step: getting the STLink v2 to work with STM32L433 that sits on the BlackIce-II board.

# BlackIce-II with STM32L433

While the STM32F103 works fine with OpenOCD 0.9.0 that comes with my Ubuntu 16.04 installation, this is not the 
case for the STM32L433. You need the stm32l4x.cfg configuration file for that, which is part of 0.10.0.

I started by connecting 4 pins between the dongle and the BlackIce board: GND, SWCLK, SWDIO, and 5V, and while 
that *did* result in some LEDs lighting up... a little bit, the FPGA didn't really come up. So I'm now NOT connecting 
the 5V and using USB instead to power the board. 

The STLink 5V is clearly not powerful enough to drive the BlackIce board.

I'm currently still at this dead-end:

```
adapter speed: 500 kHz
adapter_nsrst_delay: 100
none separate
Info : Unable to match requested speed 500 kHz, using 480 kHz
Info : Unable to match requested speed 500 kHz, using 480 kHz
Info : clock speed 480 kHz
Info : STLINK v2 JTAG v17 API v2 SWIM v4 VID 0x0483 PID 0x3748
Info : using stlink api v2
Info : Target voltage: 3.234369
Error: init mode failed (unable to connect to the target)
in procedure 'init'
in procedure 'ocd_bouncer'
 Connecting RST of the STLink to RESET_ of the BlackIce connector didn't work either.
```

So I'm stuck with that for now.

What I really want to do first is to have a multi-function interface into the FPGA with multiple virtual channels: 
STDIO, debugger for a RISC-V CPU, waveforms etc. If I can't get this to work, I might restore to just JTAG for a 
while and not use the on-board STM32L. Or I might even use the STM32F103 as driver as a temporary replacement.

# Epilogue

I was able to get it work later, by connecting an additional GND wire between the STLink dongle and the
BlackIce-II board... See [here] http://localhost:4000/2018/03/24/Debugging-My-First-STM32-Program-on-the-BlackIce-II-Board.html).

