---
layout: post
title:  Newsflash - Racing the Beam Ray Tracer"
date:   2018-11-22 00:00:00 -1000
categories: RTL
---

# For Immediate Release - Racing the Beam Ray Tracer

Ray-tracing is the best rendering technique. Used in large scale compute farms to render the images
of movies, it is also very calculation intensive, taking many hours to complete just a single image.

Nobody ever considered using ray tracing as the primary way of rendering graphics on an FPGA, and definitely not in a 10 year
old Spartan 3E. That ends today.

**Introducing: The Racing the Beam Ray Tracer !!!**

<iframe src="https://player.vimeo.com/video/303943571" width="640" height="360" frameborder="0" webkitallowfullscreen mozallowfullscreen allowfullscreen></iframe><script src="https://player.vimeo.com/api/player.js"></script>

RtBRT has the following unique features:

* Zero Latency Racing the Beam Rendering

    Pioneered by the iconic Atari 2600, now updated for the twenty first century, RtBRT features zero latency rendering: the value of each pixel
    is calculated at the exact point when it's needed: when it must be sent to the monitor.

* Frame Buffer Free

    Pixel values are calculated on the fly. No large and costly memory buffers are needed to temporarily store an image.

* Direct Math Architecture

    The RtBRT hardware contains all the math operations that are necessary for your scene and not one math operation more... or less.

* Zero Geometry Buffer

    Even more revolutionary than the lack of frame buffer is the total lack of memory required for geometry, a direct
    consequence of the Direct Math Architecture. The scene geometry is converted to pure math and then to dedicated hardware operations.

    There is no need for costly acceleration tree structures either!

* Driver-Free Plug and Play!

    Thanks to RtBRT, drivers are a thing of the past. Once the location of geometry and camera has been
    set, the hardware does all the rest.

* MR1, the Secure RISC-V CPU

    The [mathematically proven bug-free MR1 RISC-V CPU](/risc-v/2018/11/19/A-Bug-Free-RISC-V-Core-without-Simulation.html),
    which is used to move around the dynamic parts of your scene, is immune to all security attacks related to speculative execution such as 
    Meltdown and Spectre. Unlike most CPUs that are used to render today's games.

For more information, check the [Ray the Beam Ray Tracer](/rtl/2018/11/26/Racing-the-Beam-Ray-Tracer.html) article.


