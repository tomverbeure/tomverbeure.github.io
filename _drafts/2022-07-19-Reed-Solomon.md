---
layout: post
title: Reed-Solomon Info
date:  2022-07-19 00:00:00 -1000
categories:
---

Encoding methods:

* Original view: codeword as a sequence of values
    * simple encoding procedure: messages as a sequence of coefficients
    * systematic encoding procedure: message as an initial sequence of values
    * dicrete Fourier transform and its inverse
* BCH view: codeword as a sequence of coefficients
    * systematic encoding procedure



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

