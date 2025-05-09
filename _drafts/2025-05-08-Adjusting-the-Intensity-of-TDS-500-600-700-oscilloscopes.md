---
layout: post
title: Adjusting the CRT Brightness and Contrast of Tektronix TDS 500/600/700 Oscilloscopes
date:   2025-05-08 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Less than a week after finishing my 
[TDS 684B analog memory blog post](/2025/05/04/TDS684B-CCD-Memory.html), a TDS 684C landed
on my lab bench with a very dim CRT.

If you follow the lives the 3-digit TDS oscilloscope series, you probably know that this is
normally a bit of death sentence of the CRT: after years of use, the cathode ray loses its
strength and there's nothing you can do about it other than replace the CRT with an LCD screen.

I was totally ready to go that route, and if I ever need to do it, here are 3 possible LCD upgrade
options that I list for later reference:

* The most common one is to buy a $350 Newscope-T1 LCD display kit by SimmConn Labs. 
* A cheaper hobbyist alternative is to hack something together with a VGA to LVDS interface board 
  and some generic LCD panel, as described in 
 [this build report](http://hakanh.com/dl/TDS7_LCD.htm). 
 He uses a VGA LCD Controller Board KYV-N2 V2 with a 7" A070SN02 LCD panel. As I write this,
 the cost is $75, but I assume this used to be a lot cheaper before tariffs were in place.
* If you really want to go hard-core, you could make your own interface board with an FPGA
  that snoops the RAMDAC digital signals and converts them to LVDS, just like the Newscope-T1.
  There is [a whole thread about this the EEVblog forum](https://www.eevblog.com/forum/testgear/tektronix-tds744-crt-to-color-converter-fpga-module-diy/).

**But this blog post is not about installing an LCD panel!**

Before going that route, you should try to increase the brightness of the CRT by turning a
potentiometer on the display board. It sounds like an obvious thing to try, but didn't a lot
of reference to online. And in my case, it just worked.

# Finding the Display Tuning Potentiometers

In the *Display Assembly Adjustment* section of chapter 5 of the *TDS 500D, TDS 600C, TDS 700D and TDS 714L 
Service Manual*, page 5-23, you'll find the instructions on how to change rotation, brightness and contrast. It
says to remove the cabinet and then turn some potentiometer, but I just couldn't find them!

They're supposed to be next to the fan. Somewhere around there:

![Left side of the TDS 684C](/assets/tds684c/tds684c_side.jpg)

Well, I couldn't see any. It's only the next day, when I was ready to take the whole thing apart
that I noticed these dust covered holes:

![4 dust covered holes](/assets/tds684c/tds684c_dust.jpg)

A few minutes and a vaccum cleaning operation later reveals 5 glorious potentiometers:

![5 potentiometer](/assets/tds684c/tds684c_no_dust.jpg)

From left to right:

* horizontal position
* rotation 
* vertical position
* brightness
* contrast

Rotate the last 2 at will and if you're lucky, your dim CRT will look brand new again. It did
for me!

# The Result

![TDS684C with bright CRT image](/assets/tds684c/tds684c_intensity_ok.jpg)

The weird colors in the picture above is a photography artifact that's caused by Tektronix
NuColor display technology: it uses a monochrome CRT with an R/G/B shutter in front of it.
You can read more about it in 
[this Hackaday article](https://hackaday.com/2019/01/17/sharpest-color-crt-display-is-monochrome-plus-a-trick/).
In real life, the image looks perfectly fine!

# Hardcopy Preview Mode

If dialing up the brightness doesn't work and you don't want to spend money on an LCD upgrade,
there is the option of switching the display to Hardcopy mode, like this:

`[Display] -> [Settings <Color>] -> [Palette] -> [Hardcopy preview]`

![Hardcopy preview mode](/assets/tds684c/tds684c_hardcopy_mode.jpg)

Instead of a black, you will now get a white background. It made the scope usable before I made
the brightness adjustment.

