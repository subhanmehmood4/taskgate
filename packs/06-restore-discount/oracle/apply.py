from pathlib import Path

FIXED = '''def subtotal(lines: list[int]) -> int:
    return sum(lines)


def discount(amount: int) -> int:
    if amount > 100:
        return int(amount * 0.9)
    return amount


def total(lines: list[int]) -> int:
    return discount(subtotal(lines))
'''


def main() -> None:
    (Path("workspace") / "app.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
