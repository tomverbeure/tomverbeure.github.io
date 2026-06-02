---
layout: post
title: A Galois Field Arithmetic Primer
date:  2026-05-30 00:00:00 -1000
categories:
---

<script async src="https://cdn.jsdelivr.net/npm/mathjax@2/MathJax.js?config=TeX-AMS_CHTML"></script>

* TOC
{:toc}

# Introduction

In [my blog post about Reed-Solomon coding](/2022/08/07/Reed-Solomon.html),
I used regular integers for all calculations.  These are unpractical for a real-world 
implementation, but since everybody knows integer math since first grade, it made things 
easier to learn things one step at a time.

Instead of working with pure integers, actual Reed-Solomon implementations 
uses elements from a [Galois or finite field](https://en.wikipedia.org/wiki/Finite_field) 
as symbols. 

I've been sitting on writing about Reed-Solomon decoding for almost 4 years now[^galois_kickoff], and I'm 
still not quite there, but a first step is to have enough Galois field understanding
so that the lack of it isn't an obstacle. That's what this blog is about. Don't expect a solid
theoretical treatise, you can find many of those as part of univerity courses, but something
that is sufficient to refer back to in the future when I've forgotten some of the details. 

[^galois_kickoff]: According to my git log, the first words of this blog posts were written
                   in september 2023.

If you want to get a deeper understanding, Check out the [references](#references) at the bottom. 

# A Galois Field Introduction by Example

In mathematics, a field is a set of elements for which addition, subtraction, multiplication
and division operations have been defined, with properties that we take for granted when dealing 
with rational or real numbers, such as the associative and distributive properties[^assoc_dist_prop]. 

[^assoc_dist_prop]: The [associative property](https://en.wikipedia.org/wiki/Associative_property) 
                    states that a * (b * c) = (a * b) * c. 
                    The [distributive property](https://en.wikipedia.org/wiki/Distributive_property) 
                    states that a * (b + c) = (a * b) + (a * c).

For rational or real numbers, the number of elements in the field is infinite. A Galois field 
only has a limited number of elements, yet still has these kind of operations and properties.

A good example of a Galois field is $$\text{GF}(5)$$ which integer numbers 0 to 4 as elements.
Addition, subtraction, and multiplication work the same as for regular integers but each 
such operation is followed by a modulo 5 operation. 

Here are a few example operations in $$\text{GF}(5)$$:

$$
\begin{align}
1 + 3 = (1+3) \bmod 5 = 4 \bmod 5 = 4     \\
2 + 7 = (2+6) \bmod 5 = 8 \bmod 5 = 3     \\
3 \cdot 4 = (3 \cdot 4) \bmod 5 = 12 \bmod 5 = 2     \\
\end{align}
$$

Division is a bit less intuitive. It is defined as the multiplication by the inverse of the
divisor:

$$ \frac{a}{b} = a \cdot b^{-1} $$

One way of finding the multiplicative inverse of the divisor is by multiplying it with all possible 
elements and checking if the result is 1. 

Let's say we want to do $$2/3$$ in $$\text{GF}(5)$$. We need to find $$3^{-1}$$ so that $$3 
\cdot 3^{-1} = 1$$. There are 5 different options 0,1,2,3,4:

$$
\begin{align}
(3 \cdot 0) \bmod 5 = 0 \\
(3 \cdot 1) \bmod 5 = 3 \\
\boldsymbol{(3 \cdot 2) \bmod 5 = 1} \\
(3 \cdot 3) \bmod 5 = 4 \\
(3 \cdot 4) \bmod 5 = 2 \\
\end{align}
$$

We can see that $$(3 \cdot 2)\bmod 5 = 1$$, so $$3^{-1}=2$$. 

And thus:

$$2/3 = 2 \cdot 3^{-1} = (2 \cdot 2) \bmod 5 = 4$$

There are other ways to calculate the multiplicative inverse. For simple cases, you can use
[Fermat's Little Theorem](https://en.wikipedia.org/wiki/Fermat%27s_little_theorem),
which says:

$$a^{p-1} \equiv 1 \pmod{p}$$

or, after dividing both sides by $$a$$:

$$a^{p-2} \equiv a^{-1} \pmod{p}$$

In our example $$a=3$$ and $$p=5$$, so:

$$ 3^{-1} = 3^{5-2} = 3^3 = 27 $$

$$ 27 \pmod{5} = 2 $$

A more general algorithm is the 
[Extended Euclidean Algorithm](https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm).

# Base Galois Fields

The example above is one of a base Galois field

$$\text{GF}(p)$$

$$p$$ is the base number of a one-dimensional mathematical universe. In a base
Galois field, $$p$$ must always be a prime number, otherwise the division operation 
would be ill defined. 

For example, if we'd set $$p=6$$ and tried to find the multiplicative inverse of 2,
we'd get the following:

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
multiplicative inverse doesn't exist, you can create a field for $$p=1$$ and thus
$$\text{GF}(6)$$ can't exist.

Another issue for $$p=6$$ is that you can get a result of 0 when multiplying 2 non-zero
numbers:

$$ 2 \cdot 3 = 6 \equiv 0 \pmod{6} $$

That's behavior unbecoming of a proper field!


**Real world example of a base Galois field**

Since a Galois field must have a prime number of elements, only $$\text{GF}(2)$$ maps directly
to the zeros and ones of digital logic; all other fields have an odd number of elements. 
Still, there are some real-world cases where these kind of Galois fields are used:
the [Wikipedia article on Reed-Solomon error correction](https://en.wikipedia.org/wiki/Reed–Solomon_error_correction#Error_locator_polynomial)
has an example that uses GF(929), a field that is used for coding [PD417](https://en.wikipedia.org/wiki/PDF417)
bar codes.

![PD417 bar code](/assets/reed_solomon/Wikipedia_PDF417.png)<br/>
*&copy; [Markus.Jungbauer - Wikipedia](https://en.wikipedia.org/wiki/PDF417#/media/File:Wikipedia_PDF417.png)*

Modulo 929 calculations are fine for bar codes, where you only need to process a few per 
second at most. But they're not something you'd want to use for high speed communication
protocols that run at rates of gigabits or bytes per second. 

**GF(2)**

Before taking the next step, let's first look at the only basic operation that maps
neatly to ones and zeros: GF(2). The binary Galois field only has 2 symbols: 0 and 1.

It has the following addition table:

$$
\begin{align}
(0 + 0) \bmod 2 = 0 \\
(0 + 1) \bmod 2 = 1 \\
(1 + 0) \bmod 2 = 1 \\
(1 + 1) \bmod 2 = 0 \\
\end{align}
$$

And this is the multiplication table:

$$
\begin{align}
(0 \cdot 0) \bmod 2 = 0 \\
(0 \cdot 1) \bmod 2 = 0 \\
(1 \cdot 0) \bmod 2 = 0 \\
(1 \cdot 1) \bmod 2 = 1 \\
\end{align}
$$

Addition maps to a XOR and multiplication to an AND gate! Another property of note is that
subtraction is the same as addition. 

These are promising properties for a hardware implementation.

# Extended Galois Fields 

From a base Galois field $$\text{GF}(p)$$ can construct an extended Galois field

$$\text{GF}(p^n)$$

$$p$$ is still the size of mathematical universe in one dimension and prime. 
$$n$$ is the number of dimensions. The total number of elements in the extended
Galois field is simply $$p^n$$. An element $$a$$ of such a Galois field could be
written as a vector:

$$( a_{n-1}, \cdots, a_1, a_0 ) $$

Or as a polynomial:

$$ a_{n-1} x^{n-1} + \cdots + a_1 x + a_0 $$

For algorithms that are implemented in hardware, it's extremely common to deal with
$$\text{GF}(2^n)$$, and $$\text{GF}(2^8)$$ especially: this results in 8 dimensions 
of values 0 and 1 which conveniently maps to a byte.

*You'll sometimes see an extended Galois field written with argument in parenthesis 
worked out, e.g. $$\text{GF}(2^8)$$ written a $$\text{GF}(256)$$. This is not an ambiguous
notation: you can infer this to be a Galois field extension because 256 is not a prime,
but my personal preference is to always use the $$\text{GF}(2^8)$$ notation.*

All Galois fields require an addition, subtraction, multiplication, and division operation. For Galois
field extensions, we turn the polynomial notation and polynomial operations to make
this happen.

**Extended Galois field addition**

To add 2 elements $$a$$ and $$b$$:

$$
\begin{align}
(a_3 x^3 + a_2 x^2 + a_1 x + a_0) + (b_3 x^3 + b_2 x^2 + b_1 x + b_0) \\
= (a_3+b_3) x^3 + (a_2 + b_2) x^2 + (a_1 + b_1) x + (a_0 + b_0)
\end{align}
$$

The base Galois field rules apply for the addition of each of the terms.

Here's a $$\text{GF}(2^4)$$ example:

$$ (1,0,0,1) + (0,0,1,1) = $$

$$ ( 1 x^3 + 0 x^2 + 0 x + 1 ) +  ( 0 x^3 + 0 x^2 + 1 x + 1 )  = $$

$$ (1+0) x^3 + (0+0) x^2 + (0+1) x + (1+1) = $$

$$ 1 x^3 + 0 x^2 + 1 x + 0 = $$

$$ (1,0,1,0) $$

Note how for the last term $$(1+1) = 0$$. That's the base $$\text{GF}(2)$$
operation.

For polynomial addition, the order of the result remains the same: addition of
2 elements of an extended Galois field automatically belong to the same extended Galois field.

**Extended Galois field multiplication**

Like base Galois field multiplication, the extended version uses a multiplication followed
by division and retaining the remainder. Like addition, this is done with polynomials.

$$ m(x) = a(x) \cdot b(x) \pmod{p(x)} $$

The modulo operation is necessary to ensure that the result of the multiplication is
a polynomial with the same maximum order. To make that happen, the order of polynomial
$$p(x)$$ must be one higher than the polynomials that are used to represent the
field elements.

For example, for $$GF(2^4)$$, the elements have 4 dimensions and are represented
with polynomials with an order of 3: $$a_3 x^3 + a_2 x^2 + a_1 x + a_0$$. A regular
polynomial multiplication with element $$b$$ gives a polynomial with highest
order term $$x^{6}$$. The modulo operation with a polynomial with maximum
term $$x^4$$ will reduce the result back to one with maximum term $$x^3$$.

**Defining irreducible polynomial**

The following requirement are key for a field defining polynomial for $$\text{GF}(p^n)$$:

* the polynomial is of order $$n$$: $$p(x) = x^n + p_{n-1} x^{n-1} + \cdots + p x^1 + p_0 $$ with $$p_n \neq 0 $$.
* the coeffient of $$x^n$$ is always 1. The polynomial is 
  [monic](https://en.wikipedia.org/wiki/Monic_polynomial).
* the remaining coefficients are from the base field $$\text{GF}(p)$$
* the polynomial is irreducible in the field of $$\text{GF}(p)$$.

    An irreducible polynomial can not be factored into multiple lower order polynomials.

*Note the similarity with base Galois field $$\text{GF}(p)$$, where $$p$$ must be
a prime number, one that can not be factored into multiple smaller integers.*

Pay attention to the part where I write that it needs to be irreducible *in the field of $$\text{GF}(p)$$*.
What this means it that we only test this polynomial for irreducibility with
values from $$\text{GF}(p)$$, not $$\text{GF}(p^n)$$.

One thing to test when checking for irreducibility is to verify that none of the 
base Galois field elements are a root of $$p(x)$$. In the case of working with
$$\text{GF}(2^4)$$, this means checking that $$p(0) = 0 $$ and $$p(1) = 0 $$ though
those 2 checks are not sufficient to ensure irreduciblity.

Much like the earlier example where $$2 \cdot 3 \pmod{6} = 0$$, a reducible 
polynomial makes it impossible to properly define extended Galois field operations.

For example, for $$\text{GF}(2^4)$$, if we select $$p(x) = x^4 + 1 $$ as defining
polynomial and multiply 2 elements:

$$
\begin{gather}
( x^3 + x^2 + x + 1) (x + 1) \pmod{x^4 + 1} = \\
(1 \cdot 1) x^4 + (1 \cdot 1 + 1 \cdot 1) x^3 + (1 \cdot 1 + 1 \cdot 1) x^2 + (1 \cdot 1 + 1 \cdot 1) x + (1 \cdot 1) \pmod{x^4 + 1} = \\
x^4 + (1 + 1) x^3 + (1 + 1) x^2 + (1 + 1) x + 1 \pmod{x^4 + 1} = \\
x^4 + 1 \pmod{x^4 + 1} = \\
0
\end{gather}
$$

In other words, we have again a case where multiplying non-zero elements results in zero,
which is not allowed for a field.

The defining irreducible polynomial determines how Galois field multiplication behaves, 
so standardized protocols must specify which defining polynomial to use. However,
when reading about Galois fields in the context of coding, you'll rarely see this term
because most of these applications will use something stronger than
an irreducible polynomial: a primitive polynomial.

**Primitive polynomial**

A primitive polynomial is an irreducible polynomial $$p(x)$$ with one additional characteristic:
it defines a field where the powers of a root element $$\alpha$$ generate all non-zero elements 
of the field.

What does this mean? And what is $$\alpha$$ anyway?

$$\alpha$$ is defined as an element of $$\text{GF}(p^n)$$ that satisfies
the following equation:

$$ p(\alpha) = 0 $$

In other words, $$\alpha$$ is a root of $$p(x)$$.

It is crucial to understand that the equation above is the formal definition of 
$$\alpha$$. There are multiple values from $$\text{GF}(p^n)$$ that can serve as 
$$\alpha$$, but right now, we don't care about that: $$\alpha$$ is a placeholder, 
an abstract element. You compare it complex value $$i$$ being formally defined
as a solution of $$ x^2 + 1 = 0 $$ in the complex field: the equation is the
definition.

If $$p(x)$$ is irreducible, how can $$\alpha$$ be a root of it? That's because
the irreducibility criterion only applies for elements of $$\text{GF}(p)$$, 
not for elements of $$\text{GF}(p^n)$$! This is just the way $$x^2 +1$$ is
irreducible over the real numbers, but once you introduce $$i$$, it can
be factored as $$(x+i)(x-i)$$.

$$p(x)$$ is a monic polynomial of order $$n$$:

$$p(x) = x^n + p_{n-1} x^{n-1} + \cdots + p_1 x^1 + p_0 $$

Using the definition of $$\alpha$$:

$$p(\alpha) = \alpha^n + p_{n-1} \alpha^{n-1} + \cdots + p_1 \alpha^1 + p_0 = 0 $$

Simple rearrangment gives this:

$$ \alpha^n = - ( p_{n-1} \alpha^{n-1} + \cdots + p_1 \alpha^1 + p_0 ) $$

In the case of $$\text{GF}(2^n)$$, subtraction is the same as addition, so you get this:

$$ \alpha^n = p_{n-1} \alpha^{n-1} + \cdots + p_1 \alpha^1 + p_0  $$

Either way, we have derived a reduction rule that tells us how to deal with $$\alpha^i$$
where $$i \ge n$$.


If you want to use your own
coding protocol, you could try to find a primitive polynomial yourself, but it's much easier 
to just select one from one of tables that can be found online, such as 
[this one](https://www.partow.net/programming/polynomials/index.html).

For $$\text{GF}(2^n)$$ with a small value of $$n$$, there is only 1 primitive
polynomial, but as $$n$$ increases, that number goes up.

For example, $$\text{GF}(2^2)$$ has only this:

$$ p(x) = x^4 + x^1 + 1 $$

But $$\text{GF}(2^8)$$ has these:

$$
\begin{gather}
x^8 + x^4 + x^3 + x^2 + 1 \\
x^8 + x^5 + x^3 + x^1 + 1 \\
x^8 + x^6 + x^4 + x^3 + x^2 + x^1 + 1 \\
x^8 + x^6 + x^5 + x^1 + 1 \\
x^8 + x^6 + x^5 + x^2 + 1 \\
x^8 + x^6 + x^5 + x^3 + 1 \\
x^8 + x^7 + x^6 + x^1 + 1
x^8 + x^7 + x^6 + x^5 + x^2 + x^1 + 1 \\
\end{gather}
$$


Computers work with bytes. Many protocols use the $$\text{GF}(2^8)$$ field,
so that a byte can be directly mapped to a tuple of size 8. One of the most used
primitive polynomials for $$\text{GF}(2^8)$$ is

$$p(x) = x^8 + x^4 + x^3 + x^2 + 1$$

It is so popular that modern CPU ISA have instructions to perform Galois field operations 
specifically for this primitive polynomial. The Rijndael algorithm, the basis for AES encryption,
uses this polynomial. It is also used for Reed-Solomon coding in the CCSDS standard for space 
communication. And many others.

**Extended Galois Field Elements**

We now know that elements of an extended Galois field are tuples, and now to perform
operations on them, but some details of what those elements looks like. 

Let's use $$\text{GF}(2^4)$$ as an example, with $$p(x)=x^4+x+1$$ as primitive polynomial.
The field contains 16 elements. We need a zero, a one, and 14 additional elements that
we name $$\alpha^1$$ to $$\alpha^{14}$$. Here's the total set of field elements:

$$(0, 1, \alpha^1, \alpha^2, \alpha^3, \ldots, \alpha^{14})$$

We're using an exponent to number each $$\alpha$$ because that's how we're going to
construct their tuple values.

For the 0 and 1 field elements, we choose tuples $$(0,0,0,0)$$ and $$(0,0,0,1)$$.
$$\alpha^1$$ is called the primitive element. From the remaining 14 tuples, there are
multiple options that can serve a primitive element, but let's choose tuple $$(0,0,1,0)$$.
From here we can derive the tuple values for the remaining elements by using 
polynomial multiplication.


$$
\begin{align}
\alpha^1 = (0,0,1,0) = x \\
\alpha^2 = \alpha^1\alpha^1 = x\cdot x = x^2 =  (0,1,0,0) \\
\alpha^3 = \alpha^2\alpha^1 = x^2\cdot x = x^3 =  (1,0,0,0) \\
\end{align}
$$

So far so good. But now it gets interesting:

$$\alpha^4 = \alpha^3\alpha^1 = x^3\cdot x = x^4 = ???$$

$$x^4$$ is a polynomial with an order that it higher than what's allowed a $$\text{GF}(2^4)$$
field. We need to use the primitive polynomial to get the result back in check:

$$x^4 \bmod p(x) = x^4 \bmod (x^4+x+1) = x+1 $$

$$
\begin{align}
\alpha^4 = \alpha^3\alpha^1 = x^3\cdot x = x+1 =  (0,0,1,1) \\
\alpha^5 = \alpha^4\alpha^1 = (x+1)x = x^2+x =  (0,1,1,0) \\
\alpha^6 = \alpha^5\alpha^1 = (x^2+x)x = x^3+x^2 =  (1,1,0,0) \\
\alpha^7 = \alpha^6\alpha^1 = (x^3+x^2)x = x^4+x^3 = x^3+x+1 =  (1,0,1,1) \\
\end{align}
$$

For $$a^7$$, we could have done the polynomial division of $$x^4+x^3$$ with the primitive $$p(x)$$, 
but since we already calculated earlier that $$x^4$$ translates into $$x+1$$, it was easier to 
just do a substitution.

$$
\begin{align}
\alpha^8 = \alpha^7\alpha^1 = (x^3+x+1)x = x^4+x^2+x = x^2+x+x+1 = x^2+1 =  (0,1,0,1) \\
\alpha^9 = x^3+x = (1,0,1,0) \\
\alpha^{10} = x^2+x+1 = (0,1,1,1) \\
\alpha^{11} = x^3+x^2+x = (1,1,1,0) \\
\alpha^{12} = x^3+x^2+x+1 = (1,1,1,1) \\
\alpha^{13} = x^3+x^2+1 = (1,1,0,1) \\
\alpha^{14} = x^3+1 = (1,0,0,1) \\
\alpha^{15} = 1 = (0,0,0,1) \\
\alpha^{16} = x = (0,0,1,0) \\
\end{align}
$$

After $$\alpha^{14}$$, we restart at 1, or $$\alpha^0$$, and then $$\alpha^1$$, and so forth. The
whole sequence repeats again.

The take-away here is that there two main ways in which elements of a field can be described:

* a tuple that maps directly to a polynomial
* an element $$\alpha$$ with a certain exponent

The tuple and polynomial representation are great to do additions: you can just add,
or XOR in the case of a binary base field, each component. But the exponential
notation is great for multiplication: you can add the exponents and then do module 16
on the result. There's no need for a polynomial division.

# Linear Combination

It is possible to find an element $$\beta$$ from $$(0, 1, \alpha, \alpha^2, \ldots, \alpha^{14})$$ so that 
each element $$\alpha^i$$ can be written as:

$$\alpha^i = b_3\beta^8 + b_2\beta^3 +b_1\beta^2 +b_0\beta^1   $$

This is called a normal basis. The coefficients $$b_i$$ are elements
of the base field GF(2). XXXX does this only work for GF(2) ?


# References

* [Wikipedia - Finite field](https://en.wikipedia.org/wiki/Finite_field)

* [Primitive Polynomial List](https://www.partow.net/programming/polynomials/index.html)

* [Python galois package](https://galois.readthedocs.io/)

# Primitivy check:

  * Start with GF(2^4)
  * Come up with an irreducible polynomial: $$p(x) = x^4 + x + 1$$
  * Check that it is irreducible for GF(2)
    * $$p(0) = 1, p(1) = 1$$ -> 0 and 1 are not roots.
    * It is not divisible by the only irreducible polynomial of degree 2, $$x^2 + x + 1 $$.
  * Define a root $$\alpha$$ as follows: $$ p(\alpha) = 0$$.
    * This is a *formal definition*, much like $$i$$ is defined as $$x^2 + 1 = 0$$ 
  * Reduction rule: $$ p(\alpha) = 0 \rightarrow \alpha^4 + \alpha + 1 = 0 \rightarrow \alpha^4 = \alpha + 1$$
    * The reduction rule is used to lower exponents when they exceed $$n-1$$ of $$\text{GF}(p^n)$$.
    * We don't need a numerical value for $$\alpha$$, it's an abstract element, a placeholder that
      simply followed the reduction rule.
  * Now calculate all powers of $$\alpha$$, from 1 to 15, but reduce powers that are larger than 4. We start with a power
    of alpha and end with the polynomial representation of alpha.
    * $$\alpha^1 = \alpha$$
    * $$\alpha^2 = \alpha^2$$
    * $$\alpha^3 = \alpha^3$$
    * $$\alpha^4 = \alpha^1 + 1$$
    * $$\alpha^5 = \alpha \cdot \alpha^4 = \alpha (\alpha + 1) = \alpha^2 + \alpha$$
    * $$\alpha^5 = \alpha \cdot \alpha^5 = \alpha (\alpha^2 + \alpha) = \alpha^3 + \alpha^2$$
    * $$\alpha^6 = \alpha \cdot \alpha^5 = \alpha (\alpha^3 + \alpha^2) = \alpha^4 + \alpha^2 = \alpha^2 + \alpha + 1$$
    * ...
  * If it turns out that we only get 1 for $$\alpha^{15}$$, then we have verified that the cycle spans all
    multiplicative elements $$(1, \alpha, \alpha^2, \cdots, \alpha^{14})$$, that $$p(x)$$ is a primitive
    polynomial and that $$\alpha$$ is a root of the primitive. 
  * $$\alpha$$ is a field generator.
  * We can now assign a value to alpha. The easiest choice is to $$alpha = 0 x^3 + 0 x^2 + 1 x + 0 = x = 0010$$.
    For this case, the polynomial representation of $$\alpha$$ maps directly to a bit vector.
    But there are other options too. The total number of options is determined by the Euler totient function $$\varphi(n)$$. For
    $$\text{GF}(2^4)$$, there are 16 elements. The number of options is $$ \varphi(16-1) = 15(1 - 1/3)(1 - 1/5) = 8 $$. But
    that's for all possible primitive polynomials combined. For a given primitive polynomial, the number of possible
    roots is 4: $$\alpha^1, \alpha^2, \alpha^4, \alpha^8$$. All of these can be used as field generators.
  * Let's say we use $$\beta=\alpha^2$$ are root. In that case, $$\beta^1 = \alpha^2 = 0100$$. We can then 
    complete the table by continuing to multiply by $$\beta$$. 
  * In practice, protocols always use $$\alpha^1$$ as field generator.
    * Note that a field generator is not the same as a code generator!


# Footnotes


