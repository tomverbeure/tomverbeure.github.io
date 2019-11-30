---
layout: post
title:  "Altera Quartus Install on Ubuntu 16.04"
date:   2018-04-08 00:00:00
categories:
---

Since the eeColor Color3 board uses an Altera Cyclone IV chip, you need Quartus for all FPGA related activities.

I'm using OS X on my lab PC (it's a beautiful old beast of Mac Pro), and since Quartus only runs under Windows 
or Linux, I need to install a virtual machine.

Here's my setup:

* VirtualBox as virtual machine
* Vagrant to manage the whole thing
  * X11 enabled
  * xenial64 image, which uses Ubuntu 16.04.4
* XQuartz to use OS X a X server

The Cyclone IV is supported by the latest version of Quartus (17.1 as I write this), but I'm installing version
13.0sp1 instead: this is the last version that also supports a Cyclone II. And since I have already have one of 
those popular 
[EP2C5 mini development boards](http://land-boards.com/blwiki/index.php?title=Cyclone_II_EP2C5_Mini_Dev_Board), 
I need support for that as well.

So 13.0sp1 it is. You can find it [here](http://fpgasoftware.intel.com/13.0sp1/) on the Intel website.

When downloading, you'll always be greeted with the terrible Altera download manager. Cancel that, and just download the
individual .run file.

To limit space, I only download the following files:

```
QuartusSetupWeb-13.0.1.232.run
cyclone_web-13.0.1.232.qdz
```

If you want to use ModelSim Lite for simulations, you can also download that one:

```
ModelSimSetup-13.0.1.232.run
```

But I use open source tools for simulation instead: iverilog, verilator, and gtkwave.

If you run QuartusSetupWeb right after downloading, it will not work. 
This is because Quartus Lite 13.0sp1 runs in good old 32-bit mode.

So to fix that, you first need to install the 32-bit version of libc6. Like this:

```
sudo apt-get install libc6-i386
```

Once you run ./QuartusSetupWeb..., you'll have to press [ENTER] about a hundred times to get though the licenses.

At the end, you need to select which packages to install. Here's how it looks for me:

Select the components you want to install

```
Quartus II Web Edition (Free)  [Y/n] 
Quartus II Web Edition (Free)  - Quartus II Software (includes Nios II EDS) (4424MB) : Y (Cannot be edited)
Quartus II Web Edition (Free)  - Quartus II Software 64-bit support (1090MB) [Y/n] :Y
Quartus II Web Edition (Free)  - Devices [Y/n] :Y
Quartus II Web Edition (Free)  - Devices - Cyclone II/III/IV (615.2MB) [Y/n] :Y
ModelSim-Altera Starter Edition (Free) (3547.1MB) [Y/n] :n
ModelSim-Altera Edition (3547.1MB) [y/N] :N
Is the selection above correct? [Y/n]:Y

----------------------------------------------------------------------------
Ready to Install

Summary:
  Installation directory: /home/vagrant/altera/13.0sp1
  Required disk space:  6129 MB
  Available disk space: 8433 MB
```

It's important that you also install the 64-bit version of Quartus II: the 32-bit version requires a lot of standard 
Linux libraries that are simply not supported by Ubuntu 16.04.

When everything is said and done, the installer will ask you if it's ok to start Quartus 64bit. Enter Y and you're good to go.

And then after you quit, it won't really work anymore, because you need to setup your environment:

In `~/.profile`:

```
export QUARTUS_ROOTDIR="/home/vagrant/altera/13.0sp1/quartus"
PATH="$PATH:$QUARTUS_ROOTDIR/bin"
```

In `~/.bash_aliases`:

```
alias quartus='quartus --64bit'
```

Install 32-bit packages for your 64-bit Ubuntu:

```
sudo dpkg --add-architecture i386
sudo apt-get update
sudo apt-get install libc6:i386 libncurses5:i386 libstdc++6:i386 libpng12-0:i386 libfreetype6:i386 libsm6:i386 libxrender1:i386 libfontconfig1:i386 libxext6:i386 libxtst6:i386 libxi6:i386 libgtk2.0-0:i386
```

We need the 32-bit packages because some parts of Quartus such as Qsys are still completely 32-bit based for 13.0sp1.

You will also need to configure your machine to give permissions for the USB Blaster cable. The instructions on 
[this page](http://www.fpga-dev.com/altera-usb-blaster-with-ubuntu/) worked for me, but I had to reboot the machine 
after completing the steps.

Finally, if you want to run any nios2 related tools, you need execute this:

```
$QUARTUS_ROOTDIR/../nios2eds/nios2_command_shell.sh
```

TODO: put all of this simply in the Vagrantfile.

