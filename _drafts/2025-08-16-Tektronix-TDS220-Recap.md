---
layout: post
title: Refurbishing a Tektronix TDS220 Oscilloscope 
date:   2025-08-16 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I found a [Tektronix TDS220 oscilloscope](https://w140.com/tekwiki/wiki/TDS220) at the
[electronics flea market](https://www.electronicsfleamarket.com). 
The seller told me that it worked but that the screen flickered a bit and that
this model is known to have issues with leaking capacitors. He asked $25 which 
would be an great price for an evening of entertainment even if an oscilloscope
wasn't part of the deal.

Wise men claim that you should not power up an old device that might have issues with
leaking capacitors, but it obviously did that anyway. It powered up nicely with
some occasional flickering at the bottom of the LCD. When connected to a signal generator 
it showed 2 sine waves:

![TDS220 showing 2 sine waves](/assets/tds220/tds220_2_sine_waves.jpg)

But when I connected the probe to the probe compensation pin, 
I got the signal below instead of a square wave:

![TDS220 definitely not showing a square waveform](/assets/tds220/tds220_probe_compensation_waveform.jpg)

The scope had this issue for both channels.

Alright, maybe I'd get more than just an evening of fun out of it.

# The TDS220 Oscilloscope

The TDS220 was introduced in 1997. It was a low cost oscilloscope with a limited
number of features, but with a weight of just 1.5kg/3.25lb and a small size, it was
great for technicians and education. I'm not sure if it was Tektronix' first oscilloscope
with an LCD but, if not, it was definitely one of the early ones.

Some key characteristics:

* 2 channels
* 100 MHz/1Gsps
* 2500 sample points per channel
* Only a few measurements: period, frequency, cycle RMS, mean and peak-to-peak voltage

With an extension board, you could add parallel and GPIB port and FFT functionality, but
even with those, it's reallly a bare bones scope.

And yet, I expect that I'll be using it quite a bit: it's so portable and the
footprint is so small that it's perfect for a quick measurement on a "busy" workbench.

Let's take it apart!

# Opening Up the TDS220

Opening up the TDS220 isn't hard, but you need to do the steps in the right order and there's
a bit of bending-the-plastic involved.

**Remove handle and power button**

![TDS220 handle and power button](/assets/tds220/tds220_handle_and_power_button.jpg)

The handle must lay flat against the case to wide and remove it. The white
knob can simply be pulled off.

**Remove the 2 screws**

Once the handle it removed, you get access to 2 screws, one on each side. Remove
them with a Torx 15 screwdriver.

**Remove expansion module**

If you have a TDS2CM or TDS2MM expansion module, you need to remove it because
otherwise will block the case from coming off.

It took me longer than I care to admit before I figured it out how to do this. 
There is no need to play with the tab at the top of the module, just forcefully slide 
the thing upwards until it disconnects from the connector at the bottom.

![Sliding up the expansion module](/assets/tds220/tds220_remove_expansion.jpg)

**Pry off the back case**

This is the part that I always hate, because you need to figure the the best location
where to jam screwdriver between 2 pieces of pastic and hope for the best. And based
on the scuff marks in the picture below, others have struggled with it as well.

![Remove back cover](/assets/tds220/tds220_remove_back_cover.jpg)

But I think I found the best way to go about it now. At the right side, insert the
screwdriver horizontally between the blue and the white plastic and then lift the blue 
part. Insert a smaller screwdriver in the gap that you just made to prevent it from closing again
and repeat the same operation in the middle and the left.

**Inside exposed**

You can now take off the blue back cover and have a look at the inside of the scope.

[![TDS220 inside exposed](/assets/tds220/tds220_inside_exposed.jpg)](/assets/tds220/tds220_inside_exposed.jpg)
*(Click to enlarge)*

There are 2 PCBs: the left horizontal PCB contains all the acquistion and processing logic.
The one on the right is the power supply.

**Extract the power supply PCB**

To remove the power supply, unplug the orange bundle with 7 wires from the main PCB as 
well as the fat ground wire. The PCB is held in place by 2 plastic tabs at the bottom.

# Common TDS220 issues

Here are the most common TDS220 issues:

* leaking capacitor in the power supply
* mechanical stress around the BNC connectors
* LCD backlight too weak or not working

# Replacing the power supply capacitors

I didn't take pictures of it, but the solder side of the power supply PCB was drenched
in a light-brown/yellow-ish fluid. Some of that make it to the front side of the PCB
as can be seen here:

[![Fluid on front of the PCB](/assets/tds220/fluid_marks.jpg)](/assets/tds220/fluid_marks.jpg)
*(Click to enlarge)*

I'm not 100% sure because I was never able to pinpoint exactly which of the capacitors
started leaking, but it's fair to assume that this fluid was capacitor electrolyte. I decided
to remove all electrolytic capacitors with new ones. There are 11 of them, listed in the
table below:

**I used these components for my TDS220 recapping, but there is absolutely no guarantee
that these are the right components. You need to double check everything yourself! Recapping
the scope is done at your own risk!**

| **#** | **Indicator** | **Capacitance** | **Voltage** | **Location**          |
|-------|---------------|-----------------|-------------|-----------------------|
| 1a    | C3            | 47 uF           | 450V        | Largest on the PCB    |
| 1b    | C3            | 68 uF           | 450V        | Largest on the PCB    |
| 2     | C13           | 2200 uF         | 6.3V        | Next to connector CN2 |
| 3     | C12           | 2200 uF         | 6.3V        | Next to C13           |
| 4     | C11           | 2200 uF         | 6.3V        | Next to C12           |
| 5     | C14           | 1000 uF         | 6.3V        | Next to C11           |
| 6     | C15           | 470 uF          | 6.3V        | Between C13 and C12   |
| 7     | C21           | 47 uF           | 16V         | Close to "AULT KOREA" |
| 8     | C18           | 22 uF           | 35V         | Next to CN2           |
| 9     | C6            | 22 uF           | 35V         | Next to IC1           |
| 10    | C17           | 4.7 uF          | 50V         | Next to C16           |
| 11    | C10           | 2.2 uF          | 50 V        | Next to CN2           |

Pay attention to 1a and 1b: some TDS220 power supplies have a 47 uF, other have a 68 uF capacitor.
Mine had a 47 uF one. You don't need to both of them.

I created [this Digikey list](https://www.digikey.com/en/mylists/list/NISC68K89D) with
all these capacitors. At the time of writing this, the cost was $8.31, tax and shipping 
not included.

![PCB glue-like substance](/assets/tds220/pcb_glue.jpg)

On my unit, all capacitors were fixed to the PCB with a soft, glue-like substance.
Use an Exacto knife to cut it loose before desoldering a capacitor.


# Recapping

* Opening up [Youtube video](https://www.youtube.com/watch?v=PHB2XC_l7Eg)
* Remove back. Insert screwdriver as shown in picture
* Remove 2 connectors
* Remove PCB by pulling back 2 tabs

Capacitor list:

* 1x 47 uF - 450 V              
    * C22 - largest cap

    * old 43uF / 0.92 Ohm
    * new 44uF / 0.11 Ohm

* 3x 2200 uF - 6.3 V
    * C13 - next to connector CN2
    * C12 - next to C13
    * C11 - next to C12


    * old 1800 uF 0.0 Ohm (120 Hz)
    * old 1883 uF 0.0 Ohm (120 Hz)
    * old 1753 uF 0.0 Ohm (120 Hz)
    

* 1x 1000 uF - 6.3 V
    * C14 - next to C11

    * old 843 u/f 0.2 Ohm (120 Hz)


* 1x 470 uF - 6.3V
    * C15 - next to IC3

    * old 415 uF 0.4 Ohm (120 Hz)
    * new 440 uF 0.2 Ohm (120 Hz)


* 1x 47 uF - 16 V
    * C21 - next to AULT KOREA

    * old 45uF 2.2 Ohm (120 Hz)

* 2x 22 uF - 35 V
    * C18 - next to connecter CN2
    * C6 - next to IC1 

    * old 19 uF 10 Ohm (120 Hz)
    * old 20 uF 7 Ohm (120 Hz)

* 1x 4.7 uF - 50 V
    * C17 - next to C16

    * old 4.7 uF 6.4 Ohm (120 Hz)

* 1x 2.2 uF - 50 V
    * C10 - next to CN2

    * 2.2 uF 15 Ohm (120 Hz)


* Can't update the firmware without a programmer: https://www.eevblog.com/forum/testgear/reverse-engineering-tds2cmtds2mm/msg4396288/#msg4396288

# References

* [Tony Albus - Tektronix TDS220 Backlight Replace and Restore](https://www.youtube.com/watch?v=weUSGjzEoVM)

* [Max's Garage - Repairing Two Digital Oscilloscopes from the 90s! Tektronix TDS210 and TDS220 Restoration](https://www.youtube.com/watch?v=YF-kBXBnxzw)

* [Tektronix TDS200 CCFL to LED backlight replacement](http://hxc2001.free.fr/tektronix_tds220/index.html)

* [EEVblog forum - Recap list](https://www.eevblog.com/forum/testgear/tektronix-tds210-teardown-and-bnc-replacement/msg1722653/#msg1722653)

* Scope with same probe compensation issue:
  https://www.eevblog.com/forum/repair/tektronix-tds-2002b-repair/msg5170455/#msg5170455

  Looks like a bad BNC connector.

