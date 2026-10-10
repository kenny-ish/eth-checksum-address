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
from eip55 import is_address, is_checksum_address, normalize, to_checksum

normalize("  0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2\n")
# '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2'
is_checksum_address("0x52908400098527886E0F7030069857D2E4169EE7")
# True: this address's checksum happens to be all upper case
normalize("0xc02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2")
# AddressError: mixed-case address with a bad EIP-55 checksum: '0xc02a...'
```

| function | returns |
|---|---|
| `to_checksum(addr)` | the EIP-55 form (accepts any casing, with or without `0x`) |
| `checksum_status(addr)` | `valid`, `unchecked` (single case, no checksum) or `invalid` |
| `is_address(value)` | `0x` + 40 hex digits, and a correct checksum if mixed case |
| `is_checksum_address(value)` | exactly the EIP-55 form |
| `normalize(value)` | the EIP-55 form, or `AddressError` saying what is wrong |

`normalize` doesn't re-case a mixed-case address with a bad checksum, since that would hide the
typo the checksum caught.

## Keccak-256 is not hashlib.sha3_256

Ethereum adopted Keccak before NIST finished standardizing it as SHA-3. The final FIPS 202
standard changed one thing: the first padding byte, `0x01` in Keccak and `0x06` in SHA-3. The
permutation is identical, but every digest differs:

```
keccak256(b"")        c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470
hashlib.sha3_256(b"") a7ffc6f8bf1ed76651c14756a061d662f580ff4de43b49fa82d80a4b80f8434a
```

So `hashlib.sha3_256` can't be used for Ethereum hashes. The tests use that difference as a
cross-check: running this module's sponge with padding `0x06` must reproduce `hashlib.sha3_256`
exactly, which verifies the permutation against an independent implementation.

## Security considerations

- Per the EIP, a mistyped address passes the check with a probability of about 0.0247%. The
  checksum protects against typos and copy errors and does nothing against a deliberate attack.
- A valid checksum doesn't mean it's the address you meant. Address-poisoning attacks send dust
  from addresses that share the first and last characters of one you use, hoping you copy the
  wrong one from your history. Those addresses have valid checksums, so compare the whole address.
- An address written in a single case usually carries no checksum. `unchecked` means there was
  nothing to verify, and a UI should say that instead of showing the address as valid.
- EIP-1191 checksums (RSK and a few other chains) mix the chain id into the hash, so those
  addresses show as `invalid` here even when they are correct for their chain.
- The pure-Python Keccak is not constant-time. That's fine for public data such as addresses, but
  don't use it to hash secrets.

## Tests

```bash
python -m unittest -v
```

The suite covers all eight test vectors from the EIP, including the all-caps and all-lowercase
ones, known Keccak-256 digests, and the SHA3-256 cross-check. Release notes are in
[CHANGELOG.md](CHANGELOG.md).
