# Taskgate

Pre-submit reviewer for Harbor-style LLM evaluation task packs.

A task author is about to upload a coding-agent benchmark. Taskgate reads the pack, runs the official oracle and the do-nothing baseline, and returns a **submit / reject** review a person can sign.

This repository is the micro1 Agentic Workflows Hackathon submission. Public copy: [github.com/subhanmehmood4/taskgate](https://github.com/subhanmehmood4/taskgate).

## Who has this problem?

Evaluation task authors — people who write Harbor / Terminal-Bench / SWE-bench-Pro style packs for labs and platforms.

I do this work. Packs come back for the same few reasons: the starter already passes, the oracle does not, the instruction leaks the answer, a requirement lives in a comment, the tests lock a function name, or the pack is a reskin of something already in the pool.

## What bottleneck makes it worth solving?

A README and a green local demo do not tell you whether a pack will survive review. The evidence is split across `TASK.md`, hidden tests, the oracle, leftover files, and what the pool has already seen. Reading the instruction alone is how most authors self-review. That is also how most bad packs get uploaded.

The cost is not one rejected zip. It is a day of revision for a failure that a 30-second gate could have named.

## Four questions

| | |
|---|---|
| Who has this problem? | Task authors and small eval teams who submit Harbor-style packs. |
| What bottleneck makes it worth solving? | Instruction-only self-review cannot see NOP, oracle, leaks outside the prompt, or pool similarity. |
| Does the agent solve it well? | Instruction-only review is **5/12 (42%)**. A general-purpose agent with the full pack and a shell, majority of 3 trials, is **10/12 (83%)**. Taskgate is **12/12 (100%)** on the same labels, and **2/3** on hold-out packs written after the gates froze. |
| Can another person reproduce the result? | Yes. Python 3.11+, no API keys, no extra packages. The agent-arm number is a replay of committed trials. See [REPRODUCE.md](REPRODUCE.md). |

## What this is not

- Not a wrapper around a frontier model that “vibes” a score. A general-purpose agent is a **comparison arm**, not the verdict path. See [eval/agent_baseline.md](eval/agent_baseline.md).
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

## Fair comparison

Same 12 packs, same gold labels, three arms.

| Arm | Resources | Verdict | Same answer again? | Cost / pack | Time |
|---|---|---:|---|---:|---|
| Instruction-only | `TASK.md` + a keyword check | 42% (5/12) | yes | $0 | seconds |
| General-purpose agent | full pack + shell; no skill, no memory, no gold | **83% (10/12)** majority | 7/12 unanimous (t1 92%, t2 67%, t3 83%) | $0 recorded | minutes |
| Taskgate | full pack + skill + tools + memory + verifier | **100% (12/12)** | yes — same verdicts every rerun | $0 | ~0.5s / pack |

The instruction-only arm is how authors actually self-review. The agent arm is the brief's other baseline — one general-purpose agent with basic tools. Taskgate is not that agent. It is the gate you run when you need the same verdict tomorrow.

The agent arm's two majority misses are the product: `12-reskin-rollup` looks locally healthy if you have no pool, and `06-restore-discount` was a fair pack that two trials still rejected. Trial 2 also applied `oracle/apply.py` in place and then called the now-green starter too easy. The runner copies; a shell agent does not unless you make it.

Prompt, trials, and replay: [eval/agent_baseline.md](eval/agent_baseline.md).

## Measured improvement

Primary metric: **verdict accuracy** (submit vs reject vs gold).

The table below is the Taskgate changelog. The agent arm above is a comparison, not a stage we folded into the product.

| Stage | What changed | Verdict | Family |
|---|---|---:|---:|
| Baseline | `TASK.md` only | 42% (5/12) | 42% |
| Removed experiment | filenames + `TASK.md`, still no tests | 50% (6/12) | 50% |
| Iteration 1 | leak scan | 50% (6/12) | 50% |
| Iteration 2 | NOP + oracle runner | **75% (9/12)** | 75% |
| Iteration 3 | unfair + impl-detail | 92% (11/12) | 92% |
| Iteration 4 | reviewer memory | 100% (12/12) | 100% |
| Final | + citation verifier | **100% (12/12)** | 100% |
| Agent comparison | general-purpose agent, 3-trial majority | 83% (10/12) | 83% |
| Hold-out | 3 packs written after the gates froze | **67% (2/3)** | 67% |

Full changelog: [CHANGELOG.md](CHANGELOG.md). Per-pack matrix: [results/matrix.md](results/matrix.md). Raw JSON: [results/](results/).

**Human time per pack (estimate):** about 90s to read `TASK.md` and guess, vs minutes for a general-purpose agent, vs about 4s for Taskgate plus about 30s to read a reject report. Not a timed user study.

**Cost per pack:** $0 for instruction-only and Taskgate. The recorded agent arm was also $0 (Cursor agents). A live API re-run needs your key and will drift.

Gold labels were assigned from the planted defect in each pack, not from a third-party ranking. The 12-pack suite is a fixture: it shows that instruction-only review cannot see NOP, oracle, hidden comments, or pool memory. It is not a claim that Taskgate generalizes to an unseen platform corpus.

The hold-out is the honesty check. Packs `13`–`15` were written after the gates froze. The agent catches the new NOP-green pack and correctly submits the new fair pack. It **misses** `14-tiebreak-in-notes`: the hidden rule is a first-name sort tie-break, and the fairness scanner only knows UTC/Z leftovers. That miss is the generalization limit.

### Challenging case

`11-timestamp-fold` looks like a trap (file order ≠ event order) but `TASK.md` states the rule. Gold is **submit**. The agent submits. The hard *review* case on the fixture is `12-reskin-rollup`: NOP red, oracle green, no leak — only memory rejects it. The hard *hold-out* case is `14-tiebreak-in-notes`.

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
cd taskgate   # or: cd "Micro 1 challenge"
export PYTHONPATH="$PWD"
python3 -m taskgate list
python3 -m taskgate baseline packs/03-nop-already-green
python3 -m taskgate review packs/03-nop-already-green
python3 -m taskgate eval --stage all
python3 -m taskgate eval --holdout
python3 -m taskgate eval --stage agent_baseline
```

Requires Python 3.11+. Stdlib only.

## Deliverables

| Item | Where |
|---|---|
| Solution + changelog | this repo + [CHANGELOG.md](CHANGELOG.md) |
| Reproduction guide | [REPRODUCE.md](REPRODUCE.md) |
| Agent trajectories | [trajectories/](trajectories/) — Taskgate stages plus `*__agent_baseline.md` |
| Agent comparison arm | [eval/agent_baseline.md](eval/agent_baseline.md) |
| Hot take | below, and the last section of the changelog |

## What existed before this hackathon

Nothing in this repository. The rejection families come from public Harbor-style practice and from evaluation work I have written about on [subhanmehmood.com/evaluation](https://subhanmehmood.com/evaluation). No private platform pack is included.

## Hot take

Doing nothing is a valid agent strategy. If NOP is already green, you did not write a benchmark — you wrote a compliment.

The second lesson is about fluency. A reject reason that cannot point at a file is worse than a silent pass. Verification here is not a second model. It is the rule that a claim without a path is dropped.

The third is about agents with a shell. If the reviewer runs `oracle/apply.py` on the real workspace, the next look at the starter is a lie. Copy first, or do not call yourself a gate.

## License

The code and the 12 synthetic packs are original work for this submission. Use them under the terms in [LICENSE](LICENSE).
