from pathlib import Path


def final_x() -> int:
    last = 0
    path = Path(__file__).with_name("events.log")
    for line in path.read_text(encoding="utf-8").splitlines():
        if "SET x=" in line:
            last = int(line.rsplit("=", 1)[1])
    return last
