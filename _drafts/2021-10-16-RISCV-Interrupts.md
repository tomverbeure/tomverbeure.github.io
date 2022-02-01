---
layout: post
title: RISC-V Interrupts
date:  2021-10-16 00:00:00 -1000
categories:
---

* TOC
{:toc}


* [RISC-V Function attributes](https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Function-Attributes.html)

    Save all registers that are being used by the trap function:
    `void  __attribute__ ((interrupt ())) trap(){ ... }`

* noline

    `void __attribute__ ((noinline)) test(void)`

    Useful to test implications when being called by function with interrupt attribute

* [GCC RISC-V Option](https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html)

    * `CFLAGS          += -msave-restore`
    * `CFLAGS          += -mno-div`
    * `CFLAGS          += -mtune=processor-string`



# References

* [GCC Global Pointer and Thread Pointer handling](https://groups.google.com/a/groups.riscv.org/g/sw-dev/c/SkTelK-juC4)
* [The gp (Global Pointer) register](https://gnu-mcu-eclipse.github.io/arch/riscv/programmer/#the-gp-global-pointer-register)
* [RISC-V ABI Register Mapping](https://gnu-mcu-eclipse.github.io/arch/riscv/programmer/#abi)
* [gcc gp (global pointer) register discussion](https://groups.google.com/a/groups.riscv.org/g/sw-dev/c/60IdaZj27dY/m/LEVf8SrFAQAJ)
* [GCC RISC-V Options](https://gcc.gnu.org/onlinedocs/gcc/RISC-V-Options.html)
    * Some options are outdated? E.g. -mstack-protector-guard=guard doesn't work, but  -fstack-protector-all does.
* [SiFive - All Aboard, Part 2: Relocations in ELF Toolchains](https://www.sifive.com/blog/all-aboard-part-2-relocations)
* [SiFive - All Aboard, Part 3: Linker Relaxation in the RISC-V Toolchain](https://www.sifive.com/blog/all-aboard-part-3-linker-relaxation-in-riscv-toolchain)
* [RISC-V: A Baremetal Introduction using C++ Series](https://philmulholland.medium.com/modern-c-for-bare-metal-risc-v-zero-to-blink-part-1-intro-def46973cbe7)
* [The Adventures of OS - RISC-V using Rust - Handling Interrupts and Traps](https://osblog.stephenmarz.com/ch4.html)
* [SiFive Interrupt Cookbook](https://starfivetech.com/uploads/sifive-interrupt-cookbook-v1p2.pdf)
* [RISC-V Fast Interrupts Presentation](https://riscv.org/wp-content/uploads/2018/05/08.45-09.10-RISCV-20180509-FastInts.pdf)
* [SiFive - An Introduction to the RISC-V Architecture](https://cdn2.hubspot.net/hubfs/3020607/An%20Introduction%20to%20the%20RISC-V%20Architecture.pdf)

    Presentation that has a good example about interrupts.


