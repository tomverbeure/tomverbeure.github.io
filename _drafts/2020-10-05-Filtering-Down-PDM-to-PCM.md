---
layout: post
title: Filtering Down PDM to PCM
date:  2020-10-19 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

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

# Decimation is a Divide and Conquer Problem

All other things equal (sampling rate, pass band ripple, stop band attenuation), the number of
filter taps depends on the size of the transition band compared to sample rate.

In the example above, the sample rate is 2304 kHz and the transition band is just 4kHz, a ratio
of 576!

If we reduce the sample rate by, say, 6 to 384 and keep everything else the same, the number of taps
goes rougly down by 6 as well:

![Fpdm divided by 6 Frequency Response](/assets/pdm/pdm2pcm/fpdm_div6.svg)

Reducing the number of taps from 2216 down to 370 taps, gives:

```
48000 * 370  = 18M muls/s            (6x decimation - from 384 to 48kHz)
```

But that's not a fair comparison, because to be able use that filter, we first need to
decimate the original signal from its initial sample rate of 2304kHz to 384kHz.

If we do this in the most naive way possible like any other decimation filter, we create a 
filter that doesn't touch the pass band and the transition band of the final result, and that 
filters away everything above 240kHz: 480kHz/2. 

This guarantees that none of the frequencies above 240kHz will alias into the range of 0 to 10kHz 
after decimation.

Number of taps required? 18!

![Fpdm to Fpdm/6 - Frequency Response](/assets/pdm/pdm2pcm/fpdm_to_fpdm_div6.svg)

Total number of multiplications:

```
384,000 *  21 =  8M             (6x decimation - from 2400 to 384 kHz)
 48,000 * 370 = 18M             (8x decimation - from  384 to  48 kHz)
-----------------------------------
                26M multiplications/s
```

By splitting up the dumb initial filter into 2 filters, we've reduced the number of multiplications from
106M downto 26M, a factor of 4! 

In this case, I randomly choose to split 48x decimator into a 6x and an 8x decimator, but
I could have chosen to split it up in a 12x followed by a 4x decimatior:


```
192,000 *  52 = 10M             (12x decimation - from 2400 to 192 kHz)
 48,000 * 186 = 23M             ( 4x decimation - from  192 to  48 kHz)
-----------------------------------
                33M multiplications/s
```

Or a 3x followed by a 16x decimator:

```
768,000 *   9 =  7M             ( 3x decimation - from 2400 to 768 kHz)
 48,000 * 740 = 35M             (16x decimation - from  768 to  48 kHz)
-----------------------------------
                42M multiplications/s
```

Or 8x followed by 6x:

```
288,000 *  29 =  8M             ( 8x decimation - from 2400 to 288 kHz)
 48,000 * 277 = 13M             ( 6x decimation - from  288 to  48 kHz)
-----------------------------------
                21M multiplications/s
```

Starting from 106M, we're now more than 5 times better!

But wait, there's more!

What if we split the 8x/6x filter into 2x/4x/6x? Or even 2x/2x/2x/2x/3x?

There must be some optimal configuration!

Yes, of course, but before we go down that road, we first need to make some significant general 
optimizations. 

# Optimal Pass Band / Stop Band Limits for Decimators

As I mentioned earlier, when you design a single filter for a decimator, it's a simple matter
of entering the number of the pass band and stop band parameters and let your filter tool
do its magic.

For a filter with decimation ratio *n*, the pass band and the stop band frequency must be smaller
than the *Fsample/2/n*, where *Fsample* is the original sample rate.

In this section, we'll assume the following parameters:

* Incoming sample rate: 288kHz
* Valid signal bandwidth: 0 to 10kHz
* Outgoing sample rate: 48kHz
* Desired pass band: 0 to 6kHz
* Desired transition band: 6kHz to 10kHz
* Desired stop band: 10kHz to 24kHz

The ratio of incoming and outoing sample rate is 6, so we need a 6x decimating filter.

The fat black line below shows the frequency response if we use a single filter:

![Direct 6x Decimation Filter](/assets/pdm/pdm2pcm/pdm2pcm-div6_decimation_filter.svg)

We already saw earlier that 2 less aggressive filters result in a lower number of taps (and thus
multiplications) than 1 more aggressive filter. In this particular example, that means we can
either decimate by 2x first and 3x after that, or the other way around.

The figure below shows the two paths:

![Cascaded Decimation Steps](/assets/pdm/pdm2pcm/pdm2pcm-cascaded_decimation.svg)

There are 3 major things of note:

1. Naive vs smart filtering in the first stage 

    If we treated the first decimation stage as any other decimation filter, we'd put the
    stop band at end of *Fsample/2/n* to avoid any kind of aliasing of the upper
    frequencies into the remaining frequency band.

    But that is too aggressive!

    What we can do instead is start the stop band of the first filter at *(Fsample/n - Fsb)*.

    This expands the transition band by the area marked with the green rectangle and makes
    the first stage decimation filter considerably less steep. This is especially true for
    a 2x decimation ratio: in our specific example, between the naive and the smart filter,
    the transition band doubles from 62 (=72-10) to 124kHz (=144-10-10).

    A part of the upper frequencies will now alias into the lower frequency range, but we
    have a second filter stage to clean that up for us.

1. pass band frequency of the output signal is of no importance until the last filter

    The goal of the inital filter stages is to reduce the sample rate but prevent upper range
    frequencies from aliasing into the real signal. In our example, the final signal will
    have a transition band bewteen 6 and 10 kHz, but that doesn't mean that it's fine for 
    other signals to corrupt the original signal in the range.

    That's why the initial decimation filter uses 10kHz as the end of the pass band, not 6kHz.

1. pass band/stop band symmetry for the first stage 2x decimation case

    An interesting aspect is that the frequency response of the 2x decimation filter shows a 
    point symmetry around the *Fsample/4* axis:

    ![2x Decimation Symmetry](/assets/pdm/pdm2pcm/pdm2pcm-half_band_symmetry.svg)

    With some additional ripple constraints, this becomes a so-called half band filter.
    Half band filters have the interesting property that every other filter tap, except for the
    center tap, has a value of zero.

    This reduces the number of multiplications for a half band filter almost by half, which
    makes 2x decimation filters computationally an amazing deal..

# Passband Ripple and Stop Band Attenuation for Cascaded Filters

We're shooting for an overall pass band ripple of 0.1dB and a stop band attenuation of 89dB. 

When there's only 1 filter, meeting that goal is a matter of specifying that as a filter design parameter.

But what when multiple filters are cascaded?

In their 1975 paper 
["Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf),
Crochiere and Rabiner write the following:

> As it is desired that the overall pass band ripple for the composite of K stages be maintained 
> within *(1+-delta)* it is necesary to require more severe frequency constraints on the individual filters
> in the cascade. A convenient choice which will satisfy this requirement is to specify the pass band
> ripple constraints for each stage *i* to be within *(1+delta/K)*.


In other words: if we split the filter into 3 stages, they suggest to split the joint passband ripple of 0.1dB into
3 smaller pass band ripples.

``` 
    Ripple_single_db = 0.1
    Ripple_single = 10^(0.1/20)
    Ripple_div3 = ((Ripple_single-1) / 3)+1
    Ripple_div3_db = 20*log10(((Ripple_single-1) / 3)+1)
    Ripple_div3_db = 20*log10(((1.0116-1) / 3)+1)
    Ripple_div3_db = 0.033dB
```

(Note that close to 1, *20 * log10(x)* ~ *x-1*. Since pass band ripple is a deviation around 1, we can simply
divide the dB number without having to convert from dB to linear and back.)

Now for the stop band. From the same paper:

> In the stop band the ripple constraint for the composite filter must be *delta* and this
> constraint must be imposed on each of the individual low-pass filter as well, in order to suppress
> the effects of aliasing.

This is much easier: we calculated a stop band attenuation of 89dB. We have to use the same
attenuation for each filter in the cascade.


# Major Sample Rate Reduction with a CIC Filter

Earlier, I wrote about [CIC filters](/2020/09/30/Moving-Average-and-CIC-Filters.html) in preparation 
of this blog post.

CIC filters make it possible to reduce the amount of hardware to decimate a signal by a large
factor with next to no resources: no multipliers, and only a handful of register and adders.

The only price to pay is less than ideal behavior in the pass band, and a terrible stop band behavior
when used as a stand-alone filter, but that's something that can be fixed by having additional stages.

And that's exactly what we're doing here in our divide-and-conquer approach.

Here's the plan: we use a factor 16 CIC decimation filter to bring the sample rate
down from 3072 kHz to 192 kHz. 16x is a good compromise: it's a significant reduction,
yet the pass band attenuation at 14kHz is only XXXX.

If we then use the monolitic approach to decimate by a factor of 4 to end up with a 48kHz
output rate, we'd need 57 taps.

```
    48,000 * 57 = 2.7M multiplications
```

We can do better by splitting up the 4x decimator into 2 2x decimators:

* 192 -> 96: 18 taps
*  96 -> 48: 28 taps

```
     96,000 * 18  = 1.7M multiplications
     48,000 * 28  = 1.3M multiplications
   --------------------------------------
                    3.0M multiplications total

```

Apparently not! There seems to be some kind of cross-over point below which there
isn't a benefit in splitting up.

Still, we went from 104M to just 2.7M multiplications, a 38x improvement!

Can we do better?

# Stop Band Optimization

So far, the stop band of the intermediate decimation filter has been suboptimal: we
simply put it at 1/4th of the input rate, because that's what you do for a monolithic
decimation filter.

But it's not optimal in a divide an conquer configuration!

When we decimate from 192 to 96, it's overkill to put the stop band at 48kHz: we can
put the stop band at (96-20) = 76 kHz instead!

Yes, the frequency range from 48kHz to 76kHz will now alias onto 20kHz to 48kHz range,
but who cares? Nobody can hear anything above 20kHz anyway, and we have another filter
comping up to clean things up in the next decimation step!

With this new stop band constraint, there are only 11 filter taps instead of the earlier
18, for a total of:


```
     96,000 * 10  = 1.1M multiplications
     48,000 * 28  = 1.3M multiplications
   --------------------------------------
                    2.3M multiplications total

```

# Exploiting Filter Symmetry

For audio applications, linear phase behavior is important: the human ear is able to detect
phase differences in otherwise similar signals.

An FIR filter with linear phase behavior must have symmetry in its filter coefficients. And
all the filters we've designed so far have exactly that.

Because of this symmetry, each filter coefficient (except for the center one) will appear
twice, mirrored around the center tap. By adding the input samples that use the same filter coefficient
before doing the multiplication, we can reduce the number of multiplications by half!

Instead of 57 multiplications, we're now at 1+(56/2) = 29 multiplications per output sample.

# Best Case Low Pass Filtering

It should be abundantly clear now that we need that low pass filter before we can decimate to
a lower sample rate.

Let's use the following parameters:

* Original sample rate: 3.072 MHz
* Oversample rate factor: 64
* Desired sample rate: 48 kHz
* Original signal bandwidth: 20 kHz
* Desired pass band: 0 dB
* Desired stop band: 96 dB

I chose 96 dB because that's the theoretical maximum SNR for 16-bit audio. Most PDM microphones only
have an SNR in the low sixties, so this is overly aggressive, but let's just see what we can do.

The transition from pass band to stop band will start at 20 kHz. And if we look at the graph for
a 64x oversampling, 4th order sigma-delta convertor, we see that the noise goes above 96 dB 

Since the noise starts going up immediately above 24 kHz (=48/2), we have 4 kHz to construct a filter
that goes from a pass band to the stop band. 

# References

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

**Microphones**

* [Understanding Microphone Sensitivity](https://www.analog.com/en/analog-dialogue/articles/understanding-microphone-sensitivity.html)

* [Digital encoding requirements for high dynamic range microphones](https://www.infineon.com/dgdl/Infineon-AN556%20Digital%20encoding%20requirements%20for%20high%20dynamic%20range%20microphones-AN-v01_00-EN.pdf?fileId=5546d4626102d35a01612d1e33876ad8)

* [Microphone Specifications Explained](https://invensense.tdk.com/wp-content/uploads/2015/02/AN-1112-v1.1.pdf)


