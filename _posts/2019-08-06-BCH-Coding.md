---
layout: post
title: BCH Coding
date:   2019-08-06 10:00:00 -0700
categories:
---

* [Introduction](#introduction)

# Finite Field

In mathematics, a [field](https://en.wikipedia.org/wiki/Field_(mathematics)) is a set on which the operations of 
multiplication, addition, subtraction and division are defined and satisfy certain basic rules.

A [finite field](https://en.wikipedia.org/wiki/Finite_field) or Galois Field is a field where that set is finite number of elements. 

The most common example of a finite field are integers mod *p*, where *p* is a prime number.

The number of elements of a finite field is called the *order* or its *size*.

A finite field of order *q* exists if and only if the order *q* is a prime power *p*^*k*, where *p* is a prime and *k* is a positive integer.

# BCH Code

https://en.wikipedia.org/wiki/BCH_code


## Generator Polynomial

A polynomial code is a linear code where the set of valid code words are those polynomials that are divisiable by a
given fixed polynomial of short length. This short polynomial is the generator polynomial.

* Code length *n*: number of bits of the final code word, for example: 5
* generator polynomial of degree *m*, for example 2.
* Number of code words will be *q*^(*n*-*m*). For example: 5-2 = 3 -> 8 code words.
* The size of the original data has length *n*-*m*.

Construction:

* Take data word of *d(x)* (of length *n*-*m*)
* multiply by *x*^*m*. This shifts *d(x)* to the left by *m* digits.
* This will typicallly not be a valid code word, because it's not divisable by the generator.
* But we can adjust the *m* right most digits:
* Divide *x*^*m*x*d(x)* by *g(x)*


Thesis with good introduction about Galois Fields etc.
https://pdfs.semanticscholar.org/1246/a9ad98dc0421ccfc945e6529c886f23e848d.pdf

Galois Field multiplication implementation: LFSR. It's essentially doing the multiplication by doing
additions sequentially.




