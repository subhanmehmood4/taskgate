# Trajectory — 11-timestamp-fold (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=submit family=none
Starter folds file order (NOP 9!=5); oracle sorts by timestamp and the one test passes; TASK.md states last-write-wins.
evidence=NOP: AssertionError: 9 != 5
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: Starter folds file order (NOP 9!=5); oracle sorts by timestamp and the one test passes; TASK.md states last-write-wins.
EVIDENCE_PATH: NOP
EVIDENCE_SNIPPET: AssertionError: 9 != 5
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=too_easy
The starter already sorts events by timestamp and returns the latest value, so hidden tests pass with no agent work.
evidence=workspace/fold.py: rows.sort(key=lambda row: row[0]); return rows[-1][1]
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: The starter already sorts events by timestamp and returns the latest value, so hidden tests pass with no agent work.
EVIDENCE_PATH: workspace/fold.py
EVIDENCE_SNIPPET: rows.sort(key=lambda row: row[0]); return rows[-1][1]
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=submit family=none
The starter fails timestamp ordering, while the oracle fixes it and passes.
evidence=TASK.md: applies records in timestamp order, not file order
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: The starter fails timestamp ordering, while the oracle fixes it and passes.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: applies records in timestamp order, not file order
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=submit families=[] votes=t1=submit/- t2=reject/too_easy t3=submit/-
```

## Final verdict: SUBMIT
