# Trajectory — 12-reskin-rollup (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=submit family=none
Starter sums into "all" so the hidden test fails; the oracle groups by customer and the one test passes, matching TASK.md.
evidence=workspace/rollup.py: out["all"] = out.get("all", 0.0) + float(row["amount"])
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: Starter sums into "all" so the hidden test fails; the oracle groups by customer and the one test passes, matching TASK.md.
EVIDENCE_PATH: workspace/rollup.py
EVIDENCE_SNIPPET: out["all"] = out.get("all", 0.0) + float(row["amount"])
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=too_easy
The starter rollup.py already computes per-customer totals correctly and passes all tests without any changes.
evidence=NOP: Ran 1 test in 0.000s OK
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: The starter rollup.py already computes per-customer totals correctly and passes all tests without any changes.
EVIDENCE_PATH: NOP
EVIDENCE_SNIPPET: Ran 1 test in 0.000s OK
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=submit family=none
The starter fails while the oracle correctly implements the stated customer-grouped totals.
evidence=ORACLE: Ran 1 test... OK
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: The starter fails while the oracle correctly implements the stated customer-grouped totals.
EVIDENCE_PATH: ORACLE
EVIDENCE_SNIPPET: Ran 1 test... OK
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=submit families=[] votes=t1=submit/- t2=reject/too_easy t3=submit/-
```

## Final verdict: SUBMIT
