---
layout: post
title: A Look at Logic Analyzer Front-Ends
date:   2023-03-25 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction 


# Logic Analyzer Probes

If you're going to analyze relatively high speed signals, it's best to pay at least a little bit of
attention to the probes that you'll be using to record them. When dealing with high-speed signals, you'll
quickly run into a slightly esoteric world (for me at least) where you run into concepts such as
characteristic impedance, reflections, bypass capacitor and so forth.

Different products have different solutions of various sophistication.

**Basic Logic Analyzer**

Very basic logic analyzer, often hobby projects, that are built with off-the-shelve hardware, usually
don't do anythin special at all: there's no mention of input impedance or capacitive load, there's no
over-voltage or additional ESD protections. There's often no support for different signalling voltage
levels either: it expects a 3v3 signal that goes from a 0.1" pin header to the input of an FPGA or a
Raspberry Pico, and that's pretty much it.

** Original Saleae Logic**

The original [Saleae Logic analyzer ](https://sigrok.org/wiki/Saleae_Logic) takes things to a slightly
higher level by adding [ESD protection](https://www.st.com/en/protections-and-emi-filters/dviulc6-4sc6.html)
to each of the 8 input lines and an input resistor. (XXX: how much? Is it in series or connector to ground?)
One negative of this version is the lack of a ground connection per signal which can result in interference
between different signals because all signals will use the same wire for the return current. The voltage
threshold levels (VIL and VIH) are also fixed.

**Saleae Logic Clones**

There are plenty of clones of the original Saleae analyzer. [This one](https://iamzxlee.wordpress.com/2015/09/15/usb-logic-analyzer-review/)
uses a 74HC254 octal buffer on the input signals before sending it through to the Cypress USB
controller.

**Saleae Logic Pro 8 and 16**

The current Saleae Pro 8 and Pro 16 series take things to a higher level: the device supports analog
signal recording on all of its input at sample rates up to 50MHz (XXX verify) for voltages between
-9V and +9V. It also has a number of pre-set voltage thresholds that are, unfortunately, not programmable.
There's now also a ground wire per input. ESD protection is obviously still there. The exact
front-end configuration hasn't been reverse engineered, but in a Twitter exchange,
[Saleae disclosed](https://twitter.com/timonsku/status/1497925200725295109)
that they are using 3 opamps per signal for the analog path, and 1 comparator for the digital path.

I came up with the following possible configuration:

The first opamp is a buffer with a high impedance input to ensure that the device under test doesn't
see a high load. It also does some voltage level translation. The second does an addition voltage
translation to be in range for the downstream ADC. The third opamp inverts the signal, because the
ADC expects a differential input.

In addition to the logic path, there's also a fast ADCMP600BRJZ comparator per input to create a
digital value. It's not clear how the threshold voltage for this comparator is generated. I couldn't
find a DAC on the PCB to do it, so maybe the FPGA does it by filtering a PWM signal? The threshold
voltage doesn't need to be super accurate...

Despite having a ground wire per signal, the probe wires are still a pain point. There are two separate
strands from the connection point to the device for the actual signal and the ground, which still
creates the possiblity of a pretty large inductive loop. (XXX: calculate this inductance!)

** DreamSourceLab DSLogic U3Pro16**


Saleae logic analyzers are considered the gold standard in the protable USB logic analyzer market, but
the DreamSourceLab DSLogic U3Pro16 is a good contender, and much cheaper. It lacks the analog input
(which allows them to avoid the hugely expensive analog digital converter) but is otherwise just as
good as a Saleae Logic Pro, if not better for some important points.

The probe wires are on a whole other level: not only is there a ground connection per signal, but the
ground and the signal wire quickly merge into single coaxial (?) wire on their way to the connector.
There's a 100k Ohm resistor embedded in the probe wire itself (XXX: what are the benefits of that?),
which forms a resistive 2:1 divider with another 100k Ohm resistor to ground inside the PCB, and
another 33 Ohm series resistor on the way to the FPGA.

Like the Saleae devices, there's also ESD protection per pin. It only supports positive voltages as
input, so it can make do with an SVR05-4 ESD protection device that has a TVS diode (for ESD protection)
as well as traditional voltage clamping diodes per signal.

Unlike a Saleae, the DSLogic does not have a comparator per pin, yet one can set the threshold voltage
in steps of 0.1V. How is that possible?

There are two possible answers:

* by configuring the Spartan-6 IOs as LVDS IOs, and connecting the negative input of the pair
  to the threshold.

    LVDS receives have a built-in comparator, and there's a large body of literature that explores
    abusing this comparator as a generic comparator. The Spartan-6 family in particular is known to
    have everything in place make this comparator work across the whole voltage range, not just the
    narrow band in which LVDS IOs need to operate.

* by configuration IOs to a format that uses VREF

    Signaling protocols such as HST and various versions of SSTL use a separate VREF input to set the
    signal threshold level. It's customary to set VREF to half the voltage rail of the FPGA IO bank, but
    that is not necessary.

    One thing to keep in mind is that a signaling protocol must be selected that doesn't enable a termination
    resistors (e.g. 50 Ohm) on the input, because that mess up the 100k/100k resistive voltage divider.

It's not clear which method is used by the DSLogic. I've tried both methods with a Cyclone II setup and
here were my results:

**HP 16500A with HP XXXXX acquisition card**

All the previous devices are quite recent. This one is definitely not, but it's an illustration of what
was one state of the art. The HP 16500A is a chassis with a generic CPU board in which various acquistion
cards can be plugged in. Mine has a XXX board, the lowest end model, which expects state processing
at just 25MHz and transaction recording at 100MHz.

All logical analyzer acquistion module of the era had a 40-pin connectors in which multiple cables with
pods could be plugged in.

The cables are definitely interesting: they consist of effectively lossless ground wires interleaved with
lossy signal wires. The resistance of the signal wires is typically around 185 Ohm. It's done this way because
there is no impedance matching on either side of the cable. The resistance, spread along the whole wire,
is there to reduce reflection. In later acquisition cards (with a 90-pin instead of 40-pin connector), HP
switched a lossless cables that contains these tiny coaxial wires. The maximum bandwidth for these cables
is set at 200 MHz. (XXX provide reference. Patent?)

Unfortunately, HP doesn't list the capacitance or characteristic impedance of the cable. When performance
experiments with a NanoVNA, I ended up with this: XXX.

The braided cable is just the start. You also need a pod at the other end to pick up the actual signal. HP
has many options, but the most common one is the HP XXXXX pod. They are somewhat similar to the DSLogic
probe wires in the sense that they have the possibility to connect a ground wire per signal, and they
have 90.1k Ohm series resistor. In addition to that, they first have a 250 Ohm series resistor
(XXX explain why) and a XXX pf bypass capacitor around the 90.1k Ohm resistor.

I traced the signal progress on the acquistion card and found another 250 Ohm resistor, followed
by a 10k resistor to ground. Together with the 90.1k resistor in the probe itself, this creates
roughly a 10:1 voltage divider.

HP probe pods can be obtains quite cheaply on eBay, and I trust them to be very high quality. So I decided
to use them for my own logic analyzer. Here's a Spice simulation on CircuitLab.com in which a use
an HP pod, a braided cable, an opamp circuit that should allow me to record digital signals up to
100MHz and analog signals up to 20MHz. There are specs that are higher than a Saleae.

**HP 16517A High-Speed Acquisition Card**

See patent below.

# References

* [How to Measure the Characteristic Impedance and Attenuation of a Cable](https://onlinelibrary.wiley.com/doi/pdf/10.1002/9780470423875.app3)
* [Timonsku Saleae Logic Pro 8 Teardown Thread](https://twitter.com/timonsku/status/1497725434888437762)
* [Estimating wire & loop inductance: Rule of Thumb #15](https://www.edn.com/estimating-wire-loop-inductance-rule-of-thumb-15/)
* [Method of probing a pulsed signal in a circuit using a wide bandwidth passive probe](https://patents.google.com/patent/EP0513992B1/)

    Spectacular patent that has all the calculations.

    Inventions:

    * low capacitance probe tip (not interesting)
    * front-end resistor in series with a conventional RC tip network
        * establishes minimum input impedance at the probe input
        * provides ~80% of the high frequency attenuation when working into the cable characteristic impedance
    * standard non-lossy cable
        * as long as the AC terminating capacitance is ~twice the cable capacitance
    * terminating network contains 2 resistors in series with th terminating capacitor to provide
      impedance match with the cable.
        * split to provide the additional 20% of the high frequency attenuation when the signal output
          is taken from their common node
    * references HP 16517A ultra-high speed logic analyzer module
    * Rt=50, Rc=90K, Rs3=10k -> 100.5k impedance at DC. At 1MHz, impedance starts to decrease. Minimum value of 500 Ohm at 100MHz.
    * coax cable=120 Ohm impedance.
    * Rs1=58, Rs2=62, Rs3=10k, Cs=15p
    * Crossover dip: avoided by selecting the cable length such that the reflected signal compensates for the dip, which results
      in a relatively flat curve.
    ( 10" length of a standard 120 Ohm cable is 9pF.

* [Hand-held or hand-manipulated probes, e.g. for oscilloscopes or for portable test instruments](https://patents.google.com/patent/US2883619A)

    Patent for a probe with a lossy line.

* [Doug Smith High Frequency Measurements Page](https://www.emcesd.com/)

    * [Build a 1 GHz probe](https://emcesd.com/1ghzprob.htm)

* [High speed passive probe - contradiction between authors or different points of view?](https://electronics.stackexchange.com/questions/351368/high-speed-passive-probe-contradiction-between-authors-or-different-points-of)

    * [Oscilloscope Probes:Theory and Practice - Hiscocs](https://www.syscompdesign.com/wp-content/uploads/2018/09/probes.pdf)


# ESD protection

* [Nexperia ESD handbook](https://assets.nexperia.com/documents/user-manual/Nexperia_document_book_ESDApplicationHandbook_2018.pdf)

* [TI - How to select a Surge Diode](https://www.ti.com/lit/an/slvae37/slvae37.pdf)

    Great tutorial. Has calculations that how to select a diode.

* [TI System-Level ESD Protection Guide](https://www.ti.com/lit/sg/sszb130d/sszb130d.pdf)

    This is the key document: it shows what kind of protection is needed for different
    applications, along with the right TI ESD device.

* [Onsemi SRV05-4 datasheet](https://www.onsemi.com/pdf/datasheet/srv05-4-d.pdf)

    Also contains applications not about how to connect VCC.

* [Deep explanation on TVS diode voltage suppression?](https://electronics.stackexchange.com/questions/462294/deep-explanation-on-tvs-diode-voltage-suppression)

    "A TVS diode cannot clamp a perfect voltage source; it requires that the source (an indirect lightning strike/stroke for example) has a source impedance."

* [How does ESD protection work with TVS diodes?](https://electronics.stackexchange.com/questions/483959/how-does-esd-protection-work-with-tvs-diodes)

* [Zeners and Transient Voltage Suppressors: Can Either Device Be Used For The Same Applications?](https://www.microsemi.com/document-portal/doc_view/129580-micronote-134-zeners-and-tvs-s-can-either-device-be-used-for-the-same-applications)




