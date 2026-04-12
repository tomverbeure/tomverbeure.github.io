#!/usr/bin/env python3
"""Generate SFQ software-option keys from a serial number and option index."""

from __future__ import annotations

import argparse
from typing import Iterable


ROTATION_TABLE = (1, 5, 0, 3, 1, 9, 6, 2, 1, 5, 0, 3)


def parse_serial(text: str) -> int:
    digits = text.replace("/", "").strip()
    if not digits.isdigit():
        raise argparse.ArgumentTypeError(
            "serial must contain only digits, optionally with a single slash"
        )
    if len(digits) != 9:
        raise argparse.ArgumentTypeError(
            "serial must have 9 digits, for example 123456789 or 123456/789"
        )
    return int(digits)


def parse_option(text: str) -> int:
    value = int(text, 10)
    if not 0 <= value <= 8:
        raise argparse.ArgumentTypeError("option index must be between 0 and 8")
    return value


def parse_mode(text: str) -> int:
    value = int(text, 10)
    if not 0 <= value <= 2:
        raise argparse.ArgumentTypeError("mode must be 0, 1, or 2")
    return value


def parse_tail(text: str) -> int:
    value = int(text, 10)
    if not 0 <= value <= 9:
        raise argparse.ArgumentTypeError("tail digit must be between 0 and 9")
    return value


def canonical_payload(serial9: int, option_index: int, mode: int) -> str:
    return f"0{option_index}{mode}{serial9:09d}"


def make_key(serial9: int, option_index: int, mode: int = 1, tail_digit: int = 0) -> str:
    payload = canonical_payload(serial9, option_index, mode)
    rotation = ((serial9 % 10) + tail_digit) % 12

    encoded = []
    for idx, bias in enumerate(ROTATION_TABLE):
        digit = int(payload[(idx + rotation) % 12])
        encoded.append(str((digit + bias) % 10))

    return "".join(encoded) + str(tail_digit)


def decode_key(serial9: int, key: str) -> str:
    if len(key) != 13 or not key.isdigit():
        raise ValueError("key must be exactly 13 decimal digits")

    rotation = ((serial9 % 10) + int(key[12])) % 12
    decoded = [(int(ch) - bias) % 10 for ch, bias in zip(key[:12], ROTATION_TABLE)]
    return "".join(str(decoded[(idx - rotation) % 12]) for idx in range(12))


def iter_keys(serial9: int, option_index: int, mode: int, tail_digit: int | None) -> Iterable[str]:
    if tail_digit is not None:
        yield make_key(serial9, option_index, mode, tail_digit)
        return

    for digit in range(10):
        yield make_key(serial9, option_index, mode, digit)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate SFQ software-option keys from a serial number and option index."
    )
    parser.add_argument(
        "serial",
        type=parse_serial,
        help="instrument serial as 9 digits, for example 123456789 or 123456/789",
    )
    parser.add_argument(
        "option_index",
        type=parse_option,
        help="software option index from 0 to 8",
    )
    parser.add_argument(
        "--mode",
        type=parse_mode,
        default=1,
        help="key mode digit, usually 1",
    )
    parser.add_argument(
        "--tail",
        type=parse_tail,
        help="last key digit; if omitted, print all 10 valid variants",
    )
    parser.add_argument(
        "--verify",
        action="store_true",
        help="also print the decoded payload for each generated key",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    for key in iter_keys(args.serial, args.option_index, args.mode, args.tail):
        if args.verify:
            payload = decode_key(args.serial, key)
            print(f"{key}  payload={payload}")
        else:
            print(key)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
