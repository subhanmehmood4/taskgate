import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from ops import combine  # noqa: E402


class CombineTests(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(combine(4, 5), 9)
        self.assertEqual(combine(7, 1), 8)


if __name__ == "__main__":
    unittest.main()
