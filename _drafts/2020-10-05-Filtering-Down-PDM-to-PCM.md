---
layout: post
title: Filtering Down PDM to PCM
date:  2020-10-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction



# PDM to PCM Problem Statement

The problem that we want to solve now convert that PDM signal to a PCM signal while
maintaining the the quality level of the microphone.

Going forward, I'll use the characteristics of the ST MP34DT01-M microphone of my
Adafruit test board.

From [the datasheet](https://cdn-learn.adafruit.com/assets/assets/000/049/977/original/MP34DT01-M.pdf): 

![Microphone Characteristics Table](/assets/pdm/pdm2pcm/mic_characteristics.png)

![Microphone Frequency Response](/assets/pdm/pdm2pcm/mic_freq_response.png)

We can use this to help set the requirements for our design:

* An output sample rate of 48kHz

    48kHz is universally supported and probably the most common sample rate for high quality audio, 
    though it's obviously overkill for a microphone that only goes up to 10kHz.

* 1.920 MHz PDM sample rate 

    The microphone supports a PDM clock rate between 1 and 3.25MHz. 

    We shall soon see that some very efficient filters are perfect for 2x decimation, 
    so it's best to select a ratio that's divisible by 2 or by 4.

    3.072MHz is 64 times higher and 1.920MHz is 40 times higher than our desired output rate 
    of 48kHz. Let's choose the lower clock: in the real world, that's something
    you'd choose to reduce power consumption.

* A passband of our signal runs from 0 to 6kHz

    State of the art MEMS microphones have a flat sensitivity curve that goes all the way up 
    to 20kHz, but this microphone is definitely not in that category. The frequency
    response is only flat between 100Hz and 5kHz, after which is starts going up. And
    there's not data above 10kHz.

* The stop band starts at 10kHz

    Since the specification of the microphone doesn't say anything about behavior above
    10kHz, I'm simply assuming that this is no-go territory, so that's where the
    stop band will start.

* The SNR of our signal in the passband is 61dB

    I will use this number to set the minimum attenuation of all the filters that operate 
    in the stop band.

    *I'm not sure if that's the right way to do it.*

* The maximum ripple we're willing to accept in the passband is 0.1dB

    This seems to be a pretty typical requirement for high quality audio?

# Designing Filters with pyFDA

One could use Matlab or NumPy to explore different filter configurations, but during the
initial stages, it's often faster to play around with a GUI. It's also a great way
to learn about what's out there and familiarize yourself with characteristics
of different kinds of filters.

In [a recent tweet](https://twitter.com/matthewvenn/status/1311611352021118976), Matt Venn
pointed me to [pyFDA](https://github.com/chipmuenk/pyfda), short for Python Filter
Design Analysis tool, and [his video tutorial](https://www.youtube.com/watch?v=dtK-4JZ4Cwc) 
about it.

I've since been using it, and it definitely helped me in getting the current design
off the ground.

In the screenshot below, you can see an exampe of a loop pass filter that has all the
pass band and stop band characteristics that we need for our microphone, with a
sample rate of 48kHz:

![pyFDA screenshot](/assets/pdm/pdm2pcm/pyFDA.png)

pyFDA tells us that we need a 37-order filter. 

There are all kinds of visualizations: magnitude frequency response, phase frequency response, 
impulse response, group delay, pole/zero plot, even a fancy 3D plot that I don't quite understand.

Once you've designed a filter, you can export the coefficients to use in your design. pyFDA can
even write out a Verilog file to put on your ASIC or FPGA. 

# Designing Filters with NumPy's Remez Function

For all its benefits, once the basic architecture of a design has been determined,
I prefer to code all the details as a stand-alone numpy file. For the following reasons:

* It allows me to parameterize the input parameters and regenerate all the collaterals
  (coefficients, graphs) in one go
* Much more flexilibity wrt graphs

    All the graphs in this blog post have been created by the [following Python script](...).

* it's much easier for others to reproduce the results, and modify the code, learn from it.

The question is: how do you do that?

There are multiple techniques to designing FIR filters. I'm not at all qualified to give
a comprehensive overview, but here are some very common ways to determine the coefficients
of FIR filters:

I already written about [Moving Average and CIC filters](2020/09/30/Moving-Average-and-CIC-Filters.html)
earler. Their coefficients are all the same. pyFDA supports them by selecting the "Moving Average"
option.

There are [Windowed Sinc filters](http://www.dspguide.com/CH16.PDF) and [Windowed FIR filter](http://www.dspguide.com/CH17.PDF)
where you specify a filter in the frequency domain, take an inverse FFT to get an impulse
response, and then us a windowing function to turn the behavior. NumPy and the 
[`firwin`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin.html) and
[`firwin2`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.firwin2.html) function
for those. Use the "Windowed FIR" option in pyFDA for this one.

And finally, there is the 
[Parks-McClellan filter design algorithm](https://en.wikipedia.org/wiki/Parks%E2%80%93McClellan_filter_design_algorithm),
as far as I can tell, is the most common way to design FIR filters. That's what I used in my earlier
pyFDA example by selecting the default "Equiripple" option.

It would lead too far to get into the details about the benefits of one kind of filter
vs the other, but when given specific pass band and stop band parameters, Parks-McClellan
filters seem requires the lowest number of FIR coefficients to achieve the desired performance.

YOU can use the the [`remez`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.remez.html)
function in NumPy to design filters this way, and that exactly what I've been doing.

For example, the coefficients of the filter above in my pyFDA example, can be found as follows:

```python
#! /usr/bin/env python3
from scipy import signal

Fs  = 48                # Sample rate
Fpb = 6                 # End of pass band
Fsb = 10                # Start of stop band
Apb = 0.05              # Max Pass band ripple in dB
Asb = 60                # Min stop band attenuation in dB
N   = 37                # Order of the filter (=number of taps-1)

# Remez weight calculation: https://www.dsprelated.com/showcode/209.php
err_pb = (1 - 10**(-Apb/20))/2      # /2 is not part of the article above, but makes the result consistent with pyFDA
err_sb = 10**(-Asb/20)

w_pb = 1/err_pb
w_sb = 1/err_sb
    
# Calculate that FIR coefficients
h = signal.remez(
      N+1,            # Desired number of taps
      [0., Fpb/Fs, Fsb/Fs, .5], # Filter inflection points
      [1,0],          # Desired gain for each of the bands: 1 in the pass band, 0 in the stop band
      [w_pb, w_sb]    # weights used to get the right ripple and attenuation
    )               

print(h)
```

Run the code above, and you'll get the following 38 filter coefficients: 
```
[-2.50164675e-05 -1.74317423e-03 -2.54534101e-03 -7.63329067e-04
  3.77271590e-03  6.73718674e-03  2.64362264e-03 -7.87738320e-03
 -1.48337024e-02 -6.75502030e-03  1.48004646e-02  2.98724354e-02
  1.54099648e-02 -2.76986944e-02 -6.25133368e-02 -3.81892367e-02
  6.54474060e-02  2.09343906e-01  3.13554280e-01  3.13554280e-01
  2.09343906e-01  6.54474060e-02 -3.81892367e-02 -6.25133368e-02
 -2.76986944e-02  1.54099648e-02  2.98724354e-02  1.48004646e-02
 -6.75502030e-03 -1.48337024e-02 -7.87738320e-03  2.64362264e-03
  6.73718674e-03  3.77271590e-03 -7.63329067e-04 -2.54534101e-03
 -1.74317423e-03 -2.50164675e-05]
```

A little bit more additional code, will create a frequeny response plot:

```python
import numpy as np
from matplotlib import pyplot as plt

# Calculate 20*log10(x) without printing an error when x=0
def dB20(array):
    with np.errstate(divide='ignore'):
        return 20 * np.log10(array)

(w,H) = signal.freqz(h)

# Find pass band ripple
Hpb_min = min(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
Hpb_max = max(np.abs(H[0:int(Fpb/Fs*2 * len(H))]))
Rpb = 1 - (Hpb_max - Hpb_min)
    
# Find stop band attenuation
Hsb_max = max(np.abs(H[int(Fsb/Fs*2 * len(H)+1):len(H)]))
Rsb = Hsb_max
    
print("Pass band ripple:      %fdB" % (-dB20(Rpb)))
print("Stop band attenuation: %fdB" % -dB20(Rsb))

plt.figure(figsize=(10,5))
plt.subplot(211)
plt.title("Impulse Response")
plt.stem(h)
plt.subplot(212)
plt.title("Frequency Reponse")
plt.grid(True)
plt.plot(w/np.pi/2*Fs,dB20(np.abs(H)), "r")
plt.plot([0, Fpb], [dB20(Hpb_max), dB20(Hpb_max)], "b--", linewidth=1.0)
plt.plot([0, Fpb], [dB20(Hpb_min), dB20(Hpb_min)], "b--", linewidth=1.0)
plt.plot([Fsb, Fs/2], [dB20(Hsb_max), dB20(Hsb_max)], "b--", linewidth=1.0)
plt.xlim(0, Fs/2)
plt.ylim(-90, 3)

plt.tight_layout()
plt.savefig("remez_example_filter.svg")
```

Run this and you get:
```
Pass band ripple:      0.047584dB
Stop band attenuation: 60.316990dB
```

And the following plot:

![Remez Filter Plot](/assets/pdm/pdm2pcm/remez_example_filter.svg)

Check out [`remez_example.py`](https://github.com/tomverbeure/pdm/blob/master/modeling/pdm2pcm/remez_example.py) 
for the full source code.

# First try: Just Filter the Damn Thing!

Implementing filters is easy: you fire up your favorite filter design tool, enter the desired
parameters, and the tool does all the rest.

In my case, that design tool is `pyFDA`. It's great for experimentation and what-if testing,
and you don't need to type a letter of code. It uses NumPy under the hood, so that's
an obvious alternative.

After filling in our requirements, and selecting "Equiripple" filter, pyFDA first
warns us that there'll be a huge amount of coefficients, and that's the math may
become too imprecise because of it. It's not a good sign.

A few second later, it comes up with a filter that has 2174 taps.

Luckily, we're working a decimation filter, so we don't need to evaluate this
filter for each input sample, only for each output sample. At 48kHz, this
means that we need 48000 * 2174 = 104M multiplications per second.

That's a lot!

# Decimation is a Divide and Conquer Problem

It turns out that, given the same pass band and stop band frequencies, and corresponding attenuation,
changing the sample rate results in a non-linear increase or decrease of the number of taps.

For example: if we fill in the same parameters but halve the sample rate from 3072 kHz to 1536 kHz, the
number of taps reduces from 2174 to 628.

48000 * 2174 = 104M multiplications
48000 * 628  = 30M multiplications

However, before we can use that smaller filter, we first need to decimate our original signal by
a factor of two to get that 1536 kHz input rate.

But decimating by 2 requires only a very gentle FIR filter. The pass band stays the same, 14 kHz,
but the stop band only starts at 1/4th of the input sample rate, or 788kHz. After filling in
those numbers, we end up with 15 taps.

Not don't get too excited: the output of this first filter runs at 1536kHz, not 48kHz, so
the number of multiplications per second for that one is:

   1,576,000 * 15   = 23M multiplications

After splitting up our monolithic 64x decimation filter in a 2x decimation filter followed
by a 32x decimation filter, we end up with a total of:

```
   1,576,000 * 15   = 23M multiplications
      48,000 * 628  = 30M multiplications
   --------------------------------------
                      53M multiplications total

```

We can continue this sequence a split up the 32x decimation filter into smaller piece too!

But let's not go into that rabbit hole, because there are much better alternatives.



# Major Sample Rate Reduction with a CIC Filter

In a [previous blog post](...), I wrote about CIC filters in preparation of this blog post.
CIC filters make it possible to reduce the amount of hardware to decimate a signal by a large
factor with next to no resources: no multipliers, and only a handful of register and adders.

The only price to pay is less than ideal behavior in the pass band, and a terrible stop band
if used stand-alone, but that's something that can be fixed by having additional stages.

And that's exactly what we're doing here in our divide-and-conquer approach.

Here's the plan: we use a factor 16 CIC decimation filter to bring the sample rate
down from 3072 kHz to 192 kHz. 16x is a good compromise: it's a significant reduction,
yet the pass band attenuation at 14kHz is only XXXX.

If we then use the monolitic approach to decimate by a factor of 4 to end up with a 48kHz
output rate, we'd need 57 taps.

```
    48,000 * 57 = 2.7M multiplications
```

We can do better by splitting up the 4x decimator into 2 2x decimators:

* 192 -> 96: 18 taps
*  96 -> 48: 28 taps

```
     96,000 * 18  = 1.7M multiplications
     48,000 * 28  = 1.3M multiplications
   --------------------------------------
                    3.0M multiplications total

```

Apparently not! There seems to be some kind of cross-over point below which there
isn't a benefit in splitting up.

Still, we went from 104M to just 2.7M multiplications, a 38x improvement!

Can we do better?

# Stop Band Optimization

So far, the stop band of the intermediate decimation filter has been suboptimal: we
simply put it at 1/4th of the input rate, because that's what you do for a monolithic
decimation filter.

But it's not optimal in a divide an conquer configuration!

When we decimate from 192 to 96, it's overkill to put the stop band at 48kHz: we can
put the stop band at (96-20) = 76 kHz instead!

Yes, the frequency range from 48kHz to 76kHz will now alias onto 20kHz to 48kHz range,
but who cares? Nobody can hear anything above 20kHz anyway, and we have another filter
comping up to clean things up in the next decimation step!

With this new stop band constraint, there are only 11 filter taps instead of the earlier
18, for a total of:


```
     96,000 * 10  = 1.1M multiplications
     48,000 * 28  = 1.3M multiplications
   --------------------------------------
                    2.3M multiplications total

```

# Exploiting Filter Symmetry

For audio applications, linear phase behavior is important: the human ear is able to detect
phase differences in otherwise similar signals.

An FIR filter with linear phase behavior must have symmetry in its filter coefficients. And
all the filters we've designed so far have exactly that.

Because of this symmetry, each filter coefficient (except for the center one) will appear
twice, mirrored around the center tap. By adding the input samples that use the same filter coefficient
before doing the multiplication, we can reduce the number of multiplications by half!

Instead of 57 multiplications, we're now at 1+(56/2) = 29 multiplications per output sample.

# Best Case Low Pass Filtering

It should be abundantly clear now that we need that low pass filter before we can decimate to
a lower sample rate.

Let's use the following parameters:

* Original sample rate: 3.072 MHz
* Oversample rate factor: 64
* Desired sample rate: 48 kHz
* Original signal bandwidth: 20 kHz
* Desired pass band: 0 dB
* Desired stop band: 96 dB

I chose 96 dB because that's the theoretical maximum SNR for 16-bit audio. Most PDM microphones only
have an SNR in the low sixties, so this is overly aggressive, but let's just see what we can do.

The transition from pass band to stop band will start at 20 kHz. And if we look at the graph for
a 64x oversampling, 4th order sigma-delta convertor, we see that the noise goes above 96 dB 

Since the noise starts going up immediately above 24 kHz (=48/2), we have 4 kHz to construct a filter
that goes from a pass band to the stop band. 

# References

**Sigma-Delta AD Convertors**

* [How delta-sigma ADCs work, Part 1](https://www.ti.com/lit/an/slyt423a/slyt423a.pdf) 
   and [Part 2](https://www.ti.com/lit/an/slyt438/slyt438.pdf)

    Texas Instruments article.  Part 1 is a pretty gentle introduction about the sigma-delta basics.
    Part 2 talks about filtering to go from PDM to PCM, but it's very light on details.

* [Understanding PDM Digital Audio](http://users.ece.utexas.edu/~bevans/courses/realtime/lectures/10_Data_Conversion/AP_Understanding_PDM_Digital_Audio.pdf)

**Filter Design**

* [Tom Roelandts - How to Create a Simple Low-Pass Filter](https://tomroelandts.com/articles/how-to-create-a-simple-low-pass-filter)

    Simple explanation, Numpy example code.

* [Design of FIR Filters](https://www.vyssotski.ch/BasicsOfInstrumentation/SpikeSorting/Design_of_FIR_Filters.pdf)

    Good presentation about different ways to design filters, Remez, ripple etc.

* [Remez (FIR design) Weights from Requirements](https://www.dsprelated.com/showcode/209.php)

    Shows how to calculate weights for the Remez algorithm (though there seems to be an off-by-2
    error for the passband weights.)

* [Halfband Filter Design with Python/SciPy](https://www.dsprelated.com/showcode/270.php)

    Simple example that shows how to calculate half-band filter coefficients with NumPy using the Remez
    algorithm and with a windowed sinc filter. However, it doesn't discuss how to calculate the weights
    of the Remez algorithm.

* [Multiplier-Free Half-Band Filters](https://www.cs.tut.fi/~ts/sldsp_part2_identical_subfilters_halfband.pdf)

    Excellent discussion about half band filters, ways to design them, and how to design them without
    multipliers. Also has an extensive example on how to convert from PDM to PCM with a CIC filter followed
    by 4 half band filters.

    The [website of this professor](https://www.cs.tut.fi/~ts/) has a lot of course notes online. They are 
    all worth reading.

**Decimation**

* [Optimum FIR Digital Filter Implementations for Decimation, Interpolation, and Narrow-Band Filtering](https://web.ece.ucsb.edu/Faculty/Rabiner/ece259/Reprints/087_optimum%20fir%20digital%20filters.pdf)

    Paper that discusses how to size cascaded filter to optimized for FIR filter complexity.

* [Seamlessly Interfacing MEMS Microphones with Blackfin Processors](https://www.analog.com/media/en/technical-documentation/application-notes/EE-350rev1.pdf)

    Analog Devices application note. C code can be found[here](https://www.analog.com/media/en/technical-documentation/application-notes/EE350v01.zip)



