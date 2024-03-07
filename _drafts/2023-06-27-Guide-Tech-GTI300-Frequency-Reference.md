---
layout: post
title: Guide Technology GT300 Frequency Standard Teardown
date:   2023-06-27 00:00:00 -1000
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

I've gathered quite a bit of lab equipement over the years. Quite a few of them
have an oven controlled crystal oscillator (OCXO), there's even two pieces of obsolete telecom 
equipment with a Rubidium atomic clock module that are waiting for some modifications to be usable 
as timing reference.  I also have the [TM4313 GPSDO](/2023/07/09/TM4313-GPSDO-Teardown.html)
that I give took apart last year.

But none of these serve as my lab's central 10MHz reference clock generator. For that, I use
this tidy little box: a GT300 frequency standard from Guide Technology Inc., another Craigslist 
acquisition from Lew's lab that I got really cheap as part of package deal.

![GT300 Front](/assets/gt300/gt300_front.jpg)

There are a few reason why I'm using this instead some of my other references:

1. it has an aged, very low drift OCXO. Lew even had some ran some long-term tests
   to check the PPM deviation over time.
1. it doesn't require me to keep a cable running from my cave to a GPS antenna outside
   the house.
1. it has two outputs. That's usually enough for most of my use cases.
1. it's small enough to sit on my desk without taking valuable space.
1. it consumes much lower power than my boat anchor pieces of equipment with built-in
   OCXO. I can leave the GT300 on at all times.

An OCXO based reference standard is really simple. All you need is the OCXO itself,
a power supply, and a voltage trimming circuit to calibrate the output against a
GPSDO.

There's not a whole lot to learn, but Lew had already gone to the trouble to reverse
engineer the schematic down to the last detail, so why not give it a good look?

# Inside the GT300

[![GT300 PCB](/assets/gt300/gt300_pcb.jpg)](/assets/gt300/gt300_pcb.jpg)
*(Click to enlarge)*

As could be expected, neither the PCB nor the schematic tell a complicated story. 

* The output of a transformer is rectified into a crude 9V DC voltage. 
* An LM317T voltage regulator generate the power supply for most components, but
  there's a twist.
* An MC1403 voltage reference outputs a very stable 2.5V output. 
* Opamp LT1013 is used to drive the tuning port of the OCXO.
* A couple of 74ACT00 gates serves as amplifiers to drive a low pass filters before
  connecting to two outputs with opposite polarity.

[![GT300 schematic](/assets/gt300/GT300_schematic.png)](/assets/gt300/GT300 OCXO Schematic.pdf)
*(Click to enlarge)*

# MC1403 Voltage Reference and OCXO Tuning Circuit

OCXOs have a frequency adjust input to tune the the output to the desired value.
The tuning range is minimal: it's not usually for the range to be less than 1Hz.
To ensure sufficent accuracy, the voltage at the frequency adjust input must
be low noise and very stable. Deriving this voltage from a resistive divider
between the power supply and ground will not do.

The GT300 uses the obsolete [MC1403](https://www.onsemi.com/pdf/datasheet/mc1403-d.pdf)
voltage reference. 

[![MC1403 electrical characteristics](/assets/gt300/mc1403_characteristics.png)](/assets/gt300/mc1403_characteristics.png)
*(Click to enlarge)*

It has an output of 2.5V and a typical temperature coefficient
of 10ppm/C. A 5C temperature difference will change the output by 1.25mV or 0.05%. Not a lot, 
but higher than the 4 digit accuracy that's needed to maintain that 10<sup>-10</sup> 
OCXO precision! 

It shows that even with a voltage reference, it's still important to have a temperature 
controlled room for accurate frequency measurements.

I redrew the schematic in KiCAD to make the arrange the component is a more
logical way, with some annotations to confirm the values that Lew measured on the board:

[![OCXO tuning circuit](/assets/gt300/ocxo_tuning_circuit.png)](/assets/gt300/ocxo_tuning_circuit.png)
*(Click to enlarge)*

Surprisingly, Vin of the MC1403 is indirectly connected to the the unregulated +9V instead 
of the regulated 5V. I think there's two reasons for this: the electrical characteristics
of the MC1403 are specified for 15V. 5V may be too low to achieve the listed specification. 
But another one is that the 5V itself depends on the 2.5V reference! I'll get into that later.

The output of the reference goes to trim potentiometer RV1 with a control screw
that's accessible on the front panel. This is the screw to turn when you want
to calibrate that output clock. 

Opamp [LT1013](https://www.analog.com/media/en/technical-documentation/data-sheets/lt1013-lt1014.pdf) 
with a low temperature drift doubles the 0 to 2.5V output range of the potentiometer 
to the 0 to 5V range of the OXCO frequency adjust input. 

# LM317 Voltage Regulator Basics

The GT300 uses an LM317 voltage regulator to create a stable 5V supply for the
OCXO, but the circuit uses is a bit more complicated that what you'd expect.

The datasheet of the LM317 contains a number of application examples, but they're
all a variant of the following basic circuit:

![LM317 Basic Circuit](/assets/gt300/LM317_basic_circuit.jpg)

The formula of the output voltage is 

$$
V_\text{o} = V_\text{ref}(1+\frac{R_2}{R_1}) + (I_\text{adj} \cdot R_2)
$$

where $$V_\text{ref}$$ is 1.25V and $$I_\text{ADJ}$$ around 50uA, but it can go up to 
100uA.


Instead of just accepting the formula above as gospel, I derived the formula
myself. To do that, you need start with the block diagram of the LM317:

![LM317 Block Diagram](/assets/gt300/LM317_block_diagram.jpg)

We can see an opamp, a 1.25V zener diode at the plus input, a drive transistor
duo in Darlington configuration, the constant current source, and some miscellaneous 
protection logic.

Let's simplify this a little bit and only keep the items that are part of the
control loop:

![LM317 Control Loop](/assets/gt300/LM317_control_loop.svg)

Here's how we get the formula:

1. $$V_\text{plus}$$ is the voltage at the positive input of the opamp.
1. After going through the drive transistor, the output of the
   opamp gets fed back directly to the negative input of the opamp.
1. The opamp tries to keep the positive and the negative inputs
   the same.
1. Since this signal also goes to the output terminal $$V_\text{out}$$ of the
   LM317, we know that $$V_\text{out}$$ has the value of $$V_\text{plus}$$.
1. Due to the 1.25V zener, the voltage of the ADJUST input of the LM317 is
   $$V_\text{plus}-1.25V$$.
1. We can now calculate $$I_{R_1}$$, the current through resistor $$R_1$$.
1. The current through R2 is the current through $$R_1$$ plus $$I_\text{adj}$$, the
   current from the constant current source.
1. From this, we can calculate the voltage drop across $$R_2$$. 
1. And from that, we can derive the value of Vplus, and thus the output voltage Vo.

In many cases, the current through $$R_1$$ will be much larger than $$I_\text{adj}$$,
and we can just ignore the $$I_\text{adj}$$ term altogether. 

The LM317 has its own built-in voltage reference, the 1.25V zener diode. It
only takes 2 resistors to create an accurate output voltage.


# OCXO Frequency Adjustment

The crystal oscillator inside an OCXO isn't perfect, so your typical OCXO comes
with a way to tune the output frequency to the perfect value, or to use the OCXO
as an element in PLL.  The tuning range is usually quite narrow. I don't have the 
specification of the Vectron 318Y0839 that's used in the GT300, but the famous 
HP 10811A/B has a 
[service manual](http://hparchive.com/Manuals/HP-10811AB-Manual.pdf)
with full schematics (and much more!), so let's use that for the discussion here.

The 10811A has an output frequency of 10MHz and an electrical tuning range of &plusmn;1Hz, 
or a relative range of just of 10<sup>-7</sup>.
Most OCXOs have only 1 way to control the output frequency, by applying a voltage
on their frequency adjust input. The 10811A has two options:
through its EFC, electronic frequency adjust, input, or by changing the value of a 
trimmable capacitor. The trimmable capacitor is used for coarse tuning and
 can change the output frequency by &plusmn;20Hz.

Both tuning methods are highlighted in the schematic below:

[![HP 10811A OCXO schematic](/assets/gt300/hp10811_schematic.png)](/assets/gt300/hp10811_schematic.png)
*(Click to enlarge)*

The trim capacitor is circled in green. The EFC circuit is marked in red.

Fundamentally, the EFC circuit and the trim capacitor achieve their goal
the same way: they change the resonance frequency by adjusting the capacitance 
of the oscillation loop. In the case of EFC, the variable capacitance is a 
[varicap diode](https://en.wikipedia.org/wiki/Varicap), a diode with a capacitance
that depends on the reverse bias voltage. Check out section 8-13 and 8-20
of the service manual for an in-depth explanation of the oscillator theory
of operation.

For the 10811A, the EFC input accepts a voltage from -5V to 5V. If you want to
control the OCXO with a relative precision of, say, 10<sup>-10</sup>, and the 
EFC input has a 10<sup>-7</sup> frequency range, then you need to be
able to control the EFC voltage with a 4 digit accuracy, which requires 
a pretty stable voltage reference. The exact output voltage doesn't matter too
much, you'll need to calibrate the thing anyway, but the stability over
temperature and power supply, and the noise is imporant.



# Regulating the Output Voltage with an External Voltage Reference

The power supply circuit of t




> It includes current limiting, thermal overload protection, and safe 
> operating area protection. Overload protection remains functional even 
> if the ADJUST terminal is disconnected.

# Reference

* [Schematic](/assets/gt300/GT300 OCXO Schematic.pdf)
* [TI - LM317 Datasheet](https://www.ti.com/lit/ds/symlink/lm317.pdf)
* [Analog Devices/Linear Technology - LT1013 Datasheet](https://www.analog.com/media/en/technical-documentation/data-sheets/lt1013-lt1014.pdf) 
