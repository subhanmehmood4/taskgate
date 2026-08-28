import csv


def sorted_names(path: str) -> list[str]:
    rows = []
    with open(path, newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            rows.append(row)
    rows.sort(key=lambda row: row["last"])
    return [f"{row['first']} {row['last']}" for row in rows]
