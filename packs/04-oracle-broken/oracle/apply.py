from pathlib import Path

# Wrong oracle: subtracts instead of adding.
WRONG = """def combine(a, b):
    return a - b
"""


def main() -> None:
    (Path("workspace") / "ops.py").write_text(WRONG, encoding="utf-8")


if __name__ == "__main__":
    main()
