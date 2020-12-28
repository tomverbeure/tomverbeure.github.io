---
layout: post
title: CXXRTL On the Move - A Quick Look at Recent Improvements
date:  2020-12-22 00:00:00 -1000
categories:
---

* TOC
{:toc}

# CXXRTL On The Move

The first CXXRTL commit was made on December 1, 2019, a bit over 1 year ago.  I only started playing with it around April,
at time during which there was a avalanche of commits, often with major performance and feature improvements. Around June, 
things slowed down, and on August 8th, I published [my first blog post](https://tomverbeure.github.io/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html).

After that there wasn't a lot of activity for a good couple of months, but that suddenly changed in the past few weeks.

The dust is once again settling down a bit, and this is the result:

* C++ code generator has been modified to make it friendlier on the C++ compiler
* raw simulation speed has been signficantly improved
* a single binary simulation executable model can now support for waveform dumping without 
  impacting simulation speed when dumping is disabled
* a new scheduler that doesn't break down after applying some Yosys optimization.

[Whitequark](https://twitter.com/whitequark), CXXRTL's author, has stated multiple times simulation performance
is not the primary objective of CXXRTL, and I totally agree: there's a point where speed is good enough and features
determine the usefulness of a tool, and CXXRTL is IMO well beyond that point.

That said, I just can't help running some benchmarks to see how my VexRiscv benchmark improves with each new release.

The new results below were created with Yosys versions:

* Old: `Yosys 0.9+3667 (git sha1 e7f36d01e, clang 6.0.0-1ubuntu2 -fPIC -Os)`
* New: `Yosys 0.9+3780 (git sha1 d15c63eff, clang 6.0.0-1ubuntu2 -fPIC -Os)`

For comparison, I used Verilator 4.033 in single threaded mode.


# Simulation Model Compile Time

Due to its heavy use of C++ templates, CXXRTL is very hard to C++ compilers. Even a relatively small
simulation model can take a long time to compile.

My primary use case is waveform debugging, so 95% of the time, I create CXXRTL models with maximum debug
options enabled (`-g4`). By default, I use clang9 on an Ubuntu 18.04 system.

<table>
<tr>
    <th>C++ compiler</th>
    <th>CXXRTL Debug Option</th>
    <th>Old</th>
    <th>New</th>
    <th>Change</th>
</tr>
<tr>
    <td>clang9</td>
    <td>-g4</td>
    <td>0m23.999s</td>
    <td>0m6.787s</td>
    <td>-71%</td>
</tr>
<tr>
    <td>clang9</td>
    <td>-g2</td>
    <td>0m11.839s</td>
    <td>0m6.449s</td>
    <td>-46%</td>
</tr>
<tr>
    <td>clang6</td>
    <td>-g2</td>
    <td>0m23.264s</td>
    <td>0m21.907s</td>
    <td>-6%</td>
</tr>
<tr>
    <td>gcc10</td>
    <td>-g2</td>
    <td>1m18.003s</td>
    <td>0m15.221s</td>
    <td>-81%</td>
</tr>
<tr>
    <td>gcc7</td>
    <td>-g2</td>
    <td>1m9.741s</td>
    <td>0m12.941s</td>
    <td>-82%</td>
</tr>
</table>

Conclusions:

* Massive 71% compile time reduction time for my primary use case
* No more compile time penalty for enabling maximum debugging
* Don't use clang 6.
* Don't use gcc 7 or gcc 10


# Simulation Performance

<table>
<thead>
<tr><th>Simulator  </th><th>Debug  </th><th>VCD                </th><th>C++ compiler  </th><th style="text-align: right;">  Time (s)</th></tr>
</thead>
<tbody>
<tr><td>Verilator  </td><td>       </td><td>No Waves           </td><td>clang9        </td><td style="text-align: right;">     0.452</td></tr>
<tr><td>Verilator  </td><td>       </td><td>VCD                </td><td>clang9        </td><td style="text-align: right;">     7.810</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>No VCD             </td><td>clang9        </td><td style="text-align: right;">     1.136</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>VCD full (incl Mem)</td><td>clang9        </td><td style="text-align: right;">    99.980</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>VCD full (no Mem)  </td><td>clang9        </td><td style="text-align: right;">     9.075</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>VCD regs only      </td><td>clang9        </td><td style="text-align: right;">     9.759</td></tr>
<tr><td>CXXRTL     </td><td>g4     </td><td>No VCD             </td><td>clang9        </td><td style="text-align: right;">     1.097</td></tr>
<tr><td>CXXRTL     </td><td>g4     </td><td>VCD full (incl Mem)</td><td>clang9        </td><td style="text-align: right;">   109.581</td></tr>
<tr><td>CXXRTL     </td><td>g4     </td><td>VCD full (no Mem)  </td><td>clang9        </td><td style="text-align: right;">    26.479</td></tr>
<tr><td>CXXRTL     </td><td>g4     </td><td>VCD regs only      </td><td>clang9        </td><td style="text-align: right;">     9.788</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>No VCD             </td><td>clang9        </td><td style="text-align: right;">     1.052</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>No VCD             </td><td>clang6        </td><td style="text-align: right;">     1.994</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>No VCD             </td><td>gcc10         </td><td style="text-align: right;">     1.120</td></tr>
<tr><td>CXXRTL     </td><td>g2     </td><td>No VCD             </td><td>gcc7          </td><td style="text-align: right;">     1.130</td></tr>
</tbody>
</table>
 
