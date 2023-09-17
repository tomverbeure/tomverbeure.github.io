---
layout: post
title: Galois Field Mastrovito Multiplier Fail
date:  2023-09-16 00:00:00 -1000
categories:
---

<script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
<script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

* TOC
{:toc}

# Introduction

A year ago, in [my blog post about Reed-Solomon coding](/2022/08/07/Reed-Solomon.html), 
I used regular integers for all calculations.  These are unpractical for a real-world 
implementation, but since everybody knows integers math since first grade, it made things 
easier to learn things one step at a time.

Instead of working with pure integers, actual Reed-Solomon implementations will
use elements from a [Galois or Finite field](https://en.wikipedia.org/wiki/Finite_field) 
as symbols, or to be even more precise, a Galois field extension, which is a field that
is created from multiple elements of a base field.

In practice, the base field will always be $$\text{GF}(2)$$, with as only elements 0 and 1,
and the field extension could be something like $$\text{GF}(2^8)$$, a tuple of 8 $$\text{GF}(2)$$
elements, which coveniently maps to a byte.

There's a lot of beginners material on Galois fields on the web. My personal favorite is 
this [Nasa tutorial on Reed-Solomon error correcting coding](https://ntrs.nasa.gov/api/citations/19900019023/downloads/19900019023.pdf).
I won't discuss that there.

Instead, this blog post discusses a particular hardware implementation of a Galois field 
multiplier: the Mastrovito multiplier, and how it turned out to be a useless yak shaving operation.

I'm writing this down primarily so that I have a record of the references that I gathered,
and the work that I did. And maybe it will prevent somebody else from straying away
from stuff that actually matters.

The basics of mathematics in Galois fields and their extension are 

# Extended Galois Field Multiplication

In an extended Galois field, each element is presented by an ordered tuple
of base elements. Let's assume we're dealing with $$\text{GF}(2^4)$$, when 
the tuple will be 4 base elements $$(a_3, a_2, a_1, a_0), where each base element can be either 
0 or 1.

The 4-tuple map to a polynomial:

$$(a_3, a_2, a_1, a_0) \rightarrow a(x) = a_3 x^3 + a_2 x^2 + a_1 x + a_0$$

Multiplication is an extended Galois field is defined as the multiplication
of the two operand polynomials $$a(x)$$ and $$b(x)$$, followed by a division
by the primitive polynomial $$p(x)$$ that defines the Galois field extensio, and
retaining the remainder. The second step is called *modular reduction*.

$$c(x) = a(x) \cdot b(x) \bmod p(x) $$

**Polynomial Multiplication**

For the first part, polynomial multiplication $$m(x)=a(x)\cdot b(x)$$, we can use 
the method we learned in school by writing down the distributive property in a table:

$$
\begin{array}{}
&             & x^6 & x^5 & x^4 & x^3 & x^2 & x^1 & x^0 \\
\hline
& b_0 \cdot ( & & & & a_3 & a_2 & a_1 & a_0 & ) \\
& b_1 \cdot ( & & &   a_3 & a_2 & a_1 & a_0 & & ) \\
& b_2 \cdot ( & &     a_3 & a_2 & a_1 & a_0 & & & ) \\
& b_3 \cdot ( &       a_3 & a_2 & a_1 & a_0 & & & & ) \\
\end{array}
$$

Executing all the multiplications:

$$
\begin{array}{}
&             & x^6 & x^5 & x^4 & x^3 & x^2 & x^1 & x^0 \\
\hline
& & & & & b_0a_3 & b_0a_2 & b_0a_1 & b_0a_0 &  \\
& & & &   b_1a_3 & b_1a_2 & b_1a_1 & b_1a_0 & &  \\
& & &     b_2a_3 & b_2a_2 & b_2a_1 & b_2a_0 & & &  \\
& &       b_3a_3 & b_3a_2 & b_3a_1 & b_3a_0 & & & &  \\
\end{array}
$$

And adding everyting the same column together:

$$
\begin{array}{}
&             & x^6 & x^5 & x^4 & x^3 & x^2 & x^1 & x^0 \\
\hline
& 
& b_3a_3
& (b_2a_3 + b_3a_2)
& (b_1a_3 + b_2a_2 \cdots)
& (b_0a_3 + b_1a_2 \cdots)
& (b_0a_2 + b_1a_1 \cdots)
& (b_0a_1 + b_1a_0)
&  b_0a_0 & \\
\end{array}
$$

Note that there's no spill-over from one column to the next.

When implemented in hardware, each base element multiplication is a 
2-input AND gate, and each addition is a XOR gate.

So the total cost is:

* 16 AND gates
* 9 XOR gates

Generalized, if each element consists of $$n$$ bits, we have

* $$n^2$$ AND gates
* $$(n-1)^2$$ XOR gates

**Modular Reduction**

For polynomial division, we can again fall back to how things were
done at school. The order of the primitive polynomial $$p(x)$$ will
always be 1 higher than the polynomials of the elements. 

The highest term of $$p(x)$$ is always 1.

$$
\begin{array}{l}
&  & x^6 & x^5 & x^4 & x^3 & x^2 & x^1 & x^0 \\
\hline
\text{Term 1:}& r_0(x) = & m_6 & m_5 & m_4 & m_3 & m_2 & m_1 & m_0 \\
\text{Term 2:}&  & 1 & p_3 & p_2 & p_1 & p_0  \\
\text{Factor:}&  & m_6 & p_3m_6 & p_2m_6 & p_1m_6 & p_0m_6 \\
\hline
\text{Sum:}& r_1(x) = & m_6 + m_6 & m_5 + p_3m_6 & m_4 + p_2m_6 & m_3 + p_1m_6 & m_2 + p_0m_6 & m_1 & m_0 \\
\end{array}
$$

In $$\text{GF}(2)$$ math, addition and subtraction are the same, so the highest term of $$r_m(x)$$ will always 
be zero.

Let's now repeat this step until we have only 4 non-zero $$r_m(x)$$ coefficients left:

$$
\begin{array}{}
 & x^6 & x^5 & x^4 & x^3 & x^2 & x^1 & x^0 \\
\hline
r_1(x) = & 0 & r_{1,5} & r_{1,4} & r_{1,3} & r_{1,2} & m_1 & m_0 \\
 & & 1 & p_3 & p_2 & p_1 & p_0  \\
 & & r_{1,5} & p_3r_{1,4} & p_2r_{1,3} & p_1r_{1,2} & p_0m_1 \\
\hline
r_2(x) = & & r_{1,5} + r_{1,5} & r_{1,4} + p_3r_{1,5} & r_{1,3} + p_2r_{1,5} & r_{1,2} + p_1r_{1,5} & m_1 + p_0r_{1,5} & m_0 \\
\end{array}
$$

And...

$$
\begin{array}{}
 & x^6 & x^5 & x^4 & x^3 & x^2 & x^1 & x^0 \\
\hline
r_2(x) = & 0 & 0 & r_{2,4} & r_{2,3} & r_{2,2} & r_{2,1} & m_0 \\
 & & & 1 & p_3 & p_2 & p_1 & p_0  \\
 & & & r_{2,4} & p_3r_{2,3} & p_2r_{2,2} & p_1r_{2,1} & p_0m_0 \\
\hline
r_3(x) = & & & r_{2,4} + r_{2,4} & r_{2,3} + p_3r_{2,4} & r_{2,2} + p_2r_{2,4} & r_{2,1} + p_1r_{2,4} & m_0 + p_0r_{2,4} \\
\end{array}
$$

If we substute all earlier $$r_m(x)$$ equations, we get something like this for the final terms of $$r_3(x)$$:

$$
\begin{array}{llll}
c_3 = r_{3,3} = & r_{2,3} & & & + & p_3r_{2,4} \\
	  	& r_{1,3} & + & p_2r_{1,5}  & + & p_3(r_{1,4} + p_3r_{1,5}) \\
	  	& r_{0,3} & + & p_2(r_{0,5}+p_3r_{0,6})  & + & p_3((r_{0,4}+p_2r_{0,6}) + p_3(r_{0,5}+p_3r_{0,6})) \\
	  	& m_3 & + & p_2(m_5+p_3m_6)  & + & p_3((m_4+p_2m_6) + p_3(m_5+p_3m_6)) \\
\\
c_2 = r_{3,2} = & r_{2,2} & & & + & p_2r_{2,4} \\
	  	& r_{1,2} & + & p_1r_{1,5}  & + & p_2(r_{1,4} + p_3r_{1,5}) \\
	  	& r_{0,2} & + & p_1(r_{0,5}+p_3r_{0,6})  & + & p_2((r_{0,4}+p_3r_{0,6}) + p_3(r_{0,5}+p_3r_{0,6})) \\
	  	& m_2 & + & p_1(m_5+p_3m_6)  & + & p_2((m_4+p_3m_6) + p_3(m_5+p_3m_6)) \\
\\
c_1 = r_{3,1} = & r_{2,1} & & & + & p_1r_{2,4} \\
	  	& r_{1,1} & + & p_0r_{1,5}  & + & p_1(r_{1,4} + p_3r_{1,5}) \\
	  	& r_{0,1} & + & p_0(r_{0,5}+p_3r_{0,6})  & + & p_1((r_{0,4}+p_2r_{0,6}) + p_3(r_{0,5}+p_3r_{0,6})) \\
	  	& m_1 & + & p_0(m_5+p_3m_6)  & + & p_1((m_4+p_2m_6) + p_3(m_5+p_3m_6)) \\
\\
c_0 = r_{3,0} = & r_{2,0} & & & + & p_0r_{2,4} \\
	        & m_0 & & & + & p_0(r_{1,4} + p_3r_{1,5}) \\
      	   	& m_0 & & & + & p_0((r_{0,4}+p_2r_{0,6}) + p_3(r_{0,5}+p_3r_{0,6})) \\
	  	& m_0 & & & + & p_0((m_4+p_2m_6) + p_3(m_5+p_3m_6)) \\
\end{array}
$$

But that's because I've back-substituted everything back to the original inputs $$m(x)$$ and $$p(x)$$.
If we don't do that, then each step only has 4 AND operation and 4 XOR operations. And since there
are only 3 steps, that gives a total of 12 AND and 12 XOR operations.

Generalized:

* $$n(n-1)$$ AND operations
* $$n(n-1)$$ XOR operations

But it gets better: usually, all $$\text{GF}(2^n}$$ math in a hardware design uses the same
primitive polynomial $$p(x)$$. Because of this, $$p_n$$ in all the equations above can be
replaced by either a 0 or a 1.

# Galois Field Extensions

The Galois fields discussed in the previous section, constructed out of a single prime number, are sometimes 
called base Galois fields. It turns out that you can create new Galois fields, called Galois field extensions,
out of a base Galois field by grouping multiple base elements together into an ordered tuple.

The notation for a Galois field extension is as follows: $$\text{GF}(p^n)$$, where $$p$$ is the base
prime number, and $$n$$ is the order of the extended Galois field.  The total number of elements
in an extended Galois field is $$p^n$$.

For example, $$\text{GF}(2^4)$$ is a Galois field for which  each element consists of an ordered tuple 
$$(a_3, a_2, a_1, a_0)$$ of 4 $$\text{GF}(2)$$ elements.  The total number of elements of this field is 16. 

*You'll sometimes see this written a $$\text{GF}(16)$$, which isn't ambiguous since all the factors 
of 16 are 2, so there's only 1 prime number possible, but my personal preference is to always write 
it down as $$\text{GF}(2^4)$$.*

**Extended Galois Field Addition**

All Galois fields require addition, subtraction, multiplication, and division operation. For Galois
field extensions, we turn to polynomials to define these operations.

The elements within each tuple are mapped to  coefficients of a polynomial:

$$(a_3, a_2, a_1, a_0) \rightarrow a_3 x^3 + a_2 x^2 + a_1 x + a_0$$

Addition of 2 tuples becomes a polynomial addition:

$$
\begin{align}
(a_3, a_2, a_1, a_0) + (b_3, b_2, b_1, b_0)  \\
\rightarrow (a_3 x^3 + a_2 x^2 + a_1 x + a_0) + (b_3 x^3 + b_2 x^2 + b_1 x + b_0) \\
\rightarrow (a_3+b_3) x^3 + (a_2 + b_2) x^2 + (a_1 + b_1) x + (a_0 + b_0)
\end{align}
$$

Notice how, for addition, the polynomial order of the result remains the same: addition of
2 elements of an extended Galois field automatically still belong to the same Galois field.

**Extended Galois Field Multiplication**

For multiplication, we also use polynomial multiplication, but with an additional
step: pure multiplication would result in polynomials of an order that doesn't always fall
within the order of the multiplicatoin operands, which violates the requirement for
a field. We can fix this by following each multipication with division with a so called
*primitive polynomial* $$p(x)$$ and only retaining the remainder, just like we did for base Galois 
fields, where we applied a modulo operation to keep the results in check.

**Primitive Polynomial**

There are some requirements to primitive polynomial $$p(x)$$. One of the most important ones
is that it needs to be irreducible, with coefficients of the base Galois field. An
irreducible polynomial can not be factored into multiple lower order polynomials.

*Note the similarity here with base Galois fields, where the modulo operation must be
done with a prime number, one that can not be factored into multiple smaller integer.*

A primitive polynomial defines how Galois field calculations behave, so standardized
protocols always specify which primitive polynomial to use. If you want to use your own
coding protocol, you could try to find a primitive polynomial yourself, but it's much easier 
to just select one from one of tables that can be found online.

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

# Mastrovito Multiplier

Reference: A Novel Architecture for Galois Fields $$\text{GF}(2^m)$$ Multipliers Based on Mastrovito Scheme

* irreducible  polynomial: $$p(x) = z^m + p_{m-1} \cdot z^{m-1} + \ldots + p_1 \cdot z + 1 $$.

  $$p(x)$$ is also called the field generator polynomial.

* basis: $$\vec{s} = [1,\alpha,\alpha^2,\ldots,\alpha^{m-1}]$$

* $$\alpha$$ is a root of $$p(z)$$, so: 

    $$\alpha^m = p_{m-1} \cdot \alpha^{m-1} + \ldots + p_1 \cdot \alpha + 1 $$

    XXX why is this?

* elements A and B

    $$A = a_0 + a_1 \alpha + \ldots + a_{m-1}\alpha^{m-1} \tag{1}$$

    $$B = b_0 + b_1 \alpha + \ldots + b_{m-1}\alpha^{m-1} \tag{1}$$

* With $$\vec{a} = [a_0, a_1, \ldots, a_{m_1}]$$ and $$\vec{b} = [b_0, b_1, \ldots, b_{m_1}]$$,
  this can also be written as:

    $$A = \vec{s} \cdot \vec{a}^\intercal$$ 

    $$B = \vec{s} \cdot \vec{b}^\intercal$$

* C is the multiplication of A and B:

    $$C = b_0 \cdot A + b_1 \cdot A \cdot \alpha + \ldots + b_{m-1} \cdot A \cdot \alpha^{m-1} \tag{1}$$

    *Note how there's a scalar multiplication between $$b_i$$ and vector A.*

* This can also be written as:

    $$C = [ A, A \cdot \alpha, \ldots, A \cdot \alpha^{m-1} ] \cdot \vec{b}^\intercal$$

*  The following vectors are the standard-basis components of $$A\cdot\alpha^i$$:

    $$M_i = [ M_{0,i}, M_{1,i}, \ldots M_{m-1,i} ]$$

    and thus:

    $$ A\cdot\alpha^i = \vec{s} \cdot M_i^\intercal$$

    $$ C = \vec{s} \cdot [c_0, c_1, \ldots, c_{m-1}]^\intercal $$

    $$ C = \vec{s} \cdot [ M_0^\intercal, M_1^\intercal, \ldots, M_{m-1}^\intercal ] \cdot \vec{b}^\intercal $$

A Mastrovito multiplier have two steps:

1. Calculate matrix $$\mathbf{M}$$ using coefficient $$a_i$$ and coefficients $$p_i$$ from $$p(z)$$
2. Evaluate $$c_j = M_{j,0} \cdot b_0 + M_{j,1} \cdot b_1 + \ldots + M_{j,m_1} \cdot b_{m-1}$$

Step 2 does not require $$p(x)$$ and has a fixed number of XOR and AND gates, but step 1 is more
complex.

* Start with $$M_0$$:

    $$M_0 = [a_0, a_1, \ldots, a_{m-1} ]$$

* $$M_i$$ can be generated from $$M_{i-1}$$ by multiplying with $$\alpha$$:

    $$\vec{s} \cdot M_i^\intercal = \alpha \cdot \vec{s} \cdot M_{i-1}^\intercal$$

    $$\alpha \cdot \vec{s} \cdot M_{i-1}^\intercal =  \alpha \cdot (M_{0,i-1} +  M_{1,i-1} \cdot \alpha + \ldots + M_{m-1,i-1} \cdot \alpha^{m-1})$$

    $$ =  M_{0,i-1} \cdot \alpha +  M_{1,i-1} \cdot \alpha^2 + \ldots + M_{m-1,i-1} \cdot \alpha^{m})$$

    $$\alpha^{m}$$ can be replaced by $$p_{m-1} \cdot \alpha^{m-1} + \ldots + p_1 \cdot \alpha + 1$$:

    $$ =  M_{0,i-1} \cdot \alpha +  M_{1,i-1} \cdot \alpha^2 + \ldots + M_{m-1,i-1} \cdot (p_{m-1} \cdot \alpha^{m-1} + \ldots + p_1 \cdot \alpha + 1)$$

    Regroup for $$\alpha^i$$:

    $$ =  M_{m-1,i-1} +  (M_{0,i-1} + p_1 \cdot M_{m-1,i-1})  \cdot \alpha + \ldots + (M_{m-2,i-1} + M_{m-1,i-1} \cdot p_{m-1}) \cdot \alpha^{m-1}$$

* Algorithm to calculate all values of $$M_i$$:

    $$M_0 = [a_0, a_1, \ldots, a_{m-1} ]$$

    $$M_{0,i} = M_{m-1,i-1}$$

    $$M_{j,i} = M_{j-1,i-1} + M_{m-1,i-1} \cdot p_j$$


# Example

Example for $$\text{GF}(2^4)$$:

$$\vec{a} = [ a_0, a_1, a_2, a_3 ]$$

$$\vec{b} = [ a_0, b_1, b_2, b_3 ]$$

$$\vec{s} = [ 1, \alpha, \alpha^2, \alpha^3]$$

$$p(x) = 1 + x + x^4$$

$$\vec{p} = [p_0, p_1, p_2, p_3, p_4] = [1,1,0,0,1]$$

$$M_0 = [ a_0, a_1, a_2, a_3 ]$$

$$
M_1 = [  (a_3                ),
         (a_0 + a_3 \cdot p_1), 
         (a_1 + a_3 \cdot p_2), 
         (a_2 + a_3 \cdot p_3) 
         ]
$$

$$
M_2 = [ (a_2 + a_3 \cdot p_3), 
        (a_3                ) + (a_2 + a_3 \cdot p_3) \cdot p_1, 
        (a_0 + a_3 \cdot p_1) + (a_2 + a_3 \cdot p_3) \cdot p_2, 
        (a_1 + a_3 \cdot p_2) + (a_2 + a_3 \cdot p_3) \cdot p_3 
        ]
$$

$$
M_3 = [ ((a_1 + a_3 \cdot p_2) + (a_2 + a_3 \cdot p_3) \cdot p_3), 
        ((a_2 + a_3 \cdot p_3))                                   + ((a_1 + a_3 \cdot p_2) + (a_2 + a_3 \cdot p_3) \cdot p_3)) + a_3 \cdot p_1, 
        ((a_3                  + (a_2 + a_3 \cdot p_3) \cdot p_1) + ((a_1 + a_3 \cdot p_2) + (a_2 + a_3 \cdot p_3) \cdot p_3)) + a_3 \cdot p_2, 
        ((a_0 + a_3 \cdot p_1) + (a_2 + a_3 \cdot p_3) \cdot p_2) + ((a_1 + a_3 \cdot p_2) + (a_2 + a_3 \cdot p_3) \cdot p_3)) + a_3 \cdot p_3 
        ]
$$

# Linear Combination

It is possible to find an element $$\beta$$ from $$(0, 1, \alpha, \alpha^2, \ldots, \alpha^{14})$$ so that 
each element $$\alpha^i$$ can be written as:

$$\alpha^i = b_3\beta^8 + b_2\beta^3 +b_1\beta^2 +b_0\beta^1   $$

This is called a normal basis. The coefficients $$b_i$$ are elements
of the base field GF(2). XXXX does this only work for GF(2) ?


# References

* [Wikipedia - Finite field](https://en.wikipedia.org/wiki/Finite_field)

* [Nasa -  Tutorial on Reed-Solomon Error Correcting Coding](https://ntrs.nasa.gov/api/citations/19900019023/downloads/19900019023.pdf).

* [Python galois package](https://galois.readthedocs.io/)


