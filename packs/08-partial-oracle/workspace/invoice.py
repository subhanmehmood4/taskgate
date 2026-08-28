TAX = 0.05


def invoice_total(lines: list[tuple[int, int]]) -> int:
    sub = sum(cents * qty for cents, qty in lines)
    with_tax = sub * (1 + TAX)
    return int(with_tax)
