from datetime import datetime


def parse_stamp(text: str) -> datetime:
    return datetime.fromisoformat(text)
