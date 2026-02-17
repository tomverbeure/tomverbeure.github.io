---
layout: post
title: The Stunning Efficiency and Beauty of the Polyphase Channelizer
date:   2026-02-16 00:00:00 -1000
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
efficiently as possible. There's already some surprises in there, but to
top it off, I'll expand the solution to do the operation for multiple
channels in parallel.

The result is amazing.

I'm still roughly following the flow of 
[fred harris' video about polyphase filter banks](https://www.youtube.com/watch?v=afU9f5MuXr8)[^harris],
but I'll be making some detours along the way because they helped me to put things
better in context and help me with understanding the topic.

[^harris]: fred harris insists on writing his name entirely in lower case. But according to
           [this reddit comment](https://www.reddit.com/r/DSP/comments/1cyrh9/comment/c9lwtot)
           that's only true in the time domain.

There's a lot more math[^math] this time around, out of necessity: some of the optimizations
can't be figured out with intuition alone. But the math consist almost exclusively of
shuffling around sums and products of scalar values and complex exponentials, with a
convolution here and there.

[^math]: I've been spending weeks on this subject now: watching videos, reading books,
         and writing the blog posts. Doing so, I've become much more comfortable with the
         math. That's good for me personally, but it's ironic that this might make the
         blog posts less accessible for others!

For those who don't want to read previous installments of this series, check out the section with
[Some Common DSP Notations](/2026/02/07/Complex-Heterodyne.html#some-common-dsp-notations)
if you need a quick refresher about the meaning of some of the symbols.

# Where We Left Things Last Time

I ended my [blog post about complex heterodynes](/2026/02/07/Complex-Heterodyne.html)
with a question about the efficiency of implementing them as a low pass filter that is 
followed by a decimation. In [the video](https://youtu.be/afU9f5MuXr8?t=552), harris
calls this the Armstrong[^armstrong] heterodyne.

[^armstrong]: Edwin Armstrong was the inventor of the superheterodyne receiver that 
              I mentioned in the previous blog post.

Here's a quick recap of that pipeline:

![Rotator, LPF, decimator](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

* $$f_c$$ is the normalized center frequency of the channel that we're interested in. 
  In our example, the sample rate $$F_s = 100 \text{MHz}$$ and the channel center frequency
  $$F_c = 20 \text{MHz}$$ so $$f_c = 0.2$$. Further down, I'll often use $$\theta_c = 2 \pi f_c$$
  because that makes equations less cluttered.
* $$e^{-j 2 \pi f_c n}$$ is a rotator. When multiplied with the input signal, it shifts down a 
  channel with center frequency $$F_c$$ down to 0 Hz. That's the complex heterodyne.
* $$H_\text{lpf}(z)$$ is a low-pass FIR filter with 201 real taps and a linear phase[^linear_phase]. It
  removes all the frequencies outside the -5 MHz to 5 MHz range.
* Each channel has a 10 MHz bandwidth. Since there is no mirror spectrum due to the complex
  heterodyne, once the channel has been moved to 0 Hz, we can decimate by a factor 10 so that
  the range from -5 MHz to 5 MHz is all that's left.

Check out my [section with common DSP notations](/2026/02/07/Complex-Heterodyne.html#some-common-dsp-notations)
for a general overview of symbols used in DSP math formulas.

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
and output for every clock tick, the straightforward implementation is to have one multiplier per
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

And when converting the FIR filter into its polyphase form, the simple symmetry breaks entirely. Here's
an example of a symmetrical 19-tap filter. In its original form, coefficients are symmetric, but
when split up into 10 phases, the symmetry inside each phase is gone.

![19-tap filter split up into 10 phases](/assets/polyphase/polyphase_het/polyphase_het-tap_symmetry_19.svg)

It's still possible to share multiplications if you merge multiple phases, note how phase 2 has
coefficients 6 and 2 and phase 7 has coefficients 2 and 6, but that again makes data organization
and movement more difficult.

For the remainder of this blog post, I will ignore symmetry related optimizations when calculating
the number of multiplications.

# Naive Performance Baseline 

I will use multiplication as the main indicator by which to judge the efficiency of a DSP algorithm.

![Rotator, LPF, decimator](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

Let's evaluate the number of multiplications for the naive architecture:

* The complex mixer multiplies a real sample with a complex number or 2 multiplications per operation
  and 200M per second.
* The low pass filter has 201 real taps, for a total of 201 x 2 x 100M = 
  40.2B operations per second.

Total: 40.4B multiplications per second!

This is our baseline, and it's a lot. Let's see what we can do about this...

# Straightforward Polyphase Filtering and Decimation

There's a reason why I also wrote 
[Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html):
it discusses exactly this kind of scenario, the combo of an FIR filter followed by a decimation. Yes,
there's a complex rotator in front of the FIR filter, but for now we can keep it there 
while we transform the FIR/decimator to its polyphase form.

harris mentions this case only tangentially, but it's useful to compare how well the straightforward
polyphase filter bank performs compared to the naive solution.

First split the FIR filter into its polyphase form with 10 sub-filters, the decimation factor:

![Complex heterodyne - Polyphase - Decimation](/assets/polyphase/polyphase_het/polyphase_het-complex_het_polyphase_decim.svg)

Apply the [noble identity for decimation](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html#the-noble-identity-for-decimation):

![Complex heterodyne - Decimation - Polyphase](/assets/polyphase/polyphase_het/polyphase_het-complex_het_decim_polyphase.svg)

Moving the FIR filter operation behind the decimator is a huge savings. The complex mixer still counts
for 200M multiplications per second, but the combined 201 taps now need to deliver samples at a 10 times
lower rate, 201 x 2 x 10M = 4.02B operations per second, for a total of 4.22B operations per second. If
it weren't for the complex rotator, the savings ratio is exactly the decimation factor.

The biggest problem with this arrangement is that the rotator is in front of the decimator and there is
no obvious way to move it behind the decimator. If the DSP pipeline is implemented in an FPGA and the
input sample clock is very high, the multiplier hardware may simply not be fast enough.

# A Free-Running Rotator

One minor thing to note is that the rotator consists of the input signal being multiplied by
the output of a free-running oscillator. Free-running implies that there are no restrictions on 
the starting phase of the oscillator. 

In the previous diagram, sample $$x[n]$$ is multiplied by $$e^{-j \theta_c n}$$, sample $$x[n+1]$$ by 
$$e^{-j \theta_c (n+1)}$$, and so forth, but that's really arbitrary. We could multiply $$x[n]$$ by $$e^{-j \theta_c (n+1)}$$ 
and $$x[n+1]$$ by $$e^{-j \theta_c (n +2)}$$ and the outcome in terms of frequency characteristics 
wouldn't be materially different (though there would be constant phase shift.)

What is true is that you have to continuously loop through all the values of the rotator, irrespective
of the length of the number of filter taps: if the rotator completes a full rotation in 128[^steps] steps, then
you'll need a table or a calculation[^unity_point_calculation] to produce 128 points around the unity circle.

[^unity_point_calculation]: There are multiple techniques to calculate the next point on a unity circle.
                            The most straightforward one is to do a rotation with a fixed 
                            [rotation matrix](https://en.wikipedia.org/wiki/Rotation_matrix), you that
                            will cost up to 4 multipliers, and you need to watch out for accumulating
                            errors over time. The [CORDIC](https://en.wikipedia.org/wiki/CORDIC)
                            algorithm is very popular, requires no multiplication, but requires much
                            more steps per result to achieve the desired precision.

[^steps]: In theory, the number of steps to complete a rotation could be a fractional number. 

We'll soon see that this isn't the case in other schemes.

# From Low Pass to Band Pass Filter

Let's undo the previous polyphase optimization, start again from the naive solution, and try 
something different.

So far, we have been heterodyning the channel of interest to the baseband and then sent it through a low-pass filter, 
as seen in the plot from previous blog post:

![Complex heterodyne followed by low pass filter spectrum](/assets/polyphase/complex_heterodyne/complex_heterodyne-low_pass_filter.svg)

Can we turn the order around, first send the channel of interest through a band-pass filter and then heterodyne
the result down to baseband? As [harris points out](https://youtu.be/afU9f5MuXr8?t=597), the Armstrong heterodyne
was created to avoid that, because a movable band-pass filter requires mechanically tuned capacitors and inductors.
In the DSP world, however, it's just numbers and calculations. 

So, yes, we can do the filtering first and then do the heterodyne, and it's relatively easy to show that mathematically.

*In what follows, I will deviate from the harris's notation in 2 ways. He uses $$a[n] * b[n]$$ for convolution. $$(a * b)[n]$$
is the more common way. He also overloads the meaning of $$n$$ in the same equation, in a way that I found utterly
confusing. Instead, I will use the $$[\cdot]$$ and $$(\cdot)$$ notation, where $$\cdot$$ is essentially a
temporary local loop variable. If you see a $$\cdot$$ in the equations below, assume that harris had a $$n$$ there.*

Starting with this:

$$
y[n] = \big( \underbrace{ \underbrace{(x[\cdot] e^{-j \theta_c (\cdot)})}_{\text{heterodyne}} * h\big)[n]}_{\text{low-pass filter}}
$$

$$*$$ is the convolution operator, in this case, a 
[discrete convolution](https://en.wikipedia.org/wiki/Convolution#Discrete_convolution).
Let's expand the equation by applying the definition of the convolution:

$$
y[n] = \sum_{k=0}^{N-1} (x[n-k] e^{-j \theta_c (n-k)}) \; h[k] 
$$

$$N$$ is the number of coefficients of the filter.

Extract the common exponential term that doesn't depend on $$k$$:

$$
y[n] = e^{-j \theta_c n} \sum_k x[n-k] \; ( e^{j \theta_c k} h[k] )
$$

Reduce back to a convolution operator:

$$
\begin{alignedat}{0}
y[n] & = & e^{-j \theta_c n} \; \big( x * (h[\cdot] e^{j \theta_c (\cdot)} ) \big)[n] \\ 
     & = & \big( x * (h[\cdot] e^{j \theta_c (\cdot)} ) \big)[n] \; e^{-j \theta_c n}
\end{alignedat}
$$

We've just proven what, [in the video](https://youtu.be/afU9f5MuXr8?t=985), harris calls the 
*Equivalency Theorem*: 

$$
\big(( x[\cdot] e^{-j \theta_c (\cdot)} ) * h\big)[n] = e^{-j \theta_c n} \; \big( x * (h[\cdot] e^{j \theta_c (\cdot)} ) \big)[n]
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

Anyway, this transformation doesn't look like an improvement, and it will take a while before we 
can see how this helps us.  For now, let's break the equation into pieces and look at them step by step.

$$ h[\cdot] e^{j \theta_c (\cdot)} $$

The coefficients of the low-pass filter with transfer function  $$H_text{lpf}(z)$$ are each multiplied by 
a value of a rotator. Notice how the $$-$$ sign in front of the $$j$$ exponent of the rotator has
disappeared: when we were heterodyning the channel, we were bringing the spectrum *down* to baseband.
Now, we're doing the opposite and heterodyning the low-pass filter *up* to channel band!

Let's apply the equation above to an example. If the transfer function of the original filter is this: 

$$
H_\text{lpf}(z) = h_0 z^{0} + h_1 z^{-1} + h_2 z^{-2} + h_3 z^{-3} + h_4 z^{-4}
$$

Then the new filter is this:

$$
\begin{alignedat}{0}
H_\text{bpf}(z) & = & h_0 e^{j \theta_c 0} z^{0} &+& h_1 e^{j \theta_c 1} z^{-1} &+& h_2 e^{j \theta_c 2} z^{-2} &+& h_3 e^{j \theta_c 3} z^{-3} &+& h_4 e^{j \theta_c 4} z^{-4} \\
                & = & h_0 (e^{-j \theta_c} z)^{0} &+& h_1 (e^{-j \theta_c} z)^{-1} &+& h_2 (e^{-j \theta_c} z)^{-2} &+& h_3 (e^{-j \theta_c} z)^{-3} &+& h_4 (e^{-j \theta_c} z)^{-4} \\
\end{alignedat}
$$

This can be written much shorter, useful for drawings, like this:

$$
H_\text{bpf}(z) = H_\text{lpf}(e^{-j \theta_c} z)
$$

It is important to note that the coefficients of $$H_\text{bpf}(z)$$ are constants: for a given center frequency, we can
pre-calculate the coefficients and never change them again. And contrary to the free-running rotator that
shifted down the spectrum of the input signal, the number of rotator values to shift up the filter is fixed to the
number of filter taps. However, compared to the original filter $$H_\text{lpf}(z)$$, the coefficients are now complex 
instead of real.

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

The second plot of the figure above shows the input signal after applying the band-pass filter.

$$
x[n] * h_\text{bpf}[n]
$$

```python
signal_bpf_complex  = np.convolve(signal, h_bpf_complex, mode="same")
```

The final step shifts the filtered signal back to baseband:

$$
y[n] = ( x[n] * h_\text{bpf}[n] ) \; e^{-j \theta_c n}
$$


![Pipeline with band-pass filter, heterodyne and decimation](/assets/polyphase/polyphase_het/polyphase_het-bpf_het_decim.svg)

After decimation, we end up with [the same result in the previous blog post](/2026/02/07/Complex-Heterodyne.html#decimation):

![Bandpass filter, followed by heterodyne and decimation](/assets/polyphase/polyphase_het/polyphase_het_sim-signal_bfp_filtered_decim_complex.svg)

Cool! But what did we gain? 

The input to the filter is now real instead of complex, but the coefficents are now complex instead of 
real. So the number of multiplications in the filter remains the same. And the heterodyne now multiplies 2 
complex numbers instead of multiplying a real input with a complex. We've regressed!

But that's something that will be fixed in the next section...

# Disappearing the Complex Rotator

In the straightforward case, we had to switch a polyphase decomposition to move the decimator from behind
the filter to in front of the filter. But that decomposition introduces single timestep delays which
prevents moving the decimator even further to the front of the rotator.

This is not the case anymore: the rotator is behind the filter and there are no delay elements. This 
allows us to move the decimator before the rotator.

Here's the rotator before decimation:

$$
e^{-j \theta_c n}
$$

When we decimate by a factor of M, the rotator completes a circle by a factor M less steps than before
the decimation. Or the angle by which the rotator moves forward each step is now M times larger.

![Original vs decimated rotator](/assets/polyphase/polyphase_het/polyphase_het-decimated_phasor.svg)

After decimation, the exponent of the rotator now has factor $$M$$ add to it:

$$
e^{-j \theta_c M m}, m = \lfloor \frac{n}{M} \rfloor
$$

where $$\lfloor x \rfloor$$ means "$$x$$ rounded down to the closest integer number". 

Since the decimator and the rotator have swapped positions, the earlier problem of having to run the
rotator at the input sample rate has been solved!

![Pipeline with band-pass filter, decimation, and heterodyne](/assets/polyphase/polyphase_het/polyphase_het-bpf_decim_het.svg)

But we can do better! The rotator can disappear entirely if its value is equal to one at all times.

$$
e^{-j \theta_c M m} \stackrel{?}{=} 1 + 0j
$$

We don't want this to be dependent on $$m$$, so we're really finding a solution for this equation:

$$
e^{-j \theta_c M } \stackrel{?}{=} 1 + 0j
$$

The rotator is one whenever it makes a full circle or whenever the exponent is an integer multiple of $$2 \pi$$. 
$$m$$ is an integer. If the equation above is satisfied without $$m$$, then it will also be satisfied after 
adding $$m$$ to the exponent.

$$
\theta_c M = k \; 2 \pi
$$

Replace $$\theta_c$$ with its definition:

$$
2 \pi \frac{F_c}{F_s} M = k \; 2 \pi
$$

Simplify and rearrange:

$$
F_c = k \frac{F_s}{M} \\
\theta_c = \frac{2 \pi k}{M}
$$

It doesn't seem like it, but this is a crucial result:

**if the center frequency of your channel is a multiple of the sample rate divided by the decimation 
factor, the decimated rotator will always evaluate to 1 and thus the multiplication disappears entirely.**

In our example with $$F_s=100 \text{MHz}$$, $$M=10$$, $$F_c=20 \text{MHz}$$, this
equation is satisfied for $$k=2$$, and we end up with this:

![Band-pass filter and decimation](/assets/polyphase/polyphase_het/polyphase_het-bpf_decim.svg)

Even with complex filter coefficients, we can still do the polyphase decomposition and 
move the decimator before the set of filters:

![Decimator, polyphase band-pass filter](/assets/polyphase/polyphase_het/polyphase_het-decim_poly_bpf.svg)

Tadaa! All elements of the pipeline can now run at the decimated output sample rate.


Last time we checked, we needed 4.22B multiplications per second. With the complex rotator gone,
we're now at 4.02B: just a filter with 201 complex taps, fed with a real value, executed 10M 
times per second. 

A pitiful 5% savings is not worth writing home about, but we can do even better.

*Note: even if we don't satisfy the $$F_c = k \frac{F_s}{M} $$ condition, we're still better off
than before, because the rotator still runs at the output instead of the input sample rate:*

![Pipeline with decimation, polyphase band-pass filters, and heterodyne](/assets/polyphase/polyphase_het/polyphase_het-decim_poly_bpf_het.svg)

*This blog post is already long as it is, so for this one, I'm focussing only on the case
where the center frequency condition is satisfied.*

# Moving Another Rotator behind the Filter and More... Again

Let's play another game of shuffling around sums and terms. So far, we've only engaged
the polyphase decomposition after the fact, to lower the number of filter calculations. 
This time we're adding the polyphase decomposition explicitly to the mathematical mix
for additional benefits.

Here's where we left it last time:

![Band-pass filter and decimation](/assets/polyphase/polyphase_het/polyphase_het-bpf_decim.svg)

Let's move our attention to the transfer function of filter:

$$
\begin{alignedat}{0}
H_\text{bpf}(z) & = & H_\text{lpf}(e^{-j \theta_c} z) \\
           & = & \sum_{n=0}^{N-1} h[n] (e^{-j \theta_c } z)^{-n}  \\
           & = & h_0 e^{j \theta_c 0} z^{ 0} &+& h_1 e^{j \theta_c 1} z^{-1} &+& h_2 e^{j \theta_c 2} z^{-2} &+& 3 e^{j \theta_c 3}  z^{-3} &+& ... 
\end{alignedat}
$$

Do the polyphase decomposition. Instead of summing all the terms the full $$h[n]$$ polynomial in one go,
we sum the terms of $$M$$ different polyphase polynomials separately, and then add them together:

$$
= \sum_{m=0}^{M-1} \sum_{n=0}^{N-1} h[m + Mn] e^{j \theta_c (m + Mn)} z^{-(m+Mn)} \\
$$

When studying this step [in the video](https://youtu.be/afU9f5MuXr8?t=1480), it took
me a minute to understand what happened with $$h[n]$$. In the first equation,
$$n = 0 ... N-1$$, where $$N$$ is the number of coefficients. In the equation above, 
the range of $$n$$ doesn't change, but now it's used like this: $$h[m + Mn]$$. The
maximum index of $$h$$ now goes beyond the number of coefficients. This isn't a problem,
though, as long as you keep in mind that $$h[n]$$ is $$\color{red}{0}$$ when $$n$$ is smaller than 0
or larger than $$N-1$$.

To make things really clear, let's expand all these sums and products for a 9-tap
filter with decimation factor $$M=3$$:

$$
\begin{alignedat}{0}
H_\text{bpf}(z) & = &  h_0 e^{j \theta_c 0} z^{ 0} &+& h_3 e^{j \theta_c 3} z^{-3} &+& h_6 e^{j \theta_c 6} z^{-6} &+& \color{red}{0} \, e^{j \theta_c 9}  z^{-9}  &+& ... && \qquad (m = 0) \\
           & + &  h_1 e^{j \theta_c 1} z^{-1} &+& h_4 e^{j \theta_c 4} z^{-4} &+& h_7 e^{j \theta_c 7} z^{-7} &+& \color{red}{0} \, e^{j \theta_c 10} z^{-10} &+& ... && \qquad (m = 1) \\
           & + &  h_2 e^{j \theta_c 2} z^{-2} &+& h_5 e^{j \theta_c 5} z^{-5} &+& h_8 e^{j \theta_c 8} z^{-8} &+& \color{red}{0} \, e^{j \theta_c 11} z^{-11} &+& ... && \qquad (m = 2) \\
\end{alignedat}
$$

In each of the polyphase sub-filters, the factor $$e^{j \theta_c m} z^{-m}$$ is not dependent on $$n$$
and can be moved ahead of the inner sum:

$$
=  \sum_{m=0}^{M-1} e^{j \theta_c m} z^{-m} \sum_{n=0}^{N-1} h[m + Mn] e^{j \theta_c Mn} z^{-Mn} \\
$$

$$
\begin{alignedat}{0}
H_\text{bpf}(z) & = & e^{j \theta_c 0} z^{ 0} & \big(  h_0 e^{j \theta_c 0} z^{0} &+& h_3 e^{j \theta_c 3} z^{-3} &+& h_6 e^{j \theta_c 6} z^{-6} \big)  && \qquad (m = 0) \\
           & + & e^{j \theta_c 1} z^{-1} & \big(  h_1 e^{j \theta_c 0} z^{0} &+& h_4 e^{j \theta_c 3} z^{-4} &+& h_7 e^{j \theta_c 6} z^{-7} \big)  && \qquad (m = 1) \\
           & + & e^{j \theta_c 2} z^{-2} & \big(  h_2 e^{j \theta_c 0} z^{0} &+& h_5 e^{j \theta_c 3} z^{-5} &+& h_8 e^{j \theta_c 6} z^{-8} \big)  && \qquad (m = 2) \\
\end{alignedat}
$$

Now look back at the previous section where we figured out the condition to eliminate the rotator. In the equation
above, we see $$ e^{j \theta_c Mn } $$, which contains $$ e^{j \theta_c M } $$. This is exactly the same rotator
that we eliminated before.

In other words, when using the same restriction $$ F_c = k \frac{F_s}{M} $$, the rotator in the products of the
inner sum simply disappears and we end up with this:

$$
=  \sum_{m=0}^{M-1} e^{j \theta_c m} z^{-m} \sum_{n=0}^{N-1} h[m + Mn] z^{-Mn} \\
$$

$$
\begin{alignedat}{0}
H_\text{bpf}(z) & = & e^{j \theta_c 0} z^{ 0} & \big(  h_0 z^{0} &+& h_3 z^{-3} &+& h_6 z^{-6} \big)  && \qquad (m = 0) \\
           & + & e^{j \theta_c 1} z^{-1} & \big(  h_1 z^{0} &+& h_4 z^{-4} &+& h_7 z^{-7} \big)  && \qquad (m = 1) \\
           & + & e^{j \theta_c 2} z^{-2} & \big(  h_2 z^{0} &+& h_5 z^{-5} &+& h_8 z^{-8} \big)  && \qquad (m = 2) \\
\end{alignedat}
$$

Or abbreviated:

$$
H_\text{bpf}(z) = \sum_{m=0}^{M-1} e^{j \theta_c m} z^{-m} H_m(z^M)
$$

Furthermore:

$$
\theta_c = k \frac{2 \pi}{M}
$$

So we end up with this:

$$
H_\text{bpf}(z) = \sum_{m=0}^{M-1} e^{j \frac{2 \pi}{M} k m} z^{-m} H_m(z^M)
$$

$$e^{j \frac{2 \pi}{M} k m}$$ is a scalar value, so we can move the multiplication 
to the back of the filter:

$$
H_\text{bpf}(z) = \sum_{m=0}^{M-1} z^{-m} H_m(z^M) e^{j \frac{2 \pi}{M} k m} 
$$

$$
\begin{alignedat}{0}
H_\text{bpf}(z) & = & z^{ 0} & \big(  h_0 z^{0} &+& h_3 z^{-3} &+& h_6 z^{-6} \big) e^{j \frac{2 \pi}{M} k 0} \\
           & + & z^{-1} & \big(  h_1 z^{0} &+& h_4 z^{-4} &+& h_7 z^{-7} \big) e^{j \frac{2 \pi}{M} k 1} \\
           & + & z^{-2} & \big(  h_2 z^{0} &+& h_5 z^{-5} &+& h_8 z^{-8} \big) e^{j \frac{2 \pi}{M} k 2} \\
\end{alignedat}
$$

Here's how that looks as a diagram:

![Polyphase with real band-pass filter, heterodyne, decimator](/assets/polyphase/polyphase_het/polyphase_het-poly_real_bpf_het_decim.svg)

As a final step, we can move the decimator back to the front by applying the noble identity on the 
polyphase sub-filters. Note that this time, the rotator exponent is not multiplied by $$M$$, because
the exponent is a fixed value, not a changing phasor.

![Polyphase with decimator, real band-pass filter, heterodyne](/assets/polyphase/polyphase_het/polyphase_het-decim_poly_real_bpf_het.svg)

This is a truly remarkable outcome: 

* All math operations happen at a slow rate behind the decimators.
* The inputs to the filters are real.
* The coefficients of the polyphase filters are real again.
* The coefficients don't depend on the targeted channel frequency
* The rotators are located behind the filters

The importance of the last 2 points can't be overstated: if you want to change the channel $$k$$ that needs to
be brought to base band from one to another, all you need to change are the rotators.

Compared the last checkpoint, the resource requirements have also been reduced roughly by half:

* the 201 filter taps are multiplied by a real input at a rate of 10M per second = 2.01B multiplications.
* 3 rotators multiply the real output of the filters by a complex number at 10M per second = 60M multiplications.

Total: 2.016B multiplications.

Our naive initial baseline was 40.4B multiplications per second, we've reduced that number by a factor of 20.

And still we are not done...

# The Polyphase Channelizer

So far, we've focused on finding an optimal solution to extracting the signal of one channel of many to baseband.
We're now expanding our scope: what if we want to extract the signal of all channels in parallel?

This is where the conclusion of pervious section pays off ever more: since only the final rotators are channel
dependent, all we need is an additional set of rotators for each channel. The filters remain untouched. That's
a huge win: from the resource calculation, we can already conclude that the filters tend to be require the
large majority of multipliers. And that's for a filter with 201 taps, which is relatively modest. In today's
world, channels are often stacked one next to the other with a very narrow transistion band and narrow
transistion bands require very steep filters to separate one from the other.

![Polyphase channelizer with 2 channels](/assets/polyphase/polyphase_het/polyphase_het-polyphase_multi_chan.svg)

In the DSP pipeline above, 2 channels are brought to baseband resulting in 2 time domain signals $$s_k[n]$$
and $$s_l[n]$$, but the number of channels that can be extracted efficiently is really only limited by the
decimation factor (due to the $$F_c = k F_s / M$$ requirement.)

If we have a decimation factor of $$M$$ and we want to extract $$M$$ channels in parallel, then we're looking at
$$M (M-1)$$[^nr_rotators] rotators or $$ 2 M (M-1)$$ multipliers. In his video, harris talks about 
[a polyphase channelizer with 65536 channels](https://youtu.be/afU9f5MuXr8?t=2075). There are many cases where
$$O(n^2)$$ is good enough and suddenly it's not. 4,294,901,760 complex multiplications to calculate 65536 output samples
is not good enough.

[^nr_rotators]: $$M(M-1)$$ instead of $$M^2$$ because the rotator at the output of $$H_0(z)$$ has an exponent of
                0 and thus reduces to 1.

Let's look at the rotator section for a single channel:

$$
s_k[n] = \sum_{m=0}^{M-1} y_m[n] e^{j \frac{2 \pi}{M} k \, m}
$$

This calculation must be done for each output time step $$n$$, so let's drop that index. And while we're at it,
let's group the outputs $$y_m$$ of the filters into their own array, so that we can reference them, for each
time step $$n$$, as $$y[m]$$ instead of $$y_m$$:

$$
s_k = \sum_{m=0}^{M-1} y[m] e^{j \frac{2 \pi}{M} k \, m}
$$

Does this equation ring a bell? Compare against this: 

$$
x[n] = \frac{1}{N} \sum_{k=0}^{N-1}{X[k] e^{j \frac{2 \pi}{N} k \, n } }
$$

This is the definition of inverse[^inverse] 
[discrete Fourier transform (DFT)](https://en.wikipedia.org/wiki/Discrete_Fourier_transform)!
Except for the front scaling factor, our equation has the same form.

[^inverse]: It's inverse because there's no $$-$$ sign in front of $$j$$.

If, for each time step $$n$$, we want the output samples of all channels $$0..M-1$$, the DFT will give us
exactly that. That in itself doesn't solve our problem: it is well known that a naive DFT
implementation has $$O(n^2)$$ behavior. But in DSP land, it's impossible to mention the discrete
Fourier transform without immediately bringing up the 
[Fast Fourier transform (FFT)](https://en.wikipedia.org/wiki/Fast_Fourier_transform),
which has $$O(n \log n)$$ behavior.

For a 65536 channel polyphase channelizer, the FFT brings down the number of complex multiplications
from 4,294,901,760 down to 1,048,576. We're received a second boost-of-efficiency miracle.

![Polyphase filters, IFFT](/assets/polyphase/polyphase_het/polyphase_het-polyphase_ifft.svg)

The Fourier transform is known primarily for converting signals from the time domain to the
frequency domain and back, but you don't have to use it for frequency stuff, as is the case here.
The output of the IFFT in the polyphase channelizer is an array with the samples of all
channels of a given time tick. The IFFT is simply used algorithmic accelerator.

This is a good at time as any to link to my favorite Youtube video of all time:
"The Fast Fourier Transform (FFT): Most Ingenious Algorithm Ever?"

<iframe width="640" height="360" src="https://www.youtube.com/embed/h7apO7q16V0?si=8zM2mOaMBD0byhyb" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

It develops the FFT algorithm, and like the polyphase channelizer, it doesn't use the FFT
for time domain/frequency conversion, but to accelerate the multiplication of polynomials.

# From Theory to Practice

Let's put everything together in a simulated example. I've created a new signal
that has 2 active channels, with center frequency at 20 MHz and 30 MHz. The 20 MHz channel
has the same peaks as before, the 30 MHz one has 2 different peaks. As before, the
inactive channels have a large noise component.

![Spectrum of signal with 2 active channels](/assets/polyphase/polyphase_het/polyphase_het_sim-signal_multi_spectrum.svg)

NumPy has all kinds of nice operators to manipulate multi-dimensional arrays, but my
knowledge about them is thin. So the code below won't be the most canonical way
of doing things!

Split up the taps of low-pass filter `h_lpf` into `h_poly`, its polyphase decomposition:

```python
h_poly              = np.zeros((DECIM_FACTOR, int(np.ceil(LPF_FIR_TAPS / DECIM_FACTOR))))
for phase in range(DECIM_FACTOR):
    phase_taps      = h_lpf[phase::DECIM_FACTOR]
    h_poly[phase, :len(phase_taps)] = phase_taps
```

Decimate the input signal into 10 different signals, each with a different phase:

```python
signal_multi_decim  = np.zeros((DECIM_FACTOR, int(np.ceil(NR_SAMPLES/DECIM_FACTOR))))
for phase in range(DECIM_FACTOR):
    phase_decim     = signal_multi[DECIM_FACTOR-1-phase::DECIM_FACTOR]
    signal_multi_decim[phase, :len(phase_decim)] = phase_decim
```

Note the `DECIM_FACTOR-1-phase` part. It's tempting to write `phase` there, but that
won't work. Ask me how I know...

For each phase, apply the decimated input signal to the corresponding polyphase
sub-filter:

```python
h_poly_out          = np.zeros((DECIM_FACTOR, len(signal_multi_decim[0])))
for phase in range(DECIM_FACTOR):
    phase_h_out     = np.convolve(signal_multi_decim[phase], h_poly[phase], mode="same")
    h_poly_out[phase, :len(phase_h_out)] = phase_h_out
```

For each timestep, take the 10 samples from output values of the filters, perform an IFFT,
and store it as the output of 10 channels:

```
signal_poly_out    = np.zeros((DECIM_FACTOR, int(np.ceil(NR_SAMPLES/DECIM_FACTOR))), dtype=complex)
for m in range(len(h_poly_out[0])):
    ifft_input  = h_poly_out[:, m]
    ifft_out    = np.fft.ifft(ifft_input)
    signal_poly_out[:, m] = ifft_out
```

Here's a plot witih the spectra for channels 1 (noise), 2 and 3:

![Plot with the spectrum for channels 1, 2 and 3](/assets/polyphase/polyphase_het/polyphase_het_sim-signal_poly_out_ch2_ch3.svg)

Success!

# Conclusion

This was a long story, but I felt that it had to be told in one go to keep all the context
together.

Let's do step-by-step recap:

* We started with a very naive implementation of a single channel downconverter.
* Using a straightforward polyphase decomposition, we came up with a much more efficient design but
  with one major flaw: it required a mixer that runs at the input sample rate.
* With some algebraic magic, we were able to move that mixer to the back of the pipeline,
  after the decimator. No more units running at input sample rate!
* A smart choice of the sample rate allowed us to get rid of the mixer altogether.
* Even more algebraic magic, allowed to cut the number of multiplications by half and
  isolated all channel specific calculations to the very end of the pipeline.
* With only 1 non-channel specific polyphase filter and different rotators at the back, 
  we could expand the pipeline to support multiple channels at low extra cost.
* That cost became even lower by recognizing the presence of an inverse discrete Fourier
  transform and using an IFFT to accelerate the calculations.

I just love how everything, like a plan, comes beautifully together.

I deliberately left out the parts of the video where harris discusses cases where channel centers
have a fixed offset from where they should be. It would make this blog post even longer, but these
cases are also not fully worked-out in the video. I'll need more time to digest those parts.

The topics that have been covered in these last 3 blog posts only take around 40 min of a video
that's 90 min long. The remainder contains a bunch of interesting examples and applications for
polyphase filter banks and polyphase channelizers. I want to dive into those as well.

One thing that I didn't cover is the intuitive explanation about how polyphase channelizers
work. harris talks about rotating spectra, aliased to the same baseband, that cancel each other
out for different rotators. While I kind of get what he's trying to say, the truth is that I
currently don't have the kind of intuition that harris has, so I'll 
defer [to the video](https://youtu.be/afU9f5MuXr8?t=2151) for that.

# References

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: fred harris](https://www.youtube.com/watch?v=afU9f5MuXr8)

* [Stackexchange - Understanding Polyphase Filter Banks](https://dsp.stackexchange.com/questions/96042/understanding-polyphase-filter-banks)

* [IEEE - Digital Receivers and Transmitters Using Polyphase Filter Banks for Wireless Communications](https://ieeexplore.ieee.org/document/1193158)

Other blog posts in this series:

* [Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html)
* [Complex Heterodynes Explained](/2026/02/07/Complex-Heterodyne.html)

# Footnotes

