from pathlib import Path

FIXED = '''import csv


def totals(path: str) -> dict[str, float]:
    out: dict[str, float] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            key = row["project"]
            out[key] = out.get(key, 0.0) + float(row["hours"])
    return out
'''


def main() -> None:
    path = Path("workspace") / "rollup.py"
    path.write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
