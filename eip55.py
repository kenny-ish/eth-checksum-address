"""EIP-55 checksum addresses."""
import argparse
import re
import string
import sys
from pathlib import Path

from keccak import keccak256

_HEX40 = re.compile(r"^(0x)?[0-9a-fA-F]{40}$")
# 0x + 40 hex digits not glued to other letters or digits (so 32-byte hashes don't match)
_IN_TEXT = re.compile(r"(?<![0-9A-Za-z])0x[0-9a-fA-F]{40}(?![0-9A-Za-z])")
LABELS = {"valid": "valid", "unchecked": "no checksum (all one case)", "invalid": "INVALID checksum"}


class AddressError(ValueError):
    """Raised by normalize() with a message that says what is wrong with the input."""


def to_checksum(address: str) -> str:
    """Return the EIP-55 mixed-case form of a 20-byte hex address (with or without 0x)."""
    if not _HEX40.match(address):
        raise ValueError(f"not a 20-byte hex address: {address!r}")
    addr = address.lower().removeprefix("0x")
    digest = keccak256(addr.encode("ascii")).hex()
    out = [ch.upper() if int(digest[i], 16) >= 8 else ch for i, ch in enumerate(addr)]
    return "0x" + "".join(out)


def checksum_status(address: str) -> str:
    """Return 'valid', 'unchecked' or 'invalid'.

    'valid' means the casing matches the checksum, including the rare addresses whose checksum
    is all upper or all lower case. 'unchecked' is a single-case address that doesn't match,
    i.e. one that carries no checksum.
    """
    if not _HEX40.match(address):
        return "invalid"
    body = address.removeprefix("0x")
    if to_checksum(address) == "0x" + body:
        return "valid"
    if body == body.lower() or body == body.upper():
        return "unchecked"
    return "invalid"


def _problem(value) -> str:
    """Why value is not a usable address, or '' if it is."""
    if not isinstance(value, str):
        return f"expected str, got {type(value).__name__}"
    if not value.startswith("0x"):
        return "missing 0x prefix"
    body = value[2:]
    bad = next((i for i, ch in enumerate(body) if ch not in string.hexdigits), None)
    if bad is not None:
        return f"non-hex character {body[bad]!r} at position {bad + 2}"
    if len(body) != 40:
        return f"expected 40 hex digits, got {len(body)}"
    if checksum_status(value) == "invalid":
        return "mixed-case address with a bad EIP-55 checksum"
    return ""


def is_address(value) -> bool:
    """0x-prefixed, 40 hex digits, and a correct checksum if the casing is mixed."""
    return _problem(value) == ""


def is_checksum_address(value) -> bool:
    """Exactly the EIP-55 form of an address."""
    return is_address(value) and to_checksum(value) == value


def normalize(value) -> str:
    """Strip surrounding whitespace, validate, and return the checksummed address.

    Raises AddressError with the reason. A mistyped mixed-case address is an error, never
    silently re-cased: fixing the casing would hide the typo the checksum just caught.
    """
    if isinstance(value, str):
        value = value.strip()
    problem = _problem(value)
    if problem:
        raise AddressError(f"{problem}: {value!r}")
    return to_checksum(value)


def scan(text: str):
    """Yield (line, column, address, status) for every address found in text."""
    for number, line in enumerate(text.splitlines(), 1):
        for m in _IN_TEXT.finditer(line):
            yield number, m.start() + 1, m.group(), checksum_status(m.group())


def scan_files(paths, strict: bool) -> int:
    checked = problems = 0
    for path in paths:
        try:
            text = Path(path).read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            print(f"{path}: {e.strerror}")
            problems += 1
            continue
        for line, col, address, status in scan(text):
            checked += 1
            if status == "invalid" or (strict and status == "unchecked"):
                problems += 1
                print(f"{path}:{line}:{col}  {LABELS[status]}  {address}")
    print(f"{checked} address(es) checked, {problems} problem(s)")
    return 1 if problems else 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Check and produce EIP-55 checksum addresses")
    ap.add_argument("items", nargs="+", help="addresses, - to read addresses from stdin, or files with --scan")
    ap.add_argument("--scan", action="store_true", help="treat the arguments as files and check every address in them")
    ap.add_argument("--strict", action="store_true", help="also fail on single-case addresses that carry no checksum")
    args = ap.parse_args(argv)
    if args.scan:
        return scan_files(args.items, args.strict)

    items = args.items
    if items == ["-"]:
        items = [line.strip() for line in sys.stdin if line.strip()]
    bad = 0
    for a in items:
        if not _HEX40.match(a):
            print(f"{a}  not an address")
            bad += 1
            continue
        status = checksum_status(a)
        bad += status == "invalid" or (args.strict and status == "unchecked")
        print(f"{to_checksum(a)}  {LABELS[status]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
