---
layout: post
title: WS2812B Reset Old & New
date:   2019-10-13 10:00:00 -0700
categories:
---

# Public Service Notice

There are multiple versions of the WS2812B programmable LEDs.

The [World Semi website](http://www.world-semi.com/Certifications/details-111-4.html) currently only has 
[the datasheet](http://www.world-semi.com/DownLoadFile/111) of the latest one (they call it V4). 

But you google for "WS2812B datasheet", [this one](https://cdn-shop.adafruit.com/datasheets/WS2812B.pdf) 
from Adafruit is the top ranked result. That's the old one.

The old one requires an idle time ("reset") of 50us or more. On the new one, that has been increased to 280us. That makes them
backwards incompatible...

Guess which one I had been developing for first, and what happened when I connected a different LED board?

You can distinguish old and new by the pattern inside the LED 'eye':

![WS2812B Old and New]({{ "/assets/ws2812b_reset/ws2812b_old_new.jpg" | absolute_url }})

The complete timing tables:

Old

![WS2812B Old Timings]({{ "/assets/ws2812b_reset/ws2812b_old_timings.png" | absolute_url }})


New

![WS2812B New Timings]({{ "/assets/ws2812b_reset/ws2812b_new_timings.png" | absolute_url }})

[This blog post](https://blog.particle.io/2017/05/11/heads-up-ws2812b-neopixels-are-about-to-change/) goes into
more detail about difference between the old and the new version.

