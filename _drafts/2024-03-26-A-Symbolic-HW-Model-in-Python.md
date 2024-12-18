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

# An Image Downscaler as Example Design

Let's design a hardware module that is easy enough to not spend too much time on it for
a blog post, but complex enough to illustrate the benefits of a symbolic model: an
image downscaler.

The core functionality is the following:

* it accepts an 8-bits monochrome image with a maximum resolution of 7680x4320.
* it downscales the input image with a fixed ratio of 2 in both directions.
* it uses a 3x3 tap 2D filter kernel for downscaling.

![2:1 downscaling with 3x3 filter kernel](/assets/symbolic_model/symbolic_model-downscaling3x3.svg)

If this downscaler is part of a streaming display pipeline, you don't have
a lot of flexibility: pixels are coming in left to right and top to bottom
scan order and you need 2 line stores (memories) because you have 3 vertical taps.
At least, the line stores can half the horizontal resolution, because of the 2:1
scaling ratio, but that's still 7680/2 ~ 4KB of RAM just for line buffering. In the
real world, you'd have to multiply that by 3 to support RGB instead of monochrome.
And we'll need to read and write from this RAM every clock cycle, so there's no
chance of off-loading this storage to cheaper memory such as external DRAM.

However, we're lucky: the downscaler is part of a video decoder pipeline and those 
typically work with super blocks of 32x32, 64x64 or 128x128 pixels that are scanned 
left-to-right and top-to-bottom. And within each super block, pixels are grouped in
sets of 4x4 pixels that are scanned the same way within the super block.

In summary, there are 3 nested left-to-right, top-to-bottom scan operations:

* the pixels inside each 4x4 pixel block
* the pixel blocks inside each super block
* the super blocks inside each picture

The overall data flow then is something like this:

[![Input image format](/assets/symbolic_model/symbolic_model-input_image.svg)](/assets/symbolic_model/symbolic_model-input_image.svg)
*(Click to enlarge)*

The output has the same organization of pixels, 4x4 pixel blocks and super blocks, but due to the
2:1 downsampling in both directions, the size of a super block is 32x32 instead of 64x64.
incoming number of pixel blocks.

There is a major advantage to having the data flow organized this way: 

<p style="text-align:center;"><b>The downscaler operates on one super block at a time instead of the full image.</b></p>
   
For pixels inside the super block, that reduces size of the *active* line stores from 
7680 to just 64 pixels per line store, or 128 bytes for a 3 pixel high filter kernel. 
While you still need full picture width line stores when moving from one row of super blocks 
to the one below it, the the bandwidth that is required to access those line store is but a 
fraction of the one befire: 1/64th to be exact. That opens up the opportunity to stream line 
store data in and out of external DRAM instead of keeping it on-chip.

But it's not all roses! There are some negative consequences as well:

* pixels from the super block above must be fetched from DMA and stored in a local memory
* pixels from the bottom of the current super block must be sent to DMA
* the right-most column of pixels from the current super block are used in the next super block to
  when doing the 3x3 filter operation, which adds more data management.
* 4x4 size input tiles get downsampled to 2x2 size output tiles, but they must be sent
  out again as 4x4 tiles. This requires some kind of pixel block coalescing operation.
 
While the RAM area savings are totally worth it, all this adds a significant amount of data 
management complexity.  This is the kind of problem where a symbolic micro-architecture model 
shines.

[![System block diagram](/assets/symbolic_model/symbolic_model-system_block_diagram.svg)](/assets/symbolic_model/symbolic_model-system_block_diagram.svg)

# The Reference Model

When modeling transformations that work at the picture level, it's extremely convenient
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
for y in range(OUTPUT_HEIGHT):
    for x in range(OUTPUT_WIDTH):
        get coordinates of input pixels for filter
        store coordinates at (x,y) of the output image
```

The reference model python code is not much more complicated. You can find the
code [here](XXX). Instead of using a 2-dimensional array, it uses an associative
key-value array with the output pixel coordinates as key. This is a personal 
preference: I find `ref_output_pixels [ (x,y) ]` easier to read than `ref_output_pixels[y][x]`
or `ref_output_pixels[x][y]`.

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
(8,7) => ( 
           (7,6), (8,6), (9,6),
           (7,7), (8,7), (9,7),
           (7,8), (8,8), (9,8) ),
          
...
```

The reference value of each output pixel is a list of input pixels. At no point do
I care about the actual value of the pixels. That's why I call it a symbolic model. 

# The Micro-Architecture Model

The source code of the hardware symbolic model can be found [here](XXX).

It works as follows:

* an input stream is generated of 4x4 pixel tiles that are sent super block by super block and then
  tile by tile
* the DMA is modelled as a FIFO in which the bottom pixels of a super block area stored and then
  fetches when the super block of the next row needs the pixels above.




