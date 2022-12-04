---
layout: post
title: HP 3478A Multimeter RIFA Capacitors and Battery Replacement
date:  2022-12-02 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Just a bit of a year ago, I wrote a blog post about 
[repairing an HP 3478A multimeter with a hacksay](/2021/11/26/HP3478A-Multimeter-Repair-with-a-Hacksaw.html).
After posting a link on Twitter, alex commented that I should 
[replace the RIFA capacitors](https://twitter.com/geekc64os/status/1464331326652395530?s=20&t=WQFQvTtJkUr7HXN0EoEWgg)
because they have a tendency to go up in smoke:

![Tweet about replacing RIFA capacitors](/assets/hp3478a/replace_rifa_caps_tweet.png)

The multimeter went back on the shelve, but I have now some projects in mind where I could 
use some continuous voltage recording. So now is a good time to replace the capacitors.

Another weak spot of the 3478A is that fact that calibration parameters are stored in a SRAM that's
permanentely powered on by a long-lasting 3V Lithium battery.  There's no explicit production
date on my unit, but a bunch of chips were produced in 1988, so after almost 34 years, I
might as well replace that one too.

There is quite a bit of information on the web about how to do this, though some info is
buried in long forums threads on EEVBlog or (long winded) Youtube videos. This blog post
tries to bring some of the information together.

# HP 3478A Calibration Data Backup, Format, and Restore

These days, a working 3478A sells for around $150 on eBay. You'll probably pay more just to have
it professionally recalibrated, or to acquire reference voltage or resistor standards, so most
people will just keep using what they have. In many cases, you care more about measuring
relative than absolute values anyway.

As mentioned earlier, the 3478A stores the calibration data in a 
[256x4 SRAM](/assets/hp3478a/uPD5101L_datasheet.pdf) that's 'permanently' powered
by a lithium battery. You should definitely replace the RIFA capacitors, there's a real
fire risk when they fail, but if you don't want to replace the battery just yet, at least 
back up the calibration data. 

There are two ways to do that: 

* Use the GPIB interface to read the SRAM contents.
* Probe the SRAM pins with a logic analyzer

**Probing the SRAM pins**

![uPD5101L pinout](/assets/hp3478a/uPD5101L_pinout.png)

The SRAM has 22 pins, but only 20 of those are functional. Of those, you need to
probe A[7:0], DO[3:0], and some pins to determine that the microcontroller is
accessing the chip. CE2, pin 17, should do the trick.

![uPD5101L internals](/assets/hp3478a/uPD5101L_internals.png)

That's a total of 13 pins. 

Wiring up the probes is easy: the spacing of these old school DIL packages is a joy. You
do need a 16-channel logic analyzer, which are quite a bit more expensive than 
these ubiquitous $15 8-channel Saleae clones. And even if you have access to the 
[real deal](https://usd.saleae.com/products/saleae-logic-pro-16), I had the problem that... 
it didn't work: after wiring up the probes, my 3478A didn't want to boot up! 

Still, others have done it, so it's definitely possible.

**Dumping SRAM contents through the GPIB interface**

The GPIB route is much easier. I used my Agilent 82357B GPIB-to-USB dongle. Check out
my [TDS 420A control over GPIB blog post](/2020/06/27/Tektronix-TDS420A-Remote-Control-over-GPIB.html)
for details on how to install the linux-gpib kernel drivers (what a pain...).

In [a long discussion on EEVBlog](https://www.eevblog.com/forum/repair/hp-3478a-how-to-readwrite-cal-sram/), 
plenty of people post their own scripts and tools to dump the SRAM contents, but none
of them fit my needs: they were either windows-only, used Matlab, required an old version
of PyVISA, or used the linux-gpib kernel API directly.

I wanted to use the PyVISA API under Linux, so I just wrote my own version. 

Reading the data is straightforward: when you send a `W<addr>` GPIB message to the 3478A,
it will reply with a single character that has an ASCII value from 64 to 79. Subtract
64 from that, and you get a 4-bit value, the SRAM content of the specified address. 
Note that `<addr>` a binary number, not an ASCII value of the address!

In Python, the code to fetch the 256 SRAM values looks like this:

```python
def read_cal_data(hp3478a):
    cal_data = []

    for addr in range(0, 256):
        cmd = bytes([ord('W'), addr])
    
        hp3478a.write_raw(cmd)
        rvalue = ord(hp3478a.read()[0])
        assert rvalue >= 64 and rvalue < 80
        cal_data.append(rvalue)
    print()

    return cal_data
```

**SRAM Data Checksum**

The SRAM contents are organized as follows:

* at address 0, there's a read/write check nibble. The microcontroller does a read/write
  operation to it to check whether or not the SRAM is write protected.
* after that, there are 19 calibration entries of 13 nibbles. 

In total that's 248 SRAM values. The remaining ones are don't-care.

Each of the 19 calibration entries is organized as follows: 

* 11 nibbles with a real calibration value. 

    The first 6 nibbles specify an offset, the next 5 contain a gain.
    The coding method is a bit obscure and out of the scope of this blog post, but
    you can find the details [here](https://www.eevblog.com/forum/repair/hp-3478a-how-to-readwrite-cal-sram/msg1966463/#msg1966463).

    The same poster created [hp3478a_utils](https://github.com/fenugrec/hp3478a_utils),
    a DOS utility that decodes all the values.

    *Use the source of the utility as the 
    [golden reference](https://github.com/fenugrec/hp3478a_utils/blob/07e6311c9eb6118537e3238882c75efc8fe164d5/hp3478util.c#L230-L247): 
    later in the EEVBlog thread, there were some corner cases where the gain encoding didn't quite work.*

* 2 nibbles that form an 8-bit checksum

    The sum of the first 11 nibbles plus the sum of the 8-bit checksum must be
    255 for a correct calibration value.

    For example:  

    ```
@@@A@IADOD@MM -> 0 0 0 1 0 9 1 4 F 4 0 D D -> 1+9+1+4+F+4+DD = 0xFF
    ```

Here's the code that checks the validity of the SRAM contents:

```python
def verify_checksum(cal_data):
    for entry in range(0,19):
        sum = 0
        for idx in range(0, 13):
            val = cal_data[entry*13 + idx + 1]-64
            if idx!=11:
                sum += val
            else:
                sum += val*16

        print("Checksum %2d: 0x%02x " % (entry,sum), end='')
        if sum==255:
            print(" PASS")
        else:
            print(" FAIL")
```

The 19 entries contain the calibration values for the following measurement ranges:

```
entry  0: 30 mV DC
entry  1: 300 mV DC
entry  2: 3 V DC
entry  3: 30 V DC
entry  4: 300 V DC
entry  5  Not used
entry  6: ACV
entry  7: 30 Ohm 2W/4W
entry  8: 300 Ohm 2W/4W
entry  9: 3 KOhm 2W/4W
entry 10: 30 KOhm 2W/4W
entry 11: 300 KOhm 2W/4W
entry 12: 3 MOhm 2W/4W
entry 13: 30 MOhm 2W/4W
entry 14: 300 mA DC
entry 15: 3A DC
entry 16  Not used
entry 17: 300 mA/3A AC
entry 18: Not used
```

For my unit, the checksum of unused entries 5, 16 and 18 still matched, but that's
not generally true. When a checksum doesn't match for a given measurement range, the
LCD display will show "CAL" to indicate that this particular range is in need of recalibration.

The full script can be found [here](https://github.com/tomverbeure/hp3478a_calibration).
This is the output of my unit:

```
Fetching calibration data...

Contents of calibration RAM:
0000: 40 40 40 40 43 40 48 42 4f 44 44 40 4d 4b 40 40  @@@@C@HBODD@MK@@
0010: 40 40 43 43 42 4f 45 43 40 4e 40 40 40 40 40 40  @@CCBOEC@N@@@@@@
0020: 43 42 4f 44 40 40 4e 47 49 49 49 49 49 47 42 40  CBOD@@NGIIIIIGB@
0030: 4f 43 4c 4a 4b 49 49 49 49 49 49 42 40 4e 4f 4e  OCLJKIIIIIIB@NON
0040: 49 4c 40 40 40 40 40 40 40 40 40 40 40 4f 4f 49  IL@@@@@@@@@@@OOI
0050: 49 48 46 40 49 42 4e 4e 40 4c 4a 4c 49 49 49 49  IHF@IBNN@LJLIIII
0060: 49 45 41 4c 40 45 4e 4a 4d 49 49 49 49 49 48 41  IEAL@ENJMIIIIIHA
0070: 4c 41 4f 41 4a 4c 40 40 40 40 40 40 41 4c 4f 43  LAOAJL@@@@@@ALOC
0080: 40 4e 40 49 49 49 49 49 49 41 4c 4d 42 4e 49 4f  @N@IIIIIIALMBNIO
0090: 49 49 49 49 49 49 41 4c 4d 44 42 4a 49 49 49 49  IIIIIIALMDBJIIII
00a0: 49 49 49 41 4c 4e 4c 4d 49 45 49 49 49 49 49 49  IIIALNLMIEIIIIII
00b0: 41 4c 42 41 4f 4a 4a 40 40 40 40 44 42 43 40 40  ALBAOJJ@@@@DBC@@
00c0: 43 4c 4e 47 40 40 40 40 40 44 43 40 41 4c 43 4e  CLNG@@@@@DC@ALCN
00d0: 48 40 40 40 40 40 40 40 40 40 40 40 4f 4f 49 49  H@@@@@@@@@@@OOII
00e0: 48 46 40 49 43 4e 43 41 41 4c 40 40 40 40 40 40  HF@ICNCAAL@@@@@@
00f0: 40 40 40 40 40 40 4f 4f 40 40 40 40 40 40 40 40  @@@@@@OO@@@@@@@@

Checksum for all calibration values:
Checksum  0: 0xff  PASS
Checksum  1: 0xff  PASS
Checksum  2: 0xff  PASS
Checksum  3: 0xff  PASS
Checksum  4: 0xff  PASS
Checksum  5: 0xff  PASS (unused, FAIL is OK)
Checksum  6: 0xff  PASS
Checksum  7: 0xff  PASS
Checksum  8: 0xff  PASS
Checksum  9: 0xff  PASS
Checksum 10: 0xff  PASS
Checksum 11: 0xff  PASS
Checksum 12: 0xff  PASS
Checksum 13: 0xff  PASS
Checksum 14: 0xff  PASS
Checksum 15: 0xff  PASS
Checksum 16: 0xff  PASS (unused, FAIL is OK)
Checksum 17: 0xff  PASS
Checksum 18: 0xff  PASS (unused, FAIL is OK)

Writing calibration data to 'hp3478a_cal_data.bin'.
```

# Replacement 3V Battery 

The battery in the 3478A is not socketed but soldered straight on the PCB, with contacts
spot welded the plus and the minus terminals.

The schematic and PCB list a 3V battery, but as far as I can tell, all batteries start out
higher, with the voltage dropping as the battery charge goes down. In my case, the voltage was at
3.03V.

Digikey sells the [BR-2/3AE5SPN battery](https://www.digikey.com/en/products/detail/panasonic-bsg/BR-2-3AE5SPN/61161),
with spot welded contacts:

![BR-2/3AE5SPN battery](/assets/hp3478a/br-23ae5spn.png)

An alternative is to use a battery with wires, as in [this on Youtube](https://www.youtube.com/watch?v=e-itiJSftzs). 
It has the benefit over being able to wrap the battery in a plastic so that leaks won't destroy the PCB, but then 
you need a way to fix the battery in place somewhere.

![battery with wires](/assets/hp3478a/battery_with_wires.png)

I mistakenly ordered the BR-2/3A battery without the pin contacts. Luckily, I bought one of those $40 spot
welders and was able to create contact myself. 

# Replacing the Battery





# Calibration Data Backup over GPIB

* [EEVblog forum: HP 3478A: How to read/write cal SRAM](https://www.eevblog.com/forum/repair/hp-3478a-how-to-readwrite-cal-sram/)
* [hp3478a_utils](https://github.com/fenugrec/hp3478a_utils)
    * [Format of calibration parameters](https://www.eevblog.com/forum/repair/hp-3478a-how-to-readwrite-cal-sram/msg1966463/#msg1966463)
* [HP3478Ctrl](https://github.com/pigrew/HP3478Ctrl)
* [hp3478a-calibration](https://github.com/steve1515/hp3478a-calibration)
* [HP3478A instrument control software](https://mesterhome.com/gpibsw/hp3478a/index.html)

![schematic of calibration RAM logic](/assets/hp3478a/calibration_ram.png)

![schematic of battery circuit](/assets/hp3478a/battery_circuit.png)


# Various

* Works by charging a capacitor and measuring time (according to EEVblog video)

# References

* [EEVblog teardown](https://www.youtube.com/watch?v=9v6OksEFqpA) 
* [Tony Albus HP 3478A Multimeter Teardown](https://www.youtube.com/watch?v=q6JhWIUwEt4)
* [Datasheet](https://accusrc.com/uploads/datasheets/agilent_hp_3478a.pdf)
* [HP Journal](https://www.hpl.hp.com/hpjournal/pdfs/IssuePDFs/1983-02.pdf)

    Contains technical description.

* [Discussion on EEVblog](https://www.eevblog.com/forum/beginners/is-190$-a-bargain-for-a-hp-2378a-bench-multimeter/)

    "3478 are not bad but they are virtually unrepairable if they break. Especially the display is unobtainium..."

* [Service Manual](http://www.arimi.it/wp-content/Strumenti/HP/Multimetri/hp-3478a-Service.pdf)
* [Battery replacement article](http://mrmodemhead.com/blog/hp-3468a-battery-replacement/)

* [Boat Anchor Manual Archive](https://bama.edebris.com)

