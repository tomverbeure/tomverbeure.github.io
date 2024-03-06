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

* Frequency modulation - page 2.32

    * RF output signal is no longer phase-synchronized if FM is set
    EXT DC: DC to 100kHz

* 2.3.29 Modulation, external source

    "FM DC mode allows for VCO operation, externally applied analog sweeps or digital
    frequency modulation."


# References

* [SMHU Operating Manual](/assets/smhu/R&S SMHU Operating.pdf)
* [SMHU Datasheet](/assets/smhu/Rohde-Schwarz-SMHU-Datasheet.pdf)
* [SMHU Extended German Datasheet](/assets/smhu/smhu_extended_datasheet_german.pdf)

* [Double frequency range for R&S Signal Generators](/assets/smhu/freq_doubler.pdf)

* [Converting Oscillator Phase Noise to Time Jitter](https://www.analog.com/media/en/training-seminars/tutorials/MT-008.pdf)
