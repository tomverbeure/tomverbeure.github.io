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
gotten very far, I keep on reading and, occasionally, 
[writing about it](/2022/08/07/Reed-Solomon.html).
Except for really simple schemes, ECC theory gets complicated quickly.

The two codes that I've looked the most are 
[Reed-Solomon](https://en.wikipedia.org/wiki/Reed–Solomon_error_correction) 
and [BCH](https://en.wikipedia.org/wiki/BCH_code) 
codes. They are closely related: both add redundant symbols that are calculated
by evaluating a polynomial that's normally evaluated using 
[Galois Field math](/2026/06/14/Galois-Field-Arithmetic-Primer.html), though, as shown
in my earlier Reed-Solomon blog post, that's not strictly required. The encoding algorithm
is relatively straightforward, the decoding algorithms are significantly more complicated
but similar.

Reed-Solomon and BCH codes differ in the size of their symbols, their alphabet: a symbol
of the former consists of multiple bits, while the symbol of the latter is a bit. Error are
correct with a granularity of a symbol.

# Hamming Distance

When you look at the theory of error detecting and correcting codes, the discussion
immediately turns to Hamming distance: the number of bit flips required to convert one
vector of bits to another. The goal of an error correcting code is to transform the input
vector, the message, to an output vector, the code word, so that the Hamming minimum distance
between code words is guaranteed to be at least a certain number. The higher the Hamming 
distance, the higher number of bits that can be flipped in a code word without destroying 
the ability to recover the original message.

# Intuitive Estimation of Error Correction Bits

Hamming distance is not particulary complicated, but in practice I found myself using an
an even simpler mental model:

If a message of $$k$$ bits has 1 incorrect bit, you need a number of $$ r = \lceil log_2(k) \rceil$$ [^ceil] 
bits to point out the incorrect bit. Let's call that number the *error index*. To correct $$t$$ bits, 
use $$ r = t \cdot \lceil \log_2(k) \rceil$$ additional bits.

[^ceil]: $$\lceil x \rceil$$ means: round up to nearest integer.

![Error indicators](/assets/err_correction/error_correction-error_indicators.svg)

That's it! It's definitely simple, it can only be a first order estimation, but I felt
like it had to be pretty close to reality: a 1000-bit message requires 10 bits of additional
bits to recover from a 1 bit error.

But does it really?

# Digging Deeper

Let's consider some of the aspects of such a model:

**It's not practical in the real world**

Or, at least, not as a forward error correction code where you don't know up front which bit 
will be corrupted. But you could at least imaging a protocol like this:

* Participant A transmits 1000 bits to participant B over a noisy channel
* B transmits 1000 bits back to A over a perfect channel
* A transmits 10 bit error index to signal to B which bit it received wrong

![three-phase protocol](/assets/err_correction/error_correction-three_phase_protocol.svg)

**There is no way to signal that there was no corruption**

That can be solved by allocating one error index value extra to signal a perfect
transmission and calculate the number of bits as $$r =  \lceil log_2(k+1) \rceil$$ instead of 
$$r =  \lceil log_2(k) \rceil$$.

E.g. for a 1000-bit message, 0 to 999 indicates an error bit, and 1000 signals perfect 
transmision.

For messages that are not exactly a power of 2, the number of error indicator bits
remains the same.

**The transmitted error indicator bits can be corrupt as well**

One way to solve this is by going through the same procedure to verify the error index. 

For a first iteration, it would cost an additional 
$$\lceil log_2(\lceil log_2(k+1) \rceil ) \rceil $$ bits, 4 for bits for a 10 bit error index. 
Of course, those 4 bits might be corrupt too! 

A better approach is to work backwards: start out with the length of the code word and the 
number of errors you want to solve and determine the number of input message bits from there. 
In this case, you get $$r = \lceil log_2(n) \rceil$$.

**It doesn't consider that the same error index can appear only once**

If the code can correct 2 errors, you'd need $$ \lceil log_2(k+1) \rceil $$ bits for the first 
error index to indicate zero errors or the location of the first error. For the second error, you
need one less value because one location has already been corrected, so the number of
bits needed is $$\lceil log_2(k) \rceil $$.

**It does error correction the way BCH does it**

Any random bit can be corrected, but it doesn't work for Reed-Solomon coding because
there a whole symbol can be incorrect. That's fixable though, I get to that later.
 
**You don't need to signal the correct value**

Since the symbol is 1 bit in size, the location of the error is sufficient. To fix it,
the receiver just needs to invert the bit. This also doesn't work for Reed-Solomon.

# Comparing against BCH Codes

Forget about using the Wikipedia article to compare the intuition against theory: you won't
find anything explicit. I found 
[this presentation from the National Tapei University](https://web.ntpu.edu.tw/~yshan/BCH_code.pdf)
useful. The key formulas are on the first slide:

* Block length: $$ n = 2^m -1 $$
* Number of parity-check bits: $$ n - k \le m t $$
* Minimum distance: $$ d_{min} \ge 2t + 1 $$

In the equations above, $$k$$ is the length of the original message, $$t$$ is the number of bits 
that can be corrected, $$n$$ is the length of the code word. 

If we rearrange the $$n$$ equation, we get:

$$
  m = \log_2(n + 1)
$$

and thus:

$$
n - k \le \log_2(n + 1) t
$$

If we call $$r$$ the number of error correction bits, then $$r = n - k$$ and:

$$
r \le \log_2(n + 1) t
$$

Compare this with the intuitive formula that I started with:

$$
r \approx \lceil \log_2(k) \rceil t
$$

The only differences are:

* I used $$k$$ instead of $$n+1$$. That accounts for the fact that error bits themselves
  need error correction too and that a perfect transmission must be signaled.
* it assumes that the total code word length is always one less than a power of two.
* instead of an approximation, it defines an upper bound.

Theoretically, all BCH and Reed-Solomon code words have a length $$n = 2^m -1$$ bits. In practice, 
the transmitted code words are often shortened by setting a bunch of the symbols in the input message
to zero and not transmitting them.[^systematic_code]

The intuitive formula works for long code words and a limited number of errors to correct: $$n \approx k$$.

[^systematic_code]: This assume that a systematic coding scheme is used, where the original message
                    appears unmodified in the code word. This is the case for most BCH and RS coding 
                    schemes.

# What about Reed-Solomon Codes?

Reed-Solomon codes correct symbols not bits. You can still use the intuitive formula to identify the 
corrupted symbol: in a message with, say, 223 bytes you'd need 8 bits to pinpoint an incorrect byte. 
However, you also need an additional byte to fix the corruption. This would be needed for every error 
byte that needs to be corrected. 

To repair $$t$$ symbols that are $$s$$ bits in size in a message of $$k$$ symbols, you'd need this
number of bits for the error location:

$$ e_{location} \approx t \lceil log_2(k) \rceil $$ 

And a bunch of bits with the correct values:

$$ e_{values} = t \cdot s $$

Just like BCD codes, $$n = 2^s - 1$$ for Reed-Solomon codes. Change $$e_{location}$$ to
use $$n$$ instead of $$k$$ and you get:

$$ e_{location} \approx t \cdot \lceil log_2(2^s -1) \rceil $$ 

$$ e_{location} \approx t \cdot s $$ 

The final result is:

$$ 
e = e_{location} + e_{values} \approx 2 t \cdot s
$$

It turns out, that is *exactly* what you'll find in all texts about Reed-Solomon coding: the number of
parity words is equal to 2 times the number of errors you want to correct!

# BCH vs Reed-Solomon Codes

Reed-Solomon codes are much more popular than BCD codes. It's interesting to see why this is the case.

Let's create an example where code words are 255 bytes or 2040 bits and where we reserve 32 bytes or 
256 bits for error correction.

For Reed-Solomon, this allows us to correct 16 corrupt bytes or up to 128 corrupt bits. For BCH, we
can need 11 bits per error, so the 256 error bits can fix 23 corrupt bits.

Reed-Solomon is the winner if error happen in bursts: it doesn't matter if a burst is 1 or 8 bits long, it
can still count as a single corruption. When errors are spread randomly, then BCH wins: instead of fixing
16 bit flips, it can fix 23.

In practice, communication protocols have always used 2 codes: 

Reed-Solomon -> Convolutional -> Transmission -> Viterby -> Reed-Solomon

A convolutional code has a number of benefits over BCH but it can introduce burst errors which the
Reed-Solomon code can cleanup.


# References



