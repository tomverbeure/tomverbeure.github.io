---
layout: post
title: Oscilloscope Bandwidth
date:   2024-04-14 00:00:00 -1000
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

I have a bit of an oscilloscope problem. I started out with buying a pretty expensive new one,
a Siglent 2304X, but somehow that wasn't enough and one way or the other that lonely scope
multiplied into a rotating stable of old faithfuls.

The scopes have different analog bandwidths and sample rates. I wanted to check out how that's
visible in practice.

So I connected them to my Rohde & Schwarz SMHU signal generator and checked the recorded the
measured amplitude for increasing frequency values.

# Measurement Setup


# Siglent 2304X


# TDS 540 - 500MHz/1Gsps

![TDS 540 photo](/assets/scope_bw/tds540_photo.jpg)

I bought the TDS 540 cheap enough, knowing that one line item reported a FAIL during power-on
self test. Emboldened by earlier TDS 420A reverse engineering adventures, I assumed it wouldn't
be very difficult to fix. Alas, the previous owner of the scope was a fairly prominent test equipment
repair YouTuber who had already tried and failed to fix the error. I was never able to 
find an issue with the scope when using it.

At 500Mhz, it has a slightly higher bandwidth than my Siglent 2304X. The sample rate of
1 Gsps is too low for non-repetitive signals but Tektronix' equivalent time sampling is
useful enough repetitive ones.

Soon after getting this scope, a friend gave me an HP Infiniium 54825A with better specs all around 
and this scope ended up in a closet. After making this blog post, I sold the scope through Craigslist
for only a small loss. Let's have a look at how it performed:

When set to a sample rate of 1Gsps, even a 200MHz become problematic.
Due to undersampling, the peaks aren't always recorded and the measured Vpk-pk
values vary between 1.58V and 1.64V.

![TDS540 200MHz, 1Gsps](/assets/scope_bw/tds540_200MHz_1Gsps.png)

In the image above, the samples are interpolated using a $$\sin(x)/x$$ filter.
If you disable interpolation and only look at the dots, you get something
like this:

![TDS540 200MHz, 1Gsps, dots](/assets/scope_bw/tds540_200MHz_1Gsps_dots.png)

When the sample rate is 5 times the input frequency, there's not a lot to
work with.

However, the TDS 540 has a feature called 'equivalent time sampling' (ET)
where the signal is repeatedly sampled at random after the trigger and
fills up the signal over time. This only works for periodic signals, but it gets you a 
lot of detail! And the measured peak-to-peak voltage now make more sense too.

Since I want to measure the bandwidth, I'll use ET sampling when it's
available...

![TDS540 200MHz, 5Gsps](/assets/scope_bw/tds540_200MHz_5Gsps.png)

| Frequency (MHz) | Sample Rate (Gsps) | Vpk-pk (V) |
|-----------------|--------------------|------------|
| 20              | 1                  | 1.86       |
| 50              | 1                  | 1.84       |
| 100             | 1                  | 1.74       |
| 200             | 1                  | 1.54       |
| 200             | 10 (ET)            | 1.70       |
| 250             | 10                 | 1.62       |
| 300             | 10                 | 1.54       |
| 350             | 10                 | 1.42       |
| 400             | 25                 | 1.34       |
| 450             | 25                 | 1.28 (?)   |
| 500             | 50                 | 1.34       |
| 530             | 50                 | 1.34       |
| 550             | 100                | Garbage    |

You'd expect the measured amplitude of the signal to gracefully fade away
with increasing frequency, but somewhere between 530 and 550MHz, equivalent time 
samples suddenly breaks down.

![TDS540 550MHz, 100Gsps ET breakdown](/assets/scope_bw/tds540_550MHz_100Gsps.png)

I think the trigger logic stops working around that time: for equivalent 
time sampling, the trigger needs to be very precise.

When plotted in a chart, you get this:

![TDS540 frequency response graph](/assets/scope_bw/tds540_freq_response.png)

# HP 54542A - 500MHz/2Gsps

![HP 54542A picture](/assets/scope_bw/hp54542a_photo.jpg)

This scope has been a spectacular $20 flea market purchase. I just love the user interface.
Like the TDS 540 it has a useless numerical keypad, but unlike the TDS 540 those keys
can also be used to quickly select measurements.

I once again selected Vpk-pk as the main measurement and threw in frequency
measurement too.


![HP 54542A 500MHz/2Gsps](/assets/scope_bw/hp54542a_500MHz_2Gsps.png)

Let's see how it performs:

| Frequency (MHz) | Sample Rate (Gsps) | Vpk-pk (V) |
|-----------------|--------------------|------------|
| 20              | 2                  | 1.80       |
| 50              | 2                  | 1.76       |
| 100             | 2                  | 1.67       |
| 200             | 2                  | 1.68       |
| 250             | 2                  | 1.70       |
| 300             | 2                  | 1.69       |
| 350             | 2                  | 1.76       |
| 400             | 2                  | 1.81       |
| 450             | 2                  | 1.81       |
| 500             | 2                  | 1.65       |
| 550             | 2                  | 1.46       |
| 600             | 2                  | 1.27       |
| 650             | 2                  | 1.13       |
| 700             | 2                  | 0.898      |
| 750             | 2                  | 0.681      |
| 800             | 2                  | 0.505      |
| 850             | 2                  | 0.352      |
| 900             | 2                  | 0.260      |
| 950             | 2                  | 0.212      |
| 1000            | 2                  | 0.135 (*)  |

The measured amplitude isn't supposed to increase when going from 200 MHz to 400 MHz,
but it's not a huge deal. As expected, the amplitude starts going down at 500 MHz and
it shows a decent sine wave all the way down to 1GHz. 

![HP 54542A frequency response graph](/assets/scope_bw/hp54542a_freq_response.png)


