---
layout: post
title: LED Sphere
date:  2022-11-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

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

Another one is the [HEALPix algorithm](https://en.wikipedia.org/wiki/HEALPix).

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

Wikipedia has a [table with all such regular and semi-regular polyhedra](https://en.wikipedia.org/wiki/Spherical_polyhedron#Examples)

One could use something as simple as a regular tetrahedron, built out of 4 triangles, that splits the sphere surface
into 4 identical spherical sections:

![Regular tetrahedron projected onto sphere](/assets/led_sphere/spherical_tetrahedron.png)

Here's the version with a cube (6 identical sections):

![Cube projected onto sphere](/assets/led_sphere/spherical_cube.png)

A regular octahedron (8 identical section):

![Regular octahedron projected onto sphere](/assets/led_sphere/spherical_octahedron.png)

A regular dodecahedron (12 identical sections):

![Regular dodecahedron projected onto sphere](/assets/led_sphere/spherical_dodecahedron.png)

And finally a regular icosahedron (20 identical section): 

![Regular icosahedron projected onto sphere](/assets/led_sphere/spherical_icosahedron.png)

From that large Wikipedia table with polyhedra, I've cherry-picked the regular versions. These are 
the also called [Platonic solids](https://en.wikipedia.org/wiki/Platonic_solid). They have
the attractive property that you need exactly 1 sphere element to build up the full sphere. This means that 
you only need to design 1 such piece for your 3D printer and only 1 PCB.

This is certainly not a hard limitation: the truncated icosahedron, used for soccer balls, is a very good 
candidate as well:

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

