---
layout: post
title:  "Terasic vs Cheap Clone USB Blaster"
date:   2018-04-18 00:00:00 -1000
categories: 
---

I was supposed to work on getting the SiI9233 up and running on my eeColor Color3 board, but UPS delivered a nice 
package today:

![Silgent SDS 2304X scope]({{ "/assets/jtag/siglent_sds_2304x.jpeg" | absolute_url }})

I had an urgent need to measure something meaningful. 

Since I don't have a microscope (yet) to solder some really tiny wires on the TQFP144 of the SiI9233 (I want to record 
all I2C transactions to see how the thing gets configured), I decided to have a closer look at the difference between 
a high quality $50 Terasic USB Blaster and the cheap $3 Chinese clone that's available on AliExpress, eBay etc.

![Terasic vs Cheap Clone]({{ "/assets/jtag/terasic_vs_cheap_clone.jpg" | absolute_url }})

The Terasic version is supposed to be an Altera sanctioned design that has a chip USB to parallel converter chip from 
the FTDI family, and a small CPLD that converts the parallel data into JTAG (and some other formats). 

Some Chinese clones contains an STM32F101 micro controller, others are based on a PIC32 controller.

As I wrote [earlier](/2018/04/11/Dirt-Cheap-USB-Blaster-Clones-Considered-Harmful.html), the biggest issue with my 
cheap clone is that it doesn't work on my eeColor Color3 board.

So let's look at the signals as measured on the JTAG connector of the Color3 board.

# Terasic USB Blaster

![Terasic JTAG Transaction Overview]({{ "/assets/jtag/terasic_jtag_transaction_overview.png" | absolute_url }})

This is the first transaction that travels over the JTAG cable when you issue the "nios2-terminal" command.

The most important signal here is TCK, in yellow.

There are 3 major sections: during the prefix there are 8 slow clock cycles. In the middle there are 16 groups 
with fast clock cycles (each group is itself 8 clock cycles). And at the end you have a suffix with 2 slow clock cycles.

*For this investigation, it doesn't matter what gets transported when, but it's almost certain that the slow clock cycles 
are used to move the JTAG TAP from iDLE state to the scan DR or scan IR state, and that the fast clock groups are used to 
rapidly scan data in and out of a scan data register.*

When you zoom in on the slow clock cycles, you can measure a TCK frequency of 780kHz:

![Terasic JTAG Slow Phase]({{ "/assets/jtag/terasic_jtag_slow_phase.png" | absolute_url }})

Meanwhile, during a fast clock group, the clock toggles at 6MHz. This is expected: according to the 
[Altera documentation](https://www.altera.com/support/support-resources/knowledge-base/solutions/rd03112009_879.html), 
6MHz is exactly what one can expect from a USB Blaster.

In addition, there are roughly 3 idle cycles between a fast clock group.

![Terasic JTAG Fast Phase]({{ "/assets/jtag/terasic_jtag_fast_phase.png" | absolute_url }})


# Cheap Clone USB Blaster

And here's the equivalent of the cheap clone. For the overview, look at the upper set. The set of signals below 
that is a slightly zoomed in version of the one above.

![Cheap Clone JTAG Transaction Overview]({{ "/assets/jtag/cheap_clone_jtag_transaction_overview.png" | absolute_url }})

We see a similar pattern, but interestingly enough, it's not the same.

We have a prefix with 8 slow clocks, but in between the second and the third slow clock, there's a signal fast clock group.

In the middle we have the expected 16 fast clock groups. 

The suffix is really different, with 6 clock clocks but also a fast clock group in between.

While the Terasic was rock solid in its communication with the Color3 board. The cheap clone was never able to get reliable contact.

Zooming in on the slow clocks, we see a clock frequency of 192kHz.

![Cheap Clone JTAG Slow Phase]({{ "/assets/jtag/cheap_clone_jtag_slow_phase.png" | absolute_url }})

A fast clock group sets the clock at 12MHz instead of 6MHz.

![Cheap Clone JTAG Fast Phase]({{ "/assets/jtag/cheap_clone_jtag_fast_phase.png" | absolute_url }})

A really interesting difference is in the spacing between fast clock groups: for the Terasic, it was around 3 fast clocks 
(roughly 3x16us=48us). For the cheap clone, the spacing is huge: around 40 clock cycles (40x8us=320us).

![Cheap Clone JTAG Fast Spacing]({{ "/assets/jtag/cheap_clone_jtag_fast_spacing.png" | absolute_url }})

If we ignore for a second that the cheap clone doesn't work on this particular board, the biggest consequence of the cheap 
clone is that bulk transfers are much slower: (8+3)x16=176us per byte vs (8+40)x8=384us per byte.

It looks like the cheap clone is able to squeeze out bits really fast, but there's quite a bit of software overhead in processing 
the next byte in the USB packet. 

The Terasic doesn't have that problem: there is no software. All processing is done with a simply state machine.

What remains is the question about why the cheap clone doesn't work. It's not that it's broken: the clone works fine on my 
EP2C5T144 mini development board. My money is on the clock speed: even with the Terasic, the signal isn't super clean, and 
the one of the cheap clone looks a bit worse. (1) 

But the cheap clone runs TCK at exactly double the speed of the Terasic, and both devices only use a flimsy, cheap flat cable. 
It may be that 12MHz is really just pushing things too much. (2)

(1) Don't assume too much when looking at the signal quality: horrible things may have happened when setting up the measurement.

(2) Altera's newer USB Blaster II, which can run TCK at clocks of up to 24MHz, uses a much higher quality cable between the dongle and the JTAG connector.

