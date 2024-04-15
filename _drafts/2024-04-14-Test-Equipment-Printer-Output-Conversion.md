---
layout: post
title: Test Equipment Printer Output Conversion
date:   2024-04-14 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

# Tools

**GhostPCL**

GhostPCL is used to decode PCL files. On many old machines, these files are created
when printing to Thinkjet, Deskjet or Laserjet.

Installation:

* Download the [GhostPCL/GhostPDL source code](https://www.ghostscript.com/releases/gpcldnld.html).
* Compile

```sh
cd ~/tools
tar xfv ~/Downloads/ghostpdl-10.03.0.tar.gz
cd ghostpdl-10.03.0/
./configure --prefix=/opt/ghostpdl
make -j$(nproc)
export PATH="/opt/ghostpdl/bin:$PATH"
```

* Install

```sh
sudo make install
```

A whole bunch of tools will now be available in `/opt/ghostpdl/bin`, including
`gs` (Ghostscript) and `gpcl6`.

# Capturing GPIB data in Talk Only mode

Some devices will only print to GPIB in Talk Only mode, or sometimes it's just
easier to it that way. In this mode, the PC GPIB interface is a passive observer 
that doesn't initiate commands but just receives data.

![TDS540 in talk-only mode](/assets/print_file_conversion/tds540_talk_only_mode.png)


I'm using the following script to record the printing data and save it to 
a file:

[`gpib_talk_to_file.py`](/assets/print_file_conversion/gpib_talk_to_file.py):
*(click to download)*
```python
#! /usr/bin/env python3

import sys
import pyvisa

gpib_addr       = int(sys.argv[1])
output_filename = sys.argv[2]

rm = pyvisa.ResourceManager()

inst = rm.open_resource(f'GPIB::{gpib_addr}')

try:
    # Read data from the device
    data = inst.read_raw()

    with open(output_filename, 'wb') as file:
        file.write(data)

except pyvisa.VisaIOError as e:
    print(f"Error: {e}")
```

Pyvisa can easily time out. When doing a hardcopy print-out, I always first press
the hardcopy button on the oscilloscope, and then I start the script. This way,
timeouts are usually avoided.

# TDS 540 Oscilloscope

My old TDS 540 oscilloscope didn't have a printer port, so I had to make do with
GPIB. It also didn't have the ability to export bitmaps directly, but it has outputs
for:

* Thinkjet, Deskjet, and Laserjet PCL format
* Epson in ESC/P format
* Interleaf format
* EPS Image format
* HPGL plotter format

The TDS 540 has a screen resolution of 640x480. I found the Thinkjet output format
easiest to deal with. It has a DPI of 75x75. A margin of 20 pixels is added to the left,
and 47 pixels at the top, but that can be removed with ImageMagick.

The overall recipe looks like this:

```sh
# Capture the data
gpib_talk_to_file.py 11 tds540.thinkjet.pcl
# Convert to png. 
gpcl6 -dNOPAUSE -sOutputFile=tds540.png -sDEVICE=png256 -g680x574 -r75x75 tds540.thinkjet.pcl
# Optionally crop the 640x480 image
convert tds540.png -crop 640x480+20+47 tds540.crop.png
```

The end result will look like this:

![TDS540 screenshot](/assets/print_file_conversion/tds540.crop.png)



