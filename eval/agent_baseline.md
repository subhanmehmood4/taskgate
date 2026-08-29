# General-purpose agent comparison arm

This is the brief's other baseline: one general-purpose agent with the
full pack and a shell. It is **not** Taskgate. Taskgate stays
deterministic and never calls a model to decide submit/reject.

## Protocol

- Same 12 fixture packs and the same gold labels as every other stage.
- Same prompt every time: [agent_baseline_prompt.md](agent_baseline_prompt.md).
- The agent sees one pack directory. It does not get
  `taskgate/skills/eval_task_review.md`, `taskgate/memory/mechanics.yml`,
  or `eval/labels.json`.
- Three independent trials. Majority vote is the scored verdict.
- Recorded replies live in [agent_baseline_trials.json](agent_baseline_trials.json).

## Recorded run (this repo)

| Trial | Model | Verdict accuracy |
|---|---|---:|
| 1 | cursor-grok-4.6 | 11/12 (92%) |
| 2 | composer-2.5-fast | 8/12 (67%) |
| 3 | gpt-5.6-sol-medium | 10/12 (83%) |
| Majority | | **10/12 (83%)** |

Unanimous on 7/12 packs.

Trial 2 applied `oracle/apply.py` in place, then reread the now-fixed
starter and called several fair packs `too_easy`. Isolated copies were
restored before trial 3. That is the point: a shell agent can contaminate
the pack. Taskgate's runner always copies.

Majority misses:

- `06-restore-discount` — two trials rejected a fair pack (too_easy / leak).
- `12-reskin-rollup` — two trials submitted. No pool catalog, so no
  similarity catch.

## Replay (no key)

```bash
export PYTHONPATH="$PWD"
python3 -m taskgate eval --stage agent_baseline
python3 -m taskgate agent-baseline packs/03-nop-already-green
```

## Live re-run (needs a key, will drift)

```bash
export GROQ_API_KEY=...        # or ANTHROPIC_API_KEY / OPENAI_API_KEY
export PYTHONPATH="$PWD"
python3 -m taskgate agent-baseline --live --all --trials 3
```

Groq default model is `qwen/qwen3.8-27b`. Override with `TASKGATE_AGENT_MODEL`. Free-tier Groq TPM is tight; the live runner retries 429s.

Live tools are pack-scoped (`list_files`, `read_file`, `run_nop`,
`run_oracle`, `submit_review`). `run_nop` / `run_oracle` copy the pack
first. Do not treat a live re-run as the headline number. The committed
trials are the evidence.
