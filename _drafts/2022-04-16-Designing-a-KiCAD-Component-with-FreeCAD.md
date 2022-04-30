---
layout: post
title: Designing a KiCAD Component with FreeCAD and the KiCadStepUp Addon
date:  2022-04-16 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Recently, I had to design a PCB with a battery holder for 2 18650 batteries. The PCB needs to go into an
existing 3D printed object with pretty tight dimensions, so I wanted to do this the right way, withG
with not only a perfect footprint, but also a 3D model that can be used in both a FreeCAD assembly,
and a KiCAD 3D render.

FreeCAD has the KiCadStepUp addon that's designed for all your FreeCAD <-> KiCAD data exchange needs,
and while there's quite a bit information about it on the web in the form of Youtube videos, it still
took me a bit to get the hang of it. I don't make custom components that often and tend to forget the 
details about things I did earlier, so this blog post is primarily my way of making sure I don't 
forget things the next time I need to do this. Chances are that I'm doing things in some inefficient
or non-conventional way. Let me know if there are things that can be improved!

# The Battery Holder

So I needed a holder for 2 18650 batteries.  Amazon sells 
[2 of these battery holders](https://www.amazon.com/gp/product/B07VDC2QRC) for a pretty 
steep $10. I later checked out the 
[product website](http://www.blossom-ele.com/sdp/1074412/4/pd-5180803/14851101-2439217/SMT_Battery_Holder_18650X2_Cells.html) 
of the original manufacturer, which sells them for $0.8 a piece... with a minimum order of 100.

![Battery holder with overall dimensions](/assets/kicad_component/battery_holder_amazon.jpg)

Other than the overall external dimension, I wasn't able to find a datasheet with detailed dimensions, so
the calipers came out of the drawer to get accurate measurements.

![Battery holder with calipers measuring some irrelevant dimension](/assets/kicad_component/battery_holder_with_calipers.jpg)

Did you know that 18650 batteries have a diameter of 18mm and a length of 65mm? Neither did I! 
I only realized after measuring them with the calipers. Speaking battery dimensions, in the picture below, 
I'm dangerously close to a very nice spark:

![Length of battery measured with calipers that show 65.12mm](/assets/kicad_component/battery_length_with_calipers.jpg)

# Learning FreeCAD

[FreeCAD](https://www.freecadweb.org/) is probably the best open source 3D CAD program in existence.
I first tried it in 2015 as part of an attempt to create a floorplan of my house. It didn't go well,
and I soon abandonned the project. In the ensuing 6 years, I tried to pick up FreeCAD 3 more times, but
each time things ended in failure. The main reasons are a general inexperience with anything that's
mechanical CAD related (all my efforts to learn Blender 3D have similarly ended in failure) and a
learning curve that's IMO very, very steep.

Last December, I decided to try again once more, this time with more success. Compared to a couple
of years ago, there are now a lot more tutorials available, primarily on YouTube. I don't particularly
like learning things by watching videos, they are often long winded and it can be hard to find the part 
that explains your problem, but watching FreeCAD videos hours on end didn't only teach me specific techniques,
it also gave me a general feel of how one can go about designing a physical component in general.

I still struggle heavily with and waste hours trying to get past non-intuitive procedures, weird behavior, 
and bug, but when I really get stuck, I use the Help section of the [FreeCAD forums](https://forum.freecadweb.org/index.php). 
It doesn't matter how trivial the question, there's almost a guarantee that somebody will give a helpful answer
in minutes, often with a YouTube video or design file showing you exactly how to do it.

Without the forums, I'd have dropped FreeCAD for a commercial alternative long time ago.

# General Component Design Procedure

There are 2 major parts about modeling an KiCAD component:

* creating the 3D model 
* creating the component footprint

# FreeCAD only for the 3D Model

In many cases, you just reuse an existing footprint, or you can make a copy of an existing
one and make small modifications. I definitely prefer starting from something that already
exists, and in my cases the footprint editor of KiCAD, rudimentary as it may be, is sufficient 
to get the job done.

That's what I did for a WS2812D-F8 LED. For the footprint, I copied the footprint of an 8mm LED with
3 pin holes, deleted the pins, and copy-pasted the pins from a 5mm LED with 4 pin holes.

[8mm LED with 3 pin holes](/assets/kicad_component/led_d8_3_footprint.png)

[5mm LED with 4 pin holes](/assets/kicad_component/led_d5_4_footprint.png)

[8mm LED with 4 pin holes](/assets/kicad_component/led_d8_4_footprint.png)

Easy!

Since there were no 8mm LED models with 4 pins, I had to create that one myself in FreeCAD:

[WS2812D-f8 FreeCAD model](/assets/kicad_component/ws2812d_f8_freecad.png)

Even for this easy model, I felt like I had to strong arm FreeCAD into giving me what I wanted
in a very inefficient way:


# Designing the 3D Model with FreeCAD

General guidelines:

* Use the correct orientation right from the start, where the Z direction indicates the 
  height of the component.

  This removes one alignment step later on, when matching a 3D model to a footprint.

* 3D model items with a different color should end up in different bodies or parts.

  It's one of the many (unfortunately) infurating parts of FreeCAD. You can select
  items of a model, assign it a color, but in the end it will assign that color
  to everything instead of just the part you selected.

  I asked the forum about this, but the solutions offered are all work-arounds that
  don't really address the core issue.


