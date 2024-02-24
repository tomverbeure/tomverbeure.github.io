---
layout: post
title: HP 8656A Signal Generator Repair - Getting Rid of the Stank
date:   2024-02-23 00:00:00 -0700
categories:
---

* TOC
{:toc}

# Introduction

A couple of years ago, I bought my first RF signal generator: an HP 8656A. It's an excellent
deal, just $80 at the Silicon Valley Flea Market. The seller insisted that it was functional,
what could possible go wrong?

![HP 8656A](/assets/hp8656a/hp8656a.jpg)


After dragging the 40lb beast home, I could, in fact, confirm that it did work... Sort of,
because there are defintely a couple of issues with it:

1. the front 'power' button doesn't work reliably
1. the signal output power doesn't match the programmed output power level
1. last, but not least, an unbearable chemical smell wafts out of the machine
  when it's running

Surprisingly, issues 1 and 2 aren't dealbreakers for most of my use cases, which
primarily consists of connecting to other test equipment and playing with it. But the
smell is so bad that using the machine for more than a few minutes makes you feel ill with
something that feels a soar throat... for a couple of days.

In this blog post, I take the machine apart to track down the source of the smell, and
how to fix it.

# Opening Up the 8656A







    You need to finess it gently to put it just in the right position and then
    never touch it again. After that, I switched the thing on and off by unplugging
    the power cord.

    Note the quotes when I write 'power' button. That's because it's more like a button
    to switch the machine in active or stand-by mode. There is no button to truly switch
    it off: the fan, LOUD!, always keeps spinning, for example.

    One reason to keep some of the internals powered on at all time is to keep the
    internal reference oscillator stable at the same temperature and thus avoid long
    stabilization times when switching the machine to active mode.


