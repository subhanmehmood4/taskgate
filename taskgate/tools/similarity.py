from __future__ import annotations

from pathlib import Path

from taskgate.models import Finding
from taskgate.tools.fs import pack_id, read_text, task_md


def scan_similarity(pack_dir: Path, memory_path: Path) -> list[Finding]:
    """Flag a pack whose solving mechanic already lives in reviewer memory.

    This is the diversity-fail case: local tests can be green while the
    task is a reskin of something already in the pool.
    """
    mechanics = _load_mechanics_stdlib(memory_path)

    task = read_text(task_md(pack_dir)).lower() if task_md(pack_dir).exists() else ""
    workspace_blob = " ".join(
        p.name.lower() for p in (pack_dir / "workspace").rglob("*") if p.is_file()
    )
    haystack = task + " " + workspace_blob
    current = pack_id(pack_dir)
    findings: list[Finding] = []

    for mech in mechanics:
        exemplar = str(mech.get("pack", ""))
        if exemplar == current:
            continue
        signals = [str(s).lower() for s in mech.get("signals", [])]
        hits = [s for s in signals if s in haystack]
        need = int(mech.get("min_hits", 2))
        if len(hits) >= need:
            task_raw = read_text(task_md(pack_dir)) if task_md(pack_dir).exists() else ""
            snippet = next(
                (line.strip() for line in task_raw.splitlines() if any(h in line.lower() for h in hits)),
                hits[0],
            )
            findings.append(
                Finding(
                    family="similarity",
                    summary=(
                        f"Solving mechanic '{mech.get('id')}' already exists "
                        f"in memory (exemplar {exemplar})."
                    ),
                    path="TASK.md",
                    snippet=snippet,
                )
            )
    return findings


def _load_mechanics_stdlib(memory_path: Path) -> list[dict]:
    """Minimal YAML subset reader for our mechanics file."""
    if not memory_path.exists():
        return []
    mechanics: list[dict] = []
    current: dict | None = None
    mode = None
    for raw in memory_path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line or line.lstrip().startswith("#"):
            continue
        if line.startswith("- id:"):
            if current:
                mechanics.append(current)
            current = {"id": line.split(":", 1)[1].strip().strip('"'), "signals": []}
            mode = None
            continue
        if current is None:
            continue
        if line.strip().startswith("pack:"):
            current["pack"] = line.split(":", 1)[1].strip().strip('"')
        elif line.strip().startswith("min_hits:"):
            current["min_hits"] = int(line.split(":", 1)[1].strip())
        elif line.strip().startswith("signals:"):
            mode = "signals"
        elif mode == "signals" and line.strip().startswith("- "):
            current["signals"].append(line.strip()[2:].strip().strip('"'))
    if current:
        mechanics.append(current)
    return mechanics
