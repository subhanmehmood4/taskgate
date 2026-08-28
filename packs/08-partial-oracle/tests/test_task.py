import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from invoice import invoice_total  # noqa: E402


class InvoiceTests(unittest.TestCase):
    def test_tax_rate(self):
        # 1000 cents + 10% = 1100
        self.assertEqual(invoice_total([(1000, 1)]), 1100)

    def test_half_up(self):
        # 199 * 1.10 = 218.9 -> 219 cents
        self.assertEqual(invoice_total([(199, 1)]), 219)


if __name__ == "__main__":
    unittest.main()
