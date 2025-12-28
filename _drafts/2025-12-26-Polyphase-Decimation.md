---
layout: post
title: Polyphase Decimation
date:   2025-12-26 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Introduction

I'm trying to understand polyphase filters and polyphase filter banks better. 
In this blog post I write things down to better internalize things. Don't assume 
I know what I'm doing, I don't..

# Naive Decimation

Apply the filter to all input samples at the input sample rate. Then decimate.

![Filter then decimate basic block diagram](/assets/polyphase/polyphase-naive_decimation_filter_basic_block_diagram.drawio.svg)

Let's do this for with 7-tap FIR filter with the following transfer function and
a decimation factor M of 3.

$$
H(z) = h_0 + h_1 z^{-1} + h_2 z^{-2} + h_3 z^{-3} + h_4 z^{-4} + h_5 z^{-5} + h_6 z^{-6}
$$

Input samples: 

$$ \cdots, x[-3], x[-2], x[-1], x[0], x[1], x[2], x[3], x[4], \cdots $$

One filtered sample for each input sample:

$$\begin{alignedat}{0}
f[0] & = h_0 x[0] &+& h_1 x[-1] &+& h_2 x[-2] &+& h_3 x[-3] &+& h_4 x[-4] &+& h_5 x[-5] &+& h_6 x[-6] \\
f[1] & = h_0 x[1] &+& h_1 x[0]  &+& h_2 x[-1] &+& h_3 x[-2] &+& h_4 x[-3] &+& h_5 x[-4] &+& h_6 x[-5] \\
f[2] & = h_0 x[2] &+& h_1 x[1]  &+& h_2 x[0]  &+& h_3 x[-1] &+& h_4 x[-2] &+& h_5 x[-3] &+& h_6 x[-4] \\
f[3] & = h_0 x[3] &+& h_1 x[2]  &+& h_2 x[1]  &+& h_3 x[0]  &+& h_4 x[-1] &+& h_5 x[-2] &+& h_6 x[-3] \\
f[4] & = h_0 x[4] &+& h_1 x[3]  &+& h_2 x[2]  &+& h_3 x[1]  &+& h_4 x[0]  &+& h_5 x[-1] &+& h_6 x[-2] \\
f[5] & = h_0 x[5] &+& h_1 x[4]  &+& h_2 x[3]  &+& h_3 x[2]  &+& h_4 x[1]  &+& h_5 x[0]  &+& h_6 x[-1] \\
f[6] & = h_0 x[6] &+& h_1 x[5]  &+& h_2 x[4]  &+& h_3 x[3]  &+& h_4 x[2]  &+& h_5 x[1]  &+& h_6 x[0]  \\
f[7] & = h_0 x[7] &+& h_1 x[6]  &+& h_2 x[5]  &+& h_3 x[4]  &+& h_4 x[3]  &+& h_5 x[2]  &+& h_6 x[1]  \\
f[8] & = h_0 x[8] &+& h_1 x[7]  &+& h_2 x[6]  &+& h_3 x[5]  &+& h_4 x[4]  &+& h_5 x[3]  &+& h_6 x[2]  \\
f[9] & = h_0 x[9] &+& h_1 x[8]  &+& h_2 x[7]  &+& h_3 x[6]  &+& h_4 x[5]  &+& h_5 x[4]  &+& h_6 x[3]  \\
\end{alignedat}$$

Decimated by selecting 1 out of every 3 filtered sample:

$$\begin{alignedat}{0}
y[0] & = f[0] \\
y[1] & = f[3] \\
y[2] & = f[6] \\
y[3] & = x[0] \\
\end{alignedat}$$

A straight up hardware implementation looks like this:

![Naive decimation filter](/assets/polyphase/polyphase-naive_decimation_filter.drawio.svg)

This solution is dumb: 2 out of 3 filter outputs are thrown away. Let's do better.

# Reduce number of calculations - Move decimator before multiplier

We can reduce the number of calculations by moving the decimator before the filter.

$$\begin{alignedat}{0}
y[0] & = h_0 x[0] &+& h_1 x[-1] &+& h_2 x[-2] &+& h_3 x[-3] &+& h_4 x[-4] &+& h_5 x[-5] &+& h_6 x[-6] \\
y[1] & = h_0 x[3] &+& h_1 x[2]  &+& h_2 x[1]  &+& h_3 x[0]  &+& h_4 x[-1] &+& h_5 x[-2] &+& h_6 x[-3] \\
y[2] & = h_0 x[6] &+& h_1 x[5]  &+& h_2 x[4]  &+& h_3 x[3]  &+& h_4 x[2]  &+& h_5 x[1]  &+& h_6 x[0]  \\
y[3] & = h_0 x[9] &+& h_1 x[8]  &+& h_2 x[7]  &+& h_3 x[6]  &+& h_4 x[5]  &+& h_5 x[4]  &+& h_6 x[3]  \\
\end{alignedat}$$

All multiplications happen at the same time but they can now be formed in the slow clock domain. This 
definitely reduces power and also reduces the multiplication area in an ASIC process, because timing paths won't 
be as strict.

![Decimate input values, multiply in slow domain](/assets/polyphase/polyphase-delay_input_multiply_in_slow_domain.drawio.svg)

While the number of multiplications per unit of time has been reduced by 3, the number of multipliers is
still the same. 

The data flowing through this architecture looks like this:

![Decimate input value, multiply in slow domain, annotated](/assets/polyphase/polyphase-delay_input_multiply_in_slow_domain_annotated.drawio.svg)

One thing that's immediately obvious is that the pipes of input samples with the same color
have the same data flowing through them.

# Perform multiplication in the fast clock domain

In a polyphase filter, the multiplications of the filtering operation are moved back into 
fast clock domain, but split over multiple phases, where the number of phases is equal to the
decimation factor.

The equation output  $$y[2]$$ is still the same, but I've grouped the different terms that
are calculated per phase by color:

$$
y[2] = \color{red}{h_0 x[6]} + \color{green}{h_1 x[5]}  + \color{blue}{h_2 x[4]}  + \color{red}{h_3 x[3]}  + \color{green}{h_4 x[2]}  + \color{blue}{h_5 x[1]}  + \color{red}{h_6 x[0]} \\
$$

Split up in 3 steps:

$$
\begin{alignedat}{0}
\mathrm{tmp} &=& \color{red}{h_0 x[6]} &\;+\;& \color{red}  {h_3 x[3]} &\;+\;& \color{red}  {h_6 x[0]} \\
\mathrm{tmp} &=&          &&                   \color{green}{h_2 x[4]} &\;+\;& \color{green}{h_5 x[1]} &\;+\;& \mathrm{tmp} \\
y[2]         &=&          &&                   \color{blue} {h_1 x[5]} &\;+\;& \color{blue} {h_4 x[2]} &\;+\;& \mathrm{tmp} \\
\end{alignedat}
$$

Everything now happens in the fast clock domain, but there are only 3 multipliers instead of 7.
There is only one $$ y[m] $$ output every 3 clock cycles.

![Delay input - multiply in fast domain](/assets/polyphase/polyphase-delay_input_multiply_in_fast_domain.drawio.svg)

Here's the same diagram annotated with intermediates values for different time steps:

![Delay input - multiply in fast domain, internal values](/assets/polyphase/polyphase-delay_input_multiply_in_fast_domain_annotated.drawio.svg)

# Delayed multiplications intead of delayed inputs

In the previous case, the inputs are delayed and the multiplications added. We can rearrange
the terms and delay multiplication results before they are added:

$$
m_0[0] = \color{red}{h_6 x[0]} \\
m_0[1] = \color{red}{h_3 x[0]} \\
m_0[2] = \color{red}{h_0 x[0]} \\
$$

$$
m_1[0] = \color{red}{h_5 x[1]} \\
m_1[1] = \color{red}{h_2 x[1]} \\
m_1[2] = 0 \\
$$

$$
m_2[0] = \color{red}{h_4 x[2]} \\
m_2[1] = \color{red}{h_1 x[2]} \\
m_2[2] = 0 \\
$$

y[2] = \color{blue}{h_0 x[6]} + \color{green}{h_1 x[5]}  + \color{green}{h_2 x[4]}  + \color{green}{h_3 x[3]}  + \color{red}{h_4 x[2]}  + \color{red}{h_5 x[1]}  + \color{red}{h_6 x[0]} \\
$$



![Delayed multiplication results](/assets/polyphase/polyphase-multiply_in_fast_domain_delay_multiplications.drawio.svg)

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


