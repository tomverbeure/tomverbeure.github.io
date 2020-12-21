---
layout: post
title: Filtering Down PDM to PCM
date:  2020-10-19 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In the [past 5 episodes of this series](#references)), I discussed 
sigma-delta converters, how to read the datasheet of a microphone, different types 
of filters, and how to come up with the right coefficients of these filters.

Finally, it's time to bring everything together and design the full signal 
processing pipeline to convert the output of a [PDM](https://en.wikipedia.org/wiki/Pulse-density_modulation) 
microphone into standard [PCM](https://en.wikipedia.org/wiki/Pulse-code_modulation) samples. 

The goal of this series is to improve my general DSP knowledge. The application itself is 
only a means to an end. Most important is understanding the why and how of every single design 
decision along the way: if there's a filter with stop band attenuation X that starts at
frequency Y, I want to know the justification for that.

# The Design Requirements 

Let's quickly repeat the design requirements that I came up with in 
[an blog post](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html#pdm-to-pcm-design-requirements):

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
there seems to be an almost infinite amount of subtle variations, the fundamentals can
almost always be reduced to the following basic building blocks: a CIC filter at the front,
one or more half-band filters in the middle, and a generic FIR filter at the back.

![Canonical Decimation Pipeline](/assets/pdm/pdm2pcm/pdm2pcm-canonical_pipeline.svg)

The reason for this arrangement is obvious when you consider typical design constraints of
clock speeds, and resource usage.

1. A CIC filter only requires adders and delay stages, no multipliers, which makes them extremely
   area efficient.
1. The lack of multipliers also makes it much easier to run CIC filters at high clock speed.
1. A half-band filter requires only around 50% of the multiplications of an equivalent
   generic FIR filter. This reduction is at all times large enough to overcome the
   inefficiency of splitting a larger generic FIR filter into a cascaded half-band filter 
   and a FIR filter that has half the order of the original one.

With the core pipeline in place, the next step is figuring out the exact filter parameters for
each stage.

# CIC Filter Configuration and Pass Band Ripple

Since they don't require any multiplications at all, it's desirably to shift as much as
of the decimation to the front-end CIC filter.

One problem with CIC filters, however, is that the pass band ripple gets progressively
worse with increasing frequency and with increasing number of cascade stages.

Without using a counter measure in the form of a compensation filter, the frequency response
in the pass band can easily exceed the maximum ripple requirements of the overall
filter specification.

**Pass band ripple and decimation ratio**

Our overall filter has an overall decimation ratio of 48, and the 8 possible CIC decimation
ratios: 2, 4, 6, 8, 12, 16, 24, 48.

For a 5 stage configuration, these 8 options give the following magnitude frequency plots:

![All decimation ratios for a 5 stage CIC filter](/assets/pdm/pdm2pcm/cic_ratios_overview.svg)

That tiny rectangle in the top left corner shows the output bandwidth from 0 to 24kHz, our final
bandwidth. Let's zoom in on that:

![All decimation ratios for a 5 stage CIC filter - Zoom](/assets/pdm/pdm2pcm/cic_ratios_zoom.svg)

The rectangle now shows the pass band range from 0 to 6kHz and the maximum pass band ripple
boundary of 0.1dB.

You can see how a decimation ratio of 16 and higher violates the maximum ripple requirements,
and that's before taking into account that the filters that follow the CIC stage need to have
some remaining ripple as well.

**Pass band ripple and number of cascaded stages**

In the graphs above, I use an example with 5 stages with variable decimation rate. 

We can do the same with fix decimation rate and a variable number of stages:

![Fixed Decimation Rate, Variable Number of Stage CIC filter - Zoom](/assets/pdm/pdm2pcm/cic_stages_zoom.svg)

The result is more predictable, but similar: higher number of stages increases the pass band ripple.

One way to solve this issue is to add a compensation filter with a gain in the pass band region that is 
the exactly opposite of the chosen CIC filter, thus resulting in a flat pass band behavior. 
But that's something for a future blog post.

**Pass band ripple table: decimation ratio vs number of stages**

For simplicity, we will just need to limit decimation ratio and/or the number of stages
such that the pass band ripple doesn't exceed a certain maximum value. This maximum
value should be less than the 0.1dB pass band ripple of the overall filter: there must be
some margin left for the filter stages that follow the CIC filter!

Let's choose a maximum ripple of 0.5dB.

The table below lists all the combinations of decimation ratio and number of CIC stages, and
their ripple. The entries in green are the ones that don't violate the 0.5dB maximum:

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

If pass band ripple was the only design criterium, the best choice
would be a solution with the highest decimation ratio,  because that reduces
the decimation ratio of the downstream non-CIC filter blocks.

But pass band ripple is not the only consideration. There's also a anti-aliasing
performance requirement.

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

It should be clear that this attenuation number also depends on the number of CIC stages and the
decimation ratio. The design requirement of our filter specifies a stop band attenuation of
89dB. Just like the pass band ripple, we need to make a table that shows which CIC
parameters have sufficient attenuation at the stop band frequency of 10kHz.

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
the lowest number of CIC stages: a higher number of stages increases
the width of the accumulation and delay registers to avoid overflow, which
increases the number of registers as well as the timing path through
the adders.

# Final CIC Filter Configuration

Let's combine the 2 earlier tables to find all the entries that satisfy both
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

From all the green cells above, the best solution is the one with the lowest
number of CIC stages and highest decimation ratio:

* 6x decimation ratio with 3 stages

    This option requires 3 half-band filters to decimate by 8 + 1 
    generic FIR filter to satisfy final pass-band and stop-band requirements.

* 8x decimation ratio with 4 stages

    This requires a 6x decimation ratio with 1 half-band filter to decimate by
    2x, 1 generic FIR filter to decimate by 3x, and 1 generic FIR filter for the
    final pass-band and stop-band requirements.

    Alternatively, the 2 generic FIR filters can be combined into 1 generic FIR filter.

It is not at all clear which of the 3 options above is most optimal in terms of number of
multiplications! The best way forward is to just try all 3 and see what comes out as optimal.

However, a closer look at the table above shows that the combination of 12x decimation ratio
and 4 stages came very close to passing the requirements, with a pass band ripple of 0.056dB,
only 0.06dB higher than your 0.05dB limit.

The thing is: that 0.05dB was chosen rather arbitrarily. We can just as arbitrarily increase that limit
a bit, make this case pass, and end up with a overall filter architecture that's without question
better than the other ones:

* 12x decimation ratio with 4 stages

    This requires 2 half-band filters to decimation by 4 + 1 generic FIR filter for the
    final pass-band and stop-band requirements.


    ![All Filter Operations](/assets/pdm/pdm2pcm/pdm2pcm-all_filter_operations.svg)

# Design of the Half-Band and Generic FIR Filters

Once the properties of the CIC filter has been decided, the half-band and generic FIR filter
design is mostly a matter of just filling in the numbers and running the Parks-McClellan/Remez
algorithm to come up with the exact filter coefficients.

While it's certain that the 12x decimation CIC filter will give the best result, I still
wanted to know how much the difference of the 3 other configurations, so I include these here as well:

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

**My Blog Posts in this Series**

* [An Intuitive Look at Moving Average and CIC Filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
* [PDM Microphones and Sigma-Delta A/D Conversion](/2020/10/04/PDM-Microphones-and-Sigma-Delta-Conversion.html)
* [Designing Generic FIR Filters with pyFDA and NumPy](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html)
* [From Microphone Datasheet to Filter Design Specification](/2020/10/17/From-Microphone-Datasheet-to-Design-Specification.html)
* [Half-Band Filters, a Workhorse of Decimation Filters](/2020/12/15/Half-Band-Filters-A-Workhorse-of-Decimation-Filters.html)

**Filter Design**

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

