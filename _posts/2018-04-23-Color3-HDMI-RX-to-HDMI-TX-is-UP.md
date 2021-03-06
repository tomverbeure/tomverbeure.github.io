---
layout: post
title:  "eeColor Color3: HDMI RX to HDMI TX is UP!!!"
date:   2018-04-23 00:00:00 -1000
categories: 
---

Let's start with a demo first:

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/266042124" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

This video shows the following:

* A Tegra Shield console sends a 720p image to its HDMI port
* The SiI9233 chip of the eeColor Color3 board receives the 720p image and decodes into parallel RGB.
* The Cyclone 4 FPGA takes in the video, overlays a moving rectangle, replaces all bright reds with a bright green and sends it to 
  the SiL9136 chip.
* The SiI9136 converts the parallel RGB video back to HDMI
* The monitor displays the final image.

This is really huge: it shows that this $20 box can be used to modify high quality video input in real time: add subtitles, green 
screen keying, special effects, etc. (It can NOT be used to mix 2 live video streams however: the SiI9233 only supports 1 active 
input at a time.)

Getting the SiI9136 to work last week was easy: I just had to copy and paste some existing example code.

The SiI9233 was a lot harder. There are some drivers out there, but I wasn't able to get an image to come out that way.

So I decided to brute force my way in: 

* I recorded [all the I2C transaction on the pins of the SiI9233](https://hackaday.io/project/122480-eecolor-color3/log/144836-sii9233-and-sii9136-i2c-traces). 
* I wrote a script to convert all those transactions into [C code](https://github.com/tomverbeure/color3/blob/master/bringup/sw/bringup/sii9233_conn.h).
* I simply replay those transaction with my own design.

It feels like cheating, but it works!

The current design is just a proof of concept and far from ideal: there is no tight control over the timings of the input and 
output flip flops (I should just the FFs inside the IO pads for that), there is no PLL to tightly control the sample points of 
the input and output FFs either.

Every minute or so, my monitor goes blanks for few seconds. 

But the hard work is done. Next up is the SDRAM controller, the flash ROM, and, eventually, patching my board with an FTDI232 
and USB connector: that way, it can truly be controlled via USB.

