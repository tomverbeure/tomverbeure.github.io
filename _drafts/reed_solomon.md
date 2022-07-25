

[Nasa tutorial](https://ntrs.nasa.gov/api/citations/19900019023/downloads/19900019023.pdf)

Notes:

# Introduction

> The Reed-Solomon (RS) codes have been finding widespread applications ever since the 1977 
> Voyager's deep space communications system. At the time of Voyager's launch, efficient 
> encoders existed, but accurate decoding methods were not even available! The Jet Propulsion 
> Laboratory (JPL) scientists and engineers gambled that by the time Voyager II would reach 
> Uranus in 1986, decoding algorithms and equipment would be both available and perfected.  

# Algebraic field

* GF algebra has operations just like regular integers, but it has the huge benefit that
  the result of operations between two elements of the finite set is again an element
  of the finite set: it operates on a finite field.
* You have the ground field GF(2). GF(2) is the ground field of the extended Galois field
  GF(2^m).
* A field is a set of elements in which you can do addition, subtractions, multiplication
  and division without leaving the set. Addition and multiplication must satisfy
  commutative, associative, and distributive laws.
* The number of elements in a field is the order of the field. And if it's a finite number,
  then it's a finite field.

# Binary field

* Binary field (0,1): 
    addition -> modulo 2 addition or XOR gate
    multiplication -> module 2 multiplication or AND gate

# Extension field GF(2^m)

* A polynomial over the binary field GF(2) is a polynomial with binary coefficients.
* Each polynomial is the product of its irreducible factors
* A primitive polynomial:
    * ... is an irreducible binary polynomial of degree m  (in other word, the only factor is itself)
    * ... divides x^n+1 for n=2^m-1, but does not divide for x^i+1 for i < n
        * for example, if m=4 (GF2^4), then the primitive polynomial should divides (x^15+1)
* An extension field is created out of a primitive polynomial.

* Example primitive polynomial given. 
    * Long example that proves that the given polynomial is indeed irreducible.
        * It essentially does this by going through all possible factors and showing that
          the division with these factors is not 0.
    * Next it shows that this primitive polynomial is a factor of X^15+1

* Once you have a primitive polynomial, you can create the Galois field GF(2^m) or GF(16) (when m=4)
* Let's define each element of this field to alpha^i
    This is the alphabet of our extended Galois field.
* Our new Galois field has the following elements:
    0 (alpha^minus_infinity)   The first 2 elements, 0 and 1, are the original GF(2) element. 
    1 (alpha^0)                The remaining elements are the extension.
    alpha^1
    alpha^2
    alpha^3
    alpha^4
    ...
* Let's also define alpha^1 = alpha as a ordered set of 4 GF2 element: { 0,0,1,0 }.
  And each of those elements corresponds to the coefficients of a polynomial: 
  0 * x^3 + 0 * x^2 + 1 * x^1 + 0 * x^0 
  Note that this is just a choice. We could have defined alpha^1 as any other tuple and
  work things out from there. (See page 22.)
* So: alpha^1 = x
      alpha^2 = alpha * alpha   = x * x   = x^2 
      alpha^3 = alpha * alpha^2 = x * x^2 = x^3 
      alpha^3 = alpha * alpha^3 = x * x^3 = x^4   --> doesn't exist?
      ->  x^4 modulo primitive polynomial!
    They do this by setting the primitive polynomial to 0 and solve for X. Why???
        In any case, you can also calculate the modulo by just doing division and
        taking the remainder.
    This way, you can go all the way to alpha^14.
    At alpha^15, you get back to 1 -> wrap around.
* The GF(2^m) symbols can be written as bit vectors...
* Polynomials (with GF(2) coefficients) can also be written as bit vectors...
* Page 23: some talk about arithmetic shift when going from alpha^4 to alpha^5 etc.
  ??? I don't understand the alpha^7 case though?


Encoding methods:

* Original view: codeword as a sequence of values
    * simple encoding procedure: messages as a sequence of coefficients
    * systematic encoding procedure: message as an initial sequence of values
    * dicrete Fourier transform and its inverse
* BCH view: codeword as a sequence of coefficients
    * systematic encoding procedure

# Original Paper

* A code maps from vector space of dimension m over a finite field K (Vm(K)) to a vector
  space of a higher dimension Vn(K) with n>m. K is usually the field of 2 elements Z2.

  In this case, it's essentially a mapping of m bits to n bits.

* n-m bits are redundant, but allow to recover the original message m in case some of the
  n bits are transmitted in error.

* There exists codes with a decoding procedure so that the original message
  can be completely recovered as long a the number of error bits is smaller or equal
  than a number s, where s depends on n and m.

  A Hamming code is an example of such a code.

* Let K be a field of degree n over the field Z2, then K contains 2^n elements. 
  The multiplicative group of K is cyclic, and generated by power of alpha, where alpha
  is the root of an irreducible polynomial over Z2.

* The code E maps m-tuples of K into 2^n tuples of K.

* Let's consider a polynomial P(x) of degree m-1:

	P(x) = a0 + a1 x + a2 x^2 ... + am-1 x^(m-1)

   The coefficients are elements of field K and m < 2^n.

* The code E maps (a0, a1, ..., am-1) to 2^n tuple (P(0), P(alpha), ... , p(1))

    You convert from an m-tuple to an 2^n tuple, and you fill in each of the elements
    of field K into the polynomial and evaluate the result.

* This n-tuple can correct (2^n-m)/2 or (2^n-m-1)/2 symbols, depending on whether m is
  even or odd.

* E maps message of n * m bits to n * 2^n bits.

* The binary representation of code E usually allows the correction of more than (2^n-m-1)/2
  bits, because *all* the bits within a full symbol can be wrong, and a single symbol consists of n bits...
  Because of this, this code is particularly good at correcting errors that are strongly correlated or
  occur in bursts.

* Code E can be generalized to polynomials of the mth degree in several variables over K. When K=Z2,
  such codes reduce to Reed-Muller codes.

	XXX What does this mean?


In the original paper, input (a0, ..., am-1) is used as the polynomial. The polynomial is then
evaluated for all elements of the field. The result of this evaluation is NOT the same as the 
inputs a0 to am-1! So you need to figure out (a0, am-1) by solving m of the 2^n equations:
you take m of the received values and their corresponding field input value, then solve it.

If there were no errors, no matter which of the m received values you used will result in the
same results (a0...am-1).

If there were errors, then there won't be unanimity. As long as there weren't too many errors,
however, the correct value is the result that is most common.



# References

* [Wikipedia - Finite field arithmetic](https://en.wikipedia.org/wiki/Finite_field_arithmetic)
* [Galois Fields and Hardware Design](https://my.ece.utah.edu/~kalla/ECE6745/gf.pdf)
* [Comparison Bose-Chaudhuri-Hocquenghem BCH and Reed Solomon](https://www.itu.int/wftp3/av-arch/video-site/h261/H261_Specialists_Group/Contributions/476.pdf)
* [Wikipedia - BCH code](https://en.wikipedia.org/wiki/BCH_code)
* [NTPU - BCH Codes](https://web.ntpu.edu.tw/~yshan/BCH_code.pdf)
* [The Error Correcting Codes (ECC) Page](http://www.eccpage.com/)
