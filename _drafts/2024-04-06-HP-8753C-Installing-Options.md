---
layout: post
title: Installing Software Options on the HP 8753C VNA
date:   2024-04-06 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

I have an HP 8753C vector network analyzer (VNA) that I found on Craigslist. Other 
than a few smudges and scuffmarks on the handles and case, it's in near perfect shape. 

[![HP 8753C and HP 85046A](/assets/hp8753c/hp8753c.jpg)](/assets/hp8753c/hp8753c.jpg)

Mine is the 300kHz to 3GHz version without any additional options, but it came
with the matching HP 85046A S-parameter test set. Strictly speaking, you don't need this
test set to make useful measurements, but if you want to easily measure S11, S21, S22 and
S12 parameters without external couplers, it's kind of a necessity.

The HP 8753C has as few additional options (see [data sheet](/assets/hp8753c/HP_8753C Datasheet.pdf)):

* option 002: harmonic analysis, aka HP 11883A Harmonic Measurement Upgrade
* option 006: 6GHz support, aka HP 11884A 6GHz Receiver Upgrade
* option 010: time domain, aka HP 85019B Time Domain Upgrade Kit

Options 002 and 010 and pure software upgrades. And while option 006 can be enabled 
just like the software options, you need an HP 85047A test set, instead of the 85046A, 
to use it: the test set contains the frequency doublers that make 6GHz possible. The 8753C 
just sends commands to the 85047A to switch those doublers on and off.

# Getting the option codes

HP/Agilent/Keysight has long ago discontinued the sale of these software options, but
enthousiasts were able to reverse engineers the EEPROM contents on the CPU board of the
8753C to enable them. This, however, required removing the EEPROMs from the board,
reprogramming them, and putting them back in. Not rocket science, but not entirely free 
of risk either.

There is a much better alternative! As described in the 
[Kirkby Microwave](https://www.kirkbymicrowave.co.uk/Everything-you-wanted-to-know-about-the-HP-8753-VNA/)
website, you just send an email to [caesarv@email.com](mailto:caesarv@email.com),
a retired HP employees with the tools to create license keys for these options.

All you need to do is mention the exact type of your machine, "HP 8753C", and its serial
code.

![HP 8753C serial code](/assets/hp8753c/serial_code.jpg)

The serial code is shown during power up, or you can get it  through the service menu:

System -> Service Menu -> Firmware Revision

If you serial number is less than 10 characters, you'll need to take additional steps to recover 
the full number. This wasn't an issue for my case.

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
