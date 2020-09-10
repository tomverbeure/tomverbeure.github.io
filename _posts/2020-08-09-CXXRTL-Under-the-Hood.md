---
layout: post
title: CXXRTL Under the Hood
date:  2020-08-09 00:00:00 -1000
categories:
---

* TOC
{:toc}


# Event Driven Simulation - What CXXRTL is Not

There are 2 major types of RTL simulators: event driven and cycle based.

Event driven simulations are by far the most flexible: they have the ability to schedule the
execution of some kind of process simulation at pretty much any future point in time.

Simulators like Icarus Verilog and most commerical simulators, like Synopsys VCS or Modelsim, support
an event driven simulation model. CXXRTL and Verilator do not: they are pure cycle based.

To make it easier later to contrast the difference between an event-drive and cycle based simulator, 
I will discribe here what makes an event driven simulator tick.

An event driven simulator has 2 major elements:

* An time-ordered event list with process activations 

    This list contains time events in the future. For each time event, there is a set of process activations.

    For each time event, the simulator goes through the set of process activations and simulates the process
    until that process gets to a point where it must wait until some activation. (E.g. because it ran
    to completion, or because it's being instructed to halt for a certain amount of time.)

    Once all activation signals for a time event have been processed, the simulator discards the
    time event, and moves on the next one.

    New activation signals and time events are added to the event list when an assignment is made
    to a signal in an process that is being executed.

    It's possible for a process to add an activation for the current time stamp. In that case,
    it added to the next so-called delta cycle of the current time step.

* Simulation processes

    Processes have a sensitivity list: a set of signals that will trigger that process into executing 
    its simulation instructions.

    During these simulation instructions, assigments can be made to signals, which results
    in those signals being inserted into the event list.

Have a look at the pseudo-Verilog code below:

```verilog
    reg clk;
    initial clk = 0;

    always                                  // Activation: delay expiration
        clk <= #5 !clk;

    reg [7:0] a,b,c,d, sum, mul, result;

    always @(posedge clk) begin             // Activation: clk
        sum <= a + b;
        mul <= c * d;
    end

    always @(*)                             // Activation: sum, mul
        resulT = sum + mul

    reg [7:0] cntr;
    always @(posedge clk)                   // Activation: clk
        cntr <= cntr + 1;
```

The animation below shows how an event driven simulator would execute this:

![Event Driven Simulation Animation](/assets/cxxrtl/cxxrtl-event_driven.gif)

* At time *Now*, only 1 signal, `clk` is scheduled in the event list. Let's assume that its value has just
  changed from 0 to 1. This will trigger 3 processes (==`always` statement blocks). These processes will be
  executed in an order that is simulator dependent.
* First, the clock generation process is triggered. This process inserts an inverted value of `clk` in the event
  list 5ns after *Now*.
* The sum and multiply process is triggered. It assigned values to `sum` and `mul` without any delay
  value, so these get inserted in the event list at the current time plus 1 delta cycle: *Now + delta 1*.
* The `cntr` process is also triggered by `clk`. It assigned a value to `cntr`, which is also inserted to
  the next delta cycle, though that won't actually do anyting, because there are no other processes which have
  `cntr` in its sensitivity list.
* With all processes that are triggered by `clk` executed, time moves forward to the next step in the event list: *Now + delta 1*.
* `sum` and `mul` in the event list both trigger the `result` process. Since this assigns to the `result` signal without
  an explicity delay, `result` gets inserted into the event list at the next delta cycle, *Now + delta 2*.
* `count` in the event list gets discarded. (Any worthy simulator would never have put this in the event list to begin with!)
* Time now moves forward to *Now + delta 2*.


# From RTL to Simulation Model

State is retained in double buffered wires. Using single buffered wires introduces a race condition. (Why exactly?)

* `void execute`
    * process all command options
    * `prepare_design`
        * `check_design`
            Verify if the design still has synchronous initialization or memory cells
        * Yosys `flatten`
        * Yosys `proc`
        * Yosys `memory_unpack`
        * `check_design`
            Make sure that all sync inits and memories are gone.
        * `analyze_design`
            For all remaining modules (after flattening):
            * special case: black boxes
            * create FlowGraph of the module
                Graph with nodes (connections, sync cells, eval cells, processes), combinatorial wires, synchronous wires
                uses overloaded `add_node` 
                * Add all connections to flow graph
                * Add known cells to the flow graph
                    * Mark DFF cells and memory port cells as special posedge/negedge process: `register_edge_signal`
                * Gather all memories with transparent reads
                * Add all processes
                    * `register_edge_signal` for all edge triggered processes
                * Add all elidable wires
            * add FlowGraph into Scheduler
                FlowGraph nodes become scheduler vertices
            * run scheduler
            * find feedback wires
            * find all unbuffered and localized wires
            * find all buffered combinatorial wires
            * `eval_converges`: indicates for a given module that it fully converges, when there are no feedback wires and there are no
              buffered combinatorial wires.
            * find all bits in the module that have state
            * find all wires that are aliased to another wire or that are tied to a constant
            * issues warning about feedback wires and buffered combinatorial wires
    * `dump_design`
        * topologically sort all used non-internal cell and non-blackbox modules in the design.
            This is necessary so that C++ definitions of module objects are done in the right order.
        For all modules, dump the C++ CXXRTL code.
        * `dump_module_intf`, `dump_module_impl`


# CXXRTL Main Loop

CXXRTL converts your Yosys design in a set of modules, each of which are a subclass of
the `module` abstract base class.

`step()` is most important method of a `module`. It is identical for all module subclasses, and short
enough to list it here in full:

```cpp
    size_t step() {
        size_t deltas = 0;
        bool converged = false;
        do {
            converged = eval();
            deltas++;
        } while (commit() && !converged);
        return deltas;
    }
```

The testbench wrapper calls `step()` on the toplevel module. It will execute a loop
of `eval()` and `commit()` phases until all simulation values of the design have "converged" which
means that further invocations of `eval()` won't result in changes in any of the signals of the design.


# Elements of CXXRTL Module

They all follow this template:

```c
struct p_my_design : public module {

    value<1> p_my__signal;
    ...
    wire<32> pp_my__register;
    ...
    value<1> p_my__clk(); 
    value<1> prev_p_my__clk(); 
    bool posedge_p_my__clk() const {
        return !prev_p_my__clk.slice<0>().val() && p_osc__clk__in.slice<0>().val();
    }

    memory<8> memory_p_my__mem { 1024u, 
        memory<8>::init<8>::init<1> { 0x10, {
            value<8>{0x12},
        }},
    }

    ...
    p_sub__module cell_p_u__submodule;
    ...

    bool eval() override;
    bool commit() override;
    void debug_info(debug_items &items, std::string path = "") override;
}
```

The biggest chunk of the module declaration will consist of values, wires, and memories. Those are the basic
simulation primitives of CXXRTL.

* `value`

    An object that contains a single simulation value.

    A `value` is always used to represent a combinatorial signal in your design, but not all
    combinatorial signals are represented by a `value`.

* `wire`

    An object that contains the current value, and the next value.

    In most cases, this will be object is used to store the contents of a flip-flop
    or a latch, but there are some cases where a `wire` is used for a combinatorial.
    The most common case for this is an output signal of a module.

    (XXX are there any other cases?)

* `memory`

    Self-explanatory: when using Verilog, this would be used to store object that were declared
    as `reg [7:0] memory[0:1023]`.

When your CXXRTL module was written out with the `-noflatten` option, the module will also contain:

* `p_<name of submodule object> cell_<p_<instance name of the submodule>`

    A module that has non-flattened submodule instantiates each of these submodule. Each instance is
    called a "cell".

In addition to object instances, a module also contains a number of methods:

* `bool posedge_p_my__clk() const { ...`

    Whenever there's a signal inside a module that is used as a clock edge, CXXRTL creates 
    a method that check if there has been a rising (or falling) edge on that clock.

    Such a method is created for each clock that is used within a module. When a signal is used
    as a clock in a non-flatted subhierarchy but not used as a clock in the module itself, no
    such method is created.

* `bool eval()`

    The main method that calculate the new simulation values of all `values` and `wires`. It also
    invokes the `eval` methods of all the non-flattened submodule instances.

* `bool commit()`

    At the end of an `eval` cycle, this method copies over the next value of a `wire` to its
    current value, check if a 

# References

GitHub:
* [GitHub Initial pull request](https://github.com/YosysHQ/yosys/pull/1562)


Foundational paper:
* [A Fast & Effective Heuristic for the Feedback Arc Set Problem](https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf)
