---
layout: post
title: Empty
date:   2024-12-02 00:00:00 -1000
categories:
---

* TOC
{:toc}

# HP 10811

* [Schematic](http://www.leapsecond.com/museum/10811a/10811a.pdf) - page 70
* [Explanation](https://hparchive.com/Manuals/HP-10811AB-Manual.pdf) - page 50
* [Falstad Colpitts](https://www.falstad.com/circuit/e-colpitts.html)

# Basic Colpitts

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

What's the math to determine whether oscillation will happen or not?

* Vb is a ~sine wave, but Vc is not.
* Delta between main frequency an second harmonic is 23dB.

# References
