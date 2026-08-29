from __future__ import annotations

from pathlib import Path

from taskgate.models import Review

FAMILY_LABEL = {
    "leak": "answer leak",
    "too_easy": "too easy (NOP green)",
    "oracle_fail": "oracle does not pass",
    "incomplete_oracle": "oracle only partly fixes the pack",
    "unfair": "hidden requirement",
    "impl_detail": "tests check implementation, not behavior",
    "similarity": "reskin of a known mechanic",
    "malformed": "pack structure is incomplete",
}


def render_report(review: Review, pack_dir: Path | None = None) -> str:
    lines: list[str] = []
    lines.append("TASKGATE PRE-SUBMIT REVIEW")
    lines.append("=" * 46)
    lines.append(f"Pack:     {review.pack_id}")
    lines.append(f"Stage:    {review.stage}")
    lines.append(f"Verdict:  {review.verdict.upper()}")
    if review.families:
        pretty = ", ".join(FAMILY_LABEL.get(f, f) for f in review.families)
        lines.append(f"Why:      {pretty}")
    else:
        if review.stage in {"baseline", "removed_context_only"}:
            lines.append("Why:      instruction-only review found no reject signal")
        elif review.stage == "agent_baseline":
            lines.append("Why:      general-purpose agent majority vote found no reject signal")
        elif review.nop_passed is not None:
            lines.append("Why:      local gates are green; no leak, unfairness, or reskin flagged")
        else:
            lines.append("Why:      no reject findings")
    if review.nop_passed is not None:
        lines.append(
            f"NOP:      {review.nop_passed} passed / {review.nop_failed} failed"
        )
        lines.append(
            f"Oracle:   {review.oracle_passed} passed / {review.oracle_failed} failed"
        )
    lines.append("")
    live = [f for f in review.findings if f.kept]
    dropped = [f for f in review.findings if not f.kept]
    if live:
        lines.append("Evidence")
        lines.append("-" * 46)
        for finding in live:
            loc = finding.path
            if finding.line:
                loc = f"{finding.path}:{finding.line}"
            lines.append(f"  [{finding.family}] {finding.summary}")
            lines.append(f"           at {loc}")
            if finding.snippet:
                lines.append(f"           {finding.snippet[:140]}")
        lines.append("")
    if dropped:
        lines.append("Verifier dropped (no citeable evidence)")
        for finding in dropped:
            lines.append(f"  - {finding.summary} ({finding.drop_reason})")
        lines.append("")
    if review.verdict == "reject":
        lines.append("What to change")
        lines.append("-" * 46)
        lines.extend(_fixes(review))
        lines.append("")
        lines.append("Human checkpoint")
        lines.append("  Do not upload this pack to a live evaluation platform yet.")
    else:
        lines.append("Human checkpoint")
        if review.stage in {"baseline", "removed_context_only"}:
            lines.append("  Instruction-only review. A person still owns the final submit.")
        elif review.stage == "agent_baseline":
            lines.append("  Comparison arm. A person still owns the final submit.")
        else:
            lines.append("  Local gates passed. A person still owns the final submit.")
    return "\n".join(lines) + "\n"


def _fixes(review: Review) -> list[str]:
    out: list[str] = []
    fam = set(review.families)
    if "leak" in fam:
        out.append("  - Strip expected values from TASK.md and rename answer-like files.")
    if "too_easy" in fam:
        out.append("  - Break the starter so NOP is red for the right reason.")
    if "oracle_fail" in fam:
        out.append("  - Fix oracle/apply.py until hidden tests are green after it runs.")
    if "incomplete_oracle" in fam:
        out.append("  - Teach the oracle every bug the hidden tests cover, not just the first one.")
    if "unfair" in fam:
        out.append("  - Move hidden requirements into TASK.md, or delete the trap.")
    if "impl_detail" in fam:
        out.append("  - Assert behavior and outputs, not function names or private attributes.")
    if "similarity" in fam:
        out.append("  - Change the solving mechanic. A reskin will fail diversity review.")
    if "malformed" in fam:
        out.append("  - Add TASK.md, workspace/, tests/, and oracle/apply.py.")
    if not out:
        out.append("  - Address the findings above, then re-run `python3 -m taskgate review`.")
    return out


def render_trajectory(review: Review) -> str:
    lines = [f"# Trajectory — {review.pack_id} ({review.stage})", ""]
    for i, event in enumerate(review.events, start=1):
        lines.append(f"## Step {i}: {event.tool}")
        lines.append(f"- input: {event.input}")
        lines.append("```")
        lines.append(event.output[:1200] or "(empty)")
        lines.append("```")
        lines.append("")
    lines.append(f"## Final verdict: {review.verdict.upper()}")
    if review.families:
        lines.append(f"families: {', '.join(review.families)}")
    return "\n".join(lines) + "\n"
