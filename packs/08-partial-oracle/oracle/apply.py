from pathlib import Path

# Fixes tax only. Still truncates 218.9 -> 218.
PARTIAL = '''TAX = 0.10


def invoice_total(lines):
    sub = sum(cents * qty for cents, qty in lines)
    with_tax = sub * (1 + TAX)
    return int(with_tax)
'''


def main() -> None:
    (Path("workspace") / "invoice.py").write_text(PARTIAL, encoding="utf-8")


if __name__ == "__main__":
    main()
