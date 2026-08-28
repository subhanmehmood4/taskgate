import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from rollup import totals  # noqa: E402


class CustomerRollupTests(unittest.TestCase):
    def test_per_customer_totals(self):
        path = ROOT / "workspace" / "orders.csv"
        got = totals(str(path))
        self.assertEqual(got["ada"], 8.0)
        self.assertEqual(got["bev"], 2.0)
        self.assertEqual(got["cam"], 1.0)
        self.assertNotIn("all", got)


if __name__ == "__main__":
    unittest.main()
