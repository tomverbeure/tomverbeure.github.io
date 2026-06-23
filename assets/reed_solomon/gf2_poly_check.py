#!/usr/bin/env python3
"""Check whether a GF(2) polynomial is irreducible or primitive."""

import argparse

X = 0b10

def parse_poly_mask(text):
    value = text.lower()
    if not (value.startswith("0b") or value.startswith("0x")):
        raise argparse.ArgumentTypeError("polynomial must be binary or hex, such as 0b10011 or 0x13")
    try:
        return int(value, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError("invalid polynomial bit mask") from error

def degree(poly):
    if poly <= 0:
        raise ValueError("zero polynomial has no degree")
    return poly.bit_length() - 1

def multiply(a, b):
    product = 0
    shift = 0
    while b:
        if b & 1:
            product ^= a << shift
        b >>= 1
        shift += 1
    return product

def divmod_poly(dividend, divisor):
    quotient = 0
    remainder = dividend
    divisor_degree = degree(divisor)
    while remainder and degree(remainder) >= divisor_degree:
        shift = degree(remainder) - divisor_degree
        quotient ^= 1 << shift
        remainder ^= divisor << shift
    return quotient, remainder

def reduce_mod(poly, modulus):
    return divmod_poly(poly, modulus)[1]

def multiply_mod(a, b, modulus):
    return reduce_mod(multiply(a, b), modulus)

def pow_mod(base, exponent, modulus):
    result = 1
    value = reduce_mod(base, modulus)
    while exponent:
        if exponent & 1:
            result = multiply_mod(result, value, modulus)
        value = multiply_mod(value, value, modulus)
        exponent >>= 1
    return result

def gcd_poly(a, b):
    while b:
        a, b = b, reduce_mod(a, b)
    return a

def prime_factors(value):
    factors = []
    divisor = 2
    while divisor * divisor <= value:
        if value % divisor == 0:
            factors.append(divisor)
            while value % divisor == 0:
                value //= divisor
        divisor += 1 if divisor == 2 else 2
    if value > 1:
        factors.append(value)
    return factors

def format_polynomial(poly):
    terms = []
    for exponent in range(degree(poly), -1, -1):
        if not (poly & (1 << exponent)):
            continue
        if exponent == 0:
            terms.append("1")
        elif exponent == 1:
            terms.append("x")
        else:
            terms.append(f"x^{exponent}")
    return " + ".join(terms)

def is_irreducible(poly):
    n = degree(poly)
    if n == 0:
        return False
    if n == 1:
        return True
    if not (poly & 1):
        return False

    for factor in prime_factors(n):
        exponent = 1 << (n // factor)
        test_poly = pow_mod(X, exponent, poly) ^ X
        if gcd_poly(poly, test_poly) != 1:
            return False

    return pow_mod(X, 1 << n, poly) == X

def is_primitive(poly):
    n = degree(poly)
    if not is_irreducible(poly):
        return False

    order = (1 << n) - 1
    for factor in prime_factors(order):
        if pow_mod(X, order // factor, poly) == 1:
            return False
    return pow_mod(X, order, poly) == 1

def main():
    parser = argparse.ArgumentParser(
        description="Check whether a GF(2) polynomial is irreducible or primitive."
    )
    parser.add_argument("poly", type=parse_poly_mask, help="Polynomial bit mask, such as 0b10011 or 0x13.")
    args = parser.parse_args()

    poly = args.poly
    print(f"Polynomial mask: {poly:#b} / {poly:#x}")
    print(f"Polynomial: {format_polynomial(poly)}")
    print(f"Degree: {degree(poly)}")
    print(f"Irreducible: {is_irreducible(poly)}")
    print(f"Primitive: {is_primitive(poly)}")

if __name__ == "__main__":
    main()
