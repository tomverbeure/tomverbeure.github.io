---
layout: post
title: Tektronix TDS 420A Remote Control over GPIB
date:   2020-06-27 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

In [my earlier post](/2020/06/27/In-the-Lab-Tektronix-TDS420A.html), I introduced my 'new'
Tektronix TDS 420A oscilloscope, which I bought to add Tektronix support to 
[glscopeclient](https://hackaday.com/2019/05/30/glscopeclient-a-permissively-licensed-remote-oscilloscope-utility/).

![glscopeclient](/assets/tds420a/glscopeclient.png)

The first step in that process is to get my PC to talk to the scope through the GPIB interface.

It's not a complicated process, and there's quite a bit of information online that describes how
to do this, but in this post I go through the gory detail how to get from nothing to fetching recorded
waveforms from the scope onto your PC.

From unpacking the scope, it only took about 30 minutes and 95% of that time was *obviously* spent 
getting Linux drivers right.

# Acquiring a USB to GPIB Dongle

[GPIB](/2020/06/07/Making-Sense-of-Test-and-Measurement-Protocols.html#gpib--ieee-488)
is an obsolete interface standard. All modern test and measurement equipment comes with with
an Ethernet and/or a USB port. But not too long ago, virtually all equipment had GPIB support,
and most of the equipment you'll buy second hand on eBay will come with one.

The sturdy, specialized GPIB connector itself was already quite expensive
back in the day, so a full GPIB interface card or dongle was never cheap.

You can find [UGPlus](http://www.lqelectronics.com/Products/USBUG/UGPlus/UGPlus.html) USB to
GPIB controllers for around $40 on Amazon, but they aren't supported on Linux.

The cheapest Linux supported option that I could find was an 
[Agilent/Keysight 82375B](https://www.keysight.com/en/pd-851808-pn-82357B/usb-gpib-interface-high-speed-usb-20).
They're listed for $624 on the Keysight website, but you should be able to find one for ~$70 on eBay
or AliExpress.

Not wanting to wait for weeks for a shipment from China, I bought a 
[National Instruments GPIB-USB-HS](https://www.ni.com/en-us/support/model.gpib-usb-hs.html) instead. 
Instead of the $1059 list price, I got mine for $100 on eBay. 

# Installing the GPIB-USB-HS Linux Kernel Driver

It's hard to believe, but despite supporting pretty much any kind of device imaginable, the 
main line Linux kernel doesn't have any support for GPIB interfaces.

Luckily, there is the [Linux GPIB Package](https://linux-gpib.sourceforge.io/) which contains driver modules for
a variety of such interfaces, as well as whole bunch of user mode libraries and test programs.

**One major downside of the method described below is that you need to recompile and reinstall the driver 
whenever there's even a minor update of the Linux kernel. It's not a lot of work, just a very annoying
distraction.**

Here's the recipe that worked for my Ubuntu 18.04 distribution:

* Install Linux Kernel Headers

    ```
sudo apt-get install linux-headers-$(uname -r)
    ```

In theory, you will need to redo this step whenever you upgrade your kernel to a later version.

* Download the latest version of the Linux-GPIB package

    ```
cd ~/projects
svn checkout svn://svn.code.sf.net/p/linux-gpib/code/trunk linux-gpib-code
cd linux-gpib-code/linux-gpib-kernel
    ```

    Yes: `svn`. Some projects still use it. I had to install it on my machine just for this.

* Compile and install

    ```
make
sudo make install
    ```

    This will install a whole bunch of gpib drivers in `/lib/module/<kernel version>/gpib`:

    ```
cd /lib/modules/5.3.0-53-generic/gpib
find .
.
./cec
./cec/cec_gpib.ko
./agilent_82357a
./agilent_82357a/agilent_82357a.ko
./ni_usb
./ni_usb/ni_usb_gpib.ko
./hp_82341
./hp_82341/hp_82341.ko
./lpvo_usb_gpib
./lpvo_usb_gpib/lpvo_usb_gpib.ko
./ines
./ines/ines_gpib.ko
./sys
./sys/gpib_common.ko
./tnt4882
./tnt4882/tnt4882.ko
./nec7210
./nec7210/nec7210.ko
./agilent_82350b
./agilent_82350b/agilent_82350b.ko
./cb7210
./cb7210/cb7210.ko
./tms9914
./tms9914/tms9914.ko
./hp_82335
./hp_82335/hp82335.ko
    ```

* Install the appropriate GPIB driver into the kernel

    For the GPIB-USB-HS, that's the `ni_usb_gpib` driver:

    ```
sudo modprobe ni_usb_gpib
    ```

* Check that the driver gets loaded

    Plug in your GPIB USB dongle, and check what happens with `dmesg`:

    ```
dmesg -w
[63517.842042] usb 1-11.4: new high-speed USB device number 17 using xhci_hcd
[63517.957147] usb 1-11.4: New USB device found, idVendor=3923, idProduct=709b
[63517.957151] usb 1-11.4: New USB device strings: Mfr=1, Product=2, SerialNumber=3
[63517.957154] usb 1-11.4: Product: GPIB-USB-HS
[63517.957156] usb 1-11.4: Manufacturer: National Instruments
[63517.957158] usb 1-11.4: SerialNumber: 0120F5DE
[63517.975852] gpib_common: loading out-of-tree module taints kernel.
[63517.975897] gpib_common: module verification failed: signature and/or required key missing - tainting kernel
[63517.976571] Linux-GPIB 4.3.3 Driver
[63517.977564] ni_usb_gpib driver loading
[63517.977585] ni_usb_gpib: probe succeeded for path: usb-0000:00:14.0-11.4
[63517.977620] usbcore: registered new interface driver ni_usb_gpib
[63517.977621] gpib: registered ni_usb_b interface
    ```

Success!

But we're not there yet. We still need to install a bunch of user mode libraries and utilities.

# GPIB - Installing the User Mode Library and Utilities

The National Instrument GPIB USB dongles have small microcontroller on them that needs its
own firmware. This firmware must be loaded into the dongle before the dongle is able to behave
as a GPIB interface. The firmware, and the utility to load it into the dongle, is part of the
same Linux GPIB package that also contained the kernel above.


I used the following recipe:

* Compile and install the whole thing:

    ```
    cd linux-gpib-user
    ./bootstrap
    ./configure
    make
    sudo make install
    sudo ldconfig
    ```

    This will install an important configuration file in `/usr/local/etc/gpib.conf`.

    If you want the location of this file to be under `/etc` instead, you can do so with
    by using `./configure --sysconfdir=/etc`.

* Update the `/usr/local/etc/gpib.conf` configuration file

    In my case, all I had to do was change `board_type = "ni_pci"` to `board_type = "ni_usb_b"`.

* Load firmware into the dongle

    `sudo gpib_config`

# Set the GPIB Device Address on the TDS 420A

The GPIB protocol supports up to 31 devices on a single cable daisy chain. But there's no plug
and play here, the address of each device needs to be assigned manually.

![Change GPIB Address](/assets/tds420a/change_gpib_address.png)

On the TDS 420A, you do this as follows. (See also the
[user manual](https://www.tek.com/oscilloscope/tds420a-manual/tds410a-tds420a-tds460a-user-manual) on page 3-91.)

* Press SHIFT UTILITY -> System (main) -> I/O (pop-up) -> Port (main) -> GPIB (pop-up) -> Configure (main) -> Talk/Listen Address

I selected address 1.

# First Contact!

We can now finally test the whole connection.

The Linux GPIB package comes with a number of utilities, one of which is `ibtest`. Let's give it a try:

* `sudo ibtest`

    `udev` permission haven't been set yet, so, for now, let's run it as root.

* `d` (for 'device)

    `ibtest` can be used to talk to a GPIB connected device (like our scope) or to the GPIB interface dongle itself.

* `1` for GPIB address

    This is obviously the address that was assigned earlier into the scope.

* `w` : write string to scope

* `*IDN?`

    This is the standard SCPI command that returns an identification string.

* `r` : read the reply from the scope
* `1024`
* Result:

    ```
: r
enter maximum number of bytes to read [1024]: 1024
trying to read 1024 bytes from device...
received string: 'TEKTRONIX,TDS 420A,0,CF:91.1CT FV:v1.0.2e
'
Number of bytes read: 42
gpib status is:
ibsta = 0x2100  < END CMPL >
iberr= 0
    ```

    We have successfully received the identification info from the scope: manufacturer,
    product name, revision number and firmware version.

# Setting Up UDEV rules

`udev` rule set user permissions and can do all kinds of funky stuff behind the scenes.

It took me ages to get things working, and reloading the rules with `sudo udevadm control --reload` was not
sufficient: *a reboot was necessary*!

Create a file called `/etc/udev/rules.d/72-linux_gpib_ni_usb.rules`:

```
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="3923", ATTRS{idProduct}=="709b", MODE="666", GROUP="tom", SYMLINK+="usb_gpib"
SUBSYSTEMS=="usb", ACTION=="add", ATTRS{idVendor}=="3923", ATTRS{idProduct}=="709b", RUN+="/usr/local/sbin/gpib_config"
KERNEL=="gpib[0-9]*", MODE="666", GROUP="tom"
```

You will need to change `GROUP"tom"` to something else.

Earlier, we called `sudo gpib_config` to load the GPIB-USB-HS firmware into the device. The second in the udev
parameters above now does that automatically as soon as you plug in the GPIB dongle in the USB port.

Reboot your machine, unplug the USB cable of the dongle and plug it back in, and try out `ibtest`, but this
time without prefixing it with `sudo`.

Does it work? Congratulations! You're ready to start fetching waveforms from the scope!


# The GPL3 License of the Linux-GPIB Package

The user mode libraries are licensed under the GPL 3.0, which means that projects with a less restrictive
open source license can't just be built with the Linux GPIB library without applying the GPL 3.0 license
to the whole project.

There is a good discussion about this [here](https://opensource.stackexchange.com/questions/1640/if-im-using-a-gpl-3-library-in-my-project-can-i-license-my-project-under-mit-l)
on Stackoverflow.

For my purposes, this isn't a huge deal: instead of writing a GPIB backend for scopehal/glscopeclient, I want
to write a TCP/IP to GPIB server. glscopeclient already has a socket based transport driver, so it
using such a server, no additional transport driver would need to be written.


