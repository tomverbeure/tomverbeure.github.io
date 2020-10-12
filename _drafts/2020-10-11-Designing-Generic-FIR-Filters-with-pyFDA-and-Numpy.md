---
layout: post
title: Designing Generic FIR Filters with pyFDA and Numpy
date:  2020-10-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In [my previous blog post](2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html), I promised
that it was about time to start designing some real filters. Since 
[infinite response (IIR)](https://en.wikipedia.org/wiki/Infinite_impulse_response) filters are 
a bit too complicated still, and sometimes not suitable for audio processing due to non-linear phase
behavior, I implicitly meant 
[finite impulse response filters](2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html).
They are much easier to understand, and generally behave better, but they also require
a lot more calculation power to obtain similar ripple and attenuation results than IIR filters.

There are many resources on the web that will discuss the theoretical aspects about this or that
filter, but fully worked out examples with full code are much harder to find. 

In this blog post, I will discuss the tools that I've been using to evaluate and design filters: 
[pyFDA](https://github.com/chipmuenk/pyfda) and and [SciPy](https://docs.scipy.org/doc/scipy/reference/index.html).

*I'll almost always write 'NumPy' discussing Python scripts related to this filter series. This should
be considered a catch-all for various Python packages that aren't necessarily part of NumPy: matplotlib for plots,
SciPy for signal processing function, etc. I think it's fair to do this because [NumPy website](https://numpy.org)
lists SciPy as part of NumPy as well.*

[Matlab](https://www.mathworks.com/products/matlab.html) is extremely popular in the signal processing
world, but a license costs thousands of dollar, and even if it's better than NumPy (I honestly have no idea), 
it's total overkill for the beginner stuff that I want to do. [GNU Octave](https://www.gnu.org/software/octave/)
is free software that's claimed to be "drop-in compatible with many Matlab scripts", but I haven't tried
it.

# Designing Filters with pyFDA

During the initial stages of exploring filter configurations, I often find it faster to play around 
with a GUI. It's also a great way to learn about what's out there and familiarize yourself with characteristics
of different kinds of filters.

In [a recent tweet](https://twitter.com/matthewvenn/status/1311611352021118976), Matt Venn
pointed me to [pyFDA](https://github.com/chipmuenk/pyfda), short for Python Filter
Design Analysis tool, and [his video tutorial](https://www.youtube.com/watch?v=dtK-4JZ4Cwc) 
about it.

I've since been using it, and it definitely helped me in getting my PDM MEMS microphone design
off the ground.

In the screenshot below, you can see an example of a low pass filter that has all the
pass band and stop band characteristics that we need for our microphone, with a
sample rate of 48kHz:

![pyFDA screenshot](/assets/pdm/pdm2pcm/pyFDA.png)

pyFDA tells us that we need a 37-order filter (that corresponds at 38 FIR filter taps.)

There are all kinds of visualizations: magnitude frequency response, phase frequency response, 
impulse response, group delay, pole/zero plot, even a fancy 3D plot that I don't quite understand.

Once you've designed a filter, you can export the coefficients to use in your design. pyFDA can
even write out a Verilog file to put on your ASIC or FPGA. 

# Designing Filters with NumPy's Remez Function

For all its initial benefits, once the basic architecture of a design has been determined,
I prefer to code all the details as a stand-alone numpy file. For this project, that's
[pdm2pcm.py](https://github.com/tomverbeure/pdm/blob/master/modeling/pdm2pcm/pcm2pdm.py).

Code has the following benefits over a GUI:

* You can parameterize the input parameters and regenerate all the collaterals (coefficients, graphs, potentially even RTL code) in one go

    Even while writing this blog post, I made significant changes in the filter characteristics.
    You really don't want to manually regenerate all the graphs every time you do that!

* Much more flexilibity wrt graphs

    You can put multiple graphs in one figure. Add annotations. Tune colors etc.

* It's much easier for others to reproduce the results, and modify the code, learn from it.

    Feel free to clone all must stuff, and improve it!

The question is: how do you go about desiging FIR filters? 

I'm not qualified to give a comprehensive overview, but here are some very common techniques to 
determine the coefficients of FIR filters. It's probably not a coincidence that these techniques
are also supported by pyFDA.

**Moving Average and CIC Filters**

I already written about [Moving Average and CIC filters](2020/09/30/Moving-Average-and-CIC-Filters.html). 
Their coefficients are all the same. pyFDA supports them by selecting the "Moving Average"
option.

**Windowed Sinc and Windowed FIR Filters**

There are [Windowed Sinc filters](http://www.dspguide.com/CH16.PDF) and [Windowed FIR filters](http://www.dspguide.com/CH17.PDF)
where you specify a filter in the frequency domain, take an inverse FFT to get an impulse
response, and then us a windowing function to turn the behavior. NumPy and the 
[`firwin`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html) and
[`firwin2`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin2.html) function
for those. Use the "Windowed FIR" option in pyFDA for this one.

**Equiripple FIR Filters**

And finally, there are equiriplle filters that are designed with
[Parks-McClellan filter design algorithm](https://en.wikipedia.org/wiki/Parks%E2%80%93McClellan_filter_design_algorithm).
As far as I can tell, it is the most common way to design FIR filters. That's what I used in my earlier
pyFDA example by selecting the default "Equiripple" option.

It would lead too far to get into the details about the benefits of one kind of filter
vs the other, but when given specific pass band and stop band parameters, equiripple
filters requires the lowest number of FIR coefficients to achieve the desired performance.

You can use the the [`remez`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.remez.html)
function in NumPy to design filters this way, and that exactly what I've been doing.

For example, the coefficients of the filter above in my pyFDA example, can be found as follows:

```python
#! /usr/bin/env python3
from scipy import signal

Fs  = 48                # Sample rate
Fpb = 6                 # End of pass band
Fsb = 10                # Start of stop band
Apb = 0.05              # Max Pass band ripple in dB
Asb = 60                # Min stop band attenuation in dB
N   = 37                # Order of the filter (=number of taps-1)

# Remez weight calculation: https://www.dsprelated.com/showcode/209.php
err_pb = (1 - 10**(-Apb/20))/2      # /2 is not part of the article above, but makes the result consistent with pyFDA
err_sb = 10**(-Asb/20)

w_pb = 1/err_pb
w_sb = 1/err_sb
    
# Calculate that FIR coefficients
h = signal.remez(
      N+1,            # Desired number of taps
      [0., Fpb/Fs, Fsb/Fs, .5], # Filter inflection points
      [1,0],          # Desired gain for each of the bands: 1 in the pass band, 0 in the stop band
      [w_pb, w_sb]    # weights used to get the right ripple and attenuation
    )               

print(h)
```

Run the code above, and you'll get the following 38 filter coefficients: 
```
[-2.50164675e-05 -1.74317423e-03 -2.54534101e-03 -7.63329067e-04
  3.77271590e-03  6.73718674e-03  2.64362264e-03 -7.87738320e-03
 -1.48337024e-02 -6.75502030e-03  1.48004646e-02  2.98724354e-02
  1.54099648e-02 -2.76986944e-02 -6.25133368e-02 -3.81892367e-02
  6.54474060e-02  2.09343906e-01  3.13554280e-01  3.13554280e-01
  2.09343906e-01  6.54474060e-02 -3.81892367e-02 -6.25133368e-02
 -2.76986944e-02  1.54099648e-02  2.98724354e-02  1.48004646e-02
 -6.75502030e-03 -1.48337024e-02 -7.87738320e-03  2.64362264e-03
  6.73718674e-03  3.77271590e-03 -7.63329067e-04 -2.54534101e-03
 -1.74317423e-03 -2.50164675e-05]
```

A little bit more additional code, will create a frequency response plot:

```python
import numpy as np
from matplotlib import pyplot as plt

# Calculate 20*log10(x) without printing an error when x=0
def dB20(array):
    with np.errstate(divide='ignore'):
        return 20 * np.log10(array)

(w,H) = signal.freqz(h)

# Find pass band ripple
Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
Rpb = 1 - (Hpb_max - Hpb_min)
    
# Find stop band attenuation
Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
Rsb = Hsb_max
    
print("Pass band ripple:      %fdB" % (-dB20(Rpb)))
print("Stop band attenuation: %fdB" % -dB20(Rsb))

plt.figure(figsize=(10,5))
plt.subplot(211)
plt.title("Impulse Response")
plt.stem(h)
plt.subplot(212)
plt.title("Frequency Reponse")
plt.grid(True)
plt.plot(w/np.pi/2*Fs,dB20(np.abs(H)), "r")
plt.plot([0, Fpb], [dB20(Hpb_max), dB20(Hpb_max)], "b--", linewidth=1.0)
plt.plot([0, Fpb], [dB20(Hpb_min), dB20(Hpb_min)], "b--", linewidth=1.0)
plt.plot([Fsb, Fs/2], [dB20(Hsb_max), dB20(Hsb_max)], "b--", linewidth=1.0)
plt.xlim(0, Fs/2)
plt.ylim(-90, 3)

plt.tight_layout()
plt.savefig("remez_example_filter.svg")
```

Run this and you get:
```
Pass band ripple:      0.047584dB
Stop band attenuation: 60.316990dB
```

And the following plot:

![Remez Filter Plot](/assets/pdm/pdm2pcm/remez_example_filter.svg)

Check out [`remez_example.py`](https://github.com/tomverbeure/pdm/blob/master/modeling/pdm2pcm/remez_example.py) 
for the full source code.

In the code above, you need to specify order of the filter (N) yourself. To find the smallest
to satisfy the ripple and attenuation requirements, I just increase N until these requirements
are met.

# PDM to PCM First Try: Just Filter the Damn Thing!

Do we really need a complex filter architecture to convert PDM to PCM? Maybe a single equiripple
filter is sufficient for our needs?

Let's just fill in the numbers and see what happens:

```
...
Trying N=1382
Rpb: 0.094294dB
Rsb: 59.976587dB
Trying N=1383
Rpb: 0.093942dB
Rsb: 60.020647dB
Filter order: 1383
```

After more than a little while, it comes up with a filter that has 1384 taps, and the following
frequency response graph:

![Just Filter the Damn Thing](/assets/pdm/pdm2pcm/filter_the_damn_thing.svg)

Since this is a decimation filter, we only need to evaluate it for each output sample.
At 48kHz, this means that we need 48000 * 1384 = 66M multiplications per second.

That's a lot, but that's good if you're looking for a baseline and want to impress people 
about how you were able to optimize your design!

# Decimation is a Divide and Conquer Problem

All other things equal (sampling rate, pass band ripple, stop band attenuation), the number of
filter taps depends on the size of the transition band, compared to sample rate.

In the example above, the sample rate is 1920 kHz and the transition band is just 4kHz, a ratio
of 480!

If we reduce the sample rate by 5 to 384kHz and keep everything else the same, the number of taps
goes rougly down by 5 as well:

![Fpdm divided by 5 Frequency Response](/assets/pdm/pdm2pcm/fpdm_div5.svg)

Reducing the number of taps from 1384 down to 278 taps, gives

48000 * 278  = 13M multiplications

But that's not a fair comparison, because to be able use that filter, we first need to
decimate the signal at the initial sample rate from 1920kHz to 384kHz.

If we do this in the most naive way possible like any other decimation filter, we create a 
filter that doesn't touch the pass band and the transition band of the final result, and that 
filters away everything above the original sample rate divided by 5. 
In other words: a pass band from 0 to 10kHz, and a stop band that starts at 77kHz. This 
guarantees that none of the frequencies above 77kHz will alias into the range of 0 to 10kHz 
after decimation.

Number of taps required? 13!

![Fpdm to Fpdm/5 - Frequency Response](/assets/pdm/pdm2pcm/fpdm_to_fpdm_div5.svg)

Total number of multiplications:

```
384,000 *  13 =  5M             (5x decimation - from 1920 to 384 kHz)
 48,000 * 278 = 13M             (8x decimation - from 384 to 48 kHz)
-----------------------------------
                18M multiplications/s
```

By splitting up the dumb initial filter into 2 filters, we've reduced the number of multiplications from
66M downto 18M, a factor of more than 3!

If we can get that kind of savings splitting up a 40x decimation filter into a 2 filters, there must
be similar optimization possible by splitting up that 8x decimation filter. 

There must be some kind of optimal arrangment that results in a minimal number of multiplications
to get from our initial to our desired sample rate.

But before we look at that, some clarifications and corrections must be made about specifying the right 
decimation filter parameters.

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

The fat black line below shows the frequence response if we use a single filter:

![Direct 6x Decimation Filter](/assets/pdm/pdm2pcm/pdm2pcm-div6_decimation_filter.svg)

We already saw earlier that 2 less aggressive filters result in a lower number of taps (and thus
multiplications) and 1 more aggressive filter. In this particular example, that means we can
either decimate by 2x first and 3x after that, or the other way around.

The figure below shows the two paths:

![Cascaded Decimation Steps](/assets/pdm/pdm2pcm/pdm2pcm-cascaded_decimation.svg)

There are 2 major things of note:

1. Naive vs smart filtering in the first stage 

    If we treated the first decimation stage as any other decimation filter, we'd put the
    stop band at end of *Fsample/2/n* to avoid any kind of aliasing of the upper
    frequencies into the remaining frequency band.

    But that is too aggressive!

    What we can do instead is start of the stop band of the first filter at *Fsample/n* - *Fsb*.

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

We're shooting for an overall pass band ripple of 0.1dB and a stop band attenuation of 60dB. 

When there's only 1 filter, meeting that goal is a matter of specifying that as a filter design parameter.

But what when multiple filters are cascaded?

In their 1975 paper 
["Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf),
Crochiere and Rabiner write the following:

> As it is desired that the overall pass band ripple for the composite of K stages be maintained 
> within 1+-delta it is necesary to require more severe frequency constraints on the individual filters
> in the cascade. Aconvenient choice which will satisfy this requirement is to specify the pass band
> ripple constraints for each stage *i* to be within 1+delta/K.

In other words: if we split the filter into 3 stages, they suggest to split the joint passband ripple of 0.1dB into
3 pass band ripples of ~0.03dB.

(Note that close to 1, *20 * log10(x)* ~ *x-1*. Since pass band ripple is a deviation around 1, we can simply
divide the dB number without having to convert from dB to linear and back.)

In practise, this will create a joint pass band ripple that's a bit lower than specified because it's
unlikely that all 3 filters will have peaks and throughs at the same location.

Now for the stop band. From the same paper:

> In the stop band the ripple constraint for the composite filter must be *delta* and this
> constraint must be imposed on each of the individual low-pass filter as well, in order to suppress
> the effects of aliasing.

This confused me since as many frequency range will be aliased onto final signal as the decimation
ratio. And you need to account for that.

But then I realized that I whether you use a single filter or multiple ones, you always need to
take the decimation ratio into account when specifying the stop band attenuation.

Let's use this on our example: we want 60dB stop band attenuation. When reducing the sample rate from
1920kHz to 48kHz, there's a 40x decimation ratio. Our filter needs to correct for that: 

```
-60dB = 0.001 / 40 = 0.0000025 -> -72dB
```

Going forward, all 


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

**Sigma-Delta AD Convertors**

* [How delta-sigma ADCs work, Part 1](https://www.ti.com/lit/an/slyt423a/slyt423a.pdf) 
   and [Part 2](https://www.ti.com/lit/an/slyt438/slyt438.pdf)

    Texas Instruments article.  Part 1 is a pretty gentle introduction about the sigma-delta basics.
    Part 2 talks about filtering to go from PDM to PCM, but it's very light on details.

* [Understanding PDM Digital Audio](http://users.ece.utexas.edu/~bevans/courses/realtime/lectures/10_Data_Conversion/AP_Understanding_PDM_Digital_Audio.pdf)

**Filter Design**

* [Tom Roelandts - How to Create a Simple Low-Pass Filter](https://tomroelandts.com/articles/how-to-create-a-simple-low-pass-filter)

    Simple explanation, Numpy example code.

* [Design of FIR Filters](https://www.vyssotski.ch/BasicsOfInstrumentation/SpikeSorting/Design_of_FIR_Filters.pdf)

    Good presentation about different ways to design filters, Remez, ripple etc.

* [Remez (FIR design) Weights from Requirements](https://www.dsprelated.com/showcode/209.php)

    Shows how to calculate weights for the Remez algorithm (though there seems to be an off-by-2
    error for the passband weights.)

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

**Decimation**

* [Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf)

    Paper that discusses how to size cascaded filter to optimized for FIR filter complexity.

* [Seamlessly Interfacing MEMS Microphones with Blackfin Processors](https://www.analog.com/media/en/technical-documentation/application-notes/EE-350rev1.pdf)

    Analog Devices application note. C code can be found[here](https://www.analog.com/media/en/technical-documentation/application-notes/EE350v01.zip)



