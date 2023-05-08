---
layout: post
title: Automated HP 423A Crystal Detector Characterization with GPIB and Sqlite3
date:   2023-04-19 00:00:00 -1000
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

I picked up some random RF gizmos at the 
[Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com/).
It's part of the grand plan to elevate my RF knowledge from near zero to beginner level: buy
stuff, read about it, play with it, ~~spend more money~~, hope to learn useful things. 
I've found the *playing* part to be a crucial step in the whole process. Things seem to stick 
much better in my brain when all is said and done.[^1] 

[^1]: Writing blog posts about it is equally helpful too!

In this blog post, I'm taking a closer look at this contraption:

![HP 423A](/assets/hp423a/hp423a.jpg)

It's an HP 423A crystal detector. According to the
[operating and service manual](/assets/hp423a/HP_423A,8470A_Operating_&_Service.pdf):

> \[the 423A crystal detector\] is a 50&#937; device designed for measurement use in coaxial systems. The 
> instrument converts RF power levels applied to the 50&#937; input connector into proportional values
> of DC voltage. ... The frequency range of the 423A is 10MHz to 12.4GHz.

In the introduction of 
[an earlier blog post](/2023/04/01/Cable-Length-Measurement-with-an-HP-8007B-Pulse-Generator.html), 
I wrote about John, my local RF equipment dealer. A while ago, he sold me a bargain Wiltron SG-1206/U 
programmable sweep generator that can send out a signal from 10MHz all the way to 20GHz at power levels 
between -115dBm to 15dBm. I also picked up a dirt cheap (and smelly) HP 8656A 1GHz signal generator at 
a previous flea market. I hadn't found a good use for either, so now was a good time to give them a 
little workout.

[![Wiltron SG-1206/U and HP 8656A signal generators](/assets/hp423a/hp8656a_wiltron_sg1206u.jpg)](/assets/hp423a/hp8656a_wiltron_sg1206u.jpg)

In the process of playing with the detector, I discovered the warts of both signal generators, 
I picked up an RF power meter on Craigslist, learned a truckload about RF power measurements and 
the general behavior of diodes and the math behind it, I *finally* installed 
[ngspice](https://ngspice.sourceforge.io/) and ran a bunch of simulations, 
and figured out a misunderstanding about standing-wave ratio (SWR) and their relationship with 
crystal detectors. *(Phew)*

I'm writing things down here to have a reference if I need the info back, but expect
the contents to be meandering between a bunch of topics.

# What is a Crystal Detector?

So what exactly is a crystal detector? [Wikipedia](https://en.wikipedia.org/wiki/Crystal_detector)
claims that...

> ... a crystal detector is an obsolete electronic component used in some early 20th century radio 
> receivers that consists of a piece of crystalline mineral which rectifies the alternating current 
> radio signal.

If they are obsolete, then why are plenty of companies still selling them? It's because 
Wikipedia is refering to the original crystal detectors that started it all: diodes that were 
built out of crystalline minerals instead of contemporary diodes built out of silicon, germanium,
etc. Those early crystalline mineral diodes were one of the first semiconductor devices.

Today's RF crystal detectors are not fundamentally different.
[This Infineon application note](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055) 
describes how RF and microwave detectors are still built with a diode, a capacitor and a
load resistor. They now use low barrier Schottky diodes, but the name
*crystal* detector stuck.

![RF power detector with diode](/assets/hp423a/infineon_rf_power_detector.png)

Their functionality is straightforward: the diode passes only the positive voltage of an RF 
signal though to the other side, a capacitor gets charged up to the peak level of the 
signal but discharges, slowly, due to a load resistor. If all goes well, the output voltage of 
the detector tracks the envelope of the RF signal. 

![Amplitude modulation detection](/assets/hp423a/Amplitude_modulation_detection.png)

This envelope output signal is called the *video signal*, a bit of a confusing name because
the output signal may not have anything to do with video at all, but you better get used to it
because it's a standard term in the world of RF. Even cheap spectrum analyzers, such a 
[TinyVNA Ultra](https://tinysa.org/wiki/pmwiki.php?n=TinySA4.MenuTree) have a menu to change 
VBW, the video bandwidth.

In the early years, crystal detectors were used to build AM radio receivers. As a kid, 
I played with a
[RadioShack 150-in-1 kit](https://en.wikipedia.org/wiki/Electronic_kit), 
and one of the projects was exactly that, an AM radio crystal radio.

[![150-in-1 Radio Shack kit](/assets/hp423a/150in1_kit.jpg)](/assets/hp423a/150in1_kit.jpg)
*(&copy; CC BY 2.0 [Caroline](https://commons.wikimedia.org/wiki/File:Science_Fair_150in1_Electronic_Project_Kit.jpg))*

The <a href="https://www.zpag.net/Electroniques/Kit/200_manual.pdf#page=52" target="_blank">schematic</a>
is very simple. 

![Crystal set radio schematic](/assets/hp423a/crystal_set_radio.jpg)

On the left, a ferrite rod antenna and a variable capacitor create an LC tuning network to select
the radio station. A germanium diode does the detection with a 470K&#937; load resistor.
The schematic doesn't have a capacitor: the output is a 
[piezoelectric earpiece](https://en.wikipedia.org/wiki/Crystal_earpiece) 
has the required capacitance. Notice the absence of a battery. The whole circuit
is powered by the picked up radio waves.

AM radios have long ago moved on from crystal detectors to better solutions. Modern demodulators 
mix (multiply) the incoming signal with a locally generated RF sine wave which makes the original 
LF signal emerge. 

It's not 100% clear to me if crystal detectors are currently still being
used to demodulate other types of AM content. When you google for crystal detectors
today, most hits talk about using them for power measurements and power leveling, where
power measurement is part of a feedback loop that's used to regulate the output of an
RF signal source.

Here's an example of such a power leveling setup, taken from an 
[HP application note ](https://www.hpmemoryproject.org/an/pdf/an_218-5.pdf):

![Power leveling setup](/assets/hp423a/power_leveling.png)

Detector HP 8470B, a close cousin of my HP 423A, measures the power
of a chain that starts at a signal generator, goes through a 
[pulse modulator](/2023/05/06/HP-11720A-Pulse-Modulator.html),
and amplifier, and a directional coupler. The output of the detector ends up back at 
the signal generator through its automatic level control (ALC) input.

# Diode Square Law Behavior

A little bit of theory about diodes now will go a long way in understand what comes later.

A diode is often simplified to a device that blocks current when the voltage
across its junction is less than a certain threshold level, and that passes current
otherwise. Such an ideal device has the following voltage to current graph:

![Behavior of ideal diode with and without threshold](/assets/hp423a/ideal_diode.png)

In this ideal case, the resistance of the diode is zero above the threshold and
infinite below. In practice, a diode is always used in a circuit that has some kind
of some kind of series resistance (not necessarily resistor!) to limit the current. 
Together, the diode and this resistance form a voltage divider.

![Diode - Resistor schematic](/assets/hp423a/diode_r_schematic.png) 

When the diode is ideal, the infinite current characteristic simply means that the 
voltage across the diode will always be limited to the threshold voltage, and that
the remainder of the diode/resistance combo will fall over the resistance.

In reality, a diode doesn't behave like a clean on/off device that depends on the voltage
across the device. Instead, the current/voltage curve can be described with the following 
formula:

$$
I(Vd) = \begin{cases}
I_S(e^\frac{qV_d}{nkT}-1) & V_d>V_z \\
-\infty & V_d \le V_z
\end{cases}
$$

The plot of this function looks like this:

![Diode I/V curve](/assets/hp423a/diode_iv_curve.png) 

Above $$V_Z$$, the reverse breakdown voltage, the curve is an exponential
function. Below the reverse breakdown voltage, the diode self-destructs...

Compared to an ideal diode, there is:

* a small current when the diode is reverse polarized
* a smooth transition region to go from almost no current to *a lot* of current
* the reverse breakdown voltage

There are a bunch of factors in the general equation:

* $$V_d$$ is the junction voltage, the voltage across the diode terminals.
* $$T$$ is the absolute temperature.
* $$I_S$$ is the diode leakage current density in the absence of light. 
* $$n$$ is an ideality factor between 1 and 2 that typically increases when the current decreases.
* $$k$$ is [Boltzmann's constant](https://en.wikipedia.org/wiki/Boltzmann_constant).
* $$q$$ is the [charge of an electron](https://en.wikipedia.org/wiki/Elementary_charge).

The $$\frac{kT}{q}$$ factor of the exponent is usually called $$V_T$$. It simplifies the exponential 
equation to:

$$I(V_d) = I_S(e^\frac{V_d}{nV_T}-1)$$

At a temperature of 300K, $$V_T$$ has value of 0.026mV.

A lot can be said about this equation, but there's plenty of content on the web on that
already. Check out the [Diode Equation](https://www.pveducation.org/pvcdrom/pn-junctions/diode-equation)
or [the Ideal Diode Equation][ideal_diode_equation].

[ideal_diode_equation]:https://eng.libretexts.org/Bookshelves/Materials_Science/Supplemental_Modules_(Materials_Science)/Solar_Basics/D._P-N_Junction_Diodes/3%3A_Ideal_Diode_Equation

One thing is clear though: as soon as $$V_d$$ goes over a certain threshold,
the current through the diode will be so high that it might as well be an
ideal diode, and in a resistive divider, the resistance will carry the
voltage in excess of the threshold.

But let's zoom in on what happens below the threshold:

![Diode I/V curve - subthreshold](/assets/hp423a/diode_iv_curve_subthreshold.png) 

The real I/V curve is still exponential, of course, but below 0.3V, it can
be approximated very well with a quadratic curve. In this case, the
exponential curve has been aproximated by $$I(V_d)=1.055V_d^2+0.219x$$.

The quadratic behavior can be explained with a little bit of high school calculus.
The [Taylor series](https://en.wikipedia.org/wiki/Taylor_series) of exponential function is: 

$$e^x = 1 + x + \frac{x^2}{2!} + \frac{x^3}{3!} + \frac{x^4}{4!} + \frac{x^5}{5!} + \cdots$$

For small values of $$x$$, we can approximate the series above as follows:

$$e^x \approx 1 + x + \frac{x^2}{2}$$

If we substitute $$x$$ by $$\frac{V_d}{nV_T}$$, then for small $$V_d$$, the I/V
curve now looks like this:

$$
I(V_d) \approx I_S[(\frac{V_d}{nV_T}) + \frac{1}{2}(\frac{V_d}{nV_T})^2]
$$

That's nice, but there's still a linear and a power-of-two term. Are there cases
where there's just the power-of-two term left? There is!

Here's what happens when the voltage across the diode is a sine wave with amplitude
$$V_p$$ and frequency $$f$$: $$V_d = V_p\cos(2\pi f)$$.

$$
\begin{align*}
I(V_d) &\approx I_S[(\frac{V_d}{nV_T}) + \frac{1}{2}(\frac{V_d}{nV_T})^2] \\
&\approx I_S\frac{V_p}{nV_T} \cos(2\pi f) +  \frac{I_S}{2}(\frac{V_p}{nV_T}\cos(2\pi f))^2 \\
&\approx I_S\frac{V_p}{nV_T} \cos(2\pi f) +  \frac{I_S}{2}(\frac{V_p}{nV_T})^2\frac{1 + \cos(2 \cdot 2\pi f)}{2} \\
&\approx I_S\frac{V_p}{nV_T} \cos(2\pi f) +  \frac{I_S}{4}(\frac{V_p}{nV_T})^2[1 + \cos(4\pi f)]\\
\end{align*}
$$

If we apply a low pass filter with a cutoff well below frequency $$f$$, then the equation above reduces to:

$$
I_{dc} = \frac{I_S}{4}[\frac{V_p}{nV_T}]^2
$$

Under the right conditions, **the current through the diode is proportional to the power of two of the 
amplitude of the sine wave.**

![Schematic with AC source, diode and RC filter](/assets/hp423a/diode_rc_schematic.png)

The quadratic approximation is not only heavily dependent on temperature, but
also on the silicon. You can buy 2 diodes of the same type, and keep them
at the same temperature, yet their I/V curves might still be shifted quite
a bit from each other. 

That's less of a problem when the diode is operating in the region above the threshold, 
the resistance is too low to matter, but subthreshold, the resistance will much higher, 
often higher than the resistance that's in series with the diode.

We'll soon get back to square law behavior.

A quick word about the threshold voltage: there is no exact value of the diode 
threshold voltage. Most textbooks talk about the minimum forward bias voltage 
that is required for a diode to start conducting current. But the I/V curve is 
a continuous exponential function. There isn't a clear point at which a diode
starts conducting. 

In general, the treshold levels for a silicon and germanium based diodes are
around 0.7V and 0.3V respectively. For a 
[Schottky diode](https://www.electronics-tutorials.ws/diode/schottky-diode.html), 
it's around 0.4V.

[![Spice simulation: AM wave with triangle envelope with detector output](/assets/hp423a/spice_detector_triangle.png)](/assets/hp423a/spice_detector_triangle.png)

# The HP 423A Crystal Detector

The HP 423A is a low-barrier Schottky diode detector. First mentioned in a November 1963 
edition of HP Journal, the HP 423A is old. The 
[Keysight product page](https://www.keysight.com/us/en/product/423A/coaxial-crystal-detector.html)
predictably lists it as obsolete, but they still sell a 
[423B](https://www.keysight.com/us/en/support/423B/low-barrier-schottky-diode-detector-10-mhz-to-12-4-ghz.html).

Going through the specs, there are a couple of differences: the 423A only sustains an input power of 
100mW (20dBm/6.3Vpp) vs 200mW (23dBm/8.9Vpp) for the B version. There are are also differences in output impedance, 
frequency response flatness, sensitivity levels, noise levels and so forth. But the supported
frequency range is the same, from 10MHz to 12GHz.

For my basic use, the input power limits are important, exceeding them of a prolonged time will 
damage the device, but the other characteristics don't matter a whole lot since I barely know what 
they mean to begin with. 

100mW/20dBm of power is pretty high for test and measurement equipment, and well above the 
the maximum 15dBm output of my sweep and signal generator.

Despite their differences, the [423B datasheet](https://www.keysight.com/us/en/assets/7018-06773/data-sheets/5952-8299.pdf)
explains the basics about how they work and some of its applications.

In their words:

> These general purpose components are widely used for CW and pulsed
> power detection, leveling of sweepers, and frequency response testing of other
> microwave components. These detectors do not require a dc bias and can be
> used with common oscilloscopes, thus their simplicity of operation and excellent
> broadband performance make them useful measurement accessories.

If they're so useful for measurements, then let's just cut to the chase and do exactly that.

# The Crystal Detector in Action

The setup below has the 8656A RF signal generator configured to generate a 100MHz
carrier waveform at a -20dBm power level. It's set to AM mode and expects an external
signal on its modulation input.  A 
[33120A signal generator ](/2023/01/01/HP33120A-Repair-Shutting-Down-the-Eye-of-Sauron.html)
is sending out 1 kHz 1Vpp sine wave to that input.

XXXX Setup XXXX

The sample rate of scope is way below the 100MHz carrier, but it shows the outline of a 
1kHz envelop of the AM signal very well:

XXX Screenshot is wrong. It's -10dBm instead of -20dBm! XXX

[![AM signal on scope](/assets/hp423a/am_waveform.png)](/assets/hp423a/am_waveform.png)
*Click to enlarge*

When we now connect the crystal detector to the output of the RF output. 

XXXX Setup showing the cyrstal detector plugged into the RF generator XXXX

The setup has the following equivalent schematic:

[![Measurement Setup 1](/assets/hp423a/measurement_setup1.png)](/assets/hp423a/measurement_setup1.png)

Since the crystal detector has a 50&#937; input impedance, the input impedance of channel 2 
of the scope is set to 1M&#937; to avoid having two 50&#937; loads on the RF source. The HP 423A operating manual 
lists a detector output impedance of <15k&#937;, shunted by 10pF. We'll get back to that 15k&#937; later, but
the capacitor in the schematic above is the one of 10pF.

In addition to the capacitor inside the detector itself, there's also the capacitance of the coax cable
between the detector and the scope. The one that I'm using is 7ft long. At ~30pF/ft, the cable alone
add another 210pF, which dwarfs the detector capacitance. Not for nothing, the operation manual has
following: 

> when using the crystal detector with an oscilloscope, and the waveshapes to be observed have rise
> times of less than 5us, the coaxial cable connecting to the oscilloscope and detector should be as
> short as possible and shunted with a resistor.

The reason they're talking about the rise time is that cable capacitance will be part of an RC 
low-pass filter that will dull the edges on an RF pulse at the input. This is important if you
want to use a crystal detector to check the slope of pulses that come out of a
pulse modulator, like 
[the HP 11720A that I wrote about earlier](/2023/05/06/HP-11720A-Pulse-Modulator.html).

Channel 1 of the scope, connected to the output of the detector, is also set to 
1M&#937; to avoid loading the output too much.  

The diode of the detector is in 'opposite' direction. This doesn't fundamentally change the operation, 
it will pass through the negative part of the incoming signal. This is the default configuration for 
many of these kind of dectectors, but HP/Keysight, also sell an option with the diode oriented the 
other way around.

Let's now see the result on the scope. The purple waveform is now the direct output of the 
signal generator, and the yellow is the one from the crystal detector. 

[![-20dBm AM signal and detector output on scope](/assets/hp423a/am_waveform_and_detector_-20dBm.png)](/assets/hp423a/am_waveform_and_detector_-20dBm.png)
*Click to enlarge*

As expected, the output of the detector is negative, a consequence of the diode pointing
to the left. 

The detected signal looks a bit like but is not quite a sine wave, and the smaller the envelope of the 
original signal, the less the detector output seems to follow the envelope. 

This is also expected. The oscilloscope cursor shows that an RF signal peak of &plusmn;53mV. The 
diode of the detector is operating in the square law region!

This becomes even clearer when we modulate the RF signal with a triangle waveform instead of
a sine wave: the detector output is now a parabola:

[![-20dBm AM triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_-20dBm.png)](/assets/hp423a/triangle_waveform_-20dBm.png)

In the current setup, the only resistor at the output of the detector is the 1M&#937; 
load of the oscilloscope. For low power Schottky diodes, the square law region
of a detector in such a configuration runs roughly until -20dBm/63mVpp, which is how I
have configured output level of the signal generator.

When I increase the output level of the signal generator to -10dBm/0.2Vpp, the output still looks curved 
close for the small signals, but it definitely looks more linear for higher values.

[![-10dBm AM triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_-10dBm.png)](/assets/hp423a/triangle_waveform_-10dBm.png)

Raising the output by 10dBm once more to 0dBm/0.63Vpp, and there's very little left of quadratic behavior.

[![0dBm AM triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_0dBm.png)](/assets/hp423a/triangle_waveform_0dBm.png)

*If -20dBm corresponds to 63mVpp, and -10dBm to 0.2Vpp, then why does the cursor on the scope
shots show a &#916;V of 104mV and 330mV? It's because the dBm to Vpp formula assumes
a fixed amplitude sine wave. In our case, the signal is amplitude modulated, so the peak signal
excursion is larger to compensate for times where the amplitude is lower.*

# Playing with the Detector Load 

Without a load resistor, or better, with a very weak load resistor of 1M&#937;, the square law
region of the detector goes from around -50dBm to around -20dBm. There's nothing much we can do about
the lower bound of -50dBm: below that you're essentially measuring noise. But it is possible to increase 
the square law region upwards to -10dBm, by adding a load resistor at the output of the detector.

[![Measurement Setup 2](/assets/hp423a/measurement_setup2.png)](/assets/hp423a/measurement_setup2.png)

HP 11523A is exactly that: "a matched load resistor for optimimum square characteristics". I've
measured the resistance to be 562&#937;. *I don't know which criterium is used to determine
value of the matched resistor, but I'll give it a try further below.*

![HP 423A detector with HP 11523A load resistor](/assets/hp423a/hp423a_hp11523a.jpg)

Here's what happens with our signal for the -10dBm case:

[![-10dBm AM with load resistor triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_-10dBm_RL.png)](/assets/hp423a/triangle_waveform_-10dBm_RL.png)

The detector output (yellow) is definitely quadratic again, but the amplitude of the detector 
output is much smaller as well. And the yellow line also has a weird kind of fuzziness.

**Smaller Output Voltage**

The reason for the smaller detector output is simple: reducing the value of load resistor has
shifted the voltage divider so that the diode has a larger share of the total input voltage.

$$V_{out} \propto \frac{R_{load}}{R_{load}+R_{diode}}$$

$$R_{diode}$$ is a moving target and depends on the voltage $$V_d$$, but we've reduced
$$R_{load}$$ from 1M&#937; to 562&#937;, a factor of more than 2000. The voltage ratio has 
definitely shifted toward the diode.

**Output Signal Fuziness**

If we change the vertical scale of the scope and switch the scope to peak detect mode, 
we can have a better look at the output signal:

[![-10dBm AM with load resistor triangle waveform and detector output on scope - zoomed](/assets/hp423a/triangle_waveform_-10dBm_RL_zoom.png)](/assets/hp423a/triangle_waveform_-10dBm_RL_zoom.png)

It's clear that there's a lot of variation on the detector signal output.

We can see what happen when we change the timebase of the scope from 200us, perfect to
observe the 1kHz amplitude modulated envelope, to 5ns, which is needed to observe the
100MHz RF carrier:

[![-10dBm AM with load resistor triangle waveform and detector output on scope - small timebase](/assets/hp423a/triangle_waveform_small_timebase.png)](/assets/hp423a/triangle_waveform_small_timebase.png)

By reducing the load from 1M&#937; to 562&#937;, we have dramatically changed the
time constant of the RC circuit that is formed by the capacitor inside the detector,
only 10pF, the capacitance of the coax cable that is connected to the detector, ~210pF,
and the load resistor.

With the 1M&#937; load, the time constant is around $$220\times10^{-12} \cdot 10^{6} = 220us$$,
way above the 10ns clock period of the 100MHz signal.  With the 562&#937; load, that number
reduces to $$220\times10^{-12} \cdot 562 = 123ns$$. That's still well above 10ns, but
keep in mind that the time constant is the time needed to discharge a capacitor by 63%.

In the waveform above, we're nowhere close to that, and the capacitance is only a rough guess
as well.

There are tradeoffs to be made when choosing a detector configuration:

* where do you want the square law region to end?
* what's the frequency of the AM modulated signal? 
* what's the frequency of the RF signal
* how much ripple on the detected signal is acceptable?

# Why Do We Want Square Law Behavior Anyway?

Square law behavior makes the detector react quadratically to the amplitude of
an RF signal. In most signal processing systems, non-linear behavior is something you want
to avoid at all cost, because it distorts the signal.

Yet it's clear from the operating manual, and most other crystal detector literature, that
square law behavior is often a feature.

That's because crystal detectors are often used to measure the power of an RF signal, and
$$P \sim V^2$$. If we operate the detector in the square law region and measure its output, 
the voltage that we get is proportional to the power of the signal.

Note that I wrote 'proportional', not 'equal', because of the aforementioned issue with
the square law formula of a diode: it's heavily dependent on temperature and silicon.

# Why Does the Load Resistor Shift the Square Law Region?

Here's a thing that I didn't get for the longest time: if the square law region of a crystal
detector runs up to -20dBm with a 1M&#937; load resistor, why does it shift upwards when you use 
a load resistor with a much lower value?

With a lower load resistor, the voltage across the diode will increase, not decrease, which
means that you'll much quicker reach the point where the diode I/V curve behaves
quadratically?

I had to run a couple of [ngspice](https://ngspice.sourceforge.io/) simulation before I figured
it out. I ran the simulations with a diode-resistor configuration and without an amplitude
modulated signal, but the conclusion is the same.

![Schematic diode and resistor](/assets/hp423a/diode_r_schematic.png)

When the source voltage is zero, the diode resistance will initially be very high (blocking) and 
thus the source voltage will be primarily over the diode. 

As the source voltage increases, the 
resistance of the diode will decrease. Since the resistance of the load resistor stays constant, 
the voltage ratio will shift from diode to the resistor. Since an increase in source voltage only 
gets applied partially over the diode, the current through the diode won't increase quadratically 
(square law), but less than that.

The extent by which this happens depends on the value of the load resistor.

When the load resistor is high, the resistance of the diode will quickly fall below the resistance 
of the diode. The current through the system won't follow square law at all and will soon be entirely 
linear.

When the load resistor is low, it will take much longer before the resistance of the diode becomes 
lower than the load resistance. The lower the load resistance, the longer current through the diode 
will follow (more or less) the theoretical diode I/V curve.

[![Voltage over diode for different load values](/assets/hp423a/voltage_over_diode.png)](/assets/hp423a/voltage_over_diode.png)

In the graph above, you can see the voltage over the diode. The bottom red line is for a 10k load 
resistance. The top brown line is the source input. You can see how right from the start, the voltage 
over the diode is already different than the input voltage, and as the input voltage increases, the 
voltage over the diode veers away in a non-linear way: the load resistor is getting an ever larger 
share of the input voltage. It takes a much longer time for this to happen with lower load
resistor values.

Here you can see how that affects the output voltage:

[![Output voltage for different load values](/assets/hp423a/output_voltage.png)](/assets/hp423a/output_voltage.png)

The lower the load resistor, the higher the $$V_{in}$$ needs to be before output curves
start to transition from clearly quadratic to mostly linear.

The markers along the yellow line show where that happens.

# Power Measurement with Crystal Detectors

Now that we know that crystal detectors are the key sensor for a class of RF power meter,
it's time to have a look at one of them: the HP 8484A. Another oldie that's now
obsolete, but its specifications are close to the 
[HP 8481D](https://www.keysight.com/us/en/product/8481D/diode-power-sensor-10-mhz-18-ghz.html), 
which is still for sale, for a whopping $2724. 

![HP 8481D diode power sensor](/assets/hp423a/hp8481d.jpg)

Here's the schematic of the 8484A:

[![HP 8484A schematic](/assets/hp423a/hp8484a_schematic.jpg)](/assets/hp423a/hp8484a_schematic.jpg)
*(Click to enlarge)*

Except for a DC-blocking capactor at the entrance, the schematic is exactly as one could expect:
a 53&#937; termination resistor[^2], the detection diode, and a capactor. The output of the detector
goes to chopper circuit that samples the detector value at a rate of 220Hz.

[^2]: Not quite 50&#937', but I think that's because the detector circuit itself adds a bit of
      load to the input as well.

[![HP 8484A schematic frontend](/assets/hp423a/hp8484a_schematic_frontend.jpg)](/assets/hp423a/hp8484a_schematic_frontend.jpg)

How does a power meter with the temperature and silicon dependency of the detector diode? 

The obvious option is to calibrate the sensor before making a measurement. 

HP 8484A and 8481D sensors plug into an HP 438A power meter. These meters are much cheaper than
the sensors. On a good day, you can find them for less than $100 on eBay, though mine is a John freebie.

![HP 438A front image](/assets/hp423a/hp438a_front.jpg)

In the center of the front panel, a 1mW/0dBm power reference is prominently featured, and there 
are also "ZERO", "CAL ADJ", and "CAL FACTOR" buttons. Before making a set of measurements,
you first have to calibrate the power sensor before, otherwise the results will be
all over the place.

But even calibration against the power reference is not enough. The reference output
frequency is fixed at 50MHz, but the output of a crystal detector changes for different
input frequencies, and the parameters of the diode I/V curve are silicon dependent. 
Each power sensor comes with their own calibration table. You have to manually enter 
the right calibration factor before measuring.

![HP 8484A frequency calibration table](/assets/hp423a/hp8484a_calibration_table.jpg)

Keysight has a large arsenal of RF power sensors with different frequency and
power ranges. The HP 8484A and 8481D sensors shall only be used for RF sources
with a maximum power level  of -20dBm. To calibrate those against a device like
the HP 438A, you always need to use an HP provided reference attenuator.

I don't have a power sensor yet for my HP 438A, but 
[Daniel Tufvesson](https://twitter.com/DanielTufvesson/status/1647545015764230144) 
has been hard at work at building one himself.

# Characterizing the Detector

To get a better feel of how the detector behaves, I decided to
do a bunch of measurements and measure the output voltage for different
frequency and power input combinations.

The setup was pretty straightforward: the Wiltron SG-1206/U sweep generator, used
in non-sweep mode, was used to drive the detector, and my HP 3478A 5 1/2 digit
benchtop multi-meter measured the output voltage.

I did a bunch of measurements the manual way, and ended up with the following
table:


I only did measurements for 1 frequency, and recorded only 1 sample. For a clearer
picture, you need to sweep over the full frequency range. I also wanted to multiple
measurements for each combination, to check the variation of the results.

Doing this manually gets boring real quick. It's the kind of the stuff is the kind of stuff that
screams to be automated.

# Controlling Everything with GPIB

I already have all the tools for an automated setup:

* equipment with a GPIB interface

    The sweep generator and the multi-meter both have it. GPIB is an old interface that
    is being replaced by USB and Ethernet on modern equipment, though even there it's
    often still included. But modern equipment is ridiculously expensive. Almost all
    my toys are old and only have a GPIB interface on them.

* A GPIB-to-USB interface dongle

    They're not cheap, but one dongle is sufficient to daisy-chain multiple devices
    together. Here are two blog posts that describe how to make them work with
    Linux.

* PyMeasure and/or instrument manuals

    The HP 3478A is supported by the PyMeasure library, which makes data extraction
    a breeze. The Wiltron does not have such supported, but the Appendix E of its
    operating manual has everything you need, and the commands to control the device
    are trivial.

In the end, these are all the code that's needed to configure the sweep generator
to send out a 500MHz signal with a -10dBm power level in F1 mode:

```python
import pyvisa

rm = pyvisa.ResourceManager()
swp_gen = rm.open_resource("GPIB::23")

swp_gen.write("F1500MH")
swp_gen.write("LVL-10DM")
```

And this is how to read back a DC voltage from the DMV:

```python
from pymeasure.instruments.hp import HP3478A

dmv = HP3478A("GPIB::7")

v = dmv.measure_DCV
```

It's really that simple!

# Recording Data in an Sqlite3 Database

In the past I've always done the obvious when recording data: store the result in a text file,
usually in CSV format so that it can be imported into a spreadsheet.

It's easy to do, but I kind of hate the fact that you get a directoy that's cluttered with
files.

In the past, I've read the [Appropriate Uses For SQLite](https://www.sqlite.org/whentouse.html)
article and using it for data analysis is one of the obvious use cases. It's kind of obvious to
store data in a database...

I've recently started doing exactly that. Python comes with a sqlite3 support library out of the
box, and I have a small template that I just modify for each of my data gather projects. Once
you have the template, the overhead of using sqlite is pretty much zero.

The database has only 2 tables:

* sessions

    A single session contains all of the data of measurement run. A session table contains
    a session ID, name, a description (optional).

* measurements

    A measurement record contains the ID of the session during which the data has been gathered,
    a time stamp, and the actual measurement data.

I create the database and its tables like this:

```python
def create_db(filename):
    conn=sqlite3.connect(filename)
    c = conn.cursor()
    c.execute('''
        create table if not exists sessions(
            [id]            integer primary key,
            [name]          text,
            [description]   text,
            [created]       text)
        ''')
    c.execute('''
        create table if not exists measurements(
            [id]            integer primary key,
            [session_id]    integer,
            [created]       integer,
            [freq]          real,
            [power_dbm]     real,
            [v]             real)
        ''')
    conn.commit()

    return conn
```

When the database already exists, the code above will open the existing one instead of overwriting
the old one.

Creating a new session is simple:

```python
def create_session(conn, name, description=''):
    sql = '''insert into sessions(name, description, created)
             values(?, ?, datetime('now'))'''

    c = conn.cursor()
    c.execute(sql, (name, description))
    conn.commit()

    return c.lastrowid
```

The function returns the session ID that is needed to associate a new measurement with a session.

Finally, this function records the data of a new measurement:

```python
def record_measurement(conn, session_id, freq, power_dbm, v):
    sql = '''insert into measurements(session_id, created, freq, power_dbm, v) values(?, datetime('now'), ?, ?, ?)'''

    c = conn.cursor()
    c.execute(sql, (session_id, freq, power_dbm, v))
    conn.commit()
```

For different setups, all I need to do is copy the code and change the freq, power_dbm, 
and v fields to whichever different types of data I'd like to store.

# Data Recording Loop

The actual data gather process is usually a bunch of nested loops. The actual
code can be found [here](https://github.com/tomverbeure/hp423a_workout/blob/7e34636d9b9e02f3885900a971deb834dda00f00/423a_workout.py#L49-L79), 
but it looks like this

```python
def freq_power_v_graph(conn, session_id, freq_values, power_levels, nr_samples):
    for f in freq_values_mhz:
        swp_gen.write(f"F1{f}MH")       # Set frequency

        for p in power_levels_dbm:
            swp_gen.write(f"LVL{p}DM")  # Set power level
            time.sleep(0.5)
            for i in range(0,nr_samples):
                time.sleep(0.2)
                v = dmv.measure_DCV
                print(f"Freq={f}MHz, Power={p}dBm -> {v}V")
                record_measurement(conn, session_id, f, p, v)
            print()

freq_values_mhz  = [ 10, 30, 50, 70, 100, 200, 500, 1000 ]
power_levels_dbm = [ -50. -40, -30, -20, -10 ]
freq_power_v_graph(conn, cur_session, freq_values_mhz, power_levels_dbm, 10)
```


# Extracting Data from the Database

Once recorded, analyzing the data is lightweight as well. If you don't know any SQL, fetching
the data is just a matter of modifying one template SQL statement. You can then use Python
to do the heavy lifting for you. Pandas is a popular choice for Python data analysis, but I
have no experience with it... yet.

I usually first try out the SQL queries usingn the sqlite command line. When I'm satsified that
it's doing what I want, I embed it into my Python post-processing script.

Here I'm fetching all the data of a single session:

```sql
tom@zen:~/projects/hp423a$ sqlite measurements.db
sqlite> .headers on
sqlite> select * from measurements where session_id=1 order by created limit 10;
id|session_id|created|freq|power_dbm|v
1|1|2023-04-22 04:20:09|10.0|-115.0|-7.6e-06
2|1|2023-04-22 04:20:10|10.0|-115.0|-7.4e-06
3|1|2023-04-22 04:20:11|10.0|-115.0|-5.7e-06
4|1|2023-04-22 04:20:12|10.0|-115.0|-5.6e-06
5|1|2023-04-22 04:20:13|10.0|-115.0|-5.4e-06
6|1|2023-04-22 04:20:13|10.0|-115.0|-6.7e-06
7|1|2023-04-22 04:20:14|10.0|-115.0|-6.7e-06
8|1|2023-04-22 04:20:15|10.0|-115.0|-4.4e-06
9|1|2023-04-22 04:20:16|10.0|-115.0|-4.4e-06
10|1|2023-04-22 04:20:17|10.0|-115.0|-5.1e-06
```

I'm using the time stamp to sort the data in measurement order. The `limit 10` should be removed 
from the Python script, of course!

The simplest way to execute this in a Python script is as follows:

```python
import sqlite3

conn = sqlite3.connect("measurements.db")
c = conn.cursor()
c.execute("select freq,power_dbm,v from measurements where session_id=1 order by created")
rows = c.fetchall()
for row in rows:
    (freq,power_dbm,v) = row
    print(freq,power_dbm,v)
```

```sh
tom@zen:~/projects/hp423a$ ./423a_process.py | head -10
10.0 -115.0 -7.6e-06
10.0 -115.0 -7.4e-06
10.0 -115.0 -5.7e-06
10.0 -115.0 -5.6e-06
10.0 -115.0 -5.4e-06
10.0 -115.0 -6.7e-06
10.0 -115.0 -6.7e-06
10.0 -115.0 -4.4e-06
10.0 -115.0 -4.4e-06
10.0 -115.0 -5.1e-06
```

Notice how there's a bit of manual effort involved to assign the right column to the
right Python variable. This is something the Pandas library automatically do for you, but
that's for a different blog post.

SQLite has a lot of data processing tools so that you don't even need to use
Python to further filter the data.

With this query, I only want power levels that are higher than -50dBm, I group all
measurements with the same frequency and power values, and average the voltages:

```python
sqlite> .mode column
sqlite> select freq,power_dbm,avg(v) as v_avg from measurements
   ...>     where session_id=1 and power_dbm>=-50
   ...>     group by freq,power_dbm order by created limit 10;
freq        power_dbm   v_avg     
----------  ----------  ----------
10.0        -50.0       -1.118e-05
10.0        -47.0       -1.89e-05 
10.0        -43.0       -3.636e-05
10.0        -40.0       -7.97e-05 
10.0        -37.0       -0.0001547
10.0        -33.0       -0.0003309
10.0        -30.0       -0.0007762
10.0        -27.0       -0.0015307
10.0        -23.0       -0.0032825
10.0        -20.0       -0.0073059
```

Instead of averaging all the voltages, you could remove outliers first by filtering out 
those measurements that fall outside a certain standard deviation. 

SQL is a powerful language. Advanced SQL users can come up with queries that are literally
a page long. If you haven't written any SQL queries before, it's well worth learning the
basics.

# Some Measurements on a Power Reference

Before going through a sweep with a signal generator, let's first check the results of a power 
reference. 

When I bought the Wiltron sweep generator, John gave me an HP 438A power meter in pristine
condition... for free.  It came without a power sensor, the most expensive part by far, but
stand-alone, working units go for $100+ on eBay.

The HP 438A has a 1.00mW 50MHz power reference output that's used to calibrate power sensors
before doing actual measurements. Remember that the diodes in a crystal detector are temperature
sensitive, this kind of calibration is something you're supposed to do before starting a bunch
of measurements.

![HP 438A front image](/assets/hp423a/hp438a_front.jpg)

None of my instruments are properly calibrated: the procedure would cost much more than their
cost, but something that's supposed to be a reference is better than nothing. 

Here's what the signal looks like on my scope, with the necessary 50&#937; termination.

![HP 438A power meter reference signal on the oscilloscope](/assets/hp423a/hp438a_power_ref_signal_50.png)

We're seeing a 607mV peak-to-peak signal. On a spectrum analyzer, the second and
third harmonics are 54db and 55db lower, so this is a clean enough sine wave. For those,
$$V_{rms} = V_{pp}/2\sqrt{2}$$, or 214mV. $$P=V_{rms}/50$$ which gives a power of 0.92mW.
The conversion from mW to dBm goes as follows: $$P_{(dBm)} = 10 \cdot log_{10}(P_{(mW)}/1mW)$$.
0.92mW corresponds to -0.36dBm. 

Meanwhile, my spectrum analyzer, another John special, sees a power level of -0.63dBm, but 
spectrum analyzers aren't usually not good at measuring power with great accuracy. (The number 
becomes -0.55dB which I increase the resolution BW one step.)

![HP 438A power meter reference signal on the spectrum analyzer](/assets/hp423a/hp438a_power_ref_r3273.png)

The [HP 438A Operating & Service Manual](https://xdevs.com/doc/HP_Agilent_Keysight/HP%20438A%20Operating%20&%20Service.pdf)
says that "the power reference oscillator is factory-adjusted to 1.0mW &#177;0.7%. There are
different parts that can create a wrong result: just swapping out 50&#937; BNC terminations
changed the measured voltage by 4mV. Being off by 8% is definitely too much. Chances are that
the power reference itself needs to be recalibrated.

Still, things are close enough for hobbyist power measurements.

Time to take a look at the output of the crystal detector when connected to the power reference.

Without any other devices connected, one first needs to decide the termination of the oscilloscope.
This will effectively be the load resistance that determines the extent by which the capacitor
behind the detection diode will be discharge after the input sine wave reaches its peak.

The coax cable behind the detector has a characteristic impedance of 50&#937;. When connecting
this cable to an oscilloscope, it's best to use a 50&#937; termination as well to avoid
reflections when the amplitude of the incoming RF signal changes rapidly. 

Here's what the manual says:

> When using the crystal detector with an oscilloscope, and the waveshapes to be observed
> have rise times of less than 5us, the coaxial cable connecting the oscilloscope and detector
> should be as short as possible and shunted with a resistor. Ideally, this resistor
> should be 50&#937; to terminate the coaxial cable properly. However, with 50&#937;
> resistance, the output video pulse may be too small to drive some oscilloscopes. Therefore,
> the cable should be shunted with the smallest value of resistance that will obtain suitable
> deflection on the oscilloscope; typically the value will lie between 50&#937; and
> 2k&#937;.

Keep in mind that the detector was released in 1963. Modern oscilloscope have no issue
whatsoever detecting a pulse 5us pulse with a 50&#937; termination!

Speaking of capacitor: the detector itself has a 10pF capacitor. The one at the oscilloscope
receiving end is 8pF. And the rest is the coax cable. When I use 9ft traditional coax cable
with a capacitance of ~30pF/ft, the capacitive load due to the coax is around 270: it dwarfs
everything else!

Here's what the signal looks like at the scope when using a 9ft coax cable and the 50&#937;
termination:

![HP 438A power reference measured by HP 423A on scope with 50Ohm termination](/assets/hp423a/hp438a_power_ref_ripple_50.png)

We're seeing the bottom half of the 50MHz sine wave. The capacitance at the detector side is too low
to filter output of a slow moving 50MHz input signal to a constant value that measures amplitude of the incoming signal.

Let's see what happen when we generate a 300MHz/0dBm signal with the sweep generator:

![Wiltron 300MHz/0dBm output measured by HP 423A on scope with 50Ohm termination](/assets/hp423a/wiltron_300MHz_0dBM_50.png)

I added the second, horizontal, line to show ground. We still have a huge 27mV ripple,
but at least the signal doesn't go all the way back to ground anymore.


# HP 423A characterization results

# HP 432A Craigslist Ad

 The HP 432A microwave power meter was first sold in the 1960's and lives on today as the N432A from Keysight. (The two products have nothing in common, other than they both use thermistor mount power sensors, such as the 478A). Keysight continues to make a thermistor compatible meter and 478A thermistor mount because it has become a transfer standard for calibrating other power meters. The combination of the over $13K meter and the $15K thermistor mount means this 432A is less than 2% of the new price!

The power measurement range of the 432A, using an HP 478A thermistor mount, is -20dBm to +10dBm and the frequency range is 10MHz to 10GHz.

Included with this 432A power meter is one 478A thermistor mount (shown) and one 5-foot cable that connects the meter to the 478A.

I bought this instrument about 25 years ago for a consulting project. I have used it very infrequently since that project was completed. The meter itself is in good condition but shows signs of age and usage. There is a small chip out of the meter bezel. The included 478A thermistor mount appears to have been frequently used. There seem to be two deficits: the remaining label has been "reduced in size" for some reason, and the calibration label is missing.

I recently spent a few days checking operation of the meter system. I don't have a power calibrator, but I do have an HP8663A frequency synthesizer and used its output as a standard. Before use, the 432A system must be "zeroed", which is a two-step process. The power range switch is set to the "Coarse Zero" position and a screwdriver is used to adjust the meter reading to zero. Next, the switch is set to the -20dBm range and the "Fine Zero" front panel switch is toggled for a few seconds. The meter will then show a zero reading. For the most stable "zero" adjustment the process should be performed only after the meter and thermistor mount have reached a stable temperature. However, the fine zero doesn't create a lot of error on higher power measurements.

Using a 100MHz output frequency, I measured the meter readings at about +10dBm, 0dBM, -10dBm and -20dBm. The sensor was attached directly to the 8663A output N connector to eliminate cable effects. All of the readings were approximately 0.5 dBm high. I swapped the thermistor mount for another one and got approximately the same results (correlation to less than 0.1dBm). To me, the data indicates the "error" is likely due to the 8663A source amplitude calibration.

# Reference

* [HP 423A and 8470A Crystal Detector - OPerating and Service Manual](/assets/hp423a/HP_423A,8470A_Operating_&_Service.pdf)
* [HP Journal Nov, 1963 - A New Coaxial Crystal Detector with Extremely Flat Frequency Response](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1963-11.pdf)

* [DIY Power Sensor for HP 436A and 438A](https://twitter.com/DanielTufvesson/status/1647545015764230144)

    * [Chopper And Chopper-Stabilised Amplifiers, What Are They All About Then?](https://hackaday.com/2018/02/27/chopper-and-chopper-stabilised-amplifiers-what-are-they-all-about-then/)

* [Infineon - RF and microwave power detection with Schottky diodes](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055)

* [Agilent AN980 - Square Law and Linear Detection](/assets/hp423a/an986-square_law_and_linear_detection.pdf)

    Interesting sections about diode equivalent resistance.

* [Square Law Detectors](https://www.nitehawk.com/rasmit/ras_appl6.pdf)
* [Wiltron - Operator's and Unit Maintenance Manual for SG-1206/U](https://radionerds.com/images/2/20/TM_11-6625-3231-12.PDF)
* [Analog Devices - Understanding, Operating, and Interfacing to Integrated Diode-Based RF Detectors](https://www.analog.com/en/technical-articles/integrated-diode-based-rf-detectors.html)
* [Diode Detector](https://analog.intgckts.com/rf-power-detector/diode-detector-2/)
* [Design and development of RF power detector for microwave application](https://www.semanticscholar.org/paper/Design-and-development-of-RF-power-detector-for-Ali-Ibrahim/fed809b8f38fe7d0ebc0ffdc9fd1a7da3ac93037)

* [HP AN 64-1A - Fundamentals of RF and Microwave Power Measurements](https://www.hpmemoryproject.org/an/pdf/an_64-1a.pdf)

    83 pages about RF power measurements. Goes over all the different techniques, benefits, 
    disadvantages, etc.

    Required reading to get up to speed.

* [6 Lines of Python to Plot SQLite Data](https://funprojects.blog/2021/12/27/6-lines-of-python-to-plot-sqlite-data/)

* [RF Diode Detector Measurement](https://twiki.ph.rhul.ac.uk/twiki/pub/PP/Public/JackTowlerLog1/diode.pdf)

* [Diode detectors for RF measurement Part 1: Rectifier circuits, theory and calculation procedures.](https://g3ynh.info/circuits/Diode_det.pdf)

    116 pages with everything you ever wanted to know about diode rectifiers.
    
* [RF Diode detector / AM demodulator](http://www.crystal-radio.eu/diodedetector/endiodedetector.htm)

* [HP RF & Microwave Measurement Symposium and Exhibition - Characteristics and Applications of Diode Detectors](https://xdevs.com/doc/HP/pub/Pratt_Diode_detectors.pdf)

    Excellent presentation that derives the math and talks about applications.

* [Aertech Industries - Crystal Detectors](https://www.prc68.com/I/Aertech.shtml#Crystal_Detector)

    Links to various detector patents.

* [Crystal Detector Calibration Program and Procedure](https://apps.dtic.mil/sti/pdfs/ADA523931.pdf)

* [Agilent 8473B/C Crystal Detector - Operating and Service Manual](https://xdevs.com/doc/HP_Agilent_Keysight/HP%208473%20Operating%20and%20Service.pdf)

    Interesting information about frequency response, SWR etc. 
    
* [Keysight - 415E SWR Meter](https://www.keysight.com/us/en/product/415E/swr-meter.html#resources)

* [The SPICE Diode Model](https://ltwiki.org/files/SPICEdiodeModel.pdf)

* [HP App Note 218-5: Obtaining Leveled Pulse-Modulated Microwave Signals from the HP 8672A](https://www.hpmemoryproject.org/an/pdf/an_218-5.pdf)

* [Low Barrier Schottky Diode BAT62 RF Power Detection](https://www.farnell.com/datasheets/2254436.pdf)

# Footnotes
