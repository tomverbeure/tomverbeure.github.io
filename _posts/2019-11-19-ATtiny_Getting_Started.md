---
layout: post
title: ATtiny - Getting Started
date:   2019-11-19 00:00:00 -0700
categories:
---


# Plugging it in

After plugging the device into the USB port, `lsusb` will list the device as follows:

```
Bus 001 Device 081: ID 16d0:0753 MCS Digistump DigiSpark
```

DigiStump created the DigiSpark as part of a very successful Kickstarter campaign.
This lead to tons of Chinese knock-offs. At the time of writing this, the Digistump
website says that they aren't taking any orders.


`dmesg -w` gives the following:

```
...
[62247.792994] usb 1-1.2: USB disconnect, device number 65
[62248.372492] usb 1-1.2: new low-speed USB device number 66 using ehci-pci
[62248.485450] usb 1-1.2: New USB device found, idVendor=16d0, idProduct=0753
[62248.485455] usb 1-1.2: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[62253.539969] usb 1-1.2: USB disconnect, device number 66
[62254.123467] usb 1-1.2: new low-speed USB device number 67 using ehci-pci
[62254.237205] usb 1-1.2: New USB device found, idVendor=16d0, idProduct=0753
[62254.237212] usb 1-1.2: New USB device strings: Mfr=0, Product=0, SerialNumber=0
[62259.298670] usb 1-1.2: USB disconnect, device number 67
[62259.882341] usb 1-1.2: new low-speed USB device number 68 using ehci-pci
[62259.997694] usb 1-1.2: New USB device found, idVendor=16d0, idProduct=0753
[62259.997702] usb 1-1.2: New USB device strings: Mfr=0, Product=0, SerialNumber=0
...
```

It's an endless loop of USB connect and disconnect every few seconds. That's probably
by design?

These ATtiny boards are already preload with a bootloader that bitbangs a low-speed USB
device on 2 of its IOs. The cool thing about that is that you don't need a programming
cable to flash new firmware into the board.

# Installing Arduino IDE

I usually prefer going bare metal instead of using the Arduino IDE, but in this case the main
goals is to get something going as fast as possible. So Arduino IDE it is...

Follow instructions here: https://digistump.com/wiki/digispark/tutorials/connecting#installation_instructions

* Download Arduino IDE from arduino.cc
* (cd tools && tar xfv ~/Downloads/arduino-1.8.10-linux64.tar.xz)

    * Note: tar decompresses .xz file automatically without the need to specify xfvz

* Set up udev permissions

    * `~/tools/arduino/arduino-linux-setup.sh $USER`
    * Create a file called `/etc/udev/rules.d/49-micronucleus.rules` with the following content:

```
# UDEV Rules for Micronucleus boards including the Digispark.
# This file must be placed at:
#
# /etc/udev/rules.d/49-micronucleus.rules    (preferred location)
#   or
# /lib/udev/rules.d/49-micronucleus.rules    (req'd on some broken systems)
#
# After this file is copied, physically unplug and reconnect the board.
#
SUBSYSTEMS=="usb", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="0753", MODE:="0666"
KERNEL=="ttyACM*", ATTRS{idVendor}=="16d0", ATTRS{idProduct}=="0753", MODE:="0666", ENV{ID_MM_DEVICE_IGNORE}="1"
#
# If you share your linux system with other users, or just don't like the
# idea of write permission for everybody, you can replace MODE:="0666" with
# OWNER:="yourusername" to create the device owned by you, or with
# GROUP:="somegroupname" and mange access using standard unix groups.
```

* Reload udev permisssions: 

    * `sudo udevadm control --reload-rules`

* Launch IDE

    * `~/tools/arduino/arduino`

* Add board manager for Digispark

    * File -> Preferences -> Additional Boards Manager URLs: `http://digistump.com/package_digistump_index.json`
    * You can have multiple URL there. One per line.

* Install Digispark support library

    * Tools -> Board -> Board Manager -> Type: Contributed -> Digistump AVR Boards -> Install

* Select Digispark board
    * Tools -> Board -> Digispark (Default - 16.5 MHz)

* Load the Digispark Blinky Example
    
    * File -> Examples -> Digispark_Examples -> Start

* Compile 

    * Sketch -> Verify/Compile

* Upload

    * Unplug Digispark board from USB
    * Sketch -> Upload
    * Plug in Digispark board into USB
    * The design will start downloading if all goes well
    * LED will start blinking

# Boot Sequence

After powering up, the boot loader inside the Digispark ATtiny85 will wait for 4 second to see if a USB host tries to
program its flash.

If so, the flash gets programmed, and then the newly flashed programmed is executed.

If the host does NOT try to program the flash (or if the host doesn't even try to enumerate the USB device because
the Digispark board is powered by something else than USB), then the boot loader starts executing whatever program
is already in the flash.

When the board is already plugged in, and it's in non-programming mode, then you need to plug it in and out of the USB
port to put it back into programming mode (for 4 seconds.)



