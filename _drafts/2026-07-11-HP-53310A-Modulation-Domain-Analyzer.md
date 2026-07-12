---
layout: post
title: HP 53310A Modulation Domain Analyzer
date:   2026-07-11 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Intro

* $20 at SV electronics flea market

# Specs

* Options:

  * 001 Expanded Memory
  * 010 Oven Time Base
  * 031 Dig RF Comm Channel C

  Not installed:
  * 030 Channel C

# Screen intensity

Knob on the back of the machine

# Measuring an oscillator

Settings: 

* Autoscale
* Measurements:
  * Mean
  * Std Dev
* Vertical/Hist Range
  * Span: 1 Hz
* Histogram:
    * Histogram (instead of Time)
    * Fast Hist
    * # of Meas: 100
    * Accumulate: On
* Sampling:
  * Interval: Manual
  * 10ms, then 500ms

The time per update is the sampling interval times the
number of measurements. So for 500ms and 100, it's 50s.

Lower the Span (Hist Range) for higher intervals to get better
accuracy. E.g. 10mHz. 
Make sure the histogram doesn't fall out of the screen. There won't be
any feedback if that happens!

With 500ms/100 measurements, I get 618 uHz std dev with my GTI reference OCXO.

Note: std dev goes dwon by 1/sqrt(N). 

* Status: shows all parameters together


Histogram with time interval instead of frequency:

* Function/Input
  * Time Int A->B
  * Common: A goes to A and B input

Smallest bin width is 75ps.

# References

**eevblog forum**

* [53310A Sanity check](https://www.eevblog.com/forum/testgear/53310a-sanity-check/)

* [HP 53310A Modulation Domain Analyzer - frequency microscope](https://www.eevblog.com/forum/testgear/hp-53310a-modulation-domain-analyzer-79866/?all)
* [HP 53310A - Power supply troubles](https://www.eevblog.com/forum/repair/hp-53310a-power-supply-troubles/?all)

  * [Photos, Excel list with caps](https://www.eevblog.com/forum/repair/hp-53310a-power-supply-troubles/msg2365593/#msg2365593)

* [HP53310A and other counter Allan deviation](https://www.eevblog.com/forum/metrology/hp53310a-and-other-counter-allan-deviation)

**Various**

* [HP Bench Brief - Calibration of Time Base Oscillators](https://hparchive.com/Bench_Briefs/HP-Bench-Briefs-1994-04-06.pdf)
* [Youtube - HP 53310A MDA 10MHz ref adjust](https://www.youtube.com/watch?v=ly6b49ZyaRg)

* [Basic GPS clock analysis with an HP-53310A modulation domain analyzer](https://damien.douxchamps.net/elec/equipment/hp53310a/gps_clock_analysis/)
* [Always-on 10MHz reference mod for the HP53310A](https://damien.douxchamps.net/elec/equipment/hp53310a/always_on_10MHz_output/)


**Modulation Domain Analysis Software**

* [HP 53305A](/assets/hp53310a/53305A.zip)

  * Also downloadable from HP-Agilent-Keysight groups.io Files section.
  * Needs Win16 environment. See [this eevblog thread](https://www.eevblog.com/forum/metrology/using-hp-53305a-phase-analyzer-software-on-modern-windows/).

* [TVA3000 TimeView™ Datasheet](https://www.tek.com/en/datasheet/modulation-domain-analysis-software)



