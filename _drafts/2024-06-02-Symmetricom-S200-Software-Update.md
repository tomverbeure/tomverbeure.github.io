---
layout: post
title: Setting Up a Symmetricom SyncServer S200 Network Time Protocol Server
date:   2024-06-02 00:00:00 -1000
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
at 8:30am I was on my way back to the car, unsatisfied.

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
A bigger problem was an issue with the GPS module due to the 
[week number rollover (WNRO)](https://en.wikipedia.org/wiki/GPS_week_number_rollover)
problem.

In this and upcoming blog posts, I go through the steps required to bring a mostly useless
S200 back to life, how to add the connectors for 10MHz and 1PPS output, which allowed it
to do double duty as a GPSDO, and how to convert it into a full S250.

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

The SyncServer S200 is a [stratum 1](https://en.wikipedia.org/wiki/Network_Time_Protocol#Clock_strata) 
level device. The stratum level indicates the hierarchical distance to an authorative atomic 
reference clock.  While it does not act as a stratum 0 oracle of truth timing reference, it
can derive the time directly from a stratum 0 device, in this case the GPS system.

When the GPS signal disappears, a SyncServer can fall back to stratum 2 mode if it can retrieve
the time from other stratum 1 devices (e.g. other NTP-capable time servers on the network) or 
it can switch to hold-over mode, where it lets an internal oscillator run untethered, without 
being locked to the GPS system.

The S200 has 3 oscillator options:

* a TCXO with a drift of 21ms per day
* an OCXO with a drift of 1ms per day
* a rubidium atomic clock with drift of only 25us per day

Mine has the OCXO option.

It's clear that the primary use case of the S200 is not to act as a lab clock or frequency
reference, but something that belongs in a router cabinet.

# IMPORTANT: Use the Right GPS Antenna!

Before continuing, let's interrupt with a short but important service message:

GPS antennas have active elements that amplify the received signal right at the point of reception
before sending it down the cable to the GPS unit. Most antennas need 3.3V or 5V that is supplied
through the GPS antenna connector, but Symmetricom S200 supplies 12V!

**Make sure you are using a 12V GPS antenna!**

Check out [my earlier blog post](/2024/03/23/Symmetricom-58532A-Power-Supply-Modification.html) 
for more information.

![Voltage present on S200 antenna connector](/assets/s58532a/s200_output_voltage.jpg)

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
a BNC connector for the GPS antenna, a [Sysplex Timer-Out](/assets/s200/sysplex_timer.pdf) interface, 
and 3 LAN ports.

[^1]:There are also versions for telecom applications that are powered with 40-60 VDC.

Let's see what's inside:

[![S200 inside view](/assets/s200/S200_inside_view.jpg)](/assets/s200/S200_inside_view.jpg)
*Click to enlarge*

Under the heatshink with the blue heat transfer pad sits an off-the-shelf embedded
PC motherboard with a 500MHz AMD Geode x86 CPU with 256MB of DRAM. Not all SyncServer S200 
models use the same motherboard, some of them have a VIA Eden ESP 400MHz processor. Using the
front panel RS-232 serial port, I recorded this [`boot.log`](/assets/s200/boot.log) file that contains 
some low level details of the system.
The PC is running [MontaVista Linux](https://en.wikipedia.org/wiki/MontaVista#Linux), 
a commercial Linux distribution for embedded devices.

At the bottom left sits a little PCB for the USB and RS-232 ports. There are also two cables 
for the VFD and the buttons.

On the right side of the main PCB we can see a Vectron OCXO, the same brand as the huge
OCXO that you can find in the [GT300 frequency standard](/2024/04/06/Guide-Tech-GT300-Frequency-Reference-Teardown.html) 
of my home lab. It creates the 10MHz stable clock that's used for
time keeping. A 512MB CompactFlash card contains the operating system. There's still plenty 
of room for a Rubidium atomic clock module. It should be possible to 
[upgrade my S200 with a Rubidium standard](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250/msg2764532/#msg2764532),
but I didn't try that.

XXX the EEVblog forum post has a ton of other useful information!


At the top left sits a Furuno GT-8031 GPS module that is compatible with
[Motorola OnCore M12 modules](/assets/s200/Motorola Oncore M12.pdf). 
There are a bunch of connectors, and, very important, 3 unpopulated connector footprints. 

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

# Setting Up a SyncServer S200 from Scratch

My first goal was to set up the SyncServer so that it'd be synchronized to the GPS
time and display the right time on the display. That should be a pretty simple thing
to do, but it took many hours before I got there. There were 3 reasons for that:

* due to the WNRO issue, the SyncServer didn't want to lock onto the GPS time.
* the default IP addresses for the  Symmetricom NTP servers aren't operational anymore. 
  But that wasn't clear in the status screen.
* when I tried alternative NTP servers, they couldn't be found because I hadn't
  configured DNS servers.
* configuring the SyncServer to get its IP using DHCP is a bit of nightmare.

My focus was always first on the GPS and then the NTP part, but I'll do things the
opposite way here to allow you to get somehwere without the kind of hardware hacking 
that I ended up doing.

# Opening up the SyncServer S200

Just remove the 4 screws at the top of the case and lift the top cover.

*I wish other equipment was just as easy.*


# Cloning the CompactFlash Card

The S200 uses a 512MB flash card to store the OS. I wanted to make copy and leave
the original card unchanged so that I wouldn't have to worry about making crucial
mistakes. You don't really need a second flash card, a full-disk copy of the contents
of the original card can be save to your PC and restored from there, but I found it 
useful to have a second one to swap back and forth between different flash card while 
experimenting.

![S200 Flash Card](/assets/s200/S200_flash_card.jpg)

There is a lot of chatter in the EEVBlog forum about which type of flash card does or 
doesn't work. There's concensus that it must a CompactFlash card with *fixed disk PIO*
instead of *removable DMA* support. It's also good to use one that is an *industrial*
type because those have long-life SLC-type flash memory chips that allow more read-write
operations and a higher temperature range, but that's where things end. Some people aren't able 
even make a 512MB card. Others claim that their 512MB car worked, but that larger capacity 
ones didn't.

I bought [this 512MB card](https://www.amazon.com/gp/product/B07HL5F1VX) on Amazon for 
and it worked fine. This [1GB one](https://www.amazon.com/gp/product/B07HL5F1VX) worked
fine too?! I ran into none of the issues that other people had. I wonder if it has to
do with the kind of embedded PC motherboard that I'm using: remember that there are different
versions out there.

Either way, you'll also need CF card reader. It's kind of ridiculous that 
[the one that I bought](https://www.amazon.com/gp/product/B08P517NW5) is cheaper than
the flash cards themselves.

![Flash card reader](/assets/s200/flash_card_reader.jpg)

Windows people should use something like 
[HDD Raw Copy Tool](https://hddguru.com/software/HDD-Raw-Copy-Tool/)
to make a copy, but I found it to be just as easy using the standard Linux disk
utilities:

After plugging in the drive:

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

In my case, the drive is mounted on `/dev/sdb`. It can be different on your machine.

There are 5 different partitions on the flash card. There's a `_boot` partition,
the read-only `_fsroot` partitions have redundant copies of the OS itself, a
`_persist` partition contains mutable data such as configuration settings and
log files, and `_tmparea` is used for intermediate data.

Right now, we don't really care about any of that and just make a copy of the whole
drive to a file on my Linux machine, like this:

```sh
$ sudo dd if=/dev/sdb of=flash_contents_orig.img bs=1M
```

```
[sudo] password for tom: 
488+1 records in
488+1 records out
512483328 bytes (512 MB, 489 MiB) copied, 40.6726 s, 12.6 MB/s
```

If you have a second flash card, copying the original contents there is just
as easy:

```sh
$ sudo dd if=flash_contents_orig.img of=/dev/sdb bs=1M && sync
```

```
488+1 records in
488+1 records out
512483328 bytes (512 MB, 489 MiB) copied, 0.143977 s, 3.6 GB/s
```

Notice the `sync` command at the end: if you don't do that, you'll get your
command line back right away while the copy operation is going on in the background.
I didn't want to accidentally unplug the thing before it was done.

Unmount the drive after copying:

```sh
sudo unmount /dev/sdb
```

You're all set now to plug the old or the new CF card back into the S200.

# Network Setup



Notes:

* DHCP: 
    * avoid it you can
    * when enabled but no network cable connect, bootup will hang for a minutes
    * DHCP lease only negotiated at bootup
* When not using DHCP, add DNS server. For Comcast, it was 75.75.75.75
* Management can only happen on LAN port 1
* Default Symmetricom NTP servers are not operational anymore
* IL-0030B only shows satellites tracked, not satellites visible, for a long time.
  But when GPS lock, suddenly satellites are visible.
* IL-0030B has rechargable 3.3V Varta MC 621 battery. Feeds a 32768kHz oscillator for an RTC clock.
* IL-0030B is much slower at tracking satellites.
* Patch Linux distribution to enable root
* Use JP4 on motherboard for factory default settings (e.g. when misconfigured...)

Getting date from server:

```sh
ntpdate -q 192.168.1.201
```

```
server 192.168.1.201, stratum 1, offset -0.002502, delay 0.02988
 4 Jun 22:28:50 ntpdate[229341]: adjust time server 192.168.1.201 offset -0.002502 sec
```

* Make backup of compact flash card
* Reset to default settings

    * Page 120 of manual
    * Wire up jumper JP4 (not a standard jumper!)
    * power on
    * wait for 100s
    * power off
    
    (What goes on under the hood)

* Set up IP address for remote connection

    * Only LAN1 is active
    * I use static IP 192.168.1.201. The default is 192.168.0.100.
    * Gateway: 255.255.255.0
    * LAN1 Gateway: 192.168.1.1
    * Don't use DHCP for initial configuration. The moment you switch, you can't log on
      because the web panel is disabled!
    * Plug in cable. Network LED should go green.

* Connect to web panel
    * http://192.168.1.201
    * Username: admin
    * Password: symmetricom

* Webpanel: configure network:

    * NETWORK -> Ethernet:
    * Management Port User DNS Servers: Add a DNS server. 

        In the case of Comcast: 75.75.75.75

    * Check with NETWORK -> Ping that you can ping the outside world. E.g yahoo.com

* Set up NTP servers to sync with

    * The default ones don't work!!! 69.25.96.11, 69.25.96.12, 69.25.96.14 

        In NETWORK Assoc, you'll see that all these IP addresses have St(ratum) value of 16.
        
    * NTP -> Config

        * Select 69... IP address and delete them.
        * Add 0.pool.ntp.org
        * Add 1.pool.ntp.org
        * Add 2.pool.ntp.org
        * Add time.nist.gov
        * RESTART

    * NTP -> Assoc

        Will show various stratum values for the IP addresses.

    * You should be able to query your server now from your PC:

        ```sh
ntpdate  -q 192.168.1.201
        ```

        ```
server 192.168.1.201, stratum 16, offset -0.019111, delay 0.02856
 4 Jun 23:20:32 ntpdate[230482]: no server suitable for synchronization found
        ```

        Initially, this will show Stratum 16, because the internal clock was not synced to GPS
        due to the WNRO problem and because it needs time to sync to one of the NTP servers.

        After a while (around 15 minutes), you'll get this:

        ```sh
ntpdate  -q 192.168.1.201
        ```
        ```
server 192.168.1.201, stratum 2, offset -0.034768, delay 0.02989
 4 Jun 23:23:21 ntpdate[230491]: adjust time server 192.168.1.201 offset -0.034768 sec
        ```

        The Sync status LED and web page indicator will now be yellow instead of red: at
        least you have *something*, which should be good enogh for pretty much anything!

        On the front panel and on STATUS -> Timing, you'll see that the current
        sync source is NTP and that the hardware clock status is "Locked".

        This means that the OCXO is disciplined to an external NTP server. The problem is:
        the output is horrible. In my case: 9,999,901 Hz, a deviation of a whopping
        99Hz, much worse that the 7Hz deviation when the OXCO clock isn't disciplined at all!

        And then after a while, it jumped to 10,000,095Hz!

* Set correct time zone

    * TIMING -> Time Zone

        I use America/Los_Angeles

    You have an expensive and quite power hungry clock now!

* Upgrade the system: forget about doing this from the web, the Symmetricom servers have
  been shut down long time ago. But you can do upload a file.

* Make backup of settings

    * Web interface: Wizards -> Backup -> Backup
        * Save As -> browser download syncServer.bkp

* Power consumption is around 18W. Will be lower for the TCXO and higher for the Rubidium
  version.
        


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

