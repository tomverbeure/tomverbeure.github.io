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

I picked up some random RF gizmos at the [Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com/).
It's part of the grand plan to elevate my RF knowledge from near zero to beginner level: buy
stuff, read about it, play with it, hope to learn useful things. I've found the
playing part to be a crucial step of the whole process. Things seem to stick much
better in my brain when all is said and done.[^1] 

[^1]: Writing blog posts about it is equally helpful too!

In this blog post, I'm taking a closer look at this contraption:

![HP 423A](/assets/hp423a/hp423a.jpg)

It's an HP 423A crystal detector. According to the
[operating and service manual](/assets/hp423a/HP_423A,8470A_Operating_&_Service.pdf):

> \[the 423A crystal detector\] is a 50&#937; device designed for measurement use in coaxial systems. The 
> instrument converts RF power levels applied to the 50&#937; input connector into proportional values
> of DC voltage. ... The frequency range of the 423A is 10MHz to 12.4GHz.

In the  introduction of [a previous blog post](/2023/04/01/Cable-Length-Measurement-with-an-HP-8007B-Pulse-Generator.html), 
I wrote about John, my local RF equipment dealer. A while ago, he sold me a bargain Wiltron SG-1206/U 
programmable sweep generator that can send out a signal from 10MHz all the way to 20GHz at power levels 
between -115dBm to 15dBm. I also picked up a dirt cheap (and smelly) HP 8656A 1GHz signal generator at 
a previous flea market. I hadn't found a good use for either, so now was a good time to give them a little workout.

XXXX

![Wiltron SG-1206/U and HP 8656A signal generators](/assets/hp423a/...)


In the process, I discovered the warts of both signal generators, picked up an RF power meter
on Craigslist, learned a truckload about RF power measurements and the general behavior of diodes,
and figured out a misunderstanding about standing-wave ratio and their relationship with crystal
detectors.

I'm writing things down here to have a reference if I need the info back, but expect
the contents to be meandering between a bunch of topics.

# What is a Crystal Detector?

So what exactly is a crystal detector?  [Wikipedia](https://en.wikipedia.org/wiki/Crystal_detector),
the holder of all human knowledge claim that 

> a crystal detector is an obsolete electronic component used in some early 20th century radio 
> receivers that consists of a piece of crystalline mineral which rectifies the alternating current 
> radio signal.

If they are obsolete, then why are plenty of companies still selling them? It's because 
Wikipedia is refering to the crystal detectors that started it all: diodes that were 
built out of crystalline minerals, instead of contemporary diodes built out of silicon, germanium,
etc. Those early crystalline mineral diodes were one of the first semiconductor devices.

Today's RF crystal detectors are not fundamentally different.
[This Infineon application note](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055) 
describes how RF and microwave detectors are still built with a diode, a capacitor and a
load resistor. They now use low barrier Schottky diodes, but the name
*crystal* detector stuck.

![RF power detector with diode](/assets/hp423a/infineon_rf_power_detector.png)

The functionality is straightforward: the diode makes only the positive side of an RF signal pass 
through, the capacitor gets charged up to the peak level of the signal but discharges (slowly) due
to the load resistor. If all went well, the output voltage of the detector is the envelope of the 
RF signal. 

![Amplitude modulation detection](/assets/hp423a/Amplitude_modulation_detection.png)

This envelope output signal is called the *video signal*. It's a bit of a confusing name:
the output signal may not have anything to do with video at all, but you better get used to it
because it's a standard term in the world of RF: even cheap spectrum analyzers,
such a [TinyVNA Ultra](https://tinysa.org/wiki/pmwiki.php?n=TinySA4.MenuTree) have a
menu to change VBW, the video bandwidth.

One could use an RF crystal detector to build an AM radio receiver

# The HP 423A Crystal Detector

Born in 1976, the [Keysight product page](https://www.keysight.com/us/en/product/423A/coaxial-crystal-detector.html)
predictably lists the 423A as obsolete, but it sells a [423B](https://www.keysight.com/us/en/support/423B/low-barrier-schottky-diode-detector-10-mhz-to-12-4-ghz.html).
Going through the specs, there are a couple of differences: the 423A only sustains an input power of 100mW vs 200mW for the B version.
There are are also differences in output impedance, frequency response flatness, sensitivity
levels, noise levels and so forth. For my use, the input power limits are important, because exceeding
them would damage the device, but the other values don't matter a whole lot since I
barely know what they mean to begin with. 

100mW of power is pretty high for test and measurement equipment. It corresponds to 20dBm, well
above the maximum 15dBm output of the sweep generator.

What's nice about the 423B is that its [datasheet](https://www.keysight.com/us/en/assets/7018-06773/data-sheets/5952-8299.pdf)
explains the basics about how they work and some of its applications.

In their words:

> These general purpose components are widely used for CW and pulsed
> power detection, leveling of sweepers, and frequency response testing of other
> microwave components. These detectors do not require a dc bias and can be
> used with common oscilloscopes, thus their simplicity of operation and excellent
> broadband performance make them useful measurement accessories.

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

* [HP Journal Nov, 1963 - A New Coaxial Crystal Detector with Extremely Flat Frequency Response](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1963-11.pdf)
* [DIY Power Sensor for HP 436A and 438A](https://twitter.com/DanielTufvesson/status/1647545015764230144)

    * [Chopper And Chopper-Stabilised Amplifiers, What Are They All About Then?](https://hackaday.com/2018/02/27/chopper-and-chopper-stabilised-amplifiers-what-are-they-all-about-then/)

* [Infineon - RF and microwave power detection with Schottky diodes](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055)
* [Agilent AN980 - Square Law and Linear Detection](/assets/hp423a/an986-square_law_and_linear_detection.pdf)
* [Square Law Detectors](https://www.nitehawk.com/rasmit/ras_appl6.pdf)
* [Wiltron - Operator's and Unit Maintenance Manual for SG-1206/U](https://radionerds.com/images/2/20/TM_11-6625-3231-12.PDF)
* [Analog Devices - Understanding, Operating, and Interfacing to Integrated Diode-Based RF Detectors](https://www.analog.com/en/technical-articles/integrated-diode-based-rf-detectors.html)
* [Diode Detector](https://analog.intgckts.com/rf-power-detector/diode-detector-2/)
* [Design and development of RF power detector for microwave application](https://www.semanticscholar.org/paper/Design-and-development-of-RF-power-detector-for-Ali-Ibrahim/fed809b8f38fe7d0ebc0ffdc9fd1a7da3ac93037)
* [HP AN 64-1A - Fundamentals of RF and Microwave Power Measurements](https://www.hpmemoryproject.org/an/pdf/an_64-1a.pdf)

* [6 Lines of Python to Plot SQLite Data](https://funprojects.blog/2021/12/27/6-lines-of-python-to-plot-sqlite-data/)

* [RF Diode Detector Measurement](https://twiki.ph.rhul.ac.uk/twiki/pub/PP/Public/JackTowlerLog1/diode.pdf)

* [Diode detectors for RF measurement Part 1: Rectifier circuits, theory and calculation procedures.](https://g3ynh.info/circuits/Diode_det.pdf)

    116 pages with everything you ever wanted to know about diode rectifiers.
    

# Footnotes
