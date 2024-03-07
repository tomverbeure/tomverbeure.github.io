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

Between all the lab equipment that I've gathered over the years, quite a few of them
an oven controlled crystal oscillator (OCXO). I also have a 
[TM4313 GPSDO](/2023/07/09/TM4313-GPSDO-Teardown.html),
and even two pieces of obsolete telecom equipment that have Rubidium atomic
clock modules in them but those need some modifications to be usable as timing
reference.

But despite all that, my central 10MHz reference clock generator is this tidy
little box: a GT300 frequency standard from Guide Technology Inc., another
Craigslist acquisition from Lew's lab.

![GT300 Front](/assets/gt300/gt300_front.jpg)




[![GT300 PCB](/assets/gt300/gt300_pcb.jpg)](/assets/gt300/gt300_pcb.jpg)
*(Click to enlarge)*

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

The GT300 uses the obsolete [MC1403](https://www.onsemi.com/pdf/datasheet/mc1403-d.pdf)
voltage reference. 

[![MC1403 electrical characteristics](/assets/gt300/mc1403_characteristics.png)](/assets/gt300/mc1403_characteristics.png)
*(Click to enlarge)*

It has an output of 2.5V and a typical temperature coefficient
of 10ppm/C. A 5C temperature difference will change the output by
1.25mV or 0.05%. Not a lot, but higher than the 4 digit accuracy that's
needed to maintain that 10<sup>-10</sup> OCXO precision! This is why
it's so important to have a temperature controlled room for accurate frequency
measurements...

We can also see that it has a typical *Line Regulation* value of 0.6V for
a supply voltage between 4.5V and 15V. This is the output voltage deviation you 
can expect when applying different supply voltages.

![OCXO tuning circuit](/assets/gt300/ocxo_tuning_circuit.png)


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

# Regulating the Output Voltage with an External Voltage Reference

The power supply circuit of t




> It includes current limiting, thermal overload protection, and safe 
> operating area protection. Overload protection remains functional even 
> if the ADJUST terminal is disconnected.

# Reference

* [Schematic](/assets/gt300/GTI OCXO Schematic.pdf)
* [TI - LM317 Datasheet](https://www.ti.com/lit/ds/symlink/lm317.pdf)
