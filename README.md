# eth-checksum-address

Validate and produce [EIP-55](https://eips.ethereum.org/EIPS/eip-55) mixed-case checksum
addresses without installing anything. Keccak-256 is implemented in pure Python
(`hashlib.sha3_256` is the NIST variant and gives different results, so it can't be used here).

## Usage

```bash
python eip55.py 0x5aaeb6053f3e94c9b9a09f33669435e7ef1beaed
# 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed  no checksum (all one case)

python eip55.py 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed 0x5AAeb6053F3E94C9b9A09f33669435E7Ef1BeAed
# 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed  valid
# 0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed  INVALID checksum

cat addresses.txt | python eip55.py -
```

The exit code is `1` if any address has a bad checksum, so it can be used in CI to lint
config files that contain addresses.

## As a library

```python
from eip55 import to_checksum, checksum_status
to_checksum("0xfb6916095ca1df60bb79ce92ce3ea74c37c5d359")
```

## Tests

```bash
python -m unittest -v
```

The test suite uses the vectors from the EIP text plus known Keccak-256 digests.
