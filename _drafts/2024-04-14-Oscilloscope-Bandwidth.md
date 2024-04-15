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

# TDS 540 500MHz/2Gsps

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

![TDS540 Frequency Response Graph](/assets/scope_bw/tds540_freq_response.png)



