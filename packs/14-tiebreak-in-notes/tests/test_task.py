import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from roster import sorted_names  # noqa: E402


class RosterTests(unittest.TestCase):
    def test_last_then_first(self):
        path = ROOT / "workspace" / "people.csv"
        self.assertEqual(
            sorted_names(str(path)),
            ["Zoe Ames", "Ada Chen", "Ben Chen"],
        )


if __name__ == "__main__":
    unittest.main()
