from pathlib import Path

FIXED = '''_scratch = []


def compute_widget_score(values):
    if not values:
        raise ValueError("empty")
    return sum(values) / len(values)
'''


def main() -> None:
    (Path("workspace") / "stats.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
