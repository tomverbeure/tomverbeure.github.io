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

`step()` is most important method of a `module`. It's defined in the `module` superclass and small
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

The testbench calls `step()` on the toplevel module. It will execute a loop
of `eval()` and `commit()` phases until all simulation values of the design have "converged" 
or until there are no more changes in the design state variables (`wire`s).


Let's look at that in a bit more detail:

* `eval()`

    Each module has an `eval()` function that calculates all the values of design signals (these can
    be `value` objects, or the `.next` part of a `wire` object.

    When a module has submodules, that module's `eval()` function will call the `eval()` method
    of the submodules.


"converged" means the following: "whether there were any changes during commit or not, the next call 
to eval won't change anything". 

Whether or not a particular module converges during eval is calculated by the CXXRTL backend 
([here](https://github.com/YosysHQ/yosys/blob/859e52af59e75689f7b0615899bc3356ba5a7ca1/backends/cxxrtl/cxxrtl_backend.cc#L2269)):

```c++
    eval_converges[module] = feedback_wires.empty() && buffered_comb_wires.empty();
```



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

# Eval / Commit Cycles

While CXXRTL is anything but trivial, it still strives to be relatively simple. There are a number of performance
trade-offs made because of that. 

One of them is the 2-phased eval/commit process, which makes things easier, but is often not necessary.

Let's illustrate this with an example, a ring of flip-flops:

```verilog
    ...
    reg k1, k2, k3;

    always @(posedge clk) begin
        k1 <= k3;
        k2 <= k1;
        k3 <= k2;
    end
    ...
```

CXXRTL assigns a `wire` for all state holding design elements (other than memories), calculates
the `.next` value of these elements during the `eval()` phase, and copies over the values from
`.next` to `.curr` during the `commit()` phase. During the `commit()` phase, it also checks
if any over the state elements has their value changed, which will be used later on to
decide whether or not to do another `eval()` phase for the same clock cycle.

The abbreviated generated code looks like this:

```c++
struct p_ring__of__ffs : public module {
	wire<1> p_k3;
	wire<1> p_k2;
	wire<1> p_k1;
        ...
};

bool p_ring__of__ffs::eval() {
    ...
    if (posedge_p_clk) {
        p_k1.next = p_k3.curr;
    }
    if (posedge_p_clk) {
        p_k2.next = p_k1.curr;
    }
    if (posedge_p_clk) {
        p_k3.next = p_k2.curr;
    }
    ...
}

bool p_ring__of__ffs::commit() {
    bool changed = false;
    changed |= p_k3.commit();
    changed |= p_k2.commit();
    changed |= p_k1.commit();
    prev_p_clk = p_clk;
    return changed;
}
```

This code works great and is easy to understand!

By having a current and a next value of the state element, the next values can be assigned in
any order without running the risk of a race condition. But it has the problem that a single
state update requires a memory read (fetch `.curr`) and a memory write (store to `.next`) during
`eval()`, and two more memory read (fetch `.curr` and `.next`) and potential memory write (store to `.curr`) during
`.commit()`.

Here's the pseudo-code of Verilator does it:

```c++
VL_MODULE(Vring_of_ffs) {
    ...
    // LOCAL SIGNALS
    // Internals; generally not touched by application code
    VL_SIG8(ring_of_ffs__DOT__k1,0,0);
    VL_SIG8(ring_of_ffs__DOT__k2,0,0);
    VL_SIG8(ring_of_ffs__DOT__k3,0,0);
    ...
};

VL_INLINE_OPT void Vring_of_ffs::_sequent__TOP__1(Vring_of_ffs__Syms* __restrict vlSymsp) {
    Vring_of_ffs* __restrict vlTOPp VL_ATTR_UNUSED = vlSymsp->TOPp;
    // Variables
    VL_SIG8(__Vdly__ring_of_ffs__DOT__k1,0,0);
    // Body
    __Vdly__ring_of_ffs__DOT__k1 = vlTOPp->ring_of_ffs__DOT__k1;
    // ALWAYS at blink.v:95
    __Vdly__ring_of_ffs__DOT__k1 = vlTOPp->ring_of_ffs__DOT__k3;
    // ALWAYS at blink.v:95
    vlTOPp->ring_of_ffs__DOT__k3 = vlTOPp->ring_of_ffs__DOT__k2;
    // ALWAYS at blink.v:95
    vlTOPp->ring_of_ffs__DOT__k2 = vlTOPp->ring_of_ffs__DOT__k1;
    vlTOPp->ring_of_ffs__DOT__k1 = __Vdly__ring_of_ffs__DOT__k1;
}

void Vring_of_ffs::_eval(Vring_of_ffs__Syms* __restrict vlSymsp) {
    ...
    if (((IData)(vlTOPp->clk) & (~ (IData)(vlTOPp->__Vclklast__TOP__clk)))) {
	vlTOPp->_sequent__TOP__1(vlSymsp);
	vlTOPp->__Vm_traceActivity = (2U | vlTOPp->__Vm_traceActivity);
    }
    ...
}
```

Simplified, it essentially does this:

```c++
    unsigned char k1, k2, k3;

    if (clk && !clklast_clk){
        unsigned char dly_k1 = k1;
        dly_k1 = k3;
        k3 = k2;
        k2 = k1;
        k1 = dly_k1;
    }
```

CXXRTL and Verilator do a topological sort on values to ensure that they assigned in the right order during the
`eval()` phase, but Verilator also does a topological sort on the state elements, to ensure that no value gets
lost before its needed. And for those chases where there's an assignment loop, as is the case above with `k1`, a temporary
variable is introduced to break that loop.

For each state variable, a minimum of 4, and 5 when there's value change, memory transactions is reduced to 2 transaction 
in most cases.

But what about the `changed` value that is calculated by `commit()`?

It turns that this is not needed for almost all well-behaved code: circuits with combinatorial feedback loops won't
ever have cases where the calculated values don't converge in the first `eval()` phase, so `converged` is always true. 
And since the trigger to recalculate is a combination of `changed && !converged`, a second invocation of `eval()`
won't happen either.


# References

GitHub:
* [GitHub Initial pull request](https://github.com/YosysHQ/yosys/pull/1562)


Foundational paper:
* [A Fast & Effective Heuristic for the Feedback Arc Set Problem](https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf)



Questions:




