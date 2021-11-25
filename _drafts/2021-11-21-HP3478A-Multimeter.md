---
layout: post
title: Repairing an HP 3478A Multimeter with a Hacksaw
date:  2021-11-21 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I'm slowly building a small stable of equipment for my home lab. I'd be lying if I said
that it's out of hard necessity: almost all my projects are FPGA based and digital in
nature. You don't *need* a [nice high precision power supply](/2021/04/15/Agilent-E3631A-Knob-Repair.html)
to power a generic FPGA development board, but when there's one for offered on Craigslist, it's
so hard to resist. One day that that GPIB control interface might come in real handy after all!

And that's how, a few months ago, this HP 3478A benchtop multimeter appeared at my front door: 

![HP 3478A](/assets/hp3478a/hp3478a.jpg)

On eBay, these 5 1/2 digits meters go for around $140 when listed as Pre-Owned, while Parts Only listings
for around $70. In both cases, shipping costs is usually around $25. My unit was advertised as
Pre-Owned with a "Passes Self-Test" description for a low low price of only $100, so I decided
to take a chance on it.

Well, a passing self-test is what advertised, and a passing self-test is what I got!

![Self Test OK](/assets/hp3478a/self_test_ok.jpg)

But that's where it ended. Because other than the power switch, none of the front panel
buttons had an effect. I could use the thing to measure DC voltages, the default setting after
powering up, but that was about it.

The multimeter went onto an empty shelve, waiting for its time in the spotlight.

After playing with JTAG and other debugging techniques for a bit too long, Thanksgiving week was the 
perfect time to give the 3478A some tender loving care.

# Documentation

The 3478A has been retired long ago, but there's a lot of information online. It still has 
[a page on the Keysight webiste](https://www.keysight.com/us/en/product/3478A/55-digit-dmm-with-hpib-interface.html),
where it's marked as obselete, but the operator's and service manuals can found under the
resources tab.

The service manual is great, with full schematics and detailed trouble-shooting instructions for all 
kinds of failure modes. 

There's also plenty of material of Youtube: teardowns, how to replace the calibration battery without losing 
calibration data (very important!), how to download and restore calibration data over GPIB, how to clean the 
display, and so forth.

There's even a [MAME 3478A emulator](https://github.com/mamedev/mame/blob/master/src/mame/drivers/hp3478a.cpp), 
which is a great resource for 

This quote from discussion thread on the EEVblog forum is a bit ominous: 

>  3478 are not bad but they are virtually unrepairable if they break. Especially the display is unobtainium...

But somebody [managed to replace the LCD on a 3457A with an LED display](https://www.eevblog.com/forum/projects/led-display-for-hp-3457a-multimeter-i-did-it-)/),
so many something similar is possible on a 3478A?

Checkout the bottom of this blog post for a list.

# The 3478A Architecture

![HP Catalog - DVMs](/assets/hp3478a/hp_catalog_dmvs.png)

![Block Diagram](/assets/hp3478a/block_diagram.png)


The 3478A first came to market in 1981. But despite being 40 years old, it has not one but 2 microcontrollers.
That's because it's split into 2 electrically isolated sections: the "chassis common" (which the ground connected
to the chassis) section takes care of the display, the buttons, the GPIB interface, and configuration management 
while the "floating common" section handles measurement of voltage, current, and resistance. 

Both sides have a 8049 microcontroller with a whopping 256 bytes of on-chip RAM.
The firmware is stored on external EPROMs, the old style types that must be erased by shining a bright UV light
on a glasses windows.

The measurement method is unusual in that it uses a time-based analog to digital conversion process: 

XXXX


The measurement section has a floating ground, which makes it possible to connect the ground of the multimeter
to any random reference point of your device under test. However, the ground of the digital part is connected
to the chassis and the ground wire of the power plug. Since the digital and the measurement section are electrically
isolated, communication between the section can't be done with a simple wire.

In most such configurations, an optocoupler is used. And later versions of the 3478A, such as the one featured in the 
EEVblog teardown video, use exactly that. But older ones like mine have use magnetic couplers. There's one for each 
direction, from the digital part to the measurement part, and back.

# Various

* Works by charging a capacitor and measuring time (according to EEVblog video)

# References

* [EEVblog teardown](https://www.youtube.com/watch?v=9v6OksEFqpA) 
* [HP 3478A Multimeter Repair and Test](https://www.youtube.com/watch?v=e-itiJSftzs)
* [Tony Albus HP 3478A Multimeter Teardown](https://www.youtube.com/watch?v=q6JhWIUwEt4)
* [Datasheet](https://accusrc.com/uploads/datasheets/agilent_hp_3478a.pdf)
* [HP Journal](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1983-02.pdf)

    Contains technical description.

* [Discussion on EEVblog](https://www.eevblog.com/forum/beginners/is-190$-a-bargain-for-a-hp-2378a-bench-multimeter/)

    "3478 are not bad but they are virtually unrepairable if they break. Especially the display is unobtainium..."

* [Service Manual](http://www.arimi.it/wp-content/Strumenti/HP/Multimetri/hp-3478a-Service.pdf)
* [Battery replacement article](http://mrmodemhead.com/blog/hp-3468a-battery-replacement/)

* [KO4BB Manuals & EPROM dump](http://www.ko4bb.com/getsimple/index.php?id=manuals&dir=HP_Agilent/HP_3478A_Multimeter)
* [Boat Anchor Manual Archive](https://bama.edebris.com)
* [HP Catalog 1983](http://hparchive.com/Catalogs/HP-Catalog-1983.pdf)
