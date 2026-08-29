from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from taskgate.agent.pipeline import review_pack
from taskgate.agent_baseline import (
    TRIALS_PATH,
    live_review,
    load_trial_file,
    record_live_suite,
    review_from_recorded,
    trial_metrics,
)
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
        choices=[
            "baseline",
            "removed_context_only",
            "agent_baseline",
            "iter1",
            "iter2",
            "iter3",
            "iter4",
            "final",
            "all",
        ],
    )
    p_eval.add_argument(
        "--holdout",
        action="store_true",
        help="Score the 3 packs written after the gates (eval/holdout_labels.json)",
    )

    p_agent = sub.add_parser(
        "agent-baseline",
        help="Replay (default) or live-run the general-purpose agent arm",
    )
    p_agent.add_argument("pack", type=Path, nargs="?")
    p_agent.add_argument("--json", action="store_true")
    p_agent.add_argument(
        "--live",
        action="store_true",
        help="Call Anthropic/OpenAI. Needs a key. Overwrites recorded trials for the packs you run.",
    )
    p_agent.add_argument("--all", action="store_true", help="Every fixture pack in eval/labels.json")
    p_agent.add_argument("--trials", type=int, default=3)
    p_agent.add_argument("--trial", type=int, default=1, help="Trial index when reviewing one pack live")

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

    if args.cmd == "agent-baseline":
        return _agent_baseline_cmd(args)

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
            [
                "baseline",
                "removed_context_only",
                "iter1",
                "iter2",
                "iter3",
                "iter4",
                "final",
                "agent_baseline",
            ]
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
            if stage == "agent_baseline":
                _print_agent_breakdown(gold)
        summary_path = RESULTS / "summary.json"
        if args.stage != "all" and summary_path.exists():
            try:
                previous = json.loads(summary_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                previous = {}
            previous.update(summary)
            summary = previous
        summary_path.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
        if args.stage == "all":
            write_tables(RESULTS, payloads)
        return 0

    return 2


def _agent_baseline_cmd(args) -> int:
    gold = load_gold(ROOT / "eval" / "labels.json")
    if args.live and args.all:
        record_live_suite(PACKS, list(gold.keys()), args.trials, TRIALS_PATH)
        print(f"wrote {TRIALS_PATH}")
        return 0
    if args.live:
        if args.pack is None:
            print("agent-baseline --live needs a pack path, or pass --all", file=sys.stderr)
            return 2
        row = live_review(args.pack, trial=args.trial)
        if args.json:
            print(json.dumps(row, indent=2))
        else:
            fams = ",".join(row.get("families") or []) or "none"
            print(f"{row['pack_id']}  {row['verdict']}  {fams}")
            if row.get("summary"):
                print(row["summary"])
        return 0
    if args.pack is None:
        print("agent-baseline needs a pack path (replay) or --live --all", file=sys.stderr)
        return 2
    review = review_from_recorded(args.pack)
    _emit(review, args.json, save_traj=True)
    return 0


def _print_agent_breakdown(gold) -> None:
    payload = load_trial_file()
    extra = trial_metrics(payload, gold)
    acc = extra["per_trial_accuracy"]
    bits = "  ".join(f"{name} {value:.0%}" for name, value in acc.items())
    print(
        f"{'':22}  unanimous {extra['unanimous']}/{extra['n_packs']}  "
        f"({extra['unanimous_rate']:.0%})  {bits}"
    )
    meta = payload.get("meta") or {}
    if meta.get("model"):
        print(f"{'':22}  model {meta['model']}")


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
