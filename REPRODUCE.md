# Reproduction guide

For someone starting from a clean machine. The scored numbers need no API keys and no `pip install` beyond Python 3.11+. A live `--live` re-run of the agent arm is optional and needs a key.

## Versions we used

| Item | Version |
|---|---|
| OS | macOS 15 (Darwin 25.6.0) — Linux should match |
| Python | 3.12.12 (`python3 --version`) |
| Dependencies | **stdlib only** |
| Approximate runtime | `eval --stage all` ≈ 7 seconds |
| Approximate cost | $0 |

## 1. Get the repo

```bash
git clone https://github.com/subhanmehmood4/taskgate.git
cd taskgate
export PYTHONPATH="$PWD"
```

Python must be 3.11 or newer.

## 2. Sanity check

```bash
python3 -m taskgate list
```

Expected: 15 pack ids. `01`–`12` are the scored fixture. `13`–`15` are the hold-out (labels in `eval/holdout_labels.json`, not in `eval/labels.json`).

## 3. Baseline (one pack)

```bash
python3 -m taskgate baseline packs/03-nop-already-green
```

Expected: **SUBMIT**. The baseline only reads `TASK.md`. It cannot see that NOP is already green.

## 4. Agent (same pack)

```bash
python3 -m taskgate review packs/03-nop-already-green
```

Expected: **REJECT**, family `too_easy`, `NOP: 1 passed / 0 failed`.

## 5. Full evaluation (the headline number)

```bash
python3 -m taskgate eval --stage all
```

Expected stdout:

```
baseline                verdict 42%  (5/12)  family 42%
removed_context_only    verdict 50%  (6/12)  family 50%
iter1                   verdict 50%  (6/12)  family 50%
iter2                   verdict 75%  (9/12)  family 75%
iter3                   verdict 92%  (11/12)  family 92%
iter4                   verdict 100% (12/12)  family 100%
final                   verdict 100% (12/12)  family 100%
agent_baseline          verdict 83%  (10/12)  family 83%
                        unanimous 7/12  (58%)  t1 92%  t2 67%  t3 83%
                        model three independent general-purpose agents, same prompt, different model families
```

This overwrites `results/*.json` and `trajectories/*__<stage>.md`. The copies already in those folders should match these percentages.

`agent_baseline` **replays** `eval/agent_baseline_trials.json`. It does not call a model. See [eval/agent_baseline.md](eval/agent_baseline.md).

## 5b. Hold-out (written after the gates)

```bash
python3 -m taskgate eval --holdout
```

Expected:

```
holdout/final       verdict 67%  (2/3)  family 67%
  ok    13-sensor-already-green       gold=reject pred=reject
  MISS  14-tiebreak-in-notes          gold=reject pred=submit
  ok    15-window-peak                gold=submit pred=submit
```

Do not “fix” the agent so hold-out becomes 3/3. The miss is the point.

## 5c. Agent comparison arm (replay, no key)

```bash
python3 -m taskgate eval --stage agent_baseline
python3 -m taskgate agent-baseline packs/06-restore-discount
```

Expected: **83% (10/12)** majority, unanimous 7/12, per-trial 92% / 67% / 83%. Pack `06-restore-discount` majority **REJECT** (two trials false-rejected a fair pack). Pack `12-reskin-rollup` majority **SUBMIT** (no pool catalog).

Do not treat a live `--live` re-run as the headline. It needs `GROQ_API_KEY`, `ANTHROPIC_API_KEY`, or `OPENAI_API_KEY` and will drift.

## 6. Data the run needs

- `packs/` — 12 fixture packs plus 3 hold-out packs, all written for this repo
- `eval/labels.json` — gold verdicts for packs `01`–`12` (`review` does not read this)
- `eval/holdout_labels.json` — gold verdicts for packs `13`–`15`
- `taskgate/memory/mechanics.yml` — reviewer memory
- `taskgate/skills/eval_task_review.md` — the written skill
- `eval/agent_baseline_prompt.md` and `eval/agent_baseline_trials.json` — comparison arm (replay only)

No network. No secrets. No Docker. Live agent re-runs are optional and need a key.

## 7. What “done” looks like

- `results/summary.json` has `final.verdict_accuracy` = `1.0`
- `results/final.json` has 12 rows, all `verdict_ok: true`
- `results/holdout.json` has `metrics.verdict_correct` = `2`
- `results/agent_baseline.json` has `metrics.verdict_correct` = `10`
- A trajectory exists for every fixture pack and stage under `trajectories/`, including `*__agent_baseline.md`

## 8. One pack that should stay SUBMIT

```bash
python3 -m taskgate review packs/11-timestamp-fold
```

Expected: **SUBMIT**. This is the challenging fair pack. Do not “improve” the agent by rejecting it.

## Troubleshooting

| Symptom | Fix |
|---|---|
| `No module named taskgate` | `export PYTHONPATH="$PWD"` from the repo root |
| Verdicts drift from 12/12 | A pack, gold label, or `mechanics.yml` was edited |
| Hold-out becomes 3/3 | The fairness gate was widened after the hold-out was written; revert that |
| Oracle shows 0/1 on a known-good pack | `oracle/apply.py` must run with cwd = pack root (the runner does this) |
| `no recorded agent_baseline trials` | Restore `eval/agent_baseline_trials.json` from git. Replay does not call a model. |
