---
layout: post
title: Non-Critically Sampled Polyphase Channelizers
date:   2026-06-22 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Introduction

My previous episodes about the polyphase channelizer assumed a decimation factor that is the
same as the number of channels. That is a common configuration, but it doesn't have to be like
that.

In [the video](https://youtu.be/afU9f5MuXr8?t=2949) 
on which this blog post series is based, fred harris makes a strong case for filter that
consists of a 3-stage pipeline of a decimation polyphase filter, a decimating half-band filter, and
an interpolation polyphase filter to reduce the number of multiplications. Instead of 
1 M:1 decimation filter, the polyphase filter does a M:2 decimation and the half-band a
2:1 decimation.

This kind of configuration is beneficial when transition band is extremely narrow compared
to the input sample rate. 

with a decimation factor that is lower than the number of channels: it significantly

increases the transition band of the bandpass filter that separates the channels and with
that it also reduces the number of taps.

As was the case for the polyphase channelizer with offset, the video doesn't work out all the
details to get to a working solution. The goal of this blog post is to fill in those gaps.

# The Impact of Transition Band on Anti-Aliasing Filter Complexity

Conceptually, a polyphase channelizer receives an input stream with a sample rate $$F_s$$,




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

