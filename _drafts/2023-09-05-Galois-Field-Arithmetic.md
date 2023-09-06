---
layout: post
title: Galois Field Arithmetic
date:  2023-09-05 00:00:00 -1000
categories:
---

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

* TOC
{:toc}

# Introduction

In [my blog post about Reed-Solomon coding](/2022/08/07/Reed-Solomon.html), 
I used regular integers for all calculations.  These are unpractical for a real-world 
implementation, but since everybody knows integers math since first grade, it made things 
easier to learn things one step at a time.

Instead of working with pure integers, actual Reed-Solomon implementations will
use elements from a [Galois or Finite field](https://en.wikipedia.org/wiki/Finite_field) 
as symbols.

In this blog post, I will first talk a bit about Galois fields. I will rely heavily on 
examples instead of 

Not nearly enough to
have a solid theoretical understanding, just sufficiently so that I can refer back to
it when I've forgotten some of the details. You can find much better material online if 
you want to get a better understanding. Check out in the [References](#references) section
below from a bunch of links.

Once these basics are out of the way, I'll dive into some details related to hardware
implementation of Galois field multipliers.

# Galois Field

In mathematic, a field is a set of elements for which addition, subtraction, multiplication
and division operations have been defined, with propertes that are the same the ones
that we take for granted when dealing with rational or real numbers, such as the associative
and distributive properties.

A Galois field is a field that has a limited number of elements, but that still has
these kind of operations and properties.

A good example of a Galois field is GF(5). It has the integer numbers 0 to 4 as elements.
Addition, subtraction, and multiplicaiton work the same as for regular integers, except that each such operation 
is followed by a modulo 5 operation. Division is defined as a multiplication by the inverse:

$$ \frac{a}{b} = a \cdot b^{-1} $$

Here are a few example operations in GF(5):

$$
\begin{align}
1 + 3 = (1+3) \bmod 5 = 4 \bmod 5 = 4     \\
2 + 7 = (2+6) \bmod 5 = 8 \bmod 5 = 3     \\
3 \cdot 4 = (3 \cdot 4) \bmod 5 = 36 \bmod 5 = 1     \\
\end{align}
$$

**Division**

Division is a bit less intuitive: we need the multiplicative inverse of the divisor, which can be
found by checking all possible element. Let's say we want to do 2/3 in GF(5). 3 is the divisor. 
We need to find $$3^{-1}$$ so that $$3 \cdot 3^{-1} = 1$$. 

There are 5 different options 0,1,2,3,4.

$$
\begin{align}
(3 \cdot 0) \bmod 5 = 0 \\
(3 \cdot 1) \bmod 5 = 3 \\
(3 \cdot 2) \bmod 5 = 1 \\
(3 \cdot 3) \bmod 5 = 4 \\
(3 \cdot 4) \bmod 5 = 2 \\
\end{align}
$$

We can see that $$(3 \cdot 2)\bmod 5 = 1$$, so $$3^{-1}=2$$. 

And thus:

$$2/3 = (2 \cdot 2) \bmod 5 = 4$$

**A Prime Number of Elements**

One thing to note is that the number of elements in a Galois field must always be a
a prime number. This is because the division operation would otherwise be ill defined.

For example, let's try to find the multiplicative inverse of 2 when doing a modulo 6 operation:

$$
\begin{align}
(2 \cdot 0) \bmod 6 = 0 \\
(2 \cdot 1) \bmod 6 = 2 \\
(2 \cdot 2) \bmod 6 = 4 \\
(2 \cdot 3) \bmod 6 = 0 \\
(2 \cdot 4) \bmod 6 = 2 \\
(2 \cdot 5) \bmod 6 = 4 \\
\end{align}
$$

There's no solution with a result of 1. Since there's at least one element for which a
multiplicative inverse doesn't exist, GF(6) can't be a field.

**Real World Example of a Galois Field**

Since a Galois field must have a prime number of elements, only GF(2) can map directly
to the zeros and ones of digital logic. All other fields will have an odd number of elements.
But that doesn't mean that there aren't any real-world cases where these kind of Galois
fields are used: the [Wikipedia article on Reed-Solomon error correction](https://en.wikipedia.org/wiki/Reed–Solomon_error_correction#Error_locator_polynomial)
has an example that uses GF(929), a field that is used for coding [PD417](https://en.wikipedia.org/wiki/PDF417)
bar codes.

![PD417 bar code](/assets/reed_solomon/Wikipedia_PDF417.png)<br/>
*&copy; [Markus.Jungbauer - Wikipedia](https://en.wikipedia.org/wiki/PDF417#/media/File:Wikipedia_PDF417.png)*



# Galois Field Extension

Once you have a Galois field, you can create a Galois field extension that consists of multiple elements
of the Galois base field.

For example, the base field GF(5) can be extended to GF(5^3) which consists of 3 GF(3) elements.


# References

* [Wikipedia - Finite field](https://en.wikipedia.org/wiki/Finite_field)


* [Python galois package](https://galois.readthedocs.io/)


