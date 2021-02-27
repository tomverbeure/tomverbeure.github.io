---
layout: post
title: Things I learned about NumPy, FFTs, and Spectral Analysis
date:  2021-02-23 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

# Use 'endpoint=False' when using np.linspace to create a sine wave

When I want to create a test signal to experiment with some DSP function, this is used to
be my standard way of doing it:


```python
    N=10000

    x = np.linspace(0., 1., N)

    freq1 = 100
    freq2 = 1000
    freq3 = 3000

    y1 = 1.0 * np.sin(2 * np.pi * freq1 * x)
    y2 = 1.0 * np.sin(2 * np.pi * freq2 * x)
    y3 = 1.0 * np.sin(2 * np.pi * freq3 * x)

    y = y1 + y2 + y3
```

`x = np.linspace(0., 1., N)` creates linearly incrementing X-axis from 0 to 1, divided into
N equal sized steps.

There are 3 sine waves, with different frequencies. With x going from 0 to 1, all 3 sine waves
have an integer number of periods.

Inevitabley, sometime later in the process, something like this happens:

```python
    w = np.blackman(len(y)); corr = len(w)/sum(w)
    Y = corr * np.fft.fft(y * w) / (N/2)
```

If we graph that FFT as a frequency magnitude plot, you get this:

![linspace endpoint=True, window](./assets/things_i_learned/linspace_endpoint_window.svg)

Looks good! The frequency spikes are narrow and where they are supposed to be. Well, they
are arrow up to around -80dB. That's because we're using a Blackmann window to prevent
spectral leakage.

Without applying a window, the result would have been much worse. Like this:

![linspace endpoint=True, no window](./assets/things_i_learned/linspace_endpoint_no_window.svg)

But wait a minute... Didn't we create the sine waves so that they'd have an integer number
of periods in 1 second time interval over which we're calculating the FFT? If so, why
is there spectral leakage at all?

The reason because of `endpoint`, parameter of the `linspace` function that has a default
value of `True`. When `True`, `linspace` returns values that go from `start` to `stop` 
**with `stop` included**.

