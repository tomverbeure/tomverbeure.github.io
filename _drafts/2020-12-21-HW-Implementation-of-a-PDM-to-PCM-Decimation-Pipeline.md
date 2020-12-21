---
layout: post
title: HW Implementation of a Multi-Stage PDM to PCM Decimation Pipeline
date:  2020-12-19 00:00:00 -1000
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

