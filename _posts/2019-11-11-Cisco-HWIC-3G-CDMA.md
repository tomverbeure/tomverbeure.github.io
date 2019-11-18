---
layout: post
title: Reverse Engineering the Cisco HWIC-3G-CDMA
date:   2019-11-11 00:00:00 -0700
categories:
---

* [Reverse Engineering the Cisco HWIC-3G-CDMA PCB](#reverse-engineering-the-cisco-hwic-3g-cdma-pcb)
* [An Annotated Overview of the Board](#an-annotated-overview-of-the-board)
* [Powering Up the Board](#powering-up-the-board)
* [JTAG Connector](#jtag-connector)
* [And Life There Was!](#and-life-there-was)
* [LED Blinky](#led-blinky)
* [The Curious Case of Component C9059](#the-curious-case-of-component-c9059)
* [Bitstream Configuration](#bitstream-configuration)
* [Block Diagram: Putting It All Together](#block-diagram-putting-it-all-together)
* [Low Level Connections](#low-level-connections)

# Reverse Engineering the Cisco HWIC-3G-CDMA PCB

After the [abandoned attempt](https://github.com/tomverbeure/cisco-vwic2-2mft/blob/master/README.md) (\*) to reverse 
engineer the $5 Cisco VWIC2-2MFT-T1/E1 card (because its Stratix II FPGA is not supported by Quartus Web Edition), 
I set my sights on another Cisco WAN card, the HWIC-3G-CDMA. This one has a 
[Cyclone II EP2C35F484C8](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/hb/cyc2/cyc2_cii5v1.pdf) 
instead of a Stratix II EP2S30F484C5N, and you better believe that I verified it being supported by the free Quartus version 
before starting this project!

![Cisco HWIC-3G-CDMA Top View]({{ "/assets/cisco-hwic-3g-cdma/pcb_top.jpg" | absolute_url }})

This board is supposed to be inserted in the HWIC slot of a Cisco router and provide WAN functionality, allowing
the router to link the local network to the world through a wireless (slow!) CDMA connection.

![Cisco HWIC-3G-CDMA Front View]({{ "/assets/cisco-hwic-3g-cdma/pcb_front.jpg" | absolute_url }})

At the front, there are 2 antenna connectors and a diagnostic port. Don't get too excited about the present of
an Ethernet interface: it's an RJ-45 port that carries a serial interface using standard RS-232 voltage levels.

The [marketing documentation](https://www.cisco.com/c/en/us/products/collateral/interfaces-modules/3g-wireless-wan-high-speed-wan-interface-card/product_data_sheet0900aecd80600f41.html) 
mentions all kinds of protocols, but it's safe to assume that no matter whether or not one of those supported 
protocols is still in active use, it'll be very slow, and probably obsolete soon.

At the time of writing this, the cheapest such cards could be bought on eBay for $8, including shipping. As
usual, I started out by buying 2, allowing me to destroy one by desoldering components for easier tracing of
connections.

I'm not the first one to have a go at this board: the [FPGA Board Hack](https://hackaday.io/project/159853-fpga-board-hack) 
project on Hackaday.io did some work on this as well, but other than 
[a Quartus project on GitHub](https://github.com/MorriganR/c2hwic) to blink the LEDs, nothing has been documented: 
no connections from FPGA to connector, no explanation about how to power the board etc.

# An Annotated Overview of the Board

![Cisco HWIC-3G-CDMA PCB Top Annotated]({{ "/assets/cisco-hwic-3g-cdma/pcb_top_annotated.png" | absolute_url }})

![Cisco HWIC-3G-CDMA PCB Bottom Annotated]({{ "/assets/cisco-hwic-3g-cdma/pcb_bottom_annotated.jpg" | absolute_url }})

The PCB has a number of unpopulated component sites. That's because the design is used not only for the
CDMA version, but also GSM and HSPA variants, called, unsurprisingly, HWIC-3G-GSM and HWIC-3G-HSPA, both of 
which go for a considerably higher price on eBay.

The GSM version has a standard full-size slot for a SIM card as well as a large capacitance that's lacking on the
CDMA version. 

On the back side of the PCB, there is an intruiging TSOP-48 footprint which isn't populated for both versions. 
Was this originally designed to carry a flash chip?

The core functionality of this board comes from an integrated Sierra Wireless module that slots into a
PCI Express Mini Card.

Other than the wireless module, there's the Cyclone II FPGA, and an NXP ISP1564HL USB 2.0 Host PCI controller. (Yes,
that's old school PCI, not PCIe!)

This made me scramble to Google: why in the world would you need USB on a device like this?

Turns out: PCIe Mini Cards has support for 2 communication protocols between host and card: either PCIe 1x or USB 2.0. 
The more you know!

Also present: a 32MB DDR SDRAM for all your volatile data storage needs (Yay!), and the usual supporting cast of voltage
controllers, level shifters, LEDs, connectors, and various unknowns.

# Powering Up the Board

The first step of reverse engineering the VWIC2-2MFT-T1/E1 card consisted of unraveling its power supply architecture.
That board uses the full spectrum of available power sources of the HWIC connector: 12V, 5V and 3.3V (though
you cheat your way out with only a single 5V source.)

A similar exercise on this board had the following outcome:

* 12V: unused
* 5V: used for PCI Express card + mystery chip C9059
* 3.3V: used for everything else

At this stage, I was interested in getting the FPGA to talk: Can I make it work by supplying only power to the 3.3V rail? 
Let's find out!

But first, you need to connect to the JTAG port.

# JTAG Connector

JTAG is the life blood of any reverse engineer, and thus one first things to get up and running. Some boards have
a proprietary connector, some have the JTAG signals accessible as test points to which wire can easily be soldered,
some don't have anything at all.

And then there this board: it has a 10 holes in 2x5 configuration with "JTAG" printed right next to it on the silk
screen. Could it be that the Cisco engineers smiled up us and decides to add a standard Intel USB Blaster connector
for our benefit?

A few minutes of Ohm-ing out, and the best case scenario was confirmed. Time to bring out the solder iron and
desoldering needles, and install a 5x2 pin Dupont connector.

# And Life There Was!

All that remained was:

* Connect the 3.3V pin to my bench power supply
* Plug in a USB Blaster to the JTAG connector
* Fire up Quartus Programmer -> Auto Scan
* Boom! FPGA detected!

# LED Blinky

The FPGA Board Hack project already figured out the connections between the LEDs and the FPGA, so with JTAG up and
running, getting the LEDs to blink was a matter of minutes.

<iframe width="640" height="400" src="https://player.vimeo.com/video/372548312" frameborder="0" allowFullScreen mozallowfullscreen webkitAllowFullScreen></iframe>

Success!

# The Curious Case of Component C9059

With the Hello World of FPGA reverse engineering behind me, it was time to figure out the functionality of all other
components. Most of them have sufficient markings to be identified quickly with a Google search, but
2 components remained a mystery:

C9059, in an 8-pin package, and MXQ3311, in a 14-pin package. Googling these 2 devices results in no usable information.

![Mystery Chips]({{ "/assets/cisco-hwic-3g-cdma/mystery_chips.jpg" | absolute_url }})

In addition to a 5V VDD and GND, C9059 has 4 pins connected straight to MXQ3311. This made me theorize that C9059 was
a serial configuration PROM that contains the bitstream for the FPGA. Configured in Passive Serial mode, there
would need to be some kind of microcontroller to assist with copying over the data from the PROM to the FPGA.

The earlier VWIC2-2MFT-T1/E1 card has the same C9059 chip, confirming that it provides some common functionality that
is not unique to this particular design. And the Stratix II FPGA on that board has a very similar capacity in terms
of logic elements, DSPs, and memories.

But while there are indeed connections between the MXQ3311 and the FPGA, these connections don't seem to go to the
FPGA configuration pins.

Even stranger, the FPGA Board Hack project *also* had a go at reverse engineering the VWIC2-2MFT board. And when you
look at the pictures of their board the C9059 and MXQ3311 footprints are not populated! Unlikely that these were
desoldered after the fact, but that means that these components aren't even essential for basic operations.

After a while (hours!), I noticed that the VWIC2-2MFT board doesn't have an MXQ3311, but a CV9606 chip. One that
doesn't show up in any Google search either. Eventually, this made me go through all 5 of my Cisco boards to
see if there were other markings to be found.

And bingo! The second one of my VWIC2-2MFT board doesn't have a C9059 marking but 12836RCT. And the top Google
search hit for that results in "Secure Microcontroller for Smart Cards AT90SC12836RCT" which links to a 3 page
[datasheet](https://pdf1.alldatasheet.com/datasheet-pdf/view/255611/ATMEL/AT90SC12836RCT.html):

![12836rct Google Result]({{ "/assets/cisco-hwic-3g-cdma/12836rct_google_result.png" | absolute_url }})

Cisco components are expensive, but none of the main components on this board contains custom silicon.

Furthermore, unlike contemporary FPGAs, the Cyclone II FPGA has no support for encrypted bitstreams and design security
features where secret decryption keys can be one-time fused into the FPGA.

Without special steps, anybody could go to the open market to bulk purchase the FPGA, USB Host controller, and wireless
card, clone the PCB, and sell counterfeit versions. And that's exactly what happened in the past, as a quick
search for "counterfeit Cisco" will show.

However, a crypto device on the board can prevent this kind of cloning: with a challenge-response authentication
step, the hosting router can first verify that it is talking to a real Cisco sanctioned device before enabling 
enabling the functionality of the board by downloading the current bitstream.

In a way, the full value of the product lies on a small chip that can only be purchased from Atmel by Cisco, and
programmed by Cisco.

The AT90SC12836RCT has 128KB of fixed ROM and 36KB of reprogrammable ROM. Not nearly enough to contain the full 
bitstream (which requires 857,332 bytes). This kills the theory that these devices are used for configuration.

This leaves us with the MXQ3311/CV9606: it's almost certainly a level shifter to translate the HWIC 3.3V levels
to the 5V of the crypto chip and back.

Speaking of 5V: the datasheet brief of the AT90SC12836RCT mentions an operating range from 2.7V all the way to 5.5V.
*Why run the crypto chip at 5V when 3.3V would suffice?*

# Bitstream Configuration

With all other components identified, none of which containing flash, the only remaining option was that this FPGA
gets configured by the main router at bootup.

Figuring the HWIC pins that are reserved for this took much longer than expected: there are no straight connections
between the FPGA and HWIC connector. One of the most time consuming parts of reverse engineering a PCB is tracking
down connections that have small passive or active component in between them. The PCB has hundreds or even thousands
of them and the hidden layers on the PCB (especially on a sturdy high-quality one like this) leave random guessing
as the only option.

In the end, it came all down to 3 tiny components in an SOT23-5 package, marked in red below:

![Config Pins Photo]({{ "/assets/cisco-hwic-3g-cdma/config_sot23-5.jpg" | absolute_url }})

When you look on Mouser, there are many different kinds of components that use this package. My current
guess is that they are some variant of a 74xx125: a single bus buffer with tri-state, like
[this one](http://www.ti.com/product/SN74CBTLV1G125).

That would result in the following schematic:

![Config Pins Schematic]({{ "/assets/cisco-hwic-3g-cdma/config_pins.draw.io.svg" | absolute_url }})

It doesn't make a whole lot of sense, but it should be sufficient to download the bitstream through the 
HWIC interface when the time comes... And if it doesn't I can always use the JTAG interface and an SVF
file to initialize the FPGA instead.

# Block Diagram: Putting It All Together

And with that, all components and connections have been identified, giving us the following block diagram:

![Block Diagram]({{ "/assets/cisco-hwic-3g-cdma/hwic-3g-cdma-diagrams.svg" | absolute_url }})

# Low Level Connections

Block diagram is one thing, you need the know exactly which pin of the FPGA is connected to what.

When this article went to press, progress was as follows:

* All HWIC interface signals identified
* FPGA configuration pins identified
* FPGA configuration pins identified
* Connections between FPGA and SDRAM fully mapped
* Connections between FPGA and RS232 connector fully mapped

To be done:

* Connections between FPGA and PCI USB Host chip.

The [GitHub repo of this project](https://github.com/tomverbeure/cisco-hwic-3g-cdma) is still very much in 
flux, but all the low level details can be found there.

(*) Hang on! This is still a developing story!

