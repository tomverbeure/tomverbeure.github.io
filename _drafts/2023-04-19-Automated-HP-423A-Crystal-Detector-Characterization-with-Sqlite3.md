---
layout: post
title: Automated HP 423A Crystal Detector Characterization with GPIB and Sqlite3
date:   2023-04-19 00:00:00 -0700
categories:
---

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    jax: ["input/TeX", "output/HTML-CSS"],
    tex2jax: {
      inlineMath: [ ['$', '$'], ["\\(", "\\)"] ],
      displayMath: [ ['$$', '$$'], ["\\[", "\\]"] ],
      processEscapes: true,
      skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
    //,
    //displayAlign: "left",
    //displayIndent: "2em"
  });
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_HTML" type="text/javascript"></script>

* TOC
{:toc}

# Introduction

I picked up some random RF gizmos at the [Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com/).
It's part of the grand plan to elevate my RF knowledge from near zero to beginner level: buy
stuff, read about it, play with it, hope to learn useful things. I've found the
playing part to be a crucial step of the whole process. Things seem to stick much
better in my brain when all is said and done.[^1] 

[^1]: Writing blog posts about it is equally helpful too!

In this blog post, I'm taking a closer look at this contraption:

![HP 423A](/assets/hp423a/hp423a.jpg)

It's an HP 423A crystal detector. According to the
[operating and service manual](/assets/hp423a/HP_423A,8470A_Operating_&_Service.pdf):

> \[the 423A crystal detector\] is a 50&#937; device designed for measurement use in coaxial systems. The 
> instrument converts RF power levels applied to the 50&#937; input connector into proportional values
> of DC voltage. ... The frequency range of the 423A is 10MHz to 12.4GHz.

In my introduction of previous blog post, I wrote about John, my local RF equipment dealer. 
A while ago, he sold me a bargain Wiltron SG-1206/U programmable sweep generator that can send 
out a signal from 10MHz all the way to 20GHz at power levels between -115dBm to 15dBm. I hadn't
found a good use for it, so now was a good time to give it a little workout.

# What is a Crystal Detector?

According to [Wikipedia](https://en.wikipedia.org/wiki/Crystal_detector), a crystal detector is an 
obsolete electronic component used in some early 20th century radio receivers that consists of a piece 
of crystalline mineral which rectifies the alternating current radio signal.

As noted in the article, those crystalline minerals were first type of semiconductor diode.

RF crystal detectors are no different.  
[This Infineon application note](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055) describes how RF microwave power detectors are built with low barrier Schottky diodes,
with the following diagram:

![RF power detector with diode](/assets/hp423a/infineon_rf_power_detector.png)

The functionality is straightforward: the diode makes only the positive side of an RF signal pass,
the capacitor gets charged up to the peak level of the signal but discharges (slowly) due
to the load resistor. The output voltage of the detector is nothing but the envelope of the RF signal.

![Amplitude modulation detection](/assets/hp423a/Amplitude_modulation_detection.png)

One could use an RF crystal detector to build an AM receiver.

# The HP 423A Crystal Detector

Born in 1976, the [Keysight product page](https://www.keysight.com/us/en/product/423A/coaxial-crystal-detector.html)
predictably lists the 423A as obsolete, but it sells a [423B](https://www.keysight.com/us/en/support/423B/low-barrier-schottky-diode-detector-10-mhz-to-12-4-ghz.html).
Going through the specs, there are a couple of differences: the 423A only sustains an input power of 100mW vs 200mW for the B version.
There are are also differences in output impedance, frequency response flatness, sensitivity
levels, noise levels and so forth. For my use, the input power limits are important, because exceeding
them would damage the device, but the other values don't matter a whole lot since I
barely know what they mean to begin with. 

100mW of power is pretty high for test and measurement equipment. It corresponds to 20dBm, well
above the maximum 15dBm output of the sweep generator.

    

What's nice about the 423B is that its [datasheet](https://www.keysight.com/us/en/assets/7018-06773/data-sheets/5952-8299.pdf)
explains the basics about how they work and some of its applications.

In their words:

> These general purpose components are widely used for CW and pulsed
> power detection, leveling of sweepers, and frequency response testing of other
> microwave components. These detectors do not require a dc bias and can be
> used with common oscilloscopes, thus their simplicity of operation and excellent
> broadband performance make them useful measurement accessories.

# Reference

* [DIY Power Sensor for HP 436A and 438A](https://twitter.com/DanielTufvesson/status/1647545015764230144)

    * [Chopper And Chopper-Stabilised Amplifiers, What Are They All About Then?](https://hackaday.com/2018/02/27/chopper-and-chopper-stabilised-amplifiers-what-are-they-all-about-then/)

* [Infineon - RF and microwave power detection with Schottky diodes](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055)

* [Operator's and Unit Maintenance Manualfor SG-1206/U](https://radionerds.com/images/2/20/TM_11-6625-3231-12.PDF)


# Footnotes
