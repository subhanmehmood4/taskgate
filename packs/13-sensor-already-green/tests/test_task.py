import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from mean import means  # noqa: E402


class SensorMeanTests(unittest.TestCase):
    def test_per_sensor_mean(self):
        path = ROOT / "workspace" / "readings.csv"
        got = means(str(path))
        self.assertEqual(got["north"], 20.0)
        self.assertEqual(got["east"], 12.0)
        self.assertNotIn("all", got)


if __name__ == "__main__":
    unittest.main()
