import unittest

from eip55 import checksum_status, to_checksum
from keccak import keccak256

# The test vectors from the EIP-55 specification
ALL_CAPS = ["0x52908400098527886E0F7030069857D2E4169EE7", "0x8617E340B3D01FA5F11F306F4090FD50E238070D"]
ALL_LOWER = ["0xde709f2102306220921060314715629080e2fb77", "0x27b1fdb04752bbc536007a920d24acb045561c26"]
NORMAL = [
    "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
    "0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359",
    "0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB",
    "0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb",
]


class KeccakTest(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(
            keccak256(b"").hex(),
            "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470")

    def test_abc(self):
        self.assertEqual(
            keccak256(b"abc").hex(),
            "4e03657aea45a94fc7d47ba826c8d667c0d1e6e33a64a036ec44f58fa12d6c45")

    def test_multi_block(self):
        # 200 bytes spans two 136-byte blocks; must not raise and must be 32 bytes
        self.assertEqual(len(keccak256(b"a" * 200)), 32)


class Eip55Test(unittest.TestCase):
    def test_all_eip_vectors(self):
        for v in ALL_CAPS + ALL_LOWER + NORMAL:
            self.assertEqual(to_checksum(v.lower()), v)
            self.assertEqual(checksum_status(v), "valid", v)

    def test_single_case_without_checksum_is_unchecked(self):
        self.assertEqual(checksum_status(NORMAL[0].lower()), "unchecked")
        self.assertEqual(checksum_status("0x" + NORMAL[0][2:].upper()), "unchecked")

    def test_flipped_case_is_invalid(self):
        v = NORMAL[0]
        i = next(i for i, ch in enumerate(v) if i > 1 and ch.isalpha())
        flipped = v[:i] + v[i].swapcase() + v[i + 1:]
        self.assertEqual(checksum_status(flipped), "invalid")

    def test_rejects_bad_length(self):
        with self.assertRaises(ValueError):
            to_checksum("0x1234")


if __name__ == "__main__":
    unittest.main()
