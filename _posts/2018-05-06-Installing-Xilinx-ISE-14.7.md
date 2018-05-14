---
layout: post
title:  "Xilinx ISE 14.7 Installation notes"
date:   2018-05-03 22:00:00 -0700
categories: Xilinx
---

My PanoLogic Zero Client G1 has a Xilinx Spartan-3E XCS3S1600E FPGA.

The last version of Xilinx software that supports this FPGA is Xilinx ISE 14.7. (Xilinx has
since moved to Vivado, a completely different software suite.)

I have plenty of experience with Altera's Quartus, but I've never actively used ISE. 

This post contains my installation notes.

# Installation

* You have to make an account before you can download anything.
* The download page is [here](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/design-tools/v2012_4---14_7.html)
    
    There are two download options: 14.7 (Windows 10) which does NOT support the Spartan 3, and 14.7, which does.
    The second one is the only one for Linux, so that choice is easy.

* Total download size is 6.5GB. 
* Untar file...
* ./xsetup
* Select "ISE WebPACK". Diskspace required: another 17GB!
* Settings file is written to ./Xilinx/14.7/ISE_DS/settings64.csh and ./Xilinx/14.7/ISE_DS/settings64.sh
* source ./Xilinx/14.7/ISE_DS/settings64.sh
* ise

# License

* First time, this will launch Xilinx License Configuration Manager 
* After "Acquire a License" and Next, it should open a browser window and log you in to the Xilinx License manager,
  but it didn't do that for me.
  Instead I had to do that manually. Go to: https://www.xilinx.com/getlicense and follow instructions. Create "WebPack" license.
* License file will be emailed to you. Just move it to the ~/.Xilinx directory


* Create new project...

# Connect JTAG Pins

<pictures>

# Detect Device

```
jtag> cable FT2232 vid=0x0403 pid=0x6014
Connected to libftdi driver.
jtag> frequency 1000000
Setting TCK frequency to 1000000 Hz
jtag> detect
IR length: 6
Chain length: 1
Device Id: 00100001110000111010000010010011 (0x21C3A093)
  Manufacturer: Xilinx (0x093)
  Part(0):      xc3s1600e (0x1C3A)
  Stepping:     2
  Filename:     /opt/urjtag/share/urjtag/xilinx/xc3s1600e/xc3s1600e
jtag>
```



Ubuntu 12

sudo apt-get install libxi6
sudo apt-get install gitk git-gui libusb-dev build-essential libc6-dev fxload libftdi-dev

install Webpack (LabTools only doesn't work with the scripts that are used later.)


git clone usb-driver
make
setuppc

export LD_PRELOAD=~/usb-driver/libusb-driver.so

# SUCCESS !
sudo LD_PRELOAD=/home/vagrant/usb-driver/libusb-driver.so /opt/Xilinx/14.7/ISE_DS/ISE/bin/lin/impact &

