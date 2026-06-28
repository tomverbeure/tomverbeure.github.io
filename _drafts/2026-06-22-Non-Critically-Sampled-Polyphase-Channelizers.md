---
layout: post
title: Revisiting the Decimation Pipeline with Polyphase Filters
date:   2026-06-22 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Introduction

I continue my quest to deconstruct fred harris' 
[Recent Interesting and Useful Enhancements of Polyphase Filter Banks](https://www.youtube.com/watch?v=afU9f5MuXr8)
lecture on YouTube, with the goal of understanding every last detail, with some additional
side quests thrown when I feel like this.

This blog post was triggered by 
[his case of a narrow band filter](https://youtu.be/afU9f5MuXr8?t=2949) 
that ultimately consists of a 3-stage pipeline with a decimation polyphase filter, 
a decimating half-band filter, and an interpolation polyphase filter to reduce the 
number of multiplications. 

I'll go through the motions of working out the details and also make the link
to my blog posts from 6 years ago about 
[half-band filters](https://tomverbeure.github.io/2020/12/15/Half-Band-Filters-A-Workhorse-of-Decimation-Filters.html)
and about [the design of a multi-stage decimation pipeline](https://tomverbeure.github.io/2020/12/20/Design-of-a-Multi-Stage-PDM-to-PCM-Decimation-Pipeline.html).

# The Impact of Transition Band on Filter Complexity

The [key observation](https://youtu.be/afU9f5MuXr8?t=2499) about FIR filter design is that 
the complexity[^filter_complexity] of the filter depends 3 parameters:

[^filter_complexity]: In this blog post, the first order indicator for filter complexity is the number of 
                      multiplications.

* sample rate $$f_s$$
* the filter transistion bandwidth $$\Delta f$$
* stopband attenuation $$A$$ in dB

So that the number of taps is:

$$ N \widetilde{=} \frac{f_s}{\Delta f} \frac{A}{20} $$

This is an approximation, of course, the final number depends on the type of filter, the pass band
ripple, the exact location of the transition band, but it's good enough for comparison.



/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html#finding-the-optimal-filter-order




# Polyphase Filter vs Polyphase + Half-Band Filter Combo

* Benefit of cascading decimation filters
* half-band blog post
* Normally, go from simple filter to more complex. Half-band if usually easier than regular FIR filter
  but need to take into account band-pass filtering.
* Filter complexity formula
* Crossover point from one to the next

[![Polyphase filter vs Polyphase - 1 Half-Band filter combo](/assets/polyphase/non_crit/poly_vs_poly_1hb_combo.svg)](/assets/polyphase/non_crit/poly_vs_poly_1hb_combo.svg)
*(Click to enlarge)*

[![Polyphase filter vs Polyphase - 2 Half-Band filter combo](/assets/polyphase/non_crit/poly_vs_poly_2hb_combo_filter.svg)](/assets/polyphase/non_crit/poly_vs_poly_2hb_combo_filter.svg)
*(Click to enlarge)*

# References

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: fred harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [Analysis Channelizers with Even and Odd Indexed Bin Centers - fred harris](https://www.dsponlineconference.com/WPMC_2020_Even_and_Odd_Bin%20Centers_5.pdf)

* [IEEE - Digital Receivers and Transmitters Using Polyphase Filter Banks for Wireless Communications](https://ieeexplore.ieee.org/document/1193158)

**Other blog posts in this series**

* [Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html)
* [Complex Heterodynes Explained](/2026/02/07/Complex-Heterodyne.html)
* [The Stunning Efficiency and Beauty of the Polyphase Channelizer](/2026/02/16/Polyphase-Channelizer.html)
* [Polyphase Channelizers with Frequency Offset - a Bluetooth LE Example](/2026/03/05/Polyphase-Channelizer-with-Offset.html)

**Source code**

* [GitHub - Polyphase Filtering Blog Series](https://github.com/tomverbeure/polyphase_blog_series)

# Footnotes

