---
layout: post
title: HP 8656A Signal Generator Repair - Getting Rid of the Stank
date:   2024-02-23 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

A couple of years ago, I bought my first RF signal generator: an HP 8656A. It's an excellent
deal, just $80 at the Silicon Valley Flea Market. The seller insisted that it was functional,
what could possible go wrong?

![HP 8656A](/assets/hp8656a/hp8656a.jpg)


After dragging the 40lb beast home, I could, in fact, confirm that it did work... Sort of,
because there are defintely a couple of issues with it:

1. the front 'power' button doesn't work reliably
1. the signal output power doesn't match the programmed output power level
1. last, but not least, an unbearable chemical smell wafts out of the machine
  when it's running

Surprisingly, issues 1 and 2 aren't dealbreakers for most of my use cases, which
primarily consists of connecting to other test equipment and playing with it. But the
smell is so bad that using the machine for more than a few minutes makes you feel ill with
something that feels a soar throat... for a couple of days.

In this blog post, I take the machine apart to track down the source of the smell, and
how to fix it.

# Opening Up the Top and Bottom of a 8656A

Section 8 of the [HP 8656A Operating and Service Manual](/assets/hp8656a/8656A Signal Generator Operating and Service Manual - 9018-05716.pdf)
has some instructions on how to disassemble everything, but the descriptions are
sparse, and the illustrations and photos are a bad photocopy, so I'll go through
my usual routine of going over the top in show how to take things apart.

There are 4 ways to access the internal of the 8656A: the front, the back, the top,
and the bottom.

Unlike many other HP equipment, there is no sliding sleeve around the main body of the
the machine, instead there are separate top and bottom panels that are easy to remove.

First, remove 2 screws of each side: 

![HP 8656A side screws](/assets/hp8656a/hp8656a_side_screws.jpg)

These screws are holding 2 plastic side panels in place. Once removed, you can slide the
side panels towards the back.

![HP 8656A sliding side panel](/assets/hp8656a/hp8656a_sliding_side_panel.jpg)

The side panels contains notches that fit into the holes of the metal top and
bottom panels. That's really the only thing that keeps those panels in place: there
are no additional screws or anything.

![HP 8656A side panel removed](/assets/hp8656a/hp8656a_side_panel_removed.jpg)

You can now lift or slide of the panels:

![HP 8656A side panel removed](/assets/hp8656a/hp8656a_remove_panel.jpg)

The service manuals recommends putting the signal generator on its side if you want to work
on the top or the bottom, so that's what I did.

To fix the smell, you only need to remove the panel, but I didn't know that at the time.
Here's what it looks like when the top panel is removed:

![HP 8656A top inside view](/assets/hp8656a/hp8656a_top_view.jpg)

And here's the bottom inside view:

![HP 8656A bottom inside view](/assets/hp8656a/hp8656a_bottom_view.jpg)

It's easier to see on the top view, but the top and the bottom PCBs are mounted on a metal 
frame that can rotate out. This makes it really easy to perform service work on those PCBs 
without having to remove them from the chassis. 

Before you can rotate out the PCBs, you need to remove a bunch of nuts that keep fasten
the PCBs to the frame below it.

There are 11 nuts for the bottom part, though it took me a while to figure out that there were
more than 10: the bottom-right nut was hiding behind a flat cable:

![HP 8656A bottom nuts](/assets/hp8656a/hp8656a_bottom_nuts.jpg)

I had to remove the flat-cable IC plug-in connector (marked with the green arrow) to
be able to push the flat cable away from the hiding nut.

![HP 8656A hiding nut](/assets/hp8656a/hp8656a_hiding_nut.jpg)

Once all the nuts are removed, the whole bottom PCB assembly can be rotated open:

![HP 8656A bottom PCB rotated open](/assets/hp8656a/hp8656a_bottom_rotated.jpg)

Even when rotated open, the PCB assembly can conveniently be locked in place:

![HP 8656A bottom PCB rotated open](/assets/hp8656a/hp8656a_bottom_locked_in_place.jpg)

Just push the sping-loaded metal bar a bit to the inside and rotate the assembly
further into the notch.

# A Wild Goose Chase for the Source of the Smell

In one of my [HP 3478A repair blog posts](/2022/12/02/HP3478A-Multimeter-Calibration-Data-Backup-and-Battery-Replacement.html),
I replace the RIFA capacitors that are part of the input filter of the power supply
circuit.

Old RIFA capacitors are notorious for their guaranteed tendency to develop crack, creating
a potential fire hazard even when equipment is switched off (the caps are usually in the
input filter before that sits before the power switch), and their smell when they fail.

In the HP 8656A, the RIFA capacitors are, allegedly, located inside the black line
power module that contains the power plug receptacle, the fuse and the voltage selection card:

![HP 8656A backside power panel](/assets/hp8656a/hp8656a_backside_power_panel.jpg)

The [schematic](/2024/02/22/HP-8656A-Schematics.html) doesn't show any input capacitors
inside the power module, a Comcron F2058 with HP identifier 0960-0443:

![HP 8656A input power schematic](/assets/hp8656a/hp8656a_input_power_schematic.jpg)

But they are drawn on the component itself:

![Comcron F2058](/assets/hp8656a/Comcron F2058.jpg)



# Remainder


You need to finess it gently to put it just in the right position and then
never touch it again. After that, I switched the thing on and off by unplugging
the power cord.

Note the quotes when I write 'power' button. That's because it's more like a button
to switch the machine in active or stand-by mode. There is no button to truly switch
it off: the fan, LOUD!, always keeps spinning, for example.

One reason to keep some of the internals powered on at all time is to keep the
internal reference oscillator stable at the same temperature and thus avoid long
stabilization times when switching the machine to active mode.


