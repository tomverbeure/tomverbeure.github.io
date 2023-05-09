---
layout: post
title: A Look at Probes and Logic Analyzer Front-Ends
date:   2023-03-25 00:00:00 -1000
categories:
---

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    jax: ["input/TeX", "output/HTML-CSS"],
    tex2jax: {
      inlineMath: [ ['$', '$'], ["\\(", "\\)"] ],
      displayMath: [ ['$$', '$$'], ["\\[", "\\]"] ],
      processEscapes: true,
      skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
    //,
    //displayAlign: "left",
    //displayIndent: "2em"
  });
</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_HTML" type="text/javascript"></script>

* TOC
{:toc}

# Introduction 

I've recently picked up a bit of a fascination with logic analyzers. Not the digital aspects, but
the front-end part: the stuff that happens between the probe pin and the FPGA (or custom ASIC
in the case of big ticket gear) that receives the signal.

It's been enlightening. When you start digging into the subject, it's impossible to not learn
about oscilloscope probes as well. It almost embarrassing how little I knew about the whole topic,
and how it resulted in mistaken assumptions.

When you see the following marking on a probe, or on an oscilloscope, do you know what it really
means? I didn't.



I'm using this blog post to 

I'm still very much a beginner, and there are still aspects that I don't understand, so 



# From simple wire to complex probe

When dealing with high-speed signals, you'll quickly run into a slightly esoteric world (for me at least) 
where you run into concepts such as characteristic impedance, reflections, bypass capacitors and so forth.

Different product classes requires different levels of sophistication, but the most important
aspect is the fact that putting a probe on a signal will put a load on that signal which will change
its behavior. It can make a working circuit fail... or, even 'better', it can suddenly make it work.

Let's invent a probe and see how it behaves.

# A simple wire

The simplest logic analyzer probe is just a wire. 

![Probe that's just a wire - theory](/assets/probes/probe_wire_theoretical.png)

And when the conditions are right, it works well enough too:

* signal has the right voltage levels
* low speed protocol such as UART
* long rise/fall time of the signal
* no adverse environment

Let's go through these items one by one.

* signal voltage level

    The FPGA input pin will be typically be configured for one signalling level: 3.3V LVCMOS,
    3.3V LVTTL, etc. The threshold voltage of the input pin is compatible with the signal that
    you're measuring, you'll be fine. If not, then you might not be able to measure anything at
    all. E.g. a 1.8V signal will never cross the 2.0V logic high threshold level of 3.3V LVCMOS.

    A good logic analyzer front-end has the ability to specify different voltage threshold levels.

* low speed protocol

    There's no such thing as an ideal wire. The probe wires will have stray an inductance and
    capacitance. The logic on the PCB will have a capacitance as well.

    A capacitance between probe and ground will act like a low pass filter that kills the signal
    at higher clock speeds.

* long rise and fall times

    Rapidly changing signals in combination with a non-ideal, unterminated wire will result in 
    reflections between the probe point and FPGA pin. It will not only make the measurement
    unreliable, but it has a high chance of breaking the circuit that you're measuring.

* no adverse environment

    The simple wire has no over-voltage protection (e.g. measuring a 5V signals with 3.3V IOs) nor
    does it have protection against extreme overvoltage conditions due to electrostatic discharage
    (ESD) pulses.

    The FPGA itself will have some of that, but it may not be enough in a test environment.

While all of this sounds problematic, there are many cases where the setup above will work
fine. I've created a make shift logic analyzer using the GPIO pin header of an Intel FPGA
development board and running a SignalTap Logic Analyzer on it, and it worked fine for signals
lower than 5MHz, which is more than enough to debug I2C, slower SPI interfaces, UARTs and other
low bandwidth protocols.
    
A good example of an active project is the 
[Raspberry Pico Logic Analyzer](https://github.com/gusmanb/logicanalyzer/wiki/02---LogicAnalyzer-Hardware).
The barebones configuration is a PCB with nothing more but the Pico itself and a connector:

![Raspberry Pico Logical Analyzer Base Board](/assets/probes/raspberry_pico_logic_analyzer_baseboard.png)

For signals with levels other than 3.3V signalling, there is a level shifting plug-in board:

![Raspberry Pico Logical Analyzer Level Shifter Board](/assets/probes/raspberry_pico_logic_analyzer_level_shifting_board.png)

# A more correct simple wire probe

Here's a more accurate diagram of a wire-as-a-probe configuration:

![Probe that's just a wire - reality](/assets/probes/probe_wire_reality.png)

We have capacitances in the circuit-under-test, the pin of the probe, the wire from pin
to the PCB, capacitances on the PCB itself (e.g. connectors), and finally the capacitance
of the FPGA input, which depends primarily on the kind of chip package.

There's the inductance of the probe wire, the source resistance of the buffer that
drives the signal-under-test, and, finally, the input resistance of the FPGA IO.

The stray capacitances are in the pF range,  the input resistance of an FPGA
pin is high, hundreds of kOhms if not more, and the source resistance is usually less than
100 Ohm. 

One thing that's extremely important when understanding passive probes is the way voltage levels 
are divided down.

The 2 primary actors here are the resistors, whose value doesn't change with frequency, and
capacitive reactance, whose value does change with frequency.

Capactive reactance $$X_C$$ is the resistance of the capacitor to AC current. It goes down
with increasing frequency according to the following formula:

$$X_C= 1/(2\pi fC)$$

where $$f$$ is the frequency of the signal, and $$C$$ the capacitance.

For a DC signal, capacitive reactance is infinite, and the load of the probe on the siganl signal 
will be the input resistance of the FPGA. 

The voltage seen at the FPGA pin will be due to  a resitive divider only:

$$V_{FPGA} = \frac{R_{sink}}{R_{sink} + R_{src}} V_{src}$$

With $$R_{sink}$$ very high and $$R_{src}$$ low, $$V_{FPGA}$$ will be nearly
identical to $$V_{src}$$.

$$V_{FPGA} \sim V_{src}$$

Let's raise the frequency of the signal!

If the sum of all capacitances in this example is 10pF, and the signal has a frequency of 20MHz, then
the joint reactance $$X_C$$ is 796 Ohm, which is in parallel with $$R_{sink}$$, making the latter term irrelevant.

For this case, the voltage divider is now:

$$V_{FPGA} = \frac{X_{C}}{X_{C} + R_{src}} V_{src}$$

For an $$R_{src}$$ of 100 Ohm, this makes:

$$V_{FPGA} \sim 0.9 V_{src}$$

Not terrible, but you can see how things will quickly deteriorate with increasing frequencies.

At 100 MHz, the reactance is 160 Ohm, and the result is:

$$V_{FPGA} \sim 0.60 V_{src}$$

That reduces a 3.3V signal to 2.0V at the FPGA. Sufficient to not meet the $$V_{IH}$$ threshold value 
of a 3.3V LVCMOS input.

# What kind of orders of magnitude are we talking about?

One thing I struggle with are reasonable estimates about the magnitude of different
parameters. What's the capacitance of PCB trace, for example?

Here are just a few numbers...

**PCB parameters**

I'll be using the parameters of a [4-layer JLC04161H-3313 stackup](https://jlcpcb.com/impedance):

* minimum trace width: 0.1mm
* minimum trace clearance: 0.1mm
* outside copper thickness: 0.035mm
* FR4 thickness between outside and inner layer: 0.1mm
* FR4 Dielectric constant: 4.05

**Characteristics of a minimum width PCB trace**

I'm using [this PCB impedance and capacitance calculator](https://technick.net/tools/impedance-calculator/)
for this.

When the distance between 2 traces is sufficiently high, and there's a ground plane underneath
an outside trace, we can use a surface microstrip as model, which gives us the following
results:

![Minimum width PCB trace parameters](/assets/probes/minimum_width_trace_parameters.png)

One of the numbers of interest here is that capacitance per unit length. For a 5cm
PCB trace, not too unusual for the cumulative length to go from a connector to an FPGA pin,
the PCB trace capacitance is: 

$$C_{trace} = 0.05m \cdot 87pF/m = 4.4pF$$.

If you make the trace 0.2mm, the capacitance increase from $$87.4pF/m$$ to $$128.5pF/m$$.

The JLC04161H-7628 stackup has an FR4 thickness that's more than double the one of JLC04161H-3313.
For that one, the capacitance for a 0.1 and 0.2mm trace are $$60pF/m$$ and $$77pF/m$$ respectively.

**Package pin/ball capacitance**

The pin or ball of a chip package itself adds considerable amount of capacitance. Intel has 
the [following table in its a Cyclone 10 LP datasheet](https://www.intel.com/content/www/us/en/docs/programmable/683251/current/pin-capacitance.html):

[![Cyclone 10LP Pin Capacitance Table](/assets/probes/cyclone_10lp_pin_capacitance.png)](/assets/probes/cyclone_10lp_pin_capacitance.png)
*Click to enlarge*

The exact value is not important, but it's good to know that it's on the order of $$6pF/pin$$.

**Parallel wire inductance**

When you 2 parallel wires, one for the signal an one for the ground, that are just randomly laying
next to eachother, you may want to know the inductance of that.

[This calculator](https://www.eeweb.com/tools/parallel-wire-inductance/) can help with that, and
with a bunch of other configurations.

Take the Saleae Logic Pro 16 probe wires, which are around 23cm long. Let's assume that the
distance between ground and signal is around 3cm and that the wire diameter is 1mm (this number
doesn't influence the value by much). 

![Parallel Wire Inductance](/assets/probes/parallel_wire_inductance.png)

That give an inductance of $$354nH$$.

# Simulation of the simple wire probe

I like to crosscheck theory with practice, or at least with simulated practice. 
I use [CircuitLab](https://circuitlab.com) for this. It's free for small designs, but a yearly
subscription allows me to try larger circuits.

Here's the simple wire probe with inductances, resistors and capacitors added:

![CircuitLab schematic of simple wire probe](/assets/probes/probe_wire_circuitlab_schematic.png)

You can play with it yourself [here](https://www.circuitlab.com/circuit/u9fbs86jc5cz/probe-simple-wire/).

If we generate a 10MHz 3.3V square wave, here's what happens:

[![Transient waveforms of simple wire probe](/assets/probes/probe_wire_waveforms.png)](/assets/probes/probe_wire_waveforms.png)
*Click to enlarge*

Let's unpack this:

* in blue, we have an ideal square wave.
* in orange, we have the signal that we want to measure. Under ideal circumstances, this would still be
  a square wave, but it has been severely mangled by the probe circuit!
* in light brown, we have the signal that enters the FPGA. There's a massive amount of ringing there.

Instead of a 3.3V signal, the FPGA sees over- and undershoots of 5V and -1.7V. After initially
shooting up to almost 3.3V, the signal under test drops back down to 2.4V. It also takes about 5ns
for the signal at the FPGA to rise to 3.3V. 

The frequency response plot at the FPGA shows a major oscillation at the 60MHz point. 

[![Frequency plot of simple wire probe](/assets/probes/probe_wire_freq_plot.png)](/assets/probes/probe_wire_freq_plot.png)
*Click to enlarge*

This is because the wire inductance and the 20pF capacitor form an resonant LC circuit.

The resonant frequency equation is $$f=2\pi LC$$. Fill in values $$L=354nH$$ and $$C=20pF$$ and you get... 59.8MHz.

*It's important to note that the simulation is pessimistic: we are applying a square wave with an
infinitely steep rise and fall time. This exagerates the amplitude of the ringing.*

I cobbled together a setup with an FPGA sending out a square wave and recorded it with a classic 200MHz
oscilloscope probe:

Here's the result on the scope:

![Ringing signal](/assets/probes/probe_wire_oscilloscope.png)

By some amazing coincidence, there's a 60MHz resonance here as well! However, in this case, the resonance
is due to the oscilloscope probe capacitance and the ground loop which is around 200nH. Still, it's clear that
a resonant circuit is bad news...

Let's see what other logic analyzer are doing about this...

# The original Saleae Logic

Saleae is a very well known seller of streaming USB logic analyzers. There products have evolved over
the years, but it all started with their original 8-channel logic analyzer:

I Ohmed out the PCB and ended up with this:

![Saleae Logic (original) schematic](/assets/probes/saleae_logic_original.png)

We're seeing an ESD protection circuit. There are 2 such components, each one can protect 4 signals.
There's also a 510 Ohm series resistor in the signal path.

This series resistor serves 2 purposes:

* it limits the current that must be consumed in case of an ESD event.

    ESD events can result in voltages of thousands of volts. And ESD protection diode
    acts like a Zener diode that starts to conduct once the voltage across its leads
    exceeds a certain value. However, the energy of a voltage spike goes entirely through
    the protection circuit.

    A series resistor between the probe pin and the ESD protection will limit the maximum
    current through it.

* it dampens the behavior of the resonant LC circuit.

Let's see how that plays out in [CircuitLab](https://www.circuitlab.com/circuit/7f592n83cvwk/probe-saleae-logic-original/):

![Saleae Logic (Original) - CircuitLab schematic](/assets/probes/probe-salae_logic_original-circuitlab.png)

Thanks to the damping resistor, the ringing has disappeared entirely. 

[![Saleaa Logic (Original) - Transient waveform](/assets/probes/probe-saleae_logic_original-waveform.png)](/assets/probes/probe-saleae_logic_original-waveform.png)
*Click to enlarge*

There's a small dip remaining at the probe point, the orange signal, but it's not of the sort that
it would make break the circuit-under-test.

The signal at the FPGA side, or in this case, the Cypress USB chip, has a little bit of difficulty getting
where it needs to be, but it's resonable for a 10MHz signal, especially if you consider that this logic
analyzer has a sample rate limit of 24MHz.

The frequency plot looks much more reasonable as well:

[![Saleaa Logic (Original) - Frequency Response Plot](/assets/probes/probe-saleae_logic_original-freq_plot.png)](/assets/probes/probe-saleae_logic_original-freq_plot.png)
*Click to enlarge*


**Basic Logic Analyzer**

Very basic logic analyzer, often hobby projects, that are built with off-the-shelve hardware, usually
don't do anythin special at all: there's no mention of input impedance or capacitive load, there's no
over-voltage or additional ESD protections. There's often no support for different signalling voltage
levels either: it expects a 3v3 signal that goes from a 0.1" pin header to the input of an FPGA or a
Raspberry Pico, and that's pretty much it.

**Original Saleae Logic**

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

* [TI - Input and Output Characteristics of Digital Integrated Circuits at 2.5V Supply Voltage](https://www.ti.com/lit/ml/szza012/szza012.pdf)

* [StackExchange - How to determine LVCMOS output impedance?](https://electronics.stackexchange.com/questions/365871/how-to-determine-lv-cmos-output-impedance)

* [TI - Measuring Board Parasitics in High-Speed Analog Design](https://www.ti.com/lit/ml/sboa094/sboa094.pdf)

* [StackExchange: inductance of a probe ground wire is around 200nH](https://electronics.stackexchange.com/questions/411399/how-the-low-inductance-of-short-ground-clip-probes-prevents-interference)

* [Logic Analyzer Probing Techniques for High-Speed Digital Systems](https://www.montana.edu/blameres/vitae/publications/e_conference_abst/conf_abst_001_probing_techniques.pdf)

* [HP 10400A Series Operating Note](https://xdevs.com/doc/HP_Agilent_Keysight/HP%2010400A%20Series%20Operating%20Note.pdf)

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




