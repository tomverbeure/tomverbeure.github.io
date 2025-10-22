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

*This section is entirly optinional, especially the rant about some of the LTspice GUI
quirks. Feel free to skip directly to the PyLTSpice section.*

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

The waveform viewer is not terrible, but it already has a bunch of warts:

* if you add any other waveform, say, the V(in), all the V(out) waveforms get the same color.

    ![Multiple waveforms, one color](/assets/pyltspice/multiple_waveforms_one_color.png)

    You can kind of avoid this by adding a second "plot pane" above or below (but not left or right of) 
    the current one.

* There is no obvious way to figure out which waveform is for which parameter combination.

    Moving your mouse cursor over a waveform is supposed to show this, but that doesn't work
    on my version 24.1.10, the latest one.

* You can't render measurement results in the plot window. 

    ![Log window](/assets/pyltspice/log_window.png)
 
    Instead, you need to view the log file. The genius software developers decided to make 
    that a model window, which means you can't operate the plot window without first closing 
    the log window. (Seriously, what were they thinking?) It's one of the many infuriating
    quirks of the LTspice GUI.[^asc_file_save]

[^asc_file_save]: One of my biggest pet peeves is the "Save As" behavior.
                  Like every other piece of software in the world, the file dialog shows 
                  "Schematics (\*.asc)" in the "Save as type:" field. 
                  But if you fill in a new file name without adding ".asc", it will
                  error out with "Unrecognized file name extension"... unlike every other piece
                  of software in the world, which will add the extension automatically.
                  ![Save File As dialog](/assets/pyltspice/save_file_as_dialog.png)

* You can't have multiple plot windows at the same time.

    This is important in you want to embed multiple plots from the same simulation
    in a document.

Even if you only have 2 parameters to step through, there's already a bunch of reasons to
consider a different way to create plots.

**Use a table and step through all desired combinations**

If you want to run simulations and change more than 2 parameters, there's a well known
hack to do that. It goes as follows:

* Create a table for each of the parameters:

```
.param r = table(idx, 1, 1k, 2, 2k, 3, 4k)
.param c = table(idx, 1, 1u, 2, 3u, 3, 5u)
```

* Use a step directive to step through all the table elements

```
.step param idx list 1 2 3
```

Like this:

[![RC schematic with param and table directives](/assets/pyltspice/rc_schematic_param_table.png)](/assets/pyltspice/rc_schematic_param_table.png)

This works, but there's only 3 waveforms instead of 9 because you now need
to list all combinations yourself.

There are other ways to make LTspice deal with multiple variables, but they're all awkward and
IMO worse than just biting the bullet and going the route of Python scripting.

# PyPLTSpice to the Rescue 

LTspice has a way to launch simulations in batch mode from the command line. This was once again
done in a half-assed way, but it creates an opening for whoever wants to write a wrapper around it.
What's what [PyLTSpice](https://github.com/nunobrum/PyLTSpice)[^pyltspice_spelling]
does, and more.

[^pyltspice_spelling]: LTspice is spelled with lower case 's'. PyLTSpice is spelled with an upper
                       case 'S'. This kind of inconsistency bothers me, but it is what it is.

**Don't confuse the`pyltspice` library with the `PyLTSpice` library!** 

[`pyltspice`](https://github.com/thennen/pyltspice) is a light-weight LTspice wrapper that
might work for you, but as I write this, it has the following note on the front
page: "I would not call this production-ready. If in doubt, use PyLTSpice."
That said, I did run into some PyLTSpice issues that were solved after I reported
them on GitHub. The code in this blog post should work on PyLTSpice 5.4.4 and later.

Assuming that you already have Python on your system, installation is just a matter of
running:

```sh
pip install PyLTSpice
```

With PyLTSpice, you can:

* read in the .asc schematics file
* manipulate the schematic: modify component values, change simulation instructions,
  add parameters, ...
* kick off one or more simulations in parallel
* read back and parse the waveform and log file results
* process the results with your favority Python libraries

The [documentation of PyLTSpice](https://pyltspice.readthedocs.io/en/latest/index.html) 
is a set of examples. It has sections that are intended to go over its Python classes, but
right now, these section are empty. For my needs, the examples were sufficient.

# My PyLTSpice Project Script Step by Step

[`pyltspice_prj.py`](/assets/pyltspice/pyltspice_prj.py) is the project script
that I created for the example RC schematic of this blog. 

**Reading in the LTspice design file**

To simulate (and optionally modify) a design, you first need to read it in.
In my case, I provide an `.asc` file, the proprietary file format of the LTspice GUI, but 
you can also provide a `.net` text netlist file that is more or less standard for all
Spice simulators.

```python
    asc_filename = Path("rc_schematic.asc")
    netlist = PyLTSpice.SpiceEditor(asc_filename.name)
```

If you have older PyLTSpice version than 5.4.4, you may have to read in the `.asc` file
in two steps:

```python
    asc_filename = Path("rc_schematic.asc")
    PyLTSpice.LTspice.create_netlist(asc_filename.name)
    netlist_file = asc_filename.with_suffix(".net")
    netlist = PyLTSpice.SpiceEditor(netlist_file)
```

Even when you don't want to make any modifications to the design and just simulate,
you still need to load the design first before kicking off the simulator.

**Make modification**

In my case, I want to simulate all combinations of a set of values for R1 and C1. I also
want to run a transient simulation and an AC small signal simulation.

```python
    r1_values   = [ '1k', '2k', '4k' ]
    c1_values   = [ '1u', '3u', '5u' ]

    sims = [
            { "name": "tran", "instruction": ".tran 50m startup" }, 
            { "name": "ac",   "instruction": ".ac dec 10 1 100k" } 
        ]
```


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
