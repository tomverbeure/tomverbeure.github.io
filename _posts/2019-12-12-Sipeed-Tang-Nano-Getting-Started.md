---
layout: post
title: Getting Started with the Sipeed Tang Nano
date:  2019-12-12 00:00:00 -0700
categories:
---

* [Board on Seeed.com](https://www.seeedstudio.com/Sipeed-Tang-Nano-FPGA-board-powered-by-GW1N-1-FPGA-p-4304.html)
* [LCD on Seeed.com](https://www.seeedstudio.com/5-Inch-Display-for-Sipeed-Tang-Nanno-p-4301.html)

Tang Nano not listed on [their main website](https://sipeed.com).

* [Tang Nano website repo on Github](https://github.com/sipeed/Tang-Nano-Doc)

    Uses "Lichee Tang Nano" and "Sipeed Tang Nano". Company name changed.

* [Installation guide on GitHub](https://github.com/sipeed/Tang-Nano-Doc/blob/master/en/get_started/install-the-ide.md)

* [Sipeed Download Station](http://dl.sipeed.com/TANG/Nano)

    Bunch of different files, but no explanation what is what or when to use it.

* Download IDE from [their FAQ page](http://www.gowinsemi.com.cn/faq.aspx)

    I downloaded V1.9.2.02Beta for Linux. Only 440MB, but took ages to download (140KB/s).

* Create tools directory and unarchive the IDE.

    The archive does NOT contain this directory. I hate that.

    Uncompressed, the tools take around 1.2GB.

```
mkdir Gowin_V1.9.2.02Beta
tar xfvz ~/Downloads/Gowin_V1.9.2.02Beta_linux.tar.gz
```

* There are now 3 main directories:

```
drwxr-xr-x 10 tom tom 4096 Mar 28  2019 IDE/
drwxr-xr-x  3 tom tom 4096 Nov  7 18:28 Programmer/
drwxr-xr-x  8 tom tom 4096 Sep 28 17:59 SynplifyPro/
```

* Start the main IDE 

```
~/tools/Gowin_V1.9.2.02Beta/IDE/bin/gw_ide
```

    This will fail, however it will open up a dialog box in which to fill in an IP address
    to get a floating license.

    You can also simply create a `gwlicense.ini` file  in the `./bin` directory. 

`~/tools/Gowin_V1.9.2.02Beta/IDE/bin/gwlicense.ini`:

```
[license]
lic="45.33.107.56:10559"
```

* Set license variable to make Synplify work

```
export LM_LICENSE_FILE="27020@45.33.107.56"
```

* Start the main IDE again


