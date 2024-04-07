---
layout: post
title: Installing Software Options on the HP 8753C VNA
date:   2024-04-06 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

I have an HP 8753C that I found on Craigslist. Other than a few smudges and 
scuffmarks on the handles and case, it's in near perfect shape. 

Mine is the 300kHz to 3GHz version without any additional options, but it came
with the matching HP 85046A S-parameter test set. You don't absolutely need this
test set for mark useful measurements, but if you want to easily measure S11, S21, S22 and
S12 parameters without external couplers, it's kind of a necessity.

The HP 8753C has as few additional options (see [data sheet](/assets/hp8753c/HP_8753C Datasheet.pdf)):

* option 002: harmonic analysis, also callsed HP 11883A Harmonic Measurement Upgrade
* option 006: 6GHz support, also cassed HP 11884A 6GHz Receiver Upgrade
* option 010: time domain, also called HP 85019B Time Domain Upgrade Kit)

Options 002 and 010 and pure software upgrades. And while option 006 can be enabled 
just like the software options, you need an HP 85047A (instead of 85046A) for actually use 
it: the test set contains the frequency doublers that make 6GHz possible. The 8753C 
just sends commands tot he 85047A to switch those doubles on and off.

# Getting the option codes

As described in the [Kirkby Microwave](https://www.kirkbymicrowave.co.uk/Everything-you-wanted-to-know-about-the-HP-8753-VNA/)
website, you just send an email to [caesarv@email.com](mailto:caesarv@email.com) with
the type ("HP 8753C") and the serial code of your machine.

In my case, the serial code is shown during power up, or through the service menu:

System -> Service Menu -> Firmware Revision

In my case the serial number was 10 characters. There are reports from others who aren't
so lucky. 

It felt a bit weird to ask a total stranger for license codes, but I emailed Ceasar and got 2 codes
back the next day. Amazing!

```
   Model Number: HP 8753C
   Serial Number: 3310J01311
   To add :
 
   002, Harmonic Analysis
   010, Time Domain Analysis (Std on 8702D),
    enter the keyword: 3 K 8 A C J Q E F 9 3
   Note: Spaces are for reading clarity only.
 
    
   Do not install 006 unless you have an 85047 test set since the doubler is in the test set.
   Model Number: HP 8753C
   Serial Number: 3310J01311
   To add :
   006, 6 GHz Performance,
    enter the keyword: 3 U 4 3 L F 3 0 F X P
   Note: Zeros appear as "0" with this font, the letter O appears as "O."
    
   Enjoy,
   CV
```

Installing the code was all that was left.

# Installing the codes


* HP_8753D_Vector_Network_Analyzer__Service_Manual-08753-90405.pdf
* Page 3-39: Test 56


# References

* [HP 8753C Data Sheet](/assets/hp8753c/HP_8753C Datasheet.pdf)

* [HP 8753C Network Analyzer: Serial numbers, options, EEPROMs](https://www.simonsdialogs.com/2020/02/hp-8753c-network-analyzer-serial-numbers-options-eeproms/)
* 
