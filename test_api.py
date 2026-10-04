import unittest

from eip55 import AddressError, is_address, is_checksum_address, normalize

WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
TYPO = "0xc02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"  # first letter's case flipped


class ApiTest(unittest.TestCase):
    def test_is_address(self):
        self.assertTrue(is_address(WETH))
        self.assertTrue(is_address(WETH.lower()))
        self.assertFalse(is_address(WETH[2:]))
        self.assertFalse(is_address(WETH[:-1]))
        self.assertFalse(is_address(TYPO))
        self.assertFalse(is_address(None))

    def test_is_checksum_address(self):
        self.assertTrue(is_checksum_address(WETH))
        self.assertFalse(is_checksum_address(WETH.lower()))
        self.assertTrue(is_checksum_address("0x52908400098527886E0F7030069857D2E4169EE7"))

    def test_normalize(self):
        self.assertEqual(normalize("  " + WETH.lower() + "\n"), WETH)
        self.assertEqual(normalize(WETH), WETH)

    def test_normalize_says_what_is_wrong(self):
        cases = [
            ("0x1234", "expected 40 hex digits, got 4"),
            (WETH[2:], "missing 0x prefix"),
            ("0x" + "g" * 40, "non-hex character 'g' at position 2"),
            (12, "expected str, got int"),
            (TYPO, "bad EIP-55 checksum"),
        ]
        for value, message in cases:
            with self.assertRaises(AddressError) as ctx:
                normalize(value)
            self.assertIn(message, str(ctx.exception))

    def test_address_error_is_a_value_error(self):
        self.assertTrue(issubclass(AddressError, ValueError))


if __name__ == "__main__":
    unittest.main()
