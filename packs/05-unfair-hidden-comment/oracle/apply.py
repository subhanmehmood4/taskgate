from pathlib import Path

FIXED = '''from datetime import datetime, timezone


def parse_stamp(text: str) -> datetime:
    naive = datetime.fromisoformat(text)
    return naive.replace(tzinfo=timezone.utc)
'''


def main() -> None:
    (Path("workspace") / "parse.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
