---
layout: post
title:  "Micro Chip R/W Clip Review"
date:   2018-04-29 00:00:00 -0700
categories: tools
---

# Introduction

I have a few projects going on that require reverse engineering the command stream between 
different chips. For example, in my eeColor Color3 project, there is no programming documentation
of the I2C registers of the Silicon Image SiI9233.

So one way or the other, I need to probe the I2C bus of this chip.

The good news is that the chip has a TQFP144 package which means that the pins are out in the open. The
not so great news is that TQFP pins are spaced 0.5mm away from each other.

My initial plan was to buy some very small probes that can connect to those pins. The second plan was to 
solder wires on the pins. 

In the end, the second plan worked out great and was completed long before I could try out the first plan,
but since the wheels of the first plan had already been put in motion (I had ordered the probes), I might
as well share my experience with those little probes.

# The High End Stuff

If you want to go the high end route, you go to [Pomona Electronics](https://www.pomonaelectronics.com/products/test-clips/grabber-test-clips) 
or [ProbeMaster.com](http://probemaster.com/smd-grippers-test-clips/) where you'll find a number of options.

A good example are these [SMD grippers](https://probemaster.com/8174-smd-gripper/).
I've used them at work. They are spec'ed to grip pins that are 0.5mm away from each other. They also
cost $17 per gripper. Ouch.

There are two cheaper options, such as another pair of SMD grippers (at $9 each) and a set of 10 (at $12 each). 

Having used similar of these grippers as well, they are clearly of lower quality than the first ones. If
you absolutely need these kind of probes (and your employer is willing to pay for them), just spend the
money. 

But for a hobbyist, they are too expensive.

Much cheaper, $5 each, are [these Pomona grabbers](https://www.adafruit.com/product/2618) on Adafruit. They seem to be
an excellent choice for SOIC packages, but are probably too big for my 0.5mm spaced TQFP144 pins.

# Micro Chip R/W Clip

So let's get over to AliExpress and see what's available.

You'd expect there to be plenty of alternatives, and you'd be wrong. I may have been using the wrong keywords to
find the right product, but the smallest grippers are for SOIC-type packages (which have a pitch of around 1.2mm.)

Until I stumbled on the *Micro Chip R/W Clip*. Surprisingly, they are marketed as a tool that allows you to 
reprogram a *car remote control key IC*. Including shipping, they go for about $15. $1.5 per probe, not bad.

# The Product 

3 weeks after ordering, the following box arrived at my door:

![Probes Package]({{ "/assets/chip_probes/package.jpg" | absolute_url }})

The package has the follow contents:

![Package Contents]({{ "/assets/chip_probes/package_contents.jpg" | absolute_url }})

The grip of the probe is surrounded by a long and a short side. The long side is the one where the clamps will come out. 
The short side can be pressed in to push the clamp out. The metal of the probe has a transparent plastic layer around it:

![Package Closeup]({{ "/assets/chip_probes/probe_closeup.jpg" | absolute_url }})

Unlike the high end grabbers, there is no easy way to push on the short end of the probe: it's too sharp to press
with your bare finger. Instead, you need to plug in the black connector and then press on the connector. However,
even if you do that, the black connector will come loose from the wire that's inside it. So you actually have to
push on the connector and the colored wire at the same time.

It's not super practical, but it works, as long as you have your two hands available: one to hold the probe, the
other to push.

# Hands On - TSOP 0.8mm

So how do they work in practice?

Here's a small example where I connect a probe to various pins of an SDRAM:

<div style="padding:56.25% 0 0 0;position:relative;"><iframe src="https://player.vimeo.com/video/267073327" style="position:absolute;top:0;left:0;width:100%;height:100%;" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe></div><script src="https://player.vimeo.com/api/player.js"></script>

The 54 pin TSOP has the pins spaced 0.8mm from each other. It's clear that probing a single pin is pretty easy.

Probing 2 adjecent pins is a bit harder but it's definitely possible as well:

![DRAM 2 Probes]({{ "/assets/chip_probes/dram_2probes.jpg" | absolute_url }})

![DRAM 2 Probes Closeup]({{ "/assets/chip_probes/dram_2probes_closeup.jpg" | absolute_url }})

But that's about the limit: the probes themselves as just too wide reach 3 closely spaced pins. 

# Hands On - TQFP 0.5mm

Finally the case that started it all: probing an I2C bus on a TQFP 144 package.

It takes a little bit of effort, but probing a single pin is very doable:

![TQFP 144 1 Probe]({{ "/assets/chip_probes/tqfp144_1probe.jpg" | absolute_url }})

But that's where it ends. If we zoom in a little bit more, we see the grabbers of the probes
marked by the orange rectangles:

![TQFP 144 1 Probe Closeup]({{ "/assets/chip_probes/tqfp144_1probe_closeup.jpg" | absolute_url }})

It isn't encouraging: the gap between the grabber and the next pin seems to be narrower than the 
width of the grabber itself.

After a lot of trial and error, I was able to squeeze a second grabber next to the first one, but
I was never able to do so without the two making contact. And since the I2C pins were right next to 
each other, there was no way to probe them at the same time with these grabbers.

# Conclusion

The probes are cheap and they are small enough to grab isolated pins on a TQFP144 package or pairs, adjacent pairs of
a TSOP. You're out of luck if you need to probe adjacent pairs on the TQFP144, which made them useless
in my case.

If you have the tools (solder iron, microscope, very thin wires), soldering probe wires is much more effective solution, with
the additional benefit that the measurement setup is far less fragile.

That said, I'm happy to have these probes in my toolbox. They'll be useful one day.

Tom
