---
layout: post
title: Symmetricom SyncServer S200 Hacking
date:   2024-03-14 00:00:00 -1000
categories:
---


# Introduction


# Feature Comparison

|        | S200 | S250 | S250i |
|-------:|:----:|:----:|:-----:|
|    GPS |   X  |   X  |       |
|   1PPS |      |   X  |   X   |
| 10 MHz |      |   X  |   X   |
| IRIG-B |      |   X  |   X   |

# IMPORTANT: Using the Right GPS Antenna

GPS signals are incredibly weak, so most GPS antennas are active ones that amplify the received signal 
inside the antenna before the signal is sent over the cable to the GPS receiver. Instead of a separate cable, 
the power for this amplifier is provided by the GPS receiver through the antenna cable. 

While most GPS receivers insert a 5VDC on the cable, Symmetricom equipment has the honor of being 
one of the few vendors that powers the GPS antenna with 12VDC. Or even better: this is only
true for some of their equipment. The SyncServer S200 is one of them. 

If you look for GPS antennas on Amazon, most will be 3V to 5V rated. You can find them for 

You can easily measure this voltage level with a multimeter by connecting the 2 leads to the ground
and the center pin of the SMA or BNC cable:


![Measuring the voltage across the GPS antenna connector](/asset/s200/...)

If you connect a 5V rates GPS cable to a 12V GPS receiver, chances are that you'll damage the antenna.

There are a couple of options to connect an antenna to a 12V GPS receiver:

* Use a 12V rated antenna
* Use a 5V GPS antenna and a bias tee with DC blocker to insert a seperate 5V 
* Modify your GPS receiver to output 5V instead of 12V
* Modify your GPS antenna to support 12V


# Getting Started

* Reset to factor default settings
* Use a static IP address

    You won't be able to connect with your browser otherwise!


# References

* [Microsemi SyncServer S200 datasheet](/assets/s200/md_microsemi_s200_datasheet_vb_.pdf)
* [Microsemi SyncServer S200, S250, S250i User Guide](/assets/s200/syncserver-s2xx_997-01520-01_g2_md.pdf)
* [EEVblog - Symmetricom S200 Teardown/upgrade to S250](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250)

* [GPIO Labs](https://gpio.com/)

    Has a bunch of GNSS related products, such as this 
    [USB Bias Tee with GNSS band filter and 3.3V supply](https://gpio.com/collections/gnss/products/gnss-filtered-bias-tee-gps-l1-l5-glonass-beidou-navic-1100-1700-mhz)
    or this universal [USB Bias Tee](https://gpio.com/collections/bias-tees/products/usb-bias-tee-operates-from-10mhz-7000mhz).

* [DIY bias tee](https://discussions.flightaware.com/t/power-bias-tee-from-usb-port/66181)

* [HEOL S200 S250 S300 S350 XLi servers GPS upgrade](https://trends.directindustry.com/heol-design/project-57722-1149241.html)

* [EEVblog - Symmetricom Syncserver S350 + Furuno GT-8031 timing GPS + GPS week rollover](https://www.eevblog.com/forum/metrology/symmetricom-syncserver-s350-furuno-gt-8031-timing-gps-gps-week-rollover/)
