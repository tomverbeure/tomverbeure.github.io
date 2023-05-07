---
layout: post
title: Fake Parallel Printer - Converting Printer Captures to Bitmaps
date:   2023-01-25 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

The effort of converting a captured printer trace ranges from entirely painless to
very painful. It depends on which printer formats are supported by your instrument, and
the desired quality.

# Epson ESC/P to Bitmap Conversion

# Encapsulated Postscript to Bitmap Conversion

# PCL to Bitmap Conversion


My TDs 420A and Advantest R3273, the only instruments on which I tried it, have each a ton
of different screenshot format options.

Let's start with painless, the TDS 420A. Here's a slightly edited screenshot of the
Harcopy Format menu option:


The TDS 420A supports:

* The Thinkjet, Deskjet, and Laserjet. 

    These are all very old HP printers that use HP's PCL format.

* Epson 9 & 24 pin dot matrix

    Another company specific format, but it was very popular back in the day
    and a de-facto standard.

* DFU 411/11 and 412 thermal printers

    No clue about the format!

* PCX, TIFF, BMP, and Interleaf IMG file formats

    These aren't printer but file formats for bitmap images that are supposed
    to be saved to the floppy drive of the oscilloscope. But's here the 
    cool part: when you select the printer as output for a Hardcopy (=screenshot),
    the TDS 420A sends the contents of the bitmap file to the printer!

* Encapsulated Postscript Mono Img, EPS Mono Plt, EPS Color Plt
   


# Capturing Printing Data on Windows


[![TDS420 print options](/assets/parallelprintcap/tds420a_print_options.png)](/assets/parallelprintcap/tds420a_print_options.png)
*(Click to enlarge)*

# References


