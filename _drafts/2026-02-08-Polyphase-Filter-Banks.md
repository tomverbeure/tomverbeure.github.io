---
layout: post
title: The Stunning Efficiency of the Polyphase Channelizer
date:   2026-02-13 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>


* TOC
{:toc}

# Introduction

In the past 2 blog posts, I wrote about 
[polyphase decimation filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html)
and [complex heterodynes](/2026/02/07/Complex-Heterodyne.html), the latter with
some decimation thrown in for good measure.

It's now time to put everything together, and more. First, I'll look at
the complex heterodyne/decimation combo and see how it can be implemented as
efficiently as possible. There's already some surprised in there, but to
top it off, I'll expand the solution to do the operation for multiple
channels as the same time.

The result is truly amazing.

I'm still roughly following the flow of 
[fred harris' video about polyphase filter banks](https://www.youtube.com/watch?v=afU9f5MuXr8)[^harris],
but I'll be making some detours along the way because they helped me to put things
better in context and help me with understanding the topic.

[^harris]: fred harris insists on writing his name entirely in lower case. But according to
           [this reddit comment](https://www.reddit.com/r/DSP/comments/1cyrh9/comment/c9lwtot)
           that's only true in the time domain.

There will be a bit more math this time around, out of necessity: some of the optimizations
can't be figured out with intuition alone. But the math consist almost exclusively of
shuffling around sums and products of scalar values and complex exponentials, with a
convolution here and there.

# Where We Left Things Last Time

I ended my [blog post about complex heterodynes](/2026/02/07/Complex-Heterodyne.html)
with a question about the efficiency of implementing it as a low pass filter that is 
followed by a decimation.

Here's a quick recap of that pipeline:

![Rotator, LPF, decimator](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

* $$f_c$$ is the normalized center frequency of the channel that we're interested in. 
  In our example, the sample rate $$F_s = 100 \text{MHz}$$ and the channel center frequency
  $$F_c = 20 \text{MHz}$$ so $$f_c = 0.2$$. Further down, I'll often use $$\omega_c = 2 \pi f_c$$
  because that makes equations less cluttered.
* $$e^{-j 2 \pi f_c n}$$ is a complex rotator that shifts down a channel with center frequency
  $$F_c$$ down to 0 Hz with a complex heterodyne.
* $$H_\text{lpf}(z)$$ is a low-pass FIR filter with 201 real taps and a linear phase[^linear_phase]. It
  removes all the frequencies outside the -5 MHz to 5 MHz range.
* Each channel has a 10 MHz bandwidth. Since there is no mirror spectrum due to the complex
  heterodyne, once the channel has been moved to 0 Hz, we can decimate by a factor 10 so that
  the range from -5 MHz to 5 MHz is all that's left.

Check out my [section with common DSP notations](/2026/02/07/Complex-Heterodyne.html#some-common-dsp-notations)
for a general overview symbols used in math formulas.

[^linear_phase]: Whether or not an FIR is linear phase depends on its coefficients, but most
                 common methods to determine those result in a linear phase filter.

# Sidestep: Ignoring Linear Phase FIR Coefficient Symmetry

Linear phase FIR filters have the desirable property that their coefficients are symmetric
around the center tap. Here's a random example:

$$
H(z) = -1 + 3 z^{-1} - 6 z^{-2} + 10 z^{-3} - 6 z^{-4} + 3 z^{-5} - z^{-6}
$$

This filter has 7 coefficients, the center coefficient is 10, the ones to the left and right of 
it are both -6 and so forth.

When you convert a DSP algorithm to hardware that needs to consume an input sample and produce
and output for every clock tick, the straightfoward implentation is to have one multiplier per
coefficient[^multiplier]. 

[^multiplier]: For the sake of argument, I'm assuming the coefficients are programmable so that
               a full-fledged multiplier is needed. If the coefficients are constant, you can
               almost always replace a multiplier by a much cheaper combination of add and shift
               operations. 

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

If you have a hardware architecture where delayed inputs are stored in a RAM instead of individual
registers and you use an FSM to execute the filter over multiple clock cycles, trying to do this
trick can make scheduling transactions more complicated too. 

And when converting the FIR into a polyphase filter, the simple symmetry breaks entirely. Here's
an example of a symmetrical 19-tap filter. In it's original form, coefficients are symmetric, but
when split up into 10 phases, the symmetry inside each phase is gone.

![19-tap filter split up into 10 phases](/assets/polyphase/polyphase_het/polyphase_het-tap_symmetry_19.svg)

It's still possible to share multiplications if you merge multiple phases, note how phase 2 has
coefficients 6 and 2 and phase 7 has coefficients 2 and 6, but that again makes data organization
and movement more difficult.

For the remainder of this blog post, I will ignore symmetric related optimizations when calculating
the number of multiplications.

# Naive Performance Baseline 

I will use multiplication as the main indicator by which to judge the efficiency of a DSP algorithm.

![Rotator, LPF, decimator](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

Let's evaluate the number of multiplications for the naive architecture:

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

harris mentions this case only tangentially, but it's useful to compare how well the straightforward
polyphase filter bank performs compared to the naive solution.

First split the FIR filter into its polyphase form, with as many sub-filters as the decimation factor:

![Complex heterodyne - Polyphase - Decimation](/assets/polyphase/polyphase_het/polyphase_het-complex_het_polyphase_decim.svg)

Apply the [noble identity for decimation](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html#the-noble-identity-for-decimation):

![Complex heterodyne - Decimation - Polyphase](/assets/polyphase/polyphase_het/polyphase_het-complex_het_decim_polyphase.svg)

Moving the FIR filter operation behind the decimator is a huge savings. The complex mixer still counts
for 200M multiplications per second, but the combined 201 taps now need to deliver samples at a 10 times
lower rate, 201 x 2 x 10M = 4.02B operations per second, for a total of 4.22B operations per second. If
it weren't for the complex rotator, the savings ratio is exactly the decimation factor.

The complex rotator can be moved after the the decimator, like this:

![Decimation - Complex heterodyne - Polyphase](/assets/polyphase/polyphase_het/polyphase_het-decim_complex_het_polyphase.svg)

This doesn't really help us, though, the number of rotations/multiplications per decimated output sample
is still the same.

# A Free-Running Rotator

One minor thing to note is that the complex rotator consists of the input signal being multiplied by
the output of a free-running oscillator. There are no major restrictions on rotation
rate $$\omega_c$$. There's also no particular about the phase of the rotator. In the previous diagram,
phase 0 gets the value of $$e^{-j \omega_c (n \bmod M)}$$, phase 1 gets $$e^{-j \omega_c ((n+1) \bmod M)}$$, 
and so forth, but that's really arbitrary. We could assign $$e^{-j \omega_c ((n+1) \bmod M)}$$ to phase 0 and
$$e^{-j \omega_c ((n+2) \bmod M)}$$ to phase 1 and outcome in terms of frequency characteristics wouldn't
be materially different (though there would be constant phase shift.)

What is true is that you will have to continuously loop through all the values of the rotator, irrespective
of the decimation factor. We'll see later that this doesn't always have to be the case.

# From Low Pass to Band Pass Filter

Let's retrace from the previous optimization, start again from the naive solution, and then try something different.

Right now, we are heterodyning the channel of interest to the baseband and then we send it through a low-pass filter, 
as seen in the plot from prevous blog post:

![Complex heterodyne followed by low pass filter spectrum](/assets/polyphase/complex_heterodyne/complex_heterodyne-low_pass_filter.svg)

Can we turn the order around, first send the channel of interest through a band-pass filter and then heterodyne
the result down to baseband? We can, and it's relatively easy to show that mathematically.

Starting with this:

$$
y[n] = \underbrace{ \underbrace{(x[n] e^{-j \omega_c n})}_{heterodyne} * h[n]}_{low-pass filter}
$$

Expand convolution operator $$*$$. $$N$$ is the number of coefficients of the filter.

$$
y[n] = \sum_{k=0}^{N-1} (x[n-k] e^{-j \omega_c (n-k)}) \; h[k] 
$$

Extract the exponential term that doesn't depend on $$k$$:

$$
y[n] = e^{-j \omega_c n} \sum_k x[n-k] \; ( e^{j \omega_c k} h[k] )
$$

Reduce back to a convolution operator:

$$
y[n] = e^{-j \omega_c n} \; \big( x[n] * (h[n] e^{j \omega_c n} ) \big) = \big( x[n] * (h[n] e^{j \omega_c n} ) \big) \; e^{-j \omega_c n}
$$

We've just proven what, [in the video](https://youtu.be/afU9f5MuXr8?t=985), harris calls the 
*Equivalency Theorem*: 

$$
( x[n] e^{-j \omega_c n} ) * h(n) = e^{-j \omega_c n} \; \big( x[n] * (h[n] e^{j \omega_c n} ) \big)
$$

There's one minor comment about this: while Google turns up plenty of equivalency
theorems, none of them deal with the swapping around a heterodyne and convolution. The only reference[^equivalency] 
that I found was in section 6.1 of his own book, 
[Multirate Signal Processing for Communication Systems](https://www.amazon.com/Multirate-Processing-Communication-Systems-Publishers-dp-877022210X/dp/877022210X/)[^book],
which has the same formulas and figures as the one of the video. It says:

> The equivalency theorem states that the operations of a down-conversion followed by a low-pass 
> filter are totally equivalent to the operations of a band-pass filter followed by a down-conversion.

[^equivalency]: There are other references, but all of those are either papers written by harris
                or papers that reference one of his papers or books.

[^book]: I've only just started reading the book, but so far I really like what I see. 

This doesn't look like an improvement, and it will take a while before we can see how this helps us.
For now, let's break the equation into pieces and take things step by step.

$$ h[n] e^{j \omega_c n} $$

The coefficients of the low-pass filter with transfer function  $$H_{lpf}(z)$$ are each multiplied by 
a value of a rotator. Notice how the $$-$$ sign in front of the $$j$$ exponent of the rotator has
disappared: when we were heterodyning the channel, we were bringing the spectrum down to baseband.
Now, we're doing the opposite and heterodyning the low-pass filter up to baseband!

Let's apply the equation above to an example. If the transfer function of the original filter is this: 

$$
H_{lpf}(z) = h_0 z^{0} + h_1 z^{-1} + h_2 z^{-2} + h_3 z^{-3} + h_4 z^{-4}
$$

Then the new filter is this:

$$
\begin{alignedat}{0}
H_{bpf}(z) & = & h_0 e^{j \omega_c 0} z^{0} &+& h_1 e^{j \omega_c 1} z^{-1} &+& h_2 e^{j \omega_c 2} z^{-2} &+& h_3 e^{j \omega_c 3} z^{-3} &+& h_4 e^{j \omega_c 4} z^{-4} \\
           & = & h_0 (e^{-j \omega_c} z)^{0} &+& h_1 (e^{-j \omega_c} z)^{-1} &+& h_2 (e^{-j \omega_c} z)^{-2} &+& h_3 (e^{-j \omega_c} z)^{-3} &+& h_4 (e^{-j \omega_c} z)^{-4} \\
\end{alignedat}
$$

This can be written much shorter, useful for drawings:

$$
H_{bpf}(z) = H_{lpf}(e^{-j \omega_c} z)
$$

It is important to note that the coefficients of $$H_{bpf}(z)$$ are constants: for a given center frequency, we can
pre-calculate the coefficient and never change them again. But contrary to the original filter $$H_{lpf}(z)$$, the
coefficients are now complex instead of real.

To simulate the behavior of this band-pass filter, we create an array with as many complex rotator values
as there are filter taps and multiply them with the low-pass filter coefficients from previous blog:

```python
tap_idx       = np.arange(LPF_FIR_TAPS)
complex_lo    = np.exp(1j * 2 * np.pi * lo_freq_hz * tap_idx / sample_clock_hz)
h_bpf_complex = h_lpf * complex_lo
```

Looking at the spectrum of this filter, there are no surprises: the filter has been transformed from a
low-pass filter to a band-pass filter with $$F_c = 20 \text{MHz}$$ as center frequency:

![Bandpass filter spectrum and filtered input signal](/assets/polyphase/polyphase_het/polyphase_het_sim-bpf_complex_filtered.svg)

The second plot of the figure above shows the input signal after applying the bandpass filter.

$$
x[n] * h_{bpf}[n]
$$

```python
signal_bpf_complex  = np.convolve(signal, h_bpf_complex, mode="same")
```

The final step shifts the filtered signal back to baseband:

$$
y[n] = ( x[n] * h_{bpf}[n] ) \; e^{-j \omega_c n}
$$


![Pipeline with bandpass filter, heterodyne and decimation](/assets/polyphase/polyphase_het/polyphase_het-bpf_het_decim.svg)

After decimation, we end up with [the same result in the previous blog post](/2026/02/07/Complex-Heterodyne.html#decimation):

![Bandpass filter, followed by heterodyne and decimation](/assets/polyphase/polyphase_het/polyphase_het_sim-signal_bfp_filtered_decim_complex.svg)

Cool! But what did we gain? 

The input to the filter is now real instead of complex, but the coefficents are now complex instead of 
real. So the complexity of the filter remains the same. And the heterodyne now multipliers 2 complex
numbers instead of multiplying a real input with a complex. We've regressed!

But that's something that will be fixed in the next section...

# Disappearing the Complex Rotator

![Pipeline with bandpass filter, decimation, and heterodyne](/assets/polyphase/polyphase_het/polyphase_het-bpf_decim_het.svg)

![Pipeline with bandpass filter and decimation](/assets/polyphase/polyphase_het/polyphase_het-bpf_decimator.svg)

# Moving the Rotator behind the Filter

$$
H(z) = \sum_{n=0}^{N-1} h[n] e^{j \theta_k n} z^{-n} = \sum_{n=0}^{N-1} h[n] (e^{j \theta_k } z)^{-n} = H(e^{-j \theta_k} z) \\
= \sum_{m=0}^{M-1} \sum_{n=0}^{N-1} h[m + nM] e^{j \theta_k (m + nM)} z^{-(m+nM)} \\
=  \sum_{m=0}^{M-1} e^{j \theta_k m} z^{-m}\sum_{n=0}^{N-1} h[m + nM] e^{j \theta_k nM} z^{-nM} \\
=  \sum_{m=0}^{M-1} e^{j \frac{2 \pi}{M} k m} z^{-m}\sum_{n=0}^{N-1} h[m + nM]  z^{-nM} \\
=  \sum_{m=0}^{M-1} e^{j \frac{2 \pi}{M} k m} z^{-m} H_m(z^M)
$$

# References

* [Stackexchange - How to implement Polyphase filter?](https://dsp.stackexchange.com/questions/43344/how-to-implement-polyphase-filter)

 > Making a polyphase filter implementation is quite easy; given the desired coefficients 
 > for a simple FIR filter, you distribute those same coefficients in "row to column" format 
 > into the separate polyphase FIR components

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: fred harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

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

