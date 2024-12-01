---
layout: post
title: BLDC Motor Basics
date:   2024-11-17 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Notes

* [Microchip AN885 - Brushless DC (BLDC) Motor Fundamentals](https://ww1.microchip.com/downloads/en/AppNotes/00885a.pdf)

BLDC motor characteristics: 
* 3 windings for 3 phases
* windings are wrapper around coils
* coils are spread around the stator periphery to form
  an even number of poles.
* either trapezoidal and sinusoidal windings.  This is a characteristic of the motor.
  Difference is determined by interconnection of coils in the stator windings
  to give a different kind of back EMF.

  * [Trapezoidal & Sinusoidal: Two BLDC Motor Controls](https://bacancysystems.com/blog/trapezoidal-and-sinusoidal-bldc-motors)
  * [TI - [FAQ] Trapezoidal Motors vs. Sinusoidal Motors](https://e2e.ti.com/support/motor-drivers-group/motor-drivers/f/motor-drivers-forum/909911/faq-trapezoidal-motors-vs-sinusoidal-motors)

    Has a nice diagram of the 2 kinds of motors.

    You can detect which kind of motor you have by connecting the windings to
    an oscilloscope and manually rotate the motor.

  Sinusoidal commutation is used in Permanent Magnet Synchronous Motors (PMSM)
  which have a sinusoidal back EMF.

  In practice, you can use both trapezoidal and sinusoidal control on BLDC and PMSM
  motors because in both cases, the back EMF looks somewhat sinusoidal.



# References

* GreatScott! - Make Your Own ESC BLDC Motor Driver 

  Fantastic tutorial about the basics of speed control.

  * [Part 1](https://www.youtube.com/watch?v=W9IHEqlGG1s)
  * [Part 2](https://www.youtube.com/watch?v=NXkLydhRvS0)

* Modelling a BLDC motor with LTSpice

  [LTspice #15: How to Create a Brushless DC Motor Model (Part I)](https://www.youtube.com/watch?v=UEygOGviE2k)

* [Shane Colton - Motor Controllers](https://scolton.blogspot.com/p/motor-controllers.html)

  Tons of good info.

* [Aaed Musa Youtube channel](https://www.youtube.com/@AaedMusa)

  Amazing motor creations.

