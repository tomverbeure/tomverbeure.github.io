---
layout: post
title: Intuitive Estimation of the Number of Error Correction Bits
date:   2026-10-31 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>

* TOC
{:toc}

# Introduction

I've been interested in error correcting codes (ECC) for a while now, and though I haven't
really gotten anywhere, I keep on reading and, occasionally, 
[writing about it](/2022/08/07/Reed-Solomon.html).  
Except for really simple ones, ECC theory gets complicated quickly and I'm not very good at 
that.

The two codes that I've looked the most are 
[Reed-Solomon](https://en.wikipedia.org/wiki/Reed–Solomon_error_correction) 
and [BCH](https://en.wikipedia.org/wiki/BCH_code) 
codes. They are closely related: both add redundant symbols that are calculated
by evaluating a polynomial that's normally evaluated using 
[Galois Field math](/2026/06/14/Galois-Field-Arithmetic-Primer.html), though, as showing
in my earlier Reed-Solomon blog post, that's not strictly required. The encoding algorithm
is relatively straightforware, the decoding algorithims are significantly more complicated
but similar for both of them.

Reed-Solomon and BCH codes differ is the size of their symbols, their alphabet: the symbols
of the former consist of multiple bits, while the symbol of the latter is a bit.

# Hamming Distance

When you look at the theory of error detecting and correcting codes, the discussion
immediately turns to Hamming distance: the number of bit flips required to convert one
vector of bits to another. The goal of an error correcting code is to transform the input
vector, the message, to an output vector, the code word, so that the minimum distance
between code words is guaranteed the be a certain number. The higher the Hamming distance,
the higher number of bits that can be flipped without destroying the ability to recover
the original message.

# Intuitive Estimation of Error Correction Bits

Hamming distance is not particulary complicated, but in practice I found myself using an
even more simplistic mental model:

If a message of $$k$$ bits has 1 incorrect bit, you need a number of $$\lceil log_2(k) \rceil$$ [^ceil] to
point out the incorrect bit. Let's call the *error index*. To correct $$t$$ bits, 
use $$ t \cdot \lceil \log_2(k) \rceil$$.

[^ceil]: $$\lceil x \rceil$$ means: round up to nearest integer.

That's it! It's definitely simplistic, it can only be a first order estimation, but I felt
like it had to be pretty close to reality: a 1000-bit message requires ~10 bits of additional
bits to recover from a 1 bit error.

But does it really?

# Digging Deeper

Let's consider some of the aspects of such a model:

* it's not practical in the real world

  Or, at least, not as a forward error correction code where you don't know up front which bit 
  will be corrupted. But you could at least image a case like this:

  * Participant A transmits 1000 bits to participant B over a noisy channel
  * B transmits 1000 bits back to A over a perfect channel
  * A transmits 10 bit error index to signal to B which bit it received wrong

* it doesn't have a way to signal that there was no corruption

  That is solved by using $$log_2(k+1)$$ bits for the error index: it reserves
  one value to indicate perfect transmission. E.g. for a 1000-bit message, 0 to
  999 indicates an error bit, and 1000 signals perfect transmision.

  For messages that are not exactly a power of 2, it makes no difference.

* it doesn't take into account that the transmitted error index might be corrupt as well

  That can be solved by going through the same procedure to verify the error index. For
  a first iteration, it would cost an additional $$\lceil log_2(\lceil log_2(k+1) \rceil ) \rceil $$ bits, 4 for bits
  for a 10 bit error index. Note that this becomes recursive: how to you correct that
  4 bit number?

* it doesn't consider that the same error index can appear only once.

  If the code can correct 2 errors, you'd need $$ \lceil log_2(k+1) \rceil $$ for the first error index
  to indicate zero errors or the location of the first error. For the second error, you'd
  use $$\lceil log_2(k) \rceil $$ bits to indicate if there were remaining errors or its location etc.

* it does error correction the way BCH does it

  Any random bit can be corrected, but it doesn't work for Reed-Solomon coding because
  there a whole symbol can be incorrect. But that's fixable, I get to that later.

* you don't need to signal the correct value

  Since the symbol is 1 bit in size, the location of the error is sufficient. To fix it,
  the receiver just needs to invert the bit. This also doesn't work for Reed-Solomon.

# How Does It Match a BCH Code?

Forget about using the Wikipedia article to compare the intuition against theory: you won't
find anything explicit. I found 
[this presentation from the National Tapei University](https://web.ntpu.edu.tw/~yshan/BCH_code.pdf)
the most useful. The key formulas are in the first slide:

* Block length: $$ n = 2^m -1 $$
* Number of parity-check bits: $$ n - k \le m t $$
* Minimum distance: $$ d_{min} \ge 2t + 1 $$

In the equations above, $$k$$ is the length of the original message, $$t$$ is the number of bits 
that can be corrected, $$n$$ is the length of the code word. 

If we rearrange the $$n$$ equation, we get:

$$
  m = \log_2(n - 1)
$$

and thus:

$$
n - k \le \log_2(n - 1) t
$$

If we call $$e$$ the number of error bits, then $$e = n - k$$ and:

$$
e \le \log_2(n - 1) t
$$

Compare this with the intuitive formula that I started with:

$$
e \approx \lceil \log_2(k) \rceil t
$$

The only differences are:

* it uses $$k$$ instead of $$n$$. That accounts for the fact that error bits themselves
  need error correction too.
* it assumes that the total code word length is one less than a power of two.
* instead of an approximation, it defines an upper bound.

Theoretically, all BCH and Reed-Solomon code words have a length $$n = 2^m -1$$. In practice, 
the transmitted code words are often shortened by setting a bunch of the symbols in the input message
to zero and not transmitting them.[^systematic_code]

The intuitive formula works for long code words and a limited number of errors to correct: $$n \approx k$$.

[^systematic_code]: This assume that a systematic coding scheme is used, where the original message
                    appears unmodified in the code word. This is the case for most BCH and RS coding 
                    schemes.

# What about Reed-Solomon Codes?

You can still use the intuitive formula to identify the error symbol: in a message with, say, 223 bytes
you'd need 8 bits to pinpoint an incorrect byte. However, you then need an additional byte to correct
the corruption. This would be needed for every error byte that needs to be corrected. 

To repair $$t$$ symbols that are $$s$$ bits in side in a message of $$k$$ symbols, you'd need this
number of bits for the error location:

$$ e_{location} \approx t \lceil log_2(k) \rceil $$ 

And the bits with the correct values:

$$ e_{values} = t \cdot s $$

In reality, for Reed-Solomon codes, $$n = 2^s - 1$$, just like BCH. Change $$e_{location}$$ to
use $$n$$ instead of $$k$$ and you get:

$$ e_{location} \approx t \cdot s $$ 

The final result is:

$$ 
e = e_{location} + e_{values} \approx 2 t \cdot s
$$

It turns out, that is *exactly* what you'll find in all texts about Reed-Solomon coding: the number of
parity words is equal to 2 times the number of errors you want to correct!


# References



