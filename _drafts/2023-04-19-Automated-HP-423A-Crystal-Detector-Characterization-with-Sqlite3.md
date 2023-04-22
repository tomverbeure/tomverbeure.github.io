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

In my introduction of previous blog post, I wrote about John, my local RF equipment dealer. 
A while ago, he sold me a bargain Wiltron SG-1206/U programmable sweep generator that can send 
out a signal from 10MHz all the way to 20GHz at power levels between -115dBm to 15dBm. I hadn't
found a good use for it, so now was a good time to give it a little workout.

# What is a Crystal Detector?

According to [Wikipedia](https://en.wikipedia.org/wiki/Crystal_detector), a crystal detector is an 
obsolete electronic component used in some early 20th century radio receivers that consists of a piece 
of crystalline mineral which rectifies the alternating current radio signal.

As noted in the article, those crystalline minerals were first type of semiconductor diode.

RF crystal detectors are no different.
[This Infineon application note](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055) describes how RF microwave power detectors are built with low barrier Schottky diodes,
with the following diagram:

![RF power detector with diode](/assets/hp423a/infineon_rf_power_detector.png)

The functionality is straightforward: the diode makes only the positive side of an RF signal pass 
through, the capacitor gets charged up to the peak level of the signal but discharges (slowly) due
to the load resistor. The output voltage of the detector is nothing but the envelope of the RF signal.

![Amplitude modulation detection](/assets/hp423a/Amplitude_modulation_detection.png)

One could use an RF crystal detector to build an AM receiver.

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
right Python variable.

This can be avoided by using the Pandas library, which designed for this kind of
tasks, and much more:

```python3
import sqlite3
import pandas as pd

conn = sqlite3.connect("measurements.db")
df = pd.read_sql_query("select * from measurements where session_id=1 order by created", conn)
print(df)
```

```sh
tom@zen:~/projects/hp423a$ ./423a_process.py
        id  session_id              created    freq  power_dbm         v
0        1           1  2023-04-22 04:20:09    10.0     -115.0 -0.000008
1        2           1  2023-04-22 04:20:10    10.0     -115.0 -0.000007
2        3           1  2023-04-22 04:20:11    10.0     -115.0 -0.000006
3        4           1  2023-04-22 04:20:12    10.0     -115.0 -0.000006
4        5           1  2023-04-22 04:20:13    10.0     -115.0 -0.000005
...    ...         ...                  ...     ...        ...       ...
3214  3215           1  2023-04-22 05:07:47  4000.0      -10.0 -0.053945
3215  3216           1  2023-04-22 05:07:48  4000.0      -10.0 -0.053962
3216  3217           1  2023-04-22 05:07:49  4000.0      -10.0 -0.053944
3217  3218           1  2023-04-22 05:07:50  4000.0      -10.0 -0.053948
3218  3219           1  2023-04-22 05:07:51  4000.0      -10.0 -0.053952

[3219 rows x 6 columns]
```

Pandas is smart enough to fetch the SQL result headers and assign them to the right
data column. 



But SQLite has a lot of tools to do things for you so that you don't even need to use
Python to further filter the data.

If I want all the measurement points for a single frequency, I can do that like this:

```python
```

I can ask SQLite to average all the measurement points for me:

```python
```

And here I'm still averaging, but after removing outliers that fall outside 3 standard deviations
of the data set:

```python
```

# HP 423A characterization results

# Reference

* [HP Journal Nov, 1963 - A New Coaxial Crystal Detector with Extremely Flat Frequency Response](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1963-11.pdf)
* [DIY Power Sensor for HP 436A and 438A](https://twitter.com/DanielTufvesson/status/1647545015764230144)

    * [Chopper And Chopper-Stabilised Amplifiers, What Are They All About Then?](https://hackaday.com/2018/02/27/chopper-and-chopper-stabilised-amplifiers-what-are-they-all-about-then/)

* [Infineon - RF and microwave power detection with Schottky diodes](https://www.infineon.com/dgdl/Infineon-AN_1807_PL32_1808_132434_RF%20and%20microwave%20power%20detection%20-AN-v01_00-EN.pdf?fileId=5546d46265f064ff0166440727be1055)
* [Agilent AN980 - Square Law and Linear Detection](/assets/hp423a/an986-square_law_and_linear_detection.pdf)
* [Square Law Detectors](https://www.nitehawk.com/rasmit/ras_appl6.pdf)
* [Operator's and Unit Maintenance Manualfor SG-1206/U](https://radionerds.com/images/2/20/TM_11-6625-3231-12.PDF)
* [Analog Devices - Understanding, Operating, and Interfacing to Integrated Diode-Based RF Detectors](https://www.analog.com/en/technical-articles/integrated-diode-based-rf-detectors.html)
* [Diode Detector](https://analog.intgckts.com/rf-power-detector/diode-detector-2/)
* [Design and development of RF power detector for microwave application](https://www.semanticscholar.org/paper/Design-and-development-of-RF-power-detector-for-Ali-Ibrahim/fed809b8f38fe7d0ebc0ffdc9fd1a7da3ac93037)


# Footnotes
