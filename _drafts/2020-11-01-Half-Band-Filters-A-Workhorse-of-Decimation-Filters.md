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
[PDM](https://en.wikipedia.org/wiki/Pulse-density_modulation) microphone into standard 
[PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation) samples. 
Check out the the [References](#references) section below for the other installments.

Earlier, I already discussed [how to design generic FIR filters](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html).
In this installment, I impose some restrictions on the filter, which makes them less generic, but
we get something very valuable in return: an almost 50% reduction in the number of multiplications!

*The plots below were all generated with Numeric Python scripts. You can find the code 
[here](https://github.com/tomverbeure/pdm/tree/master/modeling/halfband).*

# What is a Half-Band Filter?

According to [Wikipedia](https://en.wikipedia.org/wiki/Half-band_filter),
"a half-band filter is a low-pass filter that reduces the maximum bandwidth 
of sampled data by a factor of 2 (one octave)."

When we start out with a sample rate *Fs*, the bandwidth of that signal goes from
0 to *Fs/2*. A half-band filter is used to reduce the bandwidth to *Fs/4*.

By itself, this is nothing special: you could do that with a generic FIR filter.

But something very interesting happens when you make the magnitude frequency response 
of the filter symmetric both along the frequency axis and along the magnitude response axis.

![Half Band Symmetry](/assets/pdm/halfband/halfband-half_band_symmetry.svg)

In this case, **the coefficient of every other filter tap, except for the 
center coefficient, becomes zero**. Like most FIR filters, coefficients will be
symmetric around the center coefficent as well. And the center coefficient has a value
of 0.5.

Here's an example of a some random half-band filter: 

![Half Band Example](/assets/pdm/halfband/half_band_example.svg)

You can see how everything in the linear(!) magnitude response graph is perfectly
symmetric around the point at (0.25, 0.5): the size of the pass band and stop band.
The height of the ripple in the pass band and stop band. The number of zero crossings
through 1.0 and 0.0 in the pass band and stop band, etc.

And except for the center coefficient, all odd coefficients are indeed 0.

Half-band filters are extremely useful in decimation filters. But before getting into that,
let's first see how to design them.

# Designing a Half-Band FIR filter with pyFDA

You can easily design your own half-band filters with [pyFDA](https://github.com/chipmuenk/pyfda). 

When I wrote about pyFDA in tool in a previous [blog post](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
about how to design a low pass FIR filter, I specified a desired pass band and stop band attenuation, let pyFDA 
figure out all the rest, and had it come up with the order of the filter and associated tap
coefficients. What happens behind the scenes in that case is the following: pyFDA uses the standard [Parks-McClellan filter
design algorithm](https://en.wikipedia.org/wiki/Parks%E2%80%93McClellan_filter_design_algorithm) which is
a variation of the [Remez exchange algorithm](https://en.wikipedia.org/wiki/Remez_algorithm),
an iterative way to find approximations of functions.

The [Remez algorithm as implemented in NumPy](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.remez.html)
has a list of frequency bands with associated gains as parameter, but also a weighing factor. This
weighing factor determines the relative priority of frequency bands during coefficient
optimization. The weight factors are directly related to the final ripple (and thus the
attenuation factor) of the each frequency band.

In the case of half-band filter, the ripple for the pass-band and the stop-band **has** to be the same. 
Consequently, the weighting factors must the same as well. The end result is that there is really only 1
factor to play with if we want a filter performance: the order of the filter.

In pyFDA, we can now calculate a half-band filter as follows:

![pyFDA half-band parameters](/assets/pdm/halfband/halfband-pyFDA_parameters.png)

* Enter the pass band and stop band frequencies.

    Make sure that the width of both bands are the same.

    For example, when the frequency range goes from 0 to 1/2, and you
    have a pass band that ends at 0.2, the stop band must start at 0.3 (= 0.5 - 0.2).

* Deselect the "Order: Minimum" option.

    As a result of this, we can now manually enter N, the order of the filter, and the
    weights of the pass band (Wpb and Wsb). We can not enter the attenuation parameters
    (Apb and Asb) any more.

* Enter the desired filter order N

    Choose a number that's a multiple of 2, but not a multiple of 4.

    Let's start with a value of 10, which corresponds to 11 coefficients.

* Enter a value of 1 for both Wpb and Wsb, the ripple weigths for pass and stop band

If you didn't change the default settings, you'll see in the Magnitude Frequency
Response graph: 

![pyFDA magnitude response graph - dB](/assets/pdm/halfband/halfband-pyFDA_dB_response.png)


If you're wondering why this doesn't look symmetric at all, change the units from
*dB* to *V*, you'll be greeted with this:

![pyFDA magnitude response graph - V](/assets/pdm/halfband/halfband-pyFDA_linear_response.png)

One again, the ripple in the pass band is identical to the ripple in the stop band, 
after taking into account that the negative ripple in the stop band comes out as
positive because the magnitude response graph uses absolute values.

Click on `h[n]` tab in the right pane for the filter coefficients:

![pyFDA impluse response](/assets/pdm/halfband/halfband-pyFDA_coefficients_graph.png)

And, again, except for the center tap, 50% of the coefficients are 0.

Or are they? When you click select the `b,a` tab in the left pane, you get the coefficients
listed in floating point format:

![pyFDA coefficients](/assets/pdm/halfband/halfband-pyFDA_coefficients_numbers.png)

The coefficients are very close to but not quite 0. You can easily fix that by just clamping
these coefficients to 0, but that does feel right, does it? For high order half-band filters 
with a high attenuation, this will almost certainly change the performance characteristics in
some subtle way.

There must be a better way to go about this! 

# Designing Perfect-Zero Half-Band Filters with a Trick

Today, the Parks-McClellan/Remez algorithm to calculate FIR coefficients is fast enough even
for very high order FIR filters. Even when implemented in Python.

This was definitely not that case in 1987. Back then, Vaidyanathan and Nguyen
observed in [A "Trick" for the Design of FIR Half-Band Filters](https://authors.library.caltech.edu/5892/1/VAIieeetcs87a.pdf)
that you can reduce the number of coefficients to calculate by (almost) 50% by transforming 
the half-band filter specification into a different FIR filter.

You'll have to read the paper if you want to understand the details (it's not super complicated), but
the procedure is very simple.

Give a half-band filter specification with the following parameters:

* Filter order: *N* (and thus N+1 taps)
    * N must be a multiple of 2 but not a multiple of 4
* Sample rate: *Fs*
* Pass band: from 0 to *Fpb*
* Stop band: from *Fs*/2-*Fpb* to *Fs*/2

Design a regular FIR filter with these parameters:

* Filter order: *N*/2
* Sample rate: *Fs*
* Pass band: from * to *2 x Fpb*
* Stop band: from *Fs*/2 to *Fs*/2

The previous pyFDA example now has N halved from 10 to 5, Fpb doubled from 0.2 to 0.4, and Fsb is
fixed at 0.4:

![pyFDA coefficients](/assets/pdm/halfband/halfband-pyFDA_with_a_trick.png)

The stop band is gone now, but the pass band behavior of the magnitude frequence response graph has the same
shape at the previous one.

And here are the coefficients:

![pyFDA coefficients](/assets/pdm/halfband/halfband-pyFDA_with_a_trick_coefficients.png)

There are no zeros anymore, and values are exactly double of the non-zero coeffients of the 
values that were calculated without the trick! E.g. coefficient zero is 0.1075 vs 0.05372
earlier.

All that's left now to get the half band filter coefficients is to divide the number above by half, 
insert a zero between each coefficient, except for the center coefficient which needs to be set to 0.5.

# Half-Band Filter Design with NumPy

Just like generic FIR filters, a filter design script over a GUI. The code uses the trick
and is straightforward:

```python
def half_band_calc_filter(Fs, Fpb, N):
    assert Fpb < Fs/4, "A half-band filter requires that Fpb is smaller than Fs/4"
    assert N % 2 == 0, "Filter order N must be a multiple of 2"
    assert N % 4 != 0, "Filter order N must not be a multiple of 4"

    g = signal.remez(
            N//2+1,
            [0., 2*Fpb/Fs, .5, .5],         # The Trick
            [1, 0],
            [1, 1]
            )

    # Insert zeros
    h = [item for sublist in zip(g, zeros) for item in sublist][:-1]
    # Half coefficients
    h = np.array(h)/2
    # Set center tap
    h[N//2] = 0.5
```

To find the minimal filter order that satisfies both pass band and stop band attenuation,
just increase the filter order until that condition is valid:

```python
def half_band_find_optimal_N(Fs, Fpb, Apb, Asb, Nmin = 2, Nmax = 1000):
    for N in range(Nmin, Nmax, 4):
        print("Trying N=%d" % N)
    github
        (h, w, H, Rpb, Rsb, Hpb_min, Hpb_max, Hsb_max) = half_band_calc_filter(Fs, Fpb, N)
        if -dB20(Rpb) <= Apb and -dB20(Rsb) >= Asb:
            return N

    return None
```

    github


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

    I need to study this...

**Code**

* [Code to generate the figures in this blog post](https://github.com/tomverbeure/pdm/tree/master/modeling/halfband)

**Decimation**

* [Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf)

    Paper that discusses how to size cascaded filter to optimized for FIR filter complexity.

**Implementation**

* [Digital Filter Structures](http://www.ee.ic.ac.uk/hp/staff/dmb/courses/DSPDF/01000_Structures.pdf)


