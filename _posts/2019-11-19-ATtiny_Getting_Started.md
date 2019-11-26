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

* Download Arduino IDE from arduino.cc
* (cd tools && xc -d -c <filename> | tar xfv - .)
* Set correct udev permissions
* Follow instructions here: https://digistump.com/wiki/digispark/tutorials/connecting#installation_instructions
* Select Digispark (Default - 16.5 MHz)
* Load blinky sketch
* Upload -> Success

# 


