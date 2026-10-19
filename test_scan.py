import contextlib
import io
import tempfile
import unittest
from pathlib import Path

from eip55 import main, scan

WETH = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
TYPO = "0xc02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"


def run(argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = main(argv)
    return code, out.getvalue()


class ScanTest(unittest.TestCase):
    def test_finds_addresses_with_positions(self):
        text = f'token = "{WETH}"\ntx = 0x{"ab" * 32}\nowner: {TYPO}\n'
        found = list(scan(text))
        self.assertEqual([(f[0], f[1], f[3]) for f in found], [(1, 10, "valid"), (3, 8, "invalid")])

    def test_ignores_longer_hex_strings(self):
        self.assertEqual(list(scan("0x" + "a" * 41)), [])
        self.assertEqual(list(scan("x0x" + "a" * 40)), [])

    def test_cli_exit_codes(self):
        with tempfile.TemporaryDirectory() as tmp:
            good = Path(tmp, "good.json")
            good.write_text(f'{{"weth": "{WETH}"}}\n')
            lower = Path(tmp, "lower.txt")
            lower.write_text(WETH.lower() + "\n")
            bad = Path(tmp, "bad.sol")
            bad.write_text(f"address constant OWNER = {TYPO};\n")
            self.assertEqual(run(["--scan", str(good), str(lower)])[0], 0)
            self.assertEqual(run(["--scan", "--strict", str(lower)])[0], 1)
            code, out = run(["--scan", str(bad)])
            self.assertEqual(code, 1)
            self.assertIn("bad.sol:1:26  INVALID checksum", out)


if __name__ == "__main__":
    unittest.main()
