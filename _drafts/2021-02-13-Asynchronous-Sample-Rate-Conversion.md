---
layout: post
title: Asynchronous Sample Rate Conversion
date:  2021-02-13 00:00:00 -1000
categories:
---

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    jax: ["input/TeX", "output/HTML-CSS"],
    tex2jax: {
      inlineMath: [ ['$', '$'], ["\\(", "\\)"] ],
      displayMath: [ ['$$', '$$'], ["\\[", "\\]"] ],
      processEscapes: true,
      skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
    //,
    //displayAlign: "left",
    //displayIndent: "2em"
  });
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_HTML" type="text/javascript"></script>


* TOC
{:toc}

# Introduction

Imagine the following situation: you have a number of different audio sources that
provide audio in digital from but at different sample rates. Say, one source is
a CD player which delivers 16-bit PCM samples at 44.1kHz, the other source is
a BlueRay player with 24-bit PCM samples at 48kHz.

Now you want to mix these audio streams into something new.

How would you go about that?

You'd first need to find common ground: convert the incoming streams so that
they both have exactly the same sample rate, all the time. In other words, you'd
have to make sure that the 2 audio streams are synchronous to each other.

This requires the following: 

* a common clock reference that is used by all streams 
* a way to convert the incoming sample streams to one agreed upon shared sample rate

The common clock reference doesn't need to be the same or even some kind of integer
multiple of the sample clock: what matters is that the different audio streams one way or the
other have derived their sample rate from this reference clock.

In professional audio production, this is done by having a primary clock generator and
feeding this clock to all other secondary devices. Generating a clock is pretty easy, 
so all you need are playback devices with a clock input.

A good example of this is the [Tascam CD-9010CF](https://tascam.com/us/product/cd-9010/feature) broadcast CD player.

![CD9010CF](/assets/asrc/Tascam_CD-9010CF.jpg)

It's a discontinued product now, but two of the listed features on its product website are:

* 1 BNC word-clock input (44.1/48kHz) 
* Sample Rate Converter plays 44.1kHz audio source at 48kHz when the incoming word clock sample rate is 48kHz

In other words, it satisfies the 2 requirements that I mentioned above.

One minor detail is that this kind of equipment is a little expensive. At the time of writing this,
[Prosound and Stage Lighting](https://www.pssl.com/products/tascam-cd9010cf-broadcast-cd-player-with-cf) still
had a product page up that lists the product at $4000, after a $500 discount.

I googled around a bit, but I wasn't able to find cheaper CD players with external clock input,
so something else must be done to work around the lack of sources with a common clock input.

The answer is **asynchronous sample rate conversion** (ASRC).

ASRC is a digital technique that accepts an input signal with one clock and resamples it to
a completely independent new clock while retaining as much as possible the characteristics
of the original signal.

You can buy audio ASRC chips on Digikey at prices that range between $10 and $20. Good examples
are the Analog Devices AD1895 and AD1896, the Texas Instruments SRC4382 and SRC4192,
the Cirrus Logic CS8421, and others. 

![AD1896 Block Diagram](/assets/asrc/AD1896_block_diagram.png)
*<center>AD1896 Block Diagram</center>*

If you need ASRC in your audio projects, I wouldn't hesistate to use one of those chips.

When you want to combine ASRC with DSP processing, you could choose the Analog Devices ADSP-21364
DSP, which contains 4 SRC cores that copy the functionatilty of the AD1896.

But what if you want to build an ASRC device yourself, from scratch? Not necessarily because it'll better
than commercial offerings, but maybe because you have sufficient unused logic available on your
FPGA and adding a discrete ASRC device would be a waste? Or simply because you want to use it as a
crutch to learn about a whole bunch of different DSP techniques that must be brought together to
make it happen.

The latter was my motivation. Like my PDM to PCM conversion series, I want to understand ASRC from
start to finish, leaving no question unanswered.

There is quite a bit of literature available about ASRC, but I wasn't able to find a concrete
implementation in C, Verilog, or even Matlab or NumPy. One of the goals of this series is to
fix that. Definitely a NumPy model, but maybe also something that can be run on a DSP or inside
and FPGA.

*This is redundant for those who've read my previous DSP topics, but in case there are newcomers:
I'm a DSP beginner. My blog posts are a structured record of a chaotic learning process. Writing
about a topic forces me to understand things much better than what would normally be required, but
there's a very high chance that I'm making some basic mistakes here and there. Keep that in mind!*


# SNR calculation from FFT

* max scale sine wave
* quantize with (say) 16 bits
* N samples
* N-sample FFT
* theoretical quantization SNR over the full Nyquist range for sine wave and no window function = 6.02 * 16 + 1.76 = 98.08dB
* This gets split over N/2 FFT frequency buckets
    * linear power: Power(SNR) / (N/2)
    * db: db10(SNR) - db10(N/2)

Reverse:
* Sample input at sample rate X
* Take FFT
* Actually, take multiple FFTs and average to get narrower noise floor
* Check where main signal is
* Ignore FFT value for main signal and harmonics (use average noise floor instead?)
    * don't exclude harmonics if you want SINAD (signal to noise and distortion ratio)
* Add up all remaining FFT values 

Example, using data from MT-003:

* FFT noise floor: -110dB
* 8192 samples
* convert dB to linear power: 10*log10(10^(-110/10) * 8192/2) =  73.9dB -> 74dB
    * In this case, I multiply by 4096, but I could have also just added all the values in the real world, when, 
      for example there's no noise floor with a fixed value.

When using a window, the FFT value must be multiplied by a correction factor.
This correction factor is different when correction for amplitude than for correcting for energy.

E.g. when calculation RMS value from an FFT -> use energy correction.

# FFT

**DFT Equation**

The standard equation of the DFT is as follows:

$$
X[k] = \sum_{n=0}^{N-1} x[n] \cdot e^{-2\pi i \frac{kn}{N}}, \quad k = 0, 1, 2, \dots, N-1
$$

We can write the exponential part as N-th rooth of unity format:

$$
\omega^n = e^{-2 i \pi n / N}
$$

Which reduces the DFT equation to this:

$$
X[k] = \sum_{n=0}^{N-1} x[n] \cdot \omega^{kn}, \quad k = 0, 1, 2, \dots, N-1
$$

**DFT Matrix**

This can just as well be written as a matrix, like this:

$$
\begin{bmatrix} 
X_0 \\
X_1 \\
X_2 \\
\vdots \\
X_{N-1}
\end{bmatrix} 
=
\begin{bmatrix}
1 & 1 & 1 & \cdots & 1 \\
1 & \omega & \omega^2 & \cdots & \omega^{N-1} \\
1 & \omega^2 & \omega^4 & \cdots & \omega^{2(N-1)} \\
\vdots & \vdots & \vdots & \ddots & \vdots \\
1 & \omega^{N-1} & \omega^{2(N-1)} & \cdots & \omega^{(N-1)(N-1)}
\end{bmatrix}
\begin{bmatrix}
x_0 \\
x_1 \\
x_2 \\
\vdots \\
x_{N-1}
\end{bmatrix}
$$

**DFT of size 8**

I'm not much of a math head and prefer to work concrete examples instead of manipulating
generic formulas. So let's try do that for a case where $$N=8$$.

In this case, the $$\omega$$ is defined as follows:

$$
\omega^k_8 = e^{-2 i \pi k / 8}
$$

Superscript $$k$$ indicates which of the 8th root it is. Subscript $$8$$ indicates that we're dealing 
with the 8th roots of unity. For everything that follows, we'll always be dealing with an 8-th root, so
I will drop it to avoid too much visual clutter.

The full DFT-8 matrix now becomes this one:

$$
\begin{bmatrix} 
X_0 \\
X_1 \\
X_2 \\
X_3 \\
X_4 \\
X_5 \\
X_6 \\
X_7 \\
\end{bmatrix} 
=
\begin{bmatrix} 
1 & 1 & 1 & 1 & 1 & 1 & 1 & 1 \\
1 & \omega^1_8 & \omega^{ 2}_8  & \omega^{ 3}_8 & \omega^{ 4}_8 & \omega^{ 5}_8 & \omega^{ 6}_8 & \omega^{ 7}_8   \\
1 & \omega^2_8 & \omega^{ 4}_8  & \omega^{ 6}_8 & \omega^{ 8}_8 & \omega^{10}_8 & \omega^{12}_8 & \omega^{14}_8   \\
1 & \omega^3_8 & \omega^{ 6}_8  & \omega^{ 9}_8 & \omega^{12}_8 & \omega^{15}_8 & \omega^{18}_8 & \omega^{21}_8   \\
1 & \omega^4_8 & \omega^{ 8}_8  & \omega^{12}_8 & \omega^{16}_8 & \omega^{20}_8 & \omega^{24}_8 & \omega^{28}_8   \\
1 & \omega^5_8 & \omega^{10}_8  & \omega^{15}_8 & \omega^{20}_8 & \omega^{25}_8 & \omega^{30}_8 & \omega^{35}_8   \\
1 & \omega^6_8 & \omega^{12}_8  & \omega^{18}_8 & \omega^{24}_8 & \omega^{30}_8 & \omega^{36}_8 & \omega^{42}_8   \\
1 & \omega^7_8 & \omega^{14}_8  & \omega^{21}_8 & \omega^{28}_8 & \omega^{35}_8 & \omega^{42}_8 & \omega^{49}_8   \\
\end{bmatrix}
\begin{bmatrix}
x_0 \\
x_1 \\
x_2 \\
x_3 \\
x_4 \\
x_5 \\
x_6 \\
x_7 \\
\end{bmatrix}
$$

We can write this as 8 sums:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X[0] & = x_0 &+&                 x_1 &+&                    x_2 &+&                   x_3 &+&                   x_4 &+&                   x_5 &+&                   x_6 &+&                   x_7 \\
X[1] & = x_0 &+& \omega^1  \cdot x_1 &+&  \omega^{ 2} \cdot x_2 &+& \omega^{ 3} \cdot x_3 &+& \omega^{ 4} \cdot x_4 &+& \omega^{ 5} \cdot x_5 &+& \omega^{ 6} \cdot x_6 &+& \omega^{ 7} \cdot x_7 \\
X[2] & = x_0 &+& \omega^2  \cdot x_1 &+&  \omega^{ 4} \cdot x_2 &+& \omega^{ 6} \cdot x_3 &+& \omega^{ 8} \cdot x_4 &+& \omega^{10} \cdot x_5 &+& \omega^{12} \cdot x_6 &+& \omega^{14} \cdot x_7 \\
X[3] & = x_0 &+& \omega^3  \cdot x_1 &+&  \omega^{ 6} \cdot x_2 &+& \omega^{ 9} \cdot x_3 &+& \omega^{12} \cdot x_4 &+& \omega^{15} \cdot x_5 &+& \omega^{18} \cdot x_6 &+& \omega^{21} \cdot x_7 \\
X[4] & = x_0 &+& \omega^4  \cdot x_1 &+&  \omega^{ 8} \cdot x_2 &+& \omega^{12} \cdot x_3 &+& \omega^{16} \cdot x_4 &+& \omega^{20} \cdot x_5 &+& \omega^{24} \cdot x_6 &+& \omega^{28} \cdot x_7 \\
X[5] & = x_0 &+& \omega^5  \cdot x_1 &+&  \omega^{10} \cdot x_2 &+& \omega^{15} \cdot x_3 &+& \omega^{20} \cdot x_4 &+& \omega^{25} \cdot x_5 &+& \omega^{30} \cdot x_6 &+& \omega^{35} \cdot x_7 \\
X[6] & = x_0 &+& \omega^6  \cdot x_1 &+&  \omega^{12} \cdot x_2 &+& \omega^{18} \cdot x_3 &+& \omega^{24} \cdot x_4 &+& \omega^{30} \cdot x_5 &+& \omega^{36} \cdot x_6 &+& \omega^{42} \cdot x_7 \\
X[7] & = x_0 &+& \omega^7  \cdot x_1 &+&  \omega^{14} \cdot x_2 &+& \omega^{21} \cdot x_3 &+& \omega^{28} \cdot x_4 &+& \omega^{35} \cdot x_5 &+& \omega^{42} \cdot x_6 &+& \omega^{49} \cdot x_7 \\
\end{array}
$$

We can't see it yet, but there are some significant reductions possible. Let's group the even and odd terms of $$x_k$$:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X[0] & = ( x_0 &+&                    x_2 &+&                    x_4 &+&                   x_6) &+& (&                   x_1 &+&                   x_3 &+&                   x_5 &+&                   x_7) \\
X[1] & = ( x_0 &+& \omega^{ 2}  \cdot x_2 &+&  \omega^{ 4} \cdot x_4 &+& \omega^{ 6} \cdot x_6) &+& (& \omega^{ 1} \cdot x_1 &+& \omega^{ 3} \cdot x_3 &+& \omega^{ 5} \cdot x_5 &+& \omega^{ 7} \cdot x_7) \\
X[2] & = ( x_0 &+& \omega^{ 4}  \cdot x_2 &+&  \omega^{ 8} \cdot x_4 &+& \omega^{12} \cdot x_6) &+& (& \omega^{ 2} \cdot x_1 &+& \omega^{ 6} \cdot x_3 &+& \omega^{10} \cdot x_5 &+& \omega^{14} \cdot x_7) \\
X[3] & = ( x_0 &+& \omega^{ 6}  \cdot x_2 &+&  \omega^{12} \cdot x_4 &+& \omega^{18} \cdot x_6) &+& (& \omega^{ 3} \cdot x_1 &+& \omega^{ 9} \cdot x_3 &+& \omega^{15} \cdot x_5 &+& \omega^{21} \cdot x_7) \\
X[4] & = ( x_0 &+& \omega^{ 8}  \cdot x_2 &+&  \omega^{16} \cdot x_4 &+& \omega^{24} \cdot x_6) &+& (& \omega^{ 4} \cdot x_1 &+& \omega^{12} \cdot x_3 &+& \omega^{20} \cdot x_5 &+& \omega^{28} \cdot x_7) \\
X[5] & = ( x_0 &+& \omega^{10}  \cdot x_2 &+&  \omega^{20} \cdot x_4 &+& \omega^{30} \cdot x_6) &+& (& \omega^{ 5} \cdot x_1 &+& \omega^{15} \cdot x_3 &+& \omega^{25} \cdot x_5 &+& \omega^{35} \cdot x_7) \\
X[6] & = ( x_0 &+& \omega^{12}  \cdot x_2 &+&  \omega^{24} \cdot x_4 &+& \omega^{36} \cdot x_6) &+& (& \omega^{ 6} \cdot x_1 &+& \omega^{18} \cdot x_3 &+& \omega^{30} \cdot x_5 &+& \omega^{42} \cdot x_7) \\
X[7] & = ( x_0 &+& \omega^{14}  \cdot x_2 &+&  \omega^{28} \cdot x_4 &+& \omega^{42} \cdot x_6) &+& (& \omega^{ 7} \cdot x_1 &+& \omega^{21} \cdot x_3 &+& \omega^{35} \cdot x_5 &+& \omega^{49} \cdot x_7) \\
\end{array}
$$

The right half of each of those 8 equations, the one with the odd $$x$$ elements, has a common $$\omega$$ factor:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X[0] & = ( x_0 &+&                    x_2 &+&                    x_4 &+&                   x_6) &+&            (&                   x_1 &+&                   x_3 &+&                   x_5 &+&                   x_7) \\
X[1] & = ( x_0 &+& \omega^{ 2}  \cdot x_2 &+&  \omega^{ 4} \cdot x_4 &+& \omega^{ 6} \cdot x_6) &+& \omega^{1} (& \omega^{ 0} \cdot x_1 &+& \omega^{ 2} \cdot x_3 &+& \omega^{ 4} \cdot x_5 &+& \omega^{ 6} \cdot x_7) \\
X[2] & = ( x_0 &+& \omega^{ 4}  \cdot x_2 &+&  \omega^{ 8} \cdot x_4 &+& \omega^{12} \cdot x_6) &+& \omega^{2} (& \omega^{ 0} \cdot x_1 &+& \omega^{ 4} \cdot x_3 &+& \omega^{ 8} \cdot x_5 &+& \omega^{12} \cdot x_7) \\
X[3] & = ( x_0 &+& \omega^{ 6}  \cdot x_2 &+&  \omega^{12} \cdot x_4 &+& \omega^{18} \cdot x_6) &+& \omega^{3} (& \omega^{ 0} \cdot x_1 &+& \omega^{ 6} \cdot x_3 &+& \omega^{12} \cdot x_5 &+& \omega^{18} \cdot x_7) \\
X[4] & = ( x_0 &+& \omega^{ 8}  \cdot x_2 &+&  \omega^{16} \cdot x_4 &+& \omega^{24} \cdot x_6) &+& \omega^{4} (& \omega^{ 0} \cdot x_1 &+& \omega^{ 8} \cdot x_3 &+& \omega^{16} \cdot x_5 &+& \omega^{24} \cdot x_7) \\
X[5] & = ( x_0 &+& \omega^{10}  \cdot x_2 &+&  \omega^{20} \cdot x_4 &+& \omega^{30} \cdot x_6) &+& \omega^{5} (& \omega^{ 0} \cdot x_1 &+& \omega^{10} \cdot x_3 &+& \omega^{20} \cdot x_5 &+& \omega^{30} \cdot x_7) \\
X[6] & = ( x_0 &+& \omega^{12}  \cdot x_2 &+&  \omega^{24} \cdot x_4 &+& \omega^{36} \cdot x_6) &+& \omega^{6} (& \omega^{ 0} \cdot x_1 &+& \omega^{12} \cdot x_3 &+& \omega^{24} \cdot x_5 &+& \omega^{36} \cdot x_7) \\
X[7] & = ( x_0 &+& \omega^{14}  \cdot x_2 &+&  \omega^{28} \cdot x_4 &+& \omega^{42} \cdot x_6) &+& \omega^{7} (& \omega^{ 0} \cdot x_1 &+& \omega^{14} \cdot x_3 &+& \omega^{28} \cdot x_5 &+& \omega^{42} \cdot x_7) \\
\end{array}
$$

The $$\omega$$ values between the parenthesis on the left and right are identical. But that's only
the first step. The real magic starts when we start simplifying the roots of unity.

XXX
The left and right right are DFT-4 after observing that $$\omega_8^k = \omega_4^{k/2}$$. This
only works when $$k$$ is even, but that's the case for the parts between parenthesis. 

Roots of unity are located evenly spaced on a unit circle in the complex plane. When you multiply
a number with the first root of unity, you rotate that number in the complex plane. After rotating
an 8th root of unity 8 times, you will end up where you started!

So the following equation is true for our DFT case where $$N=8$$:

$$
\begin{align}
\omega^{n + k 8} &= \omega^{n} \\
\end{align}
$$

Some examples: $$\omega^{12} = \omega^4$$, $$\omega^{37} = \omega^5$$, ...

For the specific case where the exponent is a multiple of 8: $$\omega^{k8} = \omega^0 = 1$$.

After making these exponent reductions on the 8 equations, we get this:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X[0] & = ( x_0 &+&                   x_2 &+&                    x_4 &+&                   x_6) &+&            (&  x_1 &+&                   x_3 &+&                   x_5 &+&                   x_7) \\
X[1] & = ( x_0 &+& \omega^{ 2} \cdot x_2 &+&  \omega^{ 4} \cdot x_4 &+& \omega^{ 6} \cdot x_6) &+& \omega^{1} (&  x_1 &+& \omega^{ 2} \cdot x_3 &+& \omega^{ 4} \cdot x_5 &+& \omega^{ 6} \cdot x_7) \\
X[2] & = ( x_0 &+& \omega^{ 4} \cdot x_2 &+&                    x_4 &+& \omega^{ 4} \cdot x_6) &+& \omega^{2} (&  x_1 &+& \omega^{ 4} \cdot x_3 &+&                   x_5 &+& \omega^{ 4} \cdot x_7) \\
X[3] & = ( x_0 &+& \omega^{ 6} \cdot x_2 &+&  \omega^{ 4} \cdot x_4 &+& \omega^{ 2} \cdot x_6) &+& \omega^{3} (&  x_1 &+& \omega^{ 6} \cdot x_3 &+& \omega^{ 4} \cdot x_5 &+& \omega^{ 2} \cdot x_7) \\
X[4] & = ( x_0 &+&                   x_2 &+&                    x_4 &+&                   x_6) &+& \omega^{4} (&  x_1 &+&                   x_3 &+&                   x_5 &+&                   x_7) \\
X[5] & = ( x_0 &+& \omega^{ 2} \cdot x_2 &+&  \omega^{ 4} \cdot x_4 &+& \omega^{ 6} \cdot x_6) &+& \omega^{5} (&  x_1 &+& \omega^{ 2} \cdot x_3 &+& \omega^{ 4} \cdot x_5 &+& \omega^{ 6} \cdot x_7) \\
X[6] & = ( x_0 &+& \omega^{ 4} \cdot x_2 &+&                    x_4 &+& \omega^{ 4} \cdot x_6) &+& \omega^{6} (&  x_1 &+& \omega^{ 4} \cdot x_3 &+&                   x_5 &+& \omega^{ 4} \cdot x_7) \\
X[7] & = ( x_0 &+& \omega^{ 6} \cdot x_2 &+&  \omega^{ 4} \cdot x_4 &+& \omega^{ 2} \cdot x_6) &+& \omega^{7} (&  x_1 &+& \omega^{ 6} \cdot x_3 &+& \omega^{ 4} \cdot x_5 &+& \omega^{ 2} \cdot x_7) \\
\end{array}
$$

Note how the top left half and the bottom left half are identical. This is true as
well for the parts in parenthesis for the top right half and the bottom right half, though
the common factor in front is different.

We can make another simplification to the roots of unity: points on the unit circle are point
symmetric when $$N$$ is even. When you rotate a point by $$N/2$$ units, you get the same value
but on the other side: the real and the imaginary part are inverted.

Mathematrically, this is written as follows:

$$
\begin{align}
\omega^{n + 4} &= -1 \cdot \omega^{n} \\
\end{align}
$$

Some examples: $$\omega^{5} = -\omega^1$$, $$\omega^{6} = \omega^2$$, ...

Note how $$\omega^{4} = -\omega^0 = -1$$.

Applied to the DFT-8 equations:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X[0] & = ( x_0 &+&                     x_2 &+&                    x_4 &+&                     x_6) &+&              (&  x_1 &+&                     x_3 &+&                   x_5 &+&                     x_7) \\
X[1] & = ( x_0 &+&   \omega^{ 2} \cdot x_2 &+&  -1          \cdot x_4 &+& - \omega^{ 2} \cdot x_6) &+&   \omega^{1} (&  x_1 &+&   \omega^{ 2} \cdot x_3 &+& -1          \cdot x_5 &+& - \omega^{ 2} \cdot x_7) \\
X[2] & = ( x_0 &+& - 1           \cdot x_2 &+&                    x_4 &+&   -1          \cdot x_6) &+&   \omega^{2} (&  x_1 &+&   -1          \cdot x_3 &+&                   x_5 &+&   -1          \cdot x_7) \\
X[3] & = ( x_0 &+& - \omega^{ 2} \cdot x_2 &+&  -1          \cdot x_4 &+&   \omega^{ 2} \cdot x_6) &+&   \omega^{3} (&  x_1 &+& - \omega^{ 2} \cdot x_3 &+& -1          \cdot x_5 &+&   \omega^{ 2} \cdot x_7) \\
X[4] & = ( x_0 &+&                     x_2 &+&                    x_4 &+&                     x_6) &+&   -1         (&  x_1 &+&                     x_3 &+&                   x_5 &+&                     x_7) \\
X[5] & = ( x_0 &+&   \omega^{ 2} \cdot x_2 &+&  -1          \cdot x_4 &+& - \omega^{ 2} \cdot x_6) &+& - \omega^{1} (&  x_1 &+&   \omega^{ 2} \cdot x_3 &+& -1          \cdot x_5 &+& - \omega^{ 2} \cdot x_7) \\
X[6] & = ( x_0 &+& - 1           \cdot x_2 &+&                    x_4 &+&   -1          \cdot x_6) &+& - \omega^{2} (&  x_1 &+&   -1          \cdot x_3 &+&                   x_5 &+&   -1          \cdot x_7) \\
X[7] & = ( x_0 &+& - \omega^{ 2} \cdot x_2 &+&  -1          \cdot x_4 &+&   \omega^{ 2} \cdot x_6) &+& - \omega^{3} (&  x_1 &+& - \omega^{ 2} \cdot x_3 &+& -1          \cdot x_5 &+&   \omega^{ 2} \cdot x_7) \\
\end{array}
$$

The common $$\omega$$ factors on the right half are now the same for the top and bottom 4 as well, but
with opposite sign.

Let's create the following sub-equations for the even and odd side:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X_e[0] & = ( x_0 &+&                   x_2 &+&  x_4 &+&                     x_6) \\
X_e[1] & = ( x_0 &+& \omega^{ 2} \cdot x_2 &-&  x_4 &-&   \omega^{ 2} \cdot x_6) \\
X_e[2] & = ( x_0 &-&                   x_2 &+&  x_4 &-&                     x_6) \\
X_e[3] & = ( x_0 &-& \omega^{ 2} \cdot x_2 &-&  x_4 &+&   \omega^{ 2} \cdot x_6) \\
\\
X_o[0] & = ( x_1 &+&                   x_3 &+&  x_5 &+&                     x_7) \\
X_o[1] & = ( x_1 &+& \omega^{ 2} \cdot x_3 &-&  x_5 &-&   \omega^{ 2} \cdot x_7) \\
X_o[2] & = ( x_1 &-&                   x_3 &+&  x_5 &-&                     x_7) \\
X_o[3] & = ( x_1 &-& \omega^{ 2} \cdot x_3 &-&  x_5 &+&   \omega^{ 2} \cdot x_7) \\
\end{array}
$$

With those, we can rewrite the DFT-8 equations like this:

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}
X[0] & = X_e[0] &+&            X_o[0] \\
X[1] & = X_e[1] &+& \omega^{1} X_o[1] \\
X[2] & = X_e[2] &+& \omega^{2} X_o[2] \\
X[3] & = X_e[3] &+& \omega^{3} X_o[3] \\
\\
X[4] & = X_e[0] &-&            X_o[0] \\
X[5] & = X_e[1] &-& \omega^{1} X_o[1] \\
X[6] & = X_e[2] &-& \omega^{2} X_o[2] \\
X[7] & = X_e[3] &-& \omega^{3} X_o[3] \\
\end{array}
$$

![DFT-8 DIT as 2 DFT-4](/assets/asrc/FFT-DIT_2xDFT4.svg)

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}

X_e[0] & = ( x_0 &+& x_4 &+&                   x_2 &+&                      x_6) \\
X_e[1] & = ( x_0 &-& x_4 &+& \omega^{ 2} \cdot x_2 &-&    \omega^{ 2} \cdot x_6) \\
X_e[2] & = ( x_0 &+& x_4 &-&                   x_2 &+&                      x_6) \\
X_e[3] & = ( x_0 &-& x_4 &-& \omega^{ 2} \cdot x_2 &-&    \omega^{ 2} \cdot x_6) \\

\end{array}
$$

$$
\begin{array}{ccrrrrrrrrrrrrrrrrrrrrrrrrrrrrr}

X_e[0] & = ( x_0 &+& x_4 ) &+&                   ( x_2 &+&    x_6) \\
X_e[1] & = ( x_0 &-& x_4 ) &+& \omega^{ 2} \cdot ( x_2 &-&    x_6) \\
X_e[2] & = ( x_0 &+& x_4 ) &-&                   ( x_2 &+&    x_6) \\
X_e[3] & = ( x_0 &-& x_4 ) &-& \omega^{ 2} \cdot ( x_2 &-&    x_6) \\

\end{array}
$$

#============================================================


# References


**Educational Links**

* [Thread on DIY Audio](https://www.diyaudio.com/forums/digital-source/28814-asynchronous-sample-rate-conversion.html)

    * [Blog post about this](http://hifiduino.blogspot.com/2009/06/how-asynchronous-rate-conversion-works.html). Same author?

* [An Efficient Asynchronous Sampling-Rate Conversion Algorithm for Multi-Channel Audio Applications](https://dspconcepts.com/white-papers/efficient-asynchronous-sampling-rate-conversion-algorithm-multi-channel-audio), P. Beckmann

    Very readable paper. Gives a good overview of some techniques, then presents a solution that runs
    on a SHARC DSP, with performance numbers, MIPS required etc.

* [A Stereo Asynchronous Digital Sample-Rate Converter for Digital Audio](https://ieeexplore.ieee.org/document/280698), R. Adams

    Paper from 1994 that gets referenced quite a bit.

* [Programming Asynchronous Sample Rate Converters on ADSP-2136x SHARC Processors (EE-268)](https://www.analog.com/media/en/technical-documentation/application-notes/EE268v01.pdf)

    Uses figures that are pretty much a direct copy from the paper above, but in color. :-)

    Describes a DSP software implementation, but software isn't available as source code.

* [Digital Audio Resampling Home Page](https://ccrma.stanford.edu/~jos/resample/), Julius O. Smith

    Has tons of information, including a list with free resampling software. However, it primarily
    discussed synchronous sample rate conversion.

* [High Performance Real-time Software Asynchronous Sample Rate Converter Kernel](https://www.semanticscholar.org/paper/High-Performance-Real-time-Software-Asynchronous-Heeb/6b9e4440ff28326463f82766d54e17aef632ef08), T. Heeb

    *Need to review*

* [Tonmeister series on audio jitter](https://www.tonmeister.ca/wordpress/category/jitter/)

    *Blog posts are in reverse chronological order.*

    [Part 8.3](https://www.tonmeister.ca/wordpress/2018/08/30/jitter-part-8-3-sampling-rate-conversion/)talks about ASRC.
    It also has a number of interesting links about audio sampling jitter.

* [Asynchronous Sample Rate Converter for Digital Audio Amplifiers](https://www.semanticscholar.org/paper/Asynchronous-Sample-Rate-Converter-for-Digital-Midya-Roeckner/25b0e9e86e092563f3c6c9ae4f4fe553db29771d), P. Midya

    Another paper about an ASRC implementation, this time on an FPGA. Don't add a lot of new interesting things.

* [Resampling Filters](http://www.ee.ic.ac.uk/hp/staff/dmb/courses/DSPDF/01300_Resampling.pdf)

    General course on resampling. Includes things like polynomial approximation. Doesn't specifically 
    deal with ASRC, but interesting.

**Silicon**

* [TI SRC4382](https://www.ti.com/product/SRC4382)

    * THD+N: -125dB
    * Dynamic range: 128dB
    * Sample rates: up to 216kHz
    * $11.75

* [TI SRC4192](https://www.ti.com/product/SRC4192)

    * THD+N: -140dB
    * Dynamic range: 144dB
    * Sample rates: up to 212kHz
    * Up to 24 bits
    * $12.2

* [AD1895](https://www.analog.com/en/products/ad1895.html)/[AD1896](https://www.analog.com/en/products/ad1896.html)

    * THD+N: -122dB/-133dB resp.
    * Dynamic range: 142dB 
    * Up to 24 bits
    * $10/$21

    The "ASRC Functional Overview - Theory of Operation" section of the datasheet is excellent.

* [AD1890](https://www.analog.com/en/products/ad1890.html)

    Obsolete product, but just like the AD1896, the datasheet is very educational.

* [Cirrus Logic CS8421](https://www.cirrus.com/products/cs8421/)

    * THD+N: -140dB
    * Dynamic range: 175dB
    * Sample rates: up to 1921kHz
    * Up to 32 bits
    * $11.45

**SNR Calculation**

* [Digital Audio Jitter Fundamentals](https://www.audiosciencereview.com/forum/index.php?threads/digital-audio-jitter-fundamentals-part-2.1926/)

    Shows impact of jitter on SNR. Many graphs.


**More Links**

Needs to be curated...

* [TI - Understanding Signal to Noise Ratio (SNR) and Noise Spectral Density (NSD) in High Speed Data Converters](https://training.ti.com/understanding-signal-noise-ratio-snr-and-noise-spectral-density-nsd-high-speed-data-converters)

    Also has a link to PDF file with all the slides.
* [Oregon State - SNR Calculation and Spectral Estimation](http://classes.engr.oregonstate.edu/eecs/spring2017/ece627/Lecture%20Notes/FFT%20for%20delta-sigma%20spectrum%20estimation.pdf)
* [National Instruments - The Fundamentals of FFT-Based Signal Analysis and Measurement](https://www.sjsu.edu/people/burford.furman/docs/me120/FFT_tutorial_NI.pdf)
* [Analog-to-Digital Converter Testing](https://www.mit.edu/~klund/A2Dtesting.pdf), K. Lundberg

    Extensive information about A/D testing. In section 2.2, it has the crucial observation that the
    test signals should have an integer number of cycles over the sample period **but that the
    number of cycles should be odd and prime, so that there is no common number between the number
    of input periods and the number of samples in the data record.**

    Links to the FJ Harris paper below on how to deal with windowing, if you need it.

* [On the Use of Windows for Harmonic Analysis With the Discrete Fourier Transform](https://www.researchgate.net/publication/2995027_On_the_Use_of_Windows_for_Harmonic_Analysis_With_the_Discrete_Fourier_Transform), FJ Harris

* [Jitter etc](http://www.jitter.de/english/how.html)

    Talks about *not* using ASRC to de-jitter.

* [IEEE Std 1241-2010 - IEEE Standard for Terminology and Test Methods for Analog-to-Digital Converters](http://class.ece.iastate.edu/djchen/ee509/2018/IEEE1241-2011.pdf)

    Has sections about FFT, windowing etc.

* [The ups and downs of arbitrary sample rate conversion](http://www.simonebianchi.net/downloads/The_ups_and_downs_of_ASRC.pdf)

* [Sample Rate Conversion in Digital Signal Processors](https://www2.spsc.tugraz.at/www-archive/downloads/1_SRC_Marian_Forster_1031275.pdf)

    Bachelor's thesis that compares different SRC chips (e.g. AD1895)


dsp.stackexchange.com

* [Answer to my question on dsp.stackexchange](https://dsp.stackexchange.com/questions/70154/quantization-snr-of-sine-wave-doesnt-match-1-761-6-02-q/70158#70158)
* [FFT to spectrum in decibel](https://dsp.stackexchange.com/a/32080/52155)

    How to calibrate an FFT for windowing function to get dBFS etc.

* [Measure the SNR of a signal in the frequency domain?](https://dsp.stackexchange.com/a/14864/52155)
* [How to calculate the Signal-To-Noise Ratio](https://dsp.stackexchange.com/a/17875/52155)


* [Spectrum and spectral density estimation by the Discrete Fourier transform (DFT), including a comprehensive list of window functions and some new flat-top windows](/assets/asrc/GH_FFT.pdf)

    Fantastic overview on how to estimate power spectra etc in the real world. Discusses spectrum scaling,
    windowing functions, all the basics.

* [Z-transform done quick](https://fgiesen.wordpress.com/2012/08/26/z-transform-done-quick/)

**FFT**

* [The Fast Fourier Transform in Hardware: A Tutorial Based on an FPGA Implementation](/assets/asrc/FFTtutorial121102.pdf)

* [A Survey on Pipelined FFT Hardware Architectures](/assets/asrc/s11265-021-01655-1.pdf) 

* [Real valued FFTs](https://kovleventer.com/blog/fft_real/)

    How to use a standard FFT algorithm to efficiently perform FFTs on input datasets that
    are real only.

    Blog post that explains everything step by step.

* [Implementing Fast Fourier Transform Algorithms of Real-Valued Sequences With the TMS320 DSP Platform](https://www.ti.com/lit/an/spra291/spra291.pdf)

    TI: How to use a standard FFT algorithm to efficiently perform FFTs on input datasets that
    are real only.

* [FFT Implementation on the TMS320VC5505, TMS320C5505, and TMS320C5515 DSPs](https://www.ti.com/lit/an/sprabb6b/sprabb6b.pdf)

    Describes the HWAFFT hardware FFT accelerator, how to use it, and also how to do larger FFTs than the ones
    that are natively supported by the accelerator.

* [Notes on FFTs: for implementers](https://fgiesen.wordpress.com/2023/03/19/notes-on-ffts-for-implementers/)
* [Notes on FFTs: for users](https://fgiesen.wordpress.com/2023/03/19/notes-on-ffts-for-users/)

* [Decimation in time and frequency](https://www.slideshare.net/slideshow/decimation-in-time-and-frequency/16032956)

    Slide presentation

* [Cooley - How the FFT Gained Acceptance](https://dl.acm.org/doi/pdf/10.1145/87252.88078)

* [Fast Fourier Transforms-for Fun and Profit](https://www.cis.rit.edu/class/simg716/FFT_Fun_Profit.pdf)

    DIF alternative to Cooley DIT.

* [Stackexchange - Differences between DIT & DIF algorithms](https://dsp.stackexchange.com/questions/53865/differences-between-dit-dif-algorithms)

    Derives the equations for DIT and DIF in small steps.

* [A 1 Million-Point FFT on a Single FPGA](http://liu.diva-portal.org/smash/get/diva2:1367440/FULLTEXT01.pdf)

* [DFT/FFT and Convolution Algorithms: Theory and Implementation](https://www.researchgate.net/publication/234784945_DFTFFT_and_Convolution_Algorithms_Theory_and_Implementation)

    Book on FFT implementation. PDF available.

* [dsprelated.com - DIT & DIF vs. normal & bit-reversed ordering](https://www.dsprelated.com/showthread/comp.dsp/136332-1.php)

* [Implementing the Radix-4 Decimation in Frequency (DIF) Fast Fourier Transform (FFT) Algorithm Using a TMS320C80 DSP](https://www.ti.com/lit/an/spra152/spra152.pdf)

* [Quora - What is the difference between decimation in time and decimation in frequency?](https://www.quora.com/What-is-the-difference-between-decimation-in-time-and-decimation-in-frequency)

* [Fast Fourier Transform (FFT)](https://www.cmlab.csie.ntu.edu.tw/cml/dsp/training/coding/transform/fft.html)

    Short yet quite comprehensive. DIF, DIT, Radix 4, split-radix.
    
* [NYU - The Fast Fourier Transform (FFT)](https://eeweb.engineering.nyu.edu/iselesni/EL713/zoom/fft)

    Probably the best derivation for DIF and DIT.

    [All classes of this course](https://eeweb.engineering.nyu.edu/iselesni/EL713/zoom/)

* [Multidigit multiplication for mathematicians](https://cr.yp.to/papers/m3-20010811-retypeset-20220327.pdf)

* [Lyons - The Swiss Army Knife of Digital Networks](https://www.iro.umontreal.ca/~mignotte/IFT3205/Documents/TipsAndTricks/TheSwissArmyKnifeOfDigitNetwork.pdf)

* [List of interesting papers](https://eeweb.engineering.nyu.edu/iselesni/EL713/zoom/paper_report_assignment.txt)
