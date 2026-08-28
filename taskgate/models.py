from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Verdict = Literal["submit", "reject"]

# Families the gold labels and the agent share.
FAMILIES = (
    "leak",
    "too_easy",
    "oracle_fail",
    "incomplete_oracle",
    "unfair",
    "impl_detail",
    "similarity",
    "malformed",
)


@dataclass
class Finding:
    family: str
    summary: str
    path: str
    snippet: str
    line: int | None = None
    kept: bool = True
    drop_reason: str | None = None

    def to_dict(self) -> dict:
        return {
            "family": self.family,
            "summary": self.summary,
            "path": self.path,
            "snippet": self.snippet,
            "line": self.line,
            "kept": self.kept,
            "drop_reason": self.drop_reason,
        }


@dataclass
class ToolEvent:
    tool: str
    input: str
    output: str

    def to_dict(self) -> dict:
        return {"tool": self.tool, "input": self.input, "output": self.output}


@dataclass
class Review:
    pack_id: str
    stage: str
    verdict: Verdict
    families: list[str]
    findings: list[Finding] = field(default_factory=list)
    events: list[ToolEvent] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    nop_passed: int | None = None
    nop_failed: int | None = None
    oracle_passed: int | None = None
    oracle_failed: int | None = None

    def to_dict(self) -> dict:
        return {
            "pack_id": self.pack_id,
            "stage": self.stage,
            "verdict": self.verdict,
            "families": self.families,
            "findings": [f.to_dict() for f in self.findings],
            "events": [e.to_dict() for e in self.events],
            "notes": self.notes,
            "nop_passed": self.nop_passed,
            "nop_failed": self.nop_failed,
            "oracle_passed": self.oracle_passed,
            "oracle_failed": self.oracle_failed,
        }


@dataclass
class Gold:
    verdict: Verdict
    families: list[str]
    title: str
    challenge: bool = False
