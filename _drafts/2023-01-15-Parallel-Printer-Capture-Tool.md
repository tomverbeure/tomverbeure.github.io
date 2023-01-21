---
layout: post
title: A Cheap Parallel Printer Capture Tool
date:   2023-01-15 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

My [previous blog post](/2023/01/01/HP33120A-Repair-Shutting-Down-the-Eye-of-Sauron.html)
contained a screenshot of my Advantest R3273 spectrum analyzer that I took by holding 
my iPhone in front of the screen:

![Screenshot of a spectrum analyzer](/assets/hp33120a/spectrum_comparison.jpg)

Using a camera works, of course, but it doesn't look very... professional? 

Here's another one from my
[TDS 420A blog posts](http://localhost:4000/2020/06/27/In-the-Lab-Tektronix-TDS420A.html):

![Screenshot of TDS 420A oscilloscope](/assets/tds420a/fft.jpg)

This one looks even worse, because the CRT hasn't been tuned quite right and the image is 
rotated a little bit.

What I want is a bit-for-bit hard-copy of what's shown on the screen, like this:

![Bitmap of screenshot of an R3273 spectrum analyzer](/assets/parallelprintcap/sa_harmonics.png)

or this:

![Bitmap screenshot of a TDS 420A oscilloscope](/assets/parallelprintcap/sa_waveform_on_tds420a.png)

Much better!

It's easy to save screenshots on modern equipment. On my daily driver Siglent oscilloscope, the easiest
way is to just insert a USB stick and press "Print", but you can also do by scripting some
[SCPI commands](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html#scpi---the-universal-command-language)
over a USB or Ethernet cable: 

[![Screenshot of a Siglent oscilloscope](/assets/smoke_detector/osc2-Vbst-Vled-Vdet.png)](/assets/smoke_detector/osc2-Vbst-Vled-Vdet.png)
*(Click to enlarge)*

It's not so simple for old equipment. The TDS 420A and the R3273 have a GPIB interface 
that can be used to download raw measurement data, but not the screenshot. However, they do have 
a floppy drive to save screenshots, and there's an old school parallel port to send a screenshot
straight to a printer.

I bought a floppy drive on Amazon for $19 and a pack of 10 3 1/2 HD floppy disks for $18, only
to discover that the floppy drives on both instruments were broken. Maybe that's just to
be expected from equipments that's 20 to 30 years old...

![Floppy drive](/assets/parallelprintcap/floppy_drive.jpg)

So the only interface left is the parallel printer port. Which made me think: "What if I capture
the printing data and convert it into a bitmap on my PC?" And thus a new project was born!

# What Is Out There?

I'm certainly not the first one to think about this. 
For £90, around $110, [Retro-Printer](https://www.retroprinter.com)
claims to do exactly what I want. 

![Retro-Printer solution](https://www.retroprinter.com/wp-content/uploads/2021/10/IMG_1583-scaled.jpg)

It's a Raspberry Pi hat that plugs into, well, a Raspberry 
Pi which is fine if you have one laying in a drawer somewhere, otherwise it's another $100+ 
in today's crazy market. Retro-Printer has been in existence for a while and they have dedicated 
software to back it, some open source, some not. I didn't test it, but if you want something 
that's a real product instead of a quick weekend hack, it's probably the option with the
highest chance of success.

Still, it's a little too much for what is, in my case, a non-essential gadget that I'll use only 
a few times per year.

I [asked for feedback on Twitter](https://twitter.com/tom_verbeure/status/1608976395216244738) 
and got a number of useful pointers.

[Rue Mohr](https://twitter.com/RueNahcMohr) created one by soldering a connector and an
Atmega on perfboard. It looks really neat:

![Rue's parallel port capturing tool - top](/assets/parallelprintcap/rue_dongle_top.jpg)

He also shared his [Parallel2Serial repo on GitHub](https://github.com/ruenahcmohr/Parallel2Serial)
with the Atmega firmware.

There are other projects out there, but when you google for terms such as "parallel port to usb",
they drown in a sea of "USB to parallel port" results!

# The Parallel Printer Port

The [parallel printer port](https://en.wikipedia.org/wiki/Parallel_port) and associated 
protocol was originally defined by Centronics way back in 1970 for their Model 101 printer.
The [Vintage Technology Digital Archive](vtda.org) still has the 
[specification and interface information](http://vtda.org/docs/computing/Centronics/101_101A_101AL_102A_306_SpecificationsInterfaceInformation.pdf)
for it.

![Centronics Protocol](/assets/parallelprintcap/centronics_protocol.jpg)

The diaram shows how a BUSY signal gets asserted by the printer when it's doing certain long
duration activities such a line or paper feeds, but the signal is frankly a bit redundant, as
we shall soon see.

Either way, these are the signals that actively participate in data transactions:

| Name    | Direction  | Description                                                                                   |
|---------|------------|-----------------------------------------------------------------------------------------------|
| nSTROBE | To Printer | A low pulse indicates that there's valid data on D[7:0]. This pulse can be as short as 500ns. |
| BUSY    | To Host    | Tell the host that the printer is busy and that it should wait with sending the next data.    |
| nACK    | To Host    | A low pulse tells the host that the current data has been processed.                          |
| D[7:0]  | To Printer | The data that is transmitted to the printer.                                                  |

Here is parallel port traffic between the spectrum analyzer and my capturing tool:

![Parallel port transactions on a R3273](/assets/parallelprintcap/scope_shots/5_r3273_full_transaction_cycle_busy.png)
*nSTROBE: yellow, BUSY: purple, nACK: cyan*

There's 22uS between each transaction, good for a data rate of around 350kbits/s.

I created a test version of the capturing tool that never asserts BUSY. It works just the same, showing
that the R3272 probably just ignores BUSY and waits for an end-of-tranaction nACK pulse instead:

![Parallel port transactions on a R3273 without using BUSY](/assets/parallelprintcap/scope_shots/6_r3273_full_transaction_cycle_no_busy.png)



In addition to the signals that are used for the actual data transfer, the parallel port has a bunch of
mostly static sideband signals:

| Name    | Direction  | Value | Description                                                                                           |
|---------|------------|:-----:|-------------------------------------------------------------------------------------------------------|
| nINIT   | To Printer |   1   | A negative pulse resets the printer to its default state.                                             |
| nSELINT | To Printer |   0   | A low value tells the printer that a host is present and powered on.                                  |
| nAUTOF  | To Printer |   1   | No strict definition. A low value is used to perfrom things like printer auto-feed or some other action. |
| SEL     | To Host    |   1   | A high value indicates that a printer is present.                                                     |
| PE      | To Host    |   0   | Short for Paper Error. A high value indicates that the printer can't print at this time.              |
| nERROR  | To Host    |   1   | A low value indicates that the printer has encountered some kind of error.                            |

For a simple traffic capturing tool, you can ignore the the 3 signals that are going to the printer and
you can tie the signals that go back to the host to the listed static values.

The printer port was originally only used for low speed printer communication, but it was later upgraded to
support higher transfer speeds and even bidirectional data communication. These extensions are described
in the IEEE 1284 specification which defines different modes: compatibility mode, nibble mode, byte mode,
enhanced parallel port (EPP), and extended capability port (ECP), where compatibility mode is the original
protocol.

After powering up, all printers start out in compatibility mode. They switch to a different mode through
a protocol negotiation process.

For our purposes, we can ignore all these advanced mode and stick with compatibility mode. 

The host almost always uses a DB-25 connector:

![DB-25 pinout](/assets/parallelprintcap/parallel_port_pinout.jpg)

*Source: [Wikipedia](https://en.wikipedia.org/wiki/Parallel_port#/media/File:25_Pin_D-sub_pinout.svg), (c) Andrew Buck*

The printer side has a 36-pin Centronics connector:

![Centronics connector](/assets/parallelprintcap/centronics_connector.jpg)

*Source: [Wikipedia](https://commons.wikimedia.org/wiki/File:Centronics.jpg), (c) Michael Krahe*


# Fake Printer Top Level Design Choices

Here's a summary of the fake printer features and design decisions:

* DB-25 connector + PCB that plug in straight into the instrument
* USB acting as serial port to transmit data to PC
* Raspberry Pico as microcontroller

**DB-25 instead of Centronics Connector**

The Retro-Printer solution has a Centronics port, just like a real printer. I'm using
DB-25 connector instead. The reason is cost and, IMO, convenience. On Digikey, 
the DB-25 connector is $1.60 versus $7.10 for the Centronics one. And if you
use the Centronics connector, you need a bulky DB-25 to Centronics cable too, 
good for an additional $12! And now you have 2 cables: the printer cable and
the USB cable from the fake printer back to your PC. 

**Raspberry Pico**

You can see by looking at Rue's design that a device to capture parallel port traffic and send it to a PC can
be very simple. You need to have:

* an parallel interface that can deal with 5V signalling in transmit and receive direction
* logic to reliably capture the 8-bit data and adhere to the parallel port protocol
* a way to interface with the PC. USB is the obvious choice here.

In this day and age, you use a microcontroller for stuff like this. Rue had an Atmel in his component box, 
which is great because it has USB device interface and 5V capable IOs right out of the box.

I choose a Raspberry Pico because:

* I had a couple laying around
* at around $5 a piece, they're cheap enough
* they are staightforward to program and to program for
* they are available everywhere in high volume: no issues with component shortage!

The Raspberry Pico is bulkier than smaller alternatives with the same RP2040 microcontroller
chip, such as the [Seeed Studio XIAO RP2040](https://www.seeedstudio.com/XIAO-RP2040-v1-0-p-5026.html),
but in my final PCB design, that doesn't make a practical difference. And the Pico is the
reference implementation which should be available for as long as the RP2040 exists.

Instead of a Pico, you can also use a Pico W. The boards are pin compatible after all. A wireless interface
can be useful when the back side of your oscilloscope is hard to reach, but you'd still need 
a USB cable to power the board because there is no +5V pin on the parallel port itself.

# Fake Printer Implementation 

Since a Raspberry Pico doesn't have 5V tolerant IOs, one or more buffer ICs are required for level shifting.

My initial design used 3 generic [SN74LVC8T245PW](https://www.ti.com/lit/ds/symlink/sn74lvc8t245.pdf) 8-bit
transceivers that cost $1.65 a piece on Digikey. However, I reworked it to use a
[74LVC161284](https://www.ti.com/lit/ds/symlink/sn74lvc161284.pdf) which is a bus interface chip
that's specifically designed for parallel printer ports!




If you had been keeping track, there were a total of 17 parallel port signal listed in the previous section.
In the logic diagram of the 74LVC161284, there are 17 signals as well, going in the right direction. Since the
chip can support the later IEEE 1284 protocols, the IOs for the databus are bidirectional.

![74LVC161284 logic diagram](/assets/parallelprintcap/74lvc161284_logic_diagram.png)

You can ignore the `PERI_LOGIC` and `HOST_LOGIC` feed-through signals: they are not used.



