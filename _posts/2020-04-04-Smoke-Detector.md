---
layout: post
title: Smoke Detector Disassembly
date:  2020-04-04 00:00:00 -0700
categories:
---

*Whereby I descend into a rabbit hole...*

The smoke detector in our laundry room (hopefully soon to be hobby room!) started to beep with yesterday,
even though there was no smoke to be seen. If I'm reading the manual correctly, it's a low battery condition.

It's one of those good-for-10-years types with non-replacable batteries. We installed it 5 years ago...

Once you switch that thing off, you can't (and are not supposed to) switch it back on and you should throw
it away.

In the middle of a shelter-in-place, you have to do *something* so keep yourself busy, so why not take it
apart and see what's inside?

# Disassembly

I didn't take any *before* pictures, but there's a bunch of plastic click mechanisms to keep things in place
it's assembled. I used pliers to cut my way through things. Only later did I discover that there are also
some screws hidding behind glued on paper that make taking it apart a little bit easier.

The first thing to appear was the battery.

![Deconstruction](/assets/smoke_detector/0-deconstruction.jpg)

Inside the plastic enclosure are 3 main components:

* PCB
* Battery
* Buzzer

![Major Components](/assets/smoke_detector/1-PCB_in_case.jpg)

Once disassembled, it looks like this:

![PCB front](/assets/smoke_detector/2-PCB-front.jpg)

The back of the PCB contains what I call the smoke chamber:

![PCB back](/assets/smoke_detector/3-PCB-back.jpg)

The smoke chamber attaches to the PCB with 2 plastic clamps:

![Smoke Detection Chamber](/assets/smoke_detector/6-smoke-chamber.jpg)

The smoke chamber is surrounded by some fine mesh fabric, probably to prevent tiny mosquitos from entering?
There are narrow slits to let air in and out, and there are corners so that stray light doesn't enter
the center of the chamber:

![Smoke Detect Chamber Inside](/assets/smoke_detector/8-smoke-chamber-internal.jpg)

# Electronics

The PCB is pretty simple.

There are 2 main types of smoke detector: photoelectric and ionization based. There is no best type: 
the photoelectric ones respond faster to smoke created by smoldering fires while ionization based smoke 
detector respond faster to smoke produced by fanning flames. 

For best protection, the US Fire Administration [recommends using both types](https://www.usfa.fema.gov/about/smoke_alarms_position.html)!

In the center of my smoke detector is an integrated IR emitter and detector, so we're dealing with an
photoelectric type here:

![PCB Components](/assets/smoke_detector/4-PCB-only-front.jpg)

We're seeing:

* the black detector
* an [RE46C190](http://ww1.microchip.com/downloads/en/DeviceDoc/RE46C190-DS-20002271C-Final1.pdf) IC from Microchip
* a power switch
* a push button
* connectors for the battery and beeper
* a switched power supply

The RE46C190 is a dedicated ASIC for these kind of smoke detectors. No other active components are needed to build one.

In normal operation, it triggers the IR emitter and detector once every 10 seconds and stays in deep sleep in between to
save power. When it detects smoke, the polling rate is increased to verify that there is indeed an alarm condition.

When there are 3 consecutive alarm conditions, the the beeper is enabled.

When the sensor is active, it enables a voltage boost convertor that charges capacitor IRcap (C6 on the PCB) for 10ms.
It then drains this capacitor for a time between 100 and 400us through the infra-red LED. During that time, the current
through the IR detector is integrated, digitized, and compared against a reference value that was programmed into the
IC during calibration.

# Buzzer - Piezoelectric Transducer


* [Uses for piezo transducers from old smoke alarms](https://www.youtube.com/watch?v=5UAL4QVR17s)
* [Stackoverflow - What's the third wire on a piezo transducer](https://electronics.stackexchange.com/questions/18212/whats-the-third-wire-on-a-piezo-buzzer)
* [Ask MAKE: Three leaded piezo?](https://makezine.com/2009/12/03/ask-make-three-legged-piezo/)
* [Murata - Piezoelectric Sound Components Application Manual](https://www.murata.com/~/media/webrenewal/support/library/catalog/products/sound/p15e.ashx)
