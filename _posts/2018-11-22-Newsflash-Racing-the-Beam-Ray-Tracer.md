---
layout: post
title:  Newsflash - Racing the Beam Ray Tracer"
date:   2018-11-22 14:00:00 -0700
categories: RTL
---

# Newsflash - For Immediate Release - Racing the Beam Ray Tracer

Ray-tracing has always been one of the best rendering techniques. It's often used in large scale compute farms to render the images
of movies. But it's also very calculation intensive, and those movie images can take many hours per frame to complete.

Nobody ever considered using ray tracing as the primary way of rendering graphics on an FPGA, and definitely not in a 10 year
old Spartan 3E. Well, that ends today.

Introducing: The Racing the Beam Ray Tracer !!!

RtBRT has a bunch of very appealing and unique features:

* Zero Latency Racing the Beam Rendering

    Pioneered by the iconic Atari 2600, updated for the twenty first century, RtBRT has zero latency rendering: the value of each pixel
    is calculated at the exact point where it's needed, when it must be sent to the monitor.

* Frame Buffer Free

    Since pixel values are calculated on the fly, no large and costly memory buffers are needed to temporarily store an image.

* Direct Math Architecture

    The RtBRT hardware contains all the math operations that are necessary for your scene and not one math operation more... or less.

* Zero Geometry Buffer

    Even more revolutionary than the lack of frame buffer is the total lack of memory required for geometry, which is a direct
    consequence of the Direct Math Architecture. The scene geometry is converted to pure math to dedicated hardware operations.
    There is no need to crawl acceleration tree structures either.

* Driver-Free Plug and Play!

    Drivers are a huge source of bugs and instability. The best way to avoid these issues is to do away
    with them altogether! Thanks to RtBRT, drivers are a thing of the past. Once the location of geometry and camera has been
    set, the hardware does all the rest.

* Secure RISC-V CPU

    The mathematically proven bug-free MR1 RISC-V CPU, which is used to move around the dynamic parts of your scene, is immune
    to all security attacks related to speculative execution such as Meltdown and Spectre. Unlike most CPUs that are used to render
    today's games.

For more information, check the [Ray the Beam Ray Tracer Whitepaper](...)

