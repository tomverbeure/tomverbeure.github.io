---
layout: post
title: Rohde & Schwarz SMHU
date:   2023-07-09 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Various 


*  AF = Audio Frequency

    * An internally generated signal that can be used to test FM/AM/PM.
    * Max 10kHz

* Phase Modulation

    * Modulates the phase of the internal or external AF signal
    * 0 rad -> signal is more or less stable (why not totally stable?)

* AM/FM/PM can be active at the same time

    * Select parameter for mode first, then press OFF to individually disable
    
* Tune the phase of the output signal wrt reference signal

    The output frequency doesn't need to be the same as the reference signal.

    * Set special function 23: Phase offset 

        SHIFT-SPECIAL 23 Enter

    * Select phase offset mode

        PM - INT/ON

    * Set phase offset between -180 and 180

    When using a shared reference clock, this can be used to tune the output
    of two function generators to tune their output signals to be in quadrature.

* External reference clock

    RF/CF - EXT AC


# References


* [Converting Oscillator Phase Noise to Time Jitter](https://www.analog.com/media/en/training-seminars/tutorials/MT-008.pdf)
