---
layout: post
title: Automated Crystal Detector Characterization with GPIB and Sqlite3
date:   2023-06-03 00:00:00 -1000
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

In my previous blog post, I wrote about RF crystal detectors, how they work, and how
they are used, among other things, to measure RF power.

To get a better feel of how the detector behaves under different conditions, I decided 
do a bunch of measurements for different frequency and power combinations, and see
how that changes the output voltage of the crystal detector.

# Characterizing the Detector

The setup is pretty straightforward: a newly acquired Rohde & Schwarz SHMU signal generator, 
to drive the detector, and my HP 3478A 5 1/2 digit benchtop multi-meter measured the output 
voltage. I decided on the Rohde & Schwarz instead of the HP 8656A because it's a much
younger device for which the power was calibrated as recently as 1998, which is practically
yesterday. I don't quite trust the RF power output of the HP 8656a...  

I first did a bunch of measurements the manual way, and ended up with the following
table:

Here I only did measurements for 1 frequency, and recorded only 1 sample. For a clearer
picture, you need to sweep over the full frequency range. I also wanted to do multiple
measurements for each combination, to check the variation of the results.

Doing this manually gets boring real quick. It's the kind of the stuff is the kind of stuff that
screams to be automated.

# Controlling Everything with GPIB

I already have all the tools for an automated setup:

* equipment with a GPIB interface

    The signal generator and the multi-meter both have it. GPIB is an old interface that
    is being replaced by USB and Ethernet on modern equipment, but even for those it's
    often still included. Since modern equipment is ridiculously expensive, almost all
    my toys are old and only have a GPIB interface on them.

* A GPIB-to-USB interface dongle

    They're not cheap, but one dongle is sufficient to daisy-chain multiple devices
    together. Here are two blog posts that describe how to make them work with
    Linux.

* PyMeasure and/or instrument manuals

    The HP 3478A is supported by the PyMeasure library, which makes data extraction
    a breeze. The SMHU does not have such support, but section 2.4 of its
    operating manual has everything you need, and the commands to control the device
    are trivial.

In the end, this are all the code that's needed to configure the function generator
to send out a 500MHz signal with a -10dBm power level:

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
article and using it for data analysis is one of the state use cases. It just makes
sense to store data in a database...

So I've recently started doing exactly that. Python comes with a sqlite3 support library out of the
box, and I have a small template that I just modify for each of my data gathering projects. Once
you have the template, the overhead of using sqlite is pretty much zero.

The database has only 2 tables:

* sessions

    A single session contains all of the data of measurement run. A session table contains
    a session ID, name, an optional description.

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

When the database already exists, the code above opens the existing one instead of overwriting
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

For different setups, I just copy the code above and change the freq, power_dbm, 
and v fields to whichever different types of data I'd like to store. 

*I could make things fancier by refactoring this kind of code into a library 
that can be reused later, but the boilerplate code is so small that I'd rather not.*

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

Here's a video of the system in action:

XXX

# Extracting Data from the Database

Once recorded, analyzing the data is lightweight as well. Even if you don't know any SQL, 
fetching the data is a matter of modifying one template SQL statement. You can then use 
Python to do the heavy lifting for you. Pandas is a popular choice for Python data analysis, 
but I have no experience with it... yet.

I usually first try out the SQL queries using the sqlite command line. When I'm satsified that
it's doing what I want, I embed the query into a Python post-processing script.

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

I'm using the time stamp to sort the data in measurement order. The `limit 10` is there
to avoid an avalanche of data on my screen. It should be removed from the Python script.

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
right Python variable: 

```python
    ...
    (freq,power_dbm,v) = row
    ...
```

This is something the Pandas library will automatically do for you, but
that's for a different blog post.

SQLite has a some of data processing function so that you don't even need to use
Python to further filter the data. Even if it doesn't have the function
that you need, a standard deviation function is sadly missing, you can expand
Sqlite by adding custom functions yourself.

In the query below, I only want measurement result for power levels that are higher 
than -50dBm, I then group all measurements with the same frequency and power values, and,
finally, I average these voltages:

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

This [Stackoverflow question](https://stackoverflow.com/a/24423341/188899) shows how
to define an stdev function. After this, you can call it like an other aggregation
function:

XXXX

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

Let's see what happens when we generate a 300MHz/0dBm signal with the sweep generator:

![Wiltron 300MHz/0dBm output measured by HP 423A on scope with 50Ohm termination](/assets/hp423a/wiltron_300MHz_0dBM_50.png)

I added the second, horizontal, line to show ground. We still have a huge 27mV ripple,
but at least the signal doesn't go all the way back to ground anymore.


# HP 423A characterization results

# HP 432A Craigslist Ad

The HP 432A microwave power meter was first sold in the 1960's and lives on today as the N432A from Keysight. 
(The two products have nothing in common, other than they both use thermistor mount power sensors, such as the 478A). 
Keysight continues to make a thermistor compatible meter and 478A thermistor mount because it has become a transfer 
standard for calibrating other power meters. The combination of the over $13K meter and the $15K thermistor mount 
means this 432A is less than 2% of the new price!

The power measurement range of the 432A, using an HP 478A thermistor mount, is -20dBm to +10dBm and the frequency 
range is 10MHz to 10GHz.

Included with this 432A power meter is one 478A thermistor mount (shown) and one 5-foot cable that connects the 
meter to the 478A.

I bought this instrument about 25 years ago for a consulting project. I have used it very infrequently since that 
project was completed. The meter itself is in good condition but shows signs of age and usage. There is a small 
chip out of the meter bezel. The included 478A thermistor mount appears to have been frequently used. There seem 
to be two deficits: the remaining label has been "reduced in size" for some reason, and the calibration label is missing.

I recently spent a few days checking operation of the meter system. I don't have a power calibrator, but I do have 
an HP8663A frequency synthesizer and used its output as a standard. Before use, the 432A system must be "zeroed", 
which is a two-step process. The power range switch is set to the "Coarse Zero" position and a screwdriver is used 
to adjust the meter reading to zero. Next, the switch is set to the -20dBm range and the "Fine Zero" front panel 
switch is toggled for a few seconds. The meter will then show a zero reading. For the most stable "zero" adjustment 
the process should be performed only after the meter and thermistor mount have reached a stable temperature. However, 
the fine zero doesn't create a lot of error on higher power measurements.

Using a 100MHz output frequency, I measured the meter readings at about +10dBm, 0dBM, -10dBm and -20dBm. The sensor 
was attached directly to the 8663A output N connector to eliminate cable effects. All of the readings were approximately 
0.5 dBm high. I swapped the thermistor mount for another one and got approximately the same results (correlation to less 
than 0.1dBm). To me, the data indicates the "error" is likely due to the 8663A source amplitude calibration.

# Reference

* [6 Lines of Python to Plot SQLite Data](https://funprojects.blog/2021/12/27/6-lines-of-python-to-plot-sqlite-data/)

* [RF Diode Detector Measurement](https://twiki.ph.rhul.ac.uk/twiki/pub/PP/Public/JackTowlerLog1/diode.pdf)

* [Aertech Industries - Crystal Detectors](https://www.prc68.com/I/Aertech.shtml#Crystal_Detector)

    Links to various detector patents.


# Footnotes
