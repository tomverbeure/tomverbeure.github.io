---
layout: post
title: BCH Coding
date:   2022-05-07 00:00:00 -1000
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
<script src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.1/MathJax.js?config=TeX-AMS_HTML" type="text/javascript"></script>

* [Introduction](#introduction)

# Finite Field

In mathematics, a [field](https://en.wikipedia.org/wiki/Field_(mathematics)) is a set on which the operations of 
multiplication, addition, subtraction and division are defined and satisfy certain basic rules.

A [finite field](https://en.wikipedia.org/wiki/Finite_field) or Galois Field is a field where that set is finite number of elements. 

The most common example of a finite field are integers mod *p*, where *p* is a prime number.

The number of elements of a finite field is called the *order* or its *size*.

A finite field of order *q* exists if and only if the order *q* is a prime power *p*^*k*, where *p* is a prime and *k* is a positive integer.

# Hamming Code

[Hamming code on Wikipedia](https://en.wikipedia.org/wiki/Hamming_code)

Copied from [Error Detect and Correction Using the BCH Code](https://aqdi.com/wordpress/wp-content/uploads/2015/12/bch.pdf)

* Block length: $$n=2^m-1$$
* Information bits: $$k=2^m-m-1$$ or $$k=n-m$$
* Parity check bits: $$n-k=m$$
* Correctable errors: $$t=1$$
* Distance between code: 3
* Perfect code: all code words, even the incorrect ones, are located inside a sphere that
  has the valid code word at the center. There are no invalid code words that are located
  outside the sphere. 



| **m** | **n** | **k** | **t** | **Notation**      | **Efficiency** |
|-------|-------|-------|-------|-------------------|----------------|
| 2     | 3     | 1     | 1     | $$[3,1,3]_2$$     | 33%            |
| 3     | 7     | 4     | 1     | $$[7,4,3]_2$$     | 57%            |
| 4     | 15    | 11    | 1     | $$[15,11,3]_2$$   | 73%            |
| 5     | 31    | 26    | 1     | $$[31,26,3]_2$$   | 84%            |
| 6     | 63    | 56    | 1     | $$[63,56,3]_2$$   | 89%            |
| 7     | 127   | 120   | 1     | $$[127,120,3]_2$$ | 94%            |
| 8     | 255   | 247   | 1     | $$[255,247,3]_2$$ | 97%            |

# Golay Code

[Golay code on Wikipedia](https://en.wikipedia.org/wiki/Binary_Golay_code)

Only 2 versions.

* Block length: $$n=23$$ or $$n=24$$
* Information bits: $$k=12$$
* Parity check bits: 11 or 12
* Distance between codes: 7 or 8
* The 23 bit version is a perfect code.


# BCH Code

[BCH code on Wikipedia](https://en.wikipedia.org/wiki/BCH_code)

* Block length: $$n=2^m-1$$
* Partiy check bits: $$n-k \le mt$$
* Minimum distance: $$d \ge 2t+1$$

with $$m \ge 3$$ and $$t < 2^{m-1}$$


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

Galois Field multiplication implementation: LFSR. It's essentially doing the multiplication by doing
additions sequentially.


# Resources

* [Galois LFSR](https://www.nayuki.io/page/galois-linear-feedback-shift-register)

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

# Reed-Solomon

* [Practical Reed-Solomon for Programmers](https://berthub.eu/articles/posts/reed-solomon-for-programmers/)
* [Introduction to Reed-Solomon](https://innovation.vivint.com/introduction-to-reed-solomon-bc264d0794f8)

    Good explanation, very light on math.

* [BBC R&D White Paper: Reed-Solomon error correction](https://downloads.bbc.co.uk/rd/pubs/whp/whp-pdf-files/WHP031.pdf)

    Describes mathematics and algorithms for coding and encoding, and how to implement it with logic
    circuits.

* [Parallel Multiplier Designs for the Galois/Counter Mode of Operation](https://uwspace.uwaterloo.ca/bitstream/handle/10012/3789/Final%20Thesis%20-%20Pujan%20Patel.pdf?sequence=1)

* [Reed-Solomon error-correcting code decoder](https://www.nayuki.io/page/reed-solomon-error-correcting-code-decoder)

    Mathematics explained in function of implementing it in code (Java, Python)

* [The mathematics of RAID-d6](https://mirrors.edge.kernel.org/pub/linux/kernel/people/hpa/raid6.pdf)
* [The RAID-6 Liberation Codes](https://www.usenix.org/legacy/event/fast08/tech/full_papers/plank/plank_html/index.html) 

* [Hamsterworks HDMI header error correction](https://web.archive.org/web/20191021164243/http://hamsterworks.co.nz/mediawiki/index.php/HDMI_header_error_correction)

    * [local copy](/assets/bch/HDMI_header_correction_Hamsterworks.html)

    * [HDMI header ECC tweet with code](https://twitter.com/field_hamster/status/1010141225121267713)
    * ![HDMI ECC code](/assets/bch/hdmi_ECC.jpg)
    * ![HDMI ECC encoder](/assets/bch/HDMI_BCC_encoder.png)

* [Comparision Bose-Chaudhuri-Hocquenghem BCH and Reed Solomon](https://www.itu.int/wftp3/av-arch/video-site/h261/H261_Specialists_Group/Contributions/476.pdf)

    Interesting apples-to-apples comparison between BCH and RS. It also shows how that
    you can do either burst or non-burst correction with BCH codes.

* [Error Detection and Correction Using the BCH Code](https://aqdi.com/wordpress/wp-content/uploads/2015/12/bch.pdf)

    Long-winded introduction about coding in general, but 

* [Did the Voyager spacecraft use a Golay, a Reed-Solomon and/or a Hamming code for data transmission encoding for error correction?](https://space.stackexchange.com/questions/54055/did-the-voyager-spacecraft-use-a-golay-a-reed-solomon-and-or-a-hamming-code-for)

* [Channel Coding: The Road to Channel Capacity](https://arxiv.org/abs/cs/0611112)

    Fantastic paper about the history and evolution of coding

* [Binary BCH (15,7,5) work out](http://souktha.github.io/misc/bch15_7_5/)

* [Trivialize Linear Recurrence Problems with Berlekamp-Massey!](https://mzhang2021.github.io/cp-blog/berlekamp-massey/)

    Excellent step-by-step explanation.
