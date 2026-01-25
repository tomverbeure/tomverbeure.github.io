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

# Decimation with FIR Anti-Aliasing Filter

In digital signal processing (DSP), decimation is an operation where you retain
1 out of every M samples. It has the benefit of bringing the sample rate down,
and thus the amount of data that flows through the system, the clock speeds, 
the number of calculations etc. Decimation is a very common operation.

When following DSP theory, if you want to decimate a signal from a sample
rate $$f_s$$ to a sample rate $$f_{s/M}$$, you first need to apply an anti-aliasing 
filter that removes all the frequeny components above $$f_s/(2 \cdot M)$$ to make sure
that the Nyquist criterium remains valid after the sample frequency has
been reduced.

When using an FIR filter, the conceptual block diagram then looks like this:

![Filter then decimate basic block diagram](/assets/polyphase/polyphase-naive_decimation_filter_basic_block_diagram.drawio.svg)

Let's do this with 7-tap FIR filter that has transfer function $$H(z)$$ and
a decimation factor M of 3.

$$
H(z) = h_0 + h_1 z^{-1} + h_2 z^{-2} + h_3 z^{-3} + h_4 z^{-4} + h_5 z^{-5} + h_6 z^{-6}
$$

In this kind of notation, $$z^{-2}$$ means input value that was delayed by 2 discrete
steps. In electronics, the equation above has a delay line of 6 elements and each
element is then multiplied by a different value.

Take the following stream of input samples

$$ \cdots, x[-3], x[-2], x[-1], x[0], x[1], x[2], x[3], x[4], \cdots $$

Now apply this stream to the filter equation for multiple steps:

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

Decimate by selecting 1 out of every 3 filtered sample:

$$\begin{alignedat}{0}
y[0] & = f[0] \\
y[1] & = f[3] \\
y[2] & = f[6] \\
y[3] & = f[9] \\
\end{alignedat}$$

Or:

$$\begin{alignedat}{0}
y[0] & = h_0 x[0] &+& h_1 x[-1] &+& h_2 x[-2] &+& h_3 x[-3] &+& h_4 x[-4] &+& h_5 x[-5] &+& h_6 x[-6] \\
y[1] & = h_0 x[3] &+& h_1 x[2]  &+& h_2 x[1]  &+& h_3 x[0]  &+& h_4 x[-1] &+& h_5 x[-2] &+& h_6 x[-3] \\
y[2] & = h_0 x[6] &+& h_1 x[5]  &+& h_2 x[4]  &+& h_3 x[3]  &+& h_4 x[2]  &+& h_5 x[1]  &+& h_6 x[0]  \\
y[3] & = h_0 x[9] &+& h_1 x[8]  &+& h_2 x[7]  &+& h_3 x[6]  &+& h_4 x[5]  &+& h_5 x[4]  &+& h_6 x[3]  \\
\end{alignedat}$$

# Naive Hardware Implementation

A straight up hardware implementation looks like this:

![Naive decimation filter](/assets/polyphase/polyphase-naive_decimation_filter.drawio.svg)

As mentioned before, we have 6 delay elements and 7 multipliers that operate on the each stage
of the delay line.

This solution is dumb: we calculate a filter output for every nput clock cycle only to throw away 2 
out of 3 results. Let's do better.

# Reduce number of calculations - Move decimator before multiplier

We can reduce the number of calculations by moving the decimator before the filter.

All multiplications still happen at the same time but they can now be performed in a clock domain that is
3 times slower. This definitely reduces power and also reduces the multiplication area in an ASIC process, 
because timing paths won't be as strict.

![Decimate input values, multiply in slow domain](/assets/polyphase/polyphase-delay_input_multiply_in_slow_domain.drawio.svg)

While the number of multiplications per unit of time has been reduced by 3, the number of multipliers is
still the same. 

The data flowing through this architecture looks like this:

![Decimate input value, multiply in slow domain, annotated](/assets/polyphase/polyphase-delay_input_multiply_in_slow_domain_annotated.drawio.svg)

When you look at bit closer, you can see that pipes of input samples with the same color
have the same data flowing through them: the input feed of the $$h_0$$ multiplier sees the
same $$x[3i]$$ samples as the $$h_3$$ and the $$h_6$$ multipliers.  It's just that there is 
a delay of 1 clock cycle in the slow clock domain for each terms.
Similarly, $$h_1$$ and $$h_5$$ see samples $$x[3i+1]$$, and $$h_2$$ and $$h_6$$ see samples 
$$x[3i+2]$$.

There is nothing we can do with that characteristic because we are using a slow clock for
the multipliers. 

# Polyphase decomposition of the original filter

Let's take the equation for value $$y[2]$$ again and decorate the 7 terms with the same colors
of the diagram:

$$
y[3] = \color{red}{h_0 x[9]} + \color{green}{h_1 x[8]}  + \color{blue}{h_2 x[7]}  + \color{red}{h_3 x[6]}  + \color{green}{h_4 x[5]}  + \color{blue}{h_5 x[4]}  + \color{red}{h_6 x[3]} 
$$


Now split the equation into 3 steps so that each step uses input values $$x[i]$$ with the same color:

$$
\begin{alignedat}{0}
\mathrm{tmp} &=& \color{red}  {h_0 x[9]} &\;+\;& \color{red}  {h_3 x[6]} &\;+\;& \color{red}  {h_6 x[3]} \\
\mathrm{tmp} &=& \color{green}{h_1 x[8]} &\;+\;& \color{green}{h_5 x[5]} && &\;+\;& \mathrm{tmp} \\
y[2]         &=& \color{blue} {h_2 x[7]} &\;+\;& \color{blue} {h_4 x[4]} && &\;+\;& \mathrm{tmp} \\
\end{alignedat}
$$

What we've done here is split 7-tap filter $$H(z)$$ into 3 separate sub-filters:

$$
H_0(z) = h_0 + h_3 z^{-1} + h_6 z^{-2} \\
H_1(z) = h_1 + h_4 z^{-1} + h_7 z^{-2} \\
H_2(z) = h_2 + h_5 z^{-1} + h_8 z^{-2} \\
$$

*(In our example, $$h_7$$ and $$h_8$$ are zero.)*

The equation of the original filter is now this:

$$
H(z) = H_0(z^3) + z^{-1} H_1(z^3) + z^{-2} H_2(z^3)
$$


**This is the polyphase decomposition of the original filter.** 

The exponent of 3 in $$z^3$$ tells us that input to each sub-filter is a decimated version, because if
we substitued in $$z^{-3}$$ into the previous equation of $$H_i(z)$$, we get:

$$
H_0(z^3) = h_0 + h_3 z^{-3} + h_6 z^{-6} \\
H_1(z^3) = h_1 + h_4 z^{-3} + h_7 z^{-6} \\
H_2(z^3) = h_2 + h_5 z^{-3} + h_8 z^{-6} \\
$$

The polyphase equation of $$H(z)$$ is now:

$$
H(z) = 
(h_0 + h_3 z^{-3} + h_6 z^{-6}) 
+ z^{-1} (h_1 + h_4 z^{-3} + h_7 z^{-6}) 
+ z^{-2} (h_2 + h_5 z^{-3} + h_8 z^{-6}) 
$$

Which becomes this:

$$
H(z) = 
  (h_0 + h_3 z^{-3} + h_6 z^{-6}) 
+ (h_1 + h_4 z^{-4} + h_7 z^{-7}) 
+ (h_2 + h_5 z^{-5} + h_8 z^{-8}) 
$$

And after reordering the terms and setting $$h_7$$ and $$h_8$$ to zero, we're back
to the definition of $$H(z)$$ at the start of this blog post:

$$
H(z) = h_0 + h_1 z^{-1} + h_2 z^{-2} + h_3 z^{-3} + h_4 z^{-4} + h_5 z^{-5} + h_6 z^{-6}
$$

# Perform multiplication in the fast clock domain

In a polyphase filter, the multiplications of the filtering operation are moved back into 
fast clock domain, but split over multiple phases. ~the number of phases is equal to the
decimation factor.

Everything now happens in the fast clock domain, but there are only 3 multipliers instead of 7.
There is only one $$ y[m] $$ output every 3 clock cycles.

![Delay input - multiply in fast domain](/assets/polyphase/polyphase-delay_input_multiply_in_fast_domain.drawio.svg)

Here's the same diagram annotated with intermediates values for different time steps:

![Delay input - multiply in fast domain, internal values](/assets/polyphase/polyphase-delay_input_multiply_in_fast_domain_annotated.drawio.svg)

# Delayed multiplications instead of delayed inputs

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

