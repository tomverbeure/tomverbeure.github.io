---
title: Symbolic Reference and Hardware Models in Python
date: 2024-03-26 00:00:00 -1000
categories:
---

* TOC
{:toc}

# The Traditional Hardware Design and Verification Flow 

In a professional FPGA or ASIC development flow, multiple models are tested
against each other to ensure that the final design behaves the way it should.

Common models are:

* a behavioral model that describes the functionality at the highest level

    These models can be implemented in Matlab, Python, C++ etc. and are usually
    completely hardware architecture agnostic. They are often not bit accurate
    in their calculated results, for example because they use floating point numbers 
    instead of fixed point numbers that are more commonly used by the hardware, 

    A good example is the 
    [floating point C model](/rtl/2018/11/26/Racing-the-Beam-Ray-Tracer.html#a-floating-point-c-model)
    that I used to develop my Racing the Beam Ray Tracer, though in this case, 
    the model later transistioned into a hybrid reference/achitectural model.

    ![Checkered plan with reflecting sphere above it](/assets/rt/fixed_point.png)

* an architectural transaction accurate model

    An architectural model is already aware of how the hardware is split into major
    functional groups and models the interfaces between these functional groups
    in a bit-accurate and transaction-accurate way at the interface level. It doesn't 
    have a concept of timing in the form of clock cycles.

* source hardware model

    This model is the source from which the actual hardware is generated. Traditionally,
    and still in most cases, this is a synthesizable RTL model written in Verilog or VHDL, but 
    high-level synthesis (HLS) is getting some traction as well. In the case of RTL, this model 
    is cycle accurate. In the case of HLS, it still won't be. 

    The difference between an HLS C++ model[^1] and an architectural C++ model is in the way it is coded: 
    HLS code needs to obey coding style restrictions that will otherwise prevent the HLS tool 
    to convert the code to RTL. The HLS model is usually also split up in much more smaller units 
    that interact with each other.

    [^1]:Not all HLS code is written with C++. There are other languages as well.


* RTL model

    The Verilog or VHDL model of the design. This can be the same as the source hardware
    model or it can be generated from HLS.
    
* Gate-level model

    The RTL model synthesized into a gatelevel netlist.

During the design process, different models are compared against each other. Their outputs 
should be the same... to a certain extent, since it's not possible to guarantee identical results 
between floating point and fixed point models.

One thing that is constant among these models is that they get fed with, operate on, and output
actual data values. 

Let's use the example of a video pipeline.

The input of the hardware block might be raw pixels from a video sensor, the processing could be 
some filtering algorithm to reduce noise, and the outputs are processed pixels.

To verify the design, the various models are fed with a combination of generic images, 
'interesting' images that are expected to hit certain use cases, images with just random pixels, 
or directed tests that explicity try to trigger corner cases. When there is mismatch between different 
models, the fun part begins: figuring out the root cause. For complex algorithms that have a lot of 
internal state, an error may have happened thousands of transactions before it manifests itself
at the output. Tracking down such an issue can be a gigantic pain.

For many hardware units, the hard part of the design is not the math, but getting the right
data to the math units at the right time, by making sure that the values are written, read,
and discarded from internal RAMs and FIFOs in the right order. Even with a detailed micro-architectural
specification, a major part of the code may consist of using just the correct address calculation or
multiplixer input under various conditions.

For these kind of units, I use a different kind of model: instead of passing around and operating on data 
values through the various stages of the pipeline or algorithm, I carry around where the data is coming from. 
This is not so easy to do in C++ or RTL, but it's trivial in Python. For lack of a better name, 
I call these *symbolic models*.

There are thus two additional models to my arsenal of tools:

* a reference symbolic model 
* a hardware symbolic model

These models are both written in Python and their outputs are compared against each other.

In this blog post, I'll go through an example case where I use such model.

# An Image Downscaler as Example Design

Let's design a hardware module that is easy enough to not spend too much time on it for
a blog post, but complex enough to illustrate the benefits of a symbolic model: an
image downscaler.

The core functionality is the following:

* it accepts an monochrome image with a maximum resolution of 7680x4320.
* it downscales the input image with a fixed ratio of 2 in both directions.
* it uses a 3x3 tap 2D filter kernel for downscaling.

The figure below shows how an image with a 12x8 resolution that gets filtered and
downsampled into a 6x4 resolution image. 

![2:1 downscaling with 3x3 filter kernel](/assets/symbolic_model/symbolic_model-downscaling3x3_no_tiles.drawio.svg)

Each square represents an input pixel, each hatched square an output pixel, and the 
arrows show how input pixels contribute to the input of the 3x3 filter for the output pixel.
For pixels that lay against the top or left border, the top and left pixels are repeated
upward and leftward so that the same 3x3 filter can be used.

If this downscaler is part of a streaming display pipeline that eventually sends pixels
to a monitor, there is not a lot of flexibility: pixels arrive in a left to right and top 
to bottom scan order and you need 2 line stores (memories) because there are 3 vertical filter taps.
Due to the 2:1 scaling ratio, the line stores can be half the horizontal resolution, 
but for an 8K resolution that's still 7680/2 ~ 4KB of RAM just for line buffering. In the
real world, you'd have to multiply that by 3 to support RGB instead of monochrome.
And since we need to read and write from this RAM every clock cycle, there's no chance of 
off-loading this storage to cheaper memory such as external DRAM.

However, we're lucky: the downscaler is part of a video decoder pipeline and those 
typically work with super blocks of 32x32 or 64x64 pixels that are scanned 
left-to-right and top-to-bottom. Within each super block, pixels are grouped in
tiles of 4x4 pixels that are scanned the same way.

In other words, there are 3 levels of left-to-right, top-to-bottom scan operations:

* the pixels inside each 4x4 pixel tile
* the pixel tiles inside each super block
* the super blocks inside each picture

[![Input image format](/assets/symbolic_model/symbolic_model-input_image.svg)](/assets/symbolic_model/symbolic_model-input_image.svg)

*(Click to enlarge)*

The output has the same organization of pixels, 4x4 pixel blocks and super blocks, but due to the
2:1 downsampling in both directions, the size of a super block is 32x32 instead of 64x64 pixels.

There are two major advantages to having the data flow organized this way: 

* the downscaler can operate on one super block at a time instead of the full image

    For pixels inside the super block, that reduces size of the *active* input image width from
    7680 to just 64 pixels. 

* as long as the filter kernel is less than 5 pixels high, only 1 line store is needed

    The line store contains a partial sum of multiple lines of pixels.

While the line store still needs to cover the full picture width when moving from one row of super blocks 
to the one below it, the bandwidth that is required to access the line store is but a 
fraction of the one befire: 1/64th to be exact. That opens up the opportunity to stream line 
store data in and out of external DRAM instead of keeping it in expensive on-chip RAMs.

But it's not all roses! There are some negative consequences as well:

* pixels from the super block above the current one must be fetched from DMA and stored in a local memory
* pixels at the bottom of the current super block must be sent to DMA
* the right-most column of pixels from the current super block are used in the next super block to
  when doing the 3x3 filter operation
* 4x4 size input tiles get downsampled to 2x2 size output tiles, but they must be sent
  out again as 4x4 tiles. This requires some kind of pixel tile merging operation.
 
While the RAM area savings are totally worth it, all this adds a significant amount of data 
management complexity.  This is the kind of problem where a symbolic micro-architecture model 
shines.

[![System block diagram](/assets/symbolic_model/symbolic_model-system_block_diagram.drawio.svg)](/assets/symbolic_model/symbolic_model-system_block_diagram.drawio.svg)

# The Reference Model

When modeling transformations that work at the picture level, it's convenient
to assume that there are no memory size constraints and that you can access all
pixels at all times no matter where they are located in the image. You don't
have to worry about how much RAM this would take on silicon: it's up to the designer of
the micro-architecture to figure out how to create an area efficient implementation.

This usually results in a huge simplification of the reference model, which is good
because as the source of truth you want to avoid any bugs in it.

For our downscaler, the reference model creates an array of output pixels where
each output pixel contains the coordinates of all the input pixels that are required
to calculate its value.

The pseudo code is someting like this:

```python
for y in range(OUTPUT_HEIGHT):
    for x in range(OUTPUT_WIDTH):
        get coordinates of input pixels for filter
        store coordinates at (x,y) of the output image
```

The reference model python code is not much more complicated. You can find the
code [here](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L36-L64). 

Instead of a 2-dimensional array, it uses a dictionary with the output pixel 
coordinates as key. This is a personal preference: I think `ref_output_pixels [ (x,y) ]` 
looks cleaner than `ref_output_pixels[y][x]` or `ref_output_pixels[x][y]`.

When the reference model data creation is complete, the `ref_output_pixels` array contains
values like this:

```python
(0,0) => [ Pixel(x=0, y=0), Pixel(x=0, y=0), Pixel(x=1, y=0), 
           Pixel(x=0, y=0), Pixel(x=0, y=0), Pixel(x=1, y=0), 
           Pixel(x=0, y=1), Pixel(x=0, y=1), Pixel(x=1, y=1) ]

(1,0) => [ Pixel(x=1, y=0), Pixel(x=2, y=0), Pixel(x=3, y=0), 
           Pixel(x=1, y=0), Pixel(x=2, y=0), Pixel(x=3, y=0), 
           Pixel(x=1, y=1), Pixel(x=2, y=1), Pixel(x=3, y=1) ]
...
(8,7) => [ Pixel(x=15, y=13), Pixel(x=16, y=13), Pixel(x=17, y=13), 
           Pixel(x=15, y=14), Pixel(x=16, y=14), Pixel(x=17, y=14), 
           Pixel(x=15, y=15), Pixel(x=16, y=15), Pixel(x=17, y=15) ]
...
```

The reference value of each output pixel is a list of input pixels that are needed
to calculate its value. *I do not care about the actual value of the pixels or the 
mathematical operation that is applied on these inputs*.

# The Micro-Architecture Model

The source code of the hardware symbolic model can be found 
[here](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L96).

It has the following main [data buffers and FIFOs](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L97-L111):

* an input stream, generated by [`gen_input_stream`](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L71),
  4x4 pixel tiles that are sent super block by super block and then tile by tile.
* an output stream of 4x4 pixel tiles with the downsampled image.
* a DMA FIFO, modelled with simple Python list in which the bottom pixels of a super block area 
  stored and later fetched when the super block of the next row needs the neighboring pixels
  above.
* buffers with above and left neighboring pixels that cover the width and height
  of a super block.
* an output merge FIFO is used to group a set to 4 2x2 downsampled pixels into a 4x4 tile
  of pixels

The model loops through the super blocks in scan order and then the tiles in scan order, 
and for each 4x4 tile it calculates a 2x2 output tiles.

```python
    for sy in range(nr of vertical super block):
        for sx in range(nr of horizontal super block):
            for tile_y in range(nr of vertical tiles in a superblock):
                for tile_x in range(nr of horizontal tiles in a superblock):
                    fetch 4x4 tile with input pixels
                    calculate 2x2 output pixels
                    merge 2x2 output pixels into 4x4 output tiles
                    data management
```

When we look at the inputs that are required to calculate the 4 output pixels for each tile of 16
input pixels, we get the following:

![Tile filter contributors](/assets/symbolic_model/symbolic_model-tile_filter_contributors.drawio.svg)

In addition to pixels from the tile itself, some output pixels also need input values from above, 
above-left and/or left neighbors. When switching from one super block to the next, buffers must be 
updated with neighboring pixels for the whole width and height of the super block. But instead of 
storing the values of individual pixels, we can store intermediate sums to reduce the number of values:

![Tile filter contributors optimized](/assets/symbolic_model/symbolic_model-tile_filter_contributors_2.drawio.svg)

At first sight, it looks like this reduces the number of values in the above and left neighbors buffers
by half, but that's only true for the above buffer. While the left neighbors can be reduced by half for 
the current tile, the bottom left pixel value is still needed to calculuate the above value for the 4x4 tiles of the
next row. So the size of the left buffer is not 1/2 of the size of the super block but 3/4.

![Filter inputs for current and future tiles](/assets/symbolic_model/symbolic_model-input_values_for_current_future_tiles.drawio.svg)

In the left figure above, the red rectangles contain the components needed for the top-left output pixel,
the green for the top-right output pixel etc. The right figure shows the partial sums that must be
calculated for the left and above neighbors for future 4x4 tiles.

These red, green, blue and purple rectangles have 
[direct corresponding sections in the code](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L196-L210).

```python
    p00 = (                      tile_above_pixels[0], 
            tile_left_pixels[0], input_tile[0], input_tile[1], 
                                 input_tile[4], input_tile[5] )

    p10 = (                      tile_above_pixels[1], 
            input_tile[ 1],      input_tile[ 2], input_tile[ 3] , 
            input_tile[ 5],      input_tile[ 6], input_tile[ 7] ) 

    p01 = (tile_left_pixels[1],  input_tile[ 4], input_tile[ 5] , 
                                 input_tile[ 8], input_tile[ 9] , 
                                 input_tile[12], input_tile[13] ) 

    p11 = ( input_tile[ 5],      input_tile[ 6], input_tile[ 7] , 
            input_tile[ 9],      input_tile[10], input_tile[11] , 
            input_tile[13],      input_tile[14], input_tile[15] ) 
```

For each tile, there's quite a bit of bookkeeping of context values, reading and writing to
buffers to keep everything going.

# Comparing the results

In traditional models, as soon as intermediate values are calculated, the original values can
be dropped. In the case of our example, with a filter where all coefficients are 1, the above
and left values intermediate values of the top-left output pixels are summed and stored as 18 and 11, 
and the original values of (3,9,6) and (5,6) aren't needed anymore. This and the fact the multiple
inputs might have the same numerical value is what makes traditional models often hard to debug.

![Intermediate values](/assets/symbolic_model/symbolic_model-intermediate values.drawio.svg)

This is not the case for symbolic models where all input values, the input pixel coordinates,
are carried along until the end. In our model, the intermediate results are not
removed from the final result. Here is the output result for output pixel (12,10):

```python
  ...
  (
    # Above neighbor intermediate sum
    (Pixel(x=23, y=19), Pixel(x=24, y=19), Pixel(x=25, y=19)),

    # Left neighbor intermediate sum
    (Pixel(x=23, y=20), Pixel(x=23, y=21)),

    # Values from the current tile
    Pixel(x=24, y=20),
    Pixel(x=25, y=20),
    Pixel(x=24, y=21),
    Pixel(x=25, y=21)
  ),
  ...
```

Keeping the intermediate results makes it easier to debug but to compare against the reference model, 
the data with nested lists must be 
[flattened](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L298-L307) 
into this:

```python
  ...
  (
    Pixel(x=23, y=19), 
    Pixel(x=24, y=19), 
    Pixel(x=25, y=19),
    Pixel(x=23, y=20), 
    Pixel(x=23, y=21),
    Pixel(x=24, y=20),
    Pixel(x=25, y=20),
    Pixel(x=24, y=21),
    Pixel(x=25, y=21)
  ),
  ...
```

But even that is not enough to compare: the reference value has the 3x3 input values
in a scan order that was destroyed due to using intermediate values so there's a final 
[sorting step](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L294-L296)
to restore the scan order:

```python
...
  (
    Pixel(x=23, y=19), Pixel(x=24, y=19), Pixel(x=25, y=19), 
    Pixel(x=23, y=20), Pixel(x=24, y=20), Pixel(x=25, y=20), 
    Pixel(x=23, y=21), Pixel(x=24, y=21), Pixel(x=25, y=21)
  )
```

Finally, we can go through all the output tiles of the hardware
model and [compare them](https://github.com/tomverbeure/symbolic_model/blob/2462720bbd0391e3015b044f3c70cb36ef4fd6b8/downscaler.py#L369)
against the tiles of the reference model.

If all goes well, the script should give the following:

```sh
> ./downscaler.py
PASS!
```

Any kind of bug will result in an error message like this one:

```
> ./downscaler.py
MISMATCH! sb(1,0) tile(0,0) (0,0) 1
ref:
[Pixel(x=7, y=0),
 Pixel(x=7, y=0),
 Pixel(x=8, y=0),
 Pixel(x=8, y=0),
 Pixel(x=9, y=0),
 Pixel(x=9, y=0),
 Pixel(x=7, y=1),
 Pixel(x=8, y=1),
 Pixel(x=9, y=1)]
hw:
[Pixel(x=7, y=0),
 Pixel(x=8, y=0),
 Pixel(x=8, y=0),
 Pixel(x=9, y=0),
 Pixel(x=9, y=0),
 Pixel(x=7, y=1),
 Pixel(x=8, y=1),
 Pixel(x=9, y=1),
 Pixel(x=7, y=4)]
```

# Conversion to Hardware

The difficulty of converting the Python micro-architectural model to a hardware implementation
model depends on the abstraction level of the hardware implementation language.

When using C++ and HLS, the effort can be trivial: some of my blocks have a thousand or
more lines of Python that can be converted entirely to C++ pretty much line by line. It can take
a few weeks to develop and debug the Python model yet getting the C++ model running only takes a 
day or two. If the Python model is fully debugged, the only issues encountered are typos made during
the conversion and signal precision mistakes.

The story is different when using RTL: with HLS, the synthesis-to-Verilog will convert *for* loops
to FSMs and take care of pipelining. When writing RTL directly, that tasks falls on you. You could
change the Python model and switch to FSMs there to make that step a bit easier. Either way,
having flushed out all the data management will allow you to focus on just the RTL specific
tasks while being confident that the core architecture is correct.

# Combining symbolic models with random input generation

The downscaler example is a fairly trivial unit with a predictable input data stream and a
simple algorithm. In a video encoder or decoder, instead of a scan-order stream of 4x4 tiles, the 
input is often a hierarchical coding tree with variable size coding units that are scanned
in quad-tree depth-first order.

![Super block with a coding tree](/assets/symbolic_model/symbolic_model-coding_tree.drawio.svg)

Dealing with this kind of data stream kicks up the complexity a whole lot. For designs like this,
the combination of a symbolic model and a random coding tree generator is a super power that will
hit corner case bugs with an efficiency that puts regular models to shame.

# Specification changes

The benefits of symbolic models don't stop with quickly finding corner case bugs. I've run in a
number of cases where the design requirements weren't fully understood at the time of implementation
and incorrect behavior was discovered long after the hardware model was implemented. By that time,
some of the implementation subtleties may have already been forgotten.

It's scary to make changes on a hardware design that has complex data management when corner case
bugs take thousands of regression simulations to uncover. If the symbolic model is the initial
source of truth, this is usually just not an issue: exhaustive tests can often be run in seconds and
once the changes pass there, you have confidence that the corresponding changes in the hardware model
source code are sound. 

# Things to experiment with...

**Generating hardware stimuli**

I haven't explored this yet, but it is possible to use a symbolic model to generate stimuli for the
hardware model. All it takes is to replace the symbolic input values (pixel coordinates) by the 
actual pixel values at that location and performing the right mathematical equations on the 
symbolic values.

**A joint symbolic/hardware model**

Having a Python symbolic model and a C++ HLS hardware model isn't a huge deal but there's still the
effort of converting one into the other. There is a way to have a unified symbolic/hardware model
by switching the data type of the input and output values from one that contains symbolic values to
one that contains the real values. If C++ is your HLS language, then this requires writing the
symbolic model in C++ instead of Python. You'd trade off the rapid interation time and conciseness
of Python against having only a single code base.

# Symbolic models are best for block or sub-block level modelling

Since symbolic models carry along the full history of calculated values, symbolic models aren't
very practical when modelling multiple larger blocks together: hierarchical lists with
tens or more input values create information overload. For this reason, I use symbolic models at
the individual block level or sometimes even sub-block level when dealing with particularly tricky
data management cases. My symbolic model script might contain multiple disjoint models that each
implement a sub-block of the same major block, without interacting with eachother.

# References

* [*symbolic_model* repo on GitHub](https://github.com/tomverbeure/symbolic_model/tree/main)

# Conclusion

Symbolic models in Python have been a major factor in boosting my design productivity and increasing
my confidence in a micro-architectural implementation.

If you need to architect and implement a hardware block with some tricky data management, give them a
try, and let me know how it went!



