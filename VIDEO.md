# Solution video (≤ 5 minutes)

Record the terminal and one editor window. No music. Talk over the commands.

## Script (~4:30)

**0:00–0:40 — Problem**

“I write Harbor-style evaluation packs. They come back for the same reasons: starter already passes, oracle does not, the answer leaked, a requirement hid in a comment, or the pack is a reskin. Authors review by reading the instruction. That is the bottleneck.”

Show `packs/` and `eval/labels.json` for two seconds.

**0:40–1:20 — Baseline**

```bash
export PYTHONPATH="$PWD"
python3 -m taskgate baseline packs/03-nop-already-green
```

Say: “Same task, instruction only. It submits. A do-nothing agent would already pass every hidden test. The baseline cannot see that.”

**1:20–2:10 — One realistic execution**

```bash
python3 -m taskgate review packs/03-nop-already-green
```

Walk the report: REJECT, too_easy, NOP 1/1, human checkpoint. Open `trajectories/03-nop-already-green__final.md` and show inspector → runner → verdict.

Then 20 seconds on a clean submit:

```bash
python3 -m taskgate review packs/01-hours-rollup
```

**2:10–3:20 — Changelog, the change that mattered, the one we removed**

```bash
python3 -m taskgate eval --stage all
```

Point at the jump **50% → 75%** when the runner landed (iteration 2). That is the main contribution inside Taskgate.

Then: “We tried listing filenames without running tests. It went 42% to 50% and still submitted a pack whose oracle fails. We removed that as the primary reviewer.”

Then 20 seconds on the other baseline:

```bash
python3 -m taskgate eval --stage agent_baseline
```

“A general-purpose agent with the full pack: 10 out of 12 majority. Three trials did not agree — 92, 67, 83. One trial applied the oracle in place and then called fair packs too easy. Taskgate copies first, so that cannot happen.”

Show `CHANGELOG.md` for one beat.

**3:20–4:10 — Comparison + hard case**

```bash
python3 -m taskgate review packs/12-reskin-rollup
```

“Locally this pack is healthy. Memory says it is a reskin of hours-rollup. That is the diversity fail.”

```bash
python3 -m taskgate review packs/11-timestamp-fold
```

“This one is hard to *solve*, but the instruction is fair. The agent submits. That is the challenging case.”

**4:10–4:30 — Close**

“Headline: instruction-only 5/12, general-purpose agent 10/12, Taskgate 12/12. Three hold-out packs written after the gates: 2 out of 3. The miss is an unfair sort rule the UTC scanner cannot see. No API for Taskgate. Another person can rerun `python3 -m taskgate eval --stage all` from a clean Python 3.11 and hit the same numbers. A human still owns the upload.”

## Do not

- Do not show private AfterQuery / Revelo packs.
- Do not skip the baseline.
- Do not skip the removed experiment.
