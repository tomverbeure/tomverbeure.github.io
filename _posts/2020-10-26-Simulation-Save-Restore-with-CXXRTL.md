---
layout: post
title: Simulation Save/Restore Checkpointing with CXXRTL
date:  2020-10-26 00:00:00 -1000
categories:
---

* TOC
{:toc}

# Introduction

In my [initial blog post about CXXRTL](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html), I
wrote about how the underlying data model of CXXRTL allows for 
[design introspection](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html#design-introspection), and
how this could be used for save the state of a design to a file, and later restore it.

I wanted to try this out on a real example, so that's what I'll be discussing here.

The design is not a toy example: it contains a VexRiscv RISC-V CPU with memories, LEDs, and a UART to
print out status messages.

# Save/Restore Checkpoint Use Cases

Before diving into the details, let's talk about some potential use cases.

* Accelerated debugging of long running simulations

    In most RTL regression setups, thousands of simulations are run day in/day out on a simulation farm
    with all debugging features disabled for maximal simulation speed.

    When a regression simulation fails, the whole simulation gets rerun with wave dumping enabled.

    That's a problem when the simulation fails after many hours or even days. Dumping waveforms at 
    all times is not an option, because it slows down the simulation by an order of magnitude.

    With a checkpoint save/restore option, one could simulate without dumping waveforms but instead 
    save the state of the design at fixed intervals, say, every 5 minutes, while deleting the previous 
    snapshot to save disk space.

    After a simulation failure, one can quickly get waveforms by restarting the simulation after the
    last saved checkpoint.

    The additional run time for a checkpoint save operation is minimal.

* Aggressive Waveform Format Compression

    This is an expansion of the previous use case.

    Instead of dumping the changed values of signals whenever they happen, one could instead save
    checkpoints at regular intervals, together with the simulation model. The checkpoints themselves
    could even be incremental from one step to the other.

    When zooming in on a waveform, the waveform viewer would have to simulate on-the-fly, but that
    might be an acceptable trade-off.

    There are all kinds of optimizations possible: while simulating, you could keep track of each
    signal whether or not a value has stayed constant or not, thus allowing some kind of immediate
    visual feedback in the waveform viewer about whether or not something interesting has happened
    for a particular signal.

    [Siloti](https://www.synopsys.com/verification/debug/siloti.html) by Synopsys uses this kind of
    method to reduce the bulk of waveform data.

* Bypassing a fixed long-running configuration sequence

    Imagine simulating an SOC that runs Linux or some other piece of software that requires a long
    bootup sequence.

    One could save a checkpoint after the initialization sequence has completed, but before a specific
    HW driver has started executing.

    With a bit of planning, it's possible to restart a simulation at the checkpoint, even when the HW 
    driver is different for each run, thus allowing rapid driver development interations on the
    simulation model.

    It's even possible to do this when the RTL of the HW under test changes between runs: all one needs 
    to do is keep the HW under test in reset up to the checkpoint. 

# The CXXRTL Data Model

Creating a simulation checkpoint requires an understanding of how a CXXRTL model stores the data of all
state holding objects. This can be derived from the 
[`cxxrtl.h`](https://github.com/YosysHQ/yosys/blob/master/backends/cxxrtl/cxxrtl.h), a
file that gets included in any CXXRTL generated model.

At the lowest level, CXXRTL has templated
[`value`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L83), 
[`wire`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L638), 
and [`memory`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L681) classes.
These are used to create the basic primitives that contain simulated data values.

* `value`

    Used for objects that contain  a single simulation value.

    A `value` is always used to represent a combinatorial signal in your design (but not all
    combinatorial signals are represented by a `value`.)

* `wire`

    This awkwardly named class (`reg` would have been a better name IMO) is used for objects that 
    contain the current simulation value, and the next simulation value.

    In most cases, this will be an object that is used to store the contents of a flip-flop
    or a latch. There are some cases where a `wire` is used for a combinatorial signal, such as for
    output signals of a module. *For our save/restore purpose, it's not important to understand
    these low level implementation details.*

* `memory`

    Self-explanatory: when using Verilog, this would be used to store an object that's declared
    like this `reg [7:0] memory[0:1023]`.

While one could use these objects directly when accessing the internal simulation values of a design,
it wouldn't be very pratical: they don't have the same base class, and the way they store the simulation
data differs per class.

But that's ok, because there's a much better way: the 
[`debug_item`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl.h#L826)
class exists specifically to allow external code to access the simulation values in a uniform way. It
also makes it possible to write CXXRTL testbenches with introspection in pure C, rather than C++. (You
still need to compile the CXXRTL model itself with a C++ compiler.) This is useful when you want to embed
your simulation model into a program that's written in C, such the standard Python compiler.

A `debug_item` exposes the following aspects of the simulation data holding objects:

* [`type`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L80)

    Whether the item is a `value`, `wire`, `memory`, or an `alias` (which maps one netlist item to another one
    with identical value.)

* [`flags`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L127)

    Contains all kind of attributes of the simulation object. The direction of module ports, whether or not a wire is
    driven by a storage cell, etc. 

* [`width`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L195), 
   and [`lsb_at`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L198)

    The size, in bits, of the value, and the bit number of the LSB.

    These values are essential to interpret the simulation data values correctly.

* [`depth`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L201), 
    and [`zero_at`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L204)

    For memories, these indicates the amount of memory locations in the memory, and index of the first word.

    For  a `wire` or `value`, these fields are set to 1 and 0 resp.
    Since a `debug_item` has a uniform interface for all simulation data, one doesn't need to have a special
    case to access data between the 3 storage classes: you can assume all `debug_items` to be memories, but with only 1 location.

* [`curr`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L217),
    and [`next`](https://github.com/YosysHQ/yosys/blob/cd8b2ed4e6f9447c94d801de7db7ae6ce0976d57/backends/cxxrtl/cxxrtl_capi.h#L218)

    Pointers to the actual simulation data!

    For a `wire` and `memory`, `next` is a null pointer.

    `curr` and `next` are `uint32_t` pointers because the C++ simulation model ultimately uses that as the way to store simulation data. 

    It's all pretty straightforward: the LSB of a vector is stored at bit 0 of the first `uint32_t` word, and as many `uint32_t` words
    are allocated to store all the bits of a vector.

# Save/Restore of the VexRiscv Simulation Example

I updated my main CXXRTL example (in the [./cxxrtl](https://github.com/tomverbeure/cxxrtl_eval/tree/master/cxxrtl) directory)
to add save/restore checkpointing.

The design runs the [following program](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/sw/main.c#L52-L78) 
on a VexRiscv CPU: 

```c
int main() 
{
    uart_init();
    uart_tx_str("\nHello World!\n");

    REG_WR(LED_DIR, 0xff);
    for(int i=0;i<1500;++i){
        REG_WR(LED_WRITE, 0x01);
        wait_cycles(100);
        REG_WR(LED_WRITE, 0x02);
        wait_cycles(100);
        REG_WR(LED_WRITE, 0x04);
        wait_cycles(100);
    }

    uart_tx_str("\nLEDs done!\n");

    while(1);
}
```

The testbench has new [debug level command line parameters](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L19-L34) 
to specify saving a checkpoint and restoring it:

```
  // <executable> <debug level> <vcd filename> 
  // debug level:
  // 0 -> No dumping, no save/restore
  // 1 -> dump everything
  // 2 -> dump everything except memories
  // 3 -> dump custom (only wires)
  // 4 -> save to checkpoint
  // 5 -> restore from checkpoint
```

**Simulation Save**

`./example_Og_clang9 4` dumps the design state after 10000 simulation cycles into `checkpoint.val` file:

```
ubuntu@ubuntu-xenial:~/projects/cxxrtl_eval/cxxrtl$ ./example_Og_clang9 4
UART TX:
UART TX:

UART TX: H
UART TX: e
UART TX: l
UART TX: l
UART TX: o
UART TX:
UART TX: W
UART TX: o
UART TX: r
UART TX: l
UART TX: d
UART TX: !
UART TX:
UART TX:

led_red: 1 0
led_red: 0 1
...
led_green: 1
led_green: 0
led_blue: 1
led_red: 1 18
led_blue: 0
Saving checkpoint...
```

Note how the simulation starts with the CPU writing "Hello World!" to the UART of the design, then it goes
18 times through an LED toggling sequence.

**Simulation Restore**

`./example_Og_clang9 5` restores the design from `checkpoint.val` and continues where the design was saved earlier:

```
ubuntu@ubuntu-xenial:~/projects/cxxrtl_eval/cxxrtl$ ./example_Og_clang9 5
Restoring from checkpoint...
Restore done...
All items:
       _zz_ExampleTop_1_ : type = 0 ; width =    5 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 31
       _zz_ExampleTop_2_ : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 0
                  button : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 0
                 clk_cpu : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 0
          clk_cpu_reset_ : type = 3 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 1
clk_cpu_reset_gen_reset_cntr : type = 1 ; width =    5 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 31
clk_cpu_reset_gen_reset_unbuffered_ : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 0
clk_cpu_reset_gen_reset_unbuffered__regNext : type = 1 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 1
 cpu_u_cpu _zz_CpuTop_1_ : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 0
...
                uart_rxd : type = 0 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 0
                uart_txd : type = 3 ; width =    1 ; depth =      1 ; lsb_at =   0 ; zero_at =   0 ; value = 1

led_red: 1 0
led_red: 0 1
led_green: 1

...

led_red: 0 1482
led_green: 1
led_green: 0
led_blue: 1
UART TX:
UART TX:

UART TX: L
UART TX: E
UART TX: D
UART TX: s
UART TX:
UART TX: d
UART TX: o
UART TX: n
UART TX: e
UART TX: !
UART TX:
UART TX:
```

There are 2 important things to note here:

* CPU does NOT print out "Hello World!"
* the LED toggle sequence happens 1482 times, not 1500

That's because the simulation picked up where it was saved after 18 LED toggle sequences.

# Adding Save/Restore to a CXXRTL Testbench

Through the design introspection feature of CXXRTL, you can get the simulation values of all `value`, `wire`, and `memory` objects of the
design that link back to an original Verilog named object.  The reverse is not necessarily true: depending on the CXXRTL 
optimization level, or on optimization steps that were performed by Yosys, named objects of the Verilog source code may 
not exist in the simulation model anymore.

To avoid race conditions, CXXRTL expects that values are set by a testbench after the clock has been simulated into a low state, 
and that values are read by the testbench after a high state has been simulated. I used the same convention when dumping and
restoring the state.

While dumping state, I only save the contents of `wire` and `memory` objects. The simulation value of `value` objects can be derived
by executing a simulation step.

The full process is as follows:

* Prepare the design for introspection

    This is no different than preparing the design for [VCD waveform dumping](/2020/08/08/CXXRTL-the-New-Yosys-Simulation-Backend.html#dumping-vcd-waveforms), 
    which I covered in my earlier blog post.

    ```c
    cxxrtl_design::p_ExampleTop top;
    cxxrtl::debug_items all_debug_items;
    top.debug_info(all_debug_items);
    ```

* Dump the design state when the simulation hits 10000 clock cycles

    In the [main testbench](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L99-L104),
    I call the `save_state` function:

    ```c
    if (dump_level == 4 && i==10000){
        cout << "Saving checkpoint..." << endl;
        std::ofstream checkpoint("checkpoint.val");
        save_state(all_debug_items, checkpoint);
        exit(0);
    }
    ```

    This code is called after the design has been simulated [with the clock set to 1](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L65-L66):

    ```c
    top.p_osc__clk__in.set<bool>(true);
    top.step();
    ```

    By default, [`save_state`](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/lib/cxxrtl_lib.h#L6) 
    only stores the value of `wire` and `memory` objects:

    ```
    void save_state(cxxrtl::debug_items &items, std::ofstream &save_file, 
                       uint32_t types = (CXXRTL_WIRE | CXXRTL_MEMORY));
    ```

    The [implementation](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/lib/cxxrtl_lib.cpp#L10-L27) 
    is straightforward but naive:

    ```c
    void save_state(cxxrtl::debug_items &items, std::ofstream &save_file, uint32_t types)
    {
        save_file << items.table.size() << endl;
        for(auto &it : items.table){
            save_file << it.first << endl; 
            for(auto &part: it.second){
                if (part.type & types){
                    uint32_t *mem_data = part.curr;
                    for(int a=0;a<part.depth;++a){
                        for(int n=0;n<part.width;n+=32){
                            save_file << *mem_data << endl;
                            ++mem_data;
                        }
                    }
                }
            }
        }
    }
    ```

    Note how it saves the name (`it.first`) of all simulation objects, even when they don't match the request
    `types` argument. In practice, this means that it dumps the name of all `value` objects as well, but it
    doesn't dump the associated data that comes with it. This is a place where the code can be improved...

    But more important, notice how easy it is to fetch and save the simulation values of the requested
    simulation objects.

* Restore the design state at the start of a simulation

    The testbench [calls the `restore_state` function](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L57-L63) for this:

    ```c
    if (dump_level == 5){
        cout << "Restoring from checkpoint..." << endl;
        std::ifstream checkpoint("checkpoint.val");
        restore_state(all_debug_items, checkpoint);
        cout << "Restore done..." << endl;
        dump_all_items(all_debug_items);
    }
    ```

    [`restore_state`](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/lib/cxxrtl_lib.cpp#L29-L57)
    is just as straightforward as `save_state`:

    ```c
    void restore_state(cxxrtl::debug_items &items, std::ifstream &restore_file, uint32_t types)
    {
        int size;
        restore_file >> size;
    
        for(int i=0;i<size;++i){
            std::string name;
            uint32_t value;
    
            std::getline(restore_file,name);

            vector<cxxrtl::debug_item> &item_parts = items.table[name];
            for(auto &part: item_parts){
                if (part.type & types){
                    uint32_t *mem_data = part.curr;
                    for(int a=0;a<part.depth;++a){
                        for(int n=0;n<part.width;n+=32){
                            restore_file >> value;
                            *mem_data = value;
                            ++mem_data;
                        }
                    }
                }
            }
        }
    }
    ```

    After restoring the state, it's important to 
    [run a simulation step with the clock set to 1](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L65-L66).


And that's all there is to it!

# Design Introspection to Capture the UART TX Writes

To better illustrate that save/restore actually worked, the testbench captures
writes to the TX register of a [SpinalHDL UART](https://spinalhdl.github.io/SpinalDoc-RTD/SpinalHDL/Libraries/Com/uart.html)
that is connected to the CPU through a standard APB3 bus. 

The individual signals are referenced [as follows](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L71-L75):

```c
    cxxrtl::debug_item psel    = all_debug_items.at("cpu_u_cpu u_uart io_apb_PSEL");
    cxxrtl::debug_item penable = all_debug_items.at("cpu_u_cpu u_uart io_apb_PENABLE");
    cxxrtl::debug_item pwrite  = all_debug_items.at("cpu_u_cpu u_uart io_apb_PWRITE");
    cxxrtl::debug_item pwdata  = all_debug_items.at("cpu_u_cpu u_uart io_apb_PWDATA");
    cxxrtl::debug_item paddr   = all_debug_items.at("cpu_u_cpu u_uart io_apb_PADDR");
```

The testbench [intercepts writes](https://github.com/tomverbeure/cxxrtl_eval/blob/26e7a499e24aa4c9e7142e0328e519f868c83cab/cxxrtl/main.cpp#L89-L96)
to the UART TX register at address 0 and prints out the transmitted character:

```c
    if (debug_item_get_value32(psel)    &&
        debug_item_get_value32(penable) &&
        debug_item_get_value32(pwrite)  &&
        debug_item_get_value32(paddr) == 0
    ){
        // APB write to UART RXTX register
        cout << "UART TX: " << (char)debug_item_get_value32(pwdata) << endl;
    }
```

# More Complex Designs and Potential Improvements

While non-trivial, the example is only a proof of concept to illustrate the basics, but it doesn't deal with  
complexities that can make save/restore operations a lot harder. 

**Asynchronous clock domains**

A design with multiple, asynchronous clock domains will require careful timing of when to capture the
data to avoid mismatches. I haven't tried this out myself.

**Taking care of external state**

More fundamentally, testbenches that have their own state that influences the design under simulation
will need to either save/restore their state as well, or they'll have to accept the reality that a
restored design might not simulate exaclty the same way as the design would have simulated if it hadn't
been interrupted. This doesn't have to be a problem, but it's something to be aware of.

**Dealing with changed design**

The current code expects that the CXXRTL simulation model remains the same between save and restore. It's
sufficent for 1 register to change, and it will fail horribly, hopefully with a coredump.

A robust system should deal with these cases gracefully. It could just issue a fatal, and informative, error.
Or it could even decide to just warn and continue, for the second use case in my introduction, where
RTL has changed between simulations, but the changed RTL was in reset at the time of the checkpoint.

**Optimized checkpoint file format**

The `save_state` routine is very inefficient, since it just dumps all the hierarchical names in full as well
as the data itself as an ASCII string. This can probably be optimized by 2 orders of magnitude!

# Conclusion

CXXRTL makes it easy to save and restore a simulation. It's not something that you'll often, but 
one day, you might run into a use case where it can save a major amount of simulation time.



