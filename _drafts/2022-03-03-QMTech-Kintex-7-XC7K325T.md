---
layout: post
title: QMTech Kintex-7 XC7K325T
date:  2022-03-03 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Installation


* Compile latest version of  Yosys
* Download Vivado 17.2 from here: https://www.xilinx.com/support/download/index.html/content/xilinx/en/downloadNav/vivado-design-tools/archive.html

    Xilinx_Vivado_SDK_2017.2_0616_1_Lin64.bin

* Build project Xray

 no```sh
export XRAY_VIVADO_SETTINGS=/opt/Xilinx/Vivado/2017.2/settings64.sh
git clone git@github.com:f4pga/prjxray.git
cd prjxray
git submodule update --init --recursive
make build
sudo -H pip3 install -r requirements.txt
make db-prepare-parts
```

* Build [nextpnr-xilinx](https://github.com/gatecat/nextpnr-xilinx/)

```sh
git clone git@github.com:gatecat/nextpnr-xilinx.git
git submodule init
git submodule update
cmake -DARCH=xilinx
make -j$(nproc)
```


# References

* [AliExpress product link](https://www.aliexpress.com/item/1005003668804223.html)
* [GitHub repo](https://github.com/ChinaQMTECH/QMTECH_XC7K325T_CORE_BOARD)
* [Project X-Ray](https://github.com/f4pga/prjxray)
    * [Documentation](https://f4pga.readthedocs.io/_/downloads/prjxray/en/latest/pdf/)
