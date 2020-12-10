---
layout: post
title: Half-Band Filters, a Workhorse of Decimation Filters
date:  2020-11-01 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

This is the 5th part in my ongoing series about converting the single-bit data stream of a 
[PDM](https://en.wikipedia.org/wiki/Pulse-density_modulation) microphone and converting it 
into standard [PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation) samples. Check out 
the the [References](#references) section below for the other installments.

Earlier, I already discussed [how to design generic FIR filters](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html).

In this installment, I impose some restrictions on the filter, which makes it less generic, but
we get something very valuable in return: an almost 50% reduction in the number of multiplications!

# What is a Half-Band Filter?

According to [Wikipedia](https://en.wikipedia.org/wiki/Half-band_filter),
"a half-band filter is a low-pass filter that reduces the maximum bandwidth 
of sampled data by a factor of 2 (one octave)."

When we start out with a sample rate *Fs*, the bandwidth of that signal goes from
0 to *Fs/2*. A half-band filter is used to reduce the bandwidth to *Fs/4*.

By itself, this is nothing special: you could do that with a generic FIR filter.

But something very interesting happens when you make the magnitude frequency response 
of the filter symmetric both along the frequency axis and the magnitude response axis.


![Half Band Symmetry](/assets/pdm/halfband/halfband-half_band_symmetry.svg)

In this case, **the coefficient of every other filter tap, except for the 
center coefficient, becomes zero**. Like most FIR filters, coefficients will be
symmetric around the center coefficent as well. And the center coefficient has a value
of 0.5.

To satisfy this symmetry condition, width of the pass band must be the same as the width of the stop band,
and the ripple in the pass and stop band must be the same too. An automatic consequence of
these requirements is that the transition band will be symmetric around 1/4th of the sample rate,
and the value of the magnitude response graph at this frequency will be exactly 0.5 (assuming
the passband magnitude is 1.)

# Designing a Half-Band FIR filter with pyFDA

You can easily check this out with [pyFDA](https://github.com/chipmuenk/pyfda). 

When I wrote about pyFDA in tool in a previous [blog post](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
to design a low pass FIR filter, I specified a desired pass band and stop band attenuation, let pyFDA 
figure out all the rest, and had it come up with the order of the filter and associated tap
coefficients.

What happens behind the scenes was the following: pyFDA uses the standard [Parks-McClellan filter
design algorithm](https://en.wikipedia.org/wiki/Parks%E2%80%93McClellan_filter_design_algorithm) which is, 
in turn, a variation of the [Remez exchange algorithm](https://en.wikipedia.org/wiki/Remez_algorithm),
an iterative way to find approximations of functions.

The [Remez algorithm as implemented in NumPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.remez.html)
has a list of frequency bands with associated gains as parameter, but also a weighing factor. This
weighing factor determines the relative priority of frequency bands during coefficient
optimization. The weight factors are directly related to the final ripple (and thus the
attenuation factor) of the each frequency band.

In the case of half-band filter, the ripple for the pass-band and the stop-band is the same. And thus
the weighting factor is the same as well. The end result is that there is really only 1
factor to play with if we want a filter performance: the order of the filter.

In pyFDA, we can now calculate a half-band filter as follows:

* Enter the pass band and stop band frequencies.

    Make sure that the width of both bands are the same.

    For example, when the frequency using is from 0 to 1/2, and you
    have a pass band of 0.2, the stop band must be 0.3 (=0.5 - 0.2).

* Deselect the "Order: Minimum" option.

    As a result of this, we can now manually enter N, the order of the filter, and the
    weights of the pass band (Wpb and Wsb). We can not enter the attenuation parameters
    (Apb and Asb) any more.

* Enter the desired filter order N

    Choose a number that's a multiple of 2, but not a multiple of 4.

    Let's start with a value of 10.

* Enter a value of 1 for both Wpb and Wsb.

The result will be as follows:

![pyFDA half-band parameters](/assets/pdm/halfband/halfband-pyFDA_parameters.png)

If you didn't change the default settings, you'll see in the Magnitude Frequency
Response graph: 

![pyFDA magnitude response graph - dB](/assets/pdm/halfband/halfband-pyFDA_dB_response.png)


If you're wondering why this doesn't look symmetric at all, change the units from
*dB* to *V*, you'll be greeted with this:

![pyFDA magnitude response graph - V](/assets/pdm/halfband/halfband-pyFDA_linear_response.png)

Notice how the ripple in the pass band is identical to the ripple in the stop band, 
after taking into account that the negative ripple in the stop band comes out as
positive because the magnitude response graph uses absolute values.

Click on `h[n]` tab in the right pane for the filter coefficients:

![pyFDA impluse response](/assets/pdm/halfband/halfband-pyFDA_coefficients_graph.png)

As promised, except for the center tap, 50% of the coefficients are 0. And the center tap is 0.5.

Or are they? When you click select the `b,a` tab in the left pane, you get the coefficients
listed in floating point format:

![pyFDA coefficients](/assets/pdm/halfband/halfband-pyFDA_coefficients_numbers.png)

While they are close to but not quite 0. You can easily fix that by just clamping
these coefficients to 0, but does that feel right to you? For half-band filters of a high order
with a high attenuation, this will almost certainly change the performance characteristice in
some subtle way.

There must be a better way to go about this!

# References

**My Blog Posts in this Series**

* [An Intuitive Look at Moving Average and CIC Filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
* [PDM Microphones and Sigma-Delta A/D Conversion](http://localhost:4000/2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html)
* [Designing Generic FIR Filters with pyFDA and NumPy](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
* [From Microphone Datasheet to Filter Design Specification](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html)

**Filter Design**

* [A 'trick' for the design of FIR half-band filters](https://authors.library.caltech.edu/5892/1/VAIieeetcs87a.pdf)

    Key paper that describes how to transform the parameters of a half-band filter to a different FIR filter
    with 1/2 of the filter taps, use the Remez algorithms to calculate those coefficents, and then use them
    for the half-band filter.

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


