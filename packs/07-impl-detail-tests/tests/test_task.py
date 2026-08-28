import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

import stats  # noqa: E402


class ImplTests(unittest.TestCase):
    def test_locked_name_and_private(self):
        self.assertEqual(stats.compute_widget_score.__name__, "compute_widget_score")
        self.assertTrue(hasattr(stats, "_scratch"))
        self.assertEqual(stats.compute_widget_score([4, 6]), 5)
        stats._scratch.append("touched")


if __name__ == "__main__":
    unittest.main()
