---
title: A Symbolic HW Model in Python
date: 2024-03-26 00:00:00 -1000
categories:
---

* TOC
{:toc}

# The Traditional Hardware Design and Verification Flow 

In a professional FPGA or ASIC development flow, there are often multiple model that are tested
against each other to ensure that the final model behaves as it should.

Common models are:

* a reference model that describes the behavior at the highest level

    These models are often implemented in Matlab, Python, C++ etc. and are usually
    completely hardware architecture agnostic.

* an architectural model

    An architectural model is already aware of how the hardware is split into major
    functional groups and models the interfaces between these functional groups
    in a bit-accurate away at the interface level. It doesn't have a concept of 
    timing in the form of clock cycles.

* source hardware model

    This model is the source from which the actual hardware is generated. Traditionally,
    this was an RTL model written in Verilog or VHDL, but HLS getting some traction as well. 
    In the case of RTL, this model is cycle accurate. In the case of HLS, it still won't
    be. The difference between an HLS model and the architectural model is in the level
    at which the hardware is described: the HLS model will describe every single hardware
    module of the design. The architectural model will often stop at the level of functional
    group of hardware models.

* RTL model

    The Verilog or VHDL model of the design. This can be the same as the source hardware
    model or it can be generated from HLS
    
* Gatelevel model

    The RTL model synthesized into a gatelevel netlist.

During the ASIC design flow, different models are compared against each other to ensure
that all of them behave the same way. The results created by each model should be the same.

One thing that is constant among these models is that they get fed with, operate on, and output
actual data values. 

Let's use the example of a video pipeline.

The input of the hardware block might be raw pixels from a video sensor, the processing could be 
some filtering algorithm to reduce noise, and the outputs are processed pixels.

To verify the design, the various models will be fed with a combination of generic images, 
'interesting' images that are expected to hit certain use cases, images with just random pixels, 
or directed tests that explicity try to trigger corner cases.

When there is mismatch between different models, the fun part begins: figuring out the root cause.
For complex algorithms that contain a lot of state, the error may have happened tens of thousands
of transactions before they manifested themselves on the output.  Tracking down such an issue
can be a gigantic pain.

For a certain class of algorithms, the hard part of the design is not the math, but getting the right
data to the math operators at the right time by making sure that the right values are written, read,
and discarded from internal RAMs and FIFOs at the right time. Even with a detailed microarchitectural
specification, a major part of the code may consist of using just the right address calculation under
various conditions.

For those, I've found symbolic models to be a major win: instead of carrying around data values through
the various stages of the algorithm, I carry around where the data is coming from. It's not easily possible
to do so in C++ or RTL, but it's trivial to do so in Python. So I've added two additional models to
the list:

* a Python symbolic reference model
* a Python symbolic hardware model

In this blog post, I'll go through an example case where I use such model.

# An Example Design 

Let's design a hardware module with the following characteristics:

* it accepts an 8-bits gray scale image with a maximum resolution of 7680x4320.
* it downscales the input image by a factor of 2 in both directions.
* it uses a 5x5 tap 2D filter for downscaling, except for input pixels that require
  looking over a multiple-of-64 pixels boundary. For those a 3x3 tap filter is used.







* the image is sent to the module in pixel blocks of 64x64 pixels
* the pixel blocks are send in scan-order, from left to right and from right to left
* pixels arrive through a 16 pixel wide interface that arranged in 4x4 sized pixel tiles
* these tiles themselves are also transmitted in scan order within the 64x64 pixel block
* the output of the block is the input pixel downscaled by a factor of 2 in both directions
* a 5-tap 2-D filter is used on the input image on every other pixel
* 

