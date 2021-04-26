---
layout: post
title: Porting the Embench Benchmark to a VexRiscv Embedded System
date:  2020-12-19 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Steps

[Adding a New Board to Embench](https://github.com/embench/embench-iot/tree/master/doc#adding-a-new-board-to-embench)

* Fork embench repo
* Clone the fork to your PC and create new branch

    ```
    git clone git@github.com:tomverbeure/embench-iot.git embench-iot-tvb
    cd embench-iot-tvb
    git checkout -b vex
    ```

* I created an FPGA project with a VexRiscv and semihosting for the Arrow DECA FPGA board called "vex_deca".
  Create a board configuration directory for this:

    ```
    cd config/riscv32/boards
    mkdir vex_deca
    ```

* Create a board.cfg file:

    This is actually a Python file with parameters that would otherwise
    be specified on the command line.

    My design runs at 50Mhz...
    
    `board.cfg`:
    ```
    cpu_mhz = 50
    ```

* Create `boardsupport.h` and `boardsupport.c` files

    Required functions: `initialize_board()`, `start_trigger()`, `stop_trigger()`


# References

* [Embench Website](https://www.embench.org/)
* [Embench GitHub repo](https://github.com/embench/embench-iot)
    * [User Guide](https://github.com/embench/embench-iot/tree/master/doc)
* [Antmicro Embench-LiteX results](https://antmicro.github.io/embench-tester/)
