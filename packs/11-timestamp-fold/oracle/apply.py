from pathlib import Path

FIXED = '''from pathlib import Path


def final_x() -> int:
    rows = []
    path = Path(__file__).with_name("events.log")
    for line in path.read_text(encoding="utf-8").splitlines():
        ts, rest = line.split(" ", 1)
        value = int(rest.rsplit("=", 1)[1])
        rows.append((ts, value))
    rows.sort(key=lambda row: row[0])
    return rows[-1][1]
'''


def main() -> None:
    (Path("workspace") / "fold.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
