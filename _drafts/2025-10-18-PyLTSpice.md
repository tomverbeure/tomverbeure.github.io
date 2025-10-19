---
layout: post
title: Using PyLTSpice for Automated and Repeatable LTSpice Simulations
date:   2025-10-18 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

When I write a blog post, I want to recreate all simulation results or plots with
a simple script. My blog post about 
[CIC filters](/2020/09/30/Moving-Average-and-CIC-Filters.html)
is a good example of this. The Python script that generates all the plots can be found 
[here](https://github.com/tomverbeure/pdm/blob/master/modeling/cic_filters/cic_filters.py).

There are a number of benefits to this kind of approach:

* Easy tweaking of results

  I have new insights while writing a blog post, and that may change details
  about what I want to simulate. A single script will conveniently update all results.

* Fast iteration of presentation

  The title of a plot, colors, line types... I'll keep on changing those until
  I'm happy with how they look. You just don't do that if there's too much
  effort involved.

* The script serves as a future how-to

  I often write about topics or tools for which I'm not an expert. Previously written scripts 
  are a great reference for when I need to do something similar many years later in, say, Numpy 
  or Matplotlib.

It's easy to do so for tools that have a built-in scripting language, but I've been dabbling
a bunch of analog projects in the past years, and while some of that was done on real hardware, 
most of it happened in a [SPICE](https://en.wikipedia.org/wiki/SPICE) 
simulator. 

[![Sony CRT 60W power supply schematic and waveform in LTspice GUI](/assets/pyltspice/sonly_crt_60w_ltspice.png)](/assets/pyltspice/sonly_crt_60w_ltspice.png)

I started out with the fully open source [ngspice](https://ngspice.sourceforge.io/)
which it has its own [control language](https://ngspice.sourceforge.io/ngspice-control-language-tutorial.html), 
but I soon ran into presistent issues with simulation convergence.[^oscillator_convergence]
I eventually gave up and switched to 
[LTspice](https://www.analog.com/en/resources/design-tools-and-calculators/ltspice-simulator.html),
now owned by Analog Devices after their acquisition of Linear Technologies.

LTspice is not open source, but it's 100% free as-in-beer, comes with a huge component library,
and it has never given up on me  with a non-converging simulation error.[^time_step_too_large]
Since LTspice only runs on Windows, I bought 
[the cheapest laptop](/2025/03/12/HP-Laptop-17-RAM-Upgrade.html) I could find just
for this purpose.[^wine]

[^oscillator_convergence]: ngspice is generally fine, but I suspect that the simulation
                           covergence issues pop up when the design contains an oscillator. 
                           In my case, the oscillator was part of a DC/DC boost converter.

[^time_step_too_large]: That doesn't mean that LTspice never has simulation issues.
                        A few times, I got [very strange results](https://electronics.stackexchange.com/questions/754308/understand-mismatch-between-small-signal-ac-amplitude-and-transient-amplitude-a) 
                        that were solved by making the minimal simulation time step smaller.

[^wine]: I have friends who successfully run LTspice under Linux by using [Wine](https://www.winehq.org),
         but I'm past these kind of fragile hacks. 

LTspice is a little bit quirky. The GUI is opinionated and takes some time to get used to
and the waveform viewer has some annoying limitations when dealing with multiple
results. But what bothers me the most in the total lack of tools to help with managing
a project and dealing with multiple simulations that are associated with it.

There is a friendly LTspice forum on Groups.io where I asked how others dealt with these kind 
of issues, but I didn't really get [the answers](https://groups.io/g/LTspice/topic/115566583#msg162688) 
that I was looking for.

# A Simple Example Design

Let's use a simple R/C circuit as illustration. I've added
a reverse polarized Zener diode to clamp the voltage across the
capacitor to a maximum value of 4.7V. This makes the circuit a
bit more interesting. 

![Basic RC circuit with Zener diode. No simulation instructions](/assets/pyltspice/rc_schematic_basic.png)

I want to:

* simulate the design with different values of R1 and C1
* measure the rise time when it is subjected to a step function
  at its input
* check the effect of the Zener diode for different input voltages
* create a plots to compare different cases

Let's add a few directives to prepare the schematic for simulation:

![Schematic with R and C as parameters and .meas instructions](/assets/pyltspice/rc_schematic_with_params_and_meas.png)

* the values of R1 and C1 have been replaced by parameters `{r}` and `{c}`.
* for transient simulations, input voltage source V1 has been assigned a
  piecewise linear function that's 0 V at the start and quickly rises
  to 1 V after 2 ms.
* 3 `.meas` directives measure `start_rise`, `end_rise`, and `rise_time`.
  These are the timestamps where the output waveform crosses 0.1 V and 0.9 V,
  and the time difference between those 2 points.

# Some Alternatives that don't Require Scripting

**Use up to 2 .step directives**

If we only need to go through a list of values for 2 parameters, we 
can add the `.step` directive to the schematic. Like this:

```
.step param r list 1k 2k 4k
.step param c list 1u 3u 5u
```

When you simulate this as a transient simulation, click on the `out` net and you'll
see something like this:

[![RC schematic with plot window that has 6 waveforms](/assets/pyltspice/rc_schematic_params_and_step.png)](/assets/pyltspice/rc_schematic_params_and_step.png)
*(Click to enlarge)*




Issue:

* PyLTSpice instead of PyLTspice 
* When you save a schematic in LTspice, you have to specify ".asc" even if that's
  already specified in the file dialog.
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
