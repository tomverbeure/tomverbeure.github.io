---
layout: post
title: Reverse Engineering the Comtech AHA363 PCIe Gzip Accelerator Board
date:   2019-11-03 00:00:00 -0700
categories:
---

# The Start of a Journey

One can never have enough projects going in parallel. And while programming RTL is fun, I also 
love the whole process of reverse engineering, starting from a board that you don't know nothing
about and step-by-step getting to the point where it becomes something useful.

The [FPGA board hack](https://hackaday.io/project/159853-fpga-board-hack) project on Hackaday lists 
a bunch of commercially available PCBs that have an FPGA in them. Most of them haven't really been 
comprehesively reverse engineered.

I was particularly attracted to the Comtech AHA363PCIE0301G (AHA363): FPGA development boards with PCIe 
support are never cheap. It'd be fantastic if it could be repurposed as a general FPGA PCIe accelerator
board.

The AHA363 is listed as having an Arria GX FPGA, size unknown. Its real purpose is a gzip compression 
and decompression accelerator, a common operation in data centers that need to serve  gzip compressed 
web pages.

Various eBay vendors sell the same board for wildly differing prices: $1265, $185, and $19. In an attempt 
to keep my wife happy, I settled on the $19 version. Or better: I bought 2 of them, in case I needed 
to destroy one to figure out connections etc.

![AHA363 on eBay]({{ "/assets/aha363/aha363_on_eBay.png" | absolute_url }})

In this blog post, I'm describing the journey from acquiring the board to getting to the point of doing 
something useful with it. There is no guarantee of success: at the time of writing this, I haven't been 
able to get an LED to blink yet, but I've already learned some new techniques that will help me reverse 
engineer other PCBs in the future, and that might be useful for others as well.

A few days after ordering, this arrived at my doorstep:

![AHA363 with Heat Sink]({{ "/assets/aha363/aha363_with_heat_sink.jpg" | absolute_url }})

# Undressing the FPGA

*Note: for those who'd like to replicate/help out with reverse engineering this thing: now that we know 
the type of the FPGA, there's really no reason to remove the heatsink anymore. This reduces the chances 
of accidentally destroying your board.*

The FPGA Board Hack project mentioned an Arria GX FPGA, but since it's covered by a heat sink, the exact 
type was still unknown.

The heat sink is mounted solidly to the chip with 2 clips on 2 sides. You can remove it by inserting a flat 
head screwdriver in the clip holes and pushing them out. After a bit of wiggling, the mounting bracket will 
come off. Next, squeeze the same flat head screwdriver between the FPGA and sink, and rotate it very gently 
separate them. Eventually, the sink will come off, and the secret is revealed:

What we have here is an [Arria GX](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/hb/agx/arriagx_handbook.pdf) 
EP1AGX90E: the largest device of its class with 90K logic elements, 4.4Mbits of block RAM, and 176 18x18 
multipliers. Even today, boards with FPGAs of this size are in the ~$100 range.

Reverse engineering this project got a lot more interesting!


# AHA363 Board Overview

The PCB of the AHA363 is packed with a large number of ASICs and components. It's a half-height 4x PCIe
board with a bracket of the same height: that's fine for a rack-mounted server, but it won't fit inside 
a regular PC. You need to remove that bracket first.

After doing that and plopping into my regular Linux PC, `lspci` greeted me with the following message:


Success! The board is working!

The first step of my reverse engineering process is to take photographs at close range of all the 
components and connectors. In most cases, the x2 optical zoom option of my iPhone 7 Plus is sufficient 
for that, but sometimes I use the [iPhone adapter on my microscope](/tools/2018/04/29/stereozoom4-iphone-adapter.html).
My eye sight has been declining, and photos make it so much easier to identify the markings of various 
components. 

I also annotate these photos with the component names, connector pins values etc. This makes it much easier 
when needing to find your bearings when probing things.

The PCB contains:

* the FPGA, hidden under a beefy heatsink
* 2 AHA3610 gzip accelerator ASICs. Other than some slide sets and marketing material, I could not find any technical datasheets about it.
* 1 Altera MAX II EPM570F100 CPLD: used to load the bitstream from flash into the main FPGA. This CPLD is used in the same configuration in the Altera Arria GX development kit, and in the reference designs for *remote system upgrade* designs.
* 1 ... parallel FLASH: this flash contains the bitstream
* a 10-pin connector that's almost certainly used as JTAG conector, and maybe more
* power regulation circuits: some Emperion chips, some modules
* 5 LEDs: absolutely essential if we want to get an LED blink working on this board!
* PCIe interface: the main attraction to reverse engineer this board!

One immediately notices that this board get pretty warm when plugged into the PC, even when it's not doing anything useful.


# Probing, Test points, and Tented Vias

The most important tool for reverse engineering a PCB are a multi-meter with a low reaction time when using it in short-detect mode. This makes it possible to go over
an array of vias very quickly in the hope to triggering a connection between 2 points.

Another key element is the ability to measure connections in the first place: if you're really lucky, the PCB has plenty of test points. If you're a bit lucky, there are tons of vias that are not [tented](https://macrofab.com/blog/via-tenting-for-pcb-design/). You're totally out of luck if your doesn't have test points and vias are tented at all. In those cases, I'll usually bail: discovering connections becomes simply too cumbersome.

The AHA363 board has an incredibly amount of test points, more than I've ever seen before. So that's fantastic. But strangely enough, one of my board had tented vias and the other did not. I'm using the one with tented vias to record traces with my scope and logic analyzer to check dynamic behavior, and I'm using the other board to probe out connections.

That said, even the tented vias are relatively easy to measure: I've noticed that pressing my oscilloscope's probes on them is usually sufficient to break through the protective layer and make it peel off a little bit. 

# Package Footprints and Intel Quartus

The Arria GX product family is pretty old now, and not supported anymore by today's versions of Quartus. The last official release with support was Quartus 13.0sp1, but that was only for the standard, commercial version. The last 'free' release was Quartus 11.0. You can download it [here](FIXME).

I'll use Quartus for a number of reasons:

* Quartus Programmer is very good at discovering all the JTAG TAPs (test access ports)
* We'll use Quartus to create new bitstreams for our design.
* The Quartus Pin Assignment editor gives an excellent view of the IO pins of the package, with the ability to view the package from the top or bottem, and at any desired rotation. This is a life saver when trying to find pinpoint the right IO pad on the PCB. The assignment editor also annotated all the special IO pads with the right value when you mouse over it.

Here's a screenshot of the Pin Assignment Editor showing the Arria GX FPGA as seen from the bottom of the PCB, with the PCIe transceivers located at the bottom too. 

# Correlating FPGA IOs with the FPGA vias on the PCB

When you're lucky again, the PCB has vias underneath the FPGA that map directly to the balls on the FPGA package. The Pano Logic G1 is a fantastic example of this. It even has silk screen annotation of the all PAD numbers!
When your PCB doesn't have this, you may be forced to desolder the FPGA of one of your boards at one point or another. (But be sure that you first read below about various JTAG boundary scan options!)

In the case of the AHA363, there is a pretty decent grid of vias underneath the FPGA, but it's still a bit of a struggle to find the correlation between the vias and the ball on the package. 

Time to bring out an image editor and start annotating the vias with the most plausible pad name. This is not always the linear process that's describe here: if first located some JTAG pins (see next step), then annotated those
pins, then located some the clock (see down even further), annotated those etc.

Eventually, I ended up with something like this:

# Bringing up JTAG 

Nothing is more important while reverse engineering an FPGA-based PCB than getting the JTAG interface to work, since it's the prime method of loading bitstreams during FPGA development. In addition, FPGAs also have boundary scan registers for most IO pads that make it possible to extract sometimes crucial additional information about how IOs are configured (input or output), locate the clocks, and the values that are being driven or that are being read by the IOs.

Many FPGA based PCBs have their JTAG interface easily available, even on the final production board, since it's often used as the main interface to flash production firmware and bitstreams on the factory production line.

The AHA363 has a prominent 10-pin connector that I expected to contain JTAGs pins, so the steps is to figure out how those pins are connected.

* 4 of the 10 pins are connected to ground. They are all on the front side of the PCB.
* on visual inspection, the remaining pin on the front side seemed to be unconnected (since there was no via from the connector metal to anywhere.)
* that leaves 5 more pins: TCK, TMS, TDI, TDO, and VREF (the supply voltage that goes from the PCB to the voltage level shifters in the JTAG dongle.)

The discovery process is pretty straight forward: you start with one of the JTAG pins that is shared between all chips in the chain, TCK or TMS. You check if there's a connection between those IO pads on the FPGA and one of the connector pins. Done!

I was able to identify TCK and TMS quickly, but had no such luck for TDI and TDO.

The thing is that TDI and TDO are point-to-point, and they can be part of a chain: if the FPGA is in the middle of a JTAG chain, then these pins on the FPGA package will not be connected to the connector. 

So the next step is to check if TDI of the CPLD is connected to the connector, and bingo!

I also confirmed that the TDO pin of the CPLD is connected to the TDI pin of the FPGA. Since there is no connection between the FPGA TDO and the connector, it's likely that the 2 ASICs are part of the JTAG chain as well. We don't know anything of their pin-out, so that's a dead-end. 

But if one of the pins is VREF, you can try checking if there's a connection between one of the 2 pins and VDD. And, indeed, there is! And since there's now only unknown left, that one can be assigned to TDO.
