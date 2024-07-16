---
layout: post
title: A Hardware Interposer to Fix the Symmetricom SyncServer S200 GPS Week Number Rollover Problem
date:   2024-07-16 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my earlier blog post](/2024/07/14/Symmetricom-S200-NTP-Server-Setup.html),
I wrote about how to set up a SyncServer S200 as a regular NTP server, and how to 
install the backside BNC connectors to bring out the 10 MHz and 1PPS outputs. The
ultimate goal is to use the SyncServer as a lab timing reference.

However, at the end of that blog post, it's clear that NTP is not good enough to get
a precise 10 MHz clock: the output frequency was off by almost 100Hz! 

To get a more accurate output clock, you need to synchronize the SyncServer to the
GPS system so that it becomes a GPS disciplined oscillator (GPSDO) and a stratum 1
time keeping device.

The S200 has a GPS antenna input and a GPS receiver module inside, so in theory this 
should be a matter of connecting the right GPS antenna. But in practice it was simple
at all. That's because the GPS module in the SyncServer S200 is so old that it suffers
from the so-called Week Number Roll-Over problem.

In this blog post, I'll discuss what the problem is all about, and a custom hardware
solution that fixed the problem for me.

# IMPORTANT: Use the Right GPS Antenna!

Let me once again point out the importance of using the right GPS antenna to avoid damaging
it permanently due to over-voltage.

GPS antennas have active elements that amplify the received signal right at the point of reception
before sending it down the cable to the GPS unit. Most antennas need 3.3V or 5V that is supplied
through the GPS antenna connector, but Symmetricom S200 supplies 12V!

**Make sure you are using a 12V GPS antenna!**

Check out [my earlier blog post](/2024/03/23/Symmetricom-58532A-Power-Supply-Modification.html) 
for more information.

![Voltage present on S200 antenna connector](/assets/s200/s200_output_voltage.jpg)

# The Problem: SyncServer Refuses to Lock to GPS

When you connect a GPS antenna to a SyncServer in its original configuration, everything goes 
fine initially. The front panel report the antenna connection as  "Good", the number of satellites 
detected goes up, and the right location gets reported.

![GPS sees satellites, but unlocked](/assets/s200/GPS_unlocked.jpg)

But the most important "Status" field stays put at "Unlocked". This means that the SyncServer
refuses to lock its internal clock to the GPS unit.

This issue has been discussed to death in a number of EEVblog forum threads, but conclusion is always
the same: the Furuno GT-8031 GPS module suffers from the GPS Week Number Roll-Over (WNRO) issue and nothing
can be done about it other than replacing the GPS module with an after-market replacement one.

Let's first see what the WNRO issue is all about.

# The GPS Week Number Rollover Issue

The original GPS system used a 10-bit number to count the number of weeks, starting from
January 6, 1980. Every 19.7 years, this number rolls over from 1023 back to 0. 
The first rollover happened on August 21, 1999, the second on April 6, 2019, and the
next one will be on November 20, 2038. Check out 
[this US Naval Observatory presention](/assets/s200/usno_powers.pdf) for
some more information.

GPS module manufacturers have dealt with the issue is by using a "dynamic base year" or variable 
pivot year. When a device is, say, manufactured in 2012, 7 years before the 2019 rollover, it 
assumes that all week numbers higher than 697 are for years 2012 to 2019, and that numbers from 0 to 
697 are for the years 2019 and later.

![Dynamic date rollover graph](/assets/s200/dynamic_rollover_graph.png)

Such a device will work fine for the 19.7 years from 2012 until 2032.

With just a few bits of non-volatile storage, it is possible to make a GPS unit robust against this kind of 
rollover: if the last seen date by the GPS unit was 2019 and suddenly it sees a date of 1999, 
it can infer that there was a rollover and record in the storage that the next GPS epoch has started, 
but many modules don't do that. The only way to fix the issue is to update the module firmware.

Many SyncServer S2xx devices shipped with a Motorola M12 compatible module that is based on a
[Furuno GT-8031](https://www.furuno.com/en/products/gnss-module/GT-8031) 
which has a starting date of February 2, 2003 and rolled over on September 18, 2022. 
You can send a command to the module that hints the current date and that fixes the issue, 
but there is no SyncServer S200 firmware that supports that. Check out this 
[Furuno technical document](https://furuno.ent.box.com/s/fva29wqbcioqvd6mqxn5rt976dkaxudj) 
for more the rollover details.

Like all GPSDOs, the SyncServer S200 relies on the 1PPS output that comes out of the 
module to drive a PLL that lock the internal 10 MHz oscillator to the GPS system. This 1PPS signal 
is still present on the GT-8031 of my unit, and I verified with an oscilloscope that it matches
the 1PPS output of [my TM4313 GPSDO](/2023/07/09/TM4313-GPSDO-Teardown.html) as soon as it sees
a copule of satellites.

But there is something in the SyncServer firmware that depends on more than just the 1PPS signal 
because my S200 refuses to enter into "GPS Locked" mode, and the 10 MHz oscillator stays in free-running 
mode at the miserable frequency of roughly 9,999,993 Hz.

![Unlocked output frequency](/assets/s200/unlocked_output_frequency.jpg)


# Making the Furuno GT-8031 Work Again

There are aftermarket replacement modules out there with a rollover date that is far into the
future, but they are priced pretty high. There's the iLotus IL-GPS-0030-B Module which goes for
around $100 in AliExpress but that one has a rollover date on August 2024, and other modules
go as high as $240. The reason for these high prices is because these modules don't use a $5 
location GPS chip but chips that are specialized for accurate time keeping, such as the
[u-blox NEO/LEA series](https://www.u-blox.com/en/product/neolea-m8t-series).

Instead, I wondered if it's possible to make the GT-8031 send the right date to the S200 with a 
hardware interposer that sits between the module and motherboard. There were 2 options:

* intercept the date sent from the GPS module, correct it, and transmit it to the motherboard

    I tried that, but didn't get it work.

* send a configuration command to the GPS module to set the right date

    This method was [suggested by Alex Forencich on the time-nuts mailing list](https://febo.com/pipermail/time-nuts_lists.febo.com/2024-May/109101.html).
    He implemented it by patching the firmware of a microcontroller on his SyncServer S350 which
    might be the best solution eventually, but I made it work with the interposer.

It took 2 PCB spins, but I eventually came up with the following solution: 

[![GT-8031 Module on top of interposer](/assets/s200/module_on_top_of_interposer.jpg)](/assets/s200/module_on_top_of_interposer.jpg)
*Click to enlarge*

In the picture above, you see the GT-8031 plugged into my interposer that is in turn plugged into the
motherboard.

The interposer itself looks like this:

![Interposer without module](/assets/s200/interposer_without_module.jpg)

The design is very simple: an 
[RP2024-zero](https://www.waveshare.com/rp2040-zero.htm), a smaller variant of the Raspberry
Pico, puts itself in between the serial TX and RX wires that normally
go between the module and the motherboard. It's up to the software that runs on the RP2040 to determine
what to do with the data streams that run over those wires.

![Interposer diagram](/assets/s200/interposer_diagram.svg)

There are bunch of other connectors: the one at the bottom right is for observing the signals with
a logic analyzer. There are also 2 connectors for power. When finally installed, the interposer
gets powered with a 5V supply that's available on a pin that is conveniently located right behind
the GPS module. In the picture above, the red wires provides the 5V, the ground is connected through
the screws that hold the board in place.

The total cost of the board is as follows:

* PCB: $2 for 5 PCBs + $1.50 shipping = $3.50
* RP2040-zero: $9 on Amazon
* 2 5x2 connectors: $5 on Mouser + $5 shippingn = $10

Total: $22.50

The full project details can be found my [gps_interposer GitHub repo](https://github.com/tomverbeure/gps_interposer).

# How It Works

To arrive at a working solution, I recorded all the transactions on the serial port RX and TX and ran them
through a decoder script to convert them into readable GPS messages.

Here are the messages that are exchanged between the motherboard after powering up the unit:

```
>>> @@Cf - set to defaults command: [], [37], [13, 10] - 7 
>>> @@Gf - time raim alarm message: [0, 10], [43], [13, 10] - 9 
>>> @@Aw - time correction select: [1], [55], [13, 10] - 8 
>>> @@Bp - request utc/ionospheric data: [0], [50], [13, 10] - 8 
>>> @@Ge - time raim select message: [1], [35], [13, 10] - 8 
>>> @@Gd - position control message: [3], [32], [13, 10] - 8 
<<< @@Aw - time correction select: [1], [55], [13, 10] - 8 
    time_mode:UTC
<<< @@Co - utc/ionospheric data input: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], [44], [13, 10] - 29 
    alpha0:0, alpha1:0, alhpa2:0, alpha3:0
    beta0:0, beta1:0, alhpa2:0, beta3:0
    A0:0, A1:0
    delta_tls:0, tot:0, WNt:0, WNlsf:0, DN:0, delta_Tlsf:0
```

The messages above can be seen in the blue and green rectangles of this logic analyzer screenshot:

[![DSView logic analyzer screenshot](/assets/s200/dsview_screenshot.png)](/assets/s200/dsview_screenshot.png)
*Click to enlarge*

Note how the messages arrive at the interposer and immediately get forwarded to the other side. But the
transacation in red was generated by the interposer itself. It sends the `@@Gb` command. When the GPS module
is not yet locked to a satelllite, this command sends an initial estimate of the current date and time. The
[M12 User Guide](/assets/s200/m12/M12+UsersGuide.pdf) has the following to say about this command:

![Gb comment](/assets/s200/Gb_command.png)

The interposer sends a hinted date of May 4, 2024. When the GPS module receives date from its first satellite,
it corrects the date and time to the right value *but it uses the initial estimated date to correct for the
week number rollover*!

I initially placed the @@Gb command right after the @@Cf command that resets the module to default values, but
that didn't work. The solution was to send it after the initial burst of configuration commmands.

With this fix in place, it still takes almost 15 minutes before the S200 enters into GPS lock. You can
see this on the logic analyzer by an increased rate of serial port traffic:

[![S200 entering lock](/assets/s200/S200_entering_lock.png)](/assets/s200/S200_entering_lock.png)
*Click to enlarge*

# The Future: A Software-Only Solution

My solution uses a cheap piece of custom hardware. Alex's solution currently requires patching some 
microcontroller firmware and then flashing this firmware with $30 programming dongle. So both solutions 
require some hardware. 

A software-only solution should be possible though: the microcontroller gets reprogrammed during an official
SyncServer software update procedure. It should be possible to insert the patched microcontroller firmware into 
an existing software update package and then do an upgrade.

Since the software update package is little more than a tar-archive of the Linux disk image that runs the embedded
PC, it shouldn't be very hard to make this happen, but right now, this doesn't exist, and I'm happy with what
I have.

# The Result

The video below shows the 10 MHz output of the S200 being measured by a frequency counter that
uses a [calibrated stand-alone frequency standard](/2024/04/06/Guide-Tech-GT300-Frequency-Reference-Teardown.html)
as reference clock.

<iframe width="640" height="400" src="https://www.youtube.com/embed/h8rvT0RaLhQ?si=fCF7slB049l6xfdd" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

The stability of the S200 seems slightly worse than that of my TM4313 GPSDO, but it's close. Right now,
I don't have the knowledge yet to measure and quantify these differences in a scientifically acceptable way.


# References

* [Microsemi SyncServer S200 datasheet](/assets/s200/md_microsemi_s200_datasheet_vb_.pdf)
* [Microsemi SyncServer S200, S250, S250i User Guide](/assets/s200/syncserver-s2xx_997-01520-01_g2_md.pdf)

* [EEVblog - Symmetricom S200 Teardown/upgrade to S250](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250)
* [EEVblog - Symmetricom Syncserver S350 + Furuno GT-8031 timing GPS + GPS week rollover](https://www.eevblog.com/forum/metrology/symmetricom-syncserver-s350-furuno-gt-8031-timing-gps-gps-week-rollover/)
* [EEVblog - Synserver S200 GPS lock question](https://www.eevblog.com/forum/metrology/synserver-s200-gps-lock-question/msg5339408)

* [Furuno GPS/GNSS Receiver GPS Week Number Rollover](https://furuno.ent.box.com/s/fva29wqbcioqvd6mqxn5rt976dkaxudj)

# Footnotes

