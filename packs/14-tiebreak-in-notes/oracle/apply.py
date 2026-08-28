from pathlib import Path

FIXED = '''import csv


def sorted_names(path: str) -> list[str]:
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)
    rows.sort(key=lambda row: (row["last"], row["first"]))
    return [f"{row['first']} {row['last']}" for row in rows]
'''


def main() -> None:
    (Path("workspace") / "roster.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
