---
layout: post
title: Understanding Reed-Solomon Error Correction Basics with Integer Math Only
date:  2022-07-19 00:00:00 -1000
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

* TOC
{:toc}

# Introduction

I've always been intimidated by coding techniques: encryption and decryption, hashing operations,
error correction codes, and even compression and decompression techniques. It's not that I
didn't know what they do, and there have been cases where I've used with them professionally, 
but I felt that I never quite understood the basics, let alone had an intuitive understanding of 
how they worked.

One coding technique that I've found intriguing was Reed-Solomon forward
error correction. Until the discovery of even better coding techniques (Turbo codes and
low-density parity codes), it was one of the most powerful ways to make data storage or
data transmission resilient against corruption: the Voyager spacecrafts used Reed-Solomon
coding to transmit images of planets past Saturn, and CDs can recover from scratches that 
corrupt up to 4000 bits thanks to some clever use of not one but two Reed-Solomon codes. 

The subject is covered in many college-level courses on coding and signal processing techniques, 
but a lot of the material online assumes a certain theoretical base and builds on that: start with 
Galois Fields and polynomials, throw a bunch of mathematical formulas, but in the end that 
intuitive understanding is still not there. At least not for me...

That changed when stumbled into this 
[Introduction to Reed-Solomon](https://innovation.vivint.com/introduction-to-reed-solomon-bc264d0794f8)
article. It explains how polynomials and polynomial evaluation at certain points are a way to
create a code with redundancy, and how to recover the original message back from it. The article
is excellent, and it makes some of that I'm covering below unnecessary or redundant (ha!), 
because some parts of what follows will be a recreation of that material. However it's dumbed down 
even more, and it tries to cover a larger variety of Reed-Solomon codes. 

One of the best parts of that article is the focus on integer math. Academic papers or books about 
coding theory almost always start with the theory of finite fields, aka Galois fields, and then 
build on that when explaining coding algorithms. I found this one of the bigger obstacles in 
understanding the fundamentals of Reed-Solomon coding (and BCH coding, a close relative): instead of 
getting to know one new topic, you have to tackle two at the same time. I'll be doing the same in 
this blog post: everything is integer math only. Because of that the resulting algorithms won't be 
practical for the real world, but it will result in a better feel about why finite fields are necessary.

Many books are written about coding theory and applications, and a single blog post won't even
scratch the surface of the topic. I'm also still only beginning to understand some of the
finer points. So my usual disclaimer applies: I'm writing these blog posts primarily for myself, 
as a way to solidify what I've learned after reading stuff on the web. Major errors are 
possible, inaccuracies should be expected.

You'll find some mathematical formulas below, but I always try to switch to real examples as soon
as possible.

# A Quick Recap on Polynomials 

It's impossible to discuss anything that's related to coding without touching the subject of polynomials.
I'm assume that you've learned about integer based polynomials during some algebra class in high school
or in college. A polynomial $$f(x)$$ of degree $$n$$ is a function that looks like this:

$$f(x) = c_0 + c_1 x + c_2 x^2 + ... c_n x^n$$

$$n+1$$ fixed coefficients $$c_i$$ are multiplied by function variable $$x$$ to the power of $$i$$. 
The polynomial can evaluated by replacing variable $$x$$ by some number for which you want to know the 
value of the function. You can also add, subtract, multiply or divide polynomials with each other.

Let's illustarte this with some examples, and define $$f(x)$$ and $$g(x)$$ as follows:

$$\begin{aligned}
f(x) & = 3 + 2 x + 5 x^2 - 4 x^3 \\
g(x) & = 7 x - x^2 \\
\end{aligned}$$

You add polynomials by adding together the coefficients that belong to the same $$x^i$$:

$$\begin{aligned}
f(x)+g(x) & = (3+0) + (2+7) x + (5-1) x^2 + (4+0) x^3 \\
          & = 3 + 9 x + 4 x^2 + 4 x^3 \\
\end{aligned}$$

You can multiply polynomials:

$$\begin{aligned}
f(x) g(x) {} & = (3 + 2 x + 5 x^2 - 4 x^3)(7 x - x^2) \\
 & = (3 + 2 x + 5 x^2 - 4 x^3)7 x + (3 + 2 x + 5 x^2 - 4 x^3) (-x^2) \\
 & = 3 \cdot 7x + 2 x \cdot 7x + 5 x^2 \cdot 7x - 4 x^3 \cdot 7x + 3 \cdot -x^2  + 2 x \cdot -x^2 + 5 x^2 \cdot -x^2 - 4 x^3 \cdot -x^2  \\
 & = 21 x + 14 x^2 + 35 x^3 - 28 x^4  - 3 x^2  - 2 x^3 - 5 x^4 + 4 x^5   \\
 & = 21 x + 11 x^2 + 33 x^3 - 23 x^4 + 4 x^5   \\
\end{aligned}$$

And you can divide them, using long division

$$
\begin{aligned}
\frac{f(x)}{g(x)} & =  \frac{-4 x^3 + 5 x^2 +2x + 3}{-x^2+7x} \\
    & = \begin{align*}
        &\text{ }\text{ }\text{ }\bf{4x+23}\\
        -x^2 + 7x &\overline{\big)-4 x^3 + 5 x^2 +2x + 3}\\
        &\underline{\text{ }-4 x^3 + 28 x^2}\\
        &\text{ }\text{ }\text{ }-23x^2 +2x +3\\
        &\text{ }\text{ }\underline{\text{ }-23x^2 + 161 x}\\
        &\text{ }\text{ }\text{ }\text{ }\text{ }\text{ }\bf{-159x+3}
    \end{align*} \\
    & = 4x+23 + \frac{-159x+3}{-x^2+7x} \\
\end{aligned}
$$

In the examples above, the coefficients $$c_i$$, and function variable $$x$$ are regular integers, 
but polynomials can be used for any mathematical system that has the concept of addition and
multiplication. But that's for another day.

# Minimum Information to Define a Polynomial

Here's one the most important characteristics of polynomials:

**Any polynomial function of degree $$n-1$$ is uniquely defined by any $$n$$ points that 
lay on this function.**

Being uniquely defined means that it goes both ways: 

* I can give you the $$n$$ coefficients $$c_0$$ to $$c_{n-1}$$ of $$f(x)$$, and you can evaluate the function value by filling in 
any $$x$$ coordinate you want, and thus also the function values for $$n$$ specific $$x$$ input values.

* Or, the other way around, I can give you the value $$f(x)$$ of any $$n$$ values of $$x$$ and 
you can derive the $$n$$ coefficients $$c_0$$ to $$c_{n-1}$$ of $$f(x)$$. 

Here's an example of polynomial of degree 3, $$f(x)=2 + 3x -5x^2 + x^3$$, evaluated for $$x$$ values of $$-1,0,1,2$$:

<img src="/assets/reed_solomon/desmos-graph-1.png" alt="f(x) graph, annotated with points -1,0,1,2" width="80%"/>

*I used the excellent [desmos graphing calculator](https://www.desmos.com/calculator) to create this
function plot.*

When given the points $$(-1, 7), (0,2), (1, 1), (2, -4)$$, we can set up an equation for each of those
4 points, which results in a set of linear equations with 4 unknowns:

$$
c_0 + c_1 (-1)^1 + c_2 (-1)^2 + c_3 (-1)^3 = -7 \\
c_0 + c_1 (0)^1 + c_2 (0)^2 + c_3 (0)^3 = 2 \\
c_0 + c_1 (1)^1 + c_2 (1)^2 + c_3 (1)^3 = 1 \\
c_0 + c_1 (2)^1 + c_2 (2)^2 + c_3 (2)^3 = -4 \\
$$

Such a set of equations can be solved with the well-known 
[Gaussian elimination algorithm](https://en.wikipedia.org/wiki/Gaussian_elimination). 
In our case, the values are such that we can solve it using a less systematic method:

The second row immediately reduces to $$\bf{c_0 = 2}$$. When we fill that back in, the remaining
rows become:

$$
-c_1 + c_2 - c_3 = -9 \\
c_1 + c_2 + c_3 = -1 \\
2 c_1  + 4 c_2  + 8 c_3  = -6 \\
$$

If we add the first and second row, we get: $$2c_2 = -10$$, or $$\bf{c_2=-5}$$, which simplifies
the 3 rows to:

$$
-c_1 - c_3 = -4 \\
c_1 + c_3 = 4 \\
2 c_1  + 8 c_3  = 14 \\
$$

After substituting the second equation in the third one, we get:

$$2 c_1 + 8 (4 - c_1) = 14$$

which reduces to $$-6 c_1 = -18$$ or $$\bf{c_1 = 3}$$.

And if we fill that into $$c_1 + c_3 = 4$$, we get $$\bf{c_3 = -1}$$.

Conclusion: $$(c_0, c_1, c_2, c_3) = (2, 3, -5, 1)$$. These coefficients match those of function $$f(x)$$ that
we started with!

<img src="/assets/reed_solomon/desmos-graph-2.png" alt="f(x) graph, annotated with points 1,2,3,4" width="80%"/>

We can do the same exercise with points $$(1, 1), (2, -4), (3, -7), (4, -2)$$, and we'll 
end up with the same result: $$(c_0, c_1, c_2, c_3) = (2, 3, -5, 1)$$. This is left as an exercise
for the reader.


When given a set of points of a polynomial, we can generate the coefficient by constructing
the [Lagrange interpolating polynomial](https://en.wikipedia.org/wiki/Systematic_code),
or in short, but using Lagrange interpolation.

A Lagrange polynomial looks like this:

$$
L(x) = y_0 \cdot \frac{x-x_1}{x_0-x_1} \frac{x-x_2}{x_0-x_2} ... \frac{x-x_n}{x_0-x_n} + \\
       y_1 \cdot \frac{x-x_0}{x_1-x_0} \frac{x-x_2}{x_1-x_2} ... \frac{x-x_n}{x_1-x_n} + \\
       ... \\
       y_n \cdot \frac{x-x_0}{x_n-x_0} \frac{x-x_1}{x_n-x_2} ... \frac{x-x_{n-1}}{x_n-x_{n-1}} + \\
$$


# Some Common Definitions

There is no rigid standard about which kind of letters or symbols to use when discussing coding
theory, but there's a least some commonality between different text. I'll try to use them
as good as I can.

* a message 

    A message is the uncoded piece of information that need to be encoded for storage or
    transmission. A message is a sequence of symbols.

    For example, a message could be "Hello world ".

* a message word 

    A message word is a fixed length section of the overall message. Reed-Solomon 
    coding is a block coding algorithm. This means that a message is split up into multiple 
    message words, and the encoding algorithm is performed on each message word without any
    dependency on previously received message words.

    Message words are usually indicated with the letter $$m$$, and $$k$$ is often used to
    indicate the number of symbols in the message word. In other words, $$k$$ is the size 
    or the length of the message word.

    In vector notation: $$m = (m_0, m_1, ... m_{k-1})$$.

    If a message word is defined as having a size 4, the message would be split into the 
    following message words: ('H', 'e', 'l', 'l'), ('o', ' ', 'w', 'o'), ('r', 'l', 'd', ' ').

* an alphabet

    An alphabet is the set of values that can be used for each symbol of a message word. A
    message worth of length $$k$$ is a sequence of $$k$$ elements, where each element is part of the 
    alphabet.

    $$q$$ is often used as the number of elements in an alphabet.

    If we had a system where messages only consist of lower case letters and a space, then our
    alphabet would be ('a', 'b', 'c', ... , 'z', ' '), and the size of the alphabet would be 
    27.

* a code word

    A code word is what you get after you run a message word through an encoder. In the case of
    a Reed-Solomon encoder, a code word has a length $$n$$ symbols, where $$n>k$$ and the symbols
    are from the same alphabet as the message word.

    Code words are often indicate with a vector $$s = (s_0, s_1, ... , s_{n-1})$$.

    When our message of three 4-symbol messages words is converted into three 6-symbol code words, 
    it look like this:

    ('H', 'e', 'l', 'l', 'a', 'b'), ('o', ' ', 'w', 'o', 'g', 't'), ('r', 'l', 'd', ' ', 'm', 'j')

    Notice how the first 4 symbols of each code word are the same as their corresponding message word, 
    but that 2 symbols are added for error detection and correction. This makes it a 
    [systematic code](https://en.wikipedia.org/wiki/Systematic_code). As we'll soon see, not all coding 
    schemes are systematic in nature, but it's a nice property to have.

In all the examples below, we will be using an alphabet that consists of regular, unlimited range 
integers. The message words will have a length of 4, and code words will have a length 6. 
In other words: $$k=4$$ and $$n=6$$.

Using integers as symbols is a terrible choice: there is no real-world, practical encoding algorithm
that uses them. But my primary goal is to first understand how Reed-Solomon codes work fundamentally.
That's easier with integers.  Later on, we can improve the algorithm to something practical, by using an
alphabet that's a Galois field.

# Reed Solomon Encoding through Polynomial Evaluation

Reed-Solomon coding was introduced to the world by Irving S. Reed and Gustave Solomon with a
paper with the very unassuming title "Polynomial Codes over Certain Finite Fields." The
4-page paper can be [purchased](https://doi.org/10.1137/0108018) for the low price of $36.75.
You should definitely not use Google to find one of the many copies for free.

Once you understand how Reed-Solomon coding and Galois fields work, the paper is surprisingly
readable, and light on math too! But you don't even need to know Galois fields to understand 
the core idea: regular integers do the job just fine.

In the previous section, we learned that we can set up a third degree polynomial with 4 numbers: either
the 4 coefficients $$(c_0, c_1, c_2, c_3)$$, or 4 points $$f(x)$$ on the polynomial for some 
given $$x$$ values.

Once we know the coefficients, we can evaluate the polynomial at more than 4 values of $$x$$. 
Those additional points are not required to specify the polynomial, they are 
redundant, which is *exactly* what we're looking for: redundant information that allows us find the original
values in case a value gets corrupted during transmission!

And that's what Reed-Solomon encoding is all about:

**Creating redundant information by evaluating a polynomial for more $$x$$ values than is strictly necessary**.

Let's go through a concrete example where I want to setup a communication protocol to transmit information that
consists of a sequence of numbers, but where I also want to add redundancy so that the message still can be 
recovered after a corruption.

Here's one way to go about it...

**Protocol Specification**

The transmitting and receiving parties must come up with some fixed aspects of the transmission protocol.
These aspect are not message dependent and will be used for all communication between the 2 parties:

* Agree on the length of sequence. 

* Agree on the length of the message that is sent between transmitter and receiver

    This number must be larger than the length of the sequence. The longer the transmitted
    message, the more redunancy.

* Agree on how some polynomial $$f(x)$$ should be constructed.

    For the receiver, it's easiest to use the numbers of the sequence as coefficients of the polynomial!
    But that's not always the best choice. See later...

* Agree with the receiving party which values of $$x$$ to use to evaluate the polynomial $$f(x)$$.

* Agree that the message sent between transmitter and receiver are the values $$f(x)$$ for
  the numbers of $$x$$ that we agreed on in the previous step.

That's really it.


Let's apply this to an example with the following protocol settings:

* The length of the sequence with information is 4.
* We want to 2 pieces of redundancy, so the message that we'll transmit has a length of 6.
* The polynomial is always evaluated for the numbers $$(-1, 0, 1, 2, 3, 4)$$.

For a sequence of $$(2, 3, -5, 1)$$ that gives:

**Transmitter**

* Create polynomial $$f(x)=2 + 3x -5x^2 + x^3$$.

    *This is obviously the same polynomial as the one that I used for the example in the
     previous section!*

* Evaluate the polynomial $$f(x)$$ at the 6 locations: $$(-1, 7), (0,2), (1, 1), (2, -4), (3, -7), (4, -2)$$.
* Transmit the values $$f(x)$$: $$(7,2,1,-4,-7,-2)$$.

**Receiver**

The receiver, on the other hand, does the following:

* Receive the 6 values. When there was no corruption, it will receive $$(7,2,1,-4,-7,-2)$$.
* Take 4 of the 6 received values, and add their corresponding $$x$$ value. 

    For example, $$(-1, 7), (0,2), (1, 1), (2, -4)$$.

* Use these 4 points to derive the coefficients of the polynomial that was used by the transmitter,
  using Gaussian elimination.

    In the previous section, we already saw how the points $$(-1, 7), (0,2), (1, 1), (2, -4)$$
    gave back the numbers $$(2, 3, -5, 1)$$.

    With these coefficients, we've recovered the original message!

The receiver picked 4 of the 6 received values to recover the coefficients, and ignored the 2 others, 
so what was the point of sending those 2 extra? A real receiver will obviously be smarter and use
those 2 additional points to either check the integrity of the received message, or even to correct it.

Let's talk about that next...

# A Simple Error Correcting Reed Solomon Decoder

Reed-Solomon encoding is simple. Reed-Solomon decoder is harder.  In this blog post, I'll cover 
the decoding algorithm that was suggested in the original Reed-Solomon paper, because that one is 
trivially simple.

Let's first talk about how many redundant numbers are needed to correct an error:
to correct errors:

**To correct up to $$s$$ errors, you need at least $$2s$$ redundant numbers.**

In the example above, 2 additional numbers were added, which allows us to correct 1 corrupt symbol.

The original Reed-Solomon paper proposes the following algorithm: 

* from all the received numbers, go through all distinct combinations of the minimum
  required number of numbers
* for each such combination, calculate the coefficients of the polynomial
* count how many times each unique set of coefficients occurs
* the set of coefficients with the highest count will be coefficients of the polynomial
  that was used by the transmitter.

Note that this will only work as long the number of corrupted errors doesn't exceed
the maximum allowed.

Let's apply this algorithm to our example...

* We received 6 numbers and know their corresponding $$x$$ coordinate:
  $$(-1, 7), (0,2), (1, 6), (2, -4), (3, -7), (4, -2)$$.

    Notice how the third coordinate isn't $$(1, 1)$$ but $$(1, 6)$$. There was a corruption
    during transmission!

* From these 6 coordinates, we need to draw all possible combinations of 4 elements.
  Here they are:

  $$(-1, 7),(0, 2),(1, 6),(2, -4)$$

  $$(-1, 7),(0, 2),(1, 6),(3, -7)$$

  $$(-1, 7),(0, 2),(1, 6),(4, -2)$$

  $$(-1, 7),(0, 2),(2, -4),(3, -7)$$

  $$(-1, 7),(0, 2),(2, -4),(4, -2)$$

  $$(-1, 7),(0, 2),(3, -7),(4, -2)$$

  $$(-1, 7),(1, 6),(2, -4),(3, -7)$$

  $$(-1, 7),(1, 6),(2, -4),(4, -2)$$

  $$(-1, 7),(1, 6),(3, -7),(4, -2)$$

  $$(-1, 7),(2, -4),(3, -7),(4, -2)$$

  $$(0, 2),(1, 6),(2, -4),(3, -7)$$

  $$(0, 2),(1, 6),(2, -4),(4, -2)$$

  $$(0, 2),(1, 6),(3, -7),(4, -2)$$

  $$(0, 2),(2, -4),(3, -7),(4, -2)$$

  $$(1, 6),(2, -4),(3, -7),(4, -2)$$

  There are 15 combinations.

* For each of these 15 combinations, we now need to solve the set of 4 linear equations
  to obtain the 4 polynomial coefficients:

  $$(-1, 7),(0, 2),(1, 6),(2, -4) \rightarrow (2, 8, -5/2, -3/2)$$

  $$(-1, 7),(0, 2),(1, 6),(3, -7) \rightarrow (2, 27/4, -5/2, -1/4)$$

  $$(-1, 7),(0, 2),(1, 6),(4, -2) \rightarrow (2, 19/3, -5/2, 1/6)$$

  $$(-1, 7),(0, 2),(2, -4),(3, -7) \rightarrow (2, 3, -5, 1)$$

  $$(-1, 7),(0, 2),(2, -4),(4, -2) \rightarrow (2, 3, -5, 1)$$

  $$(-1, 7),(0, 2),(3, -7),(4, -2) \rightarrow (2, 3, -5, 1)$$

  $$(-1, 7),(1, 6),(2, -4),(3, -7) \rightarrow (19/2, 17/4, -10, 9/4)$$

  $$(-1, 7),(1, 6),(2, -4),(4, -2) \rightarrow (26/3, 14/3, -55/6, 11/6)$$

  $$(-1, 7),(1, 6),(3, -7),(4, -2) \rightarrow (7, 61/12, -15/2, 17/12)$$

  $$(-1, 7),(2, -4),(3, -7),(4, -2) \rightarrow (2, 3, -5, 1)$$

  $$(0, 2),(1, 6),(2, -4),(3, -7) \rightarrow (2, 18, -35/2, 7/2)$$

  $$(0, 2),(1, 6),(2, -4),(4, -2) \rightarrow (2, 49/3, -15, 8/3)$$

  $$(0, 2),(1, 6),(3, -7),(4, -2) \rightarrow (2, 13, -65/6, 11/6)$$

  $$(0, 2),(2, -4),(3, -7),(4, -2) \rightarrow (2, 3, -5, 1)$$

  $$(1, 6),(2, -4),(3, -7),(4, -2) \rightarrow (2, 3, -5, 1)$$

* The coefficients $$(2,3,-5,1)$$ comes up 6 times. All other solutions are different
  from each other, so $$(2,3,-5,1)$$ is clearly the winner, and the correct solution!

Conclusion: we have a very straightforward error correcting algorithm. However, it's not
a practical algorithm: even for this toy example with an original message length of 4 and
only 2 additional redudant symbols, we need to perform a Gaussian elimination 15 times.

In the real world, a very popular choice is to have an original message of 223 numbers, and to
add 22 redundant numbers for a total of 255.

The [formula to calculate the number of combinations](https://en.wikipedia.org/wiki/Combination) is: 

$$\frac{n!}{r!(n-r)!}$$

With $$r=223$$ and $$n=255$$, this gives a total of 50,964,019,775,576,912,153,703,782,274,307,996,667,625 combinations!

That's just not very practical...

It's clear that a much better algorithm is required to make Reed-Solomon decoding practical. Luckily,
these algorithms exists, and some of them aren't even that complicated, but that's 
worthy of a separate blog post.

# Systematic Encoding

The earlier described encoding procedure is the one that was proposed in the original
Reed-Solomon paper. Let's recap how it works:

* The incoming numbers are used to *coefficients* of a polynomial $$f(x)$$.
* The polynomial $$f(x)$$ is evaluated at a certain number of values $$x$$.
* The values $$f(x)$$ are transmitted to the received.

This encoding system works fine, but note how the transmitted values are different
than the numbers of the original message.

In our example, incoming numbers $$(2,3,-5,1)$$ are encoded as $$(7, 2, 6, -4, -7, -2)$$.

Wouldn't it be nice if we could encode our message so that the original numbers are part
of the encoded message, with some addition numbers tacked on for redunancy? In other words,
encode $$(2,3,-5,1)$$ into $$(2,3,-5,1,r_4, r_5)$$.

One of the benefits of such an encoding scheme is that you can bypass the relatively complex
decode scheme if you can show early on that the message has been received without any error.

A code with such a property is called a [systematic code](https://en.wikipedia.org/wiki/Systematic_code),
and it's easy to modify the original encoding scheme in one that's systematic by treating the
incoming numbers as values $$f(x)$$ of a polynomial.

The encoding procedure is then as follows:

* The incoming numbers are the value of the polynomial $$f(x)$$ as certain agree-upon values of $$x$$.
* Construct the coefficients of this polynomial $$f(x)$$ from the $$(x_i, f(x_i))$$ pairs.

    You can use Lagrange interpolation for this.

* Evaluate this polynomial $$f(x)$$ at as many more values of $$x$$ as the desired number of redundant values.
* Transmit the original incoming numbers and the additional values.

Let's try this out with the same number sequence as before: 

* The incoming message is $$(2,3,-5,1)$$. These are now the $$f(x)$$ values. Let's still
  use $$(-1, 0, 1, 2)$$ as corresponding $$x$$ values.
* Construct the polynomial $$f(x)$$ out of the following coordinate pairs: $$((-1, 2), (0, 3), (1, 1), (2, 1))$$.

    I found [this website](https://www.dcode.fr/lagrange-interpolating-polynomial) to do this for me.

    The result is: $$f(x) = \frac{23}{6}x^3 + \frac{9}{2}x^2 + \frac{22}{3}x^1 + 3$$

* Evaluate $$f(x)$$ for $$x$$ values $$3$$ and $$4$$ gives $$(3, 44)$$ and $$(4, 147)$$
* Transmit the encoded message $$(2,3,-5,1,44,147)$$

On the receiving end, the procedure is *exactly* the same as before. 

# A Code Word as a Sequence of Polynomial Coefficients

In the two encoding methods above, the code word, the sequence of numbers that are transmitted, consists
of evaluated values of $$f(x)$$.  There another coding variant where the encoded message are the coefficients 
of a polynomial.

These coefficients can't be just the coefficients that are formed by the incoming numbers because there
wouldn't be any redunancy in that case. So we need to come up with something. Like before, we want the encoded 
message to be systematic. This time there's a little bit of math involved, but don't worry.

* Define polynomial $$p(x)$$. Its coefficients are the incoming numbers.
* Define a so-called generator polynomial




# References

* [Introduction to Reed-Solomon](https://innovation.vivint.com/introduction-to-reed-solomon-bc264d0794f8)

    Very good explanation on polynomial based interpolation and error correction.

    * [Joseph Louis Lagrange and the Polynomials](https://medium.com/@jtolds/joseph-louis-lagrange-and-the-polynomials-499cf0742b39)

	Side story about Lagrange interpolation.

    * [infectious - RS implementation](https://pkg.go.dev/github.com/vivint/infectious)

        Code that goes with the RS article.

* [NASA - Tutorial on Reed-Solomon error correction coding](https://ntrs.nasa.gov/citations/19900019023)

    * [Actual PDF file](https://ntrs.nasa.gov/api/citations/19900019023/downloads/19900019023.pdf)

* [Reed-Solomon on Wikipedia](https://en.wikipedia.org/wiki/Reed%E2%80%93Solomon_error_correction)

* [Original paper: Polynomial Codes over Certain Finite Fields](https://faculty.math.illinois.edu/~duursma/CT/RS-1960.pdf)

    Only 4 pages!

