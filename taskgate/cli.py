from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from taskgate.agent.pipeline import review_pack
from taskgate.baseline import baseline_review
from taskgate.eval_runner import load_gold, run_suite, write_eval_outputs, write_tables
from taskgate.report import render_report, render_trajectory

ROOT = Path(__file__).resolve().parents[1]
PACKS = ROOT / "packs"
RESULTS = ROOT / "results"
TRAJ = ROOT / "trajectories"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="taskgate",
        description="Pre-submit reviewer for Harbor-style LLM evaluation task packs.",
    )
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_review = sub.add_parser("review", help="Run the agent on one pack")
    p_review.add_argument("pack", type=Path)
    p_review.add_argument("--stage", default="final", choices=["iter1", "iter2", "iter3", "iter4", "final"])
    p_review.add_argument("--json", action="store_true")

    p_base = sub.add_parser("baseline", help="Instruction-only baseline on one pack")
    p_base.add_argument("pack", type=Path)
    p_base.add_argument("--json", action="store_true")

    p_eval = sub.add_parser("eval", help="Score a stage against gold labels")
    p_eval.add_argument(
        "--stage",
        default="final",
        choices=["baseline", "removed_context_only", "iter1", "iter2", "iter3", "iter4", "final", "all"],
    )
    p_eval.add_argument(
        "--holdout",
        action="store_true",
        help="Score the 3 packs written after the gates (eval/holdout_labels.json)",
    )

    sub.add_parser("list", help="List synthetic packs")

    args = parser.parse_args(argv)

    if args.cmd == "list":
        for path in sorted(PACKS.iterdir()):
            if path.is_dir() and not path.name.startswith("."):
                print(path.name)
        return 0

    if args.cmd == "review":
        review = review_pack(args.pack, stage=args.stage)
        _emit(review, args.json, save_traj=True)
        return 0 if review.verdict else 1

    if args.cmd == "baseline":
        review = baseline_review(args.pack)
        _emit(review, args.json, save_traj=True)
        return 0

    if args.cmd == "eval":
        if args.holdout:
            gold = load_gold(ROOT / "eval" / "holdout_labels.json")
            stages = ["final"] if args.stage == "all" else [args.stage]
            rows = run_suite(PACKS, gold, stages[0])
            payload = write_eval_outputs(RESULTS, TRAJ, "holdout", rows)
            m = payload["metrics"]
            print(
                f"{'holdout/' + stages[0]:18}  verdict {m['verdict_accuracy']:.0%}  "
                f"({m['verdict_correct']}/{m['n']})  "
                f"family {m['family_accuracy']:.0%}"
            )
            for row in rows:
                mark = "ok" if row["verdict_ok"] else "MISS"
                print(
                    f"  {mark:4}  {row['pack_id']:28}  "
                    f"gold={row['gold_verdict']:6} pred={row['pred_verdict']}"
                )
            return 0

        stages = (
            ["baseline", "removed_context_only", "iter1", "iter2", "iter3", "iter4", "final"]
            if args.stage == "all"
            else [args.stage]
        )
        gold = load_gold(ROOT / "eval" / "labels.json")
        summary = {}
        payloads = {}
        for stage in stages:
            rows = run_suite(PACKS, gold, stage)
            out = write_eval_outputs(RESULTS, TRAJ, stage, rows)
            summary[stage] = out["metrics"]
            payloads[stage] = out
            m = out["metrics"]
            print(
                f"{stage:22}  verdict {m['verdict_accuracy']:.0%}  "
                f"({m['verdict_correct']}/{m['n']})  "
                f"family {m['family_accuracy']:.0%}"
            )
        (RESULTS / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        if args.stage == "all":
            write_tables(RESULTS, payloads)
        return 0

    return 2


def _emit(review, as_json: bool, save_traj: bool) -> None:
    if as_json:
        print(json.dumps(review.to_dict(), indent=2))
    else:
        sys.stdout.write(render_report(review))
    if save_traj:
        TRAJ.mkdir(parents=True, exist_ok=True)
        path = TRAJ / f"{review.pack_id}__{review.stage}.md"
        path.write_text(render_trajectory(review), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
