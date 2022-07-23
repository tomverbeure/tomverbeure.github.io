---
layout: post
title: Reed-Solomon Info
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
didn't know what they do, and there have been cases where I've even worked with them 
professionally, but I felt that I never quite understood the basics, the theory, on
which these techniques are based.

One coding technique that I found particularly obscure was Reed-Solomon-based forward
error correction. It's not for lack of material on the web, because it's covered in many
college-level courses on coding and signal processing techniques. But a lot of that material
assumes a certain theoretical base and builds on that. They'll start with Galois
Fields and polynomials, throw a bunch of mathematical formulas at you, and you're left
with very little intuitive understanding.

That changed when stumbled into this 
[Introduction to Reed-Solomon](https://innovation.vivint.com/introduction-to-reed-solomon-bc264d0794f8)
article. It explains how polynomials and polynomial evaluation at certain points create a way to
create a code with redundancy, and how to recover the original message back from it. The article
is excellent, and it makes a lot of what I'll be covering below unnecessary. Because a major
part of what follows will be a recreation of that material... but dumbed down even more, and with
more examples too.

However, there's more to Reed-Solomon coding than what's covered in that single article: instead
of traditional integer math, a real system will use operation within a Galois Field. And even though 
all Reed-Solomon coding techniques are based on the same idea, there are subtle theoretical variations.
There's also the matter of implementing things in software or hardware. The topic is huge, and there's
probably still research on-going.

My common disclaimer applies: I'm writing these blog posts primarily for myself, as a way to solidify
what I've learned after reading stuff on the web. 

# A Quick Recap on Polynomials 

It's impossible to discuss anything that's related to coding without touching the subject of polynomials.
I'm assume that you've learned about integer based polynomials during some algebra class in high school
or in college. A polynomial f(x) of degree n is a function that looks like this:

$$f(x) = c_0 + c_1 x + c_2 x^2 + ... c_n x^n$$

$$n+1$$ fixed coefficients $$c_i$$ are multiplied by function variable $$x$$ to the power of $$i$$. 
The polynomial is evaluated by replacing variable $$x$$ by some number for which you want to know the 
value of the function.

Let's make things a bit more concrete by using actual examples:

$$\begin{aligned}
f(x) & = 3 + 2 x + 5 x^2 - 4 x^3 \\
g(x) & = 7 x - x^2 \\
\end{aligned}$$

If you have multiple polynomials, you can do operations such as adding them together. You do this
by adding together the coefficients that belong to $$x$$ with the same exponent:

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
multiplication. We'll get to that later...

# Minimum Information to Define a Polynomial

Here's one the most important characteristics of polynomials:

**Any polynomial function of degree $$n-1$$ is uniquely defined by any $$n$$ points that 
lay on this function.**

Being uniquely defined means that it goes both ways: 

* I can give you the $$n$$ coefficients $$c_0$$ to $$c_{n-1}$$ of $$f(x)$$, and you can evaluate the function value by filling in 
any $$x$$ coordinate you want, and thus also the function values for $$n$$ specific $$x$$ input values.

* Or, the other way around, I can give you the value $$f(x)$$ of any $$n$$ values of $$x$$ and 
you can derive the $$n$$ coefficients $$c_0$$ to $$c_{n-1}$$ of $$f(x)$$. 

Here's an example of a degree 3 function, $$f(x)=2 + 3x -5x^2 + x^3$$, evaluated for $$x$$ value of $$-1,0,1,2$$:

<img src="/assets/reed_solomon/desmos-graph-1.png" alt="f(x) graph, annotated with points -1,0,1,2" width="80%"/>

*I used the excellent [desmos graphing calculator](https://www.desmos.com/calculator) to create this
function plots.*

When given the points $$(-1, 7), (0,2), (1, 1), (2, -4)$$, we can set up an equation for each of those
4 points, which results in a set of linear equations with 4 unknowns:

$$
c_0 + c_1 (-1)^1 + c_2 (-1)^2 + c_3 (-1)^3 = -7 \\
c_0 + c_1 (0)^1 + c_2 (0)^2 + c_3 (0)^3 = 2 \\
c_0 + c_1 (1)^1 + c_2 (1)^2 + c_3 (1)^3 = 1 \\
c_0 + c_1 (2)^1 + c_2 (2)^2 + c_3 (2)^3 = -4 \\
$$

Such a set of equations can be with the standard 
[Gaussian elimination algorithm](https://en.wikipedia.org/wiki/Gaussian_elimination). 
In our case, the values are such that we can solve it using a less systematic method:

The second row immediately reduces to $$\bf{c_0 = 2}$$. When we fill that back in, the remaining
rows become:

$$
-c_1 + c_2 - c_3 = -9 \\
c_1 + c_2 + c_3 = -1 \\
2 c_1  + 4 c_2  + 8 c_3  = -6 \\
$$

If we add the first and second row, we get: $$2c_2 = -10$$, or $$\bf{c_2=-5}$$.

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

# Reed Solomon Encoding is Polynomial Evaluation

Reed-Solomon coding was introduced to the world by Irving S. Reed and Gustave Solomon with a
paper with the very unassuming title "Polynomial Codes over Certain Finite Fields." The
4-page paper can be [purchased](https://doi.org/10.1137/0108018) for the low price of $36.75.
You should definitely not use Google to find one of the many copies for free.

Once you understand how Reed-Solomon coding and Galois fields work, the paper is surprisingly
readable, and light on math too! But it turns out that you don't even need to know
Galois fields to understand the core idea, so let's use integers for now and so where
that gets us.

Staying with the earlier example, we now know that we can set up a polynomial with 4 numbers: either
the 4 coefficients $$(c_0, c_1, c_2, c_3)$$, or with 4 points $$f(x)$$ on the polynomial for some 
given $$x$$ values.

Once we have determined the coefficients, we can now easily evaluate the polynomial at more
than 4 values of $$x$$. Those additional points are not required to specify the polynomial, they are 
redundant, which is *exactly* what we're looking for: redundant information that allows us find the original
values in case a value gets corrupted during transmission!

And that's what Reed-Solomon encoding is all about:

**Creating redundant information by evaluating a polynomial for more $$x$$ values than is strictly necessary**.

Let's go through a concrete example where I want to setup a communication protocol to transmit information that
consists of a sequence of numbers, but where I also want to add redundancy so that the message still can be 
recovered after a corruption.

Here's one way to go about it...

**Protocol Specification**

First the transmitting and receiving parties must come up with some fixed aspects of the transmission protocol.
These aspect are not message dependent and will be used for all communication between the 2 parties:

* Agree on the length of sequence. 

* Agree on the length of the message that is sent between transmitter and receiver

    This number must be larger than the length of the sequence. The longer the transmitted
    message, the more redunancy.

* Agree on how the polynomial $$f(x)$$ should be constructed.

    For the receiver, it's easiest to use the numbers of the sequence as coefficients of the polynomial!
    But that's not always the best choice. See later...

* Agree with the receiving party which values of $$x$$ to use to evalute the polynomial $$f(x)$$.

* Agree that the message sent between transmitter and receiver are the values $$f(x)$$ for
  the numbers of $$x$$ that we agreed on in the previous step.

That's really it.


Let's apply this to an example with the following protocol settings:

* The length of the sequence with information is 4.
* We want to 2 pieces of redundancy, so the message that we'll transmit has a length of 6.
* The polynomial is alwasy evaluated for the numbers $$(-1, 0, 1, 2, 3, 4)$$.

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
so what's the point of sending those 2 extra? A real receiver will obviously be smarter and use
those 2 additional points to either check the integrity of the received message, or even to correct it.

Let's talk about that next...

# A Simple Error Correcting Reed Solomon Decoder

Reed-Solomon encoding is simple. A good Reed-Solomon decoder is hard. But that's for
another time. In this blog post, I'll cover the decoding algorithm that was suggested in the original
Reed-Solomon paper, because that one is trivially simple.

Let's first talk about how many redundant numbers are needed to detect errors, and
to correct errors:

* to detect up to $$s$$ errors, you need at least $$s$$ additional numbers
* to correct up to $$s$$ errors, you need at least $$2s$$ additional numbers

In the example above, 2 additional number were added, which allows us to correct 1 corrupt symbol.

The original Reed-Solomon paper proposes the following algorithm: 

* from all the received numbers, go through all distinct combinations of the minimum
  required number of numbers
* for each such combination, calculate the coefficients of the polynomial
* count how many times each unique set of coefficients occurs
* the set with the highest count will be original coefficients

Note that this will only work as long the number of corrupted errors doesn't exceed
the maximum allowed.

Let's apply this algorithm to our example...

* We received 6 numbers and know their corresponding $$x$$ coordinate:
  $$(-1, 7), (0,2), (1, 6), (2, -4), (3, -7), (4, -2)$$.

    Notice how the third coordinate isn't $$(1, 1)$$ but $$(1, 6)$$. We have a corruption!

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

  There's 15 such combinations.

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

# A Story about the Voyager Spacecrafts

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

