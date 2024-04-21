---
layout: post
title: Test Equipment Printer Output to Bitmap Conversion
date:   2024-04-14 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

# Tools

**Fake Parallel Printer**

There are 6 common ways to transfer screenshots from test equipment to your PC:

* USB

    Usually painless, this only works on modern equipment.

* Ethernet

    Still requires slightly modern equipment, and there's often some configuration pain
    involved.

* RS-232 serial

    Reliable, but often very slow.

* GPIB

    Requires an expensive interface dongle and I've yet to figure out how to make it
    work for all equipment. Below, I was able to make it work for the TDS 540, but not for
    the HP 54532A, for example.

* Parallel printer port

    Available on a lot of old equipment, but it normally can't be captured by a PC.
    That's why I created [Fake Parallel Printer](/2023/01/24/Fake-Parallel-Printer-Capture-Tool-HW.html),
    a tool to capture parallel port traffic. You can make one for yourself for around $20.

    We're now more than a year later, and I use it all the time. I find it to be the easiest
    to use of all the printer interfaces.

**GPIB to USB Dongle**

**ImageMagick**

ImageMagick is the swiss army knife of bitmap file processing. It has a million features,
but I primarily use it for file format conversion and image cropping.

I doubt that there's any major Linux distribution that doesn't have it as a standard
package...

```sh
sudo apt install imagemagick
```

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

**hp2xx**

hp2xx converts HPGL files, originally intended for HP plotter, to bitmaps, EPS etc.

It's available as a standard package for Ubuntu:

```sh
sudo apt install hp2xx
```

**HP 8753C Companion**

This tool is specific to HP 8753 vector network analyzers. It captures HPGL
plotter commands, extracts the data, recreates what's displayed on the screen,
and allow you to interact with it.

It's available on [GitHub](https://github.com/VK2BEA/HP8753-Companion).

# Capturing GPIB data in Talk Only mode

Some devices will only print to GPIB in Talk Only mode, or sometimes it's just
easier to use that way. 

When the device is in Talk Only mode, the PC GPIB controller becomes a Listen Only device,
a passive observer that doesn't initiate commands but just receives data.

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

Pyvisa will quickly time out when no data arrives in Talk Only mode, but since
all data transfers happen with valid-ready protocol, you can avoid time-out
issued by pressing the hardcopy or print button on your oscilloscope first, and
only then launch the script above.

This will work as long as the printing device doesn't go silent while in the middle
of printing a page.

# TDS 540 Oscilloscope - GPIB - PCL Output

My old TDS 540 oscilloscope didn't have a printer port, so I had to make do with
GPIB. Unlike later version of the TDS series, it also didn't have the ability to 
export bitmaps directly, but it has outputs for:

* Thinkjet, Deskjet, and Laserjet in PCL format
* Epson in ESC/P format
* Interleaf format
* EPS Image format
* HPGL plotter format

The TDS 540 has a screen resolution of 640x480. I found the Thinkjet output format,
with a DPI of 75x75, easiest to deal with. The device adds a margin of 20 pixels to the left,
and 47 pixels at the top, but that can be removed with ImageMagick.

With a GPIB address of 11, the overall recipe looks like this:

```sh
# Capture the PCL data
gpib_talk_to_file.py 11 tds540.thinkjet.pcl
# Convert PCL to png 
gpcl6 -dNOPAUSE -sOutputFile=tds540.png -sDEVICE=png256 -g680x574 -r75x75 tds540.thinkjet.pcl
# Remove the margins and crop the image to 640x480
convert tds540.png -crop 640x480+20+47 tds540.crop.png
```

The end result looks like this:

![TDS540 screenshot](/assets/print_file_conversion/tds540.crop.png)

# HP 54542A Oscilloscope - Parallel Port - PCL or HPGL Output

This oscilloscope was an ridiculous $20 bargain at the 
[Silicon Valley Electronics Flea Market](https://www.electronicsfleamarket.com/). It has
a GPIB, RS-232, and Centronics port, and all 3 can be used for printing.

I tried for a while to get printing to GPIB to work, but wasn't successful. I'm able to
talk to the device and send commands like "\*IDN?" and get a reply just fine, but 
the GPIB script that works fine with the TDS 540 always times out eventually.

I switched to my always reliable [Fake Parallel Printer](https://tomverbeure.github.io/2023/01/24/Fake-Parallel-Printer-Capture-Tool-HW.html)
and that worked fine. There's also the option to use the serial cable.

The printer settings menu can by accessed by pressing the Utility button and then 
the top soft-button with the name "HPIB/RS232/CENT CENTRONICS".

![HP 54542A printing options](/assets/print_file_conversion/hp54542a_printing_options.png)

You have the following options:

* ThinkJet
* DeskJet75dpi, DeskJet100dpi, DeskJet150dpi, DeskJet300dpi
* LaserJet
* PaintJet
* Plotter

Unlike the TDS 540, I wasn't able to get the ThinkJet option to convert into anything but
the DeskJet75dpi option worked fine with this recipe:

```sh
~/projects/fake_parallel_printer/fake_printer.py -i -p /dev/ttyACM0 -f hp54542a_ -s deskjet.pcl -v
gpcl6 -dNOPAUSE -sOutputFile=hp54542a.png -sDEVICE=png256 -g680x700 -r75x75 hp54542a_0.deskjet.pcl
convert hp54542a.png -crop 640x388+19+96 hp54542a.crop.png
```
The 54542A doesn't just print out the contents of the screen, it also prints the date and adds 
the settings for the channels that are enabled, trigger options etc. The size of these additional
values depends on how many channels and other parameters are enabled.

![HP 54542A with additional info](/assets/print_file_conversion/hp54542a_additional_info.png)

When you select PaintJet or Plotter as output device, then you have the option to select
different colors for regular channels, math channels, graticule, markers etc. So it is
be possible to create really nice color screenshot from this scope, even if the CRT is
monochrome. 

I tried the PaintJet option, and while gcpl6 was able to extract an image, the output was
much worse than the DeskJet option.

I had more success using the Plotter option. It prints out a file in HPGL format that can
be converted to a bitmap with `hp2xx`. The following recipe worked for me:

```sh
~/projects/fake_parallel_printer/fake_printer.py -i -p /dev/ttyACM0 -f hp54542a_ -s plotter.hpgl -v
hp2xx -m png -a 1.4 --width 250 --height 250 -c 12345671 -p 11111111 hp54542a_0.plotter.hpgl
```


I'm not smitten with the way it looks, but if you want color, this is your best option. 
The command line option of `hp2xx` are not intuitive. Maybe it's possible to get this to look a bit
better with some other options.

[![HP plotter output](/assets/print_file_conversion/hp54542a_0.plotter.png)](/assets/print_file_conversion/hp54542a_0.plotter.png)

# TDS 684B - Parallel Port - PCX Color Output

I replaced my TDS 540 oscilloscope by a TDS 684B. On the outside, they look identical. They also
have the same core user interface, but it has a color screen, a bandwidth of 1GHz and a sample
rate of 5 Gsps.

**Print formats**

The 684B also has a lot more output options:

* Thinkjet, Deskjet, DeskjetC (color), Laserjet output in PCL format
* Epson in ESC/P format
* DPU thermal printer (???)
* PC Paintbrush mono and color in PCX file format
* TIFF file format
* BMP mono and color format
* RLE color format
* EPS mono and color printer format
* EPS mono and color plotter format
* Interleaf .img format
* HPGL color plot

Phew.

Like the HP 54542A, my unit has GPIB, parallel port, and serial port. It can also write out
the files to floppy drive.

So which one to use?

BMP is an obvious choice, and supported natively by all modern PCs. The only issue is that
it gets written out without any compression. It takes over 130 seconds to capture with fake printer.
PCX is a very old bitmap file format but it uses 
[run length encoding](https://en.wikipedia.org/wiki/Run-length_encoding). It only take 22 seconds
to print.

I tried the TIFF option and was happy to see that it only took 17 seconds, but the output was 
monochrome. So for color bitmap file, PCX is the way to go. The recipe:

```sh
~/projects/fake_parallel_printer/fake_printer.py -i -p /dev/ttyACM0 -f tds684_ -s pcx -v
convert tds684_0.pcx tds684.png
```

![TDS 684B PCX screenshot with normal colors](/assets/print_file_conversion/tds684_normal.png)

The screenshot above uses the "Normal" color setting. The scope also the the "Bold" color
setting:

![TDS 684B screenshot with bold colors](/assets/print_file_conversion/tds684_bold.png)

And there's a "Hardcopy" option as well:

![TDS 684B screenshot with hardcopy colors](/assets/print_file_conversion/tds684_hardcopy.png)

It's a matter of personal taste, but my preference is the "Normal" option.

# Advantest R3273 Spectrum Analyzer - Parallel Port - PCL Output

Next up is my Advantest R3273 spectrum analyzer.

It has a printer port, a separate parallel port that I don't know what it's used for, a
serial port, a GPIB port, and floppy drive that refuses to work. However, in the menus,
I can only configure prints to go to floppy or to the parallel port, so fake parallel
printer is what I'm using.

The print configuration menu can be reached by pressing: \[Config\] - \[Copy Config\] -> \[Printer\]:

![Advantest R3273 printer configuration screen](/assets/print_file_conversion/advantest_r3273_printer_config.png)

The R3273 supports a bunch of formats, but I had the hardest time getting it create a color bitmap.
After a lot of trial and error, I ended up with this:

```sh
~/projects/fake_parallel_printer/fake_printer.py -i -p /dev/ttyACM0 -f r3273_ -s pcl -v
gpcl6 -dNOPAUSE -sOutputFile=r3273_tmp.png -sDEVICE=png256 -g4000x4000 -r600x600 r3273_0.pcl
convert r3273_tmp.png -filter point -resize 1000 r3273_filt.png
rm r3273_tmp.png
convert r3273_filt.png -crop 640x480+315+94 r3273.png
rm r3273_filt.png
```

The conversion loses something in the process. The R3273 hardcopy mimics the shades of 
depressed buttons with a 4x4 pixel dither pattern:

![R3273 dither pattern](/assets/print_file_conversion/r3273_dither_pattern.png)

If you use a 4x4 pixel box filter and downsample by a factor of 4, this dither pattern converts
in a nice uniform gray, but the actual spectrum data in that case gets filtered down as well:

![R3273 box filtered](/assets/print_file_conversion/r3273_box_filter.png)

With the recipe above, I'm using 4x4 to 1 pixel point-sampling instead, with a phase that is chosen
just right so that the black pixels of the dither pattern get picked. The highlighted buttons are now
solid black and everything looks good.

# HP 8753C Vector Network Analyzer - GPIB - HP 8753 Companion

My HP 8753C VNA only has GPIB interface, so there's not a lot of choice there.

I'm using [HP 8753 Companion](https://github.com/VK2BEA/HP8753-Companion). It can be
used for much more than just grabbing screenshots: you can save the measured data to
a filter, upload calibration kit data and so etc.

You can render the screenshot the way it was plotted by the HP 8753C, like this:

![HP 8753C HPGL screenshot](/assets/print_file_conversion/hp8753c_hpgl.png)

Or you can display it as in a high resolution mode, like this:

![HP 8753C high resolution screenshot](/assets/print_file_conversion/hp8753c_hires.png)

Default color settings for the HPGL plot aren't ideal, but everything is configurable.

If you don't have one, the existance of HP 8753 Companion alone is a good reason to buy
a USB-to-GPIB dongle.

![HP 8753C high resolution Smith chart screenshot](/assets/print_file_conversion/hp8753c_smith_hires.png)

