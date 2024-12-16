---
title: A Symbolic Reference and Hardware Model in Python
date: 2024-03-26 00:00:00 -1000
categories:
---

* TOC
{:toc}

# The Traditional Hardware Design and Verification Flow 

In a professional FPGA or ASIC development flow, multiple models are tested
against each other to ensure that the hardware behaves the way it should.

Common models are:

* a behavioral reference model that describes the functionality at the highest level

    These models are often implemented in Matlab, Python, C++ etc. and are usually
    completely hardware architecture agnostic. They are often not bit accurate
    in their calculated results, by using floating point numbers instead of 
    the fixed point numbers that are used by the hardware, 

    A good example is the [Floating Point C Model](/rtl/2018/11/26/Racing-the-Beam-Ray-Tracer.html#a-floating-point-c-model)
    that I used to develop my Racing the Beam Ray Tracer, though in this case, 
    it later transistioned into a hybrid reference/achitectural model.

    ![Checkered plan with reflecting sphere above it](/assets/rt/fixed_point.png)

* an architectural model

    An architectural model is already aware of how the hardware is split into major
    functional groups and models the interfaces between these functional groups
    in a bit-accurate away at the interface level. It doesn't have a concept of 
    timing in the form of clock cycles.

* source hardware model

    This model is the source from which the actual hardware is generated. Traditionally,
    this was an RTL model written in Verilog or VHDL, but high-level synthesis (HLS) is 
    getting some traction as well. In the case of RTL, this model is cycle accurate. In 
    the case of HLS, it still won't be. The difference between an HLS model and the architectural 
    model is in the level at which the hardware is described: the HLS model will describe every 
    single hardware module of the design. The architectural model will often stop at the 
    level of functional group of hardware models.

* RTL model

    The Verilog or VHDL model of the design. This can be the same as the source hardware
    model or it can be generated from HLS.
    
* Gatelevel model

    The RTL model synthesized into a gatelevel netlist.

During the ASIC design flow, different models are compared against each other to ensure
that all of them behave the same way. The results created by each model should be the same...
to a certain extent, since it's not possible to guarantee identical results between floating
point and fixed point models.

One thing that is constant among these models is that they get fed with, operate on, and output
actual data values. 

Let's use the example of a video pipeline.

The input of the hardware block might be raw pixels from a video sensor, the processing could be 
some filtering algorithm to reduce noise, and the outputs are processed pixels.

To verify the design, the various models will be fed with a combination of generic images, 
'interesting' images that are expected to hit certain use cases, images with just random pixels, 
or directed tests that explicity try to trigger corner cases. When there is mismatch between different 
models, the fun part begins: figuring out the root cause. For complex algorithms that contain a lot 
of state, the error may have happened tens of thousands of transactions before they manifest themselves 
at the output.  Tracking down such an issue can be a gigantic pain.

And for some hardware units, the hard part of the design is not the math, but getting the right
data to the math units at the right time, by making sure that the values are written, read,
and discarded from internal RAMs and FIFOs in the right order. Even with a detailed microarchitectural
specification, a major part of the code may consist of using just the correct address calculation or
multiplixer input under various conditions.

For these kind of units, I've found symbolic models to be a major win: instead of carrying around data 
values through the various stages of the algorithm, I carry around where the data is coming from. It's 
not easy to do so in C++ or RTL, but it's trivial to do so in Python. So I've added two additional models to
my arsenal of tools:

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
* the pixel blocks are send in scan-order, from left to right and from top to bottom
* pixels arrive through a 16 pixel wide interface that carries pixels in 4x4 pixel tiles
* these tiles themselves are also transmitted in scan order within the 64x64 pixel block
* the output of the block is the input pixels downscaled by a factor of 2 in both directions
* a 5-tap 2-D filter is used on the input image on every other pixel
* 



# The Reference Model

When modelling transformations that work at the picture level, it's extremely convenient
to just assume that you have no memory size constraints so that you can access to all
pixel information at all times, no matter where it's located in the image. You don't
have to worry about how much RAM this would take on silicon: it's up to the designer of
the micro-architecture to figure out how to be efficient.

It usually results in a huge simplification of the reference model, and that's a good
thing because you want that reference model to be the source of truth. 

For our example, the reference model simply creates a array of output pixels where
each output pixels contains the coordinates of all the input pixels that are required
to calculate its value.

The pseudo code is someting like this:

```python
for y in range(HEIGHT):
    for x in range(HEIGHT):
        if near super block boundary:
            use 3x3 filter
        else:
            use 5x5 filter

        get coordinates of input pixels for filter
        store coordinates at (x,y) of the output image
```

The reference model python code is not much more complicated. You can find the
code [here](XXX). Instead of using a 2-dimensional array, it uses an associative
key-value store with the output pixel coordinates as key. This is a personal 
preference, but I find `ref_output_pixels [ (x,y) ]` easier to read than `ref_output_pixels[y][x]`.

When the reference model data creation is complete, the `ref_output_pixels` array will contain
values like this:

```python
(0,0) => ( (0,0), (0,0), (1,0), 
           (0,0), (0,0), (1,0),
           (0,1), (0,1), (1,1) ),
(1,0) => ( (0,0), (1,0), (2,0), 
           (0,0), (1,0), (2,0),
           (0,1), (1,1), (2,1) ),
...
(8,7) => ( (6,5), (7,5), (8,5), (9,5), (10,5), 
           (6,6), (7,6), (8,6), (9,6), (10,6),
           (6,7), (7,7), (8,7), (9,7), (10,7),
           (6,8), (7,8), (8,8), (9,8), (10,8),
           (6,9), (7,9), (8,9), (9,9), (10,9) ),
...
```

Note some output pixels only have 9 input pixels, those are the boundary of a super block,
while others have 15 input pixels.

The reference value of each output pixel is a list of input pixels. At no point do
I care about the actual value of the pixels. That's why I call it a symbolic model. 

# The Micro-Architecture Model

For a hardware implemention, area and performance some of the most important considerations,
and that is something the specification has taken into account. When downscaling images, it's common
to use line stores: RAMs that store previous lines of the image and that are wide as the maximum
supported image size. However, the number of line stores required depends on the number of filter taps.
In our case, we can 5 filter taps, which would require 4 line stores. For a maximum resolution of
7684 pixels, that's 30KB of RAM, or more if you're using more than 8 bits per pixel.

The specification has a number of features that make it possible to reduce requirements:

* it operates on image in super blocks of 64x64 pixels
   
    For pixels inside the super block, that reduces the amount of working line store 
    memory to 4 times 64 pixels or 256 bytes. It also reduces the bandwidth that is required
    to handle data that must be managed between super blocks: you still need one or more line stores 
    of 7684 pixels, but they must only be stored or fetched once for every super block row. In
    other words, once every 64 lines. That opens up the opportunity to stream this line store
    data in and out of external DRAM instead of keeping it on-chip.

* reduces filter size for pixels at the boundary of a super blocks

    This reduces the amount of data that must be managed and stores for inter-super block
    operations. Instead of keeping 4 line stores in external DRAM, we now only need 1, which
    lowers the line store bandwidth even more.

* 4x4 size pixel tiles

    This allows processing 16 pixels at once, which is great to reduce the clock speed for 
    high resolution images with high pixel rates.

But it's not all roses! The optimizations above have some negative consequences as well:

* pixels from the super block above must be fetched from DMA and stored in a local memory
* pixels from the bottom of the current super block must be sent to DMA
* the right-most border of the current super block must become the left pixels of the next one
* a 5x5 sized filter is larger than the 4x4 input tiles, which adds some more data movement
* 4x4 size input tiles get downsampled to 2x2 size output tiles, but they must be sent
  out again as 4x4 tiles.
 
While the RAM area savings are totally worth it, all this adds a significant amount of data 
management complexity.  This is the kind of problem where a symbolic micro-architecture model shines.

The source code of the hardware symbolic model can be found [here](XXX).

It works as follows:

* an input stream is generated of 4x4 pixel tiles that are sent super block by super block and then
  tile by tile
* the DMA is modelled as a FIFO in which the bottom pixels of a super block area stored and then
  fetches when the super block of the next row needs the pixels above.




