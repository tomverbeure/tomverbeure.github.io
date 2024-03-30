---
layout: post
title: Converting a Symmetricom SyncServer S200 into a GPSDO
date:   2024-03-14 00:00:00 -1000
categories:
---

# Introduction

The [Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com) 
runs from March to September and then goes quiet for 6 months, so when the new
March episode hits, there is a ton of pent-up demand... and supply: inevitably,
some spouse has reached their limit and wants a few of those boat anchors gone.

Trust me: you do not want to miss the first flea market of the year! And you better
come early, think 6:30am, because the good stuff goes fast.

That fateful March 10th, I saw a broken-but-probably-repairable HP 58503A GPS
Time and Frequency Reference getting sold right in front of me for just $40. And while
I was able to pick up a very low end HP signal generator and Fluke multimeter for $10,
at 8:30am, I was on my way back to the car unsatisfied.

Until *that* guy and his wife, late arrivals, started unloading stuff from the trunk
and spread it on a blanket. Right in front of me, he unloaded a 
[Stanford Research Systems SR620 universal counter](https://thinksrs.com/products/sr620.html). 
I tried to haggle on the SR620 but was met with a "You know what you're doing and what 
this is worth." Let's just say that I paid the listed price which was still a crazy good 
deal. I even had some cash left in my pocket.

Which is great, because right next to the counter sat pristine looking Symmetricom
SyncServer S200 with accessories for the ridiculously low price of $60.

[![Flea Market Haul](/assets/s200/fleamarket_haul.jpg)](/assets/s200/fleamarket_haul.jpg)

I've never left the flea market more excited.

I didn't really know what one does with a *network time server*, but since it's a *GPS*
time server, I hope that it could work as a GPSDO, hopefully with a 10MHz reference
clock and a 1 pulse-per-second (PPS) synchronization output.

But even if not, I was sure that I'd be learning something.

Turns out that a SyncServer S200 can not be used as a GPSDO out of the box, but its
siblings can do it just fine, and it's straightforward to do the conversion. There
was also an issue with the GPS module that needed to be fixed.

In this blog post, I go through all the steps required to go from a mostly useless
S200 to a fully functional GPSDO.

Most of what's described here is based on this long 
*[Symmetricom S200 Teardown/upgrade to S250](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250)*
discussion on the EEVblog forum.

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
uses the [Network Time Protocol](https://en.wikipedia.org/wiki/Network_Time_Protocol), which

> is a networking protocol for clock synchronization between computer systems over 
> packet-switched, variable-latency data networks.

The SyncServer S200 is a [Stratum 1](https://en.wikipedia.org/wiki/Network_Time_Protocol#Clock_strata) 
level device. While it does not act as a Stratum 0 oracle of truth timing reference, it
directly derives the time from a Stratum 0 device, in this case the GPS system.

When the GPS signal falls away, a SyncServer falls back to Stratum 2 mode where it retrieves
the time from other Stratum 1 devices (e.g. other SyncServers on the network) or it switches
to hold-over mode where it let's an internal oscillator run without adjustments.

The S200 has 3 oscillator options:

* a TCXO with a drift of 21ms per day
* an OCXO with a drift of 1ms per day
* a Rubidium atomic clock with drift of 25us (!!!) per day

It's clear that the primary use case of the S200 is not to act as a lab clock or frequency
reference, but something that belong in a router cabinet.

# The SyncServer S200

[![S200 rear view](/assets/s200/S200_rear_view.jpg)](/assets/s200/S200_rear_view.jpg)


# Furuno GT-8031H:

When the S200 isn't able to lock its local OCXO to the GPS in, the 10MHz frequency is terribly
off by 7Hz:

[Unlocked output frequency](/assets/s200/unlocked_output_frequency.jpg)

(For this measurement, I'm using the 10MHz of my TM4313 GPSDO as clock reference.)

You can also see how the 1PPS output of S200 differs from the TM4313 output by 42ms.
Note that this is despite seeing 9 satellites.

The screen will show 

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

# IMPORTANT: Using the Right GPS Antenna

GPS signals are incredibly weak, so most GPS antennas are active ones that amplify the received signal 
inside the antenna before the signal is sent over the cable to the GPS receiver. Instead of a separate cable, 
the power for this amplifier is provided by the GPS receiver through the antenna cable. 

While most GPS receivers insert a 5VDC on the cable, Symmetricom equipment has the honor of being 
one of the few vendors that powers the GPS antenna with 12VDC. Or even better: this is only
true for some of their equipment. The SyncServer S200 is one of them. 

If you look for GPS antennas on Amazon, most will be 3V to 5V rated. You can find them for 

You can easily measure this voltage level with a multimeter by connecting the 2 leads to the ground
and the center pin of the SMA or BNC cable:


![Measuring the voltage across the GPS antenna connector](/asset/s200/...)

If you connect a 5V rates GPS cable to a 12V GPS receiver, chances are that you'll damage the antenna.

There are a couple of options to connect an antenna to a 12V GPS receiver:

* Use a 12V rated antenna
* Use a 5V GPS antenna and a bias tee with DC blocker to insert a seperate 5V 
* Modify your GPS receiver to output 5V instead of 12V
* Modify your GPS antenna to support 12V


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

![S250_BNC_connectors](/assets/s200/S250_BNC_connectors.png)

![S250_BNC_connectors_diagram](/assets/s200/S250_BNC_connectors_diagram.png)

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
