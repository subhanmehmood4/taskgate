import csv


def means(path: str) -> dict[str, float]:
    buckets: dict[str, list[float]] = {}
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            buckets.setdefault(row["sensor"], []).append(float(row["celsius"]))
    return {key: sum(vals) / len(vals) for key, vals in buckets.items()}
