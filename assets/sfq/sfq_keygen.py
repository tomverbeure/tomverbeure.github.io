#!/usr/bin/env python3
"""Generate SFQ software-option keys from a serial number and option index."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from typing import Iterable


ROTATION_TABLE = (1, 5, 0, 3, 1, 9, 6, 2, 1, 5, 0, 3)


@dataclass(frozen=True)
class OptionInfo:
    index: int
    mask: int
    labels: tuple[str, ...]
    notes: str


OPTION_MAP = (
    OptionInfo(
        index=0,
        mask=0x001,
        labels=("SFQ-B16",),
        notes=(
            "Hardware-dependent software-option bit. The key-enable dispatch also has a "
            "Hierarchical DVB-T-specific error path for one branch using this bit."
        ),
    ),
    OptionInfo(
        index=1,
        mask=0x002,
        labels=("SFQ-B8", "SFQ-B12"),
        notes="Same software-option bit; the installed label depends on hardware/config bytes.",
    ),
    OptionInfo(
        index=2,
        mask=0x004,
        labels=("SFQ-B9", "SFQ-B13"),
        notes=(
            "Same software-option bit; hardware decides which label appears. "
            "The enable path also contains a J.83/B-specific error string."
        ),
    ),
    OptionInfo(
        index=3,
        mask=0x008,
        labels=("SFQ-B17",),
        notes=(
            "BER-related branch. The binary contains BER-specific checks and the manuals "
            "label SFQ-B17 as BER measurement."
        ),
    ),
    OptionInfo(
        index=4,
        mask=0x010,
        labels=("SFQ-B23", "SFQ-B24"),
        notes=(
            "Software-option bit used on some hardware families. Also participates in the "
            "SFQ-B25 path together with index 6."
        ),
    ),
    OptionInfo(
        index=5,
        mask=0x020,
        labels=("SFQ-B21", "SFQ-B22"),
        notes="On supported hardware, one enabled bit can cause both labels to be reported.",
    ),
    OptionInfo(
        index=6,
        mask=0x040,
        labels=("SFQ-B25",),
        notes="Hardware-dependent Turbo Coding path. The manual title names SFQ-B25 as Turbo Coding.",
    ),
    OptionInfo(
        index=7,
        mask=0x080,
        labels=("SFQ-B27",),
        notes="Hardware-dependent Impulsive Noise path. The manual title names SFQ-B27 as Impulsive Noise.",
    ),
    OptionInfo(
        index=8,
        mask=0x100,
        labels=("SFQ-B28",),
        notes="Uses the ninth software-option bit in the second mask byte.",
    ),
)

NON_KEYED_LABELS = (
    "SFQ-B2",
    "SFQ-B3",
    "SFQ-B4",
    "SFQ-B5",
    "SFQ-B6",
    "SFQ-B10",
    "SFQ-B11",
    "SFQ-B15",
    "SFQ-B26",
    "SFQCSPL",
)


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


def format_option_map() -> str:
    lines = [
        "Recovered software-option map:",
        "  These are the 9 key-generatable option indices handled by the recovered 13-digit key path.",
        "  SFQ-B12 and higher are not separate indices; the binary reports them from the same 9-bit",
        "  software-option mask after additional hardware/config checks.",
        "",
    ]

    for info in OPTION_MAP:
        labels = ", ".join(info.labels)
        lines.append(
            f"  {info.index}: mask=0x{info.mask:03x}  labels={labels}  note={info.notes}"
        )

    lines.extend(
        (
            "",
            "Other labels seen in the installed-option/status code, but not tied to a distinct",
            "software-option key index in the recovered key path:",
            f"  {', '.join(NON_KEYED_LABELS)}",
        )
    )
    return "\n".join(lines)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Generate SFQ software-option keys from a serial number and option index. "
            "Use --list-options to print the recovered option mapping."
        )
    )
    parser.add_argument(
        "serial",
        type=parse_serial,
        nargs="?",
        help="instrument serial as 9 digits, for example 123456789 or 123456/789",
    )
    parser.add_argument(
        "option_index",
        type=parse_option,
        nargs="?",
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
    parser.add_argument(
        "--list-options",
        action="store_true",
        help="print the recovered software-option mapping and exit",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()

    if args.list_options:
        print(format_option_map())
        return 0

    if args.serial is None or args.option_index is None:
        raise SystemExit("serial and option_index are required unless --list-options is used")

    for key in iter_keys(args.serial, args.option_index, args.mode, args.tail):
        if args.verify:
            payload = decode_key(args.serial, key)
            print(f"{key}  payload={payload}")
        else:
            print(key)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
