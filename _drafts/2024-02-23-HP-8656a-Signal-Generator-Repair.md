---
layout: post
title: HP 8656A Signal Generator Repair - Getting Rid of the Stank
date:   2024-02-23 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

A couple of years ago, I bought my first RF signal generator: an HP 8656A. It was an excellent
deal, just $80 at the Silicon Valley Flea Market. The seller insisted that it was functional,
what could possible go wrong?

![HP 8656A](/assets/hp8656a/hp8656a.jpg)


After dragging the 40lb beast home, I could, in fact, confirm that it did work... Sort of,
because there are defintely two issues with it:

1. the front 'power' button doesn't work reliably
1. the fan is way too loud
1. an unbearable chemical smell wafts out of the machine when it's running

Surprisingly, issues 1 isn't a dealbreaker because it's not a real power button to begin with:
that noisy fan keeps running even when the button is set to standby, and if I finess that
button just right in the on position, I can power the machine on and off by unplugging
the power cable.

Issue 2 is definitely annoying, but survivable.

But the smell is so bad that using the machine for more than a few minutes makes you feel ill with
something that feels a soar throat... for a couple of days.

In this blog post, I take the machine apart to track down the source of the smell, and
how to fix it.

# The HP 8656A

Before getting our hands dirty, a quick word about the HP 8656A: it's a pretty terrible
product. Some call it one of the worst pieces of HP equipment ever made. An old timer at the 
electronics flea market later told me that one of the already retired HP founders let his 
displeasure know, which resulted in an 8656B that solved most of the problems.

I have no way to confirm that story, but it's saying something about the general sentiment
about it. And when I asked about the smell on the EEVblog forum, this was 
[one of the replies](https://www.eevblog.com/forum/testgear/hp-8656a-nauseating-smell/msg5323268/#msg5323268):

> Yeah, the 8656A stinks on ice....
> 
> Oh, you meant the RIFAs.  :P

Here are some of the reasons:

* the RF frequency can only be selected in selected in steps of 100Hz.
* the phase noise is pretty bad.
* there's no way to switch off the RF output. The best you can do is -127dBm.
* the buttons on the front panel are woeful.

Despite all that, it's still synthesized RF signal generator that's good enough
for many uses, especially for $80. Ironically, in my case the bad phase noise was a 
feature, because I wanted to experiment with measuring and comparing phase noise between 
a bad and a good signal generator! And it's not as if I have a real use case for an RF signal g
enerator to begin with, other than playing with them by connecting various pieces of test equipment
together. 

Here's a [sheet with the specifications](/assets/hp8656a/8656A_characteristics.pdf).

# Opening Up the Top and Bottom of a 8656A

Section 8 of the [HP 8656A Operating and Service Manual](/assets/hp8656a/8656A Signal Generator Operating and Service Manual - 9018-05716.pdf)
has some instructions on how to disassemble everything, but the descriptions are
sparse, and the illustrations and photos are a bad photocopy, so I'll go through
my usual routine of going over the top in show how to take things apart.

There are 4 ways to access the internal of the 8656A: the front, the back, the top,
and the bottom.

Unlike a lot of other HP equipment, there is no sliding sleeve around the main body of the
the machine, instead there are separate top and bottom panels that are easy to remove.

First, remove 2 screws of each side: 

![HP 8656A side screws](/assets/hp8656a/hp8656a_side_screws.jpg)

These screws are holding 2 plastic side panels in place. Once removed, you can slide the
side panels towards the back.

![HP 8656A sliding side panel](/assets/hp8656a/hp8656a_sliding_side_panel.jpg)

The side panels contain notches that fit into the holes of the metal top and
bottom panels. That and bit of friction is really the only thing that keeps those panels 
in place: there are no additional screws.

![HP 8656A side panel removed](/assets/hp8656a/hp8656a_side_panel_removed.jpg)

You can now lift or slide of the panels:

![HP 8656A side panel removed](/assets/hp8656a/hp8656a_remove_panel.jpg)

The service manual recommends putting the signal generator on its side if you want to work
on the top or the bottom, so that's what I did.

To fix the smell, you only need to remove the bottom panel, but I didn't know that at the time.
Here's how things look  when the top panel is removed:

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

I had to remove the flat cable IC plug-in connector (marked with the green arrow) before I
could push the flat cable away from the nut that was hiding underneath.

![HP 8656A hiding nut](/assets/hp8656a/hp8656a_hiding_nut.jpg)

Once all the nuts are removed, the whole bottom PCB assembly can be rotated open:

![HP 8656A bottom PCB rotated open](/assets/hp8656a/hp8656a_bottom_rotated.jpg)

When rotated open, the PCB assembly can conveniently be locked in place:

![HP 8656A bottom PCB rotated open](/assets/hp8656a/hp8656a_bottom_locked_in_place.jpg)

Just push the sping-loaded metal bar in the direction of the arrow and rotate the assembly
further into the notch.

# Removing Electrolytic Caps from the Bottom PCB

With the top and bottom open, the smell was even worse, and pervasive to the point that it
was hard to pinpoint the cause. But old capacitors are notorious for leaking or, in the
case of RIFA capacitors, bursting and catching fire. So I just removed the 4 big ones,
C17, C18, C19, and C20, and check if they smelled on their own. Oh yes, they did, but
even with these caps remove, the small was still everywhere.

Even though the caps looked fine, my current theory 



According to table 6-3, page 6-25, of the service manual, C17, C19, and C20 are rated 3200uF/40VDC, 
and C18 is rated 13000uf/25VDC. 

![HP 8656A big capacitors](/assets/hp8656a/hp8656a_big_capacitors.png)

Since all are +75%/-10%, it's clear that the value doesn't matter that much, as long as you 
don't go lower.

On my unit, C17 is not 13000uF but a whopping 24000uF. I've seen other repairs where C17
has this value, so this is something HP seems to have changed in later model. There's no reason
to follow the service manual in this case!

Capacitors have changed a lot in the past 40 years: back then, they were huge, and often in an axial
configuration with connection leads on either side. That's not the case anymore: not only are they
much smaller now, but an axial layout is harder to mount with pick-and-place machines.

On Digikey, the largest axial electrolytic capacitor that I could find was 
[18000uF](https://www.digikey.com/en/products/detail/vishay-sprague/53D183G025JT6/5611315), 
with a eye-popping price of $24.

Meanwhile, a 
[22000uF cap with a radial configuration](https://www.digikey.com/en/products/detail/nichicon/LLS1E223MELA/3768587) 
is only $4. It will require a bit more work to solder additional wires, but that's a fair
trade-off.

I decided to replace the following capacitors, they're all aluminum electrolytics:


| Reference              | Old            | New            |
|------------------------|----------------|----------------|
| A10C18                 | 24000uF/25V AL | 22000uF/25V AL |
| A10C17, A10C19, A10C20 | 3200uF/40V AL  | 4700uF/50V AL  |
| A10C23, A10C25         | 200uF/25V AL   | 220uF/25V AL   |
| A10C24                 | 500uF/10V AL   | 1000uF/16V AL  |

You can order them from DigiKey with [this list](https://www.digikey.com/en/mylists/list/T52FSWUKOO).

# Fan Replacement

The fan is ridiculously loud. When 120VAC is selected, the fan is powered directly by the mains, there is
not on/off switch.

![HP 8656A fan specifications](/assets/hp8656a/8656a_fan_specs.png)

The complete specs are: 115V 50/60Hz AC, 36-CFM.

In [this EEVblog forum thread](https://www.eevblog.com/forum/repair/hp-8656a-fan-questions/), there
are multiple suggestions about how to reduce the fan noise:

* use a series resistor to reduce the voltage over the fan
* use [a series capacitor](https://www.eevblog.com/forum/repair/hp-8656a-fan-questions/msg2485911/#msg2485911) 
  to reduce the voltage over the fan. 

  This has the benefit of not generating extra heat.
* install a separate 18V transformer and rectifier to drive a 24V DC motor 
* reduce the voltage of the fan by connecting one lead of the fan to 
  a different transformer connection. (My idea!)


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

It's not very clear, but the [schematic](/2024/02/22/HP-8656A-Schematics.html) shows 
the input capacitors inside the power module, a Corcom F2058 with HP identifier 0960-0443:

![HP 8656A input power schematic](/assets/hp8656a/hp8656a_input_power_schematic.jpg)

They're also are drawn on the component itself:

![Corcom F2058](/assets/hp8656a/Corcom F2058.jpg)


Unsurprisingly, this component has been obsolete. You can still find some on eBay, but since
these are recovered from junked equipment, chances are that the capacitors inside them have 
reached their end of life just the same. The HP 8656B, successor of the 8656A, uses a different
power module, the Schaffner FN370-2-22 (HP identifier 0960-0679) which can still be bought
[new on Mouser](https://www.mouser.com/ProductDetail/Schaffner/FN370-2-22?qs=62ecY7oL%252BWMAB7PCNdwF1A%3D%3D)
for the princely sum of $36. Unfortunately, the two are not compatible: the size and the
schematic is different.

Size 66.6x29mm

![Schaffner FN370-2-22](/assets/hp8656a/Schaffner FN370-2-22 schematic.png)

These modules have a selector in them so that, in cooperation with the transformer, you can create 
configurations ofr 100V, 120V, 230V, and 240V mains voltages. If you're sure that you'll
have never export your unit to a different country, you could configure the wiring yourself for
just one AC voltage and use a cheaper line filter module, such as 
[this one](https://www.mouser.com/ProductDetail/Astrodyne-TDI/082SM.00300.00?qs=eP2BKZSCXI7mqcKDec2Dzg%3D%3D)
from Astrodyne TDI.

Here's the equivalent schematic for the 120VAC case:

![HP 8656A input power schematic 120V](/assets/hp8656a/hp8656a_input_power_schematic_120v.jpg)

And here's the equivalent schematic for the 240VAC case:

![HP 8656A input power schematic 240](/assets/hp8656a/hp8656a_input_power_schematic_240v.jpg)

In the 120VAC case, two windings of the transformer and the fan moter are all connected in parallel 
to the 120V mains. In the 240VAC case, the two transformer windings are connected in series, and the
motor is connected to the center of those two windings which act as a series voltage divider, so the
motor will still see 120VAC.

I took the whole back panel apart and extracted the line module, after which I found out that
the module didn't smell at all. So my current, temporary(?) solution is to just put it
back together and live it with.

L -> c (transformer), d (transformer), c (fan)
N -> e (transformer), f (transformer), e (fan)
G -> gnd

Not used: a (transformer mid tap), b (L), j (N)


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


# References

* [8656A Signal Generator Operating & Service Manual](/assets/hp8656a/8656A Signal Generator Operating and Service Manual - 9018-05716.pdf)

    PDF with just the schematics: [8656A Signal Generator Operating and Service Manual - Chapter 8 Schematics.pdf](/assets/hp8656a/8656A Signal Generator Operating and Service Manual - Chapter 8 Schematics.pdf)

* [Comparing the HP 8656A, HP 8657B and HP 3586A](http://www.ko4bb.com/getsimple/index.php?id=comparing-the-hp-8656a-hp-8657b-and-hp-3586a)

    > The HP 8656B is superior to the A model, with smaller step size (10 Hz instead of 100 Hz) and lower phase noise.

* [Lazy Electrons - HP 8656A Repair](https://lazyelectrons.wordpress.com/2018/09/02/hp-8656a-signal-generator-repair/)

    Primarily focuses on the attentuator actuation mechanism. Also has a video shows how to disassembly the thing.

* [EEVBlog forum: discussion about this repair](https://www.eevblog.com/forum/testgear/hp-8656a-nauseating-smell)

* [EEVBlog forum: fan replacement](https://www.eevblog.com/forum/repair/hp-8656a-fan-questions/msg2484969/#msg2484969)

    Uses a 120VAC 92mm fan.

* [EEVBlog forum: Fool for the 8656A Sig Gen](https://www.eevblog.com/forum/testgear/fool-for-the-8656a-sig-gen/)

    Long thread about a repair. Includes replacing voltage regulators and some discussion about the attenuator
    forks and grommets.

* [Youtube: The Radio Shop - HP 8656A Troubleshoot](https://www.youtube.com/watch?v=uPELMl31ZtA)

    Debugs failing power rails.

* [Youtube: HP 8656A Frequency Generator With Bad Front Panel Switches](https://www.youtube.com/watch?v=h_4q0Oa9beA)

