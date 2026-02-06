---
layout: post
title: Polyphase Decimation Filter Banks
date:   2026-01-25 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>



* TOC
{:toc}

TODO:

* mention analytic signal
* show with Euler identity and DTDF formula why there is a negative spectrum. 
* hint at polyphase usage
* block diagram of complex heterodyne, then FIR, then decimation

# Introduction

I my earlier blog post about [polyphase decimation](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html), my
reason for looking at that topic was "reading up on polyphase filters and multi-rate digital signal processing",
but to be more specific, it's a fantastic video by Fred Harris called 
["Recent Interesting and Useful Enchancements of Polyphase Filter Banks"][pfb_video]. The video is more than
90min long and is a lot to process when your DSP knowledge is lacking.

[pfb_video]: (https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)

I've watched the video a few times now, and while I kind of get what he's doing, I made me realize even more how skin-deep
my DSP knowledge really is.

For example, I'm know that sampling an analog signal create a positive and negative spectrum, but I couldn't really
tell you why. Or the video talks about a *complex heterodyne* of the input signal, but I can't really explain how
the outcome of that operation different from mixing an input signal with a regular sinusoid. 

I decided to fix this, dive into the subject and try to fill the holes in my knowledge. In the process, I'm obviously
running into bigger gaps: I've known for quite a while that there's such a thing as the Hilbert transformation, but
I couldn't explain what it's used for if my life depended on it.

In the blog posts, and future ones, I'm writing down some of the stuff that I've learned. 

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

