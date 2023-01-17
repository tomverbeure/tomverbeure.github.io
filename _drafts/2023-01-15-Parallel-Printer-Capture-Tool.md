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
contained a screenshot of my spectrum analyzer that I took by holding my iPhone
in front of the screen:

![Screenshot of a spectrum analyzer](/assets/hp33120a/spectrum_comparison.jpg)

I take screenshots quite often, such as this one from one of my 
[TDS 420A blog posts](http://localhost:4000/2020/06/27/In-the-Lab-Tektronix-TDS420A.html):

![Screenshot of TDS 420A oscilloscope](/assets/tds420a/fft.jpg)

Using a camera works, of course, but it doesn't look very... professional? What
I sometimes want is a bit-for-bit hard-copy of what's shown on the screen, like this:

![Bitmap screenshot of a TDS 420A oscilloscope](/assets/parallelprintcap/sa_waveform_on_tds420a.png)

It's easy to save screenshots on modern equipment. On my daily driver Siglent oscilloscope, the easiest
way is to just insert a USB stick and press "Print", but you can also do by scripting some
[SCPI commands](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html#scpi---the-universal-command-language)
over a USB or Ethernet cable. 

![Screenshot of a Siglent oscilloscope](/assets/smoke_detector/osc2-Vbst-Vled-Vdet.png)

It's not so simple for old equipment. The TDS 420A and the spectrum analyzer have a GPIB interface 
that can be used to download raw measurement data, but not the screenshot. They also have a floppy 
drive to save image bitmaps, and there's an old school parallel port to send the image
straight to printer.

I bought a floppy drive on Amazon for $19 and a pack of 10 3 1/2 HD floppy disks for $18, only
to find out that the floppy drives on both instruments were broken. Maybe that's just to
be expected from equipments that's 20 to 30 years old...

So the only option left is the parallel printer port. Which made me think: "What if I capture
that printing data, and render it into a bitmap on my PC?" And thus a new project was born!

# What Is Out There?

I'm certainly not the first one to think about this. 
For £90, around $110, [Retro-Printer](https://www.retroprinter.com)
claims to do exactly what I want. 

![Retro-Printer solution](https://www.retroprinter.com/wp-content/uploads/2021/10/IMG_1583-scaled.jpg)

It's a Raspberry Pi hat that plugs into, well, a Raspberry 
Pi which is fine if you have one laying in a drawer somewhere, otherwise it's another $100+ 
in today's crazy market. Retro-Printer has been in existence for a while and there's dedicated 
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

# The Parallel Printer Port

The [parallel printer port](https://en.wikipedia.org/wiki/Parallel_port) and associated 
protocol was originally defined by Centronics, way back in 1970 for their Model 101 printer.
The [Vintage Technology Digital Archive](vtda.org) still has the 
[specification and interface information](http://vtda.org/docs/computing/Centronics/101_101A_101AL_102A_306_SpecificationsInterfaceInformation.pdf)
for it.

![Centronics Protocol](/assets/parallelprintcap/centronics_protocol.jpg)

The behavior of the BUSY signal in the diagram above doesn't line up with what's expected
of later parallel printers, where BUSY must be asserted *while STROBE is low*, but the main
idea hasn't changed:

| Name    | Direction  | Description                                                                                   |
|---------|------------|-----------------------------------------------------------------------------------------------|
| nSTROBE | To Printer | A low pulse indicates that there's valid data on D[7:0]. This pulse can be as short as 500ns. |
| BUSY    | To Host    | Tell the host that the printer is busy and that host should wait with sending the next data.  |
| nACK    | To Host    | A low pulse tells the host that the current data has been processed.                          |
| D[7:0]  | To Printer | The data that is transmitted to the printer.                                                  |

The BUSY signal is frankly a bit redundant. Originally, it was only required when the printer
need to perform things like a line feed, a carriage return or other mechanical options that took
longer than printing a single character.

Here is parallel port traffic between the spectrum analyzer and the capturing tool, as captured
from the TDS 420A using the tool, of course:

![Parallel Port Protocol on oscilloscope](/assets/parallelprintcap/sa_waveform_on_tds420a_annotated.png)

In this case, the `nSTROBE` pulse is around 1uS, but as seen in that old Centronics diagram above, the
pulse can be as short as 500ns. 

In addition to the signals that are used for the actual data transfer, the parallel port has a bunch of
mostly static sideband signals:

| Name    | Direction  | Value | Description                                                                                           |
|---------|------------|:-----:|-------------------------------------------------------------------------------------------------------|
| nINIT   | To Printer |   1   | A negative pulse resets the printer in its default state.                                             |
| nSELINT | To Printer |   0   | A low value tells the printer that a host is present and powered on.                                  |
| nAUTOF  | To Printer |   1   | No strict definition. A low value is used to from things like printer auto-feed or some other action. |
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

# ParallelPrinterCap Design 

As seen by the Rue's design, a device to capture parallel port traffic and send it to a PC can
be very simple. You need to have:

* an parallel interface that can deal with 5V signalling in transmit and receive direction
* logic to reliably capture the 8-bit data and adhere to the parallel port protocol
* a way to interface with the PC. USB is the obvious choice here.

In this day and age, a microcontroller is the obvious choice for this. Rue had an Atmel in his
component box, which is great because it has USB device interface and 5V capable IOs right out of the box.

I choose a Raspberry Pico because:

* I have a couple laying around
* at around $7 a piece, they're cheap enough
* they are staightforward to program
* they are available everywhere in high volume: no issues with component shortage!

Since a Raspberry Pico doesn't have 5V tolerant IOs, a buffer IC is required for level shifting.

My initial design used 3 generic [SN74LVC8T245PW](https://www.ti.com/lit/ds/symlink/sn74lvc8t245.pdf) 8-bit
transceivers that cost $1.65 a piece on Digikey. However, I switched to an 
[74LVC161284](https://www.ti.com/lit/ds/symlink/sn74lvc161284.pdf) which a bus interface chip
that's specifically designed for parallel printer ports!



