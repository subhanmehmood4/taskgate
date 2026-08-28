from __future__ import annotations

import ast
import re
from pathlib import Path

from taskgate.models import Finding
from taskgate.tools.fs import list_files, read_text, task_md

SKIP_INTS = {0, 1, -1, 2, 3, 10, 100, 200, 256, 404, 1000, 3600}
SKIP_STR = {
    "hs256",
    "none",
    "utf-8",
    "alpha",
    "beta",
    "credit",
    "debit",
    "project",
    "hours",
    "customer",
    "amount",
    "workspace",
}

BORING_SUFFIXES = (".csv", ".py", ".json", ".txt", ".log", ".md", ".bak")


def _boring_string(s: str) -> bool:
    lower = s.lower()
    if lower in SKIP_STR:
        return True
    if any(lower.endswith(ext) for ext in BORING_SUFFIXES):
        return True
    if "/" in s or "\\" in s:
        return True
    return False


def _interesting_constants(tree: ast.AST) -> list[str]:
    out: list[str] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Constant):
            continue
        val = node.value
        if isinstance(val, bool):
            continue
        if isinstance(val, (int, float)) and abs(val) not in SKIP_INTS and abs(val) >= 4:
            text = str(int(val)) if float(val).is_integer() else str(val)
            out.append(text)
        if isinstance(val, str):
            s = val.strip()
            if _boring_string(s):
                continue
            if re.match(r"\d{4}-\d{2}-\d{2}T", s):
                continue
            if len(s) >= 10 and s.lower() not in SKIP_STR:
                out.append(s)
            if re.fullmatch(r"[0-9a-f]{8,}", s.lower() or ""):
                out.append(s)
    return out


def test_literals(pack_dir: Path) -> list[str]:
    found: list[str] = []
    for path in (pack_dir / "tests").rglob("*.py"):
        try:
            tree = ast.parse(read_text(path))
        except SyntaxError:
            continue
        found.extend(_interesting_constants(tree))
    # unique, keep order
    seen: set[str] = set()
    uniq: list[str] = []
    for item in found:
        if item not in seen:
            seen.add(item)
            uniq.append(item)
    return uniq


def scan_leaks(pack_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    literals = test_literals(pack_dir)
    if not literals:
        return findings

    task_path = task_md(pack_dir)
    task = read_text(task_path) if task_path.exists() else ""
    task_lines = task.splitlines()

    for lit in literals:
        for i, line in enumerate(task_lines, start=1):
            if lit in line:
                findings.append(
                    Finding(
                        family="leak",
                        summary=f"TASK.md contains test expected value {lit!r}.",
                        path=str(task_path.relative_to(pack_dir)),
                        snippet=line.strip(),
                        line=i,
                    )
                )
                break

    leak_name = re.compile(r"(answer|expected|must_be|solution|flag|total_is)[_-]?", re.I)
    for path in list_files(pack_dir):
        rel = path.relative_to(pack_dir)
        name = path.name
        if leak_name.search(name):
            for lit in literals:
                if lit in name:
                    findings.append(
                        Finding(
                            family="leak",
                            summary=f"Workspace filename leaks expected value {lit!r}.",
                            path=str(rel),
                            snippet=name,
                        )
                    )
                    break
            else:
                # filename advertises that it is the answer even without the number
                if "workspace" in rel.parts:
                    findings.append(
                        Finding(
                            family="leak",
                            summary="Filename tells the solving agent where the answer lives.",
                            path=str(rel),
                            snippet=name,
                        )
                    )
    return findings
