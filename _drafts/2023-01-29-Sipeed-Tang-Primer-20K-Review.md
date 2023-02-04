---
layout: post
title: Sipeed Tang Primer 20K review
date:   2023-01-29 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

# Notes

* GW2A-LV18PG256C8IC8I7 is supported by the [Gowin Education edition](https://www.gowinsemi.com/en/support/database/1865/)
* Website is a non-responsive disaster.
* Gowin_V1.9.8.09_Education_linux.tar.gz, 382MB.
* Root of the tar file is *not* Gowin...something...something

```sh
cd ~/tools
mkdir Gowin_V1.9.8.09_Education
cd Gowin_V1.9.8.09_Education
tar xfvz ~/Downloads/Gowin_V1.9.8.09_Education_linux.tar.gz
./IDE/bin/gw_ide &
```

* File -> Open Example Project -> FFT (GW2A-LV18PG256)
    * Make sure you change target directory!
* There is a button to run synthesis, but not a menu. Or double click on Synthesize in the process tab.
* Now way to run the Programmer GUI. (What about signaltap?)
* Programming: `openFPGALoader -b tangprimer20k bottom_board_test.fs`


* Need to download Release notes, which in turn contain links to PDF file with installation instructions.

* You need to set the IO type. The bank voltage will change automatically. You often can't set the bank voltage.
* Allow READY and DONE as GPIO: LEDs 
* Set all banks to +3.3V.
* Power hierarchy: dock provides +5V. module creates +3V
    * VCC0&1: 
        * Banks 0, 1: 3.3V by default through resistor R5
        * Connector F_VCC0&1: 3.3V by default through resistor R6
    * VCC7:
        * Bank 7: 3.3V by default through resistor R9
        * F_VCCO7: 3.3V by default through resistor R13
    * Banks 2,3: always 3.3V
    * Banks 4,5,6: always 1.5V
* Official JTAG dongle: different assignments as USB blaster.
* Silicone S1 to 5: mixed voltage rails
* Dipswitch SW1 -> B10/nRECONFIG of FPGA (3.3V). SW2 to 5: 1.5V. No special purpose
* LEDs 2 and 3 are swapped either on the board or on the schematic.
* Examples:
    * HDMI works
    * 

# References

* [Sipeed Tang Primer 20K Official Website](https://wiki.sipeed.com/hardware/en/tang/tang-primer-20k/primer-20k.html)
* [Design assets: PCB, schematic, ...](https://dl.sipeed.com/shareURL/TANG/Primer_20K)
