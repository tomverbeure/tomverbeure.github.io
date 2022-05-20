---
layout: post
title: LDPC codes
date:   2022-05-12 00:00:00 -1000
categories: 
---

<script type="text/x-mathjax-config">
  MathJax.Hub.Config({
    jax: ["input/TeX", "output/HTML-CSS"],
    tex2jax: {
      inlineMath: [ ['$', '$'], ["\\(", "\\)"] ],
      displayMath: [ ['$$', '$$'], ["\\[", "\\]"] ],
      processEscapes: true,
      skipTags: ['script', 'noscript', 'style', 'textarea', 'pre', 'code']
    }
    //,
    //displayAlign: "left",
    //displayIndent: "2em"
  });
</script>
<script src="http://cdn.mathjax.org/mathjax/latest/MathJax.js?config=TeX-AMS_HTML" type="text/javascript"></script>

<cript src="/node_modules/mathjax/es5/tex-chtml.js" type="text/javascript"></cript>

In this blog post, I'm trying to build up an intuitive understanding of error correcting codes that
are built on the concept of linear block codes. As is often the case, this is primarily an exercise
for myself: a synthesis of the stuff that I've learned after reading tons of Wikipedia, papers, online
univerity course and other stuff on the web. So don't take anything here are gospel, chances are
that there are major errors or misunderstanding in it!

The goal of error codes is to be able to transmit data over a channel that is not perfect. Data
is encoded as symbol and those symbol can be damaged in some way. With error codes, we can detect
damage or even correct it.

There are different ways to do this, but there are 2 major classes: convolutional codes and block
codes. Let's talk about block codes.

With block codes, you start with an original message in the form of a vector with input symbols.
Let's take an original message that consists of 4 symbols, and put those 4 symbols in a vector:

$$\vec{m} = \begin{bmatrix}
m_1 & m_2 & m_3 & m_4
\end{bmatrix}$$

The symbols in the vector can be of different types, but let's restrict them to be just binary
digits. When we have a vector with a size of 4, it can represent numbers with a value of 0 to 15.
For example, if the MSB is on the left, the number 11 in decimal is expressed in binary
as follows: 

$$11_{10} = \begin{bmatrix}
1 & 0 & 1 & 1
\end{bmatrix}$$

Let's do one of the simplest possible error detecting schemes: a parity calculation.
We add one bit to the messages. When the number of ones a message is odd, the additional
bit is 0. When it's even, the additional bit is 0. In other words, the number of bits in the resulting
word will always be even. Our numbers are now encoded like this:

$$0_{10} = \left[\begin{array}{cccc|c}
0 & 0 & 0 & 0 & 0
\end{array}\right]$$

$$1_{10} = \left[\begin{array}{cccc|c}
0 & 0 & 0 & 1 & 1
\end{array}\right]$$

$$2_{10} = \left[\begin{array}{cccc|c}
0 & 0 & 1 & 0 & 1
\end{array}\right]$$

$$...$$

$$11_{10} = \left[\begin{array}{cccc|c}
1 & 0 & 1 & 1 & 1
\end{array}\right]$$

$$...$$

$$15_{10} = \left[\begin{array}{cccc|c}
1 & 1 & 1 & 1 & 0
\end{array}\right]$$

The additional bit is called the parity bit. In our case, there's only 1 parity bit, but
it's possible to have more than one such bit.

Mathematically, the formula to calculate the parity bit is trivial: just XOR the 4 message bits together.

$$p=m_1 \oplus m_2 \oplus m_3 \oplus m_4 $$

The encoded original message $$\vec{m}$$ is transformed into a code word $$\vec{c}$$ as follows:

$$\vec{c} = \begin{bmatrix}m_1 & m_2 & m_3 & m_4 & p\end{bmatrix}$$

By adding a parity bit, we obviously need to transmit more bits, or symbols, than strictly needed. If
the hardware has the ability to transmit a fix number of symbols per unit of time, adding more
symbols to the message will reduce the number of message carrying symbols that can be transmitted per
unit of time. This gives us the concept of "rate". The theoritcal maximum rate is 1: all symbols carry
real information. In our case, the rate is 0.8: out of 5 symbols, only 4 symbols are carrying real
information.

However, we've gained an important benefit: the ability to detect if there has been a single error
during the transmission of a symbol. Below, we can see how 10 gets converted into 4 bits, then it gets
parity encoded, but during a transmission the 4th symbols flips from 0 to 1. At the receiving end,
we can see that something when wrong because we now have an odd number of bits.

$$11 \to \left[\begin{array}{cccc}1 & 0 & 1 & 1\end{array}\right]
\to \left[\begin{array}{cccc|c}1 & 0 & 1 & 1 & 1\end{array}\right]
\to \left[\begin{array}{cccc|c}1 & 0 & 1 & \boldsymbol{0} & 1\end{array}\right]
\to
$$ odd number of bits!

# Formulation in terms of generator matrix

In the example above, we defined the encoded symbol as 

$$\vec{c} = \left[\begin{array}{ccccc}m_1 & m_2 & m_3 & m_4 & m_1 \oplus m_2 \oplus m_3 \oplus m_4\end{array}\right]$$

We can make this more general by describing it as vector/matrix multiplication. Let's introduce the concept of a generator matrix.

$$\boldsymbol{G} = \left[\begin{array}{ccccc}
1 & 0 & 0 & 0 & 1 \\
0 & 1 & 0 & 0 & 1 \\
0 & 0 & 1 & 0 & 1 \\
0 & 0 & 0 & 1 & 1\end{array}\right]$$

When you do matrix multiplication, you multiply-add rows of one matrix against the columns of another.
For binary encoded values, a multiplication is an AND operation and a sum is the same as a XOR operation, 
so to calculate a parity encoded code word, we multiply the message vector by the generator matrix:

$$\vec{c} = \vec{m} \times G$$

$$\begin{bmatrix}c_1 & c_2 & c_3 & c_4 & c_5\end{bmatrix} = \begin{bmatrix}m_1 & m_2 & m_3 & m_4\end{bmatrix} \times \begin{bmatrix}
g_{11} & g_{12} & g_{13} & g_{14} & g_{15} \\
g_{21} & g_{22} & g_{23} & g_{24} & g_{25} \\
g_{31} & g_{32} & g_{33} & g_{34} & g_{35} \\
g_{41} & g_{42} & g_{43} & g_{44} & g_{45}\end{bmatrix}$$

This expands do:

$$c_1 = m_1 g_{11} +  m_2 g_{12} + m_3 g_{13} + m_4 g_{14}$$

$$c_2 = m_1 g_{21} + m_2 g_{22} + m_3 g_{23} + m_4 g_{24}$$

$$c_3 = m_1 g_{31} + m_2 g_{32} + m_3 g_{33} + m_4 g_{34}$$

$$c_4 = m_1 g_{41} + m_2 g_{42} + m_3 g_{43} + m_4 g_{44}$$

$$c_5 = m_1 g_{51} + m_2 g_{52} + m_3 g_{53} + m_4 g_{54}$$

With our specific generator matrix, and taking into account that a binary + translates into
an OR operation:

$$c_0 = m_1 1 \oplus m_2 0 \oplus m_3 0 \oplus m_4 0$$

$$c_1 = m_1 0 \oplus m_2 1 \oplus m_3 0 \oplus m_4 0$$

$$c_2 = m_1 0 \oplus m_2 0 \oplus m_3 1 \oplus m_4 0$$

$$c_3 = m_1 0 \oplus m_2 0 \oplus m_3 0 \oplus m_4 1$$

$$c_4 = m_1 1 \oplus m_2 1 \oplus m_3 1 \oplus m_4 1$$

Which reduces to:

$$c_1 = m_1$$

$$c_2 = m_2$$

$$c_3 = m_3$$

$$c_4 = m_4$$

$$c_5 = m_1 \oplus m_2 \oplus m_3 \oplus m_4$$

In other words, we get exactly what we had before:

$$\vec{c} = \begin{bmatrix}m_1 & m_2 & m_3 & m_4 & m_1 \oplus m_2 \oplus m_3 \oplus m_4\end{bmatrix}$$

# Blah

$$\left(
\begin{array}{lcr}
a & b & c \\
d & e & f \\
g & h & i
\end{array}
\right)$$

# MathJax

$$\int e^{-kx} \, dx = -\frac{1}{k} e^{-kx}$$

$$\left(
\begin{array}{lcr}
a & b & c \\
d & e & f \\
g & h & i
\end{array}
\right)$$


# Notes

First, some general notes about lineary codes, partity check and generator matrices:

- An input value (say, 3 bits) is converted into a coded value that has a larger number of bits (say, 6 bits).
- the number of rows of H is equal to the number of input value bits (3).
- the number of columns of H is equal to the number of coded value bits (6)
- The coded value must satisfy the constraints of a 
  [parity check matrix H](https://en.wikipedia.org/wiki/Parity-check_matrix): H * cT = 0.
- In other words, a correct code word, the linear combination of the some bits of the code words must 
  sum to 0 for the rows of the parity matrix H.
- So, H is used to *check* that a given coded value is correct. (And when it's correct, that means that
  the coded value was transmitted correctly as well, as long as there weren't too many bit flips.)
- But H is NOT directly used to convert an input value to c. For that, we need to create a generator
  matrix from H. Once you have G, you can do matrix/vector multiplication G * i to get c.

In the case of LDPC, H is usuall a large, sparse matrix. (The larger, the better the error recovery
results.) It's often generated randomly, subject to certain sparsity constraints.

The code words are obtained by: 
- converting H into matrix H' where the right side of H' is 3x3 identity matrix.
- And from that, the generator matrix G can be created, with a 3x3 identity matrix on the left side.
- then multiplying all 8 input values by G.

Due to the conversion of the bits in H', the 8 code values will have the original input values as their
top 3 bits. So you can immediately observe the input value from the code words.

BTW: the multiplication of a received 6-bit word by matrix H' (I think it's H' and not H)
is called the syndrome s. A syndrome is only a valid code word if H' * sT = 0. If the result is not
equal to 0, then that indicates that there was an error during transmission, you'll need some kind
of algorithm to correct the error.

Since the generator matrix has the identify matrix on the left, encoding only needs to happen for the
non-identity part of the matrix. That's the partity part P of the matrix.


# References

* [Wikipedia](https://en.wikipedia.org/wiki/Low-density_parity-check_code)

* [Michael Field Twitter thread on LDPC codes](https://twitter.com/field_hamster/status/1356192140947148803)

* [LDPC Codes – a brief Tutorial](http://www.bernh.net/media/download/papers/ldpc.pdf) (B. Leiner)

* [Information Theory, Inference, and Learning Algorithms, David MacKey](http://www.inference.org.uk/mackay/itila/book.html)
