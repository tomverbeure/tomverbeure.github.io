---
layout: post
title: A VGA to 40-pin Sony CHM-9001-00 CRT Adapter
date:  2022-10-05 00:00:00 -1000
categories:
---

* TOC
{:toc}


# I2C programming

```
sudo apt install i2c-tools
```

```sh
i2cdetect -l
```

```
i2c-0	unknown   	SMBus I801 adapter at efa0      	N/A
i2c-1	unknown   	i915 gmbus ssc                  	N/A
i2c-2	unknown   	i915 gmbus vga                  	N/A  <<<
i2c-3	unknown   	i915 gmbus panel                	N/A
i2c-4	unknown   	i915 gmbus dpc                  	N/A
i2c-5	unknown   	i915 gmbus dpb                  	N/A
i2c-6	unknown   	i915 gmbus dpd                  	N/A
i2c-7	unknown   	AUX B/DP B                      	N/A
i2c-8	unknown   	AUX C/DP C                      	N/A
i2c-9	unknown   	AUX D/DP D                      	N/A
```


```sh
sudo i2cdetect -y 2
```
```
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
00:                         -- -- -- -- -- -- -- -- 
10: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
20: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
30: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
40: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
50: 50 -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
60: -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- 
70: -- -- -- -- -- -- -- --                         
```

```sh
sudo i2cdump -y 2 0x50
```

```
No size specified (using byte-data access)
     0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f    0123456789abcdef
00: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
10: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
20: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
30: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
40: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
50: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
60: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
70: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
80: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
90: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
a0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
b0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
c0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
d0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
e0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
f0: ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff ff    ................
```


# References

* [HP 16500A/16501A Service Manual][HP 16500A Service Manual]
* [Sony CHM-9001 Service Manual](/assets/hp16500a/sony-chm-9001-00-service-manual.pdf)

[HP 16500A Service Manual]: /assets/hp16500a/HP16500-90911-Service-Manual.pdf

