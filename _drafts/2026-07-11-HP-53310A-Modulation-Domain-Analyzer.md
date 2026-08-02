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

# Recap list Digikey

# NVRAM

* No need to do a backup.Everything can be restored by running calibration.
* Mine has a [M48Z18-100PC1](https://www.digikey.com/en/products/detail/stmicroelectronics/M48Z18-100PC1/606300).
  * 64 kbit
  * [Replace the battery](https://www.eevblog.com/forum/repair/hp54645d-mso-non-volatile-memory-fix(st-m48z18-100pc1)/)
  * [Reviving An ST M48Z35 Battery Backed RAM Chip](https://www.mattmillman.com/reviving-an-st-m48z35-battery-backed-ram-chip/)
    * Uses a Keystone 1061 battery holder
  * [HP54616C mit M48Z18-100 NVRAM und fortschreitender Demenz](https://www.wolfgangrobel.de/electronics/nvram.htm)
    * Shows solder points if you remove the battery enclosure entirely
  * [Replace with FRAM adapter](https://www.pcbway.com/project/shareproject/Dallas_DS1225Y_FRAM_Adapter_3c961bed.html)
  * [DS1225AD-85 from UTsource](https://www.utsource.net/itm/p/12035595.html)
    * Much cheaper...
    


# References

**eevblog forum**

* [53310A Sanity check](https://www.eevblog.com/forum/testgear/53310a-sanity-check/)

* [HP 53310A Modulation Domain Analyzer - frequency microscope](https://www.eevblog.com/forum/testgear/hp-53310a-modulation-domain-analyzer-79866/?all)
* [HP 53310A - Power supply troubles](https://www.eevblog.com/forum/repair/hp-53310a-power-supply-troubles/?all)

  * [Photos, Excel list with caps](https://www.eevblog.com/forum/repair/hp-53310a-power-supply-troubles/msg2365593/#msg2365593)

* [HP53310A and other counter Allan deviation](https://www.eevblog.com/forum/metrology/hp53310a-and-other-counter-allan-deviation)

* [Using HP 53305A Phase Analyzer Software on modern windows](https://www.eevblog.com/forum/metrology/using-hp-53305a-phase-analyzer-software-on-modern-windows/)

**Various**

* [HP Bench Brief - Calibration of Time Base Oscillators](https://hparchive.com/Bench_Briefs/HP-Bench-Briefs-1994-04-06.pdf)
* [Youtube - HP 53310A MDA 10MHz ref adjust](https://www.youtube.com/watch?v=ly6b49ZyaRg)
* [Youtube - Modulation Domain Analyzer - what's that for?](https://www.youtube.com/watch?v=lBLEfVUVGyU)

* [Basic GPS clock analysis with an HP-53310A modulation domain analyzer](https://damien.douxchamps.net/elec/equipment/hp53310a/gps_clock_analysis/)
* [Always-on 10MHz reference mod for the HP53310A](https://damien.douxchamps.net/elec/equipment/hp53310a/always_on_10MHz_output/)

* [HP 53310A MDA firmware upgrade? NVRAM swap?](https://groups.io/g/HP-Agilent-Keysight-equipment/topic/hp_53310a_mda_firmware/95107760)

  Replacing NVRAM with DS1225AD-150+.

* [groups.io - HP 53310A - Why did I not know about this sooner?](https://groups.io/g/HP-Agilent-Keysight-equipment/topic/hp_53310a_why_did_i_not/73053187)


**Modulation Domain Analysis Software**

* [HP 53305A](/assets/hp53310a/53305A.zip)

  * Also downloadable from HP-Agilent-Keysight groups.io Files section.
  * Needs Win16 environment. See [this eevblog thread](https://www.eevblog.com/forum/metrology/using-hp-53305a-phase-analyzer-software-on-modern-windows/). 
    The thread also contains dumps of the ROM and discussed undocumented SCIP commands.

  * 3235 dump: 4 ROM dumps. See HP53310A_FW_3235_deinterleaved.bin.gz for deinterleaved version.
  * 3944 dump: 1 file but with an incorrect 1 byte offset. See HP53310A_FW_3944_deinterleaved.bin.gz for fixed version.
 
* [TVA3000 TimeView™ Datasheet](https://www.tek.com/en/datasheet/modulation-domain-analysis-software)



