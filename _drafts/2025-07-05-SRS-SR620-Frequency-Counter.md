---
layout: post
title: Repair of a Stanford Research Systems SR620 Frequency Counter
date:   2025-07-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

A little over a year ago, I was found 
[an SRS SR620 frequency counter](https://tomverbeure.github.io/2024/07/14/Symmetricom-S200-NTP-Server-Setup.html#introduction)
at the Silicon Valley Electronics Flea Market. It had a big sticker "Passed Self-Test" 
and "Tested 3//9/24" (the day before the flea market) on it so I took the gamble and spent
an ungodly $400 on it.

[![Flea Market Haul](/assets/s200/fleamarket_haul.jpg)](/assets/s200/fleamarket_haul.jpg)

Luckily, it *did* work fine, initially at least, but I soon discovered that it sometimes
got into some weird behavior after pressing the power-on switch. 

# The SR620

The SR620 was designed sometime in the mid-1980s. Mine has a rev C PCB with a date of July 1988,
37 year old! The manual lists 1989, 2006, 2019 and 2025 revisions. I don't know if there were any
major changes along the way, but I doubt it. It's still for sale on the SRS website.

The specifications are still pretty decent, especially for a hobbyist: 

* 25ps time resolution
* 1.3GHz frequency range
* 11-digit resolution over a 1 s measurement interval


# Repairing the SR620

You can see the power-on behavior in the video below:

<iframe width="680" height="480" src="https://www.youtube.com/embed/pgqye6YGhBY?si=J_VlCNSirvTlY0vj" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>

Of note is that lightly touching the power button changes the behavior and sometimes makes it get
all the way through the power-on sequence. This made me hopeful that the switch itself was bad,
something that should be easy to fix.

Unlike my broken SRS DG535, another flea market buy, which has the most cursed assembly, the SR620
has a trivial construction: after removing the 4 side screws, you can remove the top of the case and
have access to all the components.


# References

* [The Signal Path - TNP #41 - Stanford Research SR620 Universal Time Interval Counter Teardown, Repair & Experiments](https://www.youtube.com/watch?v=sDecJDgStcI)
* [Some calibration info about the SR620](https://www.prc68.com/I/TandFTE.shtml#SR620)
* [Fast High Precision Set-up of SR 620 Counter](https://www.prc68.com/I/FTS4060.shtml#SR620Fast)

  The rest of this page has a bunch of other interesting SR620 related comments.

**Time-Nuts topics**

* [SR620 calibration](https://www.febo.com/pipermail/time-nuts/2011-February/054929.html)

  Discusses last digital of SR620 being off. Detailed procedure is listed 
  [here](https://febo.com/pipermail/time-nuts_lists.febo.com/2011-February/037194.html).

* [Anyone familiar with SR-620 repair?](https://febo.com/pipermail/time-nuts_lists.febo.com/2012-March/047729.html)
* [Convert Stanford Research SR620 time-interval counter to SR625 ???](https://febo.com/pipermail/time-nuts_lists.febo.com/2014-November/071361.html)
* [time interval measurement on SR620](https://febo.com/pipermail/time-nuts_lists.febo.com/2022-March/105214.html)
* [SR620 binary dump](https://www.febo.com/pipermail/time-nuts/2014-March/083445.html)
* [SRS SR620 External Source Issue -- Help Request](https://www.febo.com/pipermail/time-nuts/2007-February/024397.html)

  Discussion about measured frequency not being exactly 10 MHz when ref is fed into input.

  This [reply](https://www.febo.com/pipermail/time-nuts/2007-February/024413.html) mentions the use of 2
  synchronzing ECL FFs that will still introduce some mismatch.

  [Potential solution](https://www.febo.com/pipermail/time-nuts/2007-February/024458.html) to fix the 
  average input issue. [This post](https://www.febo.com/pipermail/time-nuts/2007-February/024431.html) also
  talks about that.

* [Considerations When Using The SR620](https://www.febo.com/pipermail/time-nuts/2012-December/072294.html)

  [This post](https://www.febo.com/pipermail/time-nuts/2012-December/072305.html) talks about some thermal
  design mistakes in the SR620. E.g. the linear regulators and heat sink are placed right next to the
  the TCXO. It also talks about the location of the thermistor inside the fan path, resulting in unstable
  behavior. This is something Shrirar of The Signal Path fixed by moving the thermistor.

  [This comment](https://www.febo.com/pipermail/time-nuts/2012-December/072302.html) mentions that while the
  TXCO stays powered on in standby, the DAC that sets the control voltage does not, which results in an additional
  settling time after powering up. General recommendation is to use an external 10 MHz clock reference.

  [This comments](https://www.febo.com/pipermail/time-nuts/2012-December/072369.html) talks about warm-up
  time needed depending on the desired accuracy. It also has some graphs.

* [buying a time interval counter](https://www.febo.com/pipermail/time-nuts/2016-June/098747.html)

  [Some comments](https://www.febo.com/pipermail/time-nuts/2016-June/098757.html) with links about
  how to make 1E12 measurements in a second that are linked earlier.

* [SR620 - any gotchas buying a used one?](https://febo.com/pipermail/time-nuts/2014-November/088659.html)

* [ocxo](https://febo.com/pipermail/time-nuts/2014-November/088661.html)

   Discusses OCXOs related to SR620

* [Help me make some sense of adev measurements of SR620's own clock](https://febo.com/pipermail/time-nuts/2015-January/090649.html)

* [Can one update firmware of Stanford Research Systems SR620 time interval counter?](https://febo.com/pipermail/time-nuts/2015-January/090276.html)

  Version 1.48 is the latest version.

* [Replacement fan in SR620](https://www.febo.com/pipermail/time-nuts/2014-February/082536.html)

  [This post](https://www.febo.com/pipermail/time-nuts/2014-February/082542.html) discusses moving
  the thermistor. While it improves startup behavior, it doesn't change the fact that the fan almost
  always runs at full speed, so it's largely cosmetic.

  General conclusion: there's not much to be done: not enough gaps for airflow. Heatsinks outside
  the case where the linear power regulators are might help a bit.

* [What is maximum digits that can SR620 display?](https://febo.com/pipermail/time-nuts_lists.febo.com/2015-July/075399.html)

* [Timelab, two SR620s and losing samples](https://febo.com/pipermail/time-nuts/2016-January/095462.html)

* [Stanford Research SR620 Measurement Bias](https://febo.com/pipermail/time-nuts_lists.febo.com/2009-October/023459.html)

  Continuation of some other thread where they discuss the bias.

* [SR620 TCXO calibration](https://www.febo.com/pipermail/time-nuts/2017-June/105976.html)

* [SR620 Failure Code.](https://febo.com/pipermail/time-nuts/2016-December/102786.html)

  Info about common test error 34.

* [SR620/PM66xx/CNT-90 input stages](https://www.febo.com/pipermail/time-nuts/2017-June/106000.html)

* [Frequency Counter Choice](https://febo.com/pipermail/time-nuts_lists.febo.com/2020-October/101833.html)

  [Compares different HP counters](https://febo.com/pipermail/time-nuts_lists.febo.com/2020-October/101837.html)

  [Mentions the SR620 as metrology workhorse](https://febo.com/pipermail/time-nuts_lists.febo.com/2020-October/101848.html)
  
* [SR620 fails in Self Calibration routine 07](https://febo.com/pipermail/time-nuts/2008-October/033674.html)

  Talks about the time to amplitude converter and what kind of capacitor is used.

* [Looking for good SR620 setup to compare GPS and rubidium](https://febo.com/pipermail/time-nuts_lists.febo.com/2006-September/004297.html)

  How to use the SR620 to measure the quality of output of a Rb oscillator.
  Main suggestion is to do 500 1PPS acquisitions and display MEAN and JITTER.

  Also talks about a [PTS50 distribution amplifier](https://www.ptsyst.com/PTS50-B.pdf)  
  that has a built-in clock divider to generate a 1PPS out of it.

*  [SRS SR620 counter problem](https://febo.com/pipermail/time-nuts_lists.febo.com/2010-October/033712.html)

  Test error 3: battery problem?

* [High-end GPSDO's](https://febo.com/pipermail/time-nuts_lists.febo.com/2018-August/093602.html)

  Mentions that the interpolator of an SR620 is better than one of the FS740.

* [ADEV from phase or frequency measurement](https://febo.com/pipermail/time-nuts_lists.febo.com/2014-March/065653.html)

  Uses an SR620 to measure ADEV through phase and frequency.

* [mixers for frequency measurement](https://www.febo.com/pipermail/time-nuts/2012-January/062873.html)

  Mentions SR620 high resolution mode





**Miscellaneous**

* [A Physical Sine-to-Square Converter Noise Model](https://people.mpi-inf.mpg.de/~adogan/pubs/IFCS2018_comparator_noise.pdf)

  How to convert a sine wave clock reference to a digital signal.

* [[time-nuts] Favorite counters (current production)?](https://febo.com/pipermail/time-nuts_lists.febo.com/2017-November/089966.html)

  Review of FS740 schematic.

* [Architecture, Design Aspects, and Performance of a New Cesium Beam Frequency Standard](http://leapsecond.com/corby/5071comb.pdf)

* [A NARROW BAND HIGH-RESOLUTION SYNTHESIZER USING A DIRECT DIGITAL SYNTHESIZER FOLLOWED BY REPEATED DIVIDING AND MIXING](http://www.karlquist.com/FCS95.pdf)


