---
layout: post
title: HP/Agilent E3631A Rotary Knob Repair
date:  2021-04-15 00:00:00 -1000
categories:
---

*Probably too many pictures and too much text for what's in the end a pretty straightforward 45min repair...*

* TOC
{:toc}

# Introduction

A few weeks ago, [somebody on Twitter](https://twitter.com/mightyohm/status/1373151638194561024?s=21) 
proudly posted a picture of his 'new' 
[Agilent E3631A](https://www.keysight.com/us/en/product/E3631A/80w-triple-output-power-supply-6v-5a--25v-1a.html) 
power supply. I had been looking on and off for a quality power supply for a while, but 
never gotten around to investigating which one to buy. That tweet made me look a bit more, 
and the E3631A seemed to be an excellent choice, even if a bit overqualified for my needs:

* 3 independent voltage rails: 0 to 6V (5A max), 0 to 25V (1A max), and 0 to -25V (1A max)
* all kinds of cool high precision, low noise and low ripple specifications
* GPIB and RS232 control
* "small, compact size for bench use", according to the marketing department

    Don't believe this: the thing is built like a tank and weighs the part. It
    makes quite a bit of noise too!

On eBay, the going rate for a working one is ~$430 + tax but I found one on offer
on Craigslist for $300.

![Craigslist picture](/assets/e3631a_repair/craigslist.jpg)

The seller only wanted to meet on the parking lot of a 7/11 in Milpitas with no way to check
the goods. He promised a 7-day return period but who knows how that will turn out in
practice?

Still, for the price I decided to go for it. If all goes well, this will be the last
bench power supply I'll buy.

# Rotary Knob Problem

The power supply came up just fine. Display worked, buttons worked, there was a voltage
on the power connectors, but the rotary knob worked ... only a little bit. It wasn't totally 
broken, but you had to finesse it by rotating very slowely to make it respond.

<iframe src="https://player.vimeo.com/video/537515378" width="640" height="360" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>

Turns out that this is a common issue with HP/Agilent equipment in general. It's also 
something that's easy to fix. After the upgrade adventures with my 
[TDS 420A](/2020/07/11/Option-Hacking-the-Tektronix-TDS-420A.html), I felt confident
enough to do this myself, rather than trying to get my money back on what was still
a good deal.

# Replacing the Knob
 
Traditional disclaimers:

**Make sure that you disconnect the power cord before attempting a repair like this!!!
Don't do this if you're not comfortable with the thought of getting a 110V shock!!!
If your PSU is still under warranty, expect it to be void after doing stuff like this!**

There are 2 types of rotary encoders: smooth rotating ones ("no detent") and ones
where you can feel a click when you turn it ("detent"). Some people prefer the latter, but
I decided on the smooth one to keep it the same as the original.

I bought [this rotary encoder](https://www.digikey.com/en/products/detail/bourns-inc/PEC16-4015F-N0024/3780221) 
on DigiKey for $1.20 and paid triple that for shipping.

![Rotary Encoder](/assets/e3631a_repair/rotary_encoder.png)

**Remove the knob**

Just pull a bit, it should come off easily.

![Remove the knob](/assets/e3631a_repair/0a_remove_knob.jpg)

**Remove the rotary encoder nut and washer**

![Remove the rotary encoder nut](/assets/e3631a_repair/0c_remove_nut.jpg)

**Remove back frame**

If the power supply warranty sticker wasn't broken yet, removing the back frame wil
do so!

Rather than first removing the protection rubber and then the frame, it's easier 
to remove the 4 screws and take off the combination of the rubber and the plastic frame 
as one piece.


![Remove back frame](/assets/e3631a_repair/0b_remove_back_frame.jpg)

**Remove handle and side screws**

These 4 screws fix the inner power supply cage connected to the outer metal sleeve. 

![Remove handle](/assets/e3631a_repair/1_remove_handle.jpg)

![Remove side screws](/assets/e3631a_repair/2_remove_side_screws.jpg)

**Slide off the outer sleeve**

![Slide off outer sleeve](/assets/e3631a_repair/3_slide_enclosure.jpg)

**Remove cage lock and front panel screws**

The power supply is built into a fold-open cage. 2 screws lock the top of the cage
in place.

There are also 2 screws on each side that fix the front panel to the cage.

When the screws are removed, don't try to pull away the front panel too far: there's
a cable that connects the front panel to an inner PCB.

![Remove cage lock screws](/assets/e3631a_repair/4_remove_hinge_screws.jpg)

**Open the cage**

![Open the inner cage](/assets/e3631a_repair/5_open_inner_cage.jpg)


**Unplug the front panel cable**

You'll need to wiggle with quite a bit to unplug the connector from its socket. Also
remove the cable from the plastic locking retainer. The cable needs to be completely
loose.

Pull the cable out of the hole that's next to the transformer as well.

![Disconnect cable](/assets/e3631a_repair/6_disconnect_cable.jpg)

**Fold open the front panel**

With the cable loose, you can now fold open the front panel. It will still
be connected to the main PCB with some other wires, but it's sufficient to remove
the front panel PCB.

![Fold open front panel](/assets/e3631a_repair/7_fold_open_front_panel.jpg)

**Lift PCB retaining tab and slide out PCB**

The front panel PCB is fixed to the front panel with a slide-and-click mechanism.

Removing it is very easy (as long as you didn't forget the rotary knob nut at
the start!) Just gently lift the retaining tab with a screwdrive and slide the PCB off 
the front panel.

![Lift PCB retaining tab](/assets/e3631a_repair/9_lift_retaining_tab.jpg)

**Remove cable from panel PCB**

The cable will be in the way when doing your soldering work, so just unplug that one
too.

![Panel PCB](/assets/e3631a_repair/10_panel_pcb.jpg)

**Replace the rotary encoder**

All that's left now is replacing the old rotary knob. This was easier that I thought it would be.
With a hot iron (I probably overdid it at 400C!) and some soldering wick, it took less than 10min
to remove the solder of the 5 connection points. The old knob came off very cleanly.

Adding the new one was obviously even easier.

![Soldering Joints](/assets/e3631a_repair/11_solder_joints.jpg)

You'll just have to believe that this is a photo with the old encoder replace by the new one...

![Old and new rotary encoder](/assets/e3631a_repair/12_old_meet_new.jpg)

**Check that it's working...**

I did a quick check that things worked, before closing things up in reverse order...

<iframe src="https://player.vimeo.com/video/537515619" width="640" height="360" frameborder="0" allow="autoplay; fullscreen" allowfullscreen></iframe>

Success!!!

Time spent from start to finish: 45 min.
