---
title: Repair of an SRS DG535 Digital Delay Generator
date: 2025-12-08 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

I got my hands on a [Stanford Research Systems DG535](https://www.thinksrs.com/products/dg535.html)
at the [Silicon Valley Electronics Flea Market](https://www.thinksrs.com/products/dg535.html), $40
for a device that was marked "broken". That's a really good deal: SRS projects are pricey and even 
the cheapest Parts-Only listings on eBay are marked $750 and up. Worst case, I'd get a few weekends
of unsuccessful repair entertainment out of it, but even then I'd probably able to recoup my money
by selling some piece for parts.[^parts] Just the keyboard PCB is currently se

[^parts]: Not that I've ever done that, but it's what I tell my wife.

The unit ended up on a shelf in the garage for about 18 months, but last week I finally got around
to giving it the attention it deserves.

# The Standford Research Systems DG535

Imagine a tool that generates a bunch of output pulses after being triggered by an internal or 
external event, where the delay between the event and each pulse is programmable, and you have
a pretty good idea about what a DG535 can do for you. What makes the DG535 interesting is that 
these delays can be specified with a 5 ps precision, though the jitter on the outputs far
exceed that number.

The DG535 has 9 output on the front panel:

* T0 marks the beginning of an event. It's created by the internal or external trigger.
* 4 channels A, B, C and D can independently be programmed to change a random time after T0
  or after some of the other channels.
* Output AB and CD and inverted AB and CD are a XNOR or XOR of signals A and B, and signals C
  and D resp.

All outputs can be configured to a number of logic standard: TTL, ECL, NIM[^NIM], or fully programmable
voltage amplitude and offset.

[^NIM]: NIM stands for Nuclear Instrumentation Model. It's a voltage and current standard for fast
        digital pulses for physics and nuclear experiments.

The DG535 is still for sale on the SRS website for $4495, which is remarkable for an instrument that
dates from the mid 1980s. I assume that today's buyers are primarily those who need an exact replacement
for an existing, certified setup, because the [DG645](https://www.thinksrs.com/products/dg645.html), 
SRS' more modern successor to the DG535 with better feature and specs, costs only $500 more.


# References


