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

# Deconstruction of a Sphere into Smaller Pieces

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

# Choosing the Icosahdron as Core Internal Structure

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
a lower order polyhedron will result in a higher variance in distance between surface and PCB, and in a higher
maximum incident angle at which the leads meet with the PCB surface.

Let me illustrated that with a 2D diagram, but it applies to the 3D version as well.

![Thru-hole geometry](/assets/led_sphere/thru-hole-geometry.svg)

In the figure on the left, a circle is split up into 3 equal sections. In the figure of the right, the same
circle is split into 8 equal sections. The outside circle is the actual surface, the dotted inside circle
is the one in which a triangle or octagon is inscribed. The size of the inside circle depends on the size
of the LEDs that must reside within the shell: it contains part of the main LED body as well as a small
part of the LED leads. The line between the outer points of a section is the 2D equivalent of a PCB.

LEDs that are in the center of a section are perpendicular to this PCB. They are the easiest to mount because
they behave just like any other thru-hole component. The LEDs on the boundary of a section, however, 
hit the PCB at a sharp angle, and yet need to go through the PCB perpendicularly.

When there are only 3 sections, the left case, this incident angle is much sharper than for the right case.

The second issue is even more problematic: LED leads have a fixed length. This length limits the maximum
radius of the circle. In the case on the left, the leads of the LED in the center of a section don't
reach all the way to the PCB! The case on the right doesn't have that problem.

It should be clear that dividing a circle, or a sphere, into a higher number of section has some
crucial mechanical advantages.

But there's one additional benefit: it just looks better to have more sections.

For all the reasons above, I decided on the highest possible regular inscribed polyhedron: the icosahedron.


Another consideration is that a lower order inner polyhedron will result in an outside LED arrangement that's 
is just too coarse to be visually appealing. Since there'll be one PCB design per inner face, the LED arrangement
of each sphere element will be identical. Have more sphere elements just looks better.

XXXX define sphere element XXXX

The higher the number of faces, the closer the polyhedron will match an actual sphere, and the better it will look.

https://cage.ugent.be/~hs/polyhedra/polyhedra.html

One of the most common examples is the a regular soccer ball, which uses a truncated icosahdron to approximate
a sphere.

https://en.wikipedia.org/wiki/Truncated_icosahedron

There's also the class of geodesic domes.

...geodesic dome...

There's an important other consideration than just how it looks: the number of unique parts, and the total number
of parts in general. A truncated icosahdron looks great, but it requires 2 different parts and a total of 32 pieces:
20 hexagons and 12 pentagon. It adds to the overall design, solder and assembly work.

...more faces means smaller pieces as well...

In the end, an icosahedron seemed like the best compromise: it's constructed out of identical triangles, and it has 20 face, 
which is low enough to be manageable, yet high enough reduce the angle between LEDs on opposite sides of a single element.

# LED Selection

Most objects with a large amount of LEDs have flat surfaces, which makes it possible to use surface mounted devices.
This makes mass assembly pretty easy, even for hobbyist: you order a PCB with stencil from your favorite PCB provider,
apply solder paste, put things on a hot plate or in a toaster, and you're done.

But a flat surface is not what I wanted, which left me with a number of options:

* use a flex PCB 
* glue individual SMD LEDs onto the sphere and solder them manually
* use through-hole LEDs

Compared to standard PCBs where you can get a whole bunch of just a couple of dollars, Flex PCB are still quite expensive.
And since I've never worked with them before, I almost certainly would need at least one iterations to really get things right.
Hand-soldering wires to hundreds of LEDs was out of the question, so I chose to go with through-hole LEDs.

The next question is about the kind of LEDs: you can go with the low-level 3-in-1 RGB LEDs that shift all the intelligence
to get different color shades to the driving logic, or you can use smart LEDs from the WS2812 class that where you serially
shift 24-bit color values into a chain of LEDs.

WS2812 LEDs are more expensive, they consume more power, and they aren't many thu-hole versions, LCSC only has the WS2812B-F8,
but the fact that you only need 3 pins per PCB is very attractive: it's something you can still do with regular 2.54mm pin
connectors. So that's what I choose.

As for size, I choose the WS2812B-F8 over the WS2812B-F5. The F8 has an 8mm main diameter versus 5mm for the F5, so the F5 seems
at first more attractive 


# Design of a Sphere with an Icosahedron Base

# LED Distribution within each Triangular Element

So the decision was made to go with an icosahedron 




* 194 LED sphere

    * [Youtube](https://www.youtube.com/watch?v=Q5d8gTppuYo)

* LED foldable spheres

    * [Youtube](https://www.youtube.com/watch?v=3ijp2IU6-3s)

* Interactive Geodesic LED dome

    120 lights.

    Uniform triangles -> non-uniforms LEDs

    * [Youtube](https://www.youtube.com/watch?v=E2HVLBBQtZI)
    * [Instructables](https://www.instructables.com/Interactive-Geodesic-LED-Dome/)

* Geodesic(k) RGB LED Spheres

    Uses 18650 batteries spotwelded together.

    Small: 80 LEDs. Large: 180 LEDs.

    * [Prusaprinters.org](https://www.prusaprinters.org/prints/40182-geodesick-rgb-led-spheres))


* Battery

    * 18650 cells. What configuration?

        e.g 2s4p

    * TP4056 charger module

    * [How to charge li-ion battery pack using IMAX b6 18650 lipo charger](https://www.youtube.com/watch?v=m5V4MG0WZF4)

