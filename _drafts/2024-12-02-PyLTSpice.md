---
layout: post
title: PyLTSpice for LTspice project management
date:   2025-10-05 00:00:00 -1000
categories:
---

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
