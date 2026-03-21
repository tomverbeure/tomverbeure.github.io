---
layout: post
title: Agilent 54831 Oscilloscope
date:   2026-03-15 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

After 6 months of deprivation, a new season of 
[Silicon Valley Electronics Flea markets](https://www.electronicsfleamarket.com/)
is upon us! I never make it there at opening time, an ungodly 6am. Even
6:45am is a struggle, but it was not a moment too soon, because one vendor
was selling not one but two broken Agilent 54831 oscilloscopes, but only if you 
bought them together, for $200. While I considered the marital implications of 
having to defend 2 additional boat anchors in my garage, others were lining up 
after me, so I made the courageous executive decision to take the deal.


# The Agilent 54831

The specs of the 54831 are still pretty decent by hobbyist standards: 

* 4 channels
* 600 MHz BW
* 4 Gsps

There are some limitations: channels 1 and 2 and channels 3 and 4 share the same
AD converter. To reach 4 Gsps, you can use only either channel 1 or channel 2 but not
both, and either channel 3 or channel 4 but not both. Otherwise the sample rate
drops to 2 Gsps.

The 54832 is the slightly more potent sibling of the 54831 with an analog bandwidth 
of 1 GHz, but like the Tektronix TDS 754D and the TDS 784D, the 54831 can be
upgraded to a 54832 with a single resistor modification.

The 54831 dates from the mid nineties and is one of the earlier lines of test
equipment that use Windows as their base operating system.  There are a few 
revisions, some earlier models ran Windows 98 but soon HP switched to Windows
XP. 

For many years, Agilent used a Motorola VP22 motherboard to manage the test equipment 
and that's mine have as well. They're

# My Units

**Unit A: 54831 ** 

* Motorola VP22
* Pentium III 1GHz (Xeon, Cascades, SL52)
* 256MB of RAM
* 10 GB IBM TravelStar hardrive
* CDROM drive
* LS120 floppy drive
* Customer hardware numbers:
* VIN
* OS
* Scope software



The units that I bought are a 54831M and a 54831B. The former runs Windows 98, the
latter Windows XP, or at least that's what they're supposed to run based on the
Microsoft license stickers at the back of the units. In reality, neither of them
worked, as disclosed by the seller, but in different ways:

* other than emitting long beeps, the 54831M didn't do anything at all. 

* 54831M 
* Doesn't boot
    * Long beeps
* Windows 98
* 10 GB IBM TravelStar
    * Disk image OK
* CPU: Pentium III SL52R - Socket PG370
    * Plug and unplug fixed non-boot issue
* Cooler: Thermaltalk Golden Orb Mini
   * https://www.electromyne.de/public/catalog_xmlxslproducts.aspx?art=viewproduct&suid=11565&productid=1028313753&zid=210bd6ab-f876-4795-91f7-6b11a146206f&ln=gb
   * [Review and installation procedure](https://www.frostytech.com/articles/256/index.html)
* Motherboard: VP22
    * [Retroweb](https://theretroweb.com/motherboards/s/motorola-vp22)


EEVblog:

* [[REPAIRED] Agilent 54832B CH1 vertical errors (flatness)](https://www.eevblog.com/forum/repair/agilent-54832b-ch1-vertical-errors-(flatness)/)
* [Agilent 600MHz 54831B hack for 1GHz 54832B possible? YES!](https://www.eevblog.com/forum/testgear/54831b-upgrade-to-54832b-possible)
* [Agilent 54831D modernising](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/)
    * [Upgrade to new 8" LCD panel, motherboard, Win10](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg2604720/#msg2604720)
    * [Upgrade to an 8.4" panel](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg3441942/#msg3441942)
    * [Contact to get disk image](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg3621150/#msg3621150)
    * [How to kill the app. Run "scope /service'](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg4600801/#msg4600801)
    * [General installation instructions](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg4621726/#msg4621726)
    * [More Windows XP instructions](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg4623739/#msg4623739)
    * [More instructions](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg4683551/#msg4683551)
    * [Windows XP license keys](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg4865144/#msg4865144)
* [Agilent 54831M upgrade to Windows XP, guide and resources](https://www.eevblog.com/forum/testgear/agilent-54831m-upgrade-to-windows-xp-guide-and-resources/)
* [Agilent 54835A scope (4 channel 1GHz / 4Gs/s) repair & uphack](https://www.eevblog.com/forum/testgear/agilent-54835a-scope-(4-channel-1ghz-4gss)-repair-uphack/msg5199198/#msg5199198)
    * Tony_G instructions

Others:

* [groups.io: Capacitor and thermal paste](https://groups.io/g/HP-Agilent-Keysight-equipment/topic/agilent_infiniium_54831m/117057746)
* [5V supply for adapter](https://wonghoi.humgar.com/blog/2016/07/)

* [Agilent 54831B Oscilloscope Taming](https://tolisdiy.com/2019/10/04/agilent-54831b-oscilloscope-taming/)

* [Windows XP ISO](https://archive.org/details/windows-xp-all-sp-msdn-iso-files-en-de-ru-tr-x86-x64)
* [Tony_G Various disk images](https://1drv.ms/f/s!Amqar8_XQ9Uzj6YhN1xHdM8tQdKMOA)

* [groups.io - 54831B drive image](https://groups.io/g/HP-Agilent-Keysight-equipment/topic/54831b_drive_image/75212695)

# References
