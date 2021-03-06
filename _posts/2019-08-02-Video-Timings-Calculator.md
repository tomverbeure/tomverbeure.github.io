---
layout: post
title: Video Timings Calculator
date:   2019-08-03 00:00:00 -1000
categories:
---

A very small of my day job consists of checking if the hardware on which I work will support certain 
video modes: "Hey Tom, has your widget the necessary bandwidth to deal with 4K/100Hz?".

That's the moment where I normally bring up a spreadsheet for some back-of-the-envelope math.

When doing hobby projects, I sometimes run into the same questions: can I stream 1080p at 60Hz on
this Pano Logic G1 device that has an LPDDR DRAM? Will I be able to also stream it out over
100M Ethernet?

Spreadsheet are really great for this kind of stuff, but they become cumbersome to debug as they
grow larger. So I wrote some Javascript instead and it has taken a bit of life on its own, with
more features added as I need them. Maybe you find it useful.

So I present the [Video Timings Calculator]({{ "./video_timings_calculator" | absolute_url }})!

Operation is simple: 

* Select the resolution and refresh rate that you're interested in
* Manually adjust whatever parameter that needs to be changed
* Voila! All the data you'll ever need!

Notes:

* You can fill in your custom H-blank and V-blank numbers, but no custom front-porch,
  sync, or back-porch. That's because they don't make any difference in terms of required
  bandwidth.
* "Total BW" means: the bandwidth required if you need to transmit the active pixels *and*
  the blanking with the same amount of bits per pixel.
* "Active BW" means: the bandwidth required if you only need to transmit the active pixels, and
  you can ignore blanking, as is the case for RFC4175.
* For each video protocol and timing, the percentage number shows the amount of availabe BW
  is consumed. When it exceeds 100%, the timing can't be transferred over that particular protocol.
* The custom timings ignore interlaced or margins. That's because I was lazy and nobody
  cares about these things anymore.
* The RFC4175 assumes UDP over IP over Ethernet with an Ethernet MTU of 1500. I think I got the 
  calculation mostly right, except for rounding error here and there depending on color format.
* There may be other limitations that prevent a video timing to be transmitted over a particular
  protocol. For example, GPUs may have peak pixel clock restrictions that are lower than what
  the protocol theoretically supports.

