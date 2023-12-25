---
layout: post
title: DSLogic U3Pro16 Review and Teardown
date:   2023-03-20 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The year was 2020, and offices all over the world shut down. A house remodel had just
started, so I moved from a comfortably airconditioned corporate building to a very messy 
garage.

[![A very messy garage](/assets/dslogic/garage.jpg)](/assets/dslogic/garage.jpg)

Since I'm in the business of developing, and debugging, hardware, a few pieces of
work equipment came along for the ride, including a Saleae Logic Pro 16. There's
no way around it: they make some of the best USB logic analyzers. Plenty of competitors
have matched or surpassed their digital features, but none have the ability to record 
the 16 channels in analog format as well.

While I had the Saleae for work stuff, I may once in a while also have used
it for some hobby-related activities.

![Probing the pins of an HP 3478A multimeter](/assets/hp3478a/sram_with_probes.jpg)

But eventually corporate offices reopened, the Saleae went back to its
original habitat, and I found myself without a good 16-channel USB logic analyzer.
Buy a Saleae for myself was out of the question: even after 
the [$150 hobbyist discount](https://blog.saleae.com/saleae-discounts/), I simply
can't justify a price of $1350.

After looking around for a while, I decided to give the 
[DSLogic U3Pro16](https://www.dreamsourcelab.com/product/dslogic-series/)
from [DreamSourceLab](https://www.dreamsourcelab.com) a chance. I bought it 
[on Amazon](https://www.amazon.com/DreamSourceLab-USB-Based-Analyzer-Sampling-Interface/dp/B08C2LCBGL/ref=sr_1_3) 
for $299.

[![DSLogic with all probe wires](/assets/dslogic/dslogic_with_all_wires.jpg)](/assets/dslogic/dslogic_with_all_wires.jpg)
*(Click to enlarge)*

In this blog post, I'll look at some of the features, my experience with the software,
and I'll also open it up to discover what's inside.

# The DSLogic U3Pro16

DreamSourceLab currently sells 3 logic analyzers: 

* the $149 DSLogic Plus (16 channels)
* the $299 DSLogic U3Pro16 (16 channels)
* the $399 DSLogic U3Pro32 (32 channels)

The only functional difference between the U3Pro16 and U3Pro32 is the number of channels; 
they're otherwise identical. It's tempting to go for the 32 channel version  but I've rarely 
had the need to record more than 16 channels and if I really need it, I can always fall back 
to my HP 1670G logic analyzer, a pristine $200 flea market treasure with a whopping 136 channels.
It even has the digital storage scope option with 2 analog channels, 500MHz bandwidth and 2GSa/s
sampling rate.

[![HP 1670G](/assets/dslogic/hp1670g.jpg)](/assets/dslogic/hp1670g.jpg)

The DSLogic Plus also has 16 channels, but its acquisition memory is only 256Mbits vs 2Gbits
for the U3Pro16, and it has to make do with USB 2.0 instead of a USB 3.0 interface, a crucial 
difference when streaming acquistion data straight to the PC to avoid the limitations of the 
acquistion memory. There's also a difference in sample rate, 400MHz for the Plus, 1GHz for the 
U3Pro16, but that's not very important in practice.

# In the Box

The DSLogic comes with a nice, elongated hard case. 

[![DSLogic case](/assets/dslogic/dslogic_case.jpg)](/assets/dslogic/dslogic_case.jpg)

[![DSLogic contents](/assets/dslogic/dslogic_contents.jpg)](/assets/dslogic/dslogic_contents.jpg)

Inside, you'll find:

* the device itself, a slick aluminum case
* a USB-C to USB-A cable
* 5 4-way probe cables and 1 3-way clock and trigger cable
* 18 test clips

# Probe Cables and Clips

You read it right, my device came with 5 4-way probe cables, not 4. I don't know if DreamSourceLab added one
extra in case you lose one, or if they mistakenly included one too much, but it's definitely good 
to have a spare.

![DSLogic and 6 sets of probe, clock and trigger wires](/assets/dslogic/DSLogic_and_probe_wires.jpg)

The cables are quite stiff and are not as pliable as those
that comes with a Saleae. The case has been designed such that the probe cables can
be stored without the need to bend them. I like it.

The quality of the test clips is not great, but they are no different than those of the 5 times 
more expensive Saleae Logic 16 Pro. They're clones of the HP/Agilent logic analyzer grabbers that 
I got from eBay and will do the job, but I much prefer the ones from Tektronix.

![4 different grabbers](/assets/dslogic/grabbers.jpg)
*From left to right: Tektronix, Agilent, Saleae, and DSLogic clips*

Compared to the other ones, the Tektronix probes are narrow which makes it easier to place multiple
ones next to each other one fine-pitch pin arrays.

![Tek fine pitch grabbers](/assets/dslogic/tek_fine_pitch.jpg)

If you're thinking about upgrading your current probes: stay away from fakes. As I write this,
you can find packs of 20 probes on eBay for $40 (incl shipping), so around $2 per probe. Search
for "Tektronix SMG50" or "Tektronix 020-1386-01".

Meanwhile, you can buy a pack of 12 fake ones on Amazon for $16, or $1.3 a piece. They work, but
they aren't any better than the probes that come standard with the DSLogic:

![Fake vs original Tek grabber](/assets/dslogic/fake_vs_original_tek.jpg)
*Fake probe on the left, Tek probe on the right*

The stem of the fake ones is much thicker, and the hooks are different too. 

The Tek probe has rounded hooks:

![Tek probe with rounded hooks](/assets/dslogic/tek_rounded_hooks.jpg)

The hooks of a fake probe are flat, and don't attach as well to their target:

![Fake probe with flat hooks](/assets/dslogic/fake_flat_hooks.jpg)

If you need to probe targets with a pitch that is smaller than 1.25mm, you should check out
the [micro clips that I reviewed](/tools/2018/04/29/micro-chip-rw-clip.html)


# The Hardware


![DSLogic and probe wire plugs](/assets/dslogic/DSLogic_and_probe_wire_plugs.jpg)

![DSLogic with two cables plugged in](/assets/dslogic/DSLogic_and_two_cables_plugged_in.jpg)

![DSLogic opened up](/assets/dslogic/DSLogic_opened_up.jpg)

[![DSLogic PCB top side - not annotated](/assets/dslogic/DSLogic_PCB_top_side_not_annotated.jpg)](/assets/dslogic/DSLogic_PCB_top_side_not_annotated.jpg)
*(Click to enlarge)*

[![DSLogic PCB top side - annotated](/assets/dslogic/DSLogic_PCB_top_side_annotated.jpg)](/assets/dslogic/DSLogic_PCB_top_side_annotated.jpg)
*(Click to enlarge)*

# Input Circuit

[![DSLogic input schematic](/assets/dslogic/DSLogic_input_schematic.png)](/assets/dslogic/DSLogic_input_schematic.png)


# Software: From Saleae Logic to PulseView to DSView

When Saleae first came to market, they raised the bar for logic analyzer software with
Logic, which had a GUI that allowed scrolling and zooming in and out of waveforms at blazing 
speed. Logic also added a few protocol decoders, and an C++ API to create your own decoders.

It was the inspiration of [PulseView](https://sigrok.org/wiki/PulseView), 
an open source equivalent that acts as the front-end
application of [SigRok](https://sigrok.org/wiki/Main_Page), 
an open source library and tool that acts as the waveform acquisition
backend. 

PulseView supports protocol decoders as well, but it has an easier to use Python
API, and it allows stacked protocol decoders: a low-level decoder might convert the recorded
signals into, say, I2C transactions. A higher level I2C EPROM decoder could then decode these
I2C into read and write operations. PulseView has tons of protocol decoders, from simple
UART transactions, all the way to USB 2.0 decoders.


When the DSLogic logic analyzer hit the market after a successful Kickstarter campaign, it shipped 
with DSView, DreamSourceLab's closed source waveform viewer. However, people soon discovered that it 
was a reskinned version of PulseView. A big no-no since the latter is developed under a GPL3
license.

After a bit of drama, DreamSourceLab made [DSView available on GitHub](https://github.com/DreamSourceLab/DSView) 
under the required GPL3 as well, with attribution to sigrok project. DSView is a hard 
fork of PulseView and there are still some bad feelings because DreamSourceLab doesn't push 
changes to the PulseView project, but at least they've legally in the clear for the past 6 years.

The default choice would be to use DSView to control your DSLogic, but Sigrok/PulseView
supports DSView as well. 

In the figure below, you can see DSView in demo mode, no hardware device connected, and the example
of the 3 stacked protocol described earlier:

[![DSView Stacked Protocol Decoders](/assets/dslogic/DSView_stacked_protocols.png)](/assets/dslogic/DSView_stacked_protocols.png)
*(Click to enlarge)*

For this review, I'll be using DSView.

*Saleae has since upgrade Logic to Logic2, and now also supports stacked protocol decoders.
It still uses [a C++ API](https://support.saleae.com/saleae-api-and-sdk/protocol-analyzer-sdk) though. 
You can find an example decoder [here](https://github.com/saleae/SampleAnalyzer).*

# Installing DSView on a Linux Machine

DreamSourceLab provides Windows and MacOS binaries for DSView, but not for Linux.
When you click the Download button for Linux, it simply downloads a tar file with the
source code, which you're expected to compile yourself!

I was looking forward to running into the usual issues with package dependencies, but
after following the instructions in the [INSTALL file,](https://github.com/DreamSourceLab/DSView/blob/master/INSTALL) 
I ended up with a working executable on first try.



Components:

* FPGA: Spartan-6 XC6SLX16-FTG256DIV1945
* DRAM: DDR3-1600: Micron MT41K128M16JT-125 (D9PTK), 2Gb, 16-bit
* DDR termination voltage controller: [SGM2054](http://www.sg-micro.com/uploads/soft/20220506/1651829741.pdf)
* FPGA power regulator: [LM26480](https://www.ti.com/lit/ds/symlink/lm26480.pdf)
* 24MHz oscillator
* USB interface: CYSB3014-BZX
    * [$14 on LCSC](https://www.lcsc.com/product-detail/Microcontroller-Units-MCUs-MPUs-SOCs_Cypress-Semicon-CYUSB3014-BZXC_C462526.html)
* 19.2MHz oscillator
* USB ESD protection: SP3010-04UTG
    * marked QH4
    
* USB-C mux: TI [HD3SS3220](https://www.ti.com/lit/ds/symlink/hd3ss3220.pdf)
* Clock generator: [ADF4360-7](https://www.analog.com/media/en/technical-documentation/data-sheets/ADF4360-7.pdf)
* Flash: Macronix [MX25R2035F](https://www.macronix.com/Lists/Datasheet/Attachments/8696/MX25R2035F,%20Wide%20Range,%202Mb,%20v1.6.pdf)
* Measurement ESD protection: [SRV05-4D-TP](https://www.mccsemi.com/pdf/Products/SRV05-4D(SOT23-6L).pdf)

    Probably! Might be slightly different...

* 100k resistor to ground + ESD -> 33 Ohm series resistor (into FPGA?)

# References

*Reviews*

* [Logic Analyzer Shopping](https://www.bigmessowires.com/2021/11/21/logic-analyzer-shopping/)

    Comparison between Saleae Logic Pro 16, Innomaker LA2016, Innomaker LA5016, DSLogic Plus, and DSLogic U3Pro16

LVDS comparator

* [Can I use differential I/O pins of FPGA as high speed comparator?](https://electronics.stackexchange.com/questions/90149/can-i-use-differential-i-o-pins-of-fpga-as-high-speed-comparator)
* [Logic analyzer with Kintex-7](https://www.reddit.com/r/FPGA/comments/14wx7hg/logic_analyzer_with_kintex7/)
* [FPGA ADC design](https://sps.ewi.tudelft.nl/fpga_tdc/ADC_basic.html)
* [LVDS inputs on Cyclone II](https://www.fpgarelated.com/showthread/comp.arch.fpga/42373-1.php)

    Comments by Xilinx engineer about the design of Spartan 3 LVDS comparator

* [APP NOTE: make an analog to digital converter using FPGA pins](http://dangerousprototypes.com/blog/2019/11/03/app-note-make-an-analog-to-digital-converter-using-fpga-pins/)
* [TAKING ADVANTAGE OF LVDS INPUT BUFFERS TO IMPLEMENT SIGMA-DELTA A/D CONVERTERS IN FPGAS](http://www.ee.nmt.edu/~erives/531_14/Sigma-Delta.pdf)
* [A 7.4-Bit ENOB 600 MS/s FPGA-Based Online Calibrated Slope ADC without External Components](https://www.mdpi.com/1424-8220/22/15/5852)
* [An FPGA-based 7-ENOB 600 MSample/s ADC without any External Components](https://dl.acm.org/doi/abs/10.1145/3431920.3439287)
* [200 MS/s ADC implemented in a FPGA employing TDCs](https://sps.ewi.tudelft.nl/pubs/Homulle15fpga.pdf)

