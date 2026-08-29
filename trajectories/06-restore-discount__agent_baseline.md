# Trajectory — 06-restore-discount (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: cursor-grok-4.6
```
verdict=submit family=none
Starter fails the over-100 discount case and the official restore makes both hidden tests pass.
evidence=NOP: AssertionError: 120 != 108
NOP passed=1 failed=1
ORACLE passed=2 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: Starter fails the over-100 discount case and the official restore makes both hidden tests pass.
EVIDENCE_PATH: NOP
EVIDENCE_SNIPPET: AssertionError: 120 != 108
NOP: passed=1 failed=1
ORACLE: apply_ok=true passed=2 failed=0
```

## Step 3: agent_baseline.trial_2
- input: composer-2.5-fast
```
verdict=reject family=too_easy
The starter already implements the discount rule from backup.log, so NOP passes all tests without any changes.
evidence=workspace/app.py: if amount > 100: return int(amount * 0.9)
NOP passed=2 failed=0
ORACLE passed=2 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: The starter already implements the discount rule from backup.log, so NOP passes all tests without any changes.
EVIDENCE_PATH: workspace/app.py
EVIDENCE_SNIPPET: if amount > 100: return int(amount * 0.9)
NOP: passed=2 failed=0
ORACLE: apply_ok=true passed=2 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gpt-5.6-sol-medium
```
verdict=reject family=leak
The task explicitly points to a backup containing the exact implementation tested.
evidence=workspace/backup.log: if total > 100: return int(total * 0.9)
NOP passed=1 failed=1
ORACLE passed=2 failed=0
VERDICT: reject
FAMILY: leak
SUMMARY: The task explicitly points to a backup containing the exact implementation tested.
EVIDENCE_PATH: workspace/backup.log
EVIDENCE_SNIPPET: if total > 100: return int(total * 0.9)
NOP: passed=1 failed=1
ORACLE: apply_ok=true passed=2 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['too_easy'] votes=t1=submit/- t2=reject/too_easy t3=reject/leak
```

## Final verdict: REJECT
families: too_easy
