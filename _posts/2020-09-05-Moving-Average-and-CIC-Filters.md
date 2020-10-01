---
layout: post
title: An Intuitive Look at Moving Average and CIC Filters
date:  2020-09-30 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

According my college transcripts, I'm supposed to have some knowledge about signal theory,
filters etc, but the truth is that, 25 years later, I've forgotten most of it. I couldn't
design some trivial lowpass filter if my life depended on it.

And that's a shame, because it's a fascinating topic, and a useful one too if you want to
do audio processing on an FPGA or play with software defined radio.

I also want to learn to use Numerical Python (numpy) and matplotlib, its graph plotting
package.

In an effort to revive some of that forgotten DSP knowledge, I've been slowly working my way through 
[The Scientist and Engineer's Guide to Digital Signal Processing](http://www.dspguide.com/pdfbook.htm).
It's a great book that's light on math with an emphasis on practical usage.

But the best way to really learn something is by doing, so I started an FPGA project that
takes in audio from a MEMS microphone in a single bit pulse density modulated (PDM) format,
converts it to regular 16-bit pulse code modulated (PCM) samples, and send it out to
an optical SPDIF output.

When studying the topic of PDM to PCM conversion, it's almost impossible to not run into the
topic of cascaded integrator comb (CIC) filters: they are extremely lightweight in terms of resources,
thanks to a number of interesting tricks and transformations.

The full story of my microphone to SPDIF pipeline is still a work in progress, but CIC
filters by themselves are enough of a topic to fill a pretty long blog post, so that's
what I'll be writing about below.

*As always, keep the usual disclaimer in mind: these blog posts are a way for me to solidify what
I've learned. Don't take whatever is written below as gospel, there may be significant errors in it!*

# Moving Average Filters

Typical FIR filters have a certain length, or taps, and each tap requires a multiplication and an 
addition. Larger FPGAs have a decent set of DSPs (which are essentially HW accumulate-addition blocks), 
and support logic to implement FIR filters as efficiently as possible, but even then, implementing
an FIR filter can consume quite a bit of FPGA resources that are often scarce.

The multipliers are there to shape the filter so that it has the desired pass band, transition band, and
stop band characteristics.

But what if we just ignore required characteristics to get rid of this kind of mathematical complexity?

The simplest filter, then, is the moving average filter (also called boxcar filter): it sums the last 
incoming N samples, divides the result by N and... that's it!

A moving average filter is probably one of the most common filters in digital signal processing: it's
super simple to understand and implement, they are symmetric, so they have linear phase response, 
and it's also an optimal filter for white noise reduction. (That's
because white noise doesn't have a preference to impact this sample or the other, it affects any sample
with equal chance. And because of that, there's no way you can tune this or that coefficient of the
filter coefficients in some preferential way.) 

Unfortunately, moving average filters have some major disadvantages as well: they have a large attenuation 
in the pass band, they have a very slow roll-off from the pass band to the stop band, they have bad
time domain behavior (ringing) and the stop band attentuation is very low too.

You can overcome the low stop band attenuation by cascading multipe filters after each other, but that
makes the pass band attenuation worse too.

Since the filter coefficients are fixed and constant, there are only 2 parameters to play with: the size 
of the box (the number of samples that are averaged together) and the order, number of filters that are cascaded

The filter's frequency response using a linear scale Y axis looks like this for different averaging lengths, and 
different filter orders:

![Moving Average Filter Response - Linear](/assets/pdm/moving_average_filter_overview_linear.svg)

The horizontal axis shows the normalized frequency, ranging from 0 to 1/2 of the sample rate.

Since the impulse response of the filter is a box, the frequency response is a sinc(f) function.

When we increase the length of the filter, everything gets squeezed to the left: the bandpass gets
narrower. And when we cascade multiple filters after each other, the attenuation increases.

The traditional and more useful way to look at a filter's frequency behavior is with a log Y axis:

![Moving Average Filter Response](/assets/pdm/moving_average_filter_overview.svg)

A moving average filter doesn't have a clearly defined pass band: close to the 0 frequency,
the curve starts flat, but as you move to the right, the slope get gradually steeper.

The stop band attenuation, on the other hand, is pretty clearly set at -13.3dB for a first order
filter, irrespective of the number of samples averaged.

When we increase the order, the attenuation of the stop band increases accordingly: you can just
multiply the stop band attenuation (in dB) of the first order filter by the number of stages: -26.5dB
for 2 stages, -66.3dB for 4 stages.

With these problematic characteristics, are moving average filters even worth doing?

The answer is yes!

A trivial implementation of a moving average filter is already less resource intensive than an
FIR filter with variable coefficients, but when they're used as a part of a decimation (downsampling) 
or or interpolation (upsampling) pipeline, their resource usage reduces to almost nothing. 

# Intermission: The Basics of Decimation

Before diving deeper in the specifics of moving average filters, let's do a quick primer on
decimation.

In digital signal processing, decimation is the step of removing N-1 number of samples for every
N samples. It's really as simple as that: you throw away samples.

If you start with a signal that has a sample rate of 3.072 MHz and you decimate by a factor of 64, 
you end up with a signal that's sampled at 48kHz. These numbers weren't chosen at random: they're the 
sample rates that you could get when converting the output signal of a MEMS microphone from PDM to PCM.

We know that a sample rate of 3.072MHz allows for frequency components of 
maximum 1.576MHz. And a sample rate of 48kHz allows for frequency components of up to 24kHz.

During that act of decimation, the frequency components between 24kHz and 1.576MHz don't just magically 
disappear, they fold back onto the remaining frequency range from 0 to 24kHz.

This makes total sense, because it's same as the aliasing effect that happens when you
undersample a signal right from the start.

Here's a simple example spectrum of a signal with 3 sine waves at 100Hz, 1000Hz and 2800Hz 
and some added noise, sampled at 10kHz. The sine waves at 100Hz and 1000Hz have a much lower 
amplitude than the one at 2800Hz.

![Decimation without Filtering - 3 Sine Waves - No Decimation](/assets/pdm/decimation_without_filtering-no_decimation.svg)

This is what happens when you decimate that signal by 2 or by 4: 

![Decimation without Filtering - 3 Sine Waves - No Decimation](/assets/pdm/decimation_without_filtering-2x_4x_decimation.svg)

The 2800Hz signal didn't magically disappear. It jumped to a frequency of 2200Hz and 300Hz for 2x and 4x 
decimation respectively.

If you look closely, you'll also notice that the noise level has increased after decimation too. It's well 
below -50dB before decimation, yet regularly crosses the -50dB line after 4x decimation. The same thing is 
happening here: the noise of the higher frequencies aliased into the low frequency band.

Conclusion: to avoid aliasing, you first need to apply a low pass filter to your signal before
performing decimation.

And with that, let's get back to our regular programming about moving average filters.

# From Trivial Implementation to Cascaded Integrator Comb (CIC) Configuration

In 1980, Eugene Hogenauer published a [seminal paper](http://read.pudn.com/downloads163/ebook/744947/123.pdf) 
about how to implement cascaded moving average filters for decimation and interpolation purposes. These
filters are now known as CIC filters, short for Cascaded Integrator Comb filters.
The paper is surprisingly readable... for a paper, but still contains a decent amount of theory and math. 

Here, I want to take the intuitive approach.

The most naive and trivial moving averaging filter implementation is a literal translation
of the summing math into hardware. For a length of 4, it'd look like this:

![Moving Average Filter - Trivial Implementation](/assets/pdm/moving_average_filters-trivial.svg)

The implementation above averages 4 samples, requires 3 delay elements and 3 adders. The initial
division by 4 is to ensure that the filter has a unity gain. I will drop that factor going forward, just
imagine that it's there.

As expected, there are no multipliers in this design, but the 3 adders are bit difficult to accept,
especially since that number will go up proportionally for moving average filters of a longer length.

Can we do better? Of course! There is a bunch of math that stays the same from one sample to the next.

Let's look at the math below:

```
y(3) =               x(3) + x(2) + x(1) + x(0)
y(4) =        x(4) + x(3) + x(2) + x(1)
which can be simplified to:
y(4) = y(3) + x(4)                      - x(0)
```

or in general:

```
y(n) = y(n-1) + x(n) - x(n-4)
```

The simple sum has been transformed into a recursive operation where the output of the previous
cycle gets reused for the next output.

In hardware, that looks like this:

![Moving Average Filter - Comb Integrator Version](/assets/pdm/moving_average_filters-comb_integrator_version.svg)

We have added 2 delay registers and a subtractor, but have saved a whole lot of adders. And these 2 delay
registers are a one-time cost for converting to a recursive configuration: if we increase
the summing length from 4 to 8, we'll only add 4 more registers to the delay line and nothing else. (But as
we shall see below, it will get even better!)

The section with the delay line and the subtactor is called a "comb". The recursive part that feeds back
the previous output is called the "integrator".

It's slightly less intuitive, but you can swap the interpolator and the comb sections and get the same
calculated result. In this case, instead of having a recursive output, you continuously accumulate *x*, 
and subtract that accumulation later.

![Moving Average Filter - Integrator Comb Version](/assets/pdm/moving_average_filters-integrator_comb_version.svg)

Accumulate *x* to *a* in the integrator:

```
a(n) = x(n) + a(n-1)
```

And calculate the output in the comb:
```
y(n) = a(n) - a(n-4)
```

The output *y* is still the sum of the last 4 inputs:

```
y(n) = a(n) - a(n-4)
y(n) = x(n) + a(n-1) - a(n-4)
y(n) = x(n) + x(n-1) + a(n-2) - a(n-4)
y(n) = x(n) + x(n-1) + x(n-2) + a(n-3) - a(n-4)
y(n) = x(n) + x(n-1) + x(n-2) + x(n-3) + a(n-4) - a(n-4)
y(n) = x(n) + x(n-1) + x(n-2) + x(n-3) 
```

If you were really paying attention, you might have noticed that continously accumulating *x* into *a* will 
eventually result in overflowing *a*. However, as long as the delay registers have enough bits, the
comb section will automatically counteract this overflow: you'll still get the right result.

You can increase the attenuation by cascading multiple moving average filters:

![Moving Average Filter - Cascaded Combs Integrators](/assets/pdm/moving_average_filters-cascaded_integrators_and_combs.svg)

You can even rearrange the blocks above and group the integrators and combs together, without
changing the mathematical result:

![Moving Average Filter - Rearranged Integrators and Combs](/assets/pdm/moving_average_filters-rearranged_integrators_combs.svg)

Now observe how the integrator always has exactly 1 delay register, while the comb has
as many delays as the number of samples of the moving average. If moving average filter requires a length of,
say, 64, and you're cascading multiple of those together, that's still a lot of delay registers.

But remember: these kind of filters are primarily used for decimation and interpolation. 

Let's focus on decimation: if we decimate by a factor 4, we simply retain one output sample out of every 4
input samples.

In the example below, the downsampler at the right drops those 3 samples out of 4, and the output rate,
*y'(n)*, is one fourth of the input rate *x(n)*:

![Moving Average Filter - Decimation Trivial](/assets/pdm/moving_average_filters-decimation_trivial.svg)

But if we're going to be throwing away 75% of the calculated values, can't we just move the 
downsampler from the end of the pipeline to somewhere in the middle? Right between the integrator
stage and the comb stage? That answer is yes, but to keep the math working, we also need to divide
the number of delay elements in the comb stage by the decimation rate:

![Moving Average Filter - Decimation Smart](/assets/pdm/moving_average_filters-decimation_smart.svg)

The end result is beautiful: 

**When used as part of a decimator, a moving average filter that started out as a design 
with *(n-1)* delay stages and *(n-1)* adders running at the incoming sample rate, has been reduced to 2 delay stages, 
1 adder, and 1 subtractor, and half of the logic is running at a much slower rate.** 

We can do this as long as the decimation ratio is an integer multiple of the length of the desired moving average 
filter. In practice, the decimation ratio will almost always be the same as the length of the filter, and thus, the
number of delay stages in the comb section will be 1.

The math is trivial. 

We still continously add all new values of *x* to *a*, but instead of using and delaying every *a* value in the comb stage, 
we only use and delay every 4th *a* value:

```
a(3) = x(3) + x(2) + x(1) + x(0) + <previous values>
a(7) = x(7) + x(6) + x(5) + x(4) + x(3) + x(2) + x(1) + x(0) + <previous values>
```

And *y* subtracts the current *a* value from the one that was delayed:

```
y(7) = a(7) - a(3)
y(7) = x(7) + x(6) + x(5) + x(4)
```

And we can do this just the same with cascaded sections where integrators and combs have been grouped:

![Moving Average Filter - Cascaded Decimation Smart](/assets/pdm/moving_average_filters-integrator_comb_decimated.svg)

It's important to note here that, for decimation, the integrators come first and the combs second with the downsampler in between. 
For interpolation, the reverse is true: the incoming sample rate is fraction of the outgoing sample rate, the combs must 
come first and the interpolators second.

![Moving Average Filter - Cascaded Decimation Smart](/assets/pdm/moving_average_filters-comb_integrator_interpolated.svg)


# Moving Average Filters as Decimator

We now know why moving average filters are so popular for decimation and interpolation: their
CIC implementation requires almost no resources, irrespective of the up- or downsampling ratio.

However, it's not all roses: the negatives of moving average filters that were mentioned earlier, 
poor stop band attenuation and non-flat pass band attenuation, didn't magically disappear. 

In fact, they got worse: in a decimation CIC filter, the length of the moving average filter must be
an integer multiple of the decimation ratio. In most cases, that ratio is 1. Because of this, the only way to 
influence the attenuation of the stopband is by increasing the number of cascaded interpolator and
comb banks, but that, in turn, also increases the pass band attenuation. 

Let's look here at a 5th order CIC filter with a filter length of 4. The sample frequency is 80kHz, which
means that the incoming signal can have frequency components from 0 to 40kHz.

![CIC Response before decimation](/assets/pdm/cic_decimation_full_range.svg)

The filter length of 4 gives a 2 lobes. Under normal circumstances, you'd say that this filter has a stopband 
attenuation of 56.77dB. However, since the decimation ratio of a CIC filter is linked to the filter length, that 
decimation ratio has to be 4 as well.

The output sample rate of our decimating filter will be 20kHz (80kHz/4), and the bandwidth of the outgoing signal will
be from 0 to 10kHz.

After decimation, the original signal components with a frequency higher than that of the outgoing signal will
alias into the frequency range of the outgoing signal. 

In the graph above, this means that the remaining signal components under the orange, the green and the red curve will
be alias under the blue curve. 

![CIC Response after decimation](/assets/pdm/cic_decimation_aliased.svg)

The blue curve is the true signal with a 10kHz bandwidth. The remaining curves are distorting the true signal.

Forget about a stopband attenuation of 56.77dB: the real stopband attenuation of this filter is 18.49dB, the point
where the blue curve stops and the orange curve starts! And the passband attenuation isn't flat either: it goes down 
from 0 and -18.49dB as well.

If a decimating CIC filter by itself is so terrible, why then is it so popular?

**Because a decimating CIC filter is always used as part of a multi-stage decimation configuration.**

Nobody would use a 4x decimating CIC filter to extract a 10kHz BW output signal from a 40kHz BW input signal. The CIC
filter is just a first step to reduce sample rate from some high number to a lower, intermediate, number. 
And then one or more traditional FIR filters are used to bring the sample rate to the final desired output rate.

In our example, if our signal of interest lies in the 0 to 2000Hz range, the CIC filter has reduced the signal components 
that aliased into the 0 to 2000Hz range by more than 92dB, and the passband attenuation is only 0.7dB!

![CIC Response at lower frequencies](/assets/pdm/cic_decimation_lower_freqs.svg)

All that's needed now is one or two filters with a clean passband behavior from 0 to 2000Hz and with a stop band from, 
say, 3000Hz to 10000Hz. That is much less computationally intensive than a filter with the same passband
and with a stop band that ranges from 3000Hz to 40000kHz!

An example makes this clear: a Blackmann windowed-sinc FIR with a cutoff frequency of 2500Hz, 
transition bandwidth of 1000Hz, a stopband attenuation of 74dB, and a sample rate of 80000Hz requires 369 coefficients. 

The same filter but with the sample rate reduced to 20000Hz reduces that number to only 93 coefficients.

And this is for a decimation rate of only 4. In audio applications, the sample rate of a PDM microphone often needs to be reduced 
from 3.072MHz to 48kHz, a ratio of 64.  A 16x CIC filter that reduces that ratio from 64 to, say, 4, will go a long way in making 
the size of the FIR filter manageable.

# Passband Compensation in CIC Filters

I already mentioned it a couple time before: a CIC filter doesn't have a well defined pass band, and requires
a trade-off between choosing a large pass band vs choosing low pass band attenuation.

Furthermore, a narrow pass band will often require a more complex FIR filter to remove unwanted frequency
components.

One common way around this is to add a compensation filter that counteracts the pass band behavior of
the CIC filter. In many cases, these compensation filters can implemented with limited resources.

There are 2 ways to go about this: 

* the pass band compensation can be a separate additional step at the very end of the filtering pipeline.
* the pass band compensation is part of the FIR filter(s) after the CIC filter.

![Moving Average Filter - Compensation Filter Pipeline](/assets/pdm/moving_average_filters-compensation_filter_pipeline.svg)

It seems to make sense to roll the compensation part into the low pass filter, but one good reason
to not do this is the existence of [half-band filters](https://en.wikipedia.org/wiki/Half-band_filter): 
these are filters that have their transition band centered at exactly one fourth of the sample rate. 
With some additional restrictions, they have the property that half of the FIR filter coefficients are 
zero, and they thus require only half of the multipliers. That makes them excellent candidates for 2x decimation 
filters. However, it makes them ineligible as compensation filter.

Practical compensation filter design will be discussed in the future blog post, but check out the
references at the bottom of this page if you want more information now.

# The Size of the Delay Elements in a CIC Filter

If the delay elements of a CIC filter aren't large enough, the filter will show overflow behavior.

The easiest way to avoid these overflows is to give all delay elements the same size:

nr bits = *x(n)* bits + roundUp(nr stages * log2(nr delay elements in comb stage * decimation ratio))

This number can go up quickly. For a 16x decimation filter with 5 stages and a 1 bit PDM input, you
end up with 

nr bits = 1 + roundUp(5 * log2(1 * 16)) = 26

If your input signal has a signal to noise ratio of less than that, assigning 26 bits everywhere
is overkill. Hogenauer's paper goes into low level detail about how to optimally reduce the size of the
delay stages at different location in the pipeline, but since flip-flops are pretty cheap these days,
I'll leave that for another time.

For now, just drop the LSBs of your output signal if the number of bits is higher than what's needed
to maintain the SNR of your input signal. Or check out the references below for a CIC register pruning
utility.

# A Note about Simulation

CIC filters are special in that there's no floating point involved: everything
happens with pure integer or fixed point math. But one thing to keep in mind is that integer overflow is 
expected and inevitable. The architecture is such that overflow in the initial stages gets compensated
for in the later stages. When using floating point, due to rounding errors, one can not guarantee that
this compensation happens correctly.

For that reason, when simulating a moving average filter in something like numpy, I don't bother using CIC filters,
and use the standard FIR convolution instead.

# Going Forward...

So far, I've only talked about theory. Practice is more fun and scheduled for an upcoming blog post, so
stay tuned!

Meanwhile, there's plenty to read about the topic. Check out the references below. The favorite one
is the Rick Lyon's [A Beginner's Guide To Cascaded Integrator-Comb (CIC) Filters](https://www.dsprelated.com/showarticle/1337.php).
It much everything above, but with more mathematical rigor. 

# References

CIC Filters:

* [An Economical Class of Digital Filters For Decimation and Interpolation](http://read.pudn.com/downloads163/ebook/744947/123.pdf)

    Hogenauer's original paper about CIC filters.

* [Rick Lyons - A Beginner's Guide To Cascaded Integrator-Comb (CIC) Filters](https://www.dsprelated.com/showarticle/1337.php)

    Excellent introduction to CIC filters with a bit more of math and rigor.

* [Small tutorial on CIC filters](http://www.tsdconseil.fr/log/scriptscilab/cic/cic-en.pdf)

    Excellent concrete example of a CIC decimating filter design (with compensation), the number of bits required,
    and the consequences of aliasing.

* [CIC Filter Introduction](http://dspguru.com/files/cic.pdf)

* [Designing CIC Compensation Filters](http://threespeedlogic.com/cic-compensation.html)

    References to C++ tools etc to come up with the actual coefficients.

* [Understanding CIC Compensation Filters](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/an/an455.pdf)

    Excellent application note from Altera.

* [Rick Lyons - Computing CIC Filter Register Pruning Using Matlab](https://www.dsprelated.com/showcode/269.php)

    Explanation about correctly sizing the delay elements with Matlab code. You can find a C implementation
    of the Matlab code [here: CIC filter register pruning utility](http://www.jks.com/cic/cic.html).

General DSP:

* [The Scientist and Engineer's Guide to Digital Signal Processing](http://www.dspguide.com/pdfbook.htm)

    Awesome book about DSP that's low on math and high on intuitive understanding. The digital version
    is free too!

* [Introduction to Digital Filters with Audio Applications](https://ccrma.stanford.edu/~jos/filters/filters.html)

* [Multirate Digital filters, filter banks, polyphase networks, and applications: a tutorial](https://authors.library.caltech.edu/6798/1/VAIprocieee90.pdf)

    37 page paper on decimation and interpolation.

* [dspGuru FAQs](https://dspguru.com/dsp/faqs/)
    
    FAQs about FIR, IIR, multirate (decimation, interpolation, resampling), FFT etc.
    
    Doesn't go much in detail, but really useful as a refresher.

* [TomRoelandts.com](https://tomroelandts.com/articles)

    Lots of interesting filtering related articles.

    He's also the creator [FIIIR!](https://fiiir.com/), an online tool to create a variety of filters.

* [Earlevel Engineering](https://www.earlevel.com/main/)

    Tons of articles related to audio DSP.

Decimation:

* [Rick Lyons - Optimizing the Half-band Filters in Multistage Decimation and Interpolation](https://www.dsprelated.com/showarticle/903.php)

    Talks about how it may not be ideal to have 3 identical cascaded 2x half-band filters when
    you want to be decimate by 8. Unfortunately, it only does so qualitatively, not quantitatively.

Filter Tools:

* [FIIIR1](https://fiiir.com)

* [LeventOztruk.com](https://leventozturk.com/engineering/filter_design/)

* [pyFDA](https://github.com/chipmuenk/pyfda)


