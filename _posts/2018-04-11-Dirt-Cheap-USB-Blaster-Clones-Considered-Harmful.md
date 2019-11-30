---
layout: post
title:  "Dirt Cheap USB Blaster Clones Considered Harmful"
date:   2018-04-11 00:00:00 -0700
categories: 
---

... or at least non-functional.

My very first hobby FPGA boards was the popular 
[EP2C5T144 Mini System Learning board](http://land-boards.com/blwiki/index.php?title=Cyclone_II_EP2C5_Mini_Dev_Board) with the smallest 
Altera Cyclone II FPGA. You can find them for $12 on AliExpress. 

![EP2C5T144 dev board]({{ "/assets/jtag/ep2c5t144.jpg" | absolute_url }})


To program the board, you also need a USB Blaster: Altera's version of a JTAG cable.  These, too, can be found on AliExpress for less 
than $3. It's really a steal. (Identical copies sell for $10 on Amazon.)

![USB Blaster Clone]({{ "/assets/jtag/usb-blaster-clone.jpg" | absolute_url }})


I've been able to make this cable work with the EP2C5 board so I thought it was all good.

However, I'm now in the process of reverse engineering the eeColor Color3 board (which conveniently has the JTAG connector still populated), 
and I spend more than an hour trying to get it work. Quartus was able to detect the USB Blaster, but most of the time it didn't even detect 
the JTAG chain. And if it did, it'd detect the wrong JTAG chip ID. And I never managed to get a bitstream programmed.

Now what?

Well, you try out another JTAG clone: the Terasic USB Blaster. It sells for $50 on the Terasic website and $70 on 
Amazon, which is still $230 less than the official real thing from Altera.

![Terasic USB Blaster]({{ "/assets/jtag/terasic-usb-blaster.jpg" | absolute_url }})

I plugged it in and ... voila! ... everything worked like a charm.

I suspect that the dirt cheap ones have really crappy level shifters (if they have them at all.)


