# Changelog

All notable changes to this project are documented in this file.

## 0.2.0 - 2026-10-10

- `is_address`, `is_checksum_address` and `normalize`; `normalize` raises `AddressError` (a `ValueError`) saying what is wrong with the input
- Keccak tests cross-check the permutation against `hashlib.sha3_256` by switching the padding byte (Keccak-256 and SHA3-256 differ only there)
- README: why `hashlib.sha3_256` gives different hashes, and security considerations

## 0.1.0 - 2026-09-26

- `to_checksum` and `checksum_status` for EIP-55 addresses, pure-Python Keccak-256, `eip55` command line tool
- Fixed: addresses whose checksum is all upper or all lower case (four of the EIP's test vectors) were reported as unchecked
- Tests cover all eight EIP-55 test vectors
- Installable with pip from GitHub
