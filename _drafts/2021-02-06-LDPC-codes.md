

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
