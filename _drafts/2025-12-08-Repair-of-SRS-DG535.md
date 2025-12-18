---
title: The Scenic Route to Repairing a Self-Destructing SRS DG535 Digital Delay Generator
date: 2025-12-08 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I got my hands on a [Stanford Research Systems DG535](https://www.thinksrs.com/products/dg535.html)
at the [Silicon Valley Electronics Flea Market](https://www.thinksrs.com/products/dg535.html), $40
for a device that was marked "X Dead".

![DG535 at flea market](/assets/dg535/DG535_at_flea_market.jpg)

That's a really good deal: SRS products are pricey and even 
the cheapest *Parts-Only* listings on eBay are $750 and up. Worst case, I'd get a few weekends
of unsuccessful repair entertainment out of it, but even then I'd probably able to recoup my money
by selling pieces for parts.[^parts] Just the keyboard PCB is currently selling for $150[^keyboard].

[^keyboard]: Whether or not it will ever sell for that asking price is a different story.

[^parts]: Not that I've ever done that, but it's what I tell my wife.

It doesn't matter how broken they are, the first step after acquiring a new toy is cleaning up
years of accumulated asset tracking labels, coffee stains, finger grime and glue residue. This one 
cleaned up nicely: the front panel is pretty much flawless:

![DG535 front view](/assets/dg535/DG535_frontview.jpg)

After an initial failed magic smoke repair attempt, the unit ended up in the garage for
18 months, but last week I finally got around to giving it the attention it deserves.

The repair was successful, and when you only look at the end result, it was a straightforward 
replacement of a diode bridge and LCD panel. However, the road to get there was long and winding, 
and most important, the broken power architecture and awkward mechanical design of the SRS 
DG535 make it way too easy to damage the device while trying to repair it.

So let's get that advise out of the way first:

**Do NOT power on the device with the analog PCB disconnected. It will almost certainly self-destruct
with burnt PCB traces.** 

The details will be explained further below.

# The Stanford Research Systems DG535

Conceptually, the purpose of the DG535 is straightforward: it's a tool that takes in an input
trigger pulse and generates 4 output pulse after some programmable delay. What makes the DG535 interesting 
is that these delays can be specified with a 5 ps precision, though the jitter on the outputs far
exceed that number.

The DG535 has 9 outputs on the front panel:

* T0 marks the beginning of an event. It's created by the internal or external trigger.
* 4 channels A, B, C and D can independently be programmed to change a programmable time after T0
  or after some of the other channels.
* Outputs AB and CD and inverted AB and CD are a XNOR or XOR of signals A and B, and signals C
  and D respectively.

[![DG535 timing diagram](/assets/dg535/DG535_timing_diagram.jpg)](/assets/dg535/DG535_timing_diagram.jpg)
*(Click to enlarge)*

All outputs can be configured to a number of logic standard: TTL, ECL, NIM[^NIM], or fully programmable
voltage amplitude and offset.

[^NIM]: NIM stands for Nuclear Instrumentation Model. It's a voltage and current standard for fast
        digital pulses for physics and nuclear experiments.

While all settings can be configured through the front panel, a GPIB interface is available in
the back for remote control by a PC.

![DG535 rear view](/assets/dg535/DG535_rearview.jpg)

In addition to the GPIB interface, the back has another set of T0/A/B/C/D outputs because my unit
is equiped option 04. These outputs are not an identical copy of the ones in the front: their output
voltage is much higher. There is also a connector and a switch to select the internal or an external
10 MHz timebase.

Missing screws on the connector are a first indication that I'm not the first one who has been
inside to repair the unit...


The DG535 is still for sale on the SRS website for $4495, remarkable for an instrument that
dates from the mid 1980s. I assume that today's buyers are primarily those who need an exact replacement
for an existing, certified setup, because the [DG645](https://www.thinksrs.com/products/dg645.html), 
SRS' more modern successor to the DG535 with better feature and specs, costs only $500 more.

# Who Uses a Pulse Delay Generator?

Anyone who has a setup where multiple pieces of test or lab equipment need to work together with a
strictly timed sequence.

When you research applications where the DG535 is used, you'll find long list of PhD thesis, national
or military laboratory documents, optical setups with lasers and so on. If you look closer at the first 
picture of the blog post, you can see that mine was used by Chemical Dynamics to in a molecular beam setup... 
whatever that is.

Here are just a few examples:

* [Combustion and Flame - A comprehensive study on dynamics of flames in a nanosecond pulsed discharge. Part II: Plasma-assisted ammonia and methane combustion](https://www.sciencedirect.com/science/article/pii/S0010218025001142)

  > We employed a delay generator (SRS system, DG535) to control the timing of the plasma 
  > and measurement systems. The DG535 generator was externally triggered by the pre-triggering 
  > signal from the laser system and then sent sequential TTL signals to trigger the ns 
  > pulse generator and camera.

* [Astigmatism-free 3D Optical Tweezer Control for Rapid Atom Rearrangement](https://arxiv.org/html/2510.11451v1)

  > Images were taken at delayed time steps (250-ns shutter, SRS DG535) as the translation 
  > stage was stepped from Z min = − 24.5 mm to Z max = 24.5 mm. 

* [Rapid elemental imaging of copper-bearing critical ores using laser-induced breakdown spectroscopy coupled with PCA and PLS-DA](https://www.sciencedirect.com/science/article/pii/S0039914025009531)

  > A delay generator (SRS DG-535) synchronized the laser and detection systems to capture 
  > time-integrated spectra at each point.

* [High-precision Gravity Measurements Using Atom-Interferometry](https://www.researchgate.net/publication/231085177_High-precision_Gravity_Measurements_Using_Atom-Interferometry)

  > The timing of the pulsesis controlled by a set of synchronized pulse generators
  > (SRS DG535), one of which also triggers all thehardware involved in generating the 
  > Raman frequencies.

* [Physics of Plasmas - Laboratory generation of multiple periodic arrays of Alfvénic vortices](https://pubs.aip.org/aip/pop/article/32/12/122109/3374743/Laboratory-generation-of-multiple-periodic-arrays)

  > Each antenna was switched on with a pulse generator (Stanford SRS-DG535), which then activated 
  > two arbitrary waveform generators (Agilent 3322 A).

* [Liquid-to-gas transfer of sodium in a liquid cathode glow discharge](https://www.researchgate.net/publication/382346349_Liquid-to-gas_transfer_of_sodium_in_a_liquid_cathode_glow_discharge)

  > The laser system, operating at a 200 Hz repetition rate, was synchronized with the 
  > plasma discharge using a SRS DG535 delay generator, allowing time-resolved measurements 
  > of Na fluorescence during and after the discharge pulse.

At this time, I don't have a use for a pulse delay generator, but as a hobbyist it's important 
to keep this slogan in mind:

**We buy test equipment NOT because we need it, but because one day we might need it.**

I don't see a future where I'll be doing high-precision gravity measurements in my garage, but
a DG535 could be useful to precisely time a voltage glitching pulse when trying to break the
security of a microcontroller, for example.

# Inside the DG535

It's not complicated to create pulse delay generator as long as delay precision and jitter
requirements are larger than the clock period of the internal digital logic: a simple digital
will do. But when the timing precision is much smaller than the clock speeds, you need analog
wizardry to make it happen. 

SRS includes detailed schematics and theory of operation for many of their products and the
DG535 is no exception. It's such a great way to study and learn how non-trivial problems
were solved 40 years ago.

The DG535 uses a combined digital/analog approach to create delays that are up to 1000s long.
Using an 80 MHz internal clock, the digital delay can be specified with 12.5ns of precision.
The remainder is handled by an analog digital-to-time converter.

![Analog delay schematic](/assets/dg535/dg535-analog_delay.svg)

It works as follows: a 12-bit DAC provides a voltage to set a delay from 0 to 12.5ns. If
you're wondering where the 5 ps of precision is coming from: 12.5 ns / (2^12) = 3 ps. Close
enough! At the start, a capacitor is discharged to ground through a resistor. When the delay 
must generated, the input of the capacitor is switched to a constant current source, causing
the voltage on the capacitor to rise linearly in time. A comparator checks the capacitor
voltage against the DAC voltage. When the capacitor voltage exceeds the one of the DAC,
the comparator flips and its output is deasserted.

It's simple in practise, but to make it work 


If you look carefully in the schematic, you notice that the right side input of the
comparator comes from a net that is called Vjitter. This is a crucial element in bringing
down jitter that is caused by the asynchronous crossing between the external trigger
input and the internal 80 ns clock. Vjitter is a voltage that proportional to the delay
between the starting edge of the external trigger and the first rising edge of the 80 MHz
clock. While the output delay is generated by the C-charging circuit to convert a digital
value to a time, the Vjitter circuit does the opposte: a capacitor is charged for the duration
between the 2 pulses and the output, Vjitter, reflects this time. It's a technique called
"analog interpolation" that is used by time interval and frequency counters such as the
SRS SR620. I briefly touch this in my blog post about linear regression in frequency
counters.

By compare the voltage of the delay generator against Vjitter, the DG535 is essentially
subtracting the analog output delay from the delay between external trigger and the clock.
If the charging slope of the capacitor in both circuit is carefully calibrated to be the same,
the overall delay generator becomes immune to the jitter introduced by the 80 MHz clock.

# The Annoying Mechanical Design of the DG535

In my blog post about the SR620, I comment on a mechanical design that gives full access
to all components by just removing a top or front cover. The DG535 is a different story. 

[![DG535 open side view](/assets/dg535/DG535_open_sideview.jpg)](/assets/dg535/DG535_open_sideview.jpg)
*(Click to enlarge)*

[![DG535 open bottom view](/assets/dg535/DG535_open_bottomview.jpg)](/assets/dg535/DG535_open_bottomview.jpg)
*(Click to enlarge)*

While the covers are just as easy to remove, the functionality is spread over 2 large 
PCBs, mounted with components facing inwards, and connected with a bunch of cables 
that are way too short. 

SRS was clearly aware that this kind of PCB arrangement makes a unit harder to repair,
because they helpfully added component ID and even component name annotations on 
the solder side of the PCB, though sadly no dots to mark pin of an IC.[^pin_dot]

[^pin_dot]: When dealing with mirror image of an IC footprint, I'm constantly
            second guessing myself about whether or not I'm probing the right pin.

![PCB solder-side annotated](/assets/dg535/PCB_solderside_annotated.jpg)

Most cables have connectors and can easily unplugged, but not the OPT04 board that drives 
the backside connectors.

![Power supply wires for OPT04 board](/assets/dg535/power_supply_wires_to_opt04.jpg)

The red and orange wires in the picture above provide +20 and -20V rails. They are just
long enough to connect the top PCB to the OPT04 board at the bottom. If you want to
take the unit apart, your only choice is desoldering these wires. It's not rocket science,
but... really? You also need to desolder the wires that power the cooling fan.

Enough whining... for now... When all wires are desoldered, connecters disconnected and screws
removed, you can fold open top PCB from the rest of the unit and get a full view of the inner
components:

[![DG535 folded open](/assets/dg535/DG535_folded_open.jpg)](/assets/dg535/DG535_folded_open.jpg)
*(Click to enlarge)*

There are 2 major sections: 

* the top PCB contains a Z80-based controller and the counters that are used for the digital
  delay generation
* the bottom PCB contains the rest of the delay circuitry
* the front has a generic LCD panel and a keyboard and LED PCB

# It's Always the Power Supply

Before taking it apart, I had already powered up the device and nothing happened: the LEDs 
and the LCD screen were dead, only the fan spun up. No matter what state a device is in,
you always have to make sure first that power rails are functional.

The power architecture is split over the top and bottom PCB, but the secondary windings of 
the power transformer first go to the top PCB. *Since the transformer is located at the bottom,
you always need to keep top and bottom closely together if you want to make live measurements.*

[![Power supply schematic top](/assets/dg535/power_supply_top.jpg)](/assets/dg535/power_supply_top.jpg)
*(Click to enlarge)*

We can see integrated full-bridge rectifier BR601 go to linear regulators U601 and U503 to create
+15V and -15V and immediately go to the connector on the right which goes to the bottom PCB. These
voltage rails are not used by the top PCB.

A discrete diode bridge and some capacitors create an unregulated +/-9V that goes to the same connector
and to the LM340-5, which is functionally the same an 7805, a linear +5V regulator. The 5V is used
to power pretty the entire top PCB as well as some ICs on the bottom.

When I measured the voltages on the top-to-bottom power connector, I saw the following:

* 0V (instead of 10V)
* +15V - good!
* +12V - instead of +9V
* +7V - instead of +5V. Horrible!
* GND
* 0V - instead of -9V
* -15V - good!

The lack of 10V is easy to explain: it's an input, generated out of the +15V by a high precision voltage
reference. On the top PCB, it's only used for dying gasp[^gasp] and power-on/off reset generation.

+12V instead of +9V was only a little bit concerning, at the time; the lack of -9V was clearly a problem,
and +7V instead of +5V is a great way to damage all digital logic.

Here's the part of the PCB with the 9V diode bridge:

![9V diode bridge](/assets/dg535/diode_bridge.jpg)

Observations:

* the discrete diodes look like a bodge
* there is a blackened spot above-right of the diodes
* there is a green bodge wire. There are quite a bit of those and they are harmless,
  they work around bugs in the PCB itself.

2 diodes were on the other side of the PCB to complete the full bridge, though one soon
fell off. You can't see it in this picture, but be underneath the left diode is a footprint
for a BR501 full bridge rectifier *that is not in the schematic*[^schematic]!

[^schematic]: I emailed SRS to ask if they had an updated schematic, but they told me
              to send in the unit for repair.

While doing these measurements, magic smoke appeared at the same location as 
in the picture. At that point, I called it quits and left the unit sit for 18 months.

[^gasp]: When the +9V voltage rail drops below +7.5V, the dying gasp circuit creates a non-maskable
         interrupt to the CPU, allowing to quickly store data in non-volatile RAM before the power
         is completely gone.


# Power Architecture of the DG535

I suspected an issue with the discrete diode bridge bodge on the top PCB, so the plan
was to repopulate the PCB with an integrated full-bridge rectifier. Turns out: even though
the schematic in the manual shows a discrete bridge, the schematic description indeed
talks about an integrated full bridge. Instead of buying one at Digikey (and pay $7 for
shipping a $2 component), I found a suitable 100V/2A alternative, a 2KBP01M, at Anchor
Electronics, the last remaining Silicon Valley components supplier, conveniently 
located across the street from work.

I also had a look at the power supply of the bottom PCB:

[![Bottom PCB power supply](/assets/dg535/power_supply_bottom.jpg)](/assets/dg535/power_supply_bottom.jpg)
*(Click to enlarge)*

More linear regulators, 2 on the unregulated +8V (?) rail to create +6V and +5.2V, and 3 on
the unregulated -8V rail to create -2V, -5.2V, and -6V (actually -5.6V). 

Now here's the interesting part: the -2V and -5.2V rails have heavy duty 5W 18 and 10 Ohm resistors 
between the input and the output of the linear regulator.

![Current boost resistors](/assets/dg535/current_boost_resistors.jpg)

These are called *current boost* resistors and while they are useful in the right'
conditions, they are bad news. And when we go back to the top PCB, here's what we see:

![5V current boost resistor](/assets/dg535/5v_current_boost_resistor.jpg)

It may not be in the schematic, but located right next to the 7805 5V regulator is
another 10 Ohm 5W current boost resistor. 

# How and Why of Current Boost Resistor Circuit

Imagine we have design with a 5 V rail and a load with an equivalent resistance of 3 Ohm,
good for constant current draw of 1.67 A. When we only use a linear regulator with 9 V on the
input side, the current through the regulator will be 1.67 A as well and the regulator 
needs to dissipate (9-5) * 1.6 A = 6.7 W. That is too much for a 7805 in TO-220 package 
to handle. With the right heatsink, 1.5A is about the limit of what it can deal with.

The purpose of a current boost resistor is to partially off-load a linear regulator. The
7805 still supplies current to keep the voltage over the load at 5V, but current boost
resistor injects a constant current of (9-5)/10 Ohm = 0.4 A. This reduces the current
through the regulator from 1.67 A to 1.27 A and the power dissipation from 6.7 W to 5.1 W. 
The dissipation in the resistor is now (9-5)^2 / 10 Ohm = 1.6 W. Which brings the total 
power consumption back to 5.1 W + 1.6 W = 6.7 W.

What have we gained? The overall power consumption stayed the same, but we're now staying
within the current and power limits of the 7805 in TO-220 package, all for the price
of adding a beefy 10 Ohm resistor. The alternative would mounting the TO-220 onto a larger
heatsink or even switching to a 7805 in TO-3 package. Both options would require some
mechanical redesign.




# References


# Footnotes

