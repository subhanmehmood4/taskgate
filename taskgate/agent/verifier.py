from __future__ import annotations

from pathlib import Path

from taskgate.models import Finding


def verify_findings(pack_dir: Path, findings: list[Finding]) -> list[Finding]:
    """Drop any finding we cannot point at.

    This is the verification agent: fluent summaries without a file path
    or a snippet that actually exists are not allowed to reach the user.
    """
    kept: list[Finding] = []
    for finding in findings:
        target = pack_dir / finding.path
        if finding.path in {"NOP", "ORACLE", "MEMORY"}:
            finding.kept = True
            kept.append(finding)
            continue
        if not target.exists():
            finding.kept = False
            finding.drop_reason = f"path does not exist: {finding.path}"
            kept.append(finding)
            continue
        if target.is_file() and finding.snippet:
            text = target.read_text(encoding="utf-8", errors="replace")
            token = finding.snippet.strip()
            # Allow short descriptive snippets that quote a filename.
            if token and token not in text and token not in target.name and len(token) > 24:
                # Try first 40 chars of snippet (reports often trim).
                head = token[:40]
                if head not in text and target.name not in token:
                    finding.kept = False
                    finding.drop_reason = "snippet not found in cited file"
                    kept.append(finding)
                    continue
        finding.kept = True
        kept.append(finding)
    return kept
