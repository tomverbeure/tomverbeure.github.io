---
layout: post
title: Upgrading Symmetricom SyncServer S200 and Fixing the GPS Week Number Rollover Problem
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

I didn't really know what one does with a network time server, but since it said *GPS*
time server, I hoped that it could work as a GPSDO with a 10MHz reference clock and a 1 
pulse-per-second (1PPS) synchronization output.

But even if not, I was sure that I'd learn something new, and worst case I'd reuse the
beautiful rackmount case for some future project.

Turns out that out of the box a SyncServer S200 can not be used as a GPSDO, but its
close siblings can do it just fine, and it's straightforward to do the conversion. There
was also an issue with the GPS module that needed to be fixed.

In this blog post, I go through all the steps required to go from a mostly useless
S200 to a fully functional GPSDO.

While most of what is described here is based on discussions on EEVblog forum such as 
[this one](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250),
what I found missing was a step-by-step recipe and a larger context. I hope you'll find
it useful.

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

When the GPS signal falls away, a SyncServer falls back to Stratum 2 mode where it retrieves
the time from other Stratum 1 devices (e.g. other NTP-capable time servers on the network) or 
it switches to hold-over mode where it lets an internal oscillator run untethered, without 
being locked to the GPS system.

The S200 has 3 oscillator options:

* a TCXO with a drift of 21ms per day
* an OCXO with a drift of 1ms per day
* a Rubidium atomic clock with drift of 25us (!!!) per day

Mine has the OCXO option.

It's clear that the primary use case of the S200 is not to act as a lab clock or frequency
reference, but something that belongs in a router cabinet.

# The SyncServer S200 Out- and Inside

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

Under the heatshink with the the blue heat transfer pad sits an off-the-shelf embedded
PC motherboard with a 500MHz AMD Geode x86 CPU with 256MB of DRAM. Not all SyncServer S200 
models use the same motherboard. Some of them use a VIA Eden ESP 400MHz Processor. For some gory
details about the CPU system, checkout this [`boot.log`](/assets/s200/boot.log) file that
I recorded. The CPU is running [MontaVista Linux](https://en.wikipedia.org/wiki/MontaVista#Linux), 
a commercial Linux distribution for embedded devices.

At the bottom left sits a little PCB for the USB and RS-232 ports. There are also two cables 
for the VFD and the buttons.

On the right side we can see a Vectron OCXO that will create 10MHz clock and a 512MB CompactFlash 
card. There's still plenty of room for a Rubidium atomic clock module. 

At the top left sits a Furuno GT-8031H GPS module that is compatible with the Motorola
M12M modules. There's a bunch of connectors, and, very important 3 unpopulated connector
footprints. Let's have a closer look at those:

[![S200 inside back connectors](/assets/s200/S200_inside_back_connectors.jpg)](/assets/s200/S200_inside_back_connectors.jpg)
*Click to enlarge*

Of interest are the 6 covered holes for BNC connectors. Let's just cut to the chase and show
the backside of the next model in the SyncServer product line, the S250: 

![S250_BNC_connectors](/assets/s200/S250_BNC_connectors.png)

![S250_BNC_connectors_diagram](/assets/s200/S250_BNC_connectors_diagram.png)

Those holes are used for the input and output for the
following 3 signals:

* 10MHz
* 1PPS
* IRIG

We are primarily interested in the 10MHz and 1PPS outputs, of course.

![Probe on 10MHz output](/assets/s200/probe_on_10MHz_output.jpg)

The BNC connectors may be unpopulated, but the driving circuit is not. When you probe
the hole for the 10MHz output, you get this sorry excuse of what's supposed to be a
sine wave:

![10MHz signal on BNC hole](/assets/s200/10MHz_output.png)

There's also a 50% duty cycle 1PPS signal on the other BNC hole.

# IMPORTANT: Use the Right GPS Antenna!

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
Chances are that you won't need the IRIG port, so you can make do with only 2 connectors
to save yourself some money.

![Amphenol RF 031-6577 connector](/assets/s200/amphenol_bnc_connector.jpg)

You'll need to remove the whole main PCB from the case, which is a matter of
removing all the screws and some easy to disconnect cables and then taking it out. 
The PCB rests on a bunch of spacers for the screws. When you slide the PCB out, you need 
to be very careful to not scrape the bottom of the PCB against these spacers!

Next up is opening up the covered holes. The plastic that covers that holes is quite
strong. I used a box cutter to remove the plastic and it took quite a bit of time to do
so. 

![6 covered BNC holes](/assets/s200/S200_6_covered_holes.jpg)

The holes are not perfectly round: they have a flat section at the top. You need to
open up the holes as much as possible because during reassembly the BNC connectors will
have to go through them and want this to go as smoothly without putting a lot of strain
on the PCB.

![6 opened-up BNC holes](/assets/s200/S200_6_uncovered_holes.jpg)

The end result isn't exactly commercial product quality, but it's good enough for something
that will stay hidden at the back of the instrument.

Installing the BNC connectors is easy: plug them in and solder them down...

![BNC connectors installed](/assets/s200/S200_bnc_connectors_installed.jpg)

Due to the imperfectlly cut BNC holes, installing the main PCB back into the chassis will
be harder than removing it, so, again, be careful about those spacers at the bottom of the
case damaging the PCB!

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

Many SyncServer S2xx devices shipped with an Motorola M12 compatible module that is based on a
Furuno GT-8031 which uses a starting date of February 2, 2003 and rolled over on September 18, 2022. 
You can send a command to the module that hints the current date and that fixes the issue, 
but there is no SyncServer S200 firmware that supports that. Check out this 
[Furuno technical document](https://furuno.ent.box.com/s/fva29wqbcioqvd6mqxn5rt976dkaxudj) 
for more the rollover details.

Like all GPSDOs, the SyncServer S200 primarily relies on the 1PPS output that comes out of the 
module to lock its internal 10MHz oscillator to the GPS system, and this 1PPS signal is still present on
the GT-8031 of my unit. But there is something in the SyncServer firmware that depends on more than just 
the 1PPS signal because my S200 refuses to enter into "GPS Locked" mode, and the 10MHz oscillator
stays in free-running mode at miserable frequency of roughly 9,999,993 Hz.

![Unlocked output frequency](/assets/s200/unlocked_output_frequency.jpg)

# Upgrading to an iLotus IL-GPS-0030-B Module

The normal way to work around the week rollover issue is to replace the GT-8031 with a different
module that has a later rollover date. Over the years, people have used various solutions but
these have in turn had their own rollover.

I purchased a IL-GPS-0030-B as replacement module. They go for close to $100 on AliExpress.

![GPS locked with new module](/assets/s200/GPS_locked_with_new_module.jpg)

After replacing the GT-8031H, the S200 enters into GPS Locked status, which is good, but after
some more research (which I should have done before spending that kind of money on it!) I discovered 
that it has a [rollover date of August 17, 2024](/assets/s200/M12M-2019-roll-over-and-base-dates-C.pdf):

![IL-GPS-0030-B rollover date](/assets/s200/IL-GPS-0030-B rollover.png)

But it gets worse: I snooped and decoded the serial data stream from the module to the 
motherboard and I found that that my module already had its rollover event. 

Still, one way or the other, the S200 was able to get into GPS Lock and the 10MHz output clock 
was nicely in sync with my [TM4313 GPSDO](/2023/07/09/TM4313-GPSDO-Teardown.html). That's definitely
an improvement over the GT-8031.

So there's contradicting information out there, but there's still the possibility that on August 17, 2024, 
this expensive module will become a doorstop just the same. 

# Making the Furuno GT-8031 Work Again

There are some aftermarket replacement modules out there with a rollover date that is far into the
future, but they are priced at $240.

Instead, I wondered if it's possible to make the GT-8031 or IL-GPS-0030-B send the right date to the
S200 with a hardware interposer that sits between the module and motherboard. There were 2 options:

* intercept the date sent from the GPS module, correct it, and transmit it to the motherboard
* send a configuration command to the GPS module to set the right date

It took 2 PCB spins, but I eventually came up with the following solution: 

[![GT-8031 Module on top of interposer](/assets/s200/module_on_top_of_interposer.jpg)](/assets/s200/module_on_top_of_interposer.jpg)
*Click to enlarge*

In the picture above, you see the GT-8031 plugged into an interposer that is in turn plugged into the
motherboard.

The interposer itself looks like this:

![Interposer without module](/assets/s200/interposer_without_module.jpg)

The design is very simple: a RP2024-zero puts itself in between the serial TX and RX wires that normally
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


# Furuno GT-8031H:

When the S200 isn't able to lock its local OCXO to the GPS in, the 10MHz frequency is terribly
off by 7Hz:


(For this measurement, I'm using the 10MHz of my TM4313 GPSDO as clock reference.)

You can also see how the 1PPS output of S200 differs from the TM4313 output by 42ms.
Note that this is despite seeing 9 satellites.

The screen will show 

* Antenna: Good
* Status: Unlocked
* Source: None
* GPS In: Unlocked
* 1PPS In: Unlocked
* 10MHz In: Unlocked

# Feature Comparison

|        | S200 | S250 | S250i |
|-------:|:----:|:----:|:-----:|
|    GPS |   X  |   X  |       |
|   1PPS |      |   X  |   X   |
| 10 MHz |      |   X  |   X   |
| IRIG-B |      |   X  |   X   |

# Installing the New Connectors


# Cloning the Existing Drive

**Linux**

```sh
$ df
```

```
/dev/sdb7          97854         2     92720   1% /media/tom/_tmparea
/dev/sdb2           8571       442      7683   6% /media/tom/_persist
/dev/sdb1          17047      2510     13597  16% /media/tom/_boot
/dev/sdb5         173489     69985     94256  43% /media/tom/_fsroot1
/dev/sdb6         173489     69986     94255  43% /media/tom/_fsroot2
```

```sh
$ sudo dd if=/dev/sdb of=flash_contents_orig.img bs=1M
```

```
[sudo] password for tom: 
488+1 records in
488+1 records out
512483328 bytes (512 MB, 489 MiB) copied, 40.6726 s, 12.6 MB/s
```

Notice the `sync` command!

```sh
$ sudo dd if=flash_contents_orig.img of=/dev/sdb bs=1M && sync
```

```
488+1 records in
488+1 records out
512483328 bytes (512 MB, 489 MiB) copied, 0.143977 s, 3.6 GB/s
```

**Windows**

Use the [HDD Raw Copy Tool](https://hddguru.com/software/HDD-Raw-Copy-Tool/).

# Getting Started

* Reset to factor default settings
* Use a static IP address

    You won't be able to connect with your browser otherwise!

![S200 web home screen](/assets/s200/S200_home_screen.png)

# 10MHz Out

* 2.60Vpp AC

![10MHz output on oscilloscope](/assets/s200/10MHz_output.png)

# Satellite status

```sh
ssh admin@192.168.1.201
gpsstrength
```

By default, there's only a simply command line processor the knows a few commands.

# Enable SSH root access

* Inspired by [this EEVblog post](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250/msg2952418/#msg2952418)

Boot procedure:
* Boots `_fsroot1` or `_fsroot2`.
* Overwrites /etc and /var with config.tar.gz data in the /persists partion.
* So you need to patch the config.tar.gz file!

* Use web interface to dump `syncServer.bkp` file

```sh
mkdir bak
cd bak
sudo tar xf ../syncServer.bkp
```

```
tom@zen:~/projects/tomverbeure.github.io/assets/s200/bak$ ll
total 444
drwxrwxr-x 2 tom  tom    4096 Mar 16 23:32 ./
drwxrwxr-x 4 tom  tom    4096 Mar 16 23:32 ../
-rw-r--r-- 1 root root 439681 Jan  3  2006 config-1.2.tar.gz
-r--r--r-- 1 root root    421 Jan  3  2006 persist.conf
```

```sh
sudo tar xfz config-1.2.tar.gz
```

```
sudo gvim etc/shadow
sudo gvim etc/ssh/sshd_config
sudo rm config-1.2.tar.gz
sudo tar cfz config-1.2.tar.gz ./etc ./var
sudo rm -fr ./etc ./var
tar cf ../syncServer.patched.bkp config-1.2.tar.gz persist.conf
cd ..
rm -fr ./bak
```


# Decoding M12 messages

## Working module

Initial configuration:

* Send @@Cf: set to all defaults
* Send @@Gf: set time raim alarm to 1000ns
    Receiver Autonomous Integrity Monitoring
    Tests whether or not GPS signals from different satellites are consistent.
* Send @@Aw: time correction select. 
    Set UTC mode (1) instead of GPS mode (0)
    This determines what kind of time the @@Ha and the @@Hn message will
    send back.
    If no almanac data is present, @@Ha will return GPS time until
    it receives that data. Then it switches automatically to UTC time.
* Send @@Bp: request utc/ionospheric data
    Mode 0: polled mode
* Send @@Ge: time raim select
    1: enable
* Send @@Gd: position control mode
    3: auto-survey

Before lock:


* S200 polls every 8 seconds with Bp message for atmospheric data. Module
  return Co message. Uses mode 0 - polled.
* Module automatically sends Ha message (12 channel position/status/data) every second
* Every 3 seconds there is also an automatic Hn message (time raim status message). The
  3 second rate was programmed right at the start.


After lock:
* Module polls Bp (atmospheric data, polled) message, Bj message (leap second status, polled), 
  and a Gj message (leap second pending)
* Module automatically sends Ha message (12 channel position/status/data) every second


* Time reports for both old and new traces on 2024/5/5: 2004/9/19. Delta is 1024 weeks...
* Differences

    * old: Hn: time_accuracy_est of 0, new is 65535.
    * old: Hn: fract_local_time:0, new: various numbers
    * old: Ha: iode is 0, new is various values.
            "Issue Of Data, Ephemeris"
            Used to identify updated GPS Ephemeris data.

        [Ephemerides](https://www.e-education.psu.edu/geog862/node/1737)
    * new: Bj starts appearing soon after Hn clock_bias and osc_offset becomes non-zero!
          cold_start and insufficient_sats also switches from 1 to 0. 
        In old, all these fields remain 0 or 1 resp. except insufficient_sats which is always.
    * new: Co has non-zero values for ionospeheric data. Old always has zeros, but I don't
        think this matters.

* Experiments:

    * old: force cold_start to 0.
    * new: Hn: force fract_local_time to 0
    * new: Hn: force time_accuracy_est to 0
    * new: Ha: force iode to 0
    * old: Ha: force iode to some random value?

# References

* [Microsemi SyncServer S200 datasheet](/assets/s200/md_microsemi_s200_datasheet_vb_.pdf)
* [Microsemi SyncServer S200, S250, S250i User Guide](/assets/s200/syncserver-s2xx_997-01520-01_g2_md.pdf)
* [EEVblog - Symmetricom S200 Teardown/upgrade to S250](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250)

* [GPIO Labs](https://gpio.com/)

    Has a bunch of GNSS related products, such as this 
    [USB Bias Tee with GNSS band filter and 3.3V supply](https://gpio.com/collections/gnss/products/gnss-filtered-bias-tee-gps-l1-l5-glonass-beidou-navic-1100-1700-mhz)
    or this universal [USB Bias Tee](https://gpio.com/collections/bias-tees/products/usb-bias-tee-operates-from-10mhz-7000mhz).

* [DIY bias tee](https://discussions.flightaware.com/t/power-bias-tee-from-usb-port/66181)

* [HEOL S200 S250 S300 S350 XLi servers GPS upgrade](https://trends.directindustry.com/heol-design/project-57722-1149241.html)

* [EEVblog - Symmetricom Syncserver S350 + Furuno GT-8031 timing GPS + GPS week rollover](https://www.eevblog.com/forum/metrology/symmetricom-syncserver-s350-furuno-gt-8031-timing-gps-gps-week-rollover/)

* [EEVblog - Synserver S200 GPS lock question](https://www.eevblog.com/forum/metrology/synserver-s200-gps-lock-question/msg5339408)

* [Furuno GPS/GNSS Receiver GPS Week Number Rollover](https://furuno.ent.box.com/s/fva29wqbcioqvd6mqxn5rt976dkaxudj)

* [USNO GPS Time Transfer](https://www.cnmoc.usff.navy.mil/Our-Commands/United-States-Naval-Observatory/Precise-Time-Department/Global-Positioning-System/USNO-GPS-Time-Transfer/)

    As of December 31st, 2016, GPS is ahead of UTC by 18 leap seconds.

* [What are satellite time, GPS time, and UTC time?](https://aviation.stackexchange.com/questions/90839/what-are-satellite-time-gps-time-and-utc-time)

# Footnotes

