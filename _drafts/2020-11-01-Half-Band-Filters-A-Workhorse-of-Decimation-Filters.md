---
layout: post
title: Half-Band Filters, a Workhorse of Decimation Filters
date:  2020-11-01 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The 5th part in my ongoing series about converting the single-bit data stream of a 
[PDM](https://en.wikipedia.org/wiki/Pulse-density_modulation) microphone and converting it 
into standard [PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation) samples. (See below
in the [References](#references) section for the other installments.)

Earlier, I already discussed [how to design generic FIR filters](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html).

Today, I want to impose some restrictions on the filter, which makes it less generic, but
we get something very valuable in return: an almost 50% reduction in the number of multiplications!

# What is a Half-Band Filter?

According to [Wikipedia](https://en.wikipedia.org/wiki/Half-band_filter),
"a half-band filter is a low-pass filter that reduces the maximum bandwidth 
of sampled data by a factor of 2 (one octave)."

When we start out with a sample rate *Fs*, the bandwidth of that signal goes from
0 to *Fs/2*. A half-band filter is used to reduce the bandwidth to *Fs/4*.

By itself, this is nothing special: you could do that with a generic FIR filter.

But something very interesting happens when you make the magnitude frequency response 
of the filter symmetric around the *Fs/4* frequency, both in terms of where the
pass band ends and the stop band starts, and in terms of the ripple in the pass band
and stop band: in this case, *the coefficient of every other filter tap, except for the 
center coefficient, becomes zero*.

In other words, for an FIR filter with n taps (where n is odd, and 




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


