---
layout: post
title: A Badge from Idea to Production in 4 Hours
date:  2019-12-28 00:00:00 -0700
categories:
---

# Using PCB Technology for Mechanical Projects

As a high school kid, I always wanted to create PCBs for me electronics creations. Back then,
there was really only one option: a very messy process of UV lights, transparent film, ugly
chemicals, and a high chance of failure.

30 years later, anybody can spin a design in just a few hours. I did just that about year ago,
when I thought up a design for an I2C controlled joystick interface, entered the schematic and routed
the PCB in KiCad, and sent it out for production over the course of just one evening. 

3 weeks later, I found 10 shiny new JLCPCB boards at the doorstep. Total cost, including shipping: $7.
We live in amazing times.

This go me thinking: if it's that cheap to produce a physical object that's made of a pretty sturdy
material, you could use for pretty much anything, even if it's not related to electronics. Your
home laser cutter or 3D printer, if you happen to have one, satisfy most of your mechanical needs, but
the affordable ones won't come close to the mechanical precision that can be achieve in a mass
production environment. A PCB can't be used for all mechanical needs, it only applies when you need
something flat, but that might still cover cases such as [linkage designs](https://en.wikipedia.org/wiki/Linkage_(mechanical)).

However, rather than going for something ambitious right from the start, I first wanted to just get
a flow going from some non-KiCad design program to finished PCBs.

Since I'll be giving a talk at !!Con (Bang Bang Con) West in two months, I thought it'd be neat to
design a badge that's produced as a PCB. This is the kind of elaborate badget with fancy electronics
that you can find at Defcon or the Hackaday Superconference. In fact, there are no electronics involved
at all. It's just a proof of concept of using a PCB production process as mean to create something
physical.

Nothing here is original: plenty of others have done the same thing. But by writing things down, I
won't forget what I did later. If other derive some benefit from it, so much better!

Since the target audience (myself) are PCB design beginners, I will sometimes go into low level
detail, explaining things that could be too obvious for others.

# Badge Design

I couldn't design anything if my life depended on it, so I decided to simply take the !!Con West
mascot and convert it to a badge. One of my goals was to see if there'd be any road blocks in terms 
of mechanical complexity. The !!Con Octopus with all its tentacle is really perfect for that.

The starting point was a screenshot of the [!!Con West homepage](http://bangbangcon.com/west/):

![!!Con West Mascot](./assets/bangbangbadge/logo_screentshot.png)

For the badge, I decided to drop the exclamation marks, and add a rectangle at the bottom for name
and other information.

# Conversion from Bitmap to Vector

The screenshot is a bitmap, but we'll need this in vector form.

I'd heard good things about [Inkscape](https://inkscape.org), a free vector design program like Adobe
Illustrator that works on all popular platforms. I downloaded [version 0.92.2](https://inkscape.org/release/inkscape-0.92.2/)
which was the latest version with prebuilt binaries for OSX. (OSX will also need to install XQuartz separately.)

After installation, I did the following to go from bitmap to vector:

* Import the bitmap into Inkscape: File -> Import -> logo_screenshot.png

![Logo Bitmap Imported](./assets/bangbangbadge/logo_imported.png)

* Convert to Bitmap

    * Select bitmap
    * Convert to Vector: Path -> Trace Bitmap

    The key parameters in the dialog box that follows are "Colors" and "Scans: 4".
    The latter make the business in the green background disappear into one solid.

    You can use "Live Preview" to immediately see the effect of changing the parameters.

![Trace Bitmap](./assets/bangbangbadge/trace_bitmap.png)


    * After clicking OK, my bitmap was now converted into a glorious vector image.

Since I selected 4 scans (one for each base color), the bitmap has been converted
into 4 vector paths. If you select individual colored section around, you can see that
Inkscape vector conversion works in some kind of additive way: the bottom path
(yellow) contains everything, the path above that (green) contains everything except
the yellow part, the orange path everything except green and yellow, and, finally, the 
brown-ish path only contains the brown part.

![Logo split into 4 layers](./assets/bangbangbadge/logo_four_layers.png)

*Note: there was really no reason to move these individual layers around, other than to show
how the bitmap conversion worked!*

# Removing the Background from the Logo

I was not interested in the green and yellow background, so those went first.
After deleting those 2, the original bitmap showed up. That one had to go as well.

![Logo with Background Removed](./assets/bangbangbadge/logo_background_removed.png)

The next steps will involve quite a bit of path manipulations, so now is a good a time
to save [the intermediate result](./assets/bangbangbadge/logo_0.svg).

# Inkscape SVG2Shenzhen Extension

PCB badge creation is so popular that there is a custom Inkscape extension that does
a lot of the work for you: [svg2shenzen](https://github.com/badgeek/svg2shenzhen).

It will do the following for you:

* Set up an Inkscape document with all the default KiCad layers.
* Convert your Inkscape design to a KiCad project 

Once converted to a KiCad project, if everything looks good after review, 

The installation couldn't be simpler and is described on the tool's page: just download
the thing and unzip the archive in the right directory.



