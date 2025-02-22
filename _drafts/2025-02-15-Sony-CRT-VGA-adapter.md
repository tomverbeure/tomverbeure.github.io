---
layout: post
title: A VGA adapter board for the Sony CHM-9001-00 Trinitron CRT 
date:  2025-02-15 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

![VGA adapter board soldered](/assets/hp16500a/blog_vga_adapter/vga_adapter_board.jpg)

More than 2 years ago, I extracted 
[an 8" Sony Trinitor CRT from an HP 16500A](/2022/10/05/Sony-CHM-9001-00-CRT.html)
logic analyzer boat anchor and managed to get it to work with a 120V DC/DC convertor
and the VGA output of my X220 laptop. While there was still some unfinished business,
creating a usable and portable retro-gaming monitors, I didn't expect there to be
a follow up: too many projects, too little time.

A chance encounter with a retired power supply design engineer changed that and a
future blog post will be dedicated to the design of a custom power supply. But I also
wanted to make the monitor easier to use. 

As [described in the old blog post](/2022/10/05/Sony-CHM-9001-00-CRT.html#connecting-the-crt-to-a-vga-port), 
the Sony CRT has fixed custom timings that are not compatible with standard monitors. Most
important, with a native resolution of just 576x368@60Hz, the pixel clock of 20MHz is too
low for the PLL that resides in the GPU of my X220 laptop. The solution to that is double
all the horizontal timings, which ups that pixel clock to 40MHz. The CRT itself is none
the wiser: it only sees timings in absolute terms and doesn't see the actual clock.

I used the Linux `xrandr` command to program the correct timings and was able to drive
the CRT with the laptop:

![Sony CRT driven with X220 laptop](/assets/hp16500a/blog_crt/crt_powered_by_B900W.jpg)

But the setup was yanky. In addition to the cobbled together power supply and the `xrandr`
commands, there was also a fragile adapter board to convert from a VGA connector to the
40-pin IDC connector that's used by the CRT.

![VGA to 40-pin IDC converter board](/assets/hp16500a/blog_crt/vga_crt_cable.jpg)

Since I had already a PCB ready for the new 120V DC/DC power supply, I also created a convert
PCB with an additional twist: an I2C EDID EEPROM.

In this blog post, I describe the PCB, the how and why of an EDID EEPROM, how to program an I2C EEPROM 
over a VGA cable and the fix of a broken CRT.

# The VGA to 40-pin Adapter 

You can find the KiCAD design database for this project [here XXXXXX](XXX).

The schematic of the adapter is straightforward:

* a female VGA DB-15 receptacle
* a 40-pin IDC receptable
* a 256-byte EEPROM
* some jumpers
* a 5-pin debug and programming connector

[![KiCAD schematic of the adapter](/assets/hp16500a/blog_vga_adapter/vga_40pin_adapter_schematic.png)](/assets/hp16500a/blog_vga_adapter/vga_40pin_adapter_schematic.png)
*Click to enlarge*

It will forever remain a mystery why Sony decided to use a 40 wire flat cable to connector
5 signals with the remaining wires connected to ground, but that's what they did.

The 256-byte I2C EEPROM is connected to the DDC/CI pins of the VGA connector which uses
the standard I2C protocol as well. I2C requires pull-up resistors on the SCL clock and SDA 
data lines. Section 9.4 of the [VESA DDC/CI standard](https://glenwing.github.io/docs/VESA-DDCCI-1.1.pdf)
requires pull-up resistors of no less than 2.2 kOhm at the host side (e.g. my laptop) and
section 9.2 recommends 12 to 15 kOhm pull-up resistors on the display side.

![DDC/CI pullup resistors](/assets/hp16500a/blog_vga_adapter/ddc_ci_pullup_resistors.png)

I added 2 jumpers: one to enable EEPROM write protection and another one to disconnect
the SDA data line entirely, in case I want the EEPROM to not be visible to the GPU.

![VGA adapter board PCB layout](/assets/hp16500a/blog_vga_adapter/vga_adapter_pcb.png)

I didn't bother with impedance matching the signals on the 2 layer PCB. When driven at
native 572x368 resolution, the data rate won't be any higher than 20MHz.

Here's the board after soldering everything together:

![VGA adapter board soldered](/assets/hp16500a/blog_vga_adapter/vga_adapter_board.jpg)

# An EDID with Custom Video Timings

Since way back in the 1990s, monitors have an I2C EEPROM that contains 
[Extended Display Identification Data (EDID)](https://en.wikipedia.org/wiki/Extended_Display_Identification_Data).
It contains items such as:

* 16-bit vendor and product IDs
* serial number
* physical dimensions
* supported video timings
* color space information
* audio support information 

and more.

Instead of messing around with `xrandr` commands to make my laptop output the right
timings, I wanted everything to be plug and play: insert the VGA cable and everything
just works.

[Analog Way](https://www.analogway.com) has the freely downloadable 
[AW EDID Editor](https://www.analogway.com/products/aw-edid-editor) to create your own EDID binaries.

I filled in the timing values that I derived in my previous blog post:

[![Aw EDID Editor screenshot](/assets/hp16500a/blog_vga_adapter/aw_edid_editor.png)](/assets/hp16500a/blog_vga_adapter/aw_edid_editor.png)
*Click to enlarge*

It's common for modern EDID files to be 256 bytes or more, but since this monitor only supports
a single video timing everything fits in 128 bytes. You can find the file [here XXXXX](XXX).

# Programming the I2C EEPROM through the VGA cable

I added a test connector with the I2C data lines on the PCB

```
sudo apt install i2c-tools
```

```sh
i2cdetect -l
```

```
i2c-0	unknown   	SMBus I801 adapter at efa0      	N/A
i2c-1	unknown   	i915 gmbus ssc                  	N/A
i2c-2	unknown   	i915 gmbus vga                  	N/A  <<<
i2c-3	unknown   	i915 gmbus panel                	N/A
i2c-4	unknown   	i915 gmbus dpc                  	N/A
i2c-5	unknown   	i915 gmbus dpb                  	N/A
i2c-6	unknown   	i915 gmbus dpd                  	N/A
i2c-7	unknown   	AUX B/DP B                      	N/A
i2c-8	unknown   	AUX C/DP C                      	N/A
i2c-9	unknown   	AUX D/DP D                      	N/A
```


```sh
sudo i2cdetect -y 2
```
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: 50 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
```

```sh
sudo i2cdump -y 2 0x50
```

```
No size specified (using byte-data access)
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f    0123456789abcdef
00: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
10: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
20: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
30: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
40: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
50: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
60: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
70: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
80: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
90: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
a0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
b0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
c0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
d0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
e0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
f0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
```


# References

* [HP 16500A/16501A Service Manual][HP 16500A Service Manual]
* [Sony CHM-9001 Service Manual](/assets/hp16500a/sony-chm-9001-00-service-manual.pdf)

[HP 16500A Service Manual]: /assets/hp16500a/HP16500-90911-Service-Manual.pdf

