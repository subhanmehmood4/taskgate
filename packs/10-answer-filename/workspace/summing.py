from pathlib import Path


def total() -> int:
    lines = Path(__file__).with_name("numbers.txt").read_text(encoding="utf-8").splitlines()
    # BUG: drops the last value
    return sum(int(line) for line in lines[:-1])
