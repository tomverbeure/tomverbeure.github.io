---
layout: post
title:  Pano Logic JTAG First Contact
date:   2018-12-02 17:00:00 -0700
categories: Pano Logic
---

Steps required to get JTAG working on a Pano Logic thin client.

# Get a Xilinx-compatible JTAG Programmer

I bought mine on [Amazon](https://www.amazon.com/gp/product/B06XF5HK3K). It's a obviously a clone, but still
quite expensive at $35. I've seen similar one on AliExpress for as low as $22 + shipping, but I wanted mine
fast.

![Xilinx Programming Cable]({{ "/assets/panologic-g2/jtag/0-JTAG Programming Cable.JPG" | absolute_url }})

This JTAG programmer is "USB certired". How very reassuring!

# Find the JTAG Connector on your G1 or G2

Not very complicated: I've done that for you in the picture below. Left is the Pano Logic G1. Right
is the G2.

![JTAG Connector Location for G1 and G2]({{ "/assets/panologic-g2/jtag/3-G1 vs G2.JPG" | absolute_url }})

The G1 has conventional-sized connector pins. The G2 has really tiny ones. Both connectors have 6 pins.

# JTAG Pin Order and JTAG Adapter

The order of the pins doesn't seem to follow some Xilinx standard order, but it is 
the same for the G1 and G2. The orientation is the same for the G1 and G2 as well.

1. VREF
2. TDI
3. TMS
4. TDO
5. TCK
6. GND

The GND pin is the one located closest to the FPGA.

![G1 JTAG Adapter]({{ "/assets/panologic-g2/jtag/2-G1 JTAG Adapter.JPG" | absolute_url }})

Note the little adapter that I created for the G1. The JTAG programmer comes with wires that can
be plugged in directly into the G1 pins. However, to make the board work, you also need to 
plug in the auxiliary board, which is located right above the JTAG connector. It works, but
it's a bit cramped.

To make plugging in and out easier, I created a little 90-degree adapter with a 
[connector construction kit](https://www.aliexpress.com/item/620pcs-Dupont-Connector-2-54mm-Dupont-Cable-Jumper-Wire-Pin-Header-Housing-Kit-Male-Crimp-Pins/32839071531.html). 
It cost less than $7 on AliExpress, and I use it more than I initially expected. It's great
to create quick ad-hoc connector adapters that would otherwise require tedious checking of
pinouts whenever you need to recreate a particular setup.

You can see the kit here:

![Connector Construction Kit]({{ "/assets/panologic-g2/jtag/1-Connector Construction Kit.JPG" | absolute_url }})

# G2 JTAG Adapter

For the G2, I soldered some wire-wrap wires between the tiny on-board connector and a strip of standard pins.
Wire-wrap wires are great for this kind of stuff: they're super thin and very easy to solder. 
I've even used them to solder wires to individual TQFP144 pins. 

![G2 Connector Adapter]({{ "/assets/panologic-g2/jtag/4-Connector Adapter.JPG" | absolute_url }})

Since the pin ordering is the same for the G1 and G2, I can now simply plug in my G1 JTAG adapter:

![G2 JTAG Connected]({{ "/assets/panologic-g2/jtag/5-JTAG connected.JPG" | absolute_url }})

# G2 LX150 JTAG First Contact

The free Xilinx ISE 14.7 doesn't support the Spartan-6 LX150 for synthesis and place-and-route (you need the Win10 version for that),
but it *does* support the LX150 in the Xilinx iMPACT JTAG control software.

After connecting the JTAG Programmer to the G2, and doing a boundary scan test, you should see the following:

![LX150 JTAG]({{ "/assets/panologic-g2/jtag/6-Spartan-6 LX150 JTAG.png" | absolute_url }})

"Boundary-scan chain validated successfully" and LX150 device detected!



