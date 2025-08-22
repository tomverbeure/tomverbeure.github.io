---
layout: post
title: HP 10811 Colpitts Oscillator
date:   2025-08-21 00:00:00 -1000
categories:
---

* TOC
{:toc}

# HP 10811

* [Schematic](http://www.leapsecond.com/museum/10811a/10811a.pdf) - page 70
* [Explanation](https://hparchive.com/Manuals/HP-10811AB-Manual.pdf) - page 50
* [Falstad Colpitts](https://www.falstad.com/circuit/e-colpitts.html)

# L-double-C circuit 180 degrees

[Falstad circuit](http://www.falstad.com/circuit/circuitjs.html?ctz=CQAgjCAMB0l3BWcBOaAOAbAdgCwCYsBmHMBMHZNQkEkJHahAUwFowwAoAY3BxxDx5+5fsgw0oseOWSy58hSDbQwGHGkhgNpSFmz4okzgBsQGkGLOQQhBHkMQWMOHmJkMYPBmRZIFDITUkNy8-Lb2IgJCEs7SFAoJckpgKmra2giQyOoI4tbBAO5WFuKRloXF4aE2dlAcAOaVteaEGGiGwQBKSuolyZ591hBgcHQdkggcRZGC-HiQ7bN1APICC1FzuRsdUzSWVbnWVV02bX2B4uXg4KNI+RMNdHiL0XaLOPcVDPZV-jX2X0I9ksf3KIT+v0sS34sTgMkSiUkWAQHwQmUCDCwPiwEHyHFM3z6hOO1ycUjQ5FUkAQYjQgmIyDqPD+0MsIMk8E08QRihSzx8yBGJFanjadyMHFWh3+IAw6xJFTe2xZ0WCAGdTu0QUDBtcAGYAQ2MaqYHA12GB4iw811EENxtNRUwc2ieheMMlFmefR8lzyTJAbu2QfZsK5PISSgQ0GQkEIWkyaBIBBwGHFMBMgbOlmdto5fiEaGQeFIJbasnmeRCuaWudDUjh3IjsiUeHQ2VaulchCTpHaeMaQaWQ4+Oydah93rBRWt1ksIarGta7Q+1kJq-G9pNZp6WtKfocIC3jvAB-M0-AnmseC27DON6rjTv7TIEVUL+9eJ4z7oAx-Pf4GEG3DZskjYTQY1pONPCwNAECxLAdlMH8H0vM5IiGcBoAuDxi0FaksgQHsA3-JM0MWLYgM5eFQMZcCUlkNpoIIHFvBhCVVlI4QyxsMi8Q1EZrQEW8r2E-07SNbduh-SIfyuNdrHTB5pK7MSbmiVD7lHJSYEmAAPG5MEDCIhH4ZEJGiABhAB7ABbWzrIAOwAHTVAAhA1twM8hsBoCIMDTGh6AEfgbPspzXJs4xjCYLgABdrIAJw4aS+CGYtwEIDKwAyrTFPGXSUvAa12ipYrvXYAFDG0groEmAS0pQCJ1FK3L9Uk01OL0I4bS0eUbS-U9VBoHVVGGoE13zRtaJbNgsGgLBYJIBAKRLMg9CCCVkKI8RCVIVobAG64M2IHzBWQIEGWpRDgm-DxxAmobSgyqi4hmuiwHmxbexWwRcjwZB00efbdtGnaaF6PFphaprwHBnKAQ4OLT3MBHytaqrcQcUYABMmENABXYw4t2T7vWeUqSrWftSbSWH33SxHpnuw6hm61m6mmcHHpB2GKl5tGxuepmnpGiJwcJYIDKIfgWFoQVZeIuZQrshyXLVABRWyAEs4riphku6C0+gwaJ5JofLPjqjhrNlWUwnAVxIHsNsKGpIjU2tShMABBssaQeMbBsLHA+oGnbZGe2g88QhnYEWBFoIIjcAC3wRjuP3rmETawGoahPrqW2bQnfOnfsDBYDED2UVNgVUzyTP7DmfsBHaahBELw6o6GMu6ECaAKHUMQ2meZcpogPOu7zm6bd-bvHYB6w5QWwI-AutRNAIftM4dsgg9TOpiOsAAxLGw00ceL7YEBLINAAHA0uF1g1HK4U1iIgU+OlgYYf+SEAACSjkcYE3ii-N+HAgA)

# Basic Colpitts - Falstad

`basic_colpitts_falstad.asc`

* Common emitter

* R3 and R4 are measurement resistors.
* Startup: It's important to have "Start external DC supply voltages at 0V" enabled, that
  way C1 and C2 are empty and there is no magnetic field in L1. If this is not enabled,
  then LTspice will first caluculate the DC steady state values and set those for C1, C2 and L1.
  The transient startup behavior will be very different.
* Initially, there is no voltage on Vb and the transistor is not conducting. The initial current
  through R2 is 4.5mA: 5V/(100+1000).
* The current through R2 immediately starts to drop because C1 starts charging. There's a slight
  oscillation already in the LC tank.
* Once Vb exceeds ~0.75V, the transistor starts conducting. When that happens, the current
  through R2 is close to 0. When the transistor conducts, its resistance is very low. Because of that, 
  Vc drops to near 0V. The current through R1 is now 5V/100=~50mA plus Ibc, which is ~6mA for a
  total of 56mA.
* We have oscillation now: when the voltage on the L1/C2 junction is low, the transistor is off
  and current flows into the tank through R2. 

Observations:

* With an R2 values of 1k, the initial current is 4.5mA and peaks at 3.7mA in steady state.
  The current through R4 peaks at 6.2mA, which is coming from the tank, but it's shorter, so 
  I assume there's sufficient addition of energy to keep the oscillation going.
* If you make L1 non-ideal and give it a series resistance of 1 Ohm, the oscillation still
  keeps going. The peak R2 current is now 2.8mA and the peak R4 current is 2.4mA.
* If you then increase R2 to 10k, the oscillation stops. Reducing R2 back to 1k (or 2k) 
  make the oscillation work again.
* The 2 capacitors form a voltage divider, but the center is strapped to ground? 
  Yes, but if you check the voltages on the capacitors on either side of the coil, you can 
  see that they behave in opposite phase and that the amplitudes are inverse proportional
  to the capacitors. There's also a common DC value, but that doesn't matter in the small
  signal model. When the 2 caps are equal and you add the 2 signals, you see that they
  *almost* cancel out, though not perfectly.

What's the math to determine whether oscillation will happen or not?

* Vb is a ~sine wave, but Vc is not.
* Delta between main frequency an second harmonic is 23dB.

# Basic Colpitts - 38: LC tank circuits and the Colpitts oscillator

* [#38: LC tank circuits and the Colpitts oscillator](https://youtu.be/78qzLAvGHl0?t=712)

`basic_colpitts_38_lc_tank_circuits_and_colpitts_oscillator.asc`

* Common emitter

* Very similar, but the feedback is a capacitor instead of a resistor.
* There is a 1M resistor from Vdd to the base of Q1. Without this resistor, the
  oscillation starts but then peters out! Why is that?
  I think it's there to bias the transistor, but in most standard circuits, there
  are 2 bias transistors and an input DC blocking capacitor. Here, it's only a single
  resistor.
  Capacitor C3 is a DC blocking capacitor, but its capacitance is very low. If we increase
  its value just by a factor of 10 to 0.01uF then it takes ages before the oscillation
  peters out, but it still does. 
  In general, it's probably better to always use an amplifier that is correctly biased.

# Basic Colpitts - Colpitts Oscillator Circuit Analysis (7 - Oscillators)

* [Colpitts Oscillator Circuit Analysis (7 - Oscillators)](https://www.youtube.com/watch?v=ES-kcNR4Ln0)
* [Demonstration and Discussion of Colpitts Oscillator (8 - Oscillators)](https://www.youtube.com/watch?v=wC_uKxu_3AA)

* Common emitter
* Uses standard biasing with DC blocking input cap and 2 resistors.
* Also uses collector and emitter resistors (and emitter capacitor) to regular the gain
  of the amplifier.
* Full mathematical analysis
* Builds a circuit

* Basic Colpitts - Colpits and Hartley Oscillators - Solid-state Devices and Analog Circuits - Day 6, Part 7

* [Colpits and Hartley Oscillators - Solid-state Devices and Analog Circuits - Day 6, Part 7](https://www.youtube.com/watch?v=bb5MMgNZ-OU)

* Common emitter
* Interesting because it talks about phase shift in an intuitive way.


# References

* [#96: Analysis & Design of a Typical Colpitts Oscillator](https://www.youtube.com/watch?v=TSKq5l7uuz4)

  * Excellent, fully worked out example.
  * Uses a common collector/emitter follower circuit.
  * One side of the coil is strapped to ground.

* [#38: LC tank circuits and the Colpitts oscillator](https://youtu.be/78qzLAvGHl0?t=712)

  Colpitts example with common emitter (without emitter resistor) and middle point between caps also strapped to ground.


