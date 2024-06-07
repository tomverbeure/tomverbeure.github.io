---
layout: post
title: A Hardware Interposer to Fix the Symmetricom SyncServer S200 GPS Week Number Rollover Problem
date:   2024-06-01 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The [Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com) 
runs every month from March to September and then goes on a hiatus for 6 months, so when 
the new March episode hits, there is a ton of pent-up demand... and supply: inevitably,
some spouse has reached their limit during spring cleaning and wants a few of those boat 
anchors gone. You do not want to miss the first flea market of the year, and you better
come early, think 6:30am, because the good stuff goes fast.

But success is not guaranteed: I saw a broken-but-probably-repairable HP 58503A GPS
Time and Frequency Reference getting sold right in front of me for just $40. And while
I was able to pick up a very low end HP signal generator and Fluke multimeter for $10,
at 8:30am, I was on my way back to the car unsatisfied.

Until *that* guy and his wife, late arrivals, started unloading stuff from their trunk
onto a blanket. There it was, right in front of me, a 
[Stanford Research Systems SR620 universal counter](https://thinksrs.com/products/sr620.html). 
I tried to haggle on the SR620 but was met with a "You know what you're doing and what 
this is worth." Let's just say that I paid the listed price which was still a crazy good 
deal. I even had some cash left in my pocket.

Which is great, because right next to the SR620 sat a pristine looking Symmetricom
SyncServer S200 with accessories for the ridiculously low price of $60.

[![Flea Market Haul](/assets/s200/fleamarket_haul.jpg)](/assets/s200/fleamarket_haul.jpg)

I've never left the flea market more excited.

I didn't really know what a network time server does, but since it said *GPS*
time server, I hoped that it could work as a GPSDO with a 10MHz reference clock and a 1 
pulse-per-second (1PPS) synchronization output. But even if not, I was sure that I'd learn 
something new, and worst case I'd reuse the beautiful rackmount case for some future project.

Turns out that out of the box a SyncServer S200 can not be used as a GPSDO, but its
close sibling, the S250, can do it just fine, and it's straightforward to do the conversion. 
A bigger problem was an issue with the GPS module due to the week number rollover (WNRO)
problem.

In this blog post, I go through the steps required to bring from a mostly useless
S200 back to life and how to add the connectors for 10MHz and 1PPS output, which allowed it
to do double duty as a GPSDO.

Some of what is described here is based on discussions on EEVblog forum such as 
[this one](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250).
I hope you'll find it useful.

# What was the SyncServer S200 Supposed to be Used For?

Symmetricom was acquired by Microsemi, and the SyncServer S200 is now obsolete, but
Microsemi still has a [data sheet](/assets/s200/md_microsemi_s200_datasheet_vb_.pdf)
on their website.

Here's what it says in the first paragraph:

> The SyncServer S200 GPS Network Time Server synchronizes clocks on servers for large
> or expanding IT enterprises and for the ever-demanding high-bandwidth Next Generation
> Network. Accurately synchronized clocks are critical for network log file accuracy,
> security, billing systems, electronic transactions, database integrity, VoIP, and
> many other essential applications.

There's a lot more, but one of the key aspects of a time server like this is that it
uses the [Network Time Protocol (NTP)](https://en.wikipedia.org/wiki/Network_Time_Protocol), which...

> ... is a networking protocol for clock synchronization between computer systems over 
> packet-switched, variable-latency data networks.

The SyncServer S200 is a [Stratum 1](https://en.wikipedia.org/wiki/Network_Time_Protocol#Clock_strata) 
level device. While it does not act as a Stratum 0 oracle of truth timing reference, it
directly derives the time from a Stratum 0 device, in this case the GPS system.

When the GPS signal disappears, a SyncServer falls back to Stratum 2 mode where it retrieves
the time from other Stratum 1 devices (e.g. other NTP-capable time servers on the network) or 
it switches to hold-over mode where it lets an internal oscillator run untethered, without 
being locked to the GPS system.

The S200 has 3 oscillator options:

* a TCXO with a drift of 21ms per day
* an OCXO with a drift of 1ms per day
* a Rubidium atomic clock with drift of 25us (!) per day

Mine has the OCXO option.

It's clear that the primary use case of the S200 is not to act as a lab clock or frequency
reference, but something that belongs in a router cabinet.

# The SyncServer S200 Outside and Inside

The front panel has 2 USB type-A ports, an RS-232 console interface, a 
[vacuum fluorescent display](https://en.wikipedia.org/wiki/Vacuum_fluorescent_display) (VFD), 
and a bunch of buttons.

[![S200 front view](/assets/s200/S200_front_view.jpg)](/assets/s200/S200_front_view.jpg)
*Click to enlarge*

VFDs have a tendency to degrade over time, but mine is in perfect shape.

[![S200 rear view](/assets/s200/S200_rear_view.jpg)](/assets/s200/S200_rear_view.jpg)
*Click to enlarge*

In the back, we can see a power switch for the 100-240VAC mains voltage[^1],
a GPS antenna connection, a [Sysplex Timer-Out](/assets/s200/sysplex_timer.pdf) interface, 
and 3 LAN ports.

[^1]:There are also versions for telecom applications that are powered with 40-60 VDC.

Let's see what's inside:

[![S200 inside view](/assets/s200/S200_inside_view.jpg)](/assets/s200/S200_inside_view.jpg)
*Click to enlarge*

Under the heatshink with the blue heat transfer pad sits an off-the-shelf embedded
PC motherboard with a 500MHz AMD Geode x86 CPU with 256MB of DRAM. Not all SyncServer S200 
models use the same motherboard, some of them have a VIA Eden ESP 400MHz processor. I recorded
this [`boot.log`](/assets/s200/boot.log) file that contains some low level details of the system.
The PC is running [MontaVista Linux](https://en.wikipedia.org/wiki/MontaVista#Linux), 
a commercial Linux distribution for embedded devices.

At the bottom left sits a little PCB for the USB and RS-232 ports. There are also two cables 
for the VFD and the buttons.

On the right side of the main PCB we can see a Vectron OCXO that will create the 10MHz clock 
and a 512MB CompactFlash card with the operating system. There's still plenty of room for a 
Rubidium atomic clock module. 

At the top left sits a Furuno GT-8031 GPS module that is compatible with the Motorola
M12M modules. There's a bunch of connectors, and, very important, 3 unpopulated connector
footprints. 

When looking at it from a different angle, we can also see 6 covered up holes that line up with those
3 unpopulated footprints:

[![S200 inside back connectors](/assets/s200/S200_inside_back_connectors.jpg)](/assets/s200/S200_inside_back_connectors.jpg)
*Click to enlarge*

Let's just cut to the chase and show the backside of the next model in the SyncServer product line, the S250: 

![S250_BNC_connectors](/assets/s200/S250_BNC_connectors.png)

![S250_BNC_connectors_diagram](/assets/s200/S250_BNC_connectors_diagram.png)

Those 6 holes holes are used for the input and output for the following 3 signals:

* 10MHz
* 1PPS
* IRIG

We are primarily interested in the 10MHz and 1PPS outputs, of course.

![Probe on 10MHz output](/assets/s200/probe_on_10MHz_output.jpg)

The BNC connectors may be unpopulated, but the driving circuit is not. When you probe
the hole for the 10MHz output, you get this sorry excuse of what's supposed to be a
sine wave:

![10MHz signal on BNC hole](/assets/s200/10MHz_output.png)

There's also a 50% duty cycle 1PPS signal present on the other BNC footprint.

# IMPORTANT: Use the Right GPS Antenna!

Before continuing, let's interrupt with a short but important service message:

GPS antennas have active elements that amplify the signal at the point of reception
before sending it down the cable to the GPS unit. Most antennas require 3.3V or 5V power, but the
Symmetricom S200 supplies 12V on its GPS antenna connector.

**Make sure you are using a 12V GPS antenna!**

Check out [my earlier blog post](/2024/03/23/Symmetricom-58532A-Power-Supply-Modification.html) 
for more information.

# Installing the Missing BNC Connectors

The first step is to install the missing BNC connectors. The connectors themselves
are [Amphenol RF 031-6577](https://www.amphenolrf.com/031-6577.html). They are
expensive: I got 3 of them for [$17.23 a piece from Mouser](https://www.mouser.com/ProductDetail/523-31-6577).
Chances are that you'll never use the IRIG port, so you can make do with only 2 connectors
to save yourself some money.

![Amphenol RF 031-6577 connector](/assets/s200/amphenol_bnc_connector.jpg)

You'll need to remove the whole main PCB from the case, which is a matter of
removing all the screws and some easy to disconnect cables and then taking it out. 
The PCB rests on a bunch of spacers for the screws. When you slide the PCB out, you need 
to be very careful to not scrape the bottom of the PCB against these spacers!

Next up is opening up the covered holes. The plastic that covers these holes is quite
strong. I used a box cutter to remove the plastic and it took quite a bit of time to do
so. 

![6 covered BNC holes](/assets/s200/S200_6_covered_holes.jpg)

The holes are not perfectly round: they have a flat section at the top. You need to
open up the holes as much as possible because during reassembly the BNC connectors will
have to go through them and want this to go as smoothly without putting a lot of strain
on the PCB.

![6 opened-up BNC holes](/assets/s200/S200_6_uncovered_holes.jpg)

The end result isn't commercial product quality, but it's good enough for something
that will stay hidden at the back of the instrument.

Installing the BNC connectors is easy: plug them in and solder them down...

![BNC connectors installed](/assets/s200/S200_bnc_connectors_installed.jpg)

Due to the imperfectly cut BNC holes, installing the main PCB back into the chassis will
be harder than removing it, so, again, be careful about those spacers at the bottom of the
case to prevent damaging the PCB!

The end result looks clean enough:

![S200 backside with new connectors](/assets/s200/S200_backside_with_new_connectors.jpg)


# The GPS Week Number Rollover Issue

The original GPS system used a 10-bit number to count the number of weeks, starting from
January 6, 1980. Every 19.7 years, this number rolls over from 1023 back to 0. 
The first rollover happened on August 21, 1999, the second on April 6, 2019, and the
next one will be on November 20, 2038. Check out 
[this US Naval Observatory presention](/assets/s200/usno_powers.pdf) for
some more information.

GPS module manufacturers have dealt with the issue is by using a "dynamic base year" or variable 
pivot year. When a device is, say, manufactured in 2016, 3 years before the 2019 rollover, it 
assumes that all week numbers higher than 868, 1024-3*52, are for years 2016 to 2019, and that 
numbers from 0 to 867 are for the years 2019 and later.

![Dynamic date rollover graph](/assets/s200/dynamic_rollover_graph.png)

Such a device will work fine for the 19.7 years from 2016 until 2035.

With a bit of non-volatile storage, it is possible to make a GPS unit robust against this kind of 
rollover: if the last seen date by the GPS unit was 2019 and suddenly it sees a date of 1999, 
it can infer that there was a rollover and record that in the storage, but many modules don't do 
that. The only way to fix the issue is to update the module firmware.

Many SyncServer S2xx devices shipped with a Motorola M12 compatible module that is based on a
[Furuno GT-8031](https://www.furuno.com/en/products/gnss-module/GT-8031) 
which has a starting date of February 2, 2003 and rolled over on September 18, 2022. 
You can send a command to the module that hints the current date and that fixes the issue, 
but there is no SyncServer S200 firmware that supports that. Check out this 
[Furuno technical document](https://furuno.ent.box.com/s/fva29wqbcioqvd6mqxn5rt976dkaxudj) 
for more the rollover details.

Like all GPSDOs, the SyncServer S200 primarily relies on the 1PPS output that comes out of the 
module to lock its internal 10MHzthe  oscillator to the GPS system, and this 1PPS signal is still present on
the GT-8031 of my unit. But there is something in the SyncServer firmware that depends on more than just 
the 1PPS signal because my S200 refuses to enter into "GPS Locked" mode, and the 10MHz oscillator
stays in free-running mode at the miserable frequency of roughly 9,999,993 Hz.

![Unlocked output frequency](/assets/s200/unlocked_output_frequency.jpg)

# Upgrading to an iLotus IL-GPS-0030-B Module

The normal way to work around the week number rollover issue is to replace the GT-8031 with a different
module that has a later rollover date. Over the years, people have used various solutions but
these have in turn had their own rollover.

I purchased an iLotus IL-GPS-0030-B as replacement module. They go for close to $100 on AliExpress.

![GPS locked with new module](/assets/s200/GPS_locked_with_new_module.jpg)

After replacing the GT-8031, the S200 enters into GPS Locked status, which is good, but after
some more research (which I should have done before spending that kind of money on it!) I discovered 
that it has a [rollover date of August 17, 2024](/assets/s200/M12M-2019-roll-over-and-base-dates-C.pdf):

![IL-GPS-0030-B rollover date](/assets/s200/IL-GPS-0030-B rollover.png)

But it gets worse: I snooped and decoded the serial data stream from the module to the 
motherboard and I found that that my module already had its rollover event. 

Still, one way or the other, the S200 was able to get into GPS Lock and the 10MHz output clock 
was nicely in sync with my [TM4313 GPSDO](/2023/07/09/TM4313-GPSDO-Teardown.html) which is a major
improvement over the GT-8031.

So there's contradicting information out there, but there's still the possibility that on August 17, 2024, 
this expensive module will become a doorstop just the same. 

# Making the Furuno GT-8031 Work Again

There are other aftermarket replacement modules out there with a rollover date that is far into the
future, but they are priced at $240. Instead, I wondered if it's possible to make the GT-8031 or 
IL-GPS-0030-B send the right date to the S200 with a hardware interposer that sits between the module 
and motherboard. There were 2 options:

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

The video below shows the 10MHz output of the S200 being measured by a frequency counter that
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

