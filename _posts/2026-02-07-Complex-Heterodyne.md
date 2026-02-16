---
layout: post
title: Complex Heterodynes Explained
date:   2026-02-07 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>

* TOC
{:toc}

# Introduction

In my previous blog post about [polyphase decimation](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html), 
my reason for looking at that topic was "reading up on polyphase filters and multi-rate digital signal 
processing", but to be more specific, it all started by watching 
["Recent Interesting and Useful Enchancements of Polyphase Filter Banks"](https://www.youtube.com/watch?v=afU9f5MuXr8),
a fantastic tutorial by [Fred Harris](https://en.wikipedia.org/wiki/Fredric_J._Harris).
The video is more than 90 min long and is a lot to process when your DSP knowledge is lacking.

I've watched the video a few times now, and while I kind of get what he's doing, it made me realize even 
more how skin-deep my DSP knowledge really is.

For example, the video talks about *complex heterodynes* all over the place, but I couldn't really 
explain how the outcome of that operation is different from mixing an input signal with a regular, real sinusoid. 

To fix this, I'm going through video sections step-by-step and blog post by blog post. The general
approach is to demonstrate concepts (to myself) by implementing them in 
[NumPy](httpsP//numpy.org) 
and plotting the results while limiting the number of mathematical formulas. In the process of peeling 
that onion, new knowledge gaps will be exposed that might not be directly relevant to the video, but if 
interesting enough, I'll check those out just the same.

But that's for the future. Let's talk about the why and how of the complex heterodyne.

The scripts that were used to create the figures in this blog post series can be found in
my [`polyphase_blog_series`](https://github.com/tomverbeure/polyphase_blog_series) on GitHub.

# Some Common DSP Notations

There are some conventions that are useful to know about. They aren't a hard
and fast rules, but I'll try to stick to them as well as I can. 

* $$N$$: the number of samples in the time domain buffer over which a certain
  block operation is performed.
* $$n$$: the current time in a discrete time system. For example, $$s[n]$$ could be
  an array or sequence of input samples that come out of an ADC.
* $$k$$: an index in a size limited set of numbers. $$k$$ could be used to indicate 
  one of many channels, it could be one bin out of all the bins of 
  a discrete time Fourier transform, etc.
* $$H(z)$$: a discrete transfer function, usually of a filter. The fact that it's
  an uppercase $$H$$ indicates that the function is in the z-domain, the discrete
  version of $$H(s)$$ which is in the Laplace domain, but don't worry about those
  terms, it's the last time they'll be mentioned.
* $$h[n]$$: the impulse response of the $$H(z)$$ transfer function. This is the
  time domain sequence that you get if you apply a 1 and then nothing but zeros
  to $$H(z)$$. Since I'll only be discussing finite impulse response filters (FIR),
  $$h[n]$$ will be the same as the coefficients of the polynomial that describes
  $$H(z)$$.
* $$h[k]$$: one of the polynomial coefficients of $$H(z)$$. For all coeffients of
  $$H(z)$$, $$h[k]$$ will be identical to $$h[n]$$. For all other values, $$h[n]$$
  will be zero, while $$h[k]$$ won't really exist. This is a pretty subtle difference
  and often $$h[k]$$ and $$h[n]$$ will be used interchangeably (I've definitely done so!), 
  but the notation can help to make clear the intent of a formula.
* $$F_x$$: a real world analog frequency, measured in Hz. $$F_s$$ is often used for
  the sample rate. $$F_c$$ could be the center frequency of a channel.
* $$f_x$$: a normalized frequency, usually relative to the sample frequency. 
  $$f_c$$ would be the ratio of $$F_c / F_s$$.
* $$\omega$$ and $$\theta$$: both are used to indicate the rate
  of change of a periodic signal. But $$\omega$$ tends to be used more when the intent
  is an angular frequency, e.g. in the context of shifting the spectrum of a signal,
  while $$\theta$$ puts more emphasis on the change of an angle on the unit circle.
  From a pure mathematical point of view, they're the same: $$\sin(\omega n)$$ is
  no different than $$\sin(\theta n)$$.
  One reason to use $$\omega$$ instead of $$2 \pi n/N$$ is because it reduces the visual 
  clutter when used as an argument of trigonometry functions. Compare $$\sin(2 \pi n /N)$$ 
  with $$\sin(\omega n)$$.


I'll try to stick to these conventions as much as possible. Feel free to reach out
if you think I'm doing it wrong somewhere.

# Sampling with 1 ADC Creates a Real Signal

Let's create an input signal that's interesting enough to demonstrate DSP theory in practice and
that will trip us up if we're doing something wrong. It's a signal that you could get out of
a real-world analog front-end with a single AD converter (ADC) that has a sampling clock
of 100 MHz.

```python
signal_pure = ( signal1_amplitude * np.sin(2 * np.pi * signal1_freq_hz * t)
              + signal2_amplitude * np.cos(2 * np.pi * signal2_freq_hz * t) )

noise_floor = np.random.normal(0.0, noise_rms, NR_SAMPLES)

oob_noise           = np.random.normal(0.0, oob_noise_rms, NR_SAMPLES)

oob_noise_cutoffs   = [ OOB_NOISE_SBF_LOW_MHZ / (SAMPLE_CLOCK_MHZ / 2.0),
                        OOB_NOISE_SBF_HIGH_MHZ / (SAMPLE_CLOCK_MHZ / 2.0) ]

oob_noise_h         = firwin( OOB_NOISE_FIR_TAPS,
                              oob_noise_cutoffs,
                              window=("kaiser", OOB_NOISE_KAISER_BETA),
                              pass_zero="bandstop" )

oob_noise_filtered  = np.convolve(oob_noise, oob_noise_h, mode="same")

signal      = signal_pure + noise_floor + oob_noise_filtered
```

The signal has the following components:

* 2 sinusoids, one at 22 MHz and one at 17 MHz. The second one has an amplitude that
  is 10 dB lower. 

  This is the signal that we're interested in.

* A tiny bit of noise across the whole spectrum

  This adds a noise floor to the overall spectrum which makes it more like 
  the real world and also makes the frequency plots more pleasing go the eye.

* Out-of-band noise that is everywhere expect in the frequency band where our
  signal lives.

  This is useful to verify that we're processing the signal the right way. If we
  don't then this noise will overlap the spectrum of the signal of interest and
  we'd notice that right away in the spectrum plot.

![Input signal time and spectrum plot](/assets/polyphase/complex_heterodyne/complex_heterodyne-input_signal.svg)

In a time domain plot, we see a typical case of sinusoids interacting with each other,
resulting in some kind of beat envelope frequency. The noise is too low to be noticable
in a non-logarithmic plot.

The frequency domain amplitude plot is more interesting. There are the 2 peaks
of different amplitude, a noise floor in the frequency band where our signal lives,
and the more prominent out-of-band noise everywhere else. 

We can also see that the negative frequency side of the spectrum is a mirror of 
the positive side. This is as it should be: to display the spectrum, we performed a 
[Discrete Fourier Transformation (DFT)](https://en.wikipedia.org/wiki/Discrete_Fourier_transform),
which I'll sometimes, incorrectly, call the Fourier transform for brevity.

The definition of the DFT is as follows:

$$
X[k] = \sum_{n=0}^{N-1}{x[n] e^{-j {2 \pi k n}/{N} } }
$$

That looks intimidating, but if we use
[Euler's formula](https://en.wikipedia.org/wiki/Euler%27s_formula), 
we can rewrite this as:

$$
X[k] = \sum_{n=0}^{N-1}{x[n] \cos( \frac{2 \pi k n}{N} ) } - j \sum_{n=0}^{N-1}{x[n] \sin( \frac{2 \pi k n}{N} ) } 
$$

For a given frequency bucket $$k$$, we are multiplying the input signal by cosine and by a sine.
This is essentially a correlation function that calculates the extent by which sine and cosine are part
of the input signal. Since the cosine and sine have a 90 degree phase difference between them,
we're using complex notation for the final number: 

$$
X[k] = R + j I
$$

The magnitude of the frequency of each frequench components is: 

$$
\left| X[k] \right| = \sqrt{R^2 + I^2}
$$

The phase is the angle between R and I is:

$$
\angle{X[k]} = \arctan(\frac{I}{R})
$$

If the Fourier transform is applied to signal that doesn't have complex samples, 
as is the case when there is only 1 ADC, then the Fourier transform has
[Hermitian symmetry](https://www.dsprelated.com/freebooks/sasp/Symmetry_DTFT_Real_Signals.html):
for every complex value on the positive frequency side, the corresponding negative frequency value
will have the same real value $$R_k$$ and an inverted imaginary value $$I_k$$. Because of this,
the amplitude is the same but the phase is inverted.

In the frequency plot above, only the amplitude is shown, hence the mirror image with
identical amplitudes left and right.

In DSP land, a signal that doesn't have imaginary component values is called a real
signal. A signal that is complex and that doesn't have a negative frequency 
components is an [analytic signal](https://en.wikipedia.org/wiki/Analytic_signal).

A common way of saying that the sine and cosine have a 90 degree phase difference, is that
they are in quadrature. It's an extremely powerful concept that makes many DSP operations
a whole lot easier, as we'll see below. 

# Heterodyning the Signal to Baseband the Wrong Way

Imagine that we have multiple frequency bands or channels, that each channel has 
a bandwidth of 10 MHz and a center frequencies at 0, 10, 20, 30 and 40 MHz. The signal that we
created above would then be part of the 20 MHz channel that ranges from 15 to 25 MHz.

![Different channels](/assets/polyphase/complex_heterodyne/complex_heterodyne-channels.svg)

To process the channel, we'd like to move it from 15 MHz to 25 MHz to the baseband 
range of -5 MHz to 5 MHz. For our case, this means that we want the 17 MHz and 22 MHz 
components to end up at -3 MHz and +2 MHz resp.

Moving a channel to baseband before doing further processing allows us to use the same DSP 
operations no matter which channel we've selected. It also allows us to reduce the sample rate 
from 100 MHz to something much lower, thus reducing DSP resource requirements.

You can shift the spectrum of a signal by multiplying it with a sine wave. The
multiplication of 2 signals is also called [mixing](https://en.wikipedia.org/wiki/Frequency_mixer). 
And mixing with the purpose of moving the spectrum of a signal is called 
[heterodyning](https://en.wikipedia.org/wiki/Heterodyne). In the analog world,
the signal is multiplied with the sinusoidal output of a local oscillator (LO). We still
need this in the virtual work of DSP math in the form a simulated
[numerically controlled oscillator](https://en.wikipedia.org/wiki/Numerically_controlled_oscillator)
so I will keep on using the name of local oscillator.

The math of heterodyning a sine wave is straightforward. Here I show how it works in the
continuous time domain, but it works the same after sampling. Let's start with signal
$$s(t)$$ and local oscillator $$l(t)$$:

$$
s(t)= A \cos(2 \pi f_0 t) \\
l(t)= \cos(2 \pi f_c t) \\
$$

Multiply the 2 signals to get heterodyne signal $$y(t)$$:

$$
y(t) = s(t) l(t) = A \cos(2 \pi f_0 t) \cos(2 \pi f_c t) \\
$$

Use the textbook trigonometry identity:

$$
\cos \alpha \cos \beta = \frac{1}{2} \big[ \cos(\alpha + \beta) + \cos(\alpha - \beta)  \big]
$$

We get:

$$
y(t) = \frac{1}{2} A \big[ \cos(2 \pi (f_0 + f_c) t) + \cos( 2 \pi (f_0 - f_c) t) \big]
$$

This tells us is that multiplying a signal with frequency component $$f_0$$
with sine wave with frequency $$f_c$$ creates a new signal with 2 frequency components
$$f_0 + f_c$$ and $$f_0 - f_c$$.

If we want to shift the center frequency of our channel from 20 MHz to 0 MHz, we need to
multiply with a 20 MHz sine wave. Let's simulate that:

```python
lo_signal       = np.sin(2 * np.pi * lo_freq_hz * t)
signal_real_het = signal * lo_signal
```

This is the resulting spectrum:

![Spectrum after real heterodyn](/assets/polyphase/complex_heterodyne/complex_heterodyne-real_het.svg)

That... didn't go as we hoped. 

The spectrum got shifted down by 20 MHz to 0 MHz and to -40 MHz,
giving us peaks at -3 MHz and +2MHz and -37 MHz and -42 MHz. That's what we wanted!
But since `lo_signal` is a real signal, it has a mirror image at -20 MHz. This made
the spectrum of the signal shift up to +3 MHz and -2 MHz and 37 MHz and 42 MHz. 

Instead of the desired 2 peaks in the baseband, there are now 4 peaks, at -3, -2, 2 and 3 MHz. 
We've destroyed the original signal.

Heterodyning with a real local oscillator is a common operation in the analog world, but
when this is done, the heterodyne doesn't happen to baseband but a non-zero intermediate
frequency. That is the idea of the 
[superheterodyne receiver](https://en.wikipedia.org/wiki/Superheterodyne_receiver)[^super], a huge
breakthrough in 1918 in the development of radio technology: it mixes the desired signal
to a fixed intermediate frequency (IF),  not the baseband, and does further demodulation such
AM or FM on that IF signal.

![Superheterodyne example block diagram](https://upload.wikimedia.org/wikipedia/commons/3/3f/Superheterodyne_receiver_block_diagram_2.svg)
*(Source: Wikipedia)*

[^super]: If you're wondering why it's called 'super': it's because the result of the
          heterodyne is a signal that is still in the supersonic frequency range, as in,
          above the audible frequency range. Before superheterodyne receivers, the radio signal
          of interested was heterodyned straight to the audio range.

# Complex Heterodyne to the Rescue

We could definitely do a superheterodyne in the digital world, but many modern modulation
schemes such as 
[QAM](https://en.wikipedia.org/wiki/Quadrature_amplitude_modulation) or 
[OFDM](https://en.wikipedia.org/wiki/Orthogonal_frequency-division_multiplexing)
rely on the ability to process the signal in the baseband.

Luckily, there is a solution. The root of our troubles is the presence of a 
mirror frequency image for the local oscillator. If we can get rid of one of those orange LO peaks, 
only one spectrum image of the signal will get heterodyned into the baseband.

This is surprisingly simple: instead of a real sinusoid, we use a complex one as local oscillator:

$$
l(t) = e^{-j 2 \pi f_c t}
$$

This signal only has a peak in the spectrum at $$-F_c$$. We're using a negative LO frequency
because we want to shift the spectrum down so that positive image of the channel spectrum ends
up at baseband. If we use $$F_c$$, the whole spectrum shifts up instead and the negative
channel lands on baseband.

Let's create the complex local oscillator signal and multiply it by
the input signal:

```python
complex_lo_signal   = np.exp(-1j * 2 * np.pi * lo_freq_hz * t)
signal_complex_het  = signal * complex_lo_signal
```

And voila:

![Complex LO and heterodyne](/assets/polyphase/complex_heterodyne/complex_heterodyne-complex_lo.svg)

We had to introduce complex numbers, but the result is worth it: the baseband has exactly 
what we want.

# Filtering Away the Old Negative Image

The only thing that's still bothering us are the 2 peaks around -40 MHz, the negative image
of the channel that used to be at -20 MHz. This needs to go if we want to lower the sample 
rate by decimation.

We can easily do this with a low pass FIR filter. There are multiple ways to design those,
I even wrote [a blog post](/2020/10/11/Designing-Generic-FIR-Filters-with-pyFDA-and-Numpy.html) 
about it.

Here, I chose the [windowing method](https://www.dsprelated.com/freebooks/sasp/Window_Method_FIR_Filter.html)
to create a steep 201 taps FIR filter with a passband of 5 MHz.

```python
fir_cutoff  = FIR_PASSBAND_MHZ / (SAMPLE_CLOCK_MHZ / 2.0)
h_lpf       = firwin(FIR_TAPS, fir_cutoff, window=("kaiser", FIR_KAISER_BETA), pass_zero=True)
```

The filter is applied by doing a convolution between the heterodyned signal and the filter taps in `h_lpf`:

```python
signal_het_lpf      = np.convolve(signal_complex_het, h_lpf, mode="same")
```

Note that the samples of `signal_complex_het` are complex, but the filter coefficients are real.

Here's the result:

![Complex heterodyned signal with low pass filter](/assets/polyphase/complex_heterodyne/complex_heterodyne-low_pass_filter.svg)

# Decimation 

The spectrum has now been reduced to -5 MHz and 5 MHz. Since there is no mirror image, we can safely
do a decimation without having to worry about aliasing as long as we obey 
[Nyquist](https://en.wikipedia.org/wiki/Nyquist–Shannon_sampling_theorem) 
by keeping the width of the spectrum is equal or larger than the 2-sided width of channel, which is
10 MHz. With a sample rate of 100 MHz, we can decimate by a factor of 10.

```python
signal_decim    = signal_het_lpf[::DECIM_FACTOR]
```

We now have 10 times less data to deal with, but the spectrum looks just the same
as before:

![Spectrum after decimation](/assets/polyphase/complex_heterodyne/complex_heterodyne-decim_fft.svg)

Success!

# Final Block Diagram

Wrapping up, we arrived at the following block diagram of operations and transformations:

![Block diagram with all operations](/assets/polyphase/complex_heterodyne/complex_heterodyne-block_diagram.svg)

* The analog signal is converted to a real digital with a single channel, 100 Msps ADC.
* A mixer and a complex local oscillator heterodynes the signal to baseband. The
  signal is now complex.
* A low pass filter removes all frequencies that don't reside in the baseband.
* A decimator brings down the sample rate from 100 MHz to 10 MHz
* The output is a complex 10 MHz sample stream.

![Mathematical block diagram](/assets/polyphase/complex_heterodyne/complex_heterodyne-rot_lpf_decim.svg)

Expressed mathematically:

$$
y[m] = \big[(x[n] e^{-j 2 \pi f_c n}) * h_{\text{lpf}}[n]\big] \downarrow M \\
f_c = \frac{F_c}{F_s}, m = n M
$$

The thing works, but is the optimal of doing things? My 
[previous blog post about polyphase decimation filtering](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html)
should be a hint that the answer is: definitely not.

Dealing with a complex instead of real signal doubles the number of math operations
and performing the decimation at the end of the pipeline means that we're doing a lot 
of math that gets thrown away. 

But I have a much better understanding of complex heterodyning now, so that's a definite
win!

In a next installment, I'll explore how this can be optimized.

# Conclusion

In the Fred Harris video that started this all, complex heterodynes are everywhere and
treated as a known quantity. And they're straightforward once you get to know them better.

I used to think that dealing with signals in quadrature, representing them with complex numbers, 
was dOne primarily as a way to reduce the sample rate by half. There are certain potential
cost savings to that.

But the benefits are more fundamental: they eliminate the issue of having to deal with mirror images
in the spectrum. 

# Afterthought: the Fourier Transform is a Bunch of Averaged Complex Heterodynes

While writing this blog post, I suddenly struck me: the discrete time Fourier
transform is the same as doing a complex heterodyne to 0 Hz and then calculating 
the DC value by summing the samples, for all frequencies of interest.

Complex heterodyne:

$$
y[n] = x[n] e^{-j 2 \pi f_k n}
$$

DFT:

$$
X[k] = \sum_{n=0}^{N-1}{x[n] e^{-j {2 \pi k n}/{N} } } \\
f_k = k / N \\
X[k] = \sum_{n=0}^{N-1}{x[n] e^{-j {2 \pi f_k n } } } \\
$$

This is kind of obvious when you think about it, but I had never dealt with
complex heterodynes so it's something new for me.

# References

* [Youtube - Recent Interesting and Useful Enhancements of Polyphase Filter Banks: Fred Harris](https://www.youtube.com/watch?v=afU9f5MuXr8)
* [polyphase blog series scripts](https://github.com/tomverbeure/polyphase_blog_series)

Other blog posts in this series:

* [Notes about Basic Polyphase Decimation Filters](/2026/01/25/Notes-on-Basic-Polyphase-Decimation.html)

# Footnotes

