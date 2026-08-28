import csv


def totals(path: str) -> dict[str, float]:
    out: dict[str, float] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            out["all"] = out.get("all", 0.0) + float(row["amount"])
    return out
