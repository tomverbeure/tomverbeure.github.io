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


In my blog post about Reed-Solomon coding, I used regular integers for all calculations.
These are unpractical for real-world implementations, but since everybody knows integers
since first grade, it made things easier to learn things one step at a time.

Instead of working with pure integers, practical Reed-Solomon implementations will
use Galois field elements as symbols.

# Galois Base Field

A Galois field has a limited number of elements, but still supports addition, subtraction,
multiplications and division operations. When two Galois field elements are subjected
to these operations, the result will still be a Galois field elements.

A good example of a Galois field is GF(5). As elements, it has the integer numbers 0 to 4.
Addition, subtraction, and multiplicaiton work the same as for regular integers, 
except that each such operation is followed by a modulo 5 operation. Division in a Galois field
is defined as a multiplication of the inverse: a / b = a * (b^-1).

Here are a few example operations in GF(5):

1 + 3 = (1+3) mod 5 = 4 mod 5 = 4
2 + 7 = (2+6) mod 5 = 8 mod 5 = 3
3 * 4 = (3 * 12) mod 5 = 36 mod 5 = 1

For division, let's say we want to do 2/3 in GF(5). We first need to find the multiplicative
inverse of 3 so that 3 x 3^-1 = 1. There are 5 different options 0,1,2,3,4.

(3 * 1) mod 5 = 3
(3 * 2) mod 5 = 1       <----
(3 * 3) mod 5 = 4
(3 * 4) mod 5 = 2

We can see that 3^-1 = 2.

So:

2/3 = (2 * 2) mod 5 = 4

The [Wikipedia article on Reed-Solomon error correction](https://en.wikipedia.org/wiki/Reed–Solomon_error_correction#Error_locator_polynomial),
has an example that uses GF(929), a field that is used for coding [PD417](https://en.wikipedia.org/wiki/PDF417)
bar codes.

One thing to note is that the number of elements in a Galois field must always be a
a prime number. In the examples above of GF(5) and GF(929), 5 and 929, and the power
factor is 1.

The reason why it must be a prime power is because the division operation would otherwise be ill defined.

For example, let's try to find a multiplicative inverse of 2 when doing a modulo 8 operation:

(2 * 1) mod 8 = 2
(2 * 2) mod 8 = 4
(2 * 3) mod 8 = 6
(2 * 4) mod 8 = 0
(2 * 5) mod 8 = 2
(2 * 6) mod 8 = 4
(2 * 7) mod 8 = 6

There's no solution with a result of 1. Since there's at least one element for which a
multiplicative inverse doesn't exist, there can't be a GF(8) field).

# Galois Field Extension

Once you have a Galois field, you can create a Galois field extension that consists of multiple elements
of the Galois base field.

For example, the base field GF(5) can be extended to GF(5^3) which consists of 3 GF(3) elements.




