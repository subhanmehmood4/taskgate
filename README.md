# Taskgate

Pre-submit reviewer for Harbor-style LLM evaluation task packs.

A task author is about to upload a coding-agent benchmark. Taskgate reads the pack, runs the official oracle and the do-nothing baseline, and returns a **submit / reject** review a person can sign.

Public copy: [github.com/subhanmehmood4/taskgate](https://github.com/subhanmehmood4/taskgate).

## Who has this problem?

Evaluation task authors — people who write Harbor / Terminal-Bench / SWE-bench-Pro style packs for labs and platforms.

I do this work. Packs come back for the same few reasons: the starter already passes, the oracle does not, the instruction leaks the answer, a requirement lives in a comment, the tests lock a function name, or the pack is a reskin of something already in the pool.

## What bottleneck makes it worth solving?

A README and a green local demo do not tell you whether a pack will survive review. The evidence is split across `TASK.md`, hidden tests, the oracle, leftover files, and what the pool has already seen. Reading the instruction alone is how most authors self-review. That is also how most bad packs get uploaded.

The cost is not one rejected zip. It is a day of revision for a failure that a 30-second gate could have named.

## What this is not

- Not a wrapper around a frontier model that “vibes” a score.
- Not a dump of private AfterQuery / Revelo / Turing tasks. Every pack in `packs/` was written for this repo.
- Not an auto-uploader. Consequential submit stays behind a human checkpoint.

## Agent design

Purposeful pieces, not a pile of them.

| Piece | What it is | Why it is here |
|---|---|---|
| Skill | [`taskgate/skills/eval_task_review.md`](taskgate/skills/eval_task_review.md) | Loaded on every review. The written submit/reject contract the gates implement. |
| Tools | leak scan, NOP runner, oracle runner, fairness scan | Failure modes the instruction cannot see. |
| Memory | [`taskgate/memory/mechanics.yml`](taskgate/memory/mechanics.yml) | Catches a locally-green reskin (pack 12). |
| Verification | citation check | A finding without a real path/snippet is dropped. |
| Orchestration | inspector → leak → runner → fairness → memory → verifier | Each specialist sees the previous evidence. |
| Human checkpoint | printed on every report | A person still owns the upload. |

```
TASK.md + workspace + tests + oracle
        │
        ▼
   inspector (structure, file list)
        │
        ▼
   leak agent ──► filenames + test literals vs TASK.md
        │
        ▼
   runner agent ──► NOP (do nothing) + ORACLE (official fix)
        │
        ▼
   fairness agent ──► hidden comments, impl-detail tests
        │
        ▼
   memory agent ──► known mechanics
        │
        ▼
   verifier ──► drop uncited claims
        │
        ▼
   SUBMIT / REJECT report  ──► human decides
```

## Pack format (EvalPack v1)

Original format. Not a copy of any platform schema.

```
packs/<id>/
  TASK.md           # what the solving agent is told
  workspace/        # starter files
  tests/test_task.py
  oracle/apply.py   # official fix, run from the pack root
```

Gold labels live only in [`eval/labels.json`](eval/labels.json). The agent never reads them.

## Quick start

```bash
cd taskgate
export PYTHONPATH="$PWD"
python3 -m taskgate list
python3 -m taskgate baseline packs/03-nop-already-green
python3 -m taskgate review packs/03-nop-already-green
python3 -m taskgate eval --stage all
```

Requires Python 3.11+. Stdlib only.

## License

The code and the synthetic packs are original work for this submission. Use them under the terms in [LICENSE](LICENSE).
