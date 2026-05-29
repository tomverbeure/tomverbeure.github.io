---
layout: post
title: Understanding Reed-Solomon Decoding
date:   2026-03-08 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>

* TOC
{:toc}

# Encoding

Reed-Solomon encoding is relatively straightfoward: the most common method is
described in my previous blog post, but I'll recap it here:

* Start with a message of $$k$$ symbols:

  $$(m_0, m_1, \dots , m_{k-1} ) $$

* Treat the message as a polynomial $$p(x)$$:

  $$ p(x) = m_0 + m_1 x + m_2 x^2 + \dots + m_{k-1} x^{k-1} $$

* Create a generator polynomial with $$(n-k)$$ roots $$(\alpha_0, \alpha_1, \dots, \alpha_{n-k-1})$$:

  $$ g(x) = (x - \alpha_0)(x - \alpha_1) \dots (x - \alpha_{n-k-1}) $$

  This polynomial expands to this:

  $$ g(x) = g_0 + g_1 x + g_2 x^2 + \dots + g_{n-k-1} x^{n-k-1} $$

* Define the following division:

  $$ \frac{ p(x) x^{n-k} }{ g(x) }  = q(x) g(x) + r(x) $$

  $$r(x)$$ is the remainder of that division. It has $$(n-k)$$ coefficients 
  $$(r_0, r_1, ... , r_{n-k}) $$.

* Define the code word polynomial as follows:

  $$ c(x) = q(x) r(x) = p(x) x^{n-k} - r(x) $$

  We don't need to know and we don't care about the value of quotient polynomial
  $$q(x)$$ for the encoding, $$r(x)$$ is sufficient, but it's important to keep in mind 
  that $$c(x)$$ is the multiplication of *something* with $$g(x)$$.

  The subtraction is only needed for the theoretical case where the symbols are not from
  a $$\text{GF}(2^n)$$ Galois field. If the symbols are from a Galois field, then addition
  and subtraction are the same operation and the equation becomes:

  $$ c(x) = q(x) r(x) = p(x) x^{n-k} + r(x) $$

* The code word consists of the coefficients of $$s(x)$$:
  
  $$(c_0, c_1, \dots, c_{n-1} ) $$

  Of those symbols, $$(c_0, c_1, \dots, c_{k-1})$$ comes from $$r(x)$$. Meanwhile,
  $$(c_k, c_{k+1}, \dots, c_{n-1})$$ comes from $$p(x)$$ and is identical to
  original message $$(m_0, m_1, \dots, m_{k-1})$$.

# Parameters Necessary for Reed-Solomon Coding

I don't know how to perform Reed-Solomon decoding with regular numbers[^regular_numbers], so let's switch
to Galois fields for everything that follows.

[^regular_numbers]: It is possible to do Reed-Solomon-like error decoding with regular numbers, 
                    but it's an esoteric topic that, again, I know nothing about, and it also
                    wouldn't be useful to the vast majority of people who read this.

In my previous blog post, I listed a bunch of parameters that must be agreed on between
transmitter and receiver to establish a protocol. I will revisit those parameters and
make them more concrete for the Galois field case.

* the alphabet of the symbols

  The alphabet consist of all the values that can be assigned to a symbol. When 
  a power-of-two Galois field $$GF(2^m)$$ is used, symbols map directly to binary
  words. Set $$m$$ to 8 and a byte can be used immediately as a symbol.

  Almost all real world Reed-Solmon codes are defined over a $$GF(2^m)$$ Galois
  field, but the [Reed-Solomon error correction example on Wikipedia](https://en.wikipedia.org/wiki/Reed–Solomon_error_correction#Example)
  is for a $$GF(929)$$ code, which is used in [PDF417 bar codes](https://en.wikipedia.org/wiki/PDF417).

* the primitive polynomial of the finite field 

  Every element $$s$$ of the alphabet can be written as a polynomial $$s(x)$$ with coefficients 
  $$(s_0, \dots, s_{m-1})$$. If you multiply $$s$$ by itself, $$s^i$$ and divide by polynomial $$g(x)$$
  then the remainder will be of the same order as $$s(x)$$ and thus an element of the alphabet.

  A primitive polynomial $$g(x)$$ is chosen such that $$s^i$$ covers all elements 
  of the alphabet, except 0. The primitve polynomial is said to define the finite field,
  because it determines what happens when you multiply 2 elements of the field with
  each other.

  Primitive polynomials need to have certain mathematical characteristics, but there are
  plenty of choices for $$GF(2^8)$$.

* the length $$k$$ of the message word

* the length $$n$$ of the code word

  A popular choice for $$n$$ and $$k$$ is 255 and 233, which results in a
  RS(255,223) code. It adds 32 symbols to the message and allows correcting up 
  to 16 symbol errors in the code word.

  The code word is almost always smaller than the size of the alphabet. For
  $$GF(2^8)$$, that means $$n < 256$$. 
  
  Here's why: from the earlier blog post, we know that 
  Reed-Solomon coding is all about evaluating a polynomial at more points 
  than there are number of symbols in the message word. 

  When using $$GF(2^8)$$, there are only 256 discrete points at which
  the message polynomial can be evaluated so that's the hard limit. The reason to
  use one less than this hard limit has to do with the fact that all points
  except 0 can be part of a multiplicative group, which leads to an implementation
  where the encoding can be done with a generator polynomial and a LSFR-style 
  shift-register.[^extended_rs]

  It's important to be aware of *shortened Reed-Solomon codes*. For example,
  [DVB-T](https://en.wikipedia.org/wiki/DVB-T) uses RS(204,188). In practice,
  this is RS(255,239) code, but 51 bytes of the message are always set to 0.

[^extended_rs]: It is possible to do Reed-Solomon coding where the code word matches
                the size of the alphabet. That's called *extended RS* coding, but 

* the generator polynomial of the code 

# Reed-Solomon Decoding Pipeline

So now the question is: how do we correct corrupted symbols of a received
message?

There are multiple algorithms for this, with different computational complexity,
but for hardware decoding, pretty much everybody has settled on the following
pipeline:

* Calculate syndromes $$S_0, ... S_{n-k}$$ of the received message.
* Create a syndrome polynomial
* Calculate an error locator polynomial
* Find the error locations through the error location polynomial
* Calculate the error magnitudes
* Correct the corrupt symbols

You'll find these steps and the algorithms to perform them in every textbook 
about coding theory. The only thing that this blog post adds personal
notes that helped me to better understand them.

# Calculating the Syndromes

$$c(x)$$ is the word that we expected to receive, but instead, we got $$r(x)$$.

$$ e(x) = c(x) - r(x) $$

$$e(x)$$ is the error polynomial: the difference between the coded message that
was transmitted and the one that was received.

During the decoding step, we saw that: 

$$ c(x) = q(x) g(x) $$

$$ g(x) = (x - \alpha_0)(x - \alpha_1) \dots (x - \alpha_{n-k-1}) $$

So if we received our message $$r(x)$$ without errors and $$e(x) = 0$$, then
we should also get zeros if we fill in the roots into $$r(x)$$:

$$ r(x) = c(x) + e(x) $$

$$ r(x) = q(x) g(x) + e(x) $$

$$ r(x) = q(x) (x - \alpha_0)(x - \alpha_1) \dots (x - \alpha_{n-k-1}) + e(x) $$

Let's fill in the first root of $$(\alpha_0, \alpha_1, \dots, \alpha_{n-k})$$ into polynomial $$r(x)$$:

$$ r(\alpha_0) = q(\alpha_0) \underbrace{(\alpha_0 - \alpha_0)}_{0} (\alpha_0 - \alpha_1) \dots (\alpha_0 - \alpha_{n-k-1}) + e(\alpha_0) $$

$$ r(\alpha_0) = e(\alpha_0) $$

We call $$r(\alpha_i)$$ syndrome $$S_i$$ of the received message:

$$
S_0 = r(\alpha_0) = e(\alpha_0)  \\
S_1 = r(\alpha_1) = e(\alpha_1)  \\
\dots \\
S_{n-k} = r(\alpha_{n-k}) = e(\alpha_{n-k})  \\
$$

If all syndromes are equal to 0, and if we assume that there are no more than $$(n-k)$$ corrupted symbols
in the received code word[^more_errors], then we know for sure that the code word has been received without errors.

[^more_errors]: If more than $$(n-k)$$ symbols are corrupted, then the chance that all syndromes are zero
                is extremely low but not zero: if the error polynomial $$e(x)$$ happens to be a multiple of $$g(x)$$
                then $$r(x) = q(x)g(x) + t(x)g(x)$$ will evaluate to zero for all roots $$\alpha_i$$ of $$g(x)$$, 
                where the order of $$t(x)$$ is less than $$k$$.


# References

# Footnotes
