---
layout: post
title: Repairing an HP 3478A Multimeter with a Hacksaw
date:  2021-11-21 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I'm slowly building a small stable of test and measurement equipment for my home lab. 
I'd be lying if I said that it's out of hard necessity: almost all my projects are FPGA 
based and digital in nature. You don't *need* a 
[nice high precision power supply](/2021/04/15/Agilent-E3631A-Knob-Repair.html)
to power a generic FPGA development board, but when there's one for offered on Craigslist for
a good price, it's hard to resist. One day that that GPIB control interface might come in real handy 
after all.

And that's how, a few months ago, this HP 3478A benchtop multimeter appeared at my front door: 

![HP 3478A](/assets/hp3478a/hp3478a.jpg)

On eBay, these 5 1/2 digit meters go for around $140 when listed as Pre-Owned, while Parts Only devices
go for around $70. In both cases, shipping cost is usually around $25. My unit was advertised as
Pre-Owned with a "Passes Self-Test" description for a low low price of only $100, so I decided
to take a chance on it.

Well, a passing self-test was what advertised, and a passing self-test is what I got!

![Self Test OK](/assets/hp3478a/self_test_ok.jpg)

But that's where it ended. Because other than the power switch, none of the front panel
buttons had an effect. I could use the thing to measure DC voltages, the default setting after
powering up, but that was about it.

The multimeter went onto an empty shelve, waiting for its time in the spotlight.

After playing with JTAG and other debugging techniques for a bit too long, Thanksgiving week was the 
perfect time to give the 3478A some tender loving care.

# 3478A Features

Check out [the datasheet](/assets/hp3478a/agilent_hp_3478a_datasheet.pdf) for the details, but
here's a quick summary of some of the 3478A features:

* 5 measurement types: AC and DC voltage, AC and DC current, resistance
* 3.5, 4.5 and 5.5 digit resolution
* 71 measurements per second when using 3.5 digit resolution
* GPIB interface
* 2-wire and 4-wire resistance measurement
* AC voltage and current measurements are true RMS

![HP Catalog - DVMs](/assets/hp3478a/hp_catalog_dmvs.png)

Let there be no doubt: a working 3478A far exceeds my measurement needs.

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

There's even a work-in-progress [MAME 3478A emulator](https://github.com/mamedev/mame/blob/master/src/mame/drivers/hp3478a.cpp), 
which is a great resource to understand some of the internals of the device.

This quote from [discussion thread on the EEVblog forum](https://www.eevblog.com/forum/beginners/is-190$-a-bargain-for-a-hp-2378a-bench-multimeter/)
is a bit ominous: 

>  3478 are not bad but they are virtually unrepairable if they break. Especially the display is unobtainium...

But somebody [managed to replace the LCD on a 3457A with an LED display](https://www.eevblog.com/forum/projects/led-display-for-hp-3457a-multimeter-i-did-it-),
so maybe something similar is possible on a 3478A?

Checkout the bottom of this blog post for a list.

# The 3478A Architecture

![Block Diagram](/assets/hp3478a/block_diagram.png)


The 3478A first came to market in 1981. But despite being 40 years old, it has not one but 2 microcontrollers.
That's because it's split into 2 electrically isolated sections: the "chassis common" section has the ground
connected to the chassis and takes care of the display, the buttons, the GPIB interface, and configuration management.
The "floating common" section handles measurements of voltage, current, and resistance. 

The chassis common section has an Intel 8039 microcontroller without internal ROM. The ADC controller is an Intel 8049
with internal ROM.  Both are microcontrollers of the [Intel MCS-48 family](https://en.wikipedia.org/wiki/Intel_MCS-48) 
with a whopping 128 bytes of on-chip RAM. The firmware of the 8039 is stored on an 8KB 2764 EPROM, one of those old 
style types that must be erased by shining a bright UV light on a glass window. A 256 x 4bit static RAM is used to store 
calibration data. A 3V lithium battery powers the SRAM when main power is switched off.

The AD converter of the 3478A doesn't use a high precision integrated circuit, but it's built from
discrete components and uses an integrator, a voltage reference and a comparator, under control of the 8049
microcontroller.

![AD Converter Diagram](/assets/hp3478a/ad_converter_diagram.png)

The ADC is based on a dual-slope conversion:

![Dual slope conversion](/assets/hp3478a/dual_slope_conversion.png)

* During the runup phase, the signal that must be measured is applied to the input of the integrator for a 
  fixed amount of time. 
* This charges a capacitor with a charge that's proportional to the voltage of the signal.
* during the following rundown phase, the integrator is discharged by applying a constant, known voltage reference to the input.
* the time needed to discharge the capacitor is proportional to the voltage of the input signal.

In other words, the AD convertor transforms a voltage to time, which is much easier to measure with high precision.

The real implementation is a bit more complex and uses the so-called Multi-Slope II method, which uses
the runup phase to determine the most significant digits and the rundown phase for the least significant
digits.

The detailed explanation is well beyond the scope of this blog post, but section 7-F-31 of the service manual
describes the process very well.

The [floating ground](https://en.wikipedia.org/wiki/Floating_ground)
of the measurement section makes it possible to connect the ground of the multimeter
to any random reference point of the device under test and measure other voltage compared to that reference
point. However, since the digital control section and the measurement section must remain electrically
isolated, communication between the section can't be done with a simple wire.

In most such configurations, an optocoupler is used. Later versions of the 3478A, such as 
[the one featured in the EEVblog teardown video](https://youtu.be/9v6OksEFqpA?t=211), 
use exactly that. But older ones like mine have magnetic couplers. There's one for each direction, from 
the digital part to the measurement part, and back.

![Magnetic coupling schematic](/assets/hp3478a/magnetic_coupling.png)

# A First Look inside the Box

To get a first inside look, you need to remove 2 screws on the back, and one in the back
at the bottom. The metal enclosure will slide right off, and you get to see this:

![Inside Overview](/assets/hp3478a/inside_overview.jpg)

The layout is really straigthforward. You can clearly see the separation between the control
and power sections at the top and the floating measurement section at the bottom. And just
below the main power transformer on the right, there's the 2 smaller transformers that form
the magnetic couplers.

![Magnetic Couplers](/assets/hp3478a/magnetic_coupler_transformers.jpg)

# Tracking Down Failing Buttons

Time to starting looking at the issue at hand: failing buttons. Not one, not a few, but all of them.
That can be a good thing, because it suggest that's there's a single, catastrophic, issue. Chances are that
fixing this one thing will make all buttons work again.

The schematic couldn't be easier:

![Buttons schematic](/assets/hp3478a/buttons_schematic.png)

The expected 14 buttons are wired up in a 4 by 4 matrix configuration that is controlled
by 8 GPIO pins of digital control microcontroller U501.

With a circuit this simple, there's only a few possible ways things could fail:

* the switches of the buttons are broken. 
    
    But what are the chances that all buttons are broken at the same time?

* the ports P10-P17 of the microcontroller are broken.

    In other words, the microcontroller is toast. That'd be a worst case situation.

* a connection issue between the microcontroller and the buttons.

Since the device is still printing out "Self Test OK" and showing a DC voltages, the microcontroller
is at least partially working, so the last option is the most likely.

I first put a continuity tester on the ~A button, pressed it and had a beep. (Good!) Then 
I put the probes on pins 28 and 31 (ports P11 and P14) of the microcontroller, pressed the
button again, and... got nothing.

![AC current button test points](/assets/hp3478a/ac_current_button_testing.jpg)

Conclusion: it's almost certainly a connection issue between button board PCB and the main PCB!

Let's have a closer look at this connector.

# Taking Everything Apart

It's easier said than done: the connector is on the bottom side of the PCB and impossible to reach
because there's a fat bezel around it. We'll have to take the thing apart. Or at least partially:
the main PCB, and the front assembly with the buttons and the LCD needs to slide out enough to
get access to the button PCB and the connector that links it to the main PCB.

The disassembly isn't very complicated, but make sure to keep track of how cables were connected so that you
can later reconnect them correctly. (Or just use the pictures below!)

Here's a short list of what I needed to do:

* Unplug the GPIB cable. This took quite a bit of effort, and was probably the scariest part.

    ![Remove GPIB cable](/assets/hp3478a/remove_gpib_cable.jpg)

    One pin of the connector was bent. I'm almost certain that it was already bent before I removed 
    it.

* Loosen the main power switch assembly by removing its 2 screws.

    ![Power switch assembly screws](/assets/hp3478a/power_switch_assembly_screws.jpg)

* Dismount the power regulator that's screwed to the chassis right next to the power switch.

    ![Power regulator screw](/assets/hp3478a/power_regulator_screw.jpg)

* Remove the 2 screws that tie the main transformer to the chassis.

    ![Transformer screws](/assets/hp3478a/transformer_screws.jpg)

* Remove the ground chassis screw in the back.

    ![Ground chassis screw back](/assets/hp3478a/ground_chassis_screw_back.jpg)

* Remove the ground chassis screw in the front.

    ![Ground chassis screw front](/assets/hp3478a/ground_chassis_screw_front.jpg)

* Unplug the yellow and pink wires next to the GPIB plug.

    ![Yellow and pink wires](/assets/hp3478a/yellow_and_pink_wire.jpg)

* Unplug the orange, brown, read, black and blue wires in the back.

    ![5 wires](/assets/hp3478a/5_wires.jpg)


* Rotate the device 90 degrees so that it rests on a narrow side, with the front
  facing to you.  You'll see 4 notches that keep the PCBs locked into place.

    ![Front bezel notches](/assets/hp3478a/front_bezel_latches.jpg)

* Force the plastic enclosure open to unlock the front panel, and apply some pressure on the 
  power connector in the back. When all 4 notches are unlock, the front panel and main PCB
  will slide forward.

    ![PCBs unlocked](/assets/hp3478a/pcbs_unlocked.jpg)

    Don't slide out everything out completely: the 5 wires that you unplugged earlier are connected
    to the chassis through some ties. It's sufficient to slide everything forward by a little
    bit over an inch or 2.

* Unplug 4 wires between the front panel and the main board: orange, gray, red, black.

    ![4 wires](/assets/hp3478a/4_wires.jpg)

* Finally, unplug the yellow wire, also between the front panel and the main board, but this time, the
  fixed pin is located on the main board, and a bit recessed below the plastic enclosure.

    ![Front yellow wire](/assets/hp3478a/front_yellow_wire.jpg)

* Turn the device upside down. You can see the connector between the button PCB and the main board:

    ![Connector between button PCB and the main board](/assets/hp3478a/button_panel_to_main_board_connector.jpg)

* Remove those 2 screws. The front panel will now be loose, except for the flat-cable that goes
  between the main board and the LCD.

    ![Button connector disconnected](/assets/hp3478a/button_connector_disconnected.jpg)

* If it's possible to unplug the cable between LCD and main board, it's definitely hard to do so. 
  Much easier to keep it connected and unscrew the LCD from the front panel instead.

    ![LCD screws](/assets/hp3478a/lcd_screws.jpg)

* The front panel is now completely disconnected. Let's remove those last 2 screws to
  remove the connector from the front panel.

    ![Front panel disconnected](/assets/hp3478a/front_panel_disconnected.jpg)

* With the connector removed, we are at the end of this journey!

    ![Button connector removed from front panel](/assets/hp3478a/button_connector_removed.jpg)

# The Button Board to Main Board Connector

The electrical connection between the 2 button board and the main board is unusual: instead
of a cable, there is a element with a 90 degree angle that consists of tiny individual metal
wires. The connector presses this element against the copper pads on both PCBs and creates
an electric connection between them.

![Conductive element inside connector](/assets/hp3478a/connector_conductor.jpg)

Or at least, that's what it's supposed to do.

One way or the other, all 8 connections on my device stopped working. I assume it had to do
with oxidation on the contacts?

This method of linking 2 board seems flimsy to me, and prone to fail over time. On the
other hand, Google didn't find anything related to buttons failing on 3478A multimeters, so maybe
mine is really an exception?

# Fix 1: Works, then Fails after 5 minutes

Everything looked very clean, no visible oxidation to be seen, but I used isopropyl alcohol 
to clean the contacts and connection strip. I assembled the connector back onto the LCD and the main board PCB and 
verified with a continuity tester that there was an electrical connection now between all contacts.

I then put the whole multimeter back together (retrace all the steps I documented earlier), powered
it on and... SUCCESS!

All buttons were now working perfectly... for 5 minutes.

After that, 4 out of the 14 buttons became unresponsive again.

# Fix 2: Bring Out the Hacksaw!

If that unusual connector mechanism doesn't work, why not switch to the more traditional way
of doing things, with wires? That's exactly what I did.

The connector is still useful to mechanically align the 2 PCBs, so I simply sawed away the center
part of the connector, retained the 2 ends with the screw holes, and ended up with this:

![Connector center removed](/assets/hp3478a/connector_center_removed.jpg)

The rest is obvious: I soldered a tiny wire between each of the connection pads.

Instead of using a tiny wire, I could have created a solder bridge between the opposing
connection pads of the 2 PCBs, but that would probably have been too brittle to survive long
term use. A wire will allow some flex when enthousiastically pressing on a button.

![Wire between connection pads](/assets/hp3478a/wire_between_connection_pads.jpg)

After soldering all connections, it looked like this:

![All connections soldered](/assets/hp3478a/all_connections_soldered.jpg)

I went through the whole reassembly procedure once more, and, again... SUCCESS! But
this time, it kept working after 5 minutes.

Here's the multimeter measuring a *zero* Ohm connection with some very cheap crocodile
clips.

![Ohm measurement](/assets/hp3478a/ohm_measurement.jpg)

# Conclusion

This was a fun evening project, and I've learned a bunch about the internal of multimeters too.
There's a lot of information out there. I've listed some of it in the references
below.


I've compared a number of measurements between my handheld multimeter and this one, and the
results are pretty much the same. That said, I have no clue how long it has been since
the meter was last calibrated, and I don't have any calibrated voltage sources or reference 
resistors so who knows how accurate my measurements really are? Since calibration
can easily cost $100 or more, I have no plans to do so until I really need 5 digit accuracy.

For now, the multimeter will take its place back on the shelve. A handheld multimeter is
more convenient. But if, one day, I'll need an automated measurement setup, it will be ready to go.

# References

**Official Documentation**

* [3478A Datasheet](https://accusrc.com/uploads/datasheets/agilent_hp_3478a.pdf)
* [3478A Service Manual](http://www.arimi.it/wp-content/Strumenti/HP/Multimetri/hp-3478a-Service.pdf)
* [HP Journal - February 1983](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1983-02.pdf)

    Technical description of the closely related 3468A multimeter.

* [HP Catalog 1983](http://hparchive.com/Catalogs/HP-Catalog-1983.pdf)

**Youtube Videos**

* [EEVblog #427 - HP 3478A Multimeter Teardown](https://www.youtube.com/watch?v=9v6OksEFqpA) 
* [NFM - HP 3478A Multimeter Repair and Test](https://www.youtube.com/watch?v=e-itiJSftzs)
* [Tony Albus - HP 3478A Multimeter Teardown](https://www.youtube.com/watch?v=q6JhWIUwEt4)

**Various Discussions and Article**

* [Discussion on EEVblog](https://www.eevblog.com/forum/beginners/is-190$-a-bargain-for-a-hp-2378a-bench-multimeter/)
* [3468A Battery replacement](http://mrmodemhead.com/blog/hp-3468a-battery-replacement/)
* [KO4BB Manuals & EPROM dump](http://www.ko4bb.com/getsimple/index.php?id=manuals&dir=HP_Agilent/HP_3478A_Multimeter)
* [MCS-48 Datasheet](/assets/hp3478a/mcs48_datasheet.pdf)

