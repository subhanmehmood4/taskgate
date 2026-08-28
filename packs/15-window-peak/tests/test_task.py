import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from peak import peaks  # noqa: E402


class PeakTests(unittest.TestCase):
    def test_window_max(self):
        self.assertEqual(peaks([4, 9, 1, 12, 6], 3), [9, 12, 12])

    def test_short_input(self):
        self.assertEqual(peaks([8], 3), [])


if __name__ == "__main__":
    unittest.main()
