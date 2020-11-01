---
layout: post
title: Half-Band Filters, a Workhorse of Decimation Filters
date:  2020-11-01 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Half-band 


If you've read my previous three posts in this series, you know that I'm improving my general DSP
knowledge by applying it to a concrete example of taking in the single-bit data stream of
a [PDM](https://en.wikipedia.org/wiki/Pulse-density_modulation) microphone and converting it 
into standard [PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation) samples.

The application itself is only a means to an end. Most important is understanding the why and 
how of every design decision along the way: if there's a filter with a 70dB stop band
attenuation at 10kHz, I want to know the justification for that.

After diving into [CIC filters](/2020/09/30/Moving-Average-and-CIC-Filters.html), 
the characteristics of the 
[sigma-delta generated PDM signal of a MEMS microphone](/2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html), 
and [learning how to come up with FIR filter coefficients](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html),
the time has come to start building up the filter architecture.

And for that, we need to come up with a design specification!


# References

**My Blog Posts in this Series**

* [An Intuitive Look at Moving Average and CIC Filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
* [PDM Microphones and Sigma-Delta A/D Conversion](http://localhost:4000/2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html)
* [Designing Generic FIR Filters with pyFDA and NumPy](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
* [From Microphone Datasheet to Filter Design Specification](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html)

**Filter Design**

* [Halfband Filter Design with Python/SciPy](https://www.dsprelated.com/showcode/270.php)

    Simple example that shows how to calculate half-band filter coefficients with NumPy using the Remez
    algorithm and with a windowed sinc filter. However, it doesn't discuss how to calculate the weights
    of the Remez algorithm.

* [Multiplier-Free Half-Band Filters](https://www.cs.tut.fi/~ts/sldsp_part2_identical_subfilters_halfband.pdf)

    Excellent discussion about half band filters, ways to design them, and how to design them without
    multipliers. Also has an extensive example on how to convert from PDM to PCM with a CIC filter followed
    by 4 half band filters.

    The [website of this professor](https://www.cs.tut.fi/~ts/) has a lot of course notes online. They are 
    all worth reading.

* [Efficient Multirate Realization for Narrow Transition-Band FIR Filters](https://www.cs.tut.fi/~ts/Part4_Tor_Tapio1.pdf)

    XXX Need to study this...

**Decimation**

* [Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf)

    Paper that discusses how to size cascaded filter to optimized for FIR filter complexity.

* [Seamlessly Interfacing MEMS Microphones with Blackfin Processors](https://www.analog.com/media/en/technical-documentation/application-notes/EE-350rev1.pdf)

    Analog Devices application note. C code can be found[here](https://www.analog.com/media/en/technical-documentation/application-notes/EE350v01.zip)

* [The size of an FIR filter for PDM-PCM conversion](https://www.dsprelated.com/thread/11806/the-size-of-an-fir-filter-for-pdm-pcm-conversion)

    Discussion about PDM to PCM conversion on DSPrelated.com.

* XMOS Microphone array library

    https://www.xmos.ai/download/lib_mic_array-%5buserguide%5d(3.0.1rc1).pdf

    Lots of technical info about PDM to PCM decimation.

**Sensitivity**

* [Sensitivity Analysis and Architectural Comparison of Narrow-band Sharp-transition Digital Filters](https://core.ac.uk/download/pdf/10195225.pdf)

    Thesis about different filter structures for IIR filters and the impact of fixed precision, quantization etc.

**Implementation**

* [Digital Filter Structures](http://www.ee.ic.ac.uk/hp/staff/dmb/courses/DSPDF/01000_Structures.pdf)

**Microphones**

* [Understanding Microphone Sensitivity](https://www.analog.com/en/analog-dialogue/articles/understanding-microphone-sensitivity.html)

* [Digital encoding requirements for high dynamic range microphones](https://www.infineon.com/dgdl/Infineon-AN556%20Digital%20encoding%20requirements%20for%20high%20dynamic%20range%20microphones-AN-v01_00-EN.pdf?fileId=5546d4626102d35a01612d1e33876ad8)

* [Microphone Specifications Explained](https://invensense.tdk.com/wp-content/uploads/2015/02/AN-1112-v1.1.pdf)


