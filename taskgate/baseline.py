from __future__ import annotations

import re
from pathlib import Path

from taskgate.models import Review, ToolEvent
from taskgate.tools.fs import pack_id, read_text, task_md


def baseline_review(pack_dir: Path) -> Review:
    """Instruction-only baseline: read TASK.md, no tools, no tests.

    This is the 'one direct prompt with basic instructions' analogue —
    a person or a general model that never opens the rest of the pack.
    """
    pack_dir = pack_dir.resolve()
    pid = pack_id(pack_dir)
    path = task_md(pack_dir)
    text = read_text(path) if path.exists() else ""
    findings = []
    notes = [text.splitlines()[0][:120]] if text else ["missing TASK.md"]

    leak_hit = re.search(
        r"(expected\s+\w+\s+total\s+is\s+[\d.]+|the answer is\s+\S+|must be\s+\d{2,})",
        text,
        re.I,
    )
    families: list[str] = []
    if leak_hit:
        from taskgate.models import Finding

        findings.append(
            Finding(
                family="leak",
                summary="Instruction appears to contain an expected answer.",
                path="TASK.md",
                snippet=leak_hit.group(0),
            )
        )
        families = ["leak"]

    events = [
        ToolEvent(
            tool="baseline.read_task",
            input="TASK.md only",
            output=f"{len(text.split())} words; leak_regex={'yes' if leak_hit else 'no'}",
        )
    ]
    verdict = "reject" if families else "submit"
    return Review(
        pack_id=pid,
        stage="baseline",
        verdict=verdict,
        families=families,
        findings=findings,
        events=events,
        notes=notes,
    )


def removed_context_only_review(pack_dir: Path) -> Review:
    """Experiment we later removed: glance at filenames + TASK.md, still no tests.

    Looks more 'agentic' than baseline (it lists files) but still cannot see
    NOP/oracle. It confidently submits broken oracles. Named for the extra
    context, not a model — no LLM is involved.
    """
    pack_dir = pack_dir.resolve()
    pid = pack_id(pack_dir)
    text = read_text(task_md(pack_dir)) if task_md(pack_dir).exists() else ""
    names = [p.name for p in pack_dir.rglob("*") if p.is_file()]
    from taskgate.models import Finding

    findings = []
    families: list[str] = []
    leak_hit = re.search(
        r"(expected\s+\w+\s+total\s+is\s+[\d.]+|the answer is\s+\S+|must be\s+\d{2,})",
        text,
        re.I,
    )
    if leak_hit:
        findings.append(
            Finding(
                family="leak",
                summary="Instruction appears to contain an expected answer.",
                path="TASK.md",
                snippet=leak_hit.group(0),
            )
        )
        families.append("leak")
    for name in names:
        lower = name.lower()
        if any(tag in lower for tag in ("answer", "must_be", "solution", "flag")):
            findings.append(
                Finding(
                    family="leak",
                    summary=f"Filename looks like an answer file: {name}",
                    path=name,
                    snippet=name,
                )
            )
            if "leak" not in families:
                families.append("leak")
            break

    events = [
        ToolEvent("removed_context_only.list_names", pid, ", ".join(names[:20])),
        ToolEvent("removed_context_only.read_task", "TASK.md", f"{len(text.split())} words"),
    ]
    return Review(
        pack_id=pid,
        stage="removed_context_only",
        verdict="reject" if families else "submit",
        families=families,
        findings=findings,
        events=events,
        notes=["filenames + TASK.md, no runtime"],
    )
