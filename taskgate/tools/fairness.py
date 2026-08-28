from __future__ import annotations

import ast
import re
from pathlib import Path

from taskgate.models import Finding
from taskgate.tools.fs import read_text, task_md

PRIVATE_PATTERNS = (
    "inspect.getsource",
    "inspect.getsourcefile",
    ".__name__",
    ".__qualname__",
    "co_filename",
)


def scan_fairness_bundle(pack_dir: Path) -> list[Finding]:
    return scan_impl_detail(pack_dir) + scan_unfair(pack_dir)


def scan_impl_detail(pack_dir: Path) -> list[Finding]:
    findings: list[Finding] = []
    for path in (pack_dir / "tests").rglob("*.py"):
        src = read_text(path)
        rel = str(path.relative_to(pack_dir))
        for pat in PRIVATE_PATTERNS:
            if pat in src:
                line_no = _first_line_containing(src, pat)
                findings.append(
                    Finding(
                        family="impl_detail",
                        summary=f"Hidden tests assert implementation detail ({pat}).",
                        path=rel,
                        snippet=_line_at(src, line_no),
                        line=line_no,
                    )
                )
        # private attribute access: obj._foo
        if re.search(r"\._[a-zA-Z]\w*", src):
            line_no = _first_line_matching(src, r"\._[a-zA-Z]\w*")
            findings.append(
                Finding(
                    family="impl_detail",
                    summary="Hidden tests reach into a private attribute.",
                    path=rel,
                    snippet=_line_at(src, line_no),
                    line=line_no,
                )
            )
    return findings


def scan_unfair(pack_dir: Path) -> list[Finding]:
    """A requirement lives only in a comment / leftover file, not in TASK.md."""
    task = read_text(task_md(pack_dir)).lower() if task_md(pack_dir).exists() else ""
    findings: list[Finding] = []

    hidden_files: list[Path] = []
    for path in pack_dir.rglob("*"):
        if not path.is_file():
            continue
        name = path.name.lower()
        if any(tag in name for tag in ("legacy", ".bak", "notes.txt", "hidden", "todo")):
            hidden_files.append(path)

    # Format / timezone tokens often used as unfair hidden requirements.
    tokens = ("rfc3339", "timezone.utc", "utcnow", "+00:00", 'endswith("z")', "endswith('z')")
    test_src = "\n".join(read_text(p) for p in (pack_dir / "tests").rglob("*.py"))
    test_l = test_src.lower()

    required: list[str] = []
    for tok in tokens:
        if tok in test_l:
            required.append(tok)

    utc_in_tests = any(
        marker in test_l for marker in ("timezone.utc", "+00:00", 'endswith("z")', "endswith('z')", "rfc3339")
    )
    utc_in_task = any(marker in task for marker in ("utc", "rfc3339", "+00:00", "z suffix"))
    if utc_in_tests and not utc_in_task:
        for path in hidden_files:
            text = read_text(path)
            blob = text.lower()
            if any(marker in blob for marker in ("utc", "rfc3339", "z suffix")):
                findings.append(
                    Finding(
                        family="unfair",
                        summary="Tests require UTC/Z timestamps, but TASK.md never says so.",
                        path=str(path.relative_to(pack_dir)),
                        snippet=_first_matching_line(text, "UTC") or text.strip().splitlines()[0][:120],
                    )
                )
                break

    # Also pull string constants from tests that look like format contracts.
    for path in (pack_dir / "tests").rglob("*.py"):
        try:
            tree = ast.parse(read_text(path))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Constant) and isinstance(node.value, str):
                val = node.value
                if val in {"Z", "+00:00", "UTC", "RFC3339"}:
                    required.append(val)

    for req in dict.fromkeys(required):
        if req.lower() in task or (req == "Z" and "utc" in task):
            continue
        # Must appear in a hidden/comment location to count as planted unfairness.
        for path in hidden_files:
            text = read_text(path)
            if req.lower() in text.lower() or (req == "Z" and "Z suffix" in text):
                findings.append(
                    Finding(
                        family="unfair",
                        summary=f"Tests require {req!r}, but TASK.md never says so.",
                        path=str(path.relative_to(pack_dir)),
                        snippet=_first_matching_line(text, req) or text.strip().splitlines()[0][:120],
                    )
                )
                break
        else:
            # comment-only in workspace source
            for path in (pack_dir / "workspace").rglob("*"):
                if not path.is_file() or path.suffix not in {".py", ".txt", ".md"}:
                    continue
                text = read_text(path)
                if req.lower() in text.lower() and req.lower() not in task:
                    if _in_comment(text, req):
                        findings.append(
                            Finding(
                                family="unfair",
                                summary=f"Required {req!r} appears only in a comment, not in TASK.md.",
                                path=str(path.relative_to(pack_dir)),
                                snippet=_first_matching_line(text, req),
                            )
                        )
                        break
    return _dedupe(findings)


def _dedupe(findings: list[Finding]) -> list[Finding]:
    seen: set[tuple[str, str]] = set()
    out: list[Finding] = []
    for finding in findings:
        key = (finding.family, finding.path)
        if key in seen:
            continue
        seen.add(key)
        out.append(finding)
    return out


def _in_comment(text: str, token: str) -> bool:
    for line in text.splitlines():
        stripped = line.strip()
        if token.lower() in stripped.lower() and stripped.startswith("#"):
            return True
    return False


def _first_line_containing(src: str, needle: str) -> int:
    for i, line in enumerate(src.splitlines(), start=1):
        if needle in line:
            return i
    return 1


def _first_line_matching(src: str, pattern: str) -> int:
    rx = re.compile(pattern)
    for i, line in enumerate(src.splitlines(), start=1):
        if rx.search(line):
            return i
    return 1


def _line_at(src: str, line_no: int) -> str:
    lines = src.splitlines()
    if 1 <= line_no <= len(lines):
        return lines[line_no - 1].strip()
    return ""


def _first_matching_line(text: str, token: str) -> str:
    for line in text.splitlines():
        if token.lower() in line.lower():
            return line.strip()[:160]
    return ""
