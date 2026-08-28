from pathlib import Path

FIXED = '''def peaks(values: list[int], width: int) -> list[int]:
    if width <= 0 or len(values) < width:
        return []
    out = []
    for i in range(len(values) - width + 1):
        out.append(max(values[i : i + width]))
    return out
'''


def main() -> None:
    (Path("workspace") / "peak.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
