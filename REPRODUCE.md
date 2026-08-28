# Reproduction guide

For someone starting from a clean machine. No API keys. No `pip install` beyond Python 3.11+.

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

Expected: 12 pack ids, `01-hours-rollup` through `12-reskin-rollup`.

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
```

This overwrites `results/*.json` and `trajectories/*__<stage>.md`. The copies already in those folders should match these percentages.

## 6. Data the run needs

- `packs/` — 12 synthetic fixtures written for this repo
- `eval/labels.json` — gold verdicts (`review` does not read this)
- `taskgate/memory/mechanics.yml` — reviewer memory
- `taskgate/skills/eval_task_review.md` — the written skill

No network. No secrets. No Docker.

## 7. What “done” looks like

- `results/summary.json` has `final.verdict_accuracy` = `1.0`
- `results/final.json` has 12 rows, all `verdict_ok: true`
- A trajectory exists for every pack and stage under `trajectories/`

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
| Oracle shows 0/1 on a known-good pack | `oracle/apply.py` must run with cwd = pack root (the runner does this) |
