---
layout: post
title: CXXRTL Under the Hood
date:  2020-08-09 00:00:00 -1000
categories:
---

* TOC
{:toc}


* 

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

Relevant whitequark tweets:

GitHub:
* [GitHub Initial pull request](https://github.com/YosysHQ/yosys/pull/1562)


Foundational paper:
* [A Fast & Effective Heuristic for the Feedback Arc Set Problem](https://pdfs.semanticscholar.org/c7ed/d9acce96ca357876540e19664eb9d976637f.pdf)
