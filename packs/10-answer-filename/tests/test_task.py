import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from summing import total  # noqa: E402


class SumTests(unittest.TestCase):
    def test_all_lines(self):
        self.assertEqual(total(), 128)


if __name__ == "__main__":
    unittest.main()
