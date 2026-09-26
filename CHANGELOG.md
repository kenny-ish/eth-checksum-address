# Changelog

All notable changes to this project are documented in this file.

## 0.1.0 - 2026-09-26

- `to_checksum` and `checksum_status` for EIP-55 addresses, pure-Python Keccak-256, `eip55` command line tool
- Fixed: addresses whose checksum is all upper or all lower case (four of the EIP's test vectors) were reported as unchecked
- Tests cover all eight EIP-55 test vectors
- Installable with pip from GitHub
