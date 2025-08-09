---
layout: post
title: Simple Repair of an SR620 Universal Time Interval Counter
date:   2025-07-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

A little over a year ago, I was found 
[an Stanford Research Systems SR620 frequency counter](https://tomverbeure.github.io/2024/07/14/Symmetricom-S200-NTP-Server-Setup.html#introduction)
at the 
[Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com). 
It had a big sticker "Passed Self-Test" 
and "Tested 3/9/24" (the day before the flea market) on it so I took the gamble and spent
an ungodly $400 on it.

[![Flea Market Haul](/assets/s200/fleamarket_haul.jpg)](/assets/s200/fleamarket_haul.jpg)

Luckily, it *did* work fine, initially at least, but I soon discovered that it sometimes
got into some weird behavior after pressing the power-on switch. 

# The SR620

The SR620 was designed sometime in the mid-1980s. Mine has a rev C PCB with a date of July 1988,
37 year old! The manual lists 1989, 2006, 2019 and 2025 revisions. I don't know if there were any
major changes along the way, but I doubt it. It's still for sale on the 
[SRS website](https://www.thinksrs.com/products/sr620.html), starting at $5150.

The specifications are still pretty decent, especially for a hobbyist: 

* 25 ps single shot time resolution
* 1.3 GHz frequency range
* 11-digit resolution over a 1 s measurement interval

The SR620 is not perfect, one notable issue is its thermal design. It simply doesn't have enough
ventilation holes, the heat-generating power regulators are located close to the high precision
time-to-analog converters, and the temperature sensor for the fan is inexplicably placed right
next to the fan, which is not close at all to the power regulators. The Signal Path has 
[an SR620 repair video](https://youtu.be/sDecJDgStcI?t=416) that talks about this.

# Repairing the SR620

You can see the power-on behavior in the video below:

<iframe width="680" height="480" src="https://www.youtube.com/embed/pgqye6YGhBY?si=J_VlCNSirvTlY0vj" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Of note is that lightly touching the power button changes the behavior and sometimes makes it get
all the way through the power-on sequence. This made me hopeful that the switch itself was bad,
something that should be easy to fix.

Unlike my broken SRS DG535, another flea market buy, which has the most cursed assembly, the SR620
s a dream to work on: after removing the 4 side screws, you can remove the top of the case and
have access to all the components from the top. To get access to the solder side of the PCB,  
just remove another 4 screws to remove the bottom panel: you can desolder components without the 
need to remove the main PCB out of the enclosure.

The switch is located at the right of the front panel. It has 2 black and 2 red wires. When
the unit is powered on, the 2 black wires and the 2 red wires are connected to each other.

![Switch with wires](/assets/sr620/switch_with_wires.jpg)

To make sure that the switch itself was the problem, I soldered the wires together to make a
permanently connection:

![Wires soldered together](/assets/sr620/wires_soldered_together.jpg)

After this, the SR620 worked totall fine! All that's left now is replacing the switch.

Unscrewing 4 more screws and pull the knobs of the 3 potentiometer and
power switch to get rid of the front panel:

![Front panel removed](/assets/sr620/front_panel_removed.jpg)

A handful of additional screws to remove the front PCB from the chassis, and you have access to the
switch:

![Power switch exposed](/assets/sr620/power_switch_exposed.jpg)

The switch is an ITT Schadow NE15 T70. Unsurprisingly, there are not produced anymore, but
you can still find them on eBay. I paid $7.5 + shipping, the price increased to $9.5 immediately
after that.

![Old and new switch](/assets/sr620/old_and_new_switch.jpg)

The old switch (bottom) has 6 contact points vs only 4 of the new one (top), but that wasn't an
issue since only 4 were used. Both switches also have a metal screw plate, but they were oriented
differently. However, you can easily reconfigure the screw plate by straightening 4 metal prongs.

![SR620 powered up without front panel cover](/assets/sr620/sr620_without_front_cover_powered_up.jpg)

You need to bend the contact points a bit to get the switch through the narrow hole. After soldering
the wires back in place, the SR620 powered on reliably. 

# Replacing the Backup 3V Lithium Battery

The SR620 uses a non-recharchable 3V Panasonic BR-2/3A lithium battery to retain calibration and
settings data in SRAM. You can find this battery in many old pieces of test equipment, I already
[replaced one such battery in my HP 3478A multimeter](/2022/12/02/HP3478A-Multimeter-Calibration-Data-Backup-and-Battery-Replacement.html#replacement-3v-battery).
These batteries last almost forever, but mine had a 1987 date code and 38 years is really pushing things,
so I replaced it with [this new one from Digikey](https://www.digikey.com/en/products/detail/panasonic-energy/BR-2-3AE2SP/64350).

Old version of this battery had 1 pin on each side. The new ones have a side with 2 pins, so you need
to cut one of those pins and install the battery slightly crooked back onto the PCB.

![Replacement battery installed](/assets/sr620/battery_replacement.jpg)

When you first power up the SR620 after replacing the battery, you might get a "Test Error 3". 
According to the manual:

> Test error 3 is usually "self-healing". The instrument settings will be returned to their 
> default values and factory calibration data will be recalled from ROM. Test Error 3 will 
> recur if the Lithium battery or RAM is defective.

After power cycling the device again, the test error was gone and everything worked, but with
a precision that was slightly lower than before: before the battery replacement, when feeding the 
10 MHz output reference clock into channel A and measuring frequency with a 1s gate time, I'd get a 
read-out of 10,000,000.000*N* MHz. In other words: around a milli-Hz accuracy. After the replacment, 
the accuracy was about an order of magnitude worse. That's just not acceptable!

This is because the auto-calibration parameters were lost. Luckily, this is easy to fix.

# Switching to an External Reference Clock

My SR620 has the cheap TCXO option which gives frequency measurement results that are about
one order of magnitude less accurate than using an external OCXO based reference clock. So
I always switch to an external reference clock. The SR620 doesn't do that automatically, 
you need to manually change that in the settings which goes as follows:

* SET -> "*ctrl* cal out scn"
* SEL -> "ctrl *cal* out scn"
* SET -> "auto cal"
* SET -> "cloc source int"
* Down arrow -> "clock source rear"
* SET -> "clock fr 10000000"
* SET

If you have a 5 MHz reference clock, use the down or up arrow to switch between 1000000
and 5000000.

# Running Auto-Calibration

You can rerun auto-calibration manually from the front panel without opening up the device
with this sequence:

* SET -> "*ctrl* cal out scn"
* SEL -> "ctrl *cal* out scn"
* SET -> "auto cal"
* START

The auto-calibration will take around 2 minutes. Make sure you do it once the device has been running
for a while to make use it has warmed up. The manual recommends 30 minutes.

After doing auto-calibration, feeding back the reference clock into channel A and measuring
frequency with a 1 s gate time gave me a result that oscillated around 10 MHz.

# Fine Tuning the Frequency Measurement



# References

* [The Signal Path - TNP #41 - Stanford Research SR620 Universal Time Interval Counter Teardown, Repair & Experiments](https://www.youtube.com/watch?v=sDecJDgStcI)
* [Some calibration info about the SR620](https://www.prc68.com/I/TandFTE.shtml#SR620)
* [Fast High Precision Set-up of SR 620 Counter](https://www.prc68.com/I/FTS4060.shtml#SR620Fast)

  The rest of this page has a bunch of other interesting SR620 related comments.

**Time-Nuts topics**

* [SR620 calibration](https://www.febo.com/pipermail/time-nuts/2011-February/054929.html)

  Discusses last digital of SR620 being off. Detailed procedure is listed 
  [here](https://febo.com/pipermail/time-nuts_lists.febo.com/2011-February/037194.html).

* [Anyone familiar with SR-620 repair?](https://febo.com/pipermail/time-nuts_lists.febo.com/2012-March/047729.html)
* [Convert Stanford Research SR620 time-interval counter to SR625 ???](https://febo.com/pipermail/time-nuts_lists.febo.com/2014-November/071361.html)
* [time interval measurement on SR620](https://febo.com/pipermail/time-nuts_lists.febo.com/2022-March/105214.html)
* [SR620 binary dump](https://www.febo.com/pipermail/time-nuts/2014-March/083445.html)
* [SRS SR620 External Source Issue -- Help Request](https://www.febo.com/pipermail/time-nuts/2007-February/024397.html)

  Discussion about measured frequency not being exactly 10 MHz when ref is fed into input.

  This [reply](https://www.febo.com/pipermail/time-nuts/2007-February/024413.html) mentions the use of 2
  synchronzing ECL FFs that will still introduce some mismatch.

  [Potential solution](https://www.febo.com/pipermail/time-nuts/2007-February/024458.html) to fix the 
  average input issue. [This post](https://www.febo.com/pipermail/time-nuts/2007-February/024431.html) also
  talks about that.

* [Considerations When Using The SR620](https://www.febo.com/pipermail/time-nuts/2012-December/072294.html)

  [This post](https://www.febo.com/pipermail/time-nuts/2012-December/072305.html) talks about some thermal
  design mistakes in the SR620. E.g. the linear regulators and heat sink are placed right next to the
  the TCXO. It also talks about the location of the thermistor inside the fan path, resulting in unstable
  behavior. This is something Shrirar of The Signal Path fixed by moving the thermistor.

  [This comment](https://www.febo.com/pipermail/time-nuts/2012-December/072302.html) mentions that while the
  TXCO stays powered on in standby, the DAC that sets the control voltage does not, which results in an additional
  settling time after powering up. General recommendation is to use an external 10 MHz clock reference.

  [This comments](https://www.febo.com/pipermail/time-nuts/2012-December/072369.html) talks about warm-up
  time needed depending on the desired accuracy. It also has some graphs.

* [buying a time interval counter](https://www.febo.com/pipermail/time-nuts/2016-June/098747.html)

  [Some comments](https://www.febo.com/pipermail/time-nuts/2016-June/098757.html) with links about
  how to make 1E12 measurements in a second that are linked earlier.

* [SR620 - any gotchas buying a used one?](https://febo.com/pipermail/time-nuts/2014-November/088659.html)

* [ocxo](https://febo.com/pipermail/time-nuts/2014-November/088661.html)

   Discusses OCXOs related to SR620

* [Help me make some sense of adev measurements of SR620's own clock](https://febo.com/pipermail/time-nuts/2015-January/090649.html)

* [Can one update firmware of Stanford Research Systems SR620 time interval counter?](https://febo.com/pipermail/time-nuts/2015-January/090276.html)

  Version 1.48 is the latest version.

* [Replacement fan in SR620](https://www.febo.com/pipermail/time-nuts/2014-February/082536.html)

  [This post](https://www.febo.com/pipermail/time-nuts/2014-February/082542.html) discusses moving
  the thermistor. While it improves startup behavior, it doesn't change the fact that the fan almost
  always runs at full speed, so it's largely cosmetic.

  General conclusion: there's not much to be done: not enough gaps for airflow. Heatsinks outside
  the case where the linear power regulators are might help a bit.

* [What is maximum digits that can SR620 display?](https://febo.com/pipermail/time-nuts_lists.febo.com/2015-July/075399.html)

* [Timelab, two SR620s and losing samples](https://febo.com/pipermail/time-nuts/2016-January/095462.html)

* [Stanford Research SR620 Measurement Bias](https://febo.com/pipermail/time-nuts_lists.febo.com/2009-October/023459.html)

  Continuation of some other thread where they discuss the bias.

* [SR620 TCXO calibration](https://www.febo.com/pipermail/time-nuts/2017-June/105976.html)

* [SR620 Failure Code.](https://febo.com/pipermail/time-nuts/2016-December/102786.html)

  Info about common test error 34.

* [SR620/PM66xx/CNT-90 input stages](https://www.febo.com/pipermail/time-nuts/2017-June/106000.html)

* [Frequency Counter Choice](https://febo.com/pipermail/time-nuts_lists.febo.com/2020-October/101833.html)

  [Compares different HP counters](https://febo.com/pipermail/time-nuts_lists.febo.com/2020-October/101837.html)

  [Mentions the SR620 as metrology workhorse](https://febo.com/pipermail/time-nuts_lists.febo.com/2020-October/101848.html)
  
* [SR620 fails in Self Calibration routine 07](https://febo.com/pipermail/time-nuts/2008-October/033674.html)

  Talks about the time to amplitude converter and what kind of capacitor is used.

* [Looking for good SR620 setup to compare GPS and rubidium](https://febo.com/pipermail/time-nuts_lists.febo.com/2006-September/004297.html)

  How to use the SR620 to measure the quality of output of a Rb oscillator.
  Main suggestion is to do 500 1PPS acquisitions and display MEAN and JITTER.

  Also talks about a [PTS50 distribution amplifier](https://www.ptsyst.com/PTS50-B.pdf)  
  that has a built-in clock divider to generate a 1PPS out of it.

*  [SRS SR620 counter problem](https://febo.com/pipermail/time-nuts_lists.febo.com/2010-October/033712.html)

  Test error 3: battery problem?

* [High-end GPSDO's](https://febo.com/pipermail/time-nuts_lists.febo.com/2018-August/093602.html)

  Mentions that the interpolator of an SR620 is better than one of the FS740.

* [ADEV from phase or frequency measurement](https://febo.com/pipermail/time-nuts_lists.febo.com/2014-March/065653.html)

  Uses an SR620 to measure ADEV through phase and frequency.

* [mixers for frequency measurement](https://www.febo.com/pipermail/time-nuts/2012-January/062873.html)

  Mentions SR620 high resolution mode





**Miscellaneous**

* [A Physical Sine-to-Square Converter Noise Model](https://people.mpi-inf.mpg.de/~adogan/pubs/IFCS2018_comparator_noise.pdf)

  How to convert a sine wave clock reference to a digital signal.

* [[time-nuts] Favorite counters (current production)?](https://febo.com/pipermail/time-nuts_lists.febo.com/2017-November/089966.html)

  Review of FS740 schematic.

* [Architecture, Design Aspects, and Performance of a New Cesium Beam Frequency Standard](http://leapsecond.com/corby/5071comb.pdf)

* [A NARROW BAND HIGH-RESOLUTION SYNTHESIZER USING A DIRECT DIGITAL SYNTHESIZER FOLLOWED BY REPEATED DIVIDING AND MIXING](http://www.karlquist.com/FCS95.pdf)


