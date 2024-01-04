---
layout: post
title: PLL Basics
date:   2023-07-18 00:00:00 -1000
categories:
---

* TOC
{:toc}


# References

* [Basic Equations of the PLLs](https://catalogimages.wiley.com/images/db/pdf/0470848669.excerpt.pdf)


* https://electronics.stackexchange.com/questions/476611/understanding-pll-vco-integrator-phase-shift

**Costas Loop**

* The Costas Loop Series - Eric Hagemann

    * [The Costas Loop – An Introduction](/assets/pll/DSP010315F1 - The Costas Loop - An Introduction.pdf)
    * [The Costas Loop - Closing the Loop](/assets/pll/DSP010419F1 - The Costas Loop – Closing the Loop.pdf)
    * [The Costas Loop – Setting the Loop](/assets/pll/DSP010531F1 - The Costas Loop - Setting the Loop.pdf)
    * [The Costas Loop - Wrapping It Up](/assets/pll/DSP010628F1 - The Costas Loop – Wrapping It Up.pdf)

    Fantastic series that breaks down the math down to the very basics.

* [RF signal processing - Practical Costas loop design](https://ez.analog.com/cfs-filesystemfile/__key/communityserver-discussions-components-files/333/Costas-Loop.pdf)

* [Costas Loop Lab](http://zimmer.fresnostate.edu/~pkinman/pdfs/Costas%20Loop.pdf)

* [Implementation of a Software Defined Spread Spectrum Communication System](https://egrove.olemiss.edu/cgi/viewcontent.cgi?article=1032&context=etd)

* [DSP related discussion](https://www.dsprelated.com/showthread/comp.dsp/112658-1.php)

* [DESIGN OF PLL-BASED CLOCK AND DATA RECOVERY CIRCUITS FOR HIGH-SPEED SERDES LINKS](https://core.ac.uk/download/pdf/29156891.pdf)

    Section 3 is a great tutorial on clock-and-data recovery (CDR) basics.

    * Hogge phase-detector

        Easy to understand. Negative: always requires skew between data-in and clock.

    * Bang-Bang or Alexander Phase Detector

        Most popular.

        Uses 3 samples to (2 rising, 1 falling edge) to detect if a data transition is present
        and if the clock is early or late.

        There is no linear phase difference: the clock is either leading or lagging.

* [PLL Performance, Simulation, and Design](https://www.ti.com.cn/cn/lit/ml/snaa106c/snaa106c.pdf)

**Filters**


* [Analog Devices - Linear Circuit Design Handbook](https://www.analog.com/en/education/education-library/linear-circuit-design-handbook.html)

    * [Analog Filters](https://www.analog.com/media/en/training-seminars/design-handbooks/basic-linear-design/chapter8.pdf)

* [Engineering Mathematics with Examples and Solutions](https://www.mathforengineers.com/)

    * [Low Pass Filter Transfer Function](https://www.mathforengineers.com/filters/low-pass-filter-transfer-function.html)

* [Electronics Tutorials - Band Stop Filter](https://www.electronics-tutorials.ws/filter/band-stop-filter.html)

