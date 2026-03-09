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

  This polynomial expends to this:

  $$ g(x) = g_0 + g_1 x + g_2 x^2 + \dots + g_{n-k-1} x^{n-k-1} $$

* Let's define the following division:

  $$ \frac{ p(x) x^{n-k} }{ g(x) }  = q(x) g(x) + r(x) $$

  So $$r(x)$$ is the remainder of that division. It has $$(n-k)$$ coefficients 
  $$(r_0, r_1, ... , r_{n-k}) $$.

* Define the code word polynomial as follows:

  $$ c(x) = q(x) r(x) = p(x) x^{n-k} - r(x) $$

  We don't need to know and we don't care about the value of quotient polynomial
  $$q(x)$$ for the encoding, $$r(x)$$ is sufficient, but it's important to keep in mind 
  that $$c(x)$$ is the multiplication of *something* with $$g(x)$$.

  The subtraction is only needed for the theoretical case where the symbols are not from
  a $$\text{GF}(2^n)$$ Galois field. If the symbols are from a Galois field, then addition
  and subtractions are the same thing.

* The code word consists of the coefficients of $$s(x)$$:
  
  $$(c_0, c_1, \dots, c_n ) $$

  Of those symbols, $$(c_0, c_1, \dots, c_{k-1})$$ comes from $$r(x)$$ and
  $$(c_k, c_{k+1}, \dots, c_{n-k-1})$$ come from $$p(x)$$ and identical to
  message $$(m_0, m_1, \dots, m_{k-1})$$.


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
