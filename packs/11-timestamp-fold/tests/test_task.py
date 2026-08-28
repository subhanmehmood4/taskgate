import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from fold import final_x  # noqa: E402


class FoldTests(unittest.TestCase):
    def test_latest_timestamp_wins(self):
        self.assertEqual(final_x(), 5)


if __name__ == "__main__":
    unittest.main()
