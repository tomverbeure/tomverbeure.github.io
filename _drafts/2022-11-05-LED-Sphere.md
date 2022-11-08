---
layout: post
title: LED Sphere
date:  2022-11-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

![LED Sphere](/assets/led_sphere/led_sphere.jpg)

This project started roughly in the summer of 2019. I've always been fascinated by LED creations: massive LED panels on
buildings with animations that seem to jump out into the 3D world, LED cubes with mesmerizing animations, 
[Greg Davill's icosahedron](https://www.hackster.io/news/greg-davill-s-led-icosahedron-packs-20-panels-2-400-leds-into-a-tiny-handheld-fascinator-5de9ad35872a) 
at the Hackaday Superconference. There was always the plan to make something myself, and over the years 
I assembled nice assortment of LED panels, RGB LED strips, and even a few bags of plain vanilla single color 
through-hole LEDs: the "buy" button on AliExpress is sometimes irresitable. 

But nothing ever came off it, until a bunch of lunch time discussions at work (remember them?) with my friend and
3D printing wizzard Jens about how to approach an LED sphere. The idea is not totally original, but there's surprisingly
little out there, even today, almost 3 years after our first discussion: Jiri Paus built a 
[beautiful wireframe sphere with 192 LEDs](https://www.instructables.com/Christmas-LED-Sphere/), 
Whity created created these [2 geodesic structures](https://www.printables.com/model/40182-geodesick-rgb-led-spheres)
that are a close enough approximation, with 80 and 180 LEDs.

All these projects are amazing and their creators spent long hours getting it all together. But there's something
about each of them that doesn't quite do it for me: the wireframe LED sphere only has axial symmetry, the geodesic
sphere isn't really round, and 80, 180, or even 192 LEDs is just not enough.

I wanted an LED sphere that's truly round, without an obvious north-south axis, and with moar LEDs too. 
But who am I kidding, most of all, I wanted to design it from the ground up all by myself.

# Spreading LEDs across a Sphere Surface

An ideal LED sphere has the LEDs spread perfectly even all over the surface: no matter how to rotate the object, or which
angle you look at it, the LEDs are organized exactly the same. There is no top, no bottom, no obvious sub-structure around
which the LEDs are organized.

The problem with this is that it is not possible to do this. There are only 
[good approximations](https://stackoverflow.com/questions/9600801/evenly-distributing-n-points-on-a-sphere).

One extremely good such approximation is [Fibonacci sphere](https://openprocessing.org/sketch/41142)
[algorithm](https://www.vertexshaderart.com/art/79HqSrQH4meL63aAo/revision/9c9YN5LwBQKLDa4Aa).

![Fibonacci sphere](/assets/led_sphere/fibonacci_sphere.png)

Another one is the [HEALPix algorithm](https://en.wikipedia.org/wiki/HEALPix):

![Sphere with HEALPix pixelization](/assets/led_sphere/healpix.jpg)

Unfortunately, it's one thing to come up with an arrangment that is visually almost perfect, it's another 
have one that can be physically created with a reasonable amount of effort. One of my additional constraints
was that the LEDs can be soldered down onto some kind of PCB. Because amazing as it is, precision soldering
more than 192 LEDs onto a metal wire frame is just not something I'm willing to do.

One solution Jens and I explored were flex PCBs. These have the advantage that you can solder down the 
LEDs onto the PCB using the regular and efficient surface mounted method of solder paste and reflow oven, 
yet afterwards you can wrap them around a curved surface... within limits. I still believe that this solution 
is promising, but flex PCBs are a big unknown (how much can they really be flexed?) and they're pretty 
expensive too.

So to the reduce the problem, I fell back to a more traditional approach of a polyhedral inner base with 
3D printed curved sphere elements around it, a flat PCB, and through-hole LEDs.

Whity's LED sphere takes that concept to the extreme in the sense that there isn't a curved surface at all: 
it's triangles all the way down, and there's 1 PCB per LED.

# Splitting a Sphere into Smaller Sections

There are many ways to split up a sphere into a set of individual pieces. The basic principle goes rougly 
as follows: you start with a polyhedron that is circumscribed by a sphere (meaning: all the vertices
of the polyhedron lay on the surface of the sphere.) Then you project the edges of the polyhedron onto
the sphere surface.

Wikipedia has a long page with all kinds of [regular polyhedra](https://en.wikipedia.org/wiki/Regular_polyhedron#The_regular_polyhedra),
but we're particularly interested in the the [Platonic solids](https://en.wikipedia.org/wiki/Platonic_solid),
because they have the attractive property that all sides identical. This means that you only need to design 1 such 
piece for your 3D printer and only 1 PCB.

The figure below shows all possible platonic solids: tetrahedron, cube, octahedron, dodecahedron, and
icosahedron, with respectivelh 4, 6, 8, 12, and 20 faces:

![Platonic polyhedra](/assets/led_sphere/regular_polyhedra.png)

When the sides of these polyhedra are projected onto a circumscribed sphere, you get the following
corresponding [spherical polyhedra](https://en.wikipedia.org/wiki/Spherical_polyhedron#Examples):

![Spherial Platonic polyhedra](/assets/led_sphere/spherical_regular_polyhedra.png)

Using a platonic polyhedron is certainly not a hard limitation: the truncated icosahedron, used for soccer 
balls, is a very good candidate as well:

![Truncated icosahedron projected onto sphere](/assets/led_sphere/spherical_truncated_icosahedron.png)

Compared to a regular icosahedron with 20 identical spherical triangles, the truncated version
needs 20 spherical hexagons and 12 spherical pentagons. That's 2 PCBs and 2 sphere elements to design, and
there's also the question about how to evenly spread LEDs across these 2 surfaces such that the general
density of the LEDs is the same. We're dealing with thru-hole LEDs which have their own density constraints and
some other geometrical limitations as well.

# Geometrical Limitations with Thru-Hole LEDs

Let's talk about those geometrical limitations. 

If the LEDs are located on a curved, spherical, surface while the LED leads are soldered to a flat PCB,
a lower order polyhedron will have in a higher variance in distance between surface and PCB, and in a higher
maximum incident angle at which the leads meet with the PCB surface.

Here's a 2D illustration of that, but it applies to 3D just the same:

![Thru-hole geometry](/assets/led_sphere/thru-hole-geometry.svg)

On the left, a circle is split up into 3 equal sections. In the figure of the right, the same
circle is split into 8 equal sections. The outside circle is the actual surface, the dotted inside circle
is the one in which a triangle or octagon is inscribed. The size of the inside circle depends on the portion
of the LEDs that must reside within the shell: it contains part of the main LED body as well as a small
part of the LED leads. The straight line between the outer points of a section is the 2D equivalent of a PCB.

LEDs that are in the center of a section are perpendicular to this PCB. They are easy to mount because
they behave just like any other thru-hole component. The LEDs on the boundary of a section, however, 
hit the PCB at a sharp angle, but they still need to go through the PCB perpendicularly.

When there are only 3 sections, the left case, this incident angle is much sharper than for the right case.

The second issue is even more problematic: LED leads have a fixed length that limits the maximum
radius of the outside diameter. In the case on the left, the leads of the LED in the center of a section don't
reach all the way to the PCB! The case on the right doesn't have that problem.

It's clear that dividing a circle, or a sphere, into a higher number of section has some crucial mechanical 
advantages.

One final consideration: having more sections just looks better.

So for all the reasons above, I chose on the highest possible regular inscribed polyhedron: the icosahedron.

# LED Selection

The next question is about the kind of LEDs: you can go with low-level 3-in-1 RGB LEDs that shift the intelligence
to get different color shades onto a PWM LED driving controller. Or you can use smart LEDs from the WS2812 class 
that where you serially shift 24-bit color values into a chain of LEDs.

WS2812 LEDs are more expensive, they consume more power, and they aren't many thu-hole versions: LCSC only has the 
WS2812B-F8. But the fact that you only need 3 pins (power, ground, input data) per PCB to control 
a whole string of LEDs is very attractive, because it's something you can do with regular 2.54mm pin connectors. 

As for size, I choose the WS2812B-F8 over the WS2812B-F5. The F8 has an 8mm main diameter versus 5mm for the F5. 
The F5 is attractive if you want to squeeze as many LEDs per area as possible, but the highest density would
have resulted in some other geometry difficulties such as not having enough room for magnet holes. In the end,
LCSC made the decision easy: they only had the F8 version in stock.

# Design of a Sphere with an Icosahedron Base



# Let's Talk about Magnets

Magnets are the primary way to hold the sphere elements together. And there's a lot of them!
There are 2 mechanism in which magnets are used:

* triangle-to-triangle attraction
* triangle-to-center attraction


# Triangle-to-Triangle Magnets

Triangle-to-triangle magnets keep different spherical elements attached to each other, with magents
embedded in each of the 3 sides. It's possible to keep the whole sphere together with just
the triangle-to-triangle magnets, as long as there aren't any major compression or expansion forced
exerted on the sphere. Once the elements see a bit of separation under pressure, all the elements
will collapse and scatter all over the place. It'd be possible to reduce this effect somewhat
by using stronger or more magnet, but there are number of restrictions:

The thickness of the magnets is severly limited by the desire to have a similar gap between
neighboring LEDs within the same spherical element, and neighboring LEDs between neighboring
spherical elements. And since one of the general goals of the LED sphere was to have LEDs as
close to each other as possible, this immediately impacts the thickness of the outside triangle
wall in which the magnets must be embedded. Depending on the chosen pair, the gap between
two LEDs on the same triangle varies between 2.7 and 4.0 mm.

![LED hole-to-hole separation](/assets/led_sphere/led_hole_to_hole_separation.png)

For outside wall, I chose the higher value, 4.0mm, because that number had to be divided by 2, creating
an outside wall thickness of 2mm.

Another thickness related limitation is the number of magnets of each side: because the walls
are so thin, the only location to place the magnets is between LEDs, otherwise the hole for the
magnets cuts in the hole for the LED itself. And since I'm using superglue to fix the magnet in
place, the glue would spill over into the LED hole. My implementation has 6 LEDs on each side,
which restricts the number of magnets to 5.

![Magnets between LED holes](/assets/led_sphere/magnets_between_led_holes.png)

Finally, the same limitation also restricts the diameter of each magnet. Once again, a diameter
that's too high will make the magnet hole intrude into the LED hole.

I first tried magnets with 1mm thickness and a 3mm diameter, but the magnetic force between those
was pathetic. The next step up were magnets advertised as 2mm thick and 5mm diameter. In reality,
the actual thickness is a bit less than that, but the magnet hole is still 2mm to have some
room for some room for a layer of glue and because the printer isn't very accurate either: you
don't want the magnet to stick out of the surrounding surface.

![Some magnet hole measurements](/assets/led_sphere/magnet_depth.png)

In the picture above, you can see that the magnet hole does not intersect with the LED hole. But
after sending this through Cura (the slicers that prepares the model for 3D printing), there
was still 1 magnet hole that intersected with the LED hole. I noticed this too late, but it
wasn't a big deal.

Then there's the issue of magnet polarity.

For the first triangle elements that I assembled, I populated all 5 magnets per side, but after that
I switched to a configuration with only 4 magnets per side. The diagram below shows why:

![Polarity of 5 magnets](/assets/led_sphere/magnet_polarity_5.png)

With 5 magnets populated, there are 2 magnet polarity configurations: `- + - + -` and `+ - + - +`.
Since there are 3 sides per triangle, you need to plan ahead how many triangles there'll be with
2 polarity configurations of one and 1 polarity configuration of the other. In other words,
there'll be 2 classes of triangles, and you'll need to carefully plan ahead. Ideally, you
want all triangles to be identical.

So after the assembling the first 5 triangles, I switched to the following polarity configuration : 
`+ - 0 + -`, where `0` means neutral, or no magnet at all.

![Polarity of 4 magnets](/assets/led_sphere/magnet_polarity_4.png)

With this configuration, every single side of every triangle has the same configuration. You don't 
need to plan anything ahead. 

You'd think tha removing 1 magnet reduces the attraction strength between 2 triangle by 20%, but 
it's more than that, at least on my cheap 3D printer. The reason is because because of what
you see in the picture below:

XXXX picture with gaps between pointed ends of each triangle XXXX

The sides are designed to be completely flat, but after printing they are ever so slightly curved.
The magnetic force is inversely proporitional to the distance squared, so going from 2
magnets between literally smashed against eachother to a very tiny gap makes a big difference. And
since the magnet that was removed is the one that's most likely to be the touching one on a curved
surface, it contributes to a bigger share of the overall attraction between 2 sides.

# Triangle to Center Magnets

# Number of magnets

If you want to copy the design that I've used, you'll need this amount of magnets:

* [5mm x 2mm](https://www.amazon.com/gp/product/B09QHKKWMC): 20 triangles x 3 sides x 4 magnets = 240 (3 packs)
* [4mm x 4mm](https://www.amazon.com/gp/product/B097Z5TKCY): 5 triangles x 4 magnets x 2 both sides  = 40 (1 pack)

So that's a grand total of 280.

![Magnets 4x4 and 5x2](/assets/led_sphere/magnets_4x4_and_5x2.jpg)

My LED sphere has more than 300 magnets because I plans for two center PCBs and triangle attachments,
as well as support attachments for the top and bottom 5-piece circles. But I never implemented those...

You could save on 5x2 magnets, and make the sphere much stronger, by gluing the top and bottom sections of
5 triangles together. This has one major negative: if 1 triangle goes bad, it will be hard to replace just 
that one...

You'd think that the biggest contributor to the weight of the sphere are the batteries, but that's not
the case: it's the magnets! The magnets are tiny and light individually, but not so much when you
have almost 300 of them!

# Keeping Track of Magnet Polarity

It is absolutely **crucial** to keep track of the polarity of the magnets. I used special markers
that worked to mark them sides with either red or gray. I also prepare a whole batch of them:

* have a reference magnet attached to a metal plate: the casing of my tiny Lenovo PC. (No magnetic
hard drive, of course!)
* peal off a whole bunch of magnets with the same polarity and attach them to the metal plate.
* keep the magnets far enough away from each other.
* mark them with red or gray depending on which polarity I needed.

I found these markers in my daughter's toolkit. They worked well for me.

I just can't stress enough how important it is to do this right! The polarity markings sometimes don't
still well and fade away. Don't guess and double check that you mark sides correctly when you reapply
marker.

# Glueing Magnets to PLA

Google told me that super glue is the way to go to attach magnets to 3D printed PLA. Hot glue is not
recommended because high temperatures reduce the strength of the neodymium magnets. Super glue comes
in all kinds of containers and application methods. I tried a bunch of them. I found the one with a
little brush easiest to use.

Still, gluing that many magnets is a total pain. Even if you're careful, expect that stuff to stick
everywhere. My application method was as follows:

* dip the brush in the glue
* apply to the magnet hole of interest
* push the magnet in place. Expect glue to stick on your finger.
* use a cotton swab to remove excess glue.

Optional extra steps:

* remove the new magnet from an earlier placed magnet because they love each other very much.
* replace cotton swabs often, because the glue hardens quickly... but only on cotton swabs, not
  between the magnet and the PLA....

Here's the polarity that I used for my build:

XXXXXX


# References

* [Video](https://www.youtube.com/watch?v=Q5d8gTppuYo) of Jiri's 192 LED sphere
* [Build instructions](https://www.printables.com/model/40182-geodesick-rgb-led-spheres)
  for the Geodesic(k) RGB LED Spheres with 80 and 180 LEDs
* Huge [Interactive Geodesic LED dome with 120 lights](https://www.youtube.com/watch?v=E2HVLBBQtZI)
  ([build instructions](https://www.instructables.com/Interactive-Geodesic-LED-Dome/))

* Battery

    * 18650 cells. What configuration?

        e.g 2s4p

    * TP4056 charger module

    * [How to charge li-ion battery pack using IMAX b6 18650 lipo charger](https://www.youtube.com/watch?v=m5V4MG0WZF4)

