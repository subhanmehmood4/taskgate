# Trajectory — 05-unfair-hidden-comment (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=reject family=unfair
Tests require UTC tzinfo and a Z/+00:00 suffix that TASK.md never states and contradicts by forbidding invented fields.
evidence=tests/test_task.py: self.assertEqual(got.tzinfo, timezone.utc)
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: unfair
SUMMARY: Tests require UTC tzinfo and a Z/+00:00 suffix that TASK.md never states and contradicts by forbidding invented fields.
EVIDENCE_PATH: tests/test_task.py
EVIDENCE_SNIPPET: self.assertEqual(got.tzinfo, timezone.utc)
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=too_easy
The starter parse_stamp already attaches UTC and passes the only hidden test without any changes.
evidence=NOP: Ran 1 test in 0.000s OK
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: The starter parse_stamp already attaches UTC and passes the only hidden test without any changes.
EVIDENCE_PATH: NOP
EVIDENCE_SNIPPET: Ran 1 test in 0.000s OK
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=reject family=unfair
Tests require an unstated UTC timezone that contradicts the naive no-offset task.
evidence=TASK.md: Do not invent fields that are not in the string.
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: unfair
SUMMARY: Tests require an unstated UTC timezone that contradicts the naive no-offset task.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: Do not invent fields that are not in the string.
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['unfair'] votes=t1=reject/unfair t2=reject/too_easy t3=reject/unfair
```

## Final verdict: REJECT
families: unfair
