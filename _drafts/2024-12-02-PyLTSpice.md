---
layout: post
title: Using PyLTSpice for Automated and Repeatable LTSpice Simulations
date:   2025-10-05 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

When I write a blog post, I want my simulation results or plots to be recreatable 
and this should be as easy as running a single script. My blog post about 
[CIC filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
is a good example. The Python script that generated all the plots can be found 
[here](https://github.com/tomverbeure/pdm/blob/master/modeling/cic_filters/cic_filters.py).

There are a number of benefits to this kind of approach:

* Easy tweaking of results

  I have new insights while writing a blog post, and that may change details
  about what I want to simulate. A single script will conveniently update all results.

* Fast iteration of presentation

  The title of a plot, colors, line types... I'll keep on changing those until
  I'm happy with how they look. You just don't do that if there's too much
  effort involved.

* They serve as a how-to

  I often write about topics about which I'm not an expert. Neither am I
  an expert of the tools that I use. Previously written scripts are a great reference
  for when I need to do something similar many years later in, say, Numpy or
  Matplotlib.

It's easy to do so for tools that have a built-in scripting language, but I've been dabbling
a bunch of analog projects in the past years, and while some of that was done on real hardware, 
most of it happened in a [SPICE](https://en.wikipedia.org/wiki/SPICE) 
simulator. 

[![Sony CRT 60W power supply schematic and waveform in LTspice GUI](/assets/pyltspice/sonly_crt_60w_ltspice.png)](/assets/pyltspice/sonly_crt_60w_ltspice.png)

I started out with the fully open source [ngspice](https://ngspice.sourceforge.io/)
but I soon ran into insurmountable issues with simulations that wouldn't converge. I gave
up and switched to 
[LTspice](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html).
Not open source at all, but it's 100% free, comes with a gigantic component library,
and it never gave up with a non-converging simulation.[^time_step_too_large]
Since LTspice only runs on Windows, I bought 
[the cheapest laptop](/2025/03/12/HP-Laptop-17-RAM-Upgrade.html) I could find just
for this purpose.

[^time_step_too_large]: That doesn't mean that it never has simulation issues.
   A few times, I got [very strange results](https://electronics.stackexchange.com/questions/754308/understand-mismatch-between-small-signal-ac-amplitude-and-transient-amplitude-a) 
   that were solved by making the minimal simulation time step smaller.

LTspice is a little bit quirky. The GUI is opinionated and takes some time to get used to
and the waveform viewer has some annoying limitations when dealing with multiple
results.

But what bothers me the most in the total lack of tools to help with managing
a project and dealing with multiple simulations that are associated with it.

There is a friendly LTspice forum on Groups.io where I asked how others dealt with these kind 
of issues, but I didn't really get [the answers](https://groups.io/g/LTspice/topic/115566583#msg162688) 
that I was looking for.

# Some 






Issue:

* PyLTSpice instead of PyLTspice 
* If you have a project `rc_schematic.asc` and run a simulation, it creates
  an `rc_schematic.net` file. But when you close the project, it deletes that file.
* There is no way in PyLTSpice to specify the LTspice installation path.
* plot window shows "rc_schematic" but the active plt file can have a different name.
  The only way to see which is the current plt file is to go to
  "Plot Settings -> Save Plot Settings As..." and see which file it will save to.
* You can save a .plt file and load it when you have a plot window open and then go to 
  "Plot Settings -> Open Plot Settings File"
* There can't be multiple .tran/.ac/... statements active at the same time. 
  You can't even have a .tran and .ac active at the same time. When you use the 
  "Configure Analysis" menu, it automatically converts the other analysis statements
  to a comment (and it becomes blue.) You can also right click on an analysis
  comment, then click "Cancel and Edit Text Directly" and then switch between
  text comment or Spice directive.
* simulation log file is a modal window.

* LTspice.exe can be found here: C:\Users\tom_v\AppData\Local\Programs\ADI\LTspice\LTspice.exe
  Also: ~/AppData/Local/Programs/ADI/LTspice/LTspice.exe in git bash or powershell.

* Convert .asc to .net: ..../LTspice.exe -netlist rc_schematic.asc
* Batch execution: ..../LTspice.exe -b -Run rc_schematic.asc
* .meas is done after execution. You can run new .meas scripts on raw data in the waveform
  window.
* requires versions: PyLTSpice 5.4.4 and spicelib 1.4.6


# References

# Footnotes
