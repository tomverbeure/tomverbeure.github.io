---
layout: post
title: JTAG Dongle Review
date:   2019-09-18 10:00:00 -0700
categories:
---

# Altera USB-Blaster 2

With a [DigiKey price](https://www.digikey.com/products/en?mpart=PL-USB2-BLASTER&v=544) of $225 a piece, 
the Intel/Altera USB-Blaster II is the most expensive JTAG dongle that I could get my hands on. 

![USB-Blaster2-Overview]({{ "/assets/jtag_dongles/USB-Blaster2-Overview.png" | absolute_url }})

For a change, this is the real thing: designed and sold under the Intel brand.

The successor of the original USB-Blaster in package of similar size, it has the 
following changes:

* micro-USB connector
* programmable JTAG clock speeds of  24MHz, 12MHz, or 6MHz (vs 6 MHz only for the USB-Blaster).
* higher quality wiring between dongle and Altera JTAG connector resulting in better signal quality

Looking at the internal, the whole thing seems to be ridiculously over-engineered, with a
main PCB and a daughterboard plugged into it.

![USB-Blaster2-Both Boards]({{ "/assets/jtag_dongles/USB-Blaster2-Both_Boards.png" | absolute_url }})

The main board has a [Cypress CY7C68013A](https://www.cypress.com/file/138911/download) EZ-USB 
microcontroller and an [Intel EPM570M100C4N MAX-II CPLD](https://www.intel.com/content/dam/www/programmable/us/en/pdfs/literature/pt/max-v-n-ii-cpld-features.pdf).

![USB-Blaster2-Main Board]({{ "/assets/jtag_dongles/USB-Blaster2-Main_Board.png" | absolute_url }})

The daughter card contains a couple of voltage translators/drivers of some sort.

![USB-Blaster2-Daughter Board]({{ "/assets/jtag_dongles/USB-Blaster2-Daughter_Board.png" | absolute_url }})

Here's how it gets listed with `lsusb`:

```
    Bus 001 Device 043: ID 09fb:6010 Altera 
```

It has OpenOCD support using the `altera-usb-blaster2.cfg` interface, but only the maximum speed of 24MHz is
supported.
*There is no OpenOCD command to switch the JTAG clock to 12MHz or 6MHz!*

So what do we get in return for our $225? A very clean signal with almost no reflection.

![USB-Blaster2-Signal Quality]({{ "/assets/jtag_dongles/USB-Blaster2-Signal_Quality.png" | absolute_url }})

The total bitstream load time was 236ms. Not best in class, but about where you'd expect for a 24MHz clock speed.
This 236ms includes an idle time of ~40ms between the start of the transaction and the continuous burst of data,
so for a much larger bitstream, the result will be considerably better.


# Blue Pill as USB Blaster

* Ridiculously complete overview of JTAG clones: https://wiki.cuvoodoo.info/doku.php?id=jtag

* Download GNU Arm Embedded toolchain: https://developer.arm.com/tools-and-software/open-source-software/developer-tools/gnu-toolchain/gnu-rm/downloads  
    * I downloaded https://developer.arm.com/-/media/Files/downloads/gnu-rm/9-2020q2/gcc-arm-none-eabi-9-2020-q2-update-x86_64-linux.tar.bz2
    * gcc-arm-none-eabi-8-2018-q4-major crashes with an internal compiler error!

* GitHub:
    * original: https://github.com/Icenowy/USB-Blaster-GCC
    * useful forks: 
        * Support for "ARMJISHU USB-Blaster": https://github.com/rmaxmu/USB-Blaster-GCC
        * Support for "JTAGPILL": https://github.com/sztsian/USB-Blaster-GCC

```
cd ~/tools
bunzip2 -c ~/Downloads/gcc-arm-none-eabi-9-2020-q2-update-x86_64-linux.tar.bz2 | tar xfv -
export PATH=~/tools/gcc-arm-none-eabi-9-2020-q2-update/bin:$PATH
git clone https://github.com/Icenowy/USB-Blaster-GCC
cd USB-Blaster-GCC
export CROSS_COMPILE=arm-none-eabi-
```

Edit Makefile:
```
usb-blaster.axf: $(startup-object) $(drv-objects) $(sys-objects) $(usb-objects) $(src-objects) $(stdperiph-objects) $(fsusb-objects) /home/tom/tools/gcc-arm-none-eabi-9-2020-q2-update/lib/gcc/arm-none-eabi/9.3.1/libgcc.a
```

```
make
```


