from __future__ import annotations

from pathlib import Path

from taskgate.agent.verifier import verify_findings
from taskgate.models import Finding, Review, ToolEvent
from taskgate.tools.fairness import scan_fairness_bundle
from taskgate.tools.fs import list_files, pack_id, read_text, structure_problems, task_md
from taskgate.tools.leak import scan_leaks
from taskgate.tools.runtime import run_nop, run_oracle
from taskgate.tools.similarity import scan_similarity

PKG = Path(__file__).resolve().parents[1]
ROOT = PKG.parent
MEMORY = PKG / "memory" / "mechanics.yml"
SKILL = PKG / "skills" / "eval_task_review.md"

STAGES = {
    "iter1": ("structure", "leak"),
    "iter2": ("structure", "leak", "runtime"),
    "iter3": ("structure", "leak", "runtime", "fairness"),
    "iter4": ("structure", "leak", "runtime", "fairness", "similarity"),
    "final": ("structure", "leak", "runtime", "fairness", "similarity", "verify"),
}


def review_pack(pack_dir: Path, stage: str = "final") -> Review:
    pack_dir = pack_dir.resolve()
    gates = STAGES.get(stage, STAGES["final"])
    events: list[ToolEvent] = []
    findings: list[Finding] = []
    notes: list[str] = []
    pid = pack_id(pack_dir)

    if SKILL.exists():
        events.append(
            ToolEvent(
                "skill.eval_task_review",
                str(SKILL.relative_to(ROOT)),
                read_text(SKILL).strip()[:900],
            )
        )
        notes.append("skill: eval_task_review.md")

    events.append(
        ToolEvent(
            tool="inspector.list_files",
            input=pid,
            output="\n".join(str(p.relative_to(pack_dir)) for p in list_files(pack_dir)[:40]),
        )
    )

    nop_passed = nop_failed = oracle_passed = oracle_failed = None

    if "structure" in gates:
        missing = structure_problems(pack_dir)
        events.append(
            ToolEvent("inspector.structure", pid, "ok" if not missing else f"missing {missing}")
        )
        if missing:
            findings.append(
                Finding(
                    family="malformed",
                    summary=f"Pack is missing required parts: {', '.join(missing)}.",
                    path="TASK.md" if (pack_dir / "TASK.md").exists() else missing[0],
                    snippet=", ".join(missing),
                )
            )

    if "leak" in gates:
        leaked = scan_leaks(pack_dir)
        events.append(
            ToolEvent("leak.scan", "TASK.md + filenames vs test literals", f"{len(leaked)} finding(s)")
        )
        findings.extend(leaked)

    if "runtime" in gates:
        nop = run_nop(pack_dir)
        oracle = run_oracle(pack_dir)
        nop_passed, nop_failed = nop.passed, nop.failed
        oracle_passed, oracle_failed = oracle.passed, oracle.failed
        events.append(
            ToolEvent(
                "runner.nop",
                "unittest on starter",
                f"passed={nop.passed} failed={nop.failed}\n{nop.output[-400:]}",
            )
        )
        events.append(
            ToolEvent(
                "runner.oracle",
                "apply.py then unittest",
                f"apply_ok={oracle.apply_ok} passed={oracle.passed} failed={oracle.failed}\n{oracle.output[-400:]}",
            )
        )
        findings.extend(_runtime_findings(nop_passed, nop_failed, oracle_passed, oracle_failed, oracle.apply_ok))

    if "fairness" in gates:
        fair = scan_fairness_bundle(pack_dir)
        events.append(ToolEvent("fairness.scan", "tests vs TASK.md vs comments", f"{len(fair)} finding(s)"))
        findings.extend(fair)

    if "similarity" in gates:
        sim = scan_similarity(pack_dir, MEMORY)
        events.append(
            ToolEvent("memory.mechanics", str(MEMORY.relative_to(ROOT)), f"{len(sim)} finding(s)")
        )
        findings.extend(sim)

    if "verify" in gates:
        before = len(findings)
        findings = verify_findings(pack_dir, findings)
        dropped = [f for f in findings if not f.kept]
        events.append(
            ToolEvent(
                "verifier.citations",
                f"{before} findings",
                f"kept={sum(1 for f in findings if f.kept)} dropped={len(dropped)}",
            )
        )
        live = [f for f in findings if f.kept]
    else:
        live = findings

    families = []
    for f in live:
        if f.family not in families:
            families.append(f.family)

    if task_md(pack_dir).exists():
        notes.append(read_text(task_md(pack_dir)).splitlines()[0][:120])

    verdict = "reject" if families else "submit"
    return Review(
        pack_id=pid,
        stage=stage,
        verdict=verdict,
        families=families,
        findings=findings,
        events=events,
        notes=notes,
        nop_passed=nop_passed,
        nop_failed=nop_failed,
        oracle_passed=oracle_passed,
        oracle_failed=oracle_failed,
    )


def _runtime_findings(
    nop_passed: int,
    nop_failed: int,
    oracle_passed: int,
    oracle_failed: int,
    apply_ok: bool,
) -> list[Finding]:
    out: list[Finding] = []
    total_nop = nop_passed + nop_failed
    if total_nop and nop_failed == 0:
        out.append(
            Finding(
                family="too_easy",
                summary=f"NOP is already green ({nop_passed}/{total_nop}). Doing nothing solves the task.",
                path="NOP",
                snippet=f"passed={nop_passed} failed={nop_failed}",
            )
        )
    if not apply_ok:
        out.append(
            Finding(
                family="oracle_fail",
                summary="Oracle apply.py exited non-zero.",
                path="oracle/apply.py",
                snippet="apply.py failed",
            )
        )
        return out
    if oracle_failed > 0 and nop_failed > 0 and oracle_failed < nop_failed:
        out.append(
            Finding(
                family="incomplete_oracle",
                summary=(
                    f"Oracle only partially fixes the pack "
                    f"(NOP failed {nop_failed}, oracle still fails {oracle_failed})."
                ),
                path="ORACLE",
                snippet=f"nop_failed={nop_failed} oracle_failed={oracle_failed}",
            )
        )
    elif oracle_failed > 0:
        out.append(
            Finding(
                family="oracle_fail",
                summary=f"Oracle does not make hidden tests green ({oracle_passed} passed, {oracle_failed} failed).",
                path="ORACLE",
                snippet=f"passed={oracle_passed} failed={oracle_failed}",
            )
        )
    return out
