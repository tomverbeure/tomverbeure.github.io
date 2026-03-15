---
layout: post
title: Trimble GPSDO
date:   2026-03-14 00:00:00 -1000
categories:
---

* TOC
{:toc}

* $20 at electronics flea market
* Power supply: Mean Well T-30B
    * 30W
    * 5V/3A
    * 12V/1A
    * -12V/0.5A
    * $16 on eBay
* Trimble Thunderbolt GPSDO unit
    * A002206.G1 Rev E
    * FW 3.00
    * Contains OCXO
        * Double OCXO
        * Great phase noise
    * [time-nuts discussion](https://febo.com/pipermail/time-nuts_lists.febo.com/2011-August/040881.html)
    * Rev E is a newer unit with a coarse temperature sensor. Older version have a better, finer sensor chip.
    * [eevblog discussion](https://www.eevblog.com/forum/testgear/trimble-thunderbolt-gps-disciplined-oscillator/)
    * [Fixing Trimble Thunderbolt GPSDO Temperature Sensor](https://www.youtube.com/watch?v=6KPlS2XOo-A)
    * [time-nuts Trimble Thunderbolt FAQ](http://www.leapsecond.com/tbolt-faq.htm)
    * [Notes on Trimble Thunderbolt performance and modifications](http://www.ke5fx.com/tbolt.htm)
        * Upgrade to HP 10811-60111 OCXO
        * Remove original OCXO from PCB to remove noise sources from PCB.


# References
