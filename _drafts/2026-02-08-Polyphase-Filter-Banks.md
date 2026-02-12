---
layout: post
title: Polyphase Decimation Filter Banks
date:   2026-02-08 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Baseline

I ended previous blog with questions about the efficiency of a pipeline that consists of
a complex heterodyne, a low pass filter and decimation. 

Let's do a quick recap of where we left things with a diagram of the DSP pipeline: 

![Rotator, LPF, decimator](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

* $$f_c$$ is the normalized center frequency of the channel that we're interested in. 
  In our example, the sample rate $$F_s = 100 \text{MHz}$$ and the channel center frequency
  $$F_c = 20 \text{MHz}$$ so $$f_c = 0.2$$.
* Each channel has a 10 MHz bandwidth. Since there is no negative mirror spectrum, once the
  channel has been moved to baseband, we can decimate by a factor 10.
* $$H_\text{lpf}(z)$$ is an FIR with 201 real taps and a linear phase[^linear_phase]. 


[^linear_phase]: Whether or not an FIR is linear phase depends on its coefficients, but most
                 common methods to determine those result in a linear phase filter.

In a DSP, one of the most critical resources is multipication and the number of multiplications
per second is often used to the main indicator by which to judge the efficiency of an 
algorithm.

Let's evaluate the number of multiplications for this architecture:

* The complex mixer multiplies a real sample with a complex number or 2 per operation.
  Good for 200M per second.
* The low pass filter has 201 real taps that require 101 complex multiplications due to
  symmetry of the coefficients around the center tap, for a total of 101 x 2 x 100M = 
  20200M operations per second.

Total: 20.4G multiplications per second!

This is our baseline, and it's a lot. Let's see what we can do about this...

# Straightforward Polyphase Filtering and Decimation


![Complex heterodyne - Polyphase - Decimation](/assets/polyphase/polyphase_het/polyphase_het-complex_het_polyphase_decim.svg)

![Complex heterodyne - Decimation - Polyphase](/assets/polyphase/polyphase_het/polyphase_het-complex_het_decim_polyphase.svg)

Moving the FIR filter operation behind the decimator is a huge savings. The complex mixer still counts
for 200M multiplications per second, but combined 201 taps now need to deliver samples at a 10 times
lower rate. The 


21 taps:



# References

* [Stackexchange - How to implement Polyphase filter?](https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)

 > Making a polyphase filter implementation is quite easy; given the desired coefficients 
 > for a simple FIR filter, you distribute those same coefficients in "row to column" format 
 > into the separate polyphase FIR components

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: Fred Harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

  Spectularly good video.

* [Bit by Bit Signal Processing Tutorials - Channelizer Tutorial](https://bxbsp.com/Tutorials.html)

* [IEEE - Digital Receivers and Transmitters Using Polyphase Filter Banks for Wireless Communications](https://ieeexplore.ieee.org/document/1193158)

  Also available on scihub.

* [Spectrometers and Polyphase Filterbanks in Radio Astronomy](https://arxiv.org/pdf/1607.03579)

  Includes discussion about PFB. However, there is [this comment on Stackexchange](https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)
  about it:

  > The technique in the paper may be misnamed (or does not fit the normal use of polyphase filtering for resampling).
  >
  > ...
  >
  > This technique is sometimes called the polyphase DFT or windowed overlap-add (WOLA) processing. 


  * [PFB introduction](https://github.com/telegraphic/pfb_introduction/blob/master/pfb_introduction.ipynb)

    Jypiter PFB notebook.

  * [The Polyphase Filter Bank Technique](https://casper.berkeley.edu/wiki/The_Polyphase_Filter_Bank_Technique)

    Explains why a filter before the FFT is useful: scalloping loss and leakage.

* [DSP related - Polyphase Filters and Filterbanks](https://www.dsprelated.com/showarticle/191.php)

  Confusing...
  
* [Multirate Digital Filters, Filter Banks, Polyphase Networks, and Applications: A Tutorial](https://home.engineering.iastate.edu/~julied/classes/ee524/articles/multirate_article.pdf)

  Very long article by P. P. Vaidyanathan.
    

* [Interpolation and A Decimation of Digital Signals - Tutorial Review](https://firmware-developments.com/WEB/DOC/REF/SRC%20CROCHIERE%2001456237.pdf)

* [POLYPHASE DECOMPOSITION](https://www.dsprelated.com/freebooks/sasp/Polyphase_Decomposition.html)

  Part of SPECTRAL AUDIO SIGNAL PROCESSING book by Julius Smith.

* [INTRODUCTION TO DIGITAL FILTERS WITH AUDIO APPLICATIONS - Julius Smith](https://www.dsprelated.com/freebooks/filters/)

* [MULTIRATE SIGNAL PROCESSING](https://eeweb.engineering.nyu.edu/iselesni/EL713/zoom/mrate.pdf)

  On page 21, says that the noble identities only work in one direction, if you move the 
  decimator to the right. Rarely the other way around.

* [Designing Anaylsis and Synthesis Filterbanks in GNU Radio](https://static.squarespace.com/static/543ae9afe4b0c3b808d72acd/543aee1fe4b09162d08633d9/543aee20e4b09162d086354a/1395369129837/rondeau_gr_filtering.pdf)

 > In the channelization process, we want those aliases. Recall that the filterbanks use 
 > the same filter with a different phase. When filtering, each of the aliased zones is 
 > processed by each arm of the filterbank, which has its own phase.

# Footnotes

