---
layout: post
title: Asynchronous Sample Rate Conversion
date:  2021-02-13 00:00:00 -1000
categories:
---

* TOC
{:toc}


# References


**Educational Links**

* [Thread on DIY Audio](https://www.diyaudio.com/forums/digital-source/28814-asynchronous-sample-rate-conversion.html)

    * [Blog post about this](http://hifiduino.blogspot.com/2009/06/how-asynchronous-rate-conversion-works.html). Same author?

* [An Efficient Asynchronous Sampling-Rate Conversion Algorithm for Multi-Channel Audio Applications](https://dspconcepts.com/white-papers/efficient-asynchronous-sampling-rate-conversion-algorithm-multi-channel-audio), P. Beckmann

    Very readable paper. Gives a good overview of some techniques, then presents a solution that runs
    on a SHARC DSP, with performance numbers, MIPS required etc.

* [A Stereo Asynchronous Digital Sample-Rate Converter for Digital Audio](https://ieeexplore.ieee.org/document/280698), R. Adams

    Paper from 1994 that gets referenced quite a bit.

* [Programming Asynchronous Sample Rate Converters on ADSP-2136x SHARC Processors (EE-268)](https://www.analog.com/media/en/technical-documentation/application-notes/EE268v01.pdf)

    Uses figures that are pretty much a direct copy from the paper above, but in color. :-)

    Describes a DSP software implementation, but software isn't available as source code.

* [Digital Audio Resampling Home Page](https://ccrma.stanford.edu/~jos/resample/), Julius O. Smith

    Has tons of information, including a list with free resampling software. However, it primarily
    discussed synchronous sample rate conversion.

* [High Performance Real-time Software Asynchronous Sample Rate Converter Kernel](https://www.semanticscholar.org/paper/High-Performance-Real-time-Software-Asynchronous-Heeb/6b9e4440ff28326463f82766d54e17aef632ef08), T. Heeb

    *Need to review*

* [Tonmeister series on audio jitter](https://www.tonmeister.ca/wordpress/category/jitter/)

    *Blog posts are in reverse chronological order.*

    [Part 8.3](https://www.tonmeister.ca/wordpress/2018/08/30/jitter-part-8-3-sampling-rate-conversion/)talks about ASRC.
    It also has a number of interesting links about audio sampling jitter.

* [Asynchronous Sample Rate Converter for Digital Audio Amplifiers](https://www.semanticscholar.org/paper/Asynchronous-Sample-Rate-Converter-for-Digital-Midya-Roeckner/25b0e9e86e092563f3c6c9ae4f4fe553db29771d), P. Midya

    Another paper about an ASRC implementation, this time on an FPGA. Don't add a lot of new interesting things.

* [Resampling Filters](http://www.ee.ic.ac.uk/hp/staff/dmb/courses/DSPDF/01300_Resampling.pdf)

    General course on resampling. Includes things like polynomial approximation. Doesn't specifically 
    deal with ASRC, but interesting.

**Silicon**

* [TI SRC4382](https://www.ti.com/product/SRC4382)

    * THD+N: -125dB
    * Dynamic range: 128dB
    * Sample rates: up to 216kHz
    * $11.75

* [TI SRC4192](https://www.ti.com/product/SRC4192)

    * THD+N: -140dB
    * Dynamic range: 144dB
    * Sample rates: up to 212kHz
    * Up to 24 bits
    * $12.2


* [AD1895](https://www.analog.com/en/products/ad1895.html#product-overview)/[AD1896](https://www.analog.com/en/products/ad1896.html#product-overview)

    * THD+N: -122dB/-133dB resp.
    * Dynamic range: 142dB 
    * Up to 24 bits
    * $10/$21

    The "ASRC Functional Overview - Theory of Operation" section of the datasheet is excellent.

* [Cirrus Logic CS8421](https://www.cirrus.com/products/cs8421/)

    * THD+N: -140dB
    * Dynamic range: 175dB
    * Sample rates: up to 1921kHz
    * Up to 32 bits
    * $11.45

**SNR Calculation**

* [Digital Audio Jitter Fundamentals](https://www.audiosciencereview.com/forum/index.php?threads/digital-audio-jitter-fundamentals-part-2.1926/)

    Shows impact of jitter on SNR. Many graphs.

