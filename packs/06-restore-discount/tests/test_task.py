import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from app import total  # noqa: E402


class DiscountTests(unittest.TestCase):
    def test_over_threshold(self):
        self.assertEqual(total([80, 40]), 108)

    def test_under_threshold(self):
        self.assertEqual(total([20, 30]), 50)


if __name__ == "__main__":
    unittest.main()
