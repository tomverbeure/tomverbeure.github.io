#!/usr/bin/env python3
"""Generate a GF(2^4) power-reduction table in Markdown."""

import argparse

DEFAULT_PRIMITIVE = "0b10011"
FIELD_DEGREE = 4

def parse_bit_mask(text: str) -> int:
    """Parse a polynomial bit mask."""
    try:
        return int(text, 0)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            "primitive polynomial must be a bit mask such as 0b10011, 0x13, or 19"
        ) from error

DEFAULT_PRIMITIVE_MASK = parse_bit_mask(DEFAULT_PRIMITIVE)

def degree(poly: int) -> int:
    if poly <= 0:
        raise ValueError("zero polynomial has no degree")
    return poly.bit_length() - 1

def multiply(a: int, b: int) -> int:
    product = 0
    shift = 0
    while b:
        if b & 1:
            product ^= a << shift
        b >>= 1
        shift += 1
    return product

def reduce_mod(poly: int, primitive: int) -> int:
    primitive_degree = degree(primitive)
    while poly and degree(poly) >= primitive_degree:
        poly ^= primitive << (degree(poly) - primitive_degree)
    return poly

def format_power(exponent: int, variable: str = r"\alpha") -> str:
    if exponent == 0:
        return "1"
    if exponent == 1:
        return variable
    return rf"{variable}^{{{exponent}}}"

def format_power_label(exponent: int) -> str:
    return rf"\alpha^{{{exponent}}}"

def format_polynomial(poly: int, variable: str = r"\alpha") -> str:
    if poly == 0:
        return "0"

    terms = []
    for exponent in range(degree(poly), -1, -1):
        if poly & (1 << exponent):
            terms.append(format_power(exponent, variable))
    return " + ".join(terms)

def format_binary(poly: int) -> str:
    return f"{poly:0{FIELD_DEGREE}b}"

def substitute_alpha_with_x4(poly: int) -> int:
    substituted = 0
    for exponent in range(degree(poly), -1, -1):
        if poly & (1 << exponent):
            substituted ^= 1 << (FIELD_DEGREE * exponent)
    return substituted

def build_rows(primitive: int) -> list[list[str]]:
    rows = []
    reductions: dict[int, int] = {}

    for i in range(16):
        power = f"$${format_power_label(i)}$$"
        raw_power = 1 << i
        final = reduce_mod(raw_power, primitive)
        reductions[i] = final

        if i == 0:
            split = "1"
            substitution = "1"
            product = "1"
        elif i < FIELD_DEGREE:
            split = format_power(i)
            substitution = format_power(i)
            product = format_power(i)
        elif i == FIELD_DEGREE:
            split = format_power(i)
            substitution = format_polynomial(final)
            product = format_polynomial(final)
        else:
            previous = reductions[i - 1]
            multiplied = multiply(previous, 0b10)
            split = rf"{format_power(i - 1)} \cdot \alpha"
            substitution = rf"({format_polynomial(previous)}) \cdot \alpha"
            product = format_polynomial(multiplied)

        rows.append(
            [
                power,
                f"$${split}$$",
                f"$${substitution}$$",
                f"$${product}$$",
                f"$${format_polynomial(final)}$$",
            ]
        )

    return rows

def build_table(primitive: int) -> str:
    primitive_text = f"$${format_polynomial(primitive)}$$"
    lines = [
        f"Primitive polynomial: {primitive_text}",
        "",
        "| Power | Split | Substitute reduced factor | Multiply | $$\\pmod{f(x)}$$ |",
        "| --- | --- | --- | --- | --- |",
    ]

    for row in build_rows(primitive):
        lines.append("| " + " | ".join(row) + " |")

    return "\n".join(lines)

def build_extra_table(primitive: int) -> str:
    lines = [
        "| Power | $$\\pmod{f(x)}$$ | $$\\alpha \\to x$$ | Binary |",
        "| --- | --- | --- | --- |",
    ]

    for i in range(16):
        final = reduce_mod(1 << i, primitive)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"$${format_power_label(i)}$$",
                    f"$${format_polynomial(final)}$$",
                    f"$${format_polynomial(final, 'x')}$$",
                    format_binary(final),
                ]
            )
            + " |"
        )

    return "\n".join(lines)

def build_x4_table(primitive: int) -> str:
    lines = [
        "| Power | $$\\pmod{f(x)}$$ | $$\\alpha \\to x^4$$ | $$\\pmod{f(x)}$$ | Binary |",
        "| --- | --- | --- | --- | --- |",
    ]

    for i in range(16):
        final = reduce_mod(1 << i, primitive)
        substituted = substitute_alpha_with_x4(final)
        reduced = reduce_mod(substituted, primitive)
        lines.append(
            "| "
            + " | ".join(
                [
                    f"$${format_power_label(i)}$$",
                    f"$${format_polynomial(final)}$$",
                    f"$${format_polynomial(substituted, 'x')}$$",
                    f"$${format_polynomial(reduced, 'x')}$$",
                    format_binary(reduced),
                ]
            )
            + " |"
        )

    return "\n".join(lines)

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Generate a Markdown derivation table for powers in GF(2^4)."
    )
    parser.add_argument(
        "--primitive",
        type=parse_bit_mask,
        default=DEFAULT_PRIMITIVE_MASK,
        metavar="BIT_MASK",
        help=(
            "Primitive polynomial bit mask over GF(2). For example, "
            f"{DEFAULT_PRIMITIVE} represents x^4 + x + 1. "
            f"Default: {DEFAULT_PRIMITIVE}"
        ),
    )
    parser.add_argument(
        "--extra-table",
        action="store_true",
        help="Append a compact table with x-polynomial and binary forms.",
    )
    parser.add_argument(
        "--x4-table",
        action="store_true",
        help="Append a table that substitutes alpha with x^4 and reduces it.",
    )
    args = parser.parse_args()

    primitive = args.primitive
    if degree(primitive) != FIELD_DEGREE:
        raise SystemExit(
            f"expected a degree-{FIELD_DEGREE} primitive polynomial, "
            f"got degree {degree(primitive)}"
        )

    print(build_table(primitive))
    if args.extra_table:
        print()
        print(build_extra_table(primitive))
    if args.x4_table:
        print()
        print(build_x4_table(primitive))

if __name__ == "__main__":
    main()
