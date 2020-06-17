---
layout: post
title: Tektronix TDS 420A Review
date:   2020-06-16 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

After my work on getting my Siglent oscilloscope to somewhat play nice with
[glscopeclient](https://hackaday.com/2019/05/30/glscopeclient-a-permissively-licensed-remote-oscilloscope-utility/),
I wanted to fix a major gap in the list of supported equipment: Tektronix oscilloscopes. There was none. I can't say
that there was really urgent need for it, but let's justify it by the fact that we're using Tektronix scopes at work,
and maybe, one day, I'll need the kind of processing that glscopeclient provides?

Another driver was the fact that I suspected that a Tektronix scope would be better at handling data transfers than the Siglent,
which spends 80% of the time on preparing the data for transmission and only the remaining 20% on the transmission itself.

I had already been monitoring eBay for cheap Tek scopes (there aren't many), when I noticed this one:

![Tek 420A on eBay](/assets/tds420a/tds420a_ebay.png)

The Internet is full of stories of people who were able to find $50 bargains of allegedly broken scopes that worked with
only a bit of work, but $190 (including the $30 shipping) is really not a bad price for a scope that's not only listed
as working, but one that has been calibrated only little more than a year ago!

![Tek 420A Calibration Tag](/assets/tds420a/tds420a_calibrated.png)

A week later, the goods arrived.

![Tek 420A Fresh Off the Boat](/assets/tds420a/fresh_off_the_boat.jpg)

It still had the "Property of Motorola" inventory tag attached, and 2 "RICKY J" labels. Ricky: the scope is in good hands!

The eBay listing didn't have the customary bootup screen, but whatever worries I had were unfounded: shortly after powering
up the scope, I was greeted with with "Power-On self check PASSED" message.

![Tek 420A Poweron Self Check PASSED](/assets/tds420a/power_on_self_check_passed.jpg)

# The Tektronix TDS 420A in Brief

Released in 1991, the TDS 420A is old enough to have teenage children by now! But despite its age, anybody who has worked
with more recent Tek scopes will feel right at home: the user interface is nearly identical. That doesn't mean that
the UI is great, it's not, but at least it's consistent.


Here's a quick overview of the TDS 420A:

* 4 channels

    This is my number 1 requirement of any scope. 2 channels is just not enough for many cases.

* 100MS/s sampling rate

    Let's be honest: this isn't fantastic. Even low-end FPGAs can routinely run logic at 100MHz speeds and up, so forget
    about capturing these kind of signals.

    On the other hand, it's more than sufficient to debug your typical lower speed signals, such as RS232, I2C, VGA etc.
    When I think about my personal use, the vast majority of my time, this rate would have been sufficient.

    There are 4 parallel digitizers, so the sample rate won't go down as you enable more channels. (Unlike, say, some
    Siglent scopes.)

* 200 MHz BW

    It's not super common to have a BW that's higher than the sampling rate, but once you exceed 100MS/s rate, the
    scope switches to [equivalent time sampling](https://www.tek.com/document/application-note/real-time-versus-equivalent-time-sampling)
    mode, which allows you to capture higher BW signals in detail as long as they are repetitive.

* 30000 sample points

    My Siglent scope captures up to 140M samples, but 30K is sufficient to get a lot of work done.  I rarely use 
    the 140M setting because real-time acquistion can become too slow to feel responsive.

    Like the sample rate, the number of sample points doesn't go down when you enable more than 1 channel.

* Size: 15" wide, 18.5" deep, 7.5" high

    My bench is 24" deep and always full of stuff. 18" is hard to swallow.

* 7" monochrome CRT screen

    Perfect for that 1980s Hercules graphics nostalgia! You can set different intensities for the UI
    elements and waveforms. The display is fine for what it is, and after playing with it for
    a couple of hours, it doesn't bother me at all.

* GPIB interface

    Essential for me, since the whole point of buying it is the abitilty to remote control the scope.

    It only took about 30min to go from unpacking the scope to fetching acquired waveforms from the
    scope to my PC. And 95% of that time was *obviously* spent getting Linux drivers right.

    One major negative is the price of GPIB to USB interface dongles: except for cheaper UGPlus ones that
    aren't supported by any Linux driver, you'll be paying at least ~$60 for an Agilent 82357B on AliExpress.

    I didn't want to wait 2 months for one of those to arrive, so I went with a $100 National Instruments
    GPIB-USB-HS instead. That's a steep price for what it is, but $190 + $100 is still less than any working
    second hand Tek scope with an Ethernet port.

    Once I'm done (=lose interest) with the whole glscopeclient exercise, I'll probably sell the dongle back 
    on eBay...

* Other features

    * Waveform zoom
    * X/Y display
    * Limit checks

        This checks that an acquired signal falls within a predefined guardband.

Options present on my scope:

* Option 13: RS-232/Centronics Hardcopy Interface

    The wonderful option 13 allows me to connect a variety of printers, such as an HP Thinkjet or an Epson
    dot matrix printer, via a RS-232 cable or a Centronics parallel cable straight to the scope and make
    beautiful printouts of whatever is one the screen. Amazing!

    The RS-232 port supports a BAUD rate of up to 19200 and only supports the hardcopy feature. It does
    not support remote control.

* Option 1F: File System

    It has a floppy drive! I've seen kits on eBay to replace the floppy drive with a USB flash
    drive, but there's just no need for that when you can transfer the data straight from the scope to the
    PC.

Some other options, not present on mine:

* Option 1M: 120000 sample points

    This would have been a nice step-up from the default 30000.

* Option 2F: Advanced DSP Math

    In default configuration, the only math options are add, subtract, and invert.

    The whole idea of glscopeclient is to move these kind of operations from the scope to the PC, so I don't
    really care about being able to run an FFT on the scope itself.

* Option 05: Video Trigger Interface

    This option support triggering on various conditions for old school video signals like
    PAL and NTSC.

The 420A is an upgrade of the 420. The most notable differences are the bandwidth which was upgraded from 150 to
200 MHz, and the number of sample points, upgraded from 15k/60k to 30k/120k.

# The Leaking Electrolytic Capacitor Problem

When looking around the web for information about the TDS 420A, you'll find a bunch of videos about
how to repair them by replacing electrolytic capacitors.

This is a big issue for many vintage early-1990s electronics boards: the SMD electrolytic capacitors eventually
start leaking. There are 2 problem with that:

* the caps lose their capacity
* the electrolyte is corrosive: it can eat away PCB metal traces which will make the scope non-functional

In many cases, the display will still work, and, after powering up, the scope will list which sections
of the electronics are failing after its internal self check.

The general advise for anybody who buys such an old scope is to replace *all* caps.

I was fully prepared to have to go through the whole process (the number of caps can be close to 100), and 
while waiting for the scope to arrive, Iwatched a bunch of videos about how to go about it.

After receiving mine, I took off the enclosure to check out the damage, and I found an absolutely pristine
acquisition PCB. The solder contact points are bright and shiny (leaded solder will do that) and there's 
barely any dust.

![Inside Overview](/assets/tds420a/inside_overview.jpg)

Even better: there's no leaking electrolyte whatsoever around caps:

![Capacitors Closeup](/assets/tds420a/capacitors_closeup.jpg)

There are no markings on the outside of the scope that indicate a production date. However,
the bootup screen says "Copyright 1991-1996" and on the image above, you can see a handwritten date of what
seems to be "11/8/96".

[This commenter](https://www.eevblog.com/forum/testgear/tek-tds-420a-scorequestions/msg508699/#msg508699)
on EEVBlog has the following to say to a fellow TDS 420A owner:

> Your oscilloscope says 'copyright 1996'. That means it is a later model which doesn't have the leaky capacitors.
> I'd leave the oscilloscope as it is.

And that's exactly what I'll do!

For those who aren't so lucky, here are some repair videos that I found useful:

* [Recapping Tutorial - how to replace old, leaky surface mount electrolytic capacitors](https://www.youtube.com/watch?v=SjgWo7mj8-w)

    Repairs an old Mac PCB, but the principle is of course exactly the same.

* [Electrolytic Capacitor Removal NO Desoldering Required](https://www.youtube.com/watch?v=X8N9O3a9jiMa)

    A much faster way to remove these old capacitors.

* [Tektronix TDS 540A oscilloscope repair](https://www.youtube.com/watch?v=7V0LCL4mL-8)

    A tougher repair that goes beyond just replacing caps, requiring bodge wires to fix traces that were
    corroded away.

# Option Hacking to 120K?

Tektronix oscilloscopes of that era use NVRAM to store information about which options are enabled.

And just like with some Rigol or Siglent scopes, if you know what you're doing, there are ways to
non-invasively change these configuration values and install new features for free.

The TDS 420A doesn't have many options available that would move the needle in terms of general
usefulness... except for option 1M, support for 120K sample points.

A closer look at the acquisition PCB shows 2 large ASICs that are surrounded by 16 Cypress chips of
type [CY7C199-20](https://media.digikey.com/pdf/Data%20Sheets/Cypress%20PDFs/CY7C199.pdf). Those
are 32K x 8 SRAM chips with an access time of 50MHz.

![Sample Memory Chips](/assets/tds420a/sample_memory.jpg)

16 x 32K = 512KB / 4 channels = 128 Kb per channel.

There's little doubt that this board has the hardware to support 120K sample points, it's just that
the feature is not enabled.

Since there are 4 chips per channel, interleaving accesses is sufficient to store samples at a rate of
100MHz even when the individual chips are limited to 50MHz.

* [Hacking my TDS460A to have options 1M/2F?](https://www.eevblog.com/forum/testgear/hacking-my-tds460a-to-have-options-1m2f/)

* [TDS 420 Debug Serial Port](https://forum.tek.com/viewtopic.php?t=138100)

* [Upgrade Tektronix: FFT analyzer](http://videohifi17.rssing.com/chan-62314146/all_p49.html)

    Story about upgrading the CPU board from 8MB to 16MB on a TDS420 (not 420A?) and then FFT in the
    NVRAM.

* [Enabling FFT option in Tektronix TDS 540A oscilloscope](https://www.youtube.com/watch?v=iJt2O5zaLRE)

    Not very useful: enables FFT by copying NVRAM chip.

# Documentation

Tek scopes are used for decades and Tektronics cares about its customers. 29 years after introduction,
most manuals and programming guides are readily available on their website. And if some of the more obscure
information isn't there, some other website probably has a copy.

* [TDS410A, TDS420A & TDS460A User manual](https://www.tek.com/oscilloscope/tds420a-manual/tds410a-tds420a-tds460a-user-manual)
  ([PDF link](https://download.tek.com/manual/070921900.pdf))
* [TDS Family Digitizing Oscilloscopes Programmers Manual](https://www.tek.com/manual/tds-family-programmer-manual)
  ([PDF link](https://download.tek.com/manual/070987600.pdf))
* [TDS410A, TDS420A, & TDS460A Technical Reference - Performance Verification and Specifications](https://www.tek.com/oscilloscope/tds420a-manual/tds410a-tds420a-tds460a-technical-reference)
  ([PDF link](https://download.tek.com/manual/070921800.pdf))
* [TDS420A, TDS430A & TDS460A Service Manual](https://www.tek.com/oscilloscope/tds420a-manual/tds420a-tds430a-tds460a-service-manual)
  ([PDF link](https://download.tek.com/manual/070970304.pdf))
* [TDS Family Option 13 RS-232/Centronics Hardcopy Interface](http://w140.com/tekwiki/images/f/f0/070-8567-01.pdf)

# Random Related Youtube Videos

* [Tektronix TDS 420A Oscilloscope Teardown](https://www.youtube.com/watch?v=SwFyxgGT5TA)

    A bit long-winded, but does a full teardown and goes over all the components.

* [Tektronix TDS420a Oscilloscope Repair (Replace CPU Board)](https://www.youtube.com/watch?v=DKrsFh9jfO0)


* [Tektronix TDS-460 (400 series) Oscilloscope Power Supply Repair](https://www.youtube.com/watch?v=9lmAQUjs_cE)

# GPIB - Installing the GPIB-USB-HS Linux Kernel Driver

It's hard to believe, but despite supporting pretty much any kind of device imaginable, the offical Linux kernel
doesn't have any support for GPIB interfaces!

Luckily, there is the [Linux GPIB Package](https://linux-gpib.sourceforge.io/) which contains driver modules for
a variety of such interfaces, as well as whole bunch of user mode libraries and test programs.

Here's the recipe that worked for my Ubuntu 18.04 distribution:

* Install Linux Kernel Headers

```
sudo apt-get install linux-headers-$(uname -r)
```

In theory, you will need to redo this step whenever you upgrade your kernel to a later version.

* Download the latest version of the Linux-GPIB package

```
cd ~/projects
svn checkout svn://svn.code.sf.net/p/linux-gpib/code/trunk linux-gpib-code
cd linux-gpib-code/linux-gpib-kernel
```

* Compile and install

```
make
sudo make install
```

This will install a whole bunch of gpib drivers in `/lib/module/<kernel version>/gpib`:

```
cd /lib/modules/5.3.0-53-generic/gpib
find .
.
./cec
./cec/cec_gpib.ko
./agilent_82357a
./agilent_82357a/agilent_82357a.ko
./ni_usb
./ni_usb/ni_usb_gpib.ko
./hp_82341
./hp_82341/hp_82341.ko
./lpvo_usb_gpib
./lpvo_usb_gpib/lpvo_usb_gpib.ko
./ines
./ines/ines_gpib.ko
./sys
./sys/gpib_common.ko
./tnt4882
./tnt4882/tnt4882.ko
./nec7210
./nec7210/nec7210.ko
./agilent_82350b
./agilent_82350b/agilent_82350b.ko
./cb7210
./cb7210/cb7210.ko
./tms9914
./tms9914/tms9914.ko
./hp_82335
./hp_82335/hp82335.ko
```

* Install the appropriate GPIB driver into the kernel

For the GPIB-USB-HS, that's the `ni_usb_gpib` driver:

```
sudo modprobe ni_usb_gpib
```

* Check that the driver gets loaded

Plug in your GPIB USB dongle, and check what happens with `dmesg`:

```
dmesg -w
[63517.842042] usb 1-11.4: new high-speed USB device number 17 using xhci_hcd
[63517.957147] usb 1-11.4: New USB device found, idVendor=3923, idProduct=709b
[63517.957151] usb 1-11.4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[63517.957154] usb 1-11.4: Product: GPIB-USB-HS
[63517.957156] usb 1-11.4: Manufacturer: National Instruments
[63517.957158] usb 1-11.4: SerialNumber: 0120F5DE
[63517.975852] gpib_common: loading out-of-tree module taints kernel.
[63517.975897] gpib_common: module verification failed: signature and/or required key missing - tainting kernel
[63517.976571] Linux-GPIB 4.3.3 Driver
[63517.977564] ni_usb_gpib driver loading
[63517.977585] ni_usb_gpib: probe succeeded for path: usb-0000:00:14.0-11.4
[63517.977620] usbcore: registered new interface driver ni_usb_gpib
[63517.977621] gpib: registered ni_usb_b interface
```

Success!

But we're not there yet. We still need to install a bunch of user mode libraries and utilities.

# GPIB - Installing the User Mode Library and Utilities

The National Instrument GPIB USB dongles have small microcontroller on them that needs its
own firmware. This firmware must be loaded into the dongle before the dongle is able to behave
as a GPIB interface. The firmware, and the utility to load it into the dongle, is part of the
same Linux GPIB package that also contained the kernel above.


I used the following recipe:

* Compile and install the whole thing:

    ```
    cd linux-gpib-user
    ./bootstrap
    ./configure
    make
    sudo make install
    sudo ldconfig
    ```

    This will install an important configuration file in `/usr/local/etc/gpib.conf`.

    If you want the location of this file to be under `/etc` instead, you can do so with
    by using `./configure --sysconfdir=/etc`.

* Update the `/usr/local/etc/gpib.conf` configuration file

    In my case, all I had to do was change `board_type = "ni_pci"` to `board_type = "ni_usb_b"`.

* Load firmware into the dongle

    `sudo gpib_config`

# GPIB - Set the Device Address in the TDS 420A

The GPIB protocol supports up to 31 devices on a single cable daisy chain. But there's no plug
and play here, the address of each device needs to be assigned manually.

On the TDS 420A, you do this as follows. (See also the
[user manual](https://www.tek.com/oscilloscope/tds420a-manual/tds410a-tds420a-tds460a-user-manual) on page 3-91.)

* Press SHIFT UTILITY -> System (main) -> I/O (pop-up) -> Port (main) -> GPIB (pop-up) -> Configure (main) -> Talk/Listen Address

I selected address 1...

# GPIB - First Contact!

We can now finally test the whole connection.

The Linux GPIB package comes with a number of utilities, one of which is `ibtest`. Let's give it a try:

* `sudo ibtest`

    `udev` permission haven't been set yet, so, for now, let's run it as root.

* `d` (for 'device)

    `ibtest` can be used to talk to a GPIB connected device (like our scope) or to the GPIB interface dongle itself.

* `1` for GPIB address

    This is obviously the address that was assigned earlier into the scope.

* `w` : write string to scope

* `*IDN?`

    This is the standard SCPI command that returns an identification string.

* `r` : read the reply from the scope
* 1024
* Result:

    ```
    : r
    enter maximum number of bytes to read [1024]: 1024
    trying to read 1024 bytes from device...
    received string: 'TEKTRONIX,TDS 420A,0,CF:91.1CT FV:v1.0.2e
    '
    Number of bytes read: 42
    gpib status is:
    ibsta = 0x2100  < END CMPL >
    iberr= 0
    ```

    We have successfully received the identification info from the scope!

# GPIB - Setting Up UDEV rules

`udev` rule set user permissions and can do all kinds of funky stuff behind the scenes.

It took me ages to get things working, and reloading the rules with `sudo udevadm control --reload` was not
sufficient: *a reboot was necessary*!

This is the recipe that did it eventually:

```
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="3923", ATTRS{idProduct}=="709b", MODE="666", GROUP="tom", SYMLINK+="usb_gpib"
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="3923", ATTRS{idProduct}=="709b", RUN+="/usr/local/sbin/gpib_config"
KERNEL=="gpib[0-9]*", MODE="666", GROUP="tom"
```

You will need to change `GROUP` to something else.

How how the second line automatically calls `gpib_config` after plugging in the GPIB device into the USB port.


# The GPL3 License of the Linux-GPIB Package

The user mode libraries are licensed under the GPL 3.0, which means that projects with a less restrictive
open source license can't just be built with the Linux GPIB library without applying the GPL 3.0 license
to the whole project.

There is a good discussion about this [here](https://opensource.stackexchange.com/questions/1640/if-im-using-a-gpl-3-library-in-my-project-can-i-license-my-project-under-mit-l)
on Stackoverflow.

For my purposes, this isn't a huge deal: instead of writing a GPIB backend for scopehal/glscopeclient, I want
to write a TCP/IP to GPIB server. glscopeclient already has a socket based transport driver, so it
using such a server, no additional transport driver would need to be written.

