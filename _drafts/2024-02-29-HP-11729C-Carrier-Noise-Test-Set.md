---
layout: post
title: HP 11729C Carrier Noise Test Set
date:   2024-02-29 00:00:00 -1000
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

I've always wanted to eventually learn enough about RF to do something useful with it,
but I'm just not there yet. But that hasn't stopped me from checking out Craiglist
on a daily basis to see if there's anything interesting for sale, and build
up a small stable of RF related test equipment.

A couple of weeks ago, I stumbled onto an ad for an HP 11729C Carrier Noise Test Set,
5 MHz to 18GHz. I had no idea what it was, and thus I definitely didn't have one yet.

It turns out that it's a companion machine to measure 
[*phase noise*](https://en.wikipedia.org/wiki/Phase_noise).

At that point, all I really knew about phase noise that it has something to do with the
stability of a signal or the output of an oscillator, and that it's pretty hard to measure.
For me, the most intuitive elevator-pitch explanation of phase noise is that's the equivalent 
of jitter but expressed in the frequency domain.

One of the most fun parts of a hobby is that you don't need a well-defined goal. Sometimes
you just pick up a scent and follow it and see where it leads you. That's exactly what happened
here: I have no need to measure phase noise, but it turns out to be interesting enough on its own.

In this blog post try to get setup going that allows me to measure the phase noise of some of my
signal generators.

# A Very Quick Introduction to Phase Noise

There's a ton of information available about phase noise, and it would be redundant to go
into detail here, so I'll just go through the very basic to make clear why a device like the
HP 11729C is useful.

A perfect RF signal generator or oscillator will generate a pure sine wave with an exact frequency $$f$$:

$$
s(t) = \sin(2 \pi ft)
$$

In the frequency domain, the spectrum of signal like this will show a single peak:

XXXX

In the real world, noise will add an additional term to the equation which will make the sine wave not quite
perfect:

$$
s(t) = \sin(2 \pi ft + \phi(t))
$$

In the time domain, this introduces jitter in the edges of the output signal. In the frequency domain, this
causes the single frequency peak to be smeared over neighboring frequencies:

XXXX

The farther you go from the center frequency, the lower the phase noise. When you're dealing with good quality signal 
generators, the phase noise drops very quickly. So quickly, in fact, that most spectrum analyzers aren't
able to measure the phase noise correctly: they are trying to measure the main carrier signal, the center frequency,
and the noise at the same time, and their dynamic range is just not large enough to do so.

If only there were ways to get rid of the center carrier signal while keeping the remaining phase noise?
It turns out that there are multiple techniques to do that. The HP 11729C provides the tools for two
such techniques.

# Inside the HP 11729C



# References

* [HP 11729C - Operating and Service Manual](/assets/hp11729c/HP-11729C_Operating_and_Service_Manual.pdf)
* [HP 11729B - Carrier Noise Test Set - Convenient phase and amplitude noise measurements on high quality sources](/assets/hp11729c/HP11729B - Carrier Noise Test Set - Convenient phase and amplitude noise measurements on high quality sources.pdf)
* [HP Product Note 11729C-2 - Phase Noise Characterizaton of Microwave Oscillators](/assets/hp11729c/PN11729C-2 - Phase Noise Characterization of Microwave Oscillators.pdf)
