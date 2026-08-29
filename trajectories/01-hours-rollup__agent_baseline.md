# Trajectory — 01-hours-rollup (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=submit family=none
Starter buckets into "all" and fails; oracle groups by project and the one hidden test passes; TASK states the required behavior without leaking totals.
evidence=TASK.md: returns hours summed **per project** from a CSV
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: Starter buckets into "all" and fails; oracle groups by project and the one hidden test passes; TASK states the required behavior without leaking totals.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: returns hours summed **per project** from a CSV
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=too_easy
Starter rollup.py already implements correct per-project CSV summation and passes all tests without modification.
evidence=workspace/rollup.py: out[key] = out.get(key, 0.0) + float(row["hours"])
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: Starter rollup.py already implements correct per-project CSV summation and passes all tests without modification.
EVIDENCE_PATH: workspace/rollup.py
EVIDENCE_SNIPPET: out[key] = out.get(key, 0.0) + float(row["hours"])
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=submit family=none
The clear behavioral task fails NOP and passes after the oracle fix.
evidence=ORACLE: Ran 1 test ... OK
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: The clear behavioral task fails NOP and passes after the oracle fix.
EVIDENCE_PATH: ORACLE
EVIDENCE_SNIPPET: Ran 1 test ... OK
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=submit families=[] votes=t1=submit/- t2=reject/too_easy t3=submit/-
```

## Final verdict: SUBMIT
