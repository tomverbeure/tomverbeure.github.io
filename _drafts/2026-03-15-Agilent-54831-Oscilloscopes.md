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
is upon us! I didn't make it there at 6am opening time, even getting there at 6:45am was 
a struggle, but not a moment too soon because one vendor was selling not one but two broken 
Agilent 54831 oscilloscopes, $200 for both of them.  While I considered the marital 
implications of having to defend 2 additional boat anchors in my garage, others were lining 
up after me, so I made the courageous executive decision to take the deal.

![Oscilloscopes in the trunk of a car](/assets/hp54831/scopes_in_car.jpg)

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

The HP 548xx oscilloscope series was one of the first kind of test equipment that
used Windows as their base operating system. I have an older HP 54825A, introduced in
1997, that runs Windows 95. The 54831 was introduced in 2002. Early version ran on
Windows 98 SE Embedded, Agilent later switched to Windows XP.

For many years, Agilent used a Motorola VP22 motherboard to manage the test equipment 
and that's what mine have as well. 

# Inside the PC System of the 54831

Many piece of test equipment[^sleeve] use a sleeve-like enclosure that slides around the inner
assembly. I'm not really fond of that: it can be clumsy to remove and put back, even if you
only need to work on the top side of the scope, the bottom electronics are exposed as well.
The 54831 has separate top and bottom covers. The only disadvantage is that there are much
more screws to hold it together: you need to remove 16 of them just for the top cover.

[^sleeve]: The 54825A has a sleeve-like enclosure.

Figure 6-1 of the 
[service guide](https://xdevs.com/doc/HP_Agilent_Keysight/HP%2054830,%2054831,%2054832X%20Service.pdf)
shows that very well:

[![Removing the top cover](/assets/hp54831/removing_top_cover.png)](/assets/hp54831/removing_top_cover.png)
*(Click to enlarge)*

After removing the top cover, you should see something like this:

![Top inside view](/assets/hp54831/top_inside_view.jpg)

It's really just a PC with some custom PCI plug-in boards. From top to bottom:

* PCI to PCI bridge board

  The acquisition board has its own PCI interface. The PCI signals are carried over a 
  wide flat-cable that's terminated on the PC side by a 
  [TI PCI2050PDV](https://www.ti.com/product/PCI2050B/part-details/PCI2050BPDV) 
  PCI-to-PCI bridge chip on this board.

  *I think this is the first time I've seen PCI signals being carried over a flat cable.*

  In addition to the PCI flat cable to the acquisition board, there's also a narrower flat cable
  on the side that goes to the front panel. 

* GPIB interface board
* Display adapter 

  This board, based on a 
  [CHIPS F65550](https://www.vgamuseum.info/index.php/cpu/item/185-chips-technologies-f65550), 
  is more than a regular VGA board: it has a flat panel interface to the LCD front panel and an 
  LCD backlight controller. There's also a bridge cable to the next board that carries the 
  real-time waveform overlay.

  ![Annotated display board](/assets/hp54831/display_board_annotated.jpg)

  As was the case with some 3D graphics accelerators in the nineties, the VGA card renders the
  GUI, but waveforms are rendered by a separate card and merged with the GUI in hardware.[^overlay]

[^overlay]: You shouldn't try this yourself because it can damage the electronics, but if you 
            unplug the bridge cable while the scope is up and running, you'll see that the GUI 
            is still rendered but the waveforms disappear. 

* Waveform overlay rendering board

  The full scope of this board is not 100% clear: based on an Altera FPGA, it definitely does
  the renders the video overlay, but I don't know if it does anything beyond that.

  While it has a bunch of connectors, none of them are used in the 54831 expect for the bridge
  cable to the display card. This means that all data is going through the PCI bus.

The other components are standard PC stuff:

* [Motorola VP22 motherboard](https://theretroweb.com/motherboards/s/motorola-vp22)
* [Pentium III 1 GHz (SL52R, 370 socket)](https://theretroweb.com/chips/1482)
* CDROM drive
* [Superdisk LS120 floppy drive](https://en.wikipedia.org/wiki/SuperDisk)
* 10 GB IBM TravelStar hard drive


# Unit A: Agilent 54831M

The "M" stands for military version. That doesn't mean it has different specs, it's
just that it has been assembled in Singapore, a country that's considered more trustworthy than
Malaysia, where HP scopes were usually assembled (or so 
[someone claims on The Internet](https://www.eevblog.com/forum/testgear/agilent-54831d-modernising/msg4616725/#msg4616725).)

![Unit A backside](/assets/hp54831/unit_a_backside.jpg)

The seller claimed that this unit didn't work at all, and he was right.
When plugging the power cord, it immediately started to squeal long ominous beeps and that
was it.

This unit has VIN# M42 (Rev.A.02.30), a production date of October 31, 2003 and
according to the Microsoft license sticker it's one of the early versions that runs Win98.

# First Suspect: the IBM TravelStar HD

My [Rohde & Schwarz AMIQ](/2025/04/26/RS-AMIQ-Teardown-Analog-Deep-Dive.html) came with a
non-functional IBM TravelStar HD. They are only slightly less notorious than the 
IBM Death...DeskStar drives and known to fail with a stuck read/write head assembly, so
I assume that this would be the case here as well.

The first step was to extract the drive, check if it was still working outside of the
scope, and create a backup image.

[![Unit A: hard drive mounted in case](/assets/hp54831/unit_a_hardrive_in_case.jpg)](/assets/hp54831/unit_a_hardrive_in_case.jpg)
*(Click to enlarge)*

HP always mounts their spinning disk hard drives a separate platform that's mounted on the main
chassis with some rubber feet to reduce the chance of damage due to rough handling. The screws that
fix the drive to the platform aren't accessible, so you need to remove the platform first, then
remove the drive.

I disassembled pretty much the whole PC section of the scope to get to the hard drive:

* Disconnect all cables

    Make sure to first unlock the flex cables before pulling them out!

    ![Flex cable lock](/assets/hp54831/unit_a_flex_cable.jpg)

    The IDC flat cable connectors have a metal retaining clip around them.
    Make sure you remove those first before trying to pull the connectors out. It's easy
    to do with a screw driver.

    ![IDC connector metal clip](/assets/hp54831/unit_a_idc_cable_clip.jpg)

* Remove all the PCI boards
* Remove adapter board that merges floppy drive and hard drive cables

    ![floppy/hard drive adapter board](/assets/hp54831/unit_a_floppy_hd_adapter_board.jpg)

* Remove the CDROM drive

    This requires removing a screw on the long stick across the case and one screw on the
    back of the case. See arrows:

    [![Remove CDROM drive](/assets/hp54831/unit_a_remove_CDROM.jpg)](/assets/hp54831/unit_a_remove_CDROM.jpg)
    *(Click to enlarge)*

    After this, you can slide the drive back a little bit and lift it out of the case.

* Remove the DRAM stick to access the bottom screw of the hard drive platform

* Unscrew the hard drive platform

    You now have access to all 4 screws of the platform.

    ![Screwdriver in bottom left hard drive platform screw](/assets/hp54831/unit_a_unscrew_hd_platform.jpg)


*Only after removing the platform by removing all 4 screws did I notice that the bottom 2 rubbers 
feet were not completely enclosed by the platform. It should be possible to remove the platform with 
a bit of force, without losening the bottom 2 of the 4 screws.*

The hard drive platform is freed!

![Hard drive platform freed](/assets/hp54831/unit_a_hd_freed.jpg)


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
* CPU: Pentium III SL52R - Socket PG370 - Coppermine - 1 GHz, 256 KB L2
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

* [Agilent Model 54830 Series Oscilloscopes - Service Guide](https://xdevs.com/doc/HP_Agilent_Keysight/HP%2054830,%2054831,%2054832X%20Service.pdf)

* [Pentium III thermal design guide](https://download.intel.com/design/intarch/applnots/27332504.pdf)

# Footnotes
