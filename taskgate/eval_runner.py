from __future__ import annotations

import json
from pathlib import Path

from taskgate.agent.pipeline import review_pack
from taskgate.agent_baseline import review_from_recorded
from taskgate.baseline import baseline_review, removed_context_only_review
from taskgate.models import Gold, Review
from taskgate.report import render_trajectory


def load_gold(path: Path) -> dict[str, Gold]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    out: dict[str, Gold] = {}
    for pack_id, row in raw.items():
        out[pack_id] = Gold(
            verdict=row["verdict"],
            families=list(row.get("families") or []),
            title=row.get("title", pack_id),
            challenge=bool(row.get("challenge", False)),
        )
    return out


def run_one(pack_dir: Path, stage: str) -> Review:
    if stage == "baseline":
        return baseline_review(pack_dir)
    if stage == "removed_context_only":
        return removed_context_only_review(pack_dir)
    if stage == "agent_baseline":
        return review_from_recorded(pack_dir)
    return review_pack(pack_dir, stage=stage)


def run_suite(packs_dir: Path, gold: dict[str, Gold], stage: str) -> list[dict]:
    rows = []
    for pack_id, label in gold.items():
        pack_dir = packs_dir / pack_id
        review = run_one(pack_dir, stage)
        verdict_ok = review.verdict == label.verdict
        family_ok = _family_ok(review.families, label.families, label.verdict)
        rows.append(
            {
                "pack_id": pack_id,
                "title": label.title,
                "challenge": label.challenge,
                "gold_verdict": label.verdict,
                "gold_families": label.families,
                "pred_verdict": review.verdict,
                "pred_families": review.families,
                "verdict_ok": verdict_ok,
                "family_ok": family_ok,
                "review": review.to_dict(),
            }
        )
    return rows


def _family_ok(pred: list[str], gold_families: list[str], gold_verdict: str) -> bool:
    if gold_verdict == "submit":
        return pred == []
    if not gold_families:
        return True
    return gold_families[0] in pred


def metrics(rows: list[dict]) -> dict:
    n = len(rows)
    v_ok = sum(1 for r in rows if r["verdict_ok"])
    f_ok = sum(1 for r in rows if r["family_ok"])
    return {
        "n": n,
        "verdict_correct": v_ok,
        "verdict_accuracy": v_ok / n if n else 0.0,
        "family_correct": f_ok,
        "family_accuracy": f_ok / n if n else 0.0,
    }


def write_eval_outputs(results_dir: Path, traj_dir: Path, stage: str, rows: list[dict]) -> dict:
    results_dir.mkdir(parents=True, exist_ok=True)
    traj_dir.mkdir(parents=True, exist_ok=True)
    m = metrics(rows)
    payload = {"stage": stage, "metrics": m, "rows": rows}
    (results_dir / f"{stage}.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    # trajectories for this stage
    for row in rows:
        review = row["review"]
        # reconstruct a short md from stored events
        from taskgate.models import Finding, Review, ToolEvent

        rec = Review(
            pack_id=review["pack_id"],
            stage=review["stage"],
            verdict=review["verdict"],
            families=review["families"],
            findings=[Finding(**{k: v for k, v in f.items() if k in Finding.__dataclass_fields__}) for f in review["findings"]],
            events=[ToolEvent(**e) for e in review["events"]],
            notes=review.get("notes") or [],
            nop_passed=review.get("nop_passed"),
            nop_failed=review.get("nop_failed"),
            oracle_passed=review.get("oracle_passed"),
            oracle_failed=review.get("oracle_failed"),
        )
        (traj_dir / f"{rec.pack_id}__{stage}.md").write_text(render_trajectory(rec), encoding="utf-8")
    return payload


def write_tables(results_dir: Path, payloads: dict[str, dict]) -> None:
    """Refresh results/table.md and results/matrix.md from a full-suite run."""
    order = [
        "baseline",
        "removed_context_only",
        "iter1",
        "iter2",
        "iter3",
        "iter4",
        "final",
        "agent_baseline",
    ]
    short = {
        "baseline": "baseline",
        "removed_context_only": "removed",
        "iter1": "iter1",
        "iter2": "iter2",
        "iter3": "iter3",
        "iter4": "iter4",
        "final": "final",
        "agent_baseline": "agent",
    }
    table = [
        "| Stage | Verdict accuracy | Family accuracy | Correct |",
        "|---|---:|---:|---:|",
    ]
    for stage in order:
        if stage not in payloads:
            continue
        m = payloads[stage]["metrics"]
        table.append(
            f"| {stage} | {m['verdict_accuracy']:.0%} | {m['family_accuracy']:.0%} | "
            f"{m['verdict_correct']}/{m['n']} |"
        )
    (results_dir / "table.md").write_text("\n".join(table) + "\n", encoding="utf-8")

    pack_ids: list[str] = []
    gold_map: dict[str, str] = {}
    cells: dict[str, dict[str, str]] = {}
    for stage in order:
        if stage not in payloads:
            continue
        for row in payloads[stage]["rows"]:
            pid = row["pack_id"]
            if pid not in gold_map:
                pack_ids.append(pid)
                gold_map[pid] = row["gold_verdict"]
            hit = "yes" if row["verdict_ok"] else "no"
            cells.setdefault(pid, {})[stage] = f"{hit} {row['pred_verdict']}"

    header = "| pack | gold | " + " | ".join(short[s] for s in order if s in payloads) + " |"
    sep = "|" + "|".join(["---"] * (2 + sum(1 for s in order if s in payloads))) + "|"
    lines = [
        "# Per-pack verdict matrix",
        "",
        "Checkmark means the predicted verdict matches gold. Generated from `results/*.json`.",
        "",
        header,
        sep,
    ]
    for pid in pack_ids:
        cols = [pid, gold_map[pid]]
        for stage in order:
            if stage not in payloads:
                continue
            cols.append(cells.get(pid, {}).get(stage, ""))
        lines.append("| " + " | ".join(cols) + " |")
    (results_dir / "matrix.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
