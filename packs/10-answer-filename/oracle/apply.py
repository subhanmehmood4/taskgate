from pathlib import Path

FIXED = '''from pathlib import Path


def total() -> int:
    lines = Path(__file__).with_name("numbers.txt").read_text(encoding="utf-8").splitlines()
    return sum(int(line) for line in lines if line.strip())
'''


def main() -> None:
    (Path("workspace") / "summing.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
