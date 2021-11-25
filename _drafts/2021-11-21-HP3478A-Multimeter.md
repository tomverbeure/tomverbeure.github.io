---
layout: post
title: HP 3478A Multimeter Repair - One Weird Connector
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

XXX

On eBay, these 5 1/2 digits meters go for around $140, while broken ones go for ~$70. This one was $100, and 
came with the "Passes Self-Test" description. 

And that's exactly what happens.

However, that's really as far as it went: other than the power switch, none of the front panel
buttons had an effect. The thing went onto an empty shelve, waiting for its time in the spotlight.

After playing with JTAG and other debugging techniques for a bit too long, Thanksgiving week was the 
perfect time to give this things some tender loving care.

# Documentation

The 3478A has been retired long ago, but there's a lot of information online. The service manual
is great and can be downloaded straight from the Keysight website. It has the full schematics and detailed 
trouble-shooting instructions for all kinds of failure modes. But there's also plenty of
material of Youtube: teardowns, how to replace the calibration battery without losing calibration
data, how to downloaded calibration data over GPIB, how to clean the display, and so forth.

This quote from discussion thread on the EEVblog forum is a bit ominous: 

>  3478 are not bad but they are virtually unrepairable if they break. Especially the display is unobtainium...

Checkout the bottom of this blog post for a list.

# The 3478A Architecture

The 3478A first came to market in 1981. But despite being 40 years old, it has not one but 2 microcontrollers.
That's because it's split into 2 electrically isolated sections: the digital part takes care of the display,
the buttons, the GPIB interface, and configuration management while the analog part handles measurement of
voltage, current, and resistance. Both sides have a 8049 microcontroller with a whopping 256 bytes of on-chip RAM.
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

* [Boat Anchor Manual Archive](https://bama.edebris.com)
