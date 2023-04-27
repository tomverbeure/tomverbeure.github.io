---
layout: post
title: Automated HP 423A Crystal Detector Characterization with GPIB and Sqlite3
date:   2023-04-19 00:00:00 -0700
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
stuff, read about it, play with it, ~~spend more money~~~, hope to learn useful things. 
I've found the playing part to be a crucial step of the whole process. Things seem to stick 
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
[a previous blog post](/2023/04/01/Cable-Length-Measurement-with-an-HP-8007B-Pulse-Generator.html), 
I wrote about John, my local RF equipment dealer. A while ago, he sold me a bargain Wiltron SG-1206/U 
programmable sweep generator that can send out a signal from 10MHz all the way to 20GHz at power levels 
between -115dBm to 15dBm. I also picked up a dirt cheap (and smelly) HP 8656A 1GHz signal generator at 
a previous flea market. I hadn't found a good use for either, so now was a good time to give them a 
little workout.

XXXX

![Wiltron SG-1206/U and HP 8656A signal generators](/assets/hp423a/...)

In the process of playing with the detector, I discovered the warts of both signal generators, 
I picked up an RF power meter on Craigslist, learned a truckload about RF power measurements and 
the general behavior of diodes and the math behind it, and figured out a misunderstanding about 
standing-wave ratio (SWR) and their relationship with crystal detectors.

I'm writing things down here to have a reference if I need the info back, but expect
the contents to be meandering between a bunch of topics.

# What is a Crystal Detector?

So what exactly is a crystal detector? [Wikipedia](https://en.wikipedia.org/wiki/Crystal_detector),
the caretaker of all human knowledge claims that 

> a crystal detector is an obsolete electronic component used in some early 20th century radio 
> receivers that consists of a piece of crystalline mineral which rectifies the alternating current 
> radio signal.

If they are obsolete, then why are plenty of companies still selling them? It's because 
Wikipedia is refering to the original crystal detectors that started it all: diodes that were 
built out of crystalline minerals, instead of contemporary diodes built out of silicon, germanium,
etc. Those early crystalline mineral diodes were one of the first semiconductor devices.

Today's RF crystal detectors are not fundamentally different.
[This Infineon application note](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055) 
describes how RF and microwave detectors are still built with a diode, a capacitor and a
load resistor. They now use low barrier Schottky diodes, but the name
*crystal* detector stuck.

![RF power detector with diode](/assets/hp423a/infineon_rf_power_detector.png)

Their functionality is straightforward: the diode passes only one side, positive or positive, 
of an RF signal though to the other side, a capacitor gets charged up to the peak level of the 
signal but discharges, slowly, due to a load resistor. If all went well, the output voltage of 
the detector is the envelope of the RF signal. 

![Amplitude modulation detection](/assets/hp423a/Amplitude_modulation_detection.png)

This envelope output signal is called the *video signal*, a bit of a confusing name:
the output signal may not have anything to do with video at all, but you better get used to it
because it's a standard term in the world of RF. Even cheap spectrum analyzers, such a 
[TinyVNA Ultra](https://tinysa.org/wiki/pmwiki.php?n=TinySA4.MenuTree) have a menu to change 
VBW, the video bandwidth.

In the early years, crystal detectors where used to build AM radio receivers. As a kid, 
I used to own this RadioShack 150-in-1 kit, and one of the projects was exactly that:
an AM radio crystal radio.

Link to 150-in-1 radio shack kit: https://commons.wikimedia.org/wiki/File:Science_Fair_150in1_Electronic_Project_Kit.jpg

The schematic is very simple: 

XXXX Page 53 contains the schematic: https://www.zpag.net/Electroniques/Kit/200_manual.pdf

On the left, a transformer and a variable capacitor create an LC tuning network to select
the radio station. A germanium diode does the detection, with a 22K&#937; load resistor.
There is no capacitor accross the load resistor. I think that the components downstream
filter out the RF carrier...

AM radios have long ago moved on from crystal detectors to better things. Modern demodulators 
mix (multiply) the incoming signal with a locally generated RF sine wave which makes the original 
LF signal emerge. 

It's not 100% clear to me if crystal detectors are currently still being
used to demodulate other types of AM content. When you google for crystal detectors
today, most hits will talk about using them for power measurement.

# Diode Square Law Behavior

A little bit of theory about diodes now will go a long way in understand what comes next.

A diode is often simplified to a device that blocks current when the voltage
across its junction is less than a certain threshold level, and that passes current
otherwise. Such an ideal device has the following voltage to current graph:

XXXXX

In this ideal case, an infinite current for any voltage above the threshold would
destroy the diode, but in practice, there's always some kind of series resistance to
limit the current. Together, the diode and this resistance form a voltage divider.

When the diode is ideal, the infinite current characterstic simply means that the 
voltage across the diode will always be limited to the threshold voltage, and that
the remainder of the diode/resistance combo will fall over the resistance.

In other words, when place in series with a fixed value resistor, the current
through the diode and the resistor will be:

$$I_{R} = (V_{in}-V_{th})/R$$

And the voltage across the resistor will be:

$$V_{R} = I_{R} \cdot R = V_{in}-V_{th}$$

In reality, voltage/current curve can be described with the following formula:

$$I = I_0(e^\frac{qV}{nkT}-1)$$

*The formula above does not model diode breakdown: the often destructive behavior that
happens when the junction voltage exceeds a certain negative value.*

There are a bunch of factors in there

* $$I_0$$ is the diode leakage current density in the absence of light. 
* $$T$$ is the absolute temperature.
* $$V$$ is the junction voltage, the voltage across the diode terminals.
* $$k$ is Boltzmann's constant
* $$q$$ is the charge of an electron
* $$n$$ is an ideality factor between 1 and 2 that typically increases when the current decreases.

Note that $$I_0$$ itself is temperature dependent as well!

The [Diode Equation](https://www.pveducation.org/pvcdrom/pn-junctions/diode-equation)
goes into more detail about diode behavior. It even has some interactive graphs to
play with.


Here's what such a graph typically looks like:

https://www.desmos.com/calculator/n9uo7irghk

There's a characteristic knee in the graph above which the current starts going up 
rapidly. In the graph above, the knee is somewhere around a value of $$x=0.7V$$.

Below the knee, when $$x>0$$, it's possible to approximate the curve with a
quadratic polynomial:

https://www.desmos.com/calculator/8jyd1jaqmr

That's the square law region of the diode.

When places in series with a resistors, the 

# The HP 423A Crystal Detector

First mentioned in a November 1963 edition of HP Journal, the HP 423A is old. The 
[Keysight product page](https://www.keysight.com/us/en/product/423A/coaxial-crystal-detector.html)
predictably lists it as obsolete, but Keysight sells a 
[423B](https://www.keysight.com/us/en/support/423B/low-barrier-schottky-diode-detector-10-mhz-to-12-4-ghz.html).

Going through the specs, there are a couple of differences: the 423A only sustains an input power of 
100mW (20dBm) vs 200mW (23dBm) for the B version. There are are also differences in output impedance, 
frequency response flatness, sensitivity levels, noise levels and so forth. But the supported
frequency range is the same, from 10MHz to 12GHz.

For my basic use, the input power limits are important, exceeding them of a prolonged time will 
damage the device, but the other characteristics don't matter a whole lot since I barely know what 
they mean to begin with. 

100mW/20dBm of power is pretty high for test and measurement equipment, and well above the 
the maximum 15dBm output of the sweep and signal generator.

Despite the differences, the [423B datasheet](https://www.keysight.com/us/en/assets/7018-06773/data-sheets/5952-8299.pdf)
and other documentation that explains the basics about how they work and some of its applications.

In their words:

> These general purpose components are widely used for CW and pulsed
> power detection, leveling of sweepers, and frequency response testing of other
> microwave components. These detectors do not require a dc bias and can be
> used with common oscilloscopes, thus their simplicity of operation and excellent
> broadband performance make them useful measurement accessories.

If they're so useful for measurements, then let's just get on with ti and do exactly that.

# The Crystal Detector in Action

The setup below has the 8656A RF signal generator configured to generate a 100MHz
carrier waveform at a -10dBm power level. It's set to AM mode, expecting an external
signal as modulation signal.

A [33120A signal generator ](/2023/01/01/HP33120A-Repair-Shutting-Down-the-Eye-of-Sauron.html)
is sending out 1 kHz 1Vpp sine wave that is sent to the modulation input.

The scope is configured in peak detect mode and indeed shows the
outline of a high-frequency signal with 1kHz envelope: 

[![AM signal on scope](/assets/hp423a/am_waveform.png)](/assets/hp423a/am_waveform.png)
*Click to enlarge*

When we now connect the crystal detector to the output of the RF output, we get a setup with
the following equivalent schematic:

[![Measurement Setup 1](/assets/hp423a/measurement_setup1.png)](/assets/hp423a/measurement_setup1.png)

The crystal detector has a 50&#937; input impedance, so we need to set the input impedance of channel 2 
of the scope to 1M to avoid having two 50&#937; loads on the RF source. The HP 423A operating manual 
lists an output impedance of <15k&#937;, shunted by 10pF. We'll get back to that 15k&#937; later, but
the capacitor in the schematic above is the one of 30pF.

In addition to the capacitor inside the detector itself, there's also the capacitance of the coax cable
between the detector and the scope. The one that I'm using is 7ft long. At ~30pF/ft, the cable alone
add another 210pF, which dwarfs the detector capacitance. Not for nothing, the operation manual has
following: 

> when using the crystal detector with an oscilloscope, and the waveshapes to be observed have rise
> times of less than 5us, the coaxial cable connecting to the oscilloscope and detector should be as
> short as possible and shunted with a resistor.

The reason they're bringing up the rise time is that cable capacitance will be part of an RC 
low-pass filter that will dull the edges on an RF pulse at the input.

For now, channel 1 of the scope, connected to the output of the detector, is also set to 
1M&#937; to avoid loading the output too much.  

The diode of the detector is in 'opposite' direction. This doesn't fundamentally change the operation, 
it's just that it will pass through the negative part of the incoming signal. For some reason,
that's the default configuration for many of these kind of dectectors. HP, and currently Keysight,
also sell an option with the diode oriented the other way around.

Let's now see the result on the scope:

The purple waveform is now the direct output of the signal generator, and
the yellow is the one from the crystal detector. 

[![-20dBm AM signal and detector output on scope](/assets/hp423a/am_waveform_and_detector_-20dBm.png)](/assets/hp423a/am_waveform_and_detector_-20dBm.png)
*Click to enlarge*

As expected, the output of the detector is negative, a consequence of the diode pointing
to the left. 

The detected signal looks a bit like but is not quite a sine wave, and the smaller the envelope of the 
original signal, the less the detector output seems to follow the envelope. 

This is also expected. Notice that the RF peak of the signal is &plusmn;53mV. The diode of the 
detector is operating in the so-called square law region, where detector has a quadratic I/V response
curve!

This becomes even clearer when we modulate the RF signal with a triangle waveform:

[![-20dBm AM triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_-20dBm.png)](/assets/hp423a/triangle_waveform_-20dBm.png)

In the current setup, the only resistor at the output of the detector is the 1M&#937; 
load of the oscilloscope. For low power Schottky diodes, the square wave region
of a detector in such a configuration runs roughly until -20dBm, which is how I
have configured output level of the signal generator.

If I configure the signal generator to output -10dBm, the output still looks curved close for
the small signals, but it definitely looks more linear for higher values.

[![-10dBm AM triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_-10dBm.png)](/assets/hp423a/triangle_waveform_-10dBm.png)

Raising the output by 10dBm once more to 0dBm, and there's very little left of quadratic behavior.

[![0dBm AM triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_0dBm.png)](/assets/hp423a/triangle_waveform_0dBm.png)

# Playing with the Detector Load 

Without a load resistor (or better: with a very weak load resistor of 1M&#937;), the square law
region of the detector goes from around -50dBm to around -20dBm. There's nothing much we can do about
the -50dBm: below that you're essentially measuring noise. But it is possible to increase the region
upwards to -10dBm, but adding a load resistors at the output of the detector.

[![Measurement Setup 2](/assets/hp423a/measurement_setup2.png)](/assets/hp423a/measurement_setup2.png)

HP 11523A is exactly that: "a matched load resistor for optimimum square characteristics". I've
measured the resistance to be 562&#937;.

XXXX Picture of detector with load resistor

Here's what happens with our signal for the -10dBm case:

[![-10dBm AM with load resistor triangle waveform and detector output on scope](/assets/hp423a/triangle_waveform_-10dBm_RL.png)](/assets/hp423a/triangle_waveform_-10dBm_RL.png)

The yellow detector output is definitely quadratic again, but that's not the only thing.

The amplitude of the detector output is much smaller. And the yellow line also has a weird
kind of fuzziness.

**Smaller Output Voltage**

The reason for the smaller detector output is simple: the diode may not be a resistor, but
for a given junction voltage, it will have a corresponding current. The ratio of that voltage
and current is an equivalent resistance. That resistance is not constant, it changes whenever
the junction voltage changes, but it's there. In the square law region, this resistance is
on the order of 10k&#937;, with a very large variation around it!

In combination with a load resistor, these resistance forms a voltage divider. When the only
load is the 1M&#937; of the oscilloscope, 99% of the voltage of the detector is measured
by the oscilloscope. The addition of the 562&#937; load resistor shifts the voltage divider
in the other direction, with the voltage across the divider primarily going to the diode.

**Output Signal Fuziness**

If we change the vertical scale of the scope, we can have a better look at the output signal:

[![-10dBm AM with load resistor triangle waveform and detector output on scope - zoomed](/assets/hp423a/triangle_waveform_-10dBm_RL_zoom.png)](/assets/hp423a/triangle_waveform_-10dBm_RL_zoom.png)

The scope is in peak detect mode, and it's clear that the output isn't very clean.

We can see what happen when we change the timebase of the scope from 200us, perfect to
observe the 1kHz amplitude modulated envelope, to 5ns, which is needed to observe the
100MHz RF carrier:

[![-10dBm AM with load resistor triangle waveform and detector output on scope - small timebase](/assets/hp423a/triangle_waveform_small_timebase.png)](/assets/hp423a/triangle_waveform_small_timebase.png)

By reducing the load from 1M&#937; to 562&#937;, we have dramatically changes the
time constant of the RC circuit that is formed by the capacitor inside the detector,
only 30pF, the capacitance of the coax cable that is connected to the detector, ~210pF,
and the load.

With the 1M&#937; load, the time constant is around $$240\times10^{-12} \cdot 10^{6} = 240us$$,
miles above the 10ns clock period of the 100MHz signal.  With the 562&#937; load, that number
reduces to $$240\times10^{-12} \cdot 562 = 134ns$$. That's still well above 10ns, but
keep in mind that the time constant is the time needed to discharge a capacitor by 63%.

In the waveform above, we're nowhere close to that, and the capacitance is a rough guess
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

That's because crystal detector are often used to measure the power of an RF signal, and
$$P \sim V^2$$. In other words, if we operate the detector in the square law region and
measure its output, the voltage that we get is proportional to the power of the signal.

Note that I wrote 'proportional', not 'equal'. That's because the behavior of a diode
in the square law region is not only heavily temperature dependent, it also differs
from one diode to the next.

There are different ways to deal with this. The most common option is to calibrate 
a square law power sensor before making a measurement. I have an HP 438A power meter,
another John freebie, without power sensor. 

In the center of the front panel, it prominently features a 1mW power reference. There
are also "ZERO", "CAL ADJ", and "CAL FACTOR" buttons. Before making a set of measurements,
you first have to calibrate the power sensor before, otherwise the results can be
all over the place.


# Characterizing the Detector

To get a better feel of how the detector behaves, I decided to
do a bunch of measurements and measure the output voltage for different
frequency and power input combinations.

The setup was pretty straightforward: the Wiltron SG... sweep generator, used
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

XXX

![HP 438A front image](/assets/hp423a/...)

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

# Footnotes
