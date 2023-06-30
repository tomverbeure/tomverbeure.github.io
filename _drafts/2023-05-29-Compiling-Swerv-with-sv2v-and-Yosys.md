---
layout: post
title: Synthesizing SweRV with sv2v and Yosys
date:   2023-05-29 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Instructions

* Install sv2v

    Download from [releases](https://github.com/zachjs/sv2v/releases) page.

    Put in ~/tools/sv2v

* Download SweRV

```
cd ~/projects
git clone https://github.com/chipsalliance/Cores-VeeR-EH1
cd Cores-VeeR-EH1
export RV_ROOT=`pwd`
make -f tools/Makefile
```
