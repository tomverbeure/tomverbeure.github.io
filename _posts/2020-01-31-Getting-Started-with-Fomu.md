---
layout: post
title: Getting Started with Fomu
date:  2020-01-31 00:00:00 -0700
categories:
---

# Fomu Under the Hood

The powerup configuration sequence of most FPGA board is very straightforward: as soon as the main power 
rail is up, the FPGA automatically checks for the presence of an SPI flash device to its configuration
pins, and when so, it downloads the one and only bitstream from this flash device and gets going.

If a developer wants to program a bitstream with his custom design, they use some kind of programming cable
to replace the bitstream in the SPI flash with their own, and that is that.

This simple scheme wouldn't work with Fomu: it doesn't have any interface other than the USB pins that
are used to power the device and communicate with its host.

And yet, an iCE40 UltraPlus FPGA like the one used in Fomu has at its core the same initial powerup sequence.

So how does that work?

The answer lies in multi-stage booting: most iCE40 FPGAs have a feature called "Multi Configuration Image", also called
"multi-boot". (You can read all about it in the 
[iCE40 Programming and Configuration Technical Note](http://www.latticesemi.com/~/media/LatticeSemi/Documents/ApplicationNotes/IK/iCE40ProgrammingandConfiguration.pdf).

During intial powerup, "cold boot", the FPGA loads a first bitstream, as usual, but the design of this bitstream can then
decided to wipe itself from the FPGA, and load one of 4 a completely different secondary bitstreams of its own choosing, at
any later point in time. These are called "warm boot" images.

The cold boot design of Fomu is called the Fomu bootloader. You can find its design in the 
[`foboot`](https://github.com/im-tomu/foboot) GitHub repo.

The bootloader is a pretty elaborate piece of work. 

It contains a small SOC (System on Chip) with a VexRiscV RISC-V CPU, debug UART, timer, SPI interface, LED control, and,
most important, a USB device interface. The SOC is created using a Python-based SOC builder called Litex. You
can find the code [here](https://github.com/im-tomu/foboot/blob/master/hw/foboot-bitstream.py).

The SOC runs the bootloader firmware.

The firmware has a whole bunch of options, but at its core, it runs the Fomu in Device Firmware Update (DFU) mode, where
the USB device is configured as a DFU class device that reacts to request from the open source 
[`dfu-util` utilities](http://dfu-util.sourceforge.net/).

For those who want to develop something fun with the Fomu, the two most important features of the bootloader are
the ability to flash a new warm boot bitstream in the SPI flash, and to instruct the bootloader to switch to this
warm boot bitstream.

Once the FPGA has switched to the warm boot bitstream, all traces of the bootloader are gone, and with it all its
functionality. The only way to get back to the initial state is to power cycle the FPGA, but resetting the USB port
of the Fomu or by removing and reinserting it into the USB port.

It is *extremely* important that the bootloader of the Fomu doesn't get accidentally overwritten by different
bitstream: this will brick the device and there is no easy way to recover from it! The bootloader is written
defensively, with no way to accidentally do this, but your own design uses the SPI flash as a storage device
and mistakenly corrupts the bootload, you'll have a problem!


# Plugging in Fomu

Fomu comes preloaded with an FPGA design that contains the following:

	*

When I plugged it into the USB port of my Ubuntu laptop, `dmesg` showed the following:

```
$ dmesg
...
[176543.140259] usb 1-1.2: new full-speed USB device number 7 using ehci-pci
[176543.262503] usb 1-1.2: New USB device found, idVendor=1209, idProduct=5bf0, bcdDevice= 1.01
[176543.262511] usb 1-1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[176543.262514] usb 1-1.2: Product: Fomu DFU Bootloader v1.8.6
[176543.262518] usb 1-1.2: Manufacturer: Foosn
```

And here's the output of `lsusb`: 
```
$ lsusb
...
Bus 001 Device 007: ID 1209:5bf0 InterBiometrics 
...
```

Interesting side story: InterBiometrics received the USB vendor ID of 0x1209 before the USB licensing
agreement prohibited sublicensing a vendor ID to others. Their vendor ID can now be used for open
source hardware projects that need a USB vendor ID/product ID combination. You can read all
about this [here](http://pid.codes/about/).

# Installing Fomu Toolchain

There are pre-built full releases for different operating systems. 

TDownload the latest release [here](https://github.com/im-tomu/fomu-toolchain/releases/), extract
it and set your path:

```
cd tools
tar xfvz ~/Downloads/fomu-toolchain-linux_x86_64-v1.5.3.tar.gz
export PATH=~/tools/fomu-toolchain-linux_x86_64-v1.5.3/bin/:$PATH
```

Clone workshop repo


Set environment variable based on your Fomu board:

```
export FOMU_REV=hacker
```

Upgrade bootloader to latest version: https://workshop.fomu.im/en/latest/bootloader.html

```
$ dfu-util -D ~/Downloads/hacker-updater-v2.0.3.dfu 
dfu-util 0.9

Copyright 2005-2009 Weston Schmidt, Harald Welte and OpenMoko Inc.
Copyright 2010-2019 Tormod Volden and Stefan Schmidt
This program is Free Software and has ABSOLUTELY NO WARRANTY
Please report bugs to http://sourceforge.net/p/dfu-util/tickets/

Match vendor ID from file: 1209
Match product ID from file: 70b1
Opening DFU capable USB device...
ID 1209:5bf0
Run-time device DFU version 0101
Claiming USB DFU Interface...
Setting Alternate Setting #0 ...
Determining device status: state = dfuIDLE, status = 0
dfuIDLE, continuing
DFU mode device DFU version 0101
Device returned transfer size 1024
Copying data from PC to DFU device
Download	[=========================] 100%       112828 bytes
Download done.
state(7) = dfuMANIFEST, status(0) = No error condition is present
state(8) = dfuMANIFEST-WAIT-RESET, status(0) = No error condition is present
Done!
```

After this, dfu-util will report the correct bootloader version:
```
$ dfu-util -l
dfu-util 0.9

Copyright 2005-2009 Weston Schmidt, Harald Welte and OpenMoko Inc.
Copyright 2010-2019 Tormod Volden and Stefan Schmidt
This program is Free Software and has ABSOLUTELY NO WARRANTY
Please report bugs to http://sourceforge.net/p/dfu-util/tickets/

Found DFU: [1209:5bf0] ver=0101, devnum=30, cfg=1, intf=0, path="1-1.2", alt=0, name="Fomu Hacker running DFU Bootloader v2.0.3", serial="UNKNOWN"
```

# Micropython

Load MicroPython bitstream:
```
dfu-util -D micropython-fomu.dfu
```
This load the bitstream but doesn't flash it.

```
sudo screen /dev/ttyACM0
```
Note: `sudo` seems to be required. Doesn't work without it.


# 

# Resources

* [Fomu Crowd Supply page](https://www.crowdsupply.com/sutajio-kosagi/fomu)

    Go here to buy your Fomu.

* [Fomu on the Tomu Family website](https://tomu.im/fomu.html)

    Link to all the repositories for hardware tools etc.

* [FPGA MicroPython](https://fupy.github.io/)

    Tiny version of MicroPython that works on a LiteX based SOC.


# Issue

* The documentation is non-linear. Instead of links to a manual or a getting started page, there are links to 
  github repos that link to such a manual.  
* If you start with the workshop, it starts by using dfu-util to show the version of the bootload, but dfu-util
  doesn't work yet because udev hasn't yet been set up correctly.
* It mentions that you can either use udev or use sudo, but dfu-util doesn't work with sudo. ("Failed to 
  retrieve language identifiers.")
```
Failed to retrieve language identifiers
Found DFU: [1209:5bf0] ver=0101, devnum=12, cfg=1, intf=0, path="1-1.2", alt=0, name="UNKNOWN", serial="UNKNOWN"
```
* There is no clear description that tells me how the Fomu hacker is different from the Fomu PVT in terms of
  practical usage.
* The "Failed to retrieve language identifiers" error might be due to incorrect boot-loader?
* Ran into the following issue repeatedly. It got solved by plugging the device in and out until
  it started working. Then I immediately did a `dfu-util` update of the bootloader.

```
$ dmesg -w
...
[ 3572.923873] usb 1-1.2: new full-speed USB device number 22 using ehci-pci
[ 3573.037564] usb 1-1.2: New USB device found, idVendor=1209, idProduct=5bf0, bcdDevice= 1.01
[ 3573.037581] usb 1-1.2: New USB device strings: Mfr=1, Product=2, SerialNumber=0
[ 3573.037586] usb 1-1.2: Product: Fomu DFU Bootloader v1.8.6
[ 3573.037591] usb 1-1.2: Manufacturer: Foosn
[ 3573.119887] usb 1-1.3: new full-speed USB device number 23 using ehci-pci
[ 3573.199885] usb 1-1.3: device descriptor read/64, error -32
[ 3573.387883] usb 1-1.3: device descriptor read/64, error -32
[ 3573.575894] usb 1-1.3: new full-speed USB device number 24 using ehci-pci
[ 3573.655868] usb 1-1.3: device descriptor read/64, error -32
[ 3573.843839] usb 1-1.3: device descriptor read/64, error -32
[ 3573.952286] usb 1-1-port3: attempt power cycle
...
```
* `rustup` command included the `$` in front of it when clicking 'click to copy'.
* After installing rust via the recommended way, `cargo` is still not there. And when doint 'apt-get install cargo',
  it installs rust again.
* Following error when trying to compile rust example:
```
tom@tom-ThinkPad-X220:~/projects/fomu-workshop/riscv-rust-blink$ cargo build --release
error: failed to parse lock file at: /home/tom/projects/fomu-workshop/riscv-rust-blink/Cargo.lock

Caused by:
  invalid serialized PackageId for key `package.dependencies`
tom@tom-ThinkPad-X220:~/projects/fomu-workshop/riscv-rust-blink$ 
```

