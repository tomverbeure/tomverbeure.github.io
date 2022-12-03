---
layout: post
title: Raspberry Pi as GPIB Server
date:  2022-11-30 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Steps

* [Raspberry Pi OS Installation](https://www.raspberrypi.com/documentation/computers/getting-started.html#installing-the-operating-system)

    * In my case, rpi-imager wasn't available, so I followed the compilation instructions 
      [here](https://github.com/raspberrypi/rpi-imager).
    * Start rpi-imager
    * In advanced settings
	* Enable SSH
	* Create username 'pi' with password
	* Configure WLAN
	* ...

* Plugin SD card, power on
* Remote log into rpi

```
ssh pi@raspberrypi
```

Install kernel headers for kernel module compilation:

```
sudo apt-get install raspberrypi-kernel-headers
```

If that doesn't work: [solution on StackOverflow](https://raspberrypi.stackexchange.com/questions/50240/missing-build-file-when-building-for-rtl8812au-driver).

Fetch Linux kernel source code:

```
sudo apt install flex bison libssl-dev
mkdir tools
git clone --depth 1 https://github.com/raspberrypi/linux.git
ln -s linux $(uname -r)
sudo ln -s /home/pi/tools/linux /lib/modules/$(uname -r)/build
cd linux
wget -O Module.symvers https://raw.githubusercontent.com/raspberrypi/firmware/master/extra/Module7.symvers
KERNEL=kernel7
make bcm2709_defconfig
make prepare
```

```
mkdir tools
cd tools
wget https://sourceforge.net/projects/linux-gpib/files/linux-gpib%20for%203.x.x%20and%202.6.x%20kernels/4.3.5/linux-gpib-4.3.5.tar.gz
tar xfvz linux-gpib-4.3.5.tar.gz
cd linux-gpib-4.3.5
tar xfvz linux-gpib-kernel-4.3.5.tar.gz
tar xfvz linux-gpib-user-4.3.5.tar.gz
cd linux-gpib-kernel
make
```

Error:

```
make[3]: *** No rule to make target 'scripts/module.lds', needed by '/home/pi/tools/linux-gpib-4.3.5/linux-gpib-kernel-4.3.5/drivers/gpib/agilent_82350b/agilent_82350b.ko'.  Stop.
```

Fix
cd ~/tools/linux
git fetch origin rpi-5.0.y
```

# References

* [Short tutorial about installing GPIB on a Raspberry Pi](https://github.com/PhilippCo/meas_rpi)
* [VXI-11 Server in Python](https://github.com/PhilippCo/python-vxi11-server)
* [HP E2050A Teardown](https://www.eevblog.com/forum/testgear/hp-e2050a-mini-teardown/)
* [Keysight E5810B LAN GPIB USB Gateway](https://www.keysight.com/us/en/product/E5810B/lan-gpib-usb-gateway.html)
* [ICS Electronics 9065 Ethernet GPIB Gateway](https://www.icselect.com/vxi-11_gateway.html)
* [Save Money And Have Fun Using IEEE-488](https://hackaday.com/2022/01/31/save-money-and-have-fun-using-ieee-488/)
