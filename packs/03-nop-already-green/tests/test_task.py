import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from adder import add  # noqa: E402


class AddTests(unittest.TestCase):
    def test_sum(self):
        self.assertEqual(add(4, 5), 9)
        self.assertEqual(add(0, 0), 0)


if __name__ == "__main__":
    unittest.main()
