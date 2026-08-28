import unittest
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from rollup import totals  # noqa: E402


class HoursRollupTests(unittest.TestCase):
    def test_per_project_totals(self):
        path = ROOT / "workspace" / "hours.csv"
        got = totals(str(path))
        self.assertEqual(got["alpha"], 8.0)
        self.assertEqual(got["beta"], 2.0)
        self.assertEqual(got["gamma"], 1.0)
        self.assertNotIn("all", got)


if __name__ == "__main__":
    unittest.main()
