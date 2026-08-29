# The 12 synthetic packs

All original. Gold is in `labels.json`. The general-purpose agent arm uses the same gold; see [agent_baseline.md](agent_baseline.md).

| Id | Gold | Planted issue |
|---|---|---|
| 01-hours-rollup | submit | None. Group-then-sum, NOP red, oracle green. |
| 02-leak-in-instruction | reject / leak | Expected totals printed in `TASK.md`. |
| 03-nop-already-green | reject / too_easy | Starter already passes. |
| 04-oracle-broken | reject / oracle_fail | Official `apply.py` still fails tests. |
| 05-unfair-hidden-comment | reject / unfair | UTC/Z required only in `legacy.txt`. |
| 06-restore-discount | submit | Restore a helper from `backup.log`. Fair. |
| 07-impl-detail-tests | reject / impl_detail | Tests lock `__name__` and `_scratch`. |
| 08-partial-oracle | reject / incomplete_oracle | Oracle fixes tax, not rounding. |
| 09-unsigned-token | submit | Reject `alg=none`. Fair. |
| 10-answer-filename | reject / leak | `THE_TOTAL_MUST_BE_128.txt`. |
| 11-timestamp-fold | submit (challenge) | Last write by timestamp, not file order. |
| 12-reskin-rollup | reject / similarity | Customer totals — reskin of pack 01. |

## Hold-out (written after the gates)

Gold is in `holdout_labels.json`. Not part of the 12/12 fixture.

| Id | Gold | Planted issue |
|---|---|---|
| 13-sensor-already-green | reject / too_easy | Starter already returns per-sensor means. |
| 14-tiebreak-in-notes | reject / unfair | First-name tie-break lives only in `notes.txt`. Fairness does not see it. |
| 15-window-peak | submit | Sliding-window max. Fair, original mechanic. |
