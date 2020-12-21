---
layout: post
title: Design of a Multi-Stage PDM to PCM Decimation Pipeline
date:  2020-12-20 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In the [past 5 episodes of this series](#references), I discussed 
sigma-delta converters, how to read the datasheet of a microphone, different types 
of filters, and how to come up with the right coefficients of these filters.

Finally, it's time to bring all the pieces together and create a full signal 
processing pipeline to convert the output of a [PDM](https://en.wikipedia.org/wiki/Pulse-density_modulation) 
microphone into standard [PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation) samples. 

# The Design Requirements 

Let's quickly repeat the overall design requirements that I came up with in 
[a previous blog post](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html#pdm-to-pcm-design-requirements):

* PDM input sample rate: 2.304MHz
* PCM output sample rate: 48kHz

    In other words, a decimation ratio of 48.

* Pass band: 0 to 6kHz
* Stop band: 10kHz
* Pass band ripple: 0.1dB
* Stop band attenuation: 89dB

# The Canonical Multi-Stage Decimation Pipeline

There is an overwhelming amount of literature out there about the pipeline to decimate
an incoming signal at very high sample rate down to something much lower. And while
there are an almost infinite amount of subtle variations, the fundamentals can
almost always be reduced to the following basic building blocks: 

* a CIC filter at the front
* one or more half-band filters in the middle
* a generic FIR filter in the back

![Canonical Decimation Pipeline](/assets/pdm/pdm2pcm/pdm2pcm-canonical_pipeline.svg)

The reason for this arrangement is obvious when you consider typical design constraints such
as clock speeds and resource usage.

1. A CIC filter only requires adders and delay stages, but no multipliers. This makes them extremely
   area efficient.
1. The lack of multipliers also makes it easier to run CIC filters at high clock speeds.
1. A half-band filter requires only around 50% of the multiplications of an equivalent
   generic FIR filter. This reduction is at all times large enough to overcome the
   inefficiency of splitting a larger generic FIR filter into a cascaded half-band filter 
   and a FIR filter that has half the order of the original one.

With the core pipeline in place, the next step is figuring out the exact filter parameters for
each stage.

# Pass Band Ripple, Stop Band Attenuation and Multi-Stage Decimation

The requirements call for an overall pass band ripple of 0.1dB and a stop band attenuation of 89dB. 

When there's only 1 filter, meeting that goal is a matter of specifying these numbers as the filter design 
parameter.

But what when multiple filters are cascaded?

**Pass Band Ripple**

In their 1975 paper 
["Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering"](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf),
Crochiere and Rabiner write the following:

> As it is desired that the overall pass band ripple for the composite of K stages be maintained 
> within *1&plusmn;&delta;*, it is necesary to require more severe frequency constraints on the individual filters
> in the cascade. A convenient choice which will satisfy this requirement is to specify the pass band
> ripple constraints for each stage *i* to be within *1&plusmn;&delta;/K*.

In other words: if you split the filter into 3 stages, they suggest to split the joint passband ripple of 0.1dB into
3 smaller pass band ripples.

Unfortunately, this advise doesn't work very well for our case: the referenced paper assumes that all stages
are using similar filter types, with the ability to indepdently choose the boundaries for pass band and stop
band ripple for each filter stage.

This is not the case for us: a CIC filter has very little flexibility wrt pass and stop band attenuation, 
and half-band filters have only 1 parameter, the filter order, to control the ripple of both pass band and stop band.

What we can take away, however, is the knowledge that we need to divide the overall pass band into smaller values
and uses those as design parameter for the individual stages.

**Stop Band Attenuation**

The same paper has the following to say about the stop band:

> In the stop band the ripple constraint for the composite filter must be *&delta;* and this
> constraint must be imposed on each of the individual low-pass filter as well, in order to suppress
> the effects of aliasing.

This is much easier: [I calculated a stop band attenuation of 89dB](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html#stop-band-attenuation-for-a-decimation-filter). 
We can just to use that attenuation for each filter stage.

# CIC Filter Configuration and Pass Band Ripple

Since they don't require any multiplications at all, it's desirable to shift as much as
of the decimation to the front-end CIC filter.

One problem with CIC filters, however, is that the pass band ripple gets progressively
worse with increasing frequency and with an increasing number of cascade stages.
Without using a counter measure in the form of a compensation filter, the frequency response
in the pass band can easily exceed the maximum ripple requirements of the overall
filter specification.

**Pass band ripple and decimation ratio**

Our overall filter has a decimation ratio of 48, and thus 8 possible CIC decimation
ratios: 2, 4, 6, 8, 12, 16, 24, 48.

For a 5 stage configuration, these 8 options give the following magnitude frequency plots:

![All decimation ratios for a 5 stage CIC filter](/assets/pdm/pdm2pcm/cic_ratios_overview.svg)

That tiny rectangle in the top left corner shows the frequency range from 0 to 24kHz, our final
output bandwidth. Let's zoom in on that:

![All decimation ratios for a 5 stage CIC filter - Zoom](/assets/pdm/pdm2pcm/cic_ratios_zoom.svg)

The rectangle now shows the pass band: a frequency range from 0 to 6kHz and a maximum pass band ripple
boundary of 0.1dB.

You can see how a decimation ratio of 16 and higher violates the maximum ripple requirements,
and that's before taking into account that the filters that follow the CIC stage need to get their
share of the overall pass band ripple!

**Pass band ripple and number of cascaded stages**

In the graphs above, I use an example of 5 stages with variable decimation rate.  I can do the same 
with a fixed decimation rate and a variable number of stages:

![Fixed Decimation Rate, Variable Number of Stage CIC filter - Zoom](/assets/pdm/pdm2pcm/cic_stages_zoom.svg)

The result is more predictable, but similar: a higher number of stages increases the pass band ripple.

One way to solve this issue is to add a compensation filter with a gain in the pass band region that is 
the exactly opposite of the chosen CIC filter, thus resulting in a flat pass band behavior. 
But that's something for a future blog post.

**Pass band ripple table: decimation ratio vs number of stages**

For simplicity, we will just need to limit decimation ratio and/or the number of stages
such that the pass band ripple doesn't exceed a certain maximum value. This maximum
value is than the 0.1dB pass band ripple of the overall filter to leave something for
for the filter stages that follow the CIC filter.

Let's choose a maximum ripple of 0.05dB.

The table below lists all the combinations of decimation ratio and number of CIC stages, and
their ripple. The entries in green are the ones that don't violate the 0.05dB maximum:

<table>
<caption style="text-align:center"><b>Pass Band Ripple (dB)</b><br/>Decimation Ratio / Nr of CIC Stages</caption>
<tr>    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
</tr>
<tr>
    <th>2</th>
    <td style="background-color:#a0e0a0">-0.00030</td>
    <td style="background-color:#a0e0a0">-0.00059</td>
    <td style="background-color:#a0e0a0">-0.00089</td>
    <td style="background-color:#a0e0a0">-0.00118</td>
    <td style="background-color:#a0e0a0">-0.00148</td>
    <td style="background-color:#a0e0a0">-0.00177</td>
</tr>
<tr>
    <th>4</th>
    <td style="background-color:#a0e0a0">-0.00148</td>
    <td style="background-color:#a0e0a0">-0.00295</td>
    <td style="background-color:#a0e0a0">-0.00443</td>
    <td style="background-color:#a0e0a0">-0.00591</td>
    <td style="background-color:#a0e0a0">-0.00738</td>
    <td style="background-color:#a0e0a0">-0.00886</td>
</tr>
<tr>
    <th>6</th>
    <td style="background-color:#a0e0a0">-0.00345</td>
    <td style="background-color:#a0e0a0">-0.00689</td>
    <td style="background-color:#a0e0a0">-0.01034</td>
    <td style="background-color:#a0e0a0">-0.01379</td>
    <td style="background-color:#a0e0a0">-0.01723</td>
    <td style="background-color:#a0e0a0">-0.02068</td>
</tr>
<tr>
    <th>8</th>
    <td style="background-color:#a0e0a0">-0.00620</td>
    <td style="background-color:#a0e0a0">-0.01240</td>
    <td style="background-color:#a0e0a0">-0.01860</td>
    <td style="background-color:#a0e0a0">-0.02480</td>
    <td style="background-color:#a0e0a0">-0.03101</td>
    <td style="background-color:#a0e0a0">-0.03721</td>
</tr>
<tr>
    <th>12</th>
    <td style="background-color:#a0e0a0">-0.01411</td>
    <td style="background-color:#a0e0a0">-0.02821</td>
    <td style="background-color:#a0e0a0">-0.04232</td>
    <td style="background-color:#e0a0a0">-0.05642</td>
    <td style="background-color:#e0a0a0">-0.07053</td>
    <td style="background-color:#e0a0a0">-0.08463</td>
</tr>
<tr>
    <th>16</th>
    <td style="background-color:#a0e0a0">-0.02511</td>
    <td style="background-color:#e0a0a0">-0.05022</td>
    <td style="background-color:#e0a0a0">-0.07533</td>
    <td style="background-color:#e0a0a0">-0.10044</td>
    <td style="background-color:#e0a0a0">-0.12555</td>
    <td style="background-color:#e0a0a0">-0.15066</td>
</tr>
<tr>
    <th>24</th>
    <td style="background-color:#e0a0a0">-0.05677</td>
    <td style="background-color:#e0a0a0">-0.11355</td>
    <td style="background-color:#e0a0a0">-0.17032</td>
    <td style="background-color:#e0a0a0">-0.22709</td>
    <td style="background-color:#e0a0a0">-0.28387</td>
    <td style="background-color:#e0a0a0">-0.34064</td>
</tr>
<tr>
    <th>48</th>
    <td style="background-color:#e0a0a0">-0.21903</td>
    <td style="background-color:#e0a0a0">-0.43807</td>
    <td style="background-color:#e0a0a0">-0.65710</td>
    <td style="background-color:#e0a0a0">-0.87614</td>
    <td style="background-color:#e0a0a0">-1.09517</td>
    <td style="background-color:#e0a0a0">-1.31420</td>
</tr>
</table>

If pass band ripple were the only design criterium, the best choice
would be a solution with the highest decimation ratio,  because that reduces
the decimation ratio of the downstream non-CIC filter blocks.

But pass band ripple is not the only consideration. There's also the anti-aliasing
performance requirement as specified by the stop band attenuation.

# CIC Filter Configuration and Anti-Aliasing Performance

In [this section](/2020/09/30/Moving-Average-and-CIC-Filters.html#moving-average-filters-as-decimator)
of my blog post about CIC filters, I show how the frequency of the pass band determines
the amount of aliasing of higher frequencies into the pass band after decimation: the closer
the pass band frequency to the overall output bandwidth, the more stages are needed to 
achieve a certain anti-aliasing performance.

For example, at frequency of 2000Hz, the CIC filter below attenuates aliased frequencies
by at least 92.4dB. If we were to reduce this frequency to 1000Hz, this attenuation
would go up to ~115dB.

![Anti-Alias Performance](/assets/pdm/cic_filters/cic_decimation_lower_freqs.svg)

This attenuation number also depends on the number of CIC stages and the decimation ratio. The 
design requirement of our filter requires a stop band attenuation of 89dB. 
Just like with the pass band ripple, we need a table that shows which CIC
parameters have sufficient attenuation at the stop band frequency of 10kHz:

<table>
<caption style="text-align:center"><b>Stop Band Attenuation (dB)</b><br/>Decimation Ratio / Nr of CIC Stages</caption>
<tr>    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
</tr>
<tr>
    <th>2</th>
    <td style="background-color:#e0a0a0">-37.3</td>
    <td style="background-color:#e0a0a0">-74.6</td>
    <td style="background-color:#a0e0a0">-112.0</td>
    <td style="background-color:#a0e0a0">-149.3</td>
    <td style="background-color:#a0e0a0">-186.6</td>
    <td style="background-color:#a0e0a0">-223.9</td>
</tr>
<tr>
    <th>4</th>
    <td style="background-color:#e0a0a0">-34.2</td>
    <td style="background-color:#e0a0a0">-68.4</td>
    <td style="background-color:#a0e0a0">-102.6</td>
    <td style="background-color:#a0e0a0">-136.8</td>
    <td style="background-color:#a0e0a0">-171.0</td>
    <td style="background-color:#a0e0a0">-205.2</td>
</tr>
<tr>
    <th>6</th>
    <td style="background-color:#e0a0a0">-31.1</td>
    <td style="background-color:#e0a0a0">-62.2</td>
    <td style="background-color:#a0e0a0">-93.3</td>
    <td style="background-color:#a0e0a0">-124.4</td>
    <td style="background-color:#a0e0a0">-155.5</td>
    <td style="background-color:#a0e0a0">-186.6</td>
</tr>
<tr>
    <th>8</th>
    <td style="background-color:#e0a0a0">-28.7</td>
    <td style="background-color:#e0a0a0">-57.4</td>
    <td style="background-color:#e0a0a0">-86.1</td>
    <td style="background-color:#a0e0a0">-114.8</td>
    <td style="background-color:#a0e0a0">-143.5</td>
    <td style="background-color:#a0e0a0">-172.2</td>
</tr>
<tr>
    <th>12</th>
    <td style="background-color:#e0a0a0">-25.2</td>
    <td style="background-color:#e0a0a0">-50.3</td>
    <td style="background-color:#e0a0a0">-75.5</td>
    <td style="background-color:#a0e0a0">-100.6</td>
    <td style="background-color:#a0e0a0">-125.8</td>
    <td style="background-color:#a0e0a0">-150.9</td>
</tr>
<tr>
    <th>16</th>
    <td style="background-color:#e0a0a0">-22.6</td>
    <td style="background-color:#e0a0a0">-45.2</td>
    <td style="background-color:#e0a0a0">-67.7</td>
    <td style="background-color:#a0e0a0">-90.3</td>
    <td style="background-color:#a0e0a0">-112.9</td>
    <td style="background-color:#a0e0a0">-135.5</td>
</tr>
<tr>
    <th>24</th>
    <td style="background-color:#e0a0a0">-18.8</td>
    <td style="background-color:#e0a0a0">-37.7</td>
    <td style="background-color:#e0a0a0">-56.5</td>
    <td style="background-color:#e0a0a0">-75.3</td>
    <td style="background-color:#a0e0a0">-94.2</td>
    <td style="background-color:#a0e0a0">-113.0</td>
</tr>
<tr>
    <th>48</th>
    <td style="background-color:#e0a0a0">-12.2</td>
    <td style="background-color:#e0a0a0">-24.4</td>
    <td style="background-color:#e0a0a0">-36.6</td>
    <td style="background-color:#e0a0a0">-48.8</td>
    <td style="background-color:#e0a0a0">-61.0</td>
    <td style="background-color:#e0a0a0">-73.2</td>
</tr>
</table>

From all the green entries above, it's best to choose those with
the lowest number of CIC stages: 
[a higher number of stages increases the width of the accumulation and delay registers](/2020/09/30/Moving-Average-and-CIC-Filters.html#the-size-of-the-delay-elements-in-a-cic-filter), 
which also increases the time delay through the adders.

# Final CIC Filter Configuration

Let's combine these 2 tables to find the CIC parameters that satisfy both 
pass band and stop band requirements:

<table>
<caption style="text-align:center"><b>Pass Band/Stop Band Attenuation (dB)</b><br/>Decimation Ratio / Nr of CIC Stages</caption>
<tr>    <th></th>
    <th>1</th>
    <th>2</th>
    <th>3</th>
    <th>4</th>
    <th>5</th>
    <th>6</th>
</tr>
<tr>
    <th>2</th>
    <td style="background-color:#e0a0a0">-0.000<br/>-37.3</td>
    <td style="background-color:#e0a0a0">-0.001<br/>-74.6</td>
    <td style="background-color:#a0e0a0">-0.001<br/>-112.0</td>
    <td style="background-color:#a0e0a0">-0.001<br/>-149.3</td>
    <td style="background-color:#a0e0a0">-0.001<br/>-186.6</td>
    <td style="background-color:#a0e0a0">-0.002<br/>-223.9</td>
</tr>
<tr>
    <th>4</th>
    <td style="background-color:#e0a0a0">-0.001<br/>-34.2</td>
    <td style="background-color:#e0a0a0">-0.003<br/>-68.4</td>
    <td style="background-color:#a0e0a0">-0.004<br/>-102.6</td>
    <td style="background-color:#a0e0a0">-0.006<br/>-136.8</td>
    <td style="background-color:#a0e0a0">-0.007<br/>-171.0</td>
    <td style="background-color:#a0e0a0">-0.009<br/>-205.2</td>
</tr>
<tr>
    <th>6</th>
    <td style="background-color:#e0a0a0">-0.003<br/>-31.1</td>
    <td style="background-color:#e0a0a0">-0.007<br/>-62.2</td>
    <td style="background-color:#a0e0a0">-0.010<br/>-93.3</td>
    <td style="background-color:#a0e0a0">-0.014<br/>-124.4</td>
    <td style="background-color:#a0e0a0">-0.017<br/>-155.5</td>
    <td style="background-color:#a0e0a0">-0.021<br/>-186.6</td>
</tr>
<tr>
    <th>8</th>
    <td style="background-color:#e0a0a0">-0.006<br/>-28.7</td>
    <td style="background-color:#e0a0a0">-0.012<br/>-57.4</td>
    <td style="background-color:#e0a0a0">-0.019<br/>-86.1</td>
    <td style="background-color:#a0e0a0">-0.025<br/>-114.8</td>
    <td style="background-color:#a0e0a0">-0.031<br/>-143.5</td>
    <td style="background-color:#a0e0a0">-0.037<br/>-172.2</td>
</tr>
<tr>
    <th>12</th>
    <td style="background-color:#e0a0a0">-0.014<br/>-25.2</td>
    <td style="background-color:#e0a0a0">-0.028<br/>-50.3</td>
    <td style="background-color:#e0a0a0">-0.042<br/>-75.5</td>
    <td style="background-color:#e0a0a0">-0.056<br/>-100.6</td>
    <td style="background-color:#e0a0a0">-0.071<br/>-125.8</td>
    <td style="background-color:#e0a0a0">-0.085<br/>-150.9</td>
</tr>
<tr>
    <th>16</th>
    <td style="background-color:#e0a0a0">-0.025<br/>-22.6</td>
    <td style="background-color:#e0a0a0">-0.050<br/>-45.2</td>
    <td style="background-color:#e0a0a0">-0.075<br/>-67.7</td>
    <td style="background-color:#e0a0a0">-0.100<br/>-90.3</td>
    <td style="background-color:#e0a0a0">-0.126<br/>-112.9</td>
    <td style="background-color:#e0a0a0">-0.151<br/>-135.5</td>
</tr>
<tr>
    <th>24</th>
    <td style="background-color:#e0a0a0">-0.057<br/>-18.8</td>
    <td style="background-color:#e0a0a0">-0.114<br/>-37.7</td>
    <td style="background-color:#e0a0a0">-0.170<br/>-56.5</td>
    <td style="background-color:#e0a0a0">-0.227<br/>-75.3</td>
    <td style="background-color:#e0a0a0">-0.284<br/>-94.2</td>
    <td style="background-color:#e0a0a0">-0.341<br/>-113.0</td>
</tr>
<tr>
    <th>48</th>
    <td style="background-color:#e0a0a0">-0.219<br/>-12.2</td>
    <td style="background-color:#e0a0a0">-0.438<br/>-24.4</td>
    <td style="background-color:#e0a0a0">-0.657<br/>-36.6</td>
    <td style="background-color:#e0a0a0">-0.876<br/>-48.8</td>
    <td style="background-color:#e0a0a0">-1.095<br/>-61.0</td>
    <td style="background-color:#e0a0a0">-1.314<br/>-73.2</td>
</tr>
</table>

From all the green cells above, the best solutions are those with the lowest
number of CIC stages and highest decimation ratio:

* 6x decimation ratio with 3 stages

    This option requires 3 half-band filters to decimate by 8 and 1 
    generic FIR filter to satisfy final pass-band and stop-band attenuation.

* 8x decimation ratio with 4 stages

    This requires the remaining 6x decimation ratio to be done with 1 half-band filter to decimate by
    2x, followed by some generic FIR configuraton for the final 3x decimation.

    There are 2 options for this generic FIR configuraiton:

    * 1 generic FIR filter to decimate by 3x followed by 1 generic FIR filter for the
    final pass-band and stop-band attenuation
    * 1 generic FIR filter that immediately applies the final pass-band and stop-band
    attenuation

It is not at all obvious which of the 3 options above is most optimal in terms of number of
multiplications! The best way forward is to just try all 3 and see what comes out as optimal.

However, a closer look at the table above shows that the CIC configuration with  12x decimation ratio
and 4 stages comes very close to passing the overall requirements, with a pass band ripple of 0.056dB,
only 0.06dB higher than your 0.05dB limit.

And the thing is: that 0.05dB was chosen rather arbitrarily. We can just as arbitrarily increase that limit
a bit, make this case pass, and end up with a overall filter architecture that might very well be
better than the 3 earlier ones:

* 12x decimation ratio with 4 stages

    This requires 2 half-band filters to decimate by 4 and  1 generic FIR filter for the
    final pass-band and stop-band requirements.


# Design of the Half-Band and Generic FIR Filters

Once the properties of the CIC filter has been decided, the half-band and generic FIR filter
design is mostly a matter of just filling in the numbers and running the Parks-McClellan/Remez
algorithm to come up with the exact filter coefficients.

The table below shows the resul for all 4 filter architecture candidates:

<table>
<tr>
    <th>CIC Config</th>
    <th>HB1 mul/s</th>
    <th>HB2 mul/s</th>
    <th>HB3 mul/s</th>
    <th>Decim FIR mul/s</th>
    <th>Final FIR mul/s</th>
    <th>Total mul/s</th>
</tr>
<tr>
    <td>Decim:6<br/>Stages:3</td>
    <td>4 x 192k = 768k</td>
    <td>6 x 96k = 576k</td>
    <td>10 x 48k = 480k</td>
    <td></td>
    <td>47 x 48k = 2256k</td>
    <td>4080k</td>
</tr>
<tr>
    <td>Decim:8<br/>Stages:4</td>
    <td>6 x 144k = 864k</td>
    <td></td>
    <td></td>
    <td>21 x 48k = 1008k</td>
    <td>51 x 48k = 2448k</td>
    <td>4320k</td>
</tr>
<tr>
    <td>Decim:8<br/>Stages:4</td>
    <td>6 x 144k = 864k</td>
    <td></td>
    <td></td>
    <td></td>
    <td>141 x 48k = 6768k</td>
    <td>7632k</td>
</tr>
<tr>
    <td>Decim:12<br/>Stages:4</td>
    <td>6 x 96k = 576k</td>
    <td>10 x 48k = 480k</td>
    <td></td>
    <td></td>
    <td>51 x 48k = 2448k</td>
    <td>3504k</td>
</tr>
</table>

It turns out that the solution with 12 stages is indeed the optimal one.

The [naive single-stage FIR filter](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html#pdm-to-pcm-first-try-just-filter-the-damn-thing) 
that I used as initial stake in the ground required 106M mul/s. This number has been reduced to
3.5M multiplications per second, an improvement of more than 30x!

Here are some conclusions based on the table above:

* whenever possible, try to use half-band filters for all decimation operations. Using
  a generic FIR filter as decimation stage has a significant cost.
* if you have to use a generic FIR filter for decimation (e.g. because the overall decimation ratio
  doesn't have a factor of 2), don't merge it with the final FIR filter
* play around with the pass band ripple portion that's assigned to the CIC filter to find the
  optimal solution

Here's a pretty diagram that shows the sequence of all operations:

![All Filter Operations](/assets/pdm/pdm2pcm/pdm2pcm-all_filter_operations.svg)

# Coming Up

The architecture of decimation pipeline is now complete, but there's still things of to come:

* convert theory to practise, implement everything to RTL, and run things on an FPGA
* check how a CIC compensation filter would reduce the number of multiplications even more

# References

**My Blog Posts in this Series**

* [An Intuitive Look at Moving Average and CIC Filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
* [PDM Microphones and Sigma-Delta A/D Conversion](/2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html)
* [Designing Generic FIR Filters with pyFDA and NumPy](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
* [From Microphone Datasheet to Filter Design Specification](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html)
* [Half-Band Filters, a Workhorse of Decimation Filters](/2020/12/15/Half-Band-Filters-A-Workhorse-of-Decimation-Filters.html)
* [Design of a Multi-Stage PDM to PCM Decimation Pipeline](/2020/12/20/Design-of-a-Multi-Stage-PDM-to-PCM-Decimation-Pipeline.html)

**Decimation**

* [Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf)

    Paper that discusses how to size cascaded filter to optimized for FIR filter complexity.

* [Seamlessly Interfacing MEMS Microphones with Blackfin Processors](https://www.analog.com/media/en/technical-documentation/application-notes/EE-350rev1.pdf)

    Analog Devices application note. C code can be found [here](https://www.analog.com/media/en/technical-documentation/application-notes/EE350v01.zip)

* XMOS Microphone array library

    https://www.xmos.ai/download/lib_mic_array-%5buserguide%5d(3.0.1rc1).pdf

    Lots of technical info about PDM to PCM decimation.


