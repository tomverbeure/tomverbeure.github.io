---
layout: post
title:  Racing the Beam Ray Tracer Whitepaper
date:   2018-11-22 14:00:00 -0700
categories: RTL
---

# Introduction

One of the most exciting moments of a chip designer is the first power-on of freshly baked silicon. Engineers
have been flown in from all over the world. Debug stations are ready. Emails are being sent with hourly
status updates: "Chips are in SFO and being processed by customs!", "First vectors are passing on the tester!",
"First board expected in the lab in 10mins!".

Once in the lab, it's a race to get that thing doing what it has been designed to do.

And that's where the difference between a telecom silicon vendor and a graphics silicon vendor becomes clear:
when you DSL chip works, you're celebrating the fact that bits are being successfully transported from one
side of the chips to another. Nice! But when your graphics chips comes up, there's suddenly
a zombie walking on your screen. Which is awesome!

All of this just to make the point: there's something magic about working on something that puts an image
on the screen.

So when I reverse engineered the Pano Logic device, getting the VGA interface was the first target. Luckily,
compared to Ethernet and USD, it's also far easier to get up and running.

After [my short RISC-V detour](...), instead of getting back to Ethernet, I wanted get a real application going, and
since ray tracing has been grabbing a lot of headlines lately, why not check if anything could be done on this
pedestrian Spartan-3E FPGA that lives in the Pano Logic G1?

My first experience with ray tracing was sometime in the early nineties, when I was running [PovRay](...) on
a 33MHz 486 in my college dorm. And when thinking about a subject for my thesis, hardware accelerated ray-triangle
intersection was high on the list but ultimately rejected.

Lately, ray tracing has become sort of a big thing, so I wondered if anything could be done on my Pano Logic.

Because, yes, it's a pretty pedestrian FPGA by today's standards, but the specs are actually pretty decent 
when compared to many of today's hobby FPGA boards: 27k LUTs, quite a bit of RAM, and 36 18x18bit hardware multipliers.

Is that enough to do ray tracing? Let's find out...

# Racing the Beam - Graphics without a Frame Buffer 

The traditional way of doing computer graphics looks like this:

* Render an image to frame buffer A which is large enough to store the value of all pixels on the screen.
* While the previous step is on-going, send the previously calculated image that's stored in an alternate
  framebuffer B to the monitor.
* When you're doing rendering your images, start sending the contents of frame buffer A to the monitor and
  render the next image in frame buffer B.

This setup has the huge advantage that you decouple render time and monitor refresh rate, and it's used
in all modern graphics system (with some potential enhancements.)

But there are a lot of pixels on a screen, and even for a 640x480 resolution and 24 bits-per-pixel, you need
7.3Mbits per frame buffer, and you need two of those. So that's 14.5Mbits of memory. The FPGA on the Pano Logic
has only 648Kbit of block RAM.

Luckily, there's a 32MByte of DRAM on the board, which is more than enough. All the SDRAM IO connections
to the FPGA have been mapped out, and Xilinx has an SDRAM memory controller generator, so using that
should be a breeze. Alas, no. The generator only supports regular DDR SDRAM. It does NOT support the
LPDDR that's used by the Pano. Designing a custom DRAM controller isn't super hard, but it's a major
project in itself, one that I didn't want to start just yet.

So the SDRAM was out. And so were all traditional graphics rendering methods.

When you can't use memory to store your image, you go back to a technique that was used more than 40 years
ago in the Atari 2600 VCS: you race the beam! The beam is the beam of a CRT monitor that paints the pixel
onto the phosphor.

Back in those days, memory was extremely expensive, so to save on cost, they dropped the frame buffer and
replaced it by a line buffer. It was up to the CPU render the next line before the previous one was sent
to the screen. If the CPU did not finish in time, the TIA video chip would just send the previous line again.

We can take this technique to its ultimate conclusion where you not only replace the frame buffer by a line
buffer, but where you drop the line buffer completely: if you are able to calculate each pixel on-the-fly
exactly when the video output block wants it, you don't need memory at all!

Now most graphics rendering techniques don't build the image in pixel scan order: they'll first paint the
background, then they draw a triangle here and a triangle there, and eventually the whole image comes together.

But ray tracing is not like that: you shoot a ray from a camera through a pixel to the scene and calculate
the value of that pixel. More contempary ray tracing software choses the pixel in a stochastic order: essentially
randomly distributed across the image. The benefit of this is that you see the whole image at once while it
slowly refines into a high quality image. But that's totally not necessary: you can just as well chose the
pixels in scan order.

And if you're then able to calculate one pixel per pixel clock, you end up with a ray tracer that's racing
the beam!

https://events.ccc.de/congress/2011/Fahrplan/attachments/2004_28c3-4711-Ultimate_Atari_2600_Talk.pdf

# One Pixel per Clock Ray Tracing

Ray tracing algorithms typically render scenes with a lot of triangles. The algorithm injects a ray into
the scene, figures out the closest intersecting triangle.  If there are hundreds of thousands or more triangles, 
it uses bounding box acceleration structures to reduce the number of ray/triangle intersections.

Once it has found the closest object, it calculates a base color and then casts a bunch
of secondary rays into the scene to figure out light spots, shadows, reflections, refractions etc. 

Doing all of that in a single clock cycle is a bit of a challenge, so there were some consequences and
trade-offs.

First of all, if you have only 1 clock to calculate something, you are forced to calculate in parallel whatever
you can, and if that's not possible, you do it in a rigid pipeline: yes, it can potentially take many cycles
to calculate one pixel, but you can issue the calculate of a new pixel each clock cycle, so you still end
up with one pixel per clock at the output.

It also means that all the geometry of the scene is transformed into math operations that are embedded in the
pipeline. Do you want one more sphere? Well, that will cost you all the hardware needed to calculate a ray/sphere
intersection, the reflected ray, the sphere normal etc.

But wait, it gets worse! One of the main benefits of ray tracing are the ease by which it can render reflections.
It'd be a shame if you couldn't show that off. Unfortunately, reflection is recursive: if you have 2 reflecting
objects, light rays can essentially bounce between them forever. You'd need an infinite amount of hardware to 
do that in one clock cycle... but even if you limit things to 2 bounces, you're still looking at a rapid expansion
of math operations, and thus HW resources.

Or you chose the alternative: only allow 1 reflecting object in the scene.

Since our FPGA is really quite small, there was a strict limit on what could be done. So the decision was made
to have a scene with just 1 non-reflecting plane, a reflecting ball.

# Creating a C model

For a project with a lot of math, and a lot of pixels (and thus potentially very large simulation times), it's
essential to first implement a C model to validate the whole concept before laying things down in RTL.

First step is to simply use floating point. Converting to a format that's more suitable for an FPGA is for later.

It didn't take long to get the first useful pixels on the screen:

![cmodel1_plane]({{ "/assets/rt/cmodel1_plane.png" | absolute_url }})

The [code](https://github.com/tomverbeure/rt/blob/cba6c0f1caa04c2797f21d0c4d85c9f1c127c88d/src/main.c) is almost trivial.
I decided on pure C code without any outside libraries, so I had to create my own vector structs. I made a lot
of changes to those along the way.

I used the [scratchapixel.com](scratchapixel.com) ray-tracing tutorial code as the base for 
[ray/plane](https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-plane-and-ray-disk-intersection) 
and [ray/sphere](https://www.scratchapixel.com/lessons/3d-basic-rendering/minimal-ray-tracer-rendering-simple-shapes/ray-sphere-intersection) intersection.

A bit more code resulted in this:

![cmodel2_ray-sphere-intersection]({{ "/assets/rt/cmodel2-ray-sphere-intersection.png" | absolute_url }})

and finally this:

![cmodel3-reflection.png]({{ "/assets/rt/cmodel3-reflection.png" | absolute_url }})


