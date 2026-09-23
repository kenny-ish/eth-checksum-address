"""EIP-55 checksum addresses."""
import argparse
import re
import sys

from keccak import keccak256

_HEX40 = re.compile(r"^(0x)?[0-9a-fA-F]{40}$")


def to_checksum(address: str) -> str:
    if not _HEX40.match(address):
        raise ValueError(f"not a 20-byte hex address: {address!r}")
    addr = address.lower().removeprefix("0x")
    digest = keccak256(addr.encode("ascii")).hex()
    out = [ch.upper() if int(digest[i], 16) >= 8 else ch for i, ch in enumerate(addr)]
    return "0x" + "".join(out)


def checksum_status(address: str) -> str:
    """Return 'valid', 'unchecked' (single case, no checksum) or 'invalid'."""
    body = address.removeprefix("0x")
    if not _HEX40.match(address):
        return "invalid"
    if body == body.lower() or body == body.upper():
        return "unchecked"
    return "valid" if to_checksum(address) == "0x" + body else "invalid"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("addresses", nargs="+", help="addresses, or - to read stdin")
    args = ap.parse_args()

    items = args.addresses
    if items == ["-"]:
        items = [line.strip() for line in sys.stdin if line.strip()]

    labels = {"valid": "valid", "unchecked": "no checksum (all one case)",
              "invalid": "INVALID checksum"}
    bad = 0
    for a in items:
        if not _HEX40.match(a):
            print(f"{a}  not an address")
            bad += 1
            continue
        status = checksum_status(a)
        bad += status == "invalid"
        print(f"{to_checksum(a)}  {labels[status]}")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
