import unittest
from datetime import timezone
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from parse import parse_stamp  # noqa: E402


class ParseTests(unittest.TestCase):
    def test_utc_z(self):
        got = parse_stamp("2026-01-02T03:04:05")
        self.assertEqual(got.tzinfo, timezone.utc)
        self.assertTrue(got.isoformat().endswith("+00:00") or got.isoformat().endswith("Z"))


if __name__ == "__main__":
    unittest.main()
