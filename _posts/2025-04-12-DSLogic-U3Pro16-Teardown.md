---
layout: post
title: DSLogic U3Pro16 Review and Teardown
ate:   2025-04-12 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The year was 2020 and offices all over the world shut down. A house remodel had just
started, so my office moved from a comfortably airconditioned corporate building to a very messy 
garage.

[![A very messy garage](/assets/dslogic/garage.jpg)](/assets/dslogic/garage.jpg)

Since I'm in the business of developing and debugging hardware, a few pieces of
equipment came along for the ride, including a Saleae Logic Pro 16. I had the
unit for work stuff and may once in a while have used it for some hobby-related activities 
too.

![Probing the pins of an HP 3478A multimeter](/assets/hp3478a/sram_with_probes.jpg)

There's no way around it: Saleae makes some of the best USB logic analyzers around. Plenty of competitors 
have matched or surpassed their digital features, but none have the ability to record the 16 channels 
in analog format as well.

After corporate offices reopened, the Saleae went back to its original habitat and I found myself 
without a good 16-channel USB logic analyzer.  Buying a Saleae for myself was out of the question: even after 
the [$150 hobbyist discount](https://blog.saleae.com/saleae-discounts/), I can't justify the $1350
price tag. After looking around for a bit, I decided to give the 
[DSLogic U3Pro16](https://www.dreamsourcelab.com/product/dslogic-series/)
from [DreamSourceLab](https://www.dreamsourcelab.com) a chance. I bought it 
[on Amazon](https://www.amazon.com/DreamSourceLab-USB-Based-Analyzer-Sampling-Interface/dp/B08C2LCBGL/ref=sr_1_3) 
for $299.

[![DSLogic with all probe wires](/assets/dslogic/dslogic_with_all_wires.jpg)](/assets/dslogic/dslogic_with_all_wires.jpg)
*(Click to enlarge)*

In this blog post, I'll look at some of the features, my experience with the software,
and I'll also open it up to discover what's inside.

# The DSLogic U3Pro16

The [DSLogic series](https://www.dreamsourcelab.com/product/dslogic-series/) currently consists 
of 3 logic analyzers: 

* the $149 DSLogic Plus (16 channels)
* the $299 DSLogic U3Pro16 (16 channels)
* the $399 DSLogic U3Pro32 (32 channels)

The DSLogic Plus and U3Pro16 both have 16 channels, but acquisition memory of the Plus is only 
256Mbits vs 2Gbits for the U3Pro16, and it has to make do with USB 2.0 instead of a USB 3.0 interface, 
a crucial difference when streaming acquisition data straight to the PC to avoid the limitations 
of the acquisition memory. There's also a difference in sample rate, 400MHz vs 1GHz, but that's not 
important in practice.

The only functional difference between the U3Pro16 and U3Pro32 is the number of channels. 
It's tempting to go for the 32 channel version  but I've rarely had the need to record more than 
16 channels at the same time and if I do, I can always fall back to my HP 1670G logic analyzer, 
a pristine $200 flea market treasure with a whopping 136 channels[^1].

[^1]:It even has the digital storage scope option with 2 analog channels, 500MHz bandwidth and 2GSa/s
     sampling rate.

[![HP 1670G](/assets/dslogic/hp1670g.jpg)](/assets/dslogic/hp1670g.jpg)

So the U3Pro16 it is!

# In the Box

The DSLogic U3Pro16 comes with a nice, elongated hard case. 

[![DSLogic case](/assets/dslogic/dslogic_case.jpg)](/assets/dslogic/dslogic_case.jpg)

[![DSLogic contents](/assets/dslogic/dslogic_contents.jpg)](/assets/dslogic/dslogic_contents.jpg)

Inside, you'll find:

* the device itself. It has a slick aluminum enclosure
* a USB-C to USB-A cable
* 5 4-way probe cables and 1 3-way clock and trigger cable
* 18 test clips

# Probe Cables and Clips

You read it right, my unit came with 5 4-way probe cables, not 4. I don't know if DreamSourceLab added one
extra in case you lose one or if they mistakenly included one too much, but it's good to have a spare.

![DSLogic and 6 sets of probe, clock and trigger wires](/assets/dslogic/DSLogic_and_probe_wires.jpg)

The cables are slightly stiffer than those that come with a Saleae but not to the point that it
adds a meaningful additional strain to the probe point. They're stiffer because each of the 16 probe wires
carries both signal and ground, probably a thin coaxial cable, which lowers the inductance of the 
probe and reduces ringing when measuring a signal with fast rise and fall times. In terms of quality,
the probe cables are a step up from the Saleae ones.

The case is long enough so that the probe cables can be stored without bending them. 

The quality of the test clips is not great, but they are no different than those of the 5 times 
more expensive Saleae Logic 16 Pro. Both are clones of the HP/Agilent logic analyzer grabbers that 
I got from eBay and they will do the job, but I much prefer the ones from Tektronix.

The picture below shows 4 different grabbers. From left to right: Tektronix, Agilent, Saleae and DSLogic ones.

![4 different grabbers](/assets/dslogic/grabbers.jpg)

Compared to the 3 others, the stem of the Tektronix probe is narrow which makes it easier to place multiple
ones next to each other on fine-pitch pin arrays.

![Tek fine pitch grabbers](/assets/dslogic/tek_fine_pitch.jpg)

If you're thinking about upgrading your current probes to Tektronix ones: stay away from fakes. As I write this,
you can find packs of 20 probes on eBay for $40, so around $2 per probe. Search
for "Tektronix SMG50" or "Tektronix 020-1386-01".

Meanwhile, you can buy a pack of 12 fake ones on Amazon for $16, or $1.3 a piece. They work, but
they aren't any better than the probes that come standard with the DSLogic.

![Fake vs original Tek grabber](/assets/dslogic/fake_vs_original_tek.jpg)
*Fake probe on the left, Tek probe on the right*

The stem of the fake one is much thicker and the hooks are different too. The Tek probe has rounded 
hooks with a sharp angle at the tip:

![Tek probe with rounded hooks](/assets/dslogic/tek_rounded_hooks.jpg)
*Tektronix hooks*

The hooks of a fake probe are flat and don't attach nearly as well to their target:

![Fake probe with flat hooks](/assets/dslogic/fake_flat_hooks.jpg)
*Fake hooks*

If you need to probe targets with a pitch that is smaller than 1.25mm, you should check out
these [micro clips that I reviewed](/tools/2018/04/29/micro-chip-rw-clip.html) ages ago.


# The Controller Hardware

Each cable supports 4 probes and plugs into the main unit with 8 0.05" pins in 4x2 configuration, 
4 pins for the signals and 4 pins for ground. The cable itself has a tiny PCB sticking out that slots 
into a gap of the aluminum enclosure. This way it's not possible to plug in the cable incorrectly... 
unlike the Saleae. It's great.

![DSLogic and probe wire plugs](/assets/dslogic/DSLogic_and_probe_wire_plugs.jpg)

![DSLogic with two cables plugged in](/assets/dslogic/DSLogic_and_two_cables_plugged_in.jpg)

When we open up the device, we can see an Infineon (formerly Cypress)
[CYUSB3014-BZX EZ-USB FX3 SuperSpeed controller](https://www.digikey.com/en/products/detail/infineon-technologies/CYUSB3014-BZXI/2827561). 
A Saleae Logic Pro uses the same device. 

![DSLogic opened up](/assets/dslogic/DSLogic_opened_up.jpg)

These are your to-go-to USB interface chips when you need a microcontroller in addition
to the core USB3 functionality. They're relatively cheap too, you can get them
for [$16 in single digital quantities at LCSC.com](https://www.lcsc.com/product-detail/span-style-background-color-ff0-USB-span-ICs_Cypress-Semicon-CYUSB3014-BZXI_C57294.html).

![CYUSB3014 block diagram](/assets/dslogic/CYUSB3014.png)

The other side of the PCB is much busier.

[![DSLogic PCB top side - not annotated](/assets/dslogic/DSLogic_PCB_top_side_not_annotated.jpg)](/assets/dslogic/DSLogic_PCB_top_side_not_annotated.jpg)
*(Click to enlarge)*

The big ticket components are:

* a [Spartan-6](https://www.xilinx.com/products/silicon-devices/fpga/spartan-6.html) XC6SLX16 FPGA

    Responsible for data acquisition, triggering, run-length encoding/compression,
    data storage to DRAM, and sending data to the CYUSB3014.

    A Saleae Logic 16 Pro has a smaller Spartan-6 LX9. That makes sense: its triggering options
    aren't as advanced as the DSLogic and since it lacks external DDR memory, it doesn't need a
    memory controller on the FPGA either.

* a DDR3-1600 DRAM

    It's a [Micron MT41K128M16JT-125](https://www.micron.com/products/memory/dram-components/ddr3-sdram/part-catalog/part-detail/mt41k128m16jt-125-it-k),
    marked D9PTK, with 2Gbits of storage and a 16-bit data bus.

* an Analog Devices [ADF4360-7](https://www.analog.com/media/en/technical-documentation/data-sheets/ADF4360-7.pdf) clock generator

    I found this a bit surprising. A Spartan-6 LX16 FPGA has 2 clock management tiles (CMT) that each have 1 real PLL and
    2 DCMs (digital clock manager) with delay locked loop, digital frequency synthesizer, etc. The VCO of the PLL can be configured 
    with a frequency up to 1080 MHz which should be sufficient to capture signals at 1GHz, but clearly there was a
    need for something better.

    The ADF4360-7 can generate an output clock as fast a 1800MHz.


There's obviously an extensive supporting cast:

* a Macronix [MX25R2035F](https://www.macronix.com/Lists/Datasheet/Attachments/8696/MX25R2035F,%20Wide%20Range,%202Mb,%20v1.6.pdf)
  serial flash

    This is used to configure the FPGA.

* an [SGM2054](http://www.sg-micro.com/uploads/soft/20220506/1651829741.pdf) DDR termination voltage controller

* an [LM26480](https://www.ti.com/lit/ds/symlink/lm26480.pdf) power management unit

  It has two linear voltage regulators and two step-down DC-DC converters.

* two clock oscillators: 24MHz and 19.2MHz 

* a TI [HD3SS3220](https://www.ti.com/lit/ds/symlink/hd3ss3220.pdf) USB-C Mux

  This is the glue logic that makes it possible for USB-C connectors to be orientation independent.

* a [SP3010-04UTG](https://www.arrow.com/en/products/sp3010-04utg/littelfuse) for USB ESD protection 

    Marked QH4

Two 5x2 pin connectors J7 and J8 on the right size of the PCB are almost certainly used to connect
JTAG programming and debugging cables to the FPGA and the CYUSB-3014. 
    

[![DSLogic PCB top side - annotated](/assets/dslogic/DSLogic_PCB_top_side_annotated.jpg)](/assets/dslogic/DSLogic_PCB_top_side_annotated.jpg)
*(Click to enlarge)*

# The Input Circuit

I spent a bit of time Ohm-ing out the input circuit. Here's what I came up with:

[![DSLogic input schematic](/assets/dslogic/DSLogic_input_schematic.png)](/assets/dslogic/DSLogic_input_schematic.png)

The cable itself has a 100k Ohm series resistance. Together with a 100k Ohm shunt resistor to ground at the entrance of
the PCB it acts as by-two resistive divider. The series resistor also limits the current going into the device.

Before passing through a 33 Ohm series resistor that goes into the FPGA, there's an ESD protection
device. I'm not 100% sure, but my guess is that it's an [SRV05-4D-TP](https://www.mccsemi.com/pdf/Products/SRV05-4D(SOT23-6L).pdf)
or some variant thereof.

I'm not 100% sure why the 33 Ohm resistor is there. It's common to have these type of resistors on high
speed lines to avoid reflection but since there's already a 100k resistor in the path, I don't think that
makes much sense here. It might be there for additional protection of the ESD structure that resides inside
the FPGA IOs?

A DSLogic has a fully programmable input threshold voltage. If that's the case, then where's the 
opamp to compare the input voltage against this threshold voltage? (There is such a comparator on a
Saleae Logic Pro!)

The answer to that question is: "it's in the FPGA!"

FPGA IOs can support many different I/O standards: single-ended ones, think CMOS and TTL, and a whole bunch of differential
standards too. Differential protocols compare a positive and a negative version of the same signal but nothing 
prevents anyone from assigning a static value to the negative input of a differential pair and making the input
circuit behave as a regular single-end pair with programmable threshold. Like this:

[![DSLogic Spartan LVDS Input](/assets/dslogic/DSLogic_Spartan_LVDS_Input.png)](/assets/dslogic/DSLogic_Spartan_LVDS_Input.png)

There is plenty of literature out there about using the LVDS comparator in single-ended mode. It's even
possible to create pretty fast analog-digital convertors this way, but that's outside the scope of this
blog post.

# Impact of Input Circuit on Circuit Under Test


[![DSLogic Pro video](/assets/dslogic/DSLogic_Pro_video.jpg)](/assets/dslogic/DSLogic_Pro_video.jpg)

7 years ago, OpenTechLab [reviewed the DSLogic Plus](https://www.youtube.com/watch?v=xZ5wKYnCNcs), 
the predecessor of the DSLogic U3Pro16. Joel
spent a lot of time [looking at its input circuit](https://youtu.be/xZ5wKYnCNcs?t=439). He mentions
a 7.6k Ohm pull-down resistor at the input, different than the 100k Ohm that I measured. There's
no mention of a series resistor in the cable or about the way adjustable thresholds are handled, but
I think that the DSLogic Pro has a simular input circuit.

His review continues with an [in-depth analysis](https://youtu.be/xZ5wKYnCNcs?t=660) of how measuring a signal 
can impact the signal itself. He even [builds a simulation model of the whole system](https://youtu.be/xZ5wKYnCNcs?t=1142)
and does a [real-world comparison between a DSLogic measurement and a fake-Saleae one](https://youtu.be/xZ5wKYnCNcs?t=1397).

While his measurements are convincing, I wasn't able to repeat his results on a similar setup with
a DSLogic U3Pro16 and a Saleae Logic Pro: for both cases, a 200MHz signal was still good enough. I need to
spend a bit more time to better understand the difference between my and his setup...

Either way, I recommend watching this video.

# Additional IOs: External Clock, Trigger In, Trigger Out

In addition to the 16 input pins that are used to record data, the DSLogic has 3 special IOs and
a seperate 3-wire cable to wire them up. They are marked with the character "OIC" above the connector, short 
for Output, Input, Clock.

* Clock

    Instead of using a free-running internal clock, the 16 input signals can be sampled with an
    external sampling clock.

    This corresponds to a mode that's called "state clocking" in big-iron Tektronix and
    HP/Agilent/Keysight logic analyzers. 

    Using an external clock that is the same as the one that is used to generate the signals that you 
    want to record is a major benefit: you will always record the signal at the right time as long as 
    setup and hold requirements are met. When using a free-running internal sampling clock, the sample
    rate must a factor of 2 or more higher to get an accurate representation of what's going on in the 
    system.

    The DSLogic U3Pro16 provides the option to sample the data signals at the positive or negative
    edge of the external clock. On one hand, I would have prefered more options in moving the edge of 
    the clock back and forth. It's something that should be doable with the DLLs that are part of the
    DCMs blocks of a Spartan-6. But on the other, external clocking is not supported at all by Saleae
    analyzers.

    The maximum clock speed of the external clock input is 50MHz, significantly lower than the free-running 
    sample speed. This is the usually the case as well for big iron logic analyzers. For example, my
    old Agilent 1670G has a free running sampling clock of 500MHz and supports a maximum state clock of 150MHz.

* Trigger In

    According to the manual: "TI is the input for an external trigger signal". That's a great
    feature, but I couldn't figure out a way in DSView on how to enable it. After a bit of googling,
    I found the [following comment in an issue on GitHub](https://github.com/DreamSourceLab/DSView/issues/145#issuecomment-408728931).

    > This "TI" signal has no function now. It's reserved for compatible and further extension.

    This comment is dated July 29, 2018. A closer look at the U3Pro16 datasheets shows the description of
    the "TI" input as "Reserved"...

* Trigger Out
    
    When a trigger is activated inside the U3Pro16, a pulse is generated on this pin.

    The manual doesn't give more details, but after futzing around with the horrible oscilloscope UI of my
    1670G, I was able to capture a 500ms trigger-out pulse of 1.8V.


# Software: From Saleae Logic to PulseView to DSView

When Saleae first came to market, they raised the bar for logic analyzer software with
Logic, which had a GUI that allowed scrolling and zooming in and out of waveforms at blazing 
speed. Logic also added a few protocol decoders and an C++ API to create your own decoders.

It was the inspiration of [PulseView](https://sigrok.org/wiki/PulseView), 
an open source equivalent that acts as the front-end
application of [SigRok](https://sigrok.org/wiki/Main_Page), 
an open source library and tool that acts as the waveform data acquisition
backend. 

PulseView supports protocol decoders as well, but it has an easier to use Python
API and it allows stacked protocol decoders: a low-level decoder might convert the recorded
signals into, say, I2C tokens (start/stop/one/zero). A second decoder creates byte-level I2C transactions
out of the tokens. And an I2C EEPROM decoder could interpret multiple I2C byte transactions as read and write operations. 
PulseView has tons of protocol decoders, from simple UART transactions, all the way to USB 2.0 decoders.

When the DSLogic logic analyzer hit the market after a successful Kickstarter campaign, it shipped 
with DSView, DreamSourceLab's closed source waveform viewer. However, people soon discovered that it 
was a reskinned version of PulseView, a big no-no since the latter is developed under a GPL3
license.

After a bit of drama, DreamSourceLab made [DSView available on GitHub](https://github.com/DreamSourceLab/DSView) 
under the required GPL3 as well, with attribution to the Sigrok project. DSView is a hard 
fork of PulseView and there are still some bad feelings because DreamSourceLab doesn't push 
changes to the PulseView project, but at least they've legally in the clear for the past 6 years.

The default choice would be to use DSView to control your DSLogic, but Sigrok/PulseView
supports DSView as well. 

In the figure below, you can see DSView in demo mode, no hardware device connected, and an example
of the 3 stacked protocol described earlier:

[![DSView Stacked Protocol Decoders](/assets/dslogic/DSView_stacked_protocols.png)](/assets/dslogic/DSView_stacked_protocols.png)
*(Click to enlarge)*

For this review, I'll be using DSView.

*Saleae has since upgrade Logic to Logic2, and now also supports stacked protocol decoders.
It still uses [a C++ API](https://support.saleae.com/saleae-api-and-sdk/protocol-analyzer-sdk) though. 
You can find an example decoder [here](https://github.com/saleae/SampleAnalyzer).*

# Installing DSView on a Linux Machine

DreamSourceLab provides DSView binaries for Windows and MacOS binaries but not for Linux.
When you click the Download button for Linux, it returns a tar file with the
source code, which you're expected to compile yourself.

I wasn't looking forward to running into the usual issues with package dependencies and build failures, but
after following the instructions in the [INSTALL file,](https://github.com/DreamSourceLab/DSView/blob/master/INSTALL) 
I ended up with a working executable on first try.

# DSView UI

The UI of DSView is straightforward and similar to Saleae Logic 2. There are things that annoy me in both 
tools but I have a slight preference for Logic 2. Both DSView and Logic2 have a demo mode that allows you to
play with it without a real device attached. If you want to get a feel of what you like better, just download
the software and play with it.

Some random observations:

* DSView can pan and zoom in or out just as fast as Logic 2.
* On a MacBook, the way to navigate through the waveform really rubs me the wrong way: it uses the pinching
  gesture on a trackpad to zoom in and out. That seems like the obvious way to do it, but since it's such a common
  operation to browse through a waveform it slows you down. On my HP Laptop 17, DSView uses the 2 finger slide up 
  and down to zoom in and out which is much faster. Logic 2 also uses the 2 finger slide up and down.
* The stacked protocol decoders area amazing. 
* Like Logic 2, DSView can export decoded protocols as CSV files, but only one protocol at a time. It would be nice to be 
  able to export multiple protocols in the same CSV file so that you can easier compare transaction flow between interfaces.
* Logic 2 behaves predictably when you navigate through waveforms while the devices is still acquiring new data. DSView
  behaves a bit erratic.
* In DSView, you need to double click on the waveform to set a time marker. That's easy enough, but it's not intuitive and
  since I only use the device occasionally, I need to google every time I take it out of the closet.
* You can't assign a text label to a DSView cursors/time marker. 

None of the points above disquality DSView: it's a functional and stable piece of software. But I'd be lying if I wrote
that DSView is as frictionless and polished as Logic 2.

# Streaming Data to the Host vs Local Storage in DRAM

The Saleae Logic 16 Pro only supports streaming mode: recorded data is immediately sent to the PC to which the
device is connected. The U3Pro16 supports both streaming and buffered mode, where data is written in the
DRAM that's on the device and only transported to the host when the recording is complete.

Streaming mode introduces a dependency on the upstream bandwidth. An Infineon FX3 supports USB3 data rates
up 5Gbps, but it's far from certain that those rates are achieved in practice. And if so, it still limits
recording 16 channels to around 300MHz, assuming no overhead.

In practice, higher rates are possible because both devices support run length encoding (RLE), a compression
technique that reduces sequences of the same value to that value and the length of the sequence. Of course, RLE
introduces recording uncertainty: high activity rates may result in the exceeding the available bandwidth.

The U3Pro16 has a 16-bit wide 2Gbit DDR3 DRAM with a maximum data rate of 1.6G samples per second. Theoretically,
make it possible to record 16 channels with a 1.6GHz sample rate, but that assumes accessing DRAM with 100% efficiency,
which is never the case.

![DSView Device Options window](/assets/dslogic/DSView_device_options_window.png)

The GUI has the option of recording 16 signals at 500MHz or 8 signals at 1GHz. Even when recording to the local
DRAM, RLE compression is still possible. When RLE is disabled and the highest sample rate is selected, 268ms
of data can be recorded.

When connected to my Windows laptop, buffered mode worked fine, but on my MacBook Air M2 DSView always hangs when
downloading the data that was recorded at high sample rates and I have to kill the application. 

In practice, I rarely record at high sample rates and I always use streaming mode which works reliably on the
Mac too. But it's not a good look for DSView.

# Triggers

One of the biggest benefits of the U3Pro16 over a Saleae is their trigger capability. Saleae Logic 2.4.22 offers the following
options:

[![Saleae Logic trigger options](/assets/dslogic/Saleae_trigger_options.png)](/assets/dslogic/Saleae_trigger_options.png)

You can set a rising edge, falling edge, a high or a low level on 1 signal in combination with some static values on 
other signals, and that's it. There's not even a rising-or-falling edge option. It's frankly a bit embarrassing. When you have a 
FPGA at your disposal, triggering functionality is not hard to implement.

Meanwhile, even in Simple Trigger mode, the DSLogic can trigger on multiple edges at the same time, something that can
be useful when using an external sampling clock.

[![DSLogic simple trigger options](/assets/dslogic/DSLogic_simple_trigger_option.png)](/assets/dslogic/DSLogic_simple_trigger_option.png)

But the DSLogic really shines when enabling the Advanced Trigger option.

In Stage Trigger mode, you can create state sequences that are up to 16 phases long, with 2 16-bit comparisons
and a counter per stage. 

[![DSLogic stage trigger](/assets/dslogic/DSLogic_stage_trigger.png)](/assets/dslogic/DSLogic_stage_trigger.png)

Alternatively, Serial Trigger mode is a powerful enough to capture protocols like I2C, as shown below, where a start
flag is triggered by a falling edge of SDA when SCL is high, a stop flag by a rising edge of SDA when SCL is high,
and data bits are captured on the rising edge of SCL:

[![DSLogic serial trigger](/assets/dslogic/DSLogic_serial_trigger.png)](/assets/dslogic/DSLogic_serial_trigger.png)

You don't always need powerful trigger options, but they're great to have when you do.

# Conclusion

The U3Pro16 is not perfect. It doesn't have an analog mode, buffered mode doesn't work reliably on my MacBook, and the DSView
GUI is a bit quirky. But it is relatively cheap, it has a huge library of decoding protocols, and the triggering modes are
excellent.

I've used it for a few projects now and it hasn't let me down so far. If you're in the market for a cheap logic analyzer,
give it a good look.

# References

* [Logic Analyzer Shopping](https://www.bigmessowires.com/2021/11/21/logic-analyzer-shopping/)

    Comparison between Saleae Logic Pro 16, Innomaker LA2016, Innomaker LA5016, DSLogic Plus, and DSLogic U3Pro16

# Footnotes
