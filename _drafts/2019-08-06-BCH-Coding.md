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


# Resources

* [Galois LFSR] (https://www.nayuki.io/page/galois-linear-feedback-shift-register)

    Shows the higher level meaning of an LFSR.


* [LFSR Berkeley Course](http://inst.eecs.berkeley.edu/~cs150/sp03/handouts/15/LectureA/lec27-6up)


The key understanding of an LFSR: 

* An LFSR is a polynomial multiplication on the GF(2) field.
* the GF(2) polynomials form a Galois (finite) field for operations that are a multiplication modulo a prime polynomial
* the modulo operation consists of subtracting an integer multiple of the prime polynomial
  * for GF(2), subtraction is the same as addition is XOR
  * so if the integer multiple is 1, then the module operation is just a XOR
* in addition, every field has a primitive element that can create all elements of the field just by taking the power of the
  primitive element
* for some prime polynomials, this primitive element is x^1.
* So... an LFSR first shifts left -> this is the multiplication by the prime element, 
  and then it XORs the result with the prime polynomial when the MSB is 1 -> this is the modulo operation
    When the MSB is 1, then the multiplication result (shift by 1) is higher than what fits in the polynomial, and thus
    you need to divide by the prime polynomial. So the XORs being a feed-through or an inversion depends on the MSB.




* [](https://www.embeddedrelated.com/showarticle/1065.php)
* [](https://www.embeddedrelated.com/showarticle/1070.php)
* [](https://www.embeddedrelated.com/showarticle/1086.php)

* [Practical Reed-Solomon for Programmers](https://berthub.eu/articles/posts/reed-solomon-for-programmers/)
