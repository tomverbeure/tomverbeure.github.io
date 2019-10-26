---
layout: post
title:  "eeColor Color3: HDMI TX is Up!"
date:   2018-04-15 00:00:00 -0700
categories: 
---


Huge progress: I now have a design that sends a test image over HDMI to a monitor, which then correctly decodes the image!

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/264892349" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

The image in the video is only 640x480@60Hz (scaled up by the monitor.)

A number of things had to come together for this:

* the connections between the FPGA and the SiI9136 (obviously)
* a Nios2 design on the FPGA that bit-bangs I2C codes to the SiL9136 
* programming the right registers on the SiL9136 to configure it into sending out the image correctly
* a test image generator

Though there were no real head-scratching road blocks, it took a while for everything to work. Especially the I2C configuration part. 

Once I had the 9136 talking back to me, it was smooth sailing. I'm programming out with the same values that are programmed by the 
example design in the Terasic HDMI FMC board. That mostly configures up format transformation settings, but no resolution or video 
timings: the 9136 derives those from the input signal.

I'm *assuming* that I'm using single clock mode (as opposed to DDR or double clocking). The output clock sent to the device is simply 
the internal clock that I use to generate the test image. There is no control over setup or hold on the IOs. Once I upgrade to faster 
timings (right now, the pixel clock is only 25MHz), that may require some extra attention.

Next step: the HDMI receiver? Since there is no simply example design, that will require a lot more work, reading the Linux driver code 
for the SiI9233 etc.

