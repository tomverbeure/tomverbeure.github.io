---
layout: post
title: An Intuitive Understanding of Dithering and Noise Shaping
date:  2022-04-24 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction


After my PDM to PCM conversion series, I've been on a bit of digital signal processing
hiatus: there's just too many projects going on in parallel.

But I've always been intrigued by the concept of dithering. It started after reading
Chapter 3 of "The Scientist and Engineer's Guide to Digital Signal Processing" (download
it [here](https://www.dspguide.com) for free!) and stumbling onto this figure:

![DSP Guide Figure 3-2: Illustration of Dithering](/assets/dither_noise_shaping/dsp_guide_dithering.png)

In the figure above, they take an original signal with a very small amplitude of only 1 LSB,
add of noise, and the resulting digitized signal represents original analog signal much better.

I think it's fascinating that adding *noise*


# References

* [A Theory of Dithered Quantization](http://www.robertwannamaker.com/writings/rw_phd.pdf)

    Math heavy, but the conclusions at the end of some chapters show the consequences of the theory.
    Intersection sections:

    * 4.4.4 Summary of Non-Subtractive Dither (page 84)

    More important take-aways: 

    * TPDF is optimal solution for NSD. However, even with a random dither signal, the 
      error is still influenced by the input signal. It's worse for RPDF. With higher order
      PDF, something else gets worse.
    * Peak to peak amplitude of the dither must be a multiple of the quantization error (1 LSB) and at least
      1 LSB for RTPF and 2 LSBs for TPDF. Otherwise, some theorem conditions are broken.

      Page 77: "Furthermode , it is important to note that using rectangular-pdf dithers of peak-to-peak 
      amplitude not equalto one LSB (or, rather, not equal to an integral number of LSB's) wiU not render 
      error moments independent of the input since the zeros of the associated sinc fimctions will not fall
      at integral multiples of 1/delta... (See [16])

    * Page 78: RPDF: mean error is zero for all inputs -> quantizer has been linearized, thus elimination distortion.
      The error variance is signal dependent, so that the noise power in the signal varies with the system input.
      This is sornetimes referred to as noise modulation, and is undesirable in many applications, such as in audio 
      where audible time-dependent error signals are considered intolerable.

    * Page 80: TPDF:  ... this dither renders both the fist and second moments of the total error independent of x.
      The second moment of the total error is a constant delta^2/4 for ail inputs... dither has eliminated both
      distortion and noise modulation. ... TPDF is the only dither which renders first and second moment of the
      total error independent while minimizing the second moment.

    * Page 82: any dither PDF outside [-delta, delta] will produce a greater error variance.

    * Page 87: noise floor of NSD is 4.8dB higher than for SD.

    * Page 103: requirements for a dither signal after going through an FIR to still create a flat
      error spectrum.

    * 5.2 Dithered Noise-Shaping Quantization Systems



* [Optimal Dither and Noise Shaping in Image Processing](https://uwspace.uwaterloo.ca/bitstream/handle/10012/3867/thesis.pdf;jsessionid=1A2C7BC03040A27F4F475541E53018E4?sequence=1)

* [Dither in Digital Audio](http://www2.ece.rochester.edu/courses/ECE472/Site/Assignments/Entries/2009/1/15_Week_1_files/Vanderkooy_1987.pdf)

* [Resolution Below the Least Significant Bit in Digital Systems with Dither](http://drewdaniels.com/dither.pdf)

* [Why 1-Bit Sigma-Delta Conversion is Unsuitable for High-Quality Applications](https://timbreluces.com/assets/sacd.pdf)

    Excellent description of simply dithered noise shaping quantizer.

