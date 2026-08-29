# Trajectory — 03-nop-already-green (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: cursor-grok-4.6
```
verdict=reject family=too_easy
The starter already implements add(a, b) as a + b, so the hidden tests pass with no changes.
evidence=workspace/adder.py: return a + b
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: The starter already implements add(a, b) as a + b, so the hidden tests pass with no changes.
EVIDENCE_PATH: workspace/adder.py
EVIDENCE_SNIPPET: return a + b
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: composer-2.5-fast
```
verdict=reject family=too_easy
Starter already implements add correctly, so NOP passes all tests with no changes required.
evidence=workspace/adder.py: return a + b
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: Starter already implements add correctly, so NOP passes all tests with no changes required.
EVIDENCE_PATH: workspace/adder.py
EVIDENCE_SNIPPET: return a + b
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gpt-5.6-sol-medium
```
verdict=reject family=too_easy
The starter already implements addition and passes all tests unchanged.
evidence=NOP: Ran 1 test ... OK
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: The starter already implements addition and passes all tests unchanged.
EVIDENCE_PATH: NOP
EVIDENCE_SNIPPET: Ran 1 test ... OK
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['too_easy'] votes=t1=reject/too_easy t2=reject/too_easy t3=reject/too_easy
```

## Final verdict: REJECT
families: too_easy
