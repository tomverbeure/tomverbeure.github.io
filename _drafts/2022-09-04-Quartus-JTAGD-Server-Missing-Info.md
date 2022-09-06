---
layout: post
title: The Quartus JTAGD Server Missing Info Blog Post
date:  2022-09-04 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

When you're working with Intel's Quartus software, you'll almost certainly also be using it to load 
bitstreams to an FPGA with the *Quartus Programmer* tool.

![Quartus Programmer](/assets/jtagd/quartus_programmer.png)

Behind this GUI, a number of steps and processes are working under the hood to make all of this happen:

Quartus Programmer -> [socket interface] -> jtagd ->  USB device driver -> JTAG dongle -> JTAG signals

This blog posts talks about jtagd, a server daemon that is used by Quartus to execute all JTAG related 
operations.

Quartus Progammer talks to jtagd over a standard socket interface. It can connect to a local jtagd server
using kernel sockets, or to a remote one over TCP/IP. In the latter configuration, this allows you to run Quartus
on one machine, say the development machine on your desk, while controlling a PC in the lab that's connected
to your develoment board and FPGA.

The standard way to load a bitstream to your FPGA is very straightforward:

* Compile a design that creates a bitstream
* Launch Quartus Programmer
* Press "Start"
* Wait until you see "100% (Successful)" on the top right of the Quartus Programmer window

That's all there is to it... if things go well.

But things don't go always go well. And when that's the case, there are number of issues:

* the GUI tools don't provide a lot of feedback about what's going wrong
* the system can go into a state that can only be resolved by quitting and restarting Quartus. Not just
  Quartus Programmer but the main tool as well.
* in some cases, you need to manually kill the JTAG daemon to make things work again.

It can be extremely frustrating...

At some point, I had the plan of writing a jtagd shim that would allow Quartus Programmer to talk to OpenOCD, and
thus any JTAG dongle in existence instead of just one that's officially supported by Intel or an Intel clone.
The way I approached this was to inflict Ghidra on jtagd and reverse engineer the whole program execution flow
when programming a bitstream.

I never completed the exercise,  but I got at least to the point where I could make Quartus Programmer believe that
it was talking to a real jtagd server.

<blockquote class="twitter-tweet"><p lang="en" dir="ltr">Here&#39;s an unusual sight in Intel&#39;s Quartus Programmer: next to Hardware Setup, you don&#39;t see the name of some Intel JTAG dongle or clone (such as &quot;USB-Blaster&quot;), but &quot;Tom&#39;s JTAG server&quot;. 1/ <a href="https://t.co/tOTJ29i54c">pic.twitter.com/tOTJ29i54c</a></p>&mdash; Tom Verbeure (@tom_verbeure) <a href="https://twitter.com/tom_verbeure/status/1379669381806845953?ref_src=twsrc%5Etfw">April 7, 2021</a></blockquote> <script async src="https://platform.twitter.com/widgets.js" charset="utf-8"></script>

What I discovered in the process where a bunch of command line options that not only make it much easier
to root cause jtagd issues, but they also made the Quartus Programmer / jtagd combination more robust!

# Starting jtagd from the command line

In normal GUI operation, you don't need to start jtagd from the command line. But for this blog post, we'll
be doing exactly that.  With the `$QUARTUS_ROOTDIR` environment variable set to a Quartus installation directory 
of choice, here's how I typically run `jtagd`:

```sh
LD_LIBRARY_PATH=$QUARTUS_ROOTDIR/linux64:$LD_LIBRARY_PATH \ 
$QUARTUS_ROOTDIR/linux64/jtagd <command line options>
```

Notice how I make sure that both the executable and a whole bunch of shared libraries have
their path explicitly set. I have a multiple Quartus installations on my PC. I don't there
to be any issues with mixing code from different locations. 

I have an alias the following alias for this:

```sh
alias jtagd="LD_LIBRARY_PATH=$QUARTUS_ROOTDIR/linux64:$LD_LIBRARY_PATH $QUARTUS_ROOTDIR/linux64/jtagd"
```

*It's probably better to use a bash function for this, but it works well enough for now.*


# jtagd command line options 

The `--help` option returns the following:

```sh
jtagd --help
```

```
jtagd
Version 20.1.1 Build 720 11/11/2020 SJ Standard Edition
Copyright (C) 2020  Intel Corporation. All rights reserved.

You should not need to run this command.
Please use the jtagconfig command to control the JTAG server.

Syntax: jtagd [--user-start] [--config <filename>]
```

There's only 2 official command line options. The Quartus documentation doesn't even bother explaining those, but
Google is your friend.

* `--user-start`

    [This Intel forum post](https://community.intel.com/t5/Intel-Quartus-Prime-Software/Problems-connecting-remotely-to-jtagd-running-on-linux/m-p/72209/highlight/true#M14904)
    explains that `--user-start` causes jtagd to stop itself 2 minutes after the last client disconnects from it.
    I've tried it: it works.

    In normal GUI operation, that user client will be Quartus Programmer, but it could be any tool that requires
    JTAG functionality: Quartus SignalTap, Quartus System Console, or even another PC that talks to jtagd for
    remote JTAG control

* `--config <filename>`

    Tells jtagd where to find a configuration file.

    When not specified, jtagd will look in `/etc/jtagd/jtagd.conf`. That file will normally not exist if you
    haven't explicitly created it.

    When there's no jtagd already running, Quartus Programmer will launch it for you, with the following parameters:

    ```sh
tom@thinkcenter:~/projects/jtagd$ ps -ef | grep jtagd
tom  22198  1  0 22:14 ?  00:00:00 jtagd --user-start --config /home/tom/.jtagd.conf
    ```

    Instead of using `/etc/jtagd/jtagd.conf`, Programmer makes jtagd look at `~/.jtagd.conf`. That's a file will
    normally also not exist. 

    We'll come back to this later.

In addition to these 2 officially supported command lines options, there are two more that are often
mentioned in blog posts or on [StackOverflow](https://stackoverflow.com/questions/18704913/unable-to-lock-chain-insufficient-port-permissions):

* `--foreground`

    This will run jtagd as a regular server process instead of daemon. If you want to stop the process, you can
    just CTRL-C yourself out of it. This is incredibly useful because status messages will be sent to the terminal
    instead of being forwarded to `/dev/null`.

    You should start jtagd like this before you start Quartus Programmer, otherwise the jtagd daemon that's started
    by Programmer will prevent your foreground jtagd from starting, and you'll get the following message:

    ```sh
tom@thinkcenter:~$ jtagd --foreground
JTAG daemon started
No USB device change detection because libudev.so.0 not found
Can't bind to TCP port 1309 - exiting
    ```

    Notice the libudev.so.0 message: I always get this, but it doesn't seem to impact correct operations of my
    JTAG dongle. (You may not be so lucky!)

    I don't always use `--foreground`, but whenever I encounter intermittent issues with my JTAG connection, 
    `--foreground` seem to make things work better. I've noticed this on multiple PCs...

* `--debug`

    This option makes jtagd print a bit more information to the console. That makes it only useful when
    jtagd is running in the foreground.

    Here's what happens when I start jtagd with `--debug` added:

    ```sh
tom@thinkcenter:~$ jtagd --foreground --debug
JTAG daemon started
Using config file /etc/jtagd/jtagd.conf
Remote JTAG permitted when password set
No USB device change detection because libudev.so.0 not found
USB-Blaster "USB-Blaster" firmware version 4.00
USB-Blaster endpoints out=02(64), in=81(64); urb size=1024
USB-Blaster added "USB-Blaster [1-7]"
    ```

There are a number of additional undocumented command line options that I discovered by browsing through the `main()`
function routine with [Ghidra](https://ghidra-sre.org/):

* `--no-config`

    Tells jtagd to not use the default `/etc/jtagd/jtagd.conf` configuration file.

* `--version`

    Does exactly what you'd expect...

    ```sh
tom@thinkcenter:~$ jtagd --version
jtagd
Version 20.1.1 Build 720 11/11/2020 SJ Standard Edition
Copyright (C) 2020  Intel Corporation. All rights reserved.
    ```

* `--no-auto-detect`

    Without this option, jtagd scans your system for supported attached JTAG dongles.

    On my system, jtagd automatically conenects to my USB-Blaster clone:
    ```sh
USB-Blaster added "USB-Blaster [1-7]"
    ```

    With the `-no-auto-detect` option, jtagd doesn't do that:

    ```sh
tom@thinkcenter:~$ jtagd --foreground --debug --no-auto-detect
JTAG daemon started
Using config file /etc/jtagd/jtagd.conf
Remote JTAG permitted when password set
    ```

    This option is useful if you want a jtagd server to only use explicitly declared 
    JTAG dongles. These dongles can be defined in a `jtagd.conf` file, or added and
    removed from a running server with the `jtagconfig` tool.

* `--auto-detect-filter <JTAG dongle serial number>`

    With this option, you can tell jtagd to only connect to JTAG dongles that have a specific serial number.

    Here's what happens when I used this option with some random serial number:

    ```sh
tom@thinkcenter:~$ jtagd --foreground --debug --auto-detect-filter 12345
JTAG daemon started
Using config file /etc/jtagd/jtagd.conf
Remote JTAG permitted when password set
Matches cable with serial number "12345"
No USB device change detection because libudev.so.0 not found
Cable with serial number "91d28408" ignored due to filter   <<<<<<<<<<<
    ```

    Surprisingly, I don't have device with 12345 as serial number, but now I do know the serial number
    of my USB Blaster, and I can use that number to only allows jtagd to that one:

    ```sh
tom@thinkcenter:~$ jtagd --foreground --debug --auto-detect-filter 91d28408
JTAG daemon started
Using config file /etc/jtagd/jtagd.conf
Remote JTAG permitted when password set
Matches cable with serial number "91d28408"   <<<<<<<<<<<<<<<<
No USB device change detection because libudev.so.0 not found
USB-Blaster "USB-Blaster" firmware version 4.00
USB-Blaster endpoints out=02(64), in=81(64); urb size=1024
USB-Blaster added "USB-Blaster [1-7]"
    ```

    If you're wondering where that serial number is coming from: it's a standard field in 
    the USB descriptors, as shown with `lsusb -v`:

    ```sh
Bus 001 Device 007: ID 09fb:6001 Altera Blaster
Device Descriptor:
  bLength                18
  bDescriptorType         1
  bcdUSB               1.10
  bDeviceClass            0 (Defined at Interface level)
  bDeviceSubClass         0 
  bDeviceProtocol         0 
  bMaxPacketSize0         8
  idVendor           0x09fb Altera
  idProduct          0x6001 Blaster
  bcdDevice            4.00
  iManufacturer           1 Altera
  iProduct                2 USB-Blaster
  iSerial                 3 91d28408            <<<<<<<<<<<<
    ```
    
* `--port <port nr>`

    By default, the jtagd server uses TCP/IP port 1309. With this option, you can change this
    to whichever port number you want.

    This might seem useful in some circumstances, but only if you can tell Quartus Programmer which port
    to use when connecting to a remote server. I have not found a way to do that...

* `--port-file <filename>`, `--pid-file <filename>`

    These options make jtagd write the server port number and the process ID to a file.

    ```sh
tom@thinkcenter:~$ jtagd  --foreground --port-file port.info --pid-file pid.info --debug
JTAG daemon started
Using config file /etc/jtagd/jtagd.conf
Remote JTAG permitted when password set
No USB device change detection because libudev.so.0 not found
Wrote port to file port.info            <<<<<<<<<<<<<<<<<<<<<<
Wrote pid to file pid.info              <<<<<<<<<<<<<<<<<<<<<<
USB-Blaster "USB-Blaster" firmware version 4.00
USB-Blaster endpoints out=02(64), in=81(64); urb size=1024
USB-Blaster added "USB-Blaster [1-7]"
    ```

    ```sh
tom@thinkcenter:~$ cat pid.info 
4730
tom@thinkcenter:~$ cat port.info 
1309
    ```

* `--idle-stop`

    When you start jtagd with `--idle-stop` in combination with `--foreground`, you get this:

    ```sh
tom@thinkcenter:~$ jtagd --idle-stop --foreground
JTAG daemon started (will stop when idle)
No remote JTAG because stops when idle
No USB device change detection because libudev.so.0 not found
    ```

    You get the same message with `--user-start`. However, when using `--idle-stop`, Quartus
    Programmer can't connect to jtagd.

    It's currently not clear what `--idle-stop` is supposed to do...

* `--multi-thread`

    When added as an option, jtagd will report that it has started a thread
    on a particlar port"

    ```sh
tom@thinkcenter:~/projects/jtagd$ jtagd --foreground --debug --multi-thread
JTAG daemon started
Using config file /etc/jtagd/jtagd.conf
Remote JTAG permitted when password set
No USB device change detection because libudev.so.0 not found
USB-Blaster "USB-Blaster" firmware version 4.00
USB-Blaster endpoints out=02(64), in=81(64); urb size=1024
USB-Blaster added "USB-Blaster [1-7]"
Start thread for port 46231             <<<<<<
    ```

    And Quartus Programmer will still connect to it too.

    But I don't know if it's useful for anything practical...

* `--set-config`

    I think this option makes it possible to specify configuration options that are normally
    defined in jtagd.conf, but jtagd always returns `Unknown argument '--set-config'`. 

# Using jtagconfig to set configuration options

We saw earlier that jtagd picks up configuration options from a `jtagd.conf` file. But how do set theses options?

There are 3 ways to do that:

* Use Quartus Programmer

    When you use Quartus Programmer to set some special parameters, it will create the `~/.jtagd.conf` file and
    store the parameters in this file.

    For example, here I use the GUI to connect Quartus Programmer to a jtagd server that runs on a
    laptop with IP address 192.168.1.132:

    ![Quartus Programmer JTAG Server Configuration](/assets/jtagd/quartus_programmer_set_server.png)

    ![Quartus Programmer JTAG Remote Server Connected](/assets/jtagd/quartus_programmer_remote_server_connected.png)

    After clicking [OK], `~/.jtag.conf` (NOT: `~/jtagd.conf`!!!) has the following:

```sh
# /home/tom/.jtag.conf
#
# This file is written by the JTAG client when its configuration is changed.
# If you edit this file directly then your changes will probably be lost.


Remote1 {
	Host = "192.168.1.132";
	Password = "my_pwd";
}
```

* Server information goes into `jtagd.conf`. Client information goes into `jtag.conf`.
* jtagd will read both `jtagd.conf` and `jtag.conf`.
* Programmer GUI can set the jtagd server password if jtagd is started by the user, and
  config file is under /etc and writable.
  If not, then you get this:
  ```
tom@thinkcenter:~/projects/jtagd$ jtagconfig --enableremote blah
Error when setting password - Feature not implemented or unavailable under current execution privilege level
  ```
* jtagconfig is used to deal with hardware dongles. 
* You can chain jtagd servers. One points to a server (with jtag.conf file) which in turns
  points to the next server.
* `jtagconfig --addserver 192.168.1.132 my_pwd`
* jtagconfig starts jtagd if there isn't already one running and if it exists.
  * jtagconfig still works to access remote server, even if jtagd doesn't exist, but it's much slower.
  * jtagd creates a permanent connection?
* jtagconfig --define <JTAG IDCODE> <device name> <IR Length>
  * jtagconfig --defined

  ```
tom@thinkcenter:~/projects/jtagd$ jtagconfig --defined
  jtagconfig --define "test" 020B10ED 10
  ```

  * Doesnt work when IDCODE matches Intel device.
* jtagconfig --undefine <JTAG IDCODE> <device name>  removes it.
* jtagconfig --getparam 1 JtagClock
    * Other parameters: `strings -a jtagd`
        * NormalBypass
        * CapturedBypass
        * CapturedIR        -> last captured IR?
        * CapturedDR        -> last captured DR?
        * ExtendedId
        * SerialNumber

    
* jtagconfig --setparam 1 JtagClock 6M -> No parameter named JtagClock

* After set remote password in `/etc/jtagd/jtagd.conf`:

```
# /etc/jtagd/jtagd.conf
#
# This file is written by the JTAG daemon when its configuration is changed.
# If you edit this file directly then your changes will probably be lost.

Password = "my_pwd";
```

* Permissions on /etc/jtagd:

```
tom@thinkcenter:~/projects/tomverbeure.github.io/_drafts$ ll -d /etc/jtagd/
drwxrwxrwx 2 root root 4096 Sep  5 16:47 /etc/jtagd//
```
* Easiest to set global permissions, make changes, then set them back to restricted read-only.



# References

* [Installing and Configuring a Local JTAG Server (jtagd) on Linux](https://www.intel.com/content/www/us/en/docs/programmable/683472/22-2/installing-and-configuring-a-local-jtag.html)
* [JTAG Connections Over SSH](https://www.intel.com/content/www/us/en/docs/programmable/683756/21-2/jtag-connections-over-ssh.html)
* [Remote access to Altera FPGA via jtagd in Linux](https://www.fpgarelated.com/showthread/comp.arch.fpga/74229-1.php)
* [JTA-Over-Protocol (JOP) Intel FPGA IP](https://www.intel.com/content/www/us/en/docs/programmable/728673/21-3/jtag-over-protocol-overview.html)
    
    Explains how to send JTAG information over a custom protocol.

    * [remote-debug-for-intel-fpga](https://github.com/altera-opensource/remote-debug-for-intel-fpga)

        Creates a server that jtagd server can connect to.

    * [AN 972: JTAG Remote Debugging Over a PCIe Interface Example Design](https://www.intel.com/content/www/us/en/docs/programmable/728675/21-3/running-the-remote-debugging-over-a.html)
* [Remote FPGA Debug at RocketBoards](https://www.rocketboards.org/foswiki/Documentation/RemoteDebug)
