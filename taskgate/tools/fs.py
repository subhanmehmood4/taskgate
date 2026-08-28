from __future__ import annotations

from pathlib import Path

REQUIRED = ("TASK.md", "workspace", "tests", "oracle")


def pack_id(pack_dir: Path) -> str:
    return pack_dir.resolve().name


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def list_files(pack_dir: Path) -> list[Path]:
    skip = {".git", "__pycache__", ".taskgate-tmp"}
    out: list[Path] = []
    for p in pack_dir.rglob("*"):
        if any(part in skip for part in p.parts):
            continue
        if p.is_file():
            out.append(p)
    return sorted(out)


def structure_problems(pack_dir: Path) -> list[str]:
    missing = [name for name in REQUIRED if not (pack_dir / name).exists()]
    return missing


def task_md(pack_dir: Path) -> Path:
    return pack_dir / "TASK.md"
