---
layout: post
title: Polyphase Decimation Filter Banks
date:   2026-02-08 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Where We Left Things Last Time

I ended my [previous blog about complex heterodynes](/2026/02/07/Complex-Heterodyne.html)
with questions about the efficiency of implementing it as a low pass filter
that is followed by a decimation.

Here's a quick recap of that pipeline:

![Rotator, LPF, decimator](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

* $$f_c$$ is the normalized center frequency of the channel that we're interested in. 
  In our example, the sample rate $$F_s = 100 \text{MHz}$$ and the channel center frequency
  $$F_c = 20 \text{MHz}$$ so $$f_c = 0.2$$. Further down, I'll often use $$\omega_c = 2 \pi f_c$$
  because that makes equations less cluttered.
* Each channel has a 10 MHz bandwidth. Since there is no negative mirror spectrum, once the
  channel has been moved to baseband, we can decimate by a factor 10.
* $$H_\text{lpf}(z)$$ is an FIR with 201 real taps and a linear phase[^linear_phase]. 

Check out my [section with common DSP notations](/2026/02/07/Complex-Heterodyne.html#some-common-dsp-notations)
for a general overview symbols used in math formulas.

[^linear_phase]: Whether or not an FIR is linear phase depends on its coefficients, but most
                 common methods to determine those result in a linear phase filter.

# Ignoring Linear Phase FIR Coefficient Symmetry

Linear phase FIR filters have the desirable property that their coefficients are symmetric
around the center tap. Here's a random example:

$$
H(z) = -1 + 3 z^{-1} - 6 z^{-2} + 10 z^{-3} - 6 z^{-4} + 3 z^{-5} - z^{-6}
$$

This filter has 7 coefficients, the center coefficient is 10, the ones to the left and right of 
it are both -6 and so forth.

When you convert a DSP algorithm to hardware that needs to consume an input sample and produce
and output for every clock tick, the straightfoward implentation is to have one multiplier per
coefficient. 

![FIR without optimized multipliers](/assets/polyphase/polyphase_het/polyphase_het-fir_no_optimized_muls.svg)

Since multipliers are often a scarce resource, you can reduce their number by
almost half by rearranging the equation as follows:

$$
H(z) = -1 (1 + z^{-6})  + 3 (z^{-1} + z^{-5} ) - 6 (z^{-2} + z^{-4})  + 10 z^{-3}
$$

We've removed 3 out of 7 multipliers.

![FIR with optimized multipliers](/assets/polyphase/polyphase_het/polyphase_het-fir_optimized_muls.svg)

This works, but you need to trade off the reduction in multipliers against an increase in wiring
to get the 2 operands to the addition that feeds the multiplier. On FPGAs, wiring congestion is
a real concern so it's not always a slam dunk.

If you have a hardware architecture where delayed input are stored in a RAM instead of individual
registers and you use an FSM to execute the filter over multiple clock cycles, trying to do this
trick can make scheduling transactions more complicated too. 

And when converting the FIR into a polyphase filter, the simple symmetry breaks entirely. Here's
an example of a symmetrical 19-tap filter. In it's original form, coefficients are symmetric, but
when split up into 10 phases, the symmetry inside each phase is gone.

![19-tap filter split up into 10 phases](/assets/polyphase/polyphase_het/polyphase_het-tap_symmetry_19.svg)

It's still possible to share multiplications if you merge multiple phases, note how phase 2 has
coefficients 6 and 2 and phase 7 has coefficients 2 and 6, but that again make data organization
and movement more difficult.

For the remainder of this blog post, I will ignore symmetric related optimizations when calculating
the number of multiplications.

# Performance Baseline 

I will use multiplication as the main indicator by which to judge the efficiency of a DSP algorithm.

Let's evaluate the number of multiplications for this architecture:

* The complex mixer multiplies a real sample with a complex number or 2 per operation.
  Good for 200M per second.
* The low pass filter has 201 real taps, for a total of 201 x 2 x 100M = 
  40.2B operations per second.

Total: 40.4B multiplications per second!

This is our baseline, and it's a lot. Let's see what we can do about this...

# Straightforward Polyphase Filtering and Decimation

There's a reason why I also wrote 
[Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html):
it discusses exactly this kind of scenario, the combo of an FIR filter followed by a decimation. Yes,
there's a complex rotator in front of the FIR filter, but for now we can keep it there 
while we transfrom the FIR/decimator to its polyphase form.

First split the FIR filter in as many sub-filters as the decimation factor:

![Complex heterodyne - Polyphase - Decimation](/assets/polyphase/polyphase_het/polyphase_het-complex_het_polyphase_decim.svg)

Apply the [noble identity for decimation](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html#the-noble-identity-for-decimation):

![Complex heterodyne - Decimation - Polyphase](/assets/polyphase/polyphase_het/polyphase_het-complex_het_decim_polyphase.svg)

Moving the FIR filter operation behind the decimator is a huge savings. The complex mixer still counts
for 200M multiplications per second, but the combined 201 taps now need to deliver samples at a 10 times
lower rate, 201 x 2 x 10M = 4.02B operations per second, for a total of 4.22B operations per second.

The complex rotator can be moved after the the decimator, like this:

![Decimation - Complex heterodyne - Polyphase](/assets/polyphase/polyphase_het/polyphase_het-decim_complex_het_polyphase.svg)

This doesn't really help us, though, the number of rotations/multiplications per decimated output sample
is still the same.

# The Free-Running Rotator

One thing to note here is that the complex rotator consists of the input signal being multiplied by
the output of a free-running oscillator. There are no major restrictions on rotation
rate $$\omega_c$$.

If we have a decimation factor of 10 and we want the center frequencies of the channel to be a multiple
of the sample frequency divided by the decimation factor ($$F_c = k F_s/M$$)


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

