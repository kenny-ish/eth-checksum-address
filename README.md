# eth-checksum-address

[![CI](https://github.com/kenny-ish/eth-checksum-address/actions/workflows/ci.yml/badge.svg)](https://github.com/kenny-ish/eth-checksum-address/actions/workflows/ci.yml)

Validates and produces [EIP-55](https://eips.ethereum.org/EIPS/eip-55) mixed-case checksum
addresses. Keccak-256 is implemented in pure Python, so there are no dependencies.

## How EIP-55 works

Write the address as 40 lowercase hex characters and hash that ASCII string with Keccak-256.
Then walk the address: every letter (a-f) whose hex digit at the same position in the hash is 8
or higher is written in upper case. The casing carries about 15 check bits on average, so a
mistyped address almost never passes.

## Install

```bash
pip install git+https://github.com/kenny-ish/eth-checksum-address
```

Requires Python 3.10 or newer.

## Command line

```bash
$ eip55 0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2
0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2  no checksum (all one case)
$ eip55 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 0xc02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2  valid
0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2  INVALID checksum
$ cat addresses.txt | eip55 -
```

The address is WETH on Ethereum mainnet. The second address in the second call has one letter's
case flipped. The exit code is `1` if any address has a bad checksum, so the tool can guard config
files in CI. `python eip55.py ...` works without installing.

## Library

```python
from eip55 import checksum_status, to_checksum

to_checksum("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")
# '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
checksum_status("0x52908400098527886E0F7030069857D2E4169EE7")
# 'valid': this address's checksum happens to be all upper case
```

`checksum_status` returns `valid`, `unchecked` (a single-case address that carries no checksum)
or `invalid`.

## Tests

```bash
python -m unittest -v
```

The suite covers all eight test vectors from the EIP, including the all-caps and all-lowercase
ones, and known Keccak-256 digests. Release notes are in [CHANGELOG.md](CHANGELOG.md).
