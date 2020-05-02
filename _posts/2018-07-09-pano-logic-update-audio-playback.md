---
layout: post
title:  "Pano Logic Update: Audio Playback, USB and Ethernet Connections"
date:   2018-07-10 00:00:00 -1000
categories: Pano Logic
---

After a vacation and lots of World Cup quality time (Go Belgium!), the pace on the Pano Logic project has been picking up again.

Audio Playback
--------------

Audio playback was always high on the list and there's a lot of progress on this front: I can play a 1KHz test tone when plugging in
my headphones! 

For reasons unknown, the speaker does not work, even after a long evening of trying as many settings as possible.

Still, with this milestone, I'm one step closer to using the Pano Logic box as a mini game console.

USB 
---

The interface between the NXP ISP1760 and the FPGA has been completely mapped... I think. The chip has a 16-bit and a
32-bit mode. On this board, the 16-bit mode is used. I expect that it will be quite a bit of effort to get USB going. First
step will simply to be get the FPGA to read and write registers and then we'll see where it leads us.

Even though the ISP1760 has a built-in 3-way hub, there is an external SMSC USB2513 hub. I was told that the ISP1760 has some
bugs in the hub, so that probably explains the presence of this SMSC chip.

The SMSC chip has an I2C interface, but was only able to identify a reset and a clkin signal between the FPGA and the SMSC chip.
It's possible that the default configuration is sufficient and that no further configuration is necessary.

Ethernet 
--------

A bunch of connections between the Micrel KSZ8721BL Ethernet PHY and the FPGA were identified as well. However, there are
some signals that seem to be suspiciously not connected (e.g. `eth_txc` and `eth_pd_`).

Getting Ethernet to work would be incredibly nice, but it's a pretty complex undertaking and lowest priority.

Next Up
-------

I may spend a bit more time on getting the speaker to work, but the true challenge ahead will be USB: the Pano Logic box is 
almost useless if you can't connect a keyboard to it.


