---
title: Wavetek Pacific Instruments Model 1038-N10 Network Analyzer
date: 2024-03-19 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

John has been downsizing his RF home lab for a while now, and after initially posting all this
stuff on Craigslist, he got into the habit of first asking me. All this test equipment is
kept in top shape, and he always allows me to check that all is working before buying.

One day, he emailed me to see if I were interested in a Wavetek 1038-N10 network analyzer with
a set of detectors for a very low friends and family price. Not knowing quite exactly what I was 
buying, I still say yes.

It turned out to be a much better deal than expected: he threw in a fantastic Racal-Dana 1992 
universal counter and an HP 428A power meter, without power probe, into the mix as well, at
no extra cost.

I already knew what you can do with a vector network analyzer (VNA), and a scalar network analyzer is 
like a VNA without phase measurement, so I expected operating this thing to be smooth sailing, but
it didn't quite work out that way. The 1038-N10 was a low cost instrument, one that works quite
a bit different. And there's not a whole lot of information about it online either. Most information
can be found on [Tekwiki](https://w140.com/tekwiki/wiki/Pacific_Measurements_1038), because some
parts of the 1038 product line where Tektronix OEM models.

In this blog post, write down my own experience in getting the 1038-N10 to work. I'll also
look a bit at how it works under the hood.


# The Wavetek 1038-N10

The network analyzer consists of the 1038-D14A mainframe with display unit and the 
1038-N10 which slides into the mainframe. John gave me one working N10 and a second one with a
bunch of buttons missing in case I ever needed spare parts. So far I have not needed those,
but that's because my attention shifted towards the Racal-Dana 1992 counter.

[![Wavetek 1038-D14A and 1038-N10](/assets/w1038-n10/wavetek_1038-n10-chassis.jpg)](/assets/w1038-n10/wavetek_1038-n10-chassis.jpg)

The mainframe exists in 2 form factors, one with the display unit on top and one with the
display on the left of the N10. Mine luckily has the second configuration. It's much easier
to stow on a shelve. Don't confuse the 1038-D14A with the 1038-D14 mainframe. But can be used
with the N10, but the D14 has a lower temperature operating range of 0C to 40C instead of 0C to 
50C. There are also differences in the GPIB command set.

The unit also has a little drawer for cables, connectors, and, in my case, a 30 page operational
handbook that proved really useful: operating the 1038-N10 is not very intuitive, and while
there is an operating and maintenance manual that goes in detail, having a booklet with just
the basics makes it easier to get started.

![1038-N10 Operational Handbook](/assets/w1038-n10/1038-N10 Operational Handbook.jpg)

I couldn't find this manual anywhere online, so I made a scan that you can download 
[here](/assets/w1038-n10/1038-N10 Operational Handbook.pdf). The quality isn't great,
but it's better than nothing.

# References

**Manuals**

* [Wavetek Model 1038-N10 Network Analyzer - Operating and Maintenance Manual](/assets/w1038-n10/Wavetek_pacific_1038-n10-operating_and_maintenance_manual.pdf)
* [Wavetek Model 1038-N10 Network Analyzer - Operational Handbook](/assets/w1038-n10/1038-N10 Operational Handbook.pdf)

**On the web**

* [Pacific Measurements 1038 on tekwiki](https://w140.com/tekwiki/wiki/Pacific_Measurements_1038)
* [Pacific Measurements or Wavetek 1038 System on groups.io](https://groups.io/g/TekScopes/topic/pacific_measurements_or/31300487?p=,,,20,0,0,0::recentpostdate%2Fsticky,,,20,2,20,31300487)
* [Pacific Measurements or Wavetek 1038 System on eevblog forum](https://www.eevblog.com/forum/testgear/pacific-measurements-or-wavetek-1038-ns1020-nsn201/)


