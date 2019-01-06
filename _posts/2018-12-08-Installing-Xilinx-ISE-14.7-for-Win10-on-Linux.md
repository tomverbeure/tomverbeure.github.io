---
layout: post
title:  Installing Xilinx ISE 14.7 for Win10 ... on Linux
date:   2018-12-02 17:00:00 -0700
categories: Pano Logic
---

The [Xilinx ISE 14.7 WebPack edition](https://www.xilinx.com/products/design-tools/ise-design-suite/ise-webpack.html) 
is available for free to be used for a variety of smaller FPGAs. It has versions for Linux and Windows.
It entered into [sustaining mode in October 2013](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/design-tools/v2012_4---14_7.html),
without support for the largest Spartan-6 FPGAs and that was that. Or so everybody thought.

In [February 2018](https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/design-tools/14_7-windows.html) however,
Xilinx make a new release of ISE, still graced with the same 14.7 version number, for Windows 10.

What's special about this is that it only supports Spartan-6 devices, but it supports *all* Spartan-6 devices, including
the LX100 and LX150 which are used in the [Pano Logic G2](https://github.com/tomverbeure/panologic-g2) thin clients.

As suggested by the release name, it officially only supports Windows 10, but it doesn't actually contain the expected
native Windows executables: instead it's a VirtualBox container with a Linux installation of ISE, wrapped in a Windows
installer.

Installation for Windows 10 is pretty straightforward, and the intended use, but the beauty of a virtual machine is that
it abstracts the host OS. And since VirtualBox works just as well with Linux or OSX as host OS, this version should work
on those machines too!

In this post, I show you who to get that going. There is nothing overly difficult about this, so don't expect
deep insights or advanced hacker tricker. But I ran into a few minor roadblocks that cost me 

