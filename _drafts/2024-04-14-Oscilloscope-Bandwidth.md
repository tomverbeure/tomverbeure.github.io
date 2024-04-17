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

# TDS 540 - 500MHz/1Gsps

I bought this scope cheap enough and had plans to do some repairs on it, and because
it had a higher bandwidth than my Siglent 2304X. But soon after a friend gave
me an HP Infiniium XXX with better specs and this scope ended up in a closet.

When set to a sample rate of 1Gsps, even a 200MHz become problematic.
Due to undersampling, the peaks aren't always recorded and so the Vpk-pk
varies between 1.58V and 1.64V.

![TDS540 200MHz, 1Gsps](/assets/scope_bw/tds540_200MHz_1Gsps.png)

In the image above, the samples are interpolated using a $$\sin(x)/x$$ filter.
But if you disable interpolation and only look at the dots, you get something
like this:

![TDS540 200MHz, 1Gsps, dots](/assets/scope_bw/tds540_200MHz_1Gsps_dots.png)

When the sample rate is 5 times the input frequency, there's not a lot to
work with.

However, the TDS 540 has a feature called 'equivalent time sampling' (ET)
where the signal is repeatedly sampled at random after the trigger and
fills up the signal over time. This gets you a lot of detail! And the
measured peak-to-peak voltage now make more sense to.

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

The scope has a rated bandwidth of 500MHz. Somewhere between 530 and 550MHz,
equivalent time samples suddenly breaks down.

![TDS540 550MHz, 100Gsps ET breakdown](/assets/scope_bw/tds540_550MHz_100Gsps.png)

I think that there's an issue with the trigger logic breaking down: for 
equivalent time sampling, the trigger needs to be very precise.

When plotted in a chart, you get this:

![TDS540 frequency response graph](/assets/scope_bw/tds540_freq_response.png)

# HP 54542A - 500MHz/2Gsps

This scope has been a spectacular $20 flea market purchase. I love 

![HP 54542A 500MHz/2Gsps](/assets/scope_bw/hp54542a_500MHz_2Gsps.png)

Let's so how it performs:

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

![HP 54542A frequency response graph](/assets/scope_bw/hp54542a_freq_response.png)
