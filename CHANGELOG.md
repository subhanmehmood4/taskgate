# Improvement changelog

Primary metric is **verdict accuracy** on the same 12 packs and the same gold labels (`eval/labels.json`). Family accuracy means the gold reject family appears in the predicted families (or the pack is a clean submit).

| Stage | What we tried and why | Evidence | Decision / learning |
|---|---|---|---|
| Baseline | Instruction-only review. This is how authors actually self-check: read `TASK.md`, decide submit. | 5/12 (42%). Catches the obvious instruction leak (`02`). Submits the other 7 rejects, including NOP-green, broken oracle, filename leak, unfair comment, impl-detail tests, partial oracle, and the reskin. | Established the starting point. Reading the prompt is not a review. |
| Removed experiment (`removed_context_only`) | Listed filenames and read `TASK.md`. Looked more “agentic.” Still did not run tests. No model is involved — the old stage name implied one. | 6/12 (50%). Gains `10-answer-filename`. Still submits `03`, `04`, `05`, `07`, `08`, `12` with a fluent report. | **Removed as the primary reviewer.** File listing stays as the inspector step. A confident submit on a broken oracle is the failure mode we refuse to ship. |
| Iteration 1 | Added a leak skill: test literals vs `TASK.md` and answer-shaped filenames. | 6/12 (50%). Same headline as the removed experiment on this suite. | Kept. Cheap, deterministic, and it is the right place to catch `02` and `10` without a model. Not sufficient. |
| Iteration 2 | Added the runner: NOP (do nothing) and oracle (`apply.py` then tests). | **9/12 (75%).** New catches: `03` too easy, `04` oracle fail, `08` incomplete oracle. Largest single jump. | **Kept. This is the main contribution.** `05`, `07`, and `12` still look locally healthy. |
| Iteration 3 | Added fairness: hidden-file requirements and tests that lock `__name__` / private attributes. | 11/12 (92%). New catches: `05` unfair, `07` impl-detail. | Kept. “Hard” and “unfair” are not the same gate. |
| Iteration 4 | Added reviewer memory of known mechanics. | **12/12 (100%).** Catches `12-reskin-rollup` — NOP red, oracle green, no leak. | Kept. Diversity failure is invisible to a pack that only looks at itself. |
| Final | Combined the kept gates and added a citation verifier. Findings whose snippet is not in the cited file are dropped. | 12/12 (100%). Same score as iteration 4 on this suite. During development the verifier dropped a similarity finding whose snippet was a paraphrase, not a quote. | Kept. Score did not move on the final labels, but the report became something a person would sign. |

## Per-pack matrix

✓ = verdict matches gold. Full file: [results/matrix.md](results/matrix.md).

| Pack | Gold | Baseline | Removed | Iter1 | Iter2 | Iter3 | Iter4 / Final |
|---|---|---|---|---|---|---|---|
| 01-hours-rollup | submit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 02-leak-in-instruction | reject / leak | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 03-nop-already-green | reject / too_easy | no | no | no | ✓ | ✓ | ✓ |
| 04-oracle-broken | reject / oracle_fail | no | no | no | ✓ | ✓ | ✓ |
| 05-unfair-hidden-comment | reject / unfair | no | no | no | no | ✓ | ✓ |
| 06-restore-discount | submit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 07-impl-detail-tests | reject / impl_detail | no | no | no | no | ✓ | ✓ |
| 08-partial-oracle | reject / incomplete_oracle | no | no | no | ✓ | ✓ | ✓ |
| 09-unsigned-token | submit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 10-answer-filename | reject / leak | no | ✓ | ✓ | ✓ | ✓ | ✓ |
| 11-timestamp-fold (challenge) | submit | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| 12-reskin-rollup | reject / similarity | no | no | no | no | no | ✓ |

## Evaluation notes

- Ten or more cases: **12**.
- One challenging case: `11-timestamp-fold` (fair, easy to get wrong as a solver; the reviewer must still submit). The challenging review is `12-reskin-rollup`.
- Secondary: family accuracy tracks verdict on this suite because each reject pack has one planted primary family. Pack `02` also flags `similarity` (it is a leaked reskin of pack `01`); the primary family `leak` still matches gold.
- Human time / cost: see README. Suite runtime is about 7 seconds on a laptop. Cost is $0.

## Main failure mode we observed

The removed experiment. Adding “more context” (filenames) without a runner produced a better-looking report and an 8-point gain — then a clean submit on a pack whose official oracle fails. Fluency hid the miss.

## Hot take

Doing nothing is a valid agent strategy. If NOP is green, the pack is not a benchmark.

A reject reason that cannot point at a file is worse than a silent pass. Verification is not a second model. It is refusing to emit a claim you cannot cite.
