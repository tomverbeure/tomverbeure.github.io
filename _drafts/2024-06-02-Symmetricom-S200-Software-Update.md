---
layout: post
title: Symmetricom SyncServer S200 Software Update
date:   2024-06-02 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

Notes:

* DHCP: 
    * avoid it you can
    * when enabled but no network cable connect, bootup will hang for a minutes
    * DHCP lease only negotiated at bootup
* When not using DHCP, add DNS server. For Comcast, it was 75.75.75.75
* Management can only happen on LAN port 1
* Default Symmetricom NTP servers are not operational anymore
* IL-0030B only shows satellites tracked, not satellites visible, for a long time.
  But when GPS lock, suddenly satellites are visible.
* IL-0030B has rechargable 3.3V Varta MC 621 battery. Feeds a 32768kHz oscillator for an RTC clock.
* IL-0030B is much slower at tracking satellites.
* Patch Linux distribution to enable root
* Use JP4 on motherboard for factory default settings (e.g. when misconfigured...)

Getting date from server:

```sh
ntpdate -q 192.168.1.201
```

```
server 192.168.1.201, stratum 1, offset -0.002502, delay 0.02988
 4 Jun 22:28:50 ntpdate[229341]: adjust time server 192.168.1.201 offset -0.002502 sec
```

* Make backup of compact flash card
* Reset to default settings

    * Page 120 of manual
    * Wire up jumper JP4 (not a standard jumper!)
    * power on
    * wait for 100s
    * power off
    
    (What goes on under the hood)

* Set up IP address for remote connection

    * Only LAN1 is active
    * I use static IP 192.168.1.201. The default is 192.168.0.100.
    * Gateway: 255.255.255.0
    * LAN1 Gateway: 192.168.1.1
    * Don't use DHCP for initial configuration. The moment you switch, you can't log on
      because the web panel is disabled!
    * Plug in cable. Network LED should go green.

* Connect to web panel
    * http://192.168.1.201
    * Username: admin
    * Password: symmetricom

* Webpanel: configure network:

    * NETWORK -> Ethernet:
    * Management Port User DNS Servers: Add a DNS server. 

        In the case of Comcast: 75.75.75.75

    * Check with NETWORK -> Ping that you can ping the outside world. E.g yahoo.com

* Set up NTP servers to sync with

    * The default ones don't work!!! 69.25.96.11, 69.25.96.12, 69.25.96.14 

        In NETWORK Assoc, you'll see that all these IP addresses have St(ratum) value of 16.
        
    * NTP -> Config

        * Select 69... IP address and delete them.
        * Add 0.pool.ntp.org
        * Add 1.pool.ntp.org
        * Add 2.pool.ntp.org
        * Add time.nist.gov
        * RESTART

        * [NIST servers](https://tf.nist.gov/tf-cgi/servers.cgi)

    * NTP -> Assoc

        Will show various stratum values for the IP addresses.

    * You should be able to query your server now from your PC:

        ```sh
ntpdate  -q 192.168.1.201
        ```

        ```
server 192.168.1.201, stratum 16, offset -0.019111, delay 0.02856
 4 Jun 23:20:32 ntpdate[230482]: no server suitable for synchronization found
        ```

        Initially, this will show Stratum 16, because the internal clock was not synced to GPS
        due to the WNRO problem and because it needs time to sync to one of the NTP servers.

        After a while (around 15 minutes), you'll get this:

        ```sh
ntpdate  -q 192.168.1.201
        ```
        ```
server 192.168.1.201, stratum 2, offset -0.034768, delay 0.02989
 4 Jun 23:23:21 ntpdate[230491]: adjust time server 192.168.1.201 offset -0.034768 sec
        ```

        The Sync status LED and web page indicator will now be yellow instead of red: at
        least you have *something*, which should be good enogh for pretty much anything!

        On the front panel and on STATUS -> Timing, you'll see that the current
        sync source is NTP and that the hardware clock status is "Locked".

        This means that the OCXO is disciplined to an external NTP server. The problem is:
        the output is horrible. In my case: 9,999,901 Hz, a deviation of a whopping
        99Hz, much worse that the 7Hz deviation when the OXCO clock isn't disciplined at all!

        And then after a while, it jumped to 10,000,095Hz!

* Set correct time zone

    * TIMING -> Time Zone

        I use America/Los_Angeles

    You have an expensive and quite power hungry clock now!

* Upgrade the system: forget about doing this from the web, the Symmetricom servers have
  been shut down long time ago. But you can do upload a file.

* Make backup of settings

    * Web interface: Wizards -> Backup -> Backup
        * Save As -> browser download syncServer.bkp

* Power consumption is around 18W. Will be lower for the TCXO and higher for the Rubidium
  version.

* Optional:

    
        


# Furuno GT-8031H:

When the S200 isn't able to lock its local OCXO to the GPS in, the 10MHz frequency is terribly
off by 7Hz:


(For this measurement, I'm using the 10MHz of my TM4313 GPSDO as clock reference.)

You can also see how the 1PPS output of S200 differs from the TM4313 output by 42ms.
Note that this is despite seeing 9 satellites.

The screen will show 

* Antenna: Good
* Status: Unlocked
* Source: None
* GPS In: Unlocked
* 1PPS In: Unlocked
* 10MHz In: Unlocked

# Feature Comparison

|        | S200 | S250 | S250i |
|-------:|:----:|:----:|:-----:|
|    GPS |   X  |   X  |       |
|   1PPS |      |   X  |   X   |
| 10 MHz |      |   X  |   X   |
| IRIG-B |      |   X  |   X   |

# Installing the New Connectors


# Cloning the Existing Drive

**Linux**

```sh
$ df
```

```
/dev/sdb7          97854         2     92720   1% /media/tom/_tmparea
/dev/sdb2           8571       442      7683   6% /media/tom/_persist
/dev/sdb1          17047      2510     13597  16% /media/tom/_boot
/dev/sdb5         173489     69985     94256  43% /media/tom/_fsroot1
/dev/sdb6         173489     69986     94255  43% /media/tom/_fsroot2
```

```sh
$ sudo dd if=/dev/sdb of=flash_contents_orig.img bs=1M
```

```
[sudo] password for tom: 
488+1 records in
488+1 records out
512483328 bytes (512 MB, 489 MiB) copied, 40.6726 s, 12.6 MB/s
```

Notice the `sync` command!

```sh
$ sudo dd if=flash_contents_orig.img of=/dev/sdb bs=1M && sync
```

```
488+1 records in
488+1 records out
512483328 bytes (512 MB, 489 MiB) copied, 0.143977 s, 3.6 GB/s
```

**Windows**

Use the [HDD Raw Copy Tool](https://hddguru.com/software/HDD-Raw-Copy-Tool/).

# Getting Started

* Reset to factor default settings
* Use a static IP address

    You won't be able to connect with your browser otherwise!

![S200 web home screen](/assets/s200/S200_home_screen.png)

# 10MHz Out

* 2.60Vpp AC

![10MHz output on oscilloscope](/assets/s200/10MHz_output.png)

# Satellite status

```sh
ssh -oHostKeyAlgorithms=+ssh-dss admin@192.168.1.201
gpsstrength
```

By default, there's only a simply command line processor the knows a few commands.

# Enable SSH root access

* Inspired by [this EEVblog post](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250/msg2952418/#msg2952418)

Boot procedure:
* Boots `_fsroot1` or `_fsroot2`.
* Overwrites /etc and /var with config.tar.gz data in the /persists partion.
* So you need to patch the config.tar.gz file!

* Use web interface to dump `syncServer.bkp` file

```sh
mkdir bak
cd bak
sudo tar xf ../syncServer.bkp
```

```
tom@zen:~/projects/tomverbeure.github.io/assets/s200/bak$ ll
total 444
drwxrwxr-x 2 tom  tom    4096 Mar 16 23:32 ./
drwxrwxr-x 4 tom  tom    4096 Mar 16 23:32 ../
-rw-r--r-- 1 root root 439681 Jan  3  2006 config-1.2.tar.gz
-r--r--r-- 1 root root    421 Jan  3  2006 persist.conf
```

```sh
sudo tar xfz config-1.2.tar.gz
```

```
# Delete root line
# Copy admin and rename to root
sudo gvim etc/shadow
# PermitRootLogin yes
sudo gvim etc/ssh/sshd_config
sudo rm config-1.2.tar.gz
sudo tar cfz config-1.2.tar.gz ./etc ./var
sudo rm -fr ./etc ./var
tar cf ../syncServer.patched.bkp config-1.2.tar.gz persist.conf
cd ..
rm -fr ./bak
```


# Decoding M12 messages

## Working module

Initial configuration:

* Send @@Cf: set to all defaults
* Send @@Gf: set time raim alarm to 1000ns
    Receiver Autonomous Integrity Monitoring
    Tests whether or not GPS signals from different satellites are consistent.
* Send @@Aw: time correction select. 
    Set UTC mode (1) instead of GPS mode (0)
    This determines what kind of time the @@Ha and the @@Hn message will
    send back.
    If no almanac data is present, @@Ha will return GPS time until
    it receives that data. Then it switches automatically to UTC time.
* Send @@Bp: request utc/ionospheric data
    Mode 0: polled mode
* Send @@Ge: time raim select
    1: enable
* Send @@Gd: position control mode
    3: auto-survey

Before lock:


* S200 polls every 8 seconds with Bp message for atmospheric data. Module
  return Co message. Uses mode 0 - polled.
* Module automatically sends Ha message (12 channel position/status/data) every second
* Every 3 seconds there is also an automatic Hn message (time raim status message). The
  3 second rate was programmed right at the start.


After lock:
* Module polls Bp (atmospheric data, polled) message, Bj message (leap second status, polled), 
  and a Gj message (leap second pending)
* Module automatically sends Ha message (12 channel position/status/data) every second


* Time reports for both old and new traces on 2024/5/5: 2004/9/19. Delta is 1024 weeks...
* Differences

    * old: Hn: time_accuracy_est of 0, new is 65535.
    * old: Hn: fract_local_time:0, new: various numbers
    * old: Ha: iode is 0, new is various values.
            "Issue Of Data, Ephemeris"
            Used to identify updated GPS Ephemeris data.

        [Ephemerides](https://www.e-education.psu.edu/geog862/node/1737)
    * new: Bj starts appearing soon after Hn clock_bias and osc_offset becomes non-zero!
          cold_start and insufficient_sats also switches from 1 to 0. 
        In old, all these fields remain 0 or 1 resp. except insufficient_sats which is always.
    * new: Co has non-zero values for ionospeheric data. Old always has zeros, but I don't
        think this matters.

* Experiments:

    * old: force cold_start to 0.
    * new: Hn: force fract_local_time to 0
    * new: Hn: force time_accuracy_est to 0
    * new: Ha: force iode to 0
    * old: Ha: force iode to some random value?

# References

* [Microsemi SyncServer S200 datasheet](/assets/s200/md_microsemi_s200_datasheet_vb_.pdf)
* [Microsemi SyncServer S200, S250, S250i User Guide](/assets/s200/syncserver-s2xx_997-01520-01_g2_md.pdf)
* [EEVblog - Symmetricom S200 Teardown/upgrade to S250](https://www.eevblog.com/forum/metrology/symmetricom-s200-teardownupgrade-to-s250)

* [GPIO Labs](https://gpio.com/)

    Has a bunch of GNSS related products, such as this 
    [USB Bias Tee with GNSS band filter and 3.3V supply](https://gpio.com/collections/gnss/products/gnss-filtered-bias-tee-gps-l1-l5-glonass-beidou-navic-1100-1700-mhz)
    or this universal [USB Bias Tee](https://gpio.com/collections/bias-tees/products/usb-bias-tee-operates-from-10mhz-7000mhz).

* [DIY bias tee](https://discussions.flightaware.com/t/power-bias-tee-from-usb-port/66181)

* [HEOL S200 S250 S300 S350 XLi servers GPS upgrade](https://trends.directindustry.com/heol-design/project-57722-1149241.html)

* [EEVblog - Symmetricom Syncserver S350 + Furuno GT-8031 timing GPS + GPS week rollover](https://www.eevblog.com/forum/metrology/symmetricom-syncserver-s350-furuno-gt-8031-timing-gps-gps-week-rollover/)

* [EEVblog - Synserver S200 GPS lock question](https://www.eevblog.com/forum/metrology/synserver-s200-gps-lock-question/msg5339408)

* [Furuno GPS/GNSS Receiver GPS Week Number Rollover](https://furuno.ent.box.com/s/fva29wqbcioqvd6mqxn5rt976dkaxudj)

* [USNO GPS Time Transfer](https://www.cnmoc.usff.navy.mil/Our-Commands/United-States-Naval-Observatory/Precise-Time-Department/Global-Positioning-System/USNO-GPS-Time-Transfer/)

    As of December 31st, 2016, GPS is ahead of UTC by 18 leap seconds.

* [What are satellite time, GPS time, and UTC time?](https://aviation.stackexchange.com/questions/90839/what-are-satellite-time-gps-time-and-utc-time)

# Footnotes

