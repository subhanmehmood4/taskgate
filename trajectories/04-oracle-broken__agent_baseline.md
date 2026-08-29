# Trajectory — 04-oracle-broken (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: cursor-grok-4.6
```
verdict=reject family=oracle_fail
Official oracle writes subtraction instead of addition, so tests still fail after apply.
evidence=oracle/apply.py: return a - b
NOP passed=0 failed=1
ORACLE passed=0 failed=1
VERDICT: reject
FAMILY: oracle_fail
SUMMARY: Official oracle writes subtraction instead of addition, so tests still fail after apply.
EVIDENCE_PATH: oracle/apply.py
EVIDENCE_SNIPPET: return a - b
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=0 failed=1
```

## Step 3: agent_baseline.trial_2
- input: composer-2.5-fast
```
verdict=reject family=oracle_fail
The official oracle writes subtraction code, so tests still fail after apply.
evidence=oracle/apply.py: # Wrong oracle: subtracts instead of adding.
NOP passed=0 failed=1
ORACLE passed=0 failed=1
VERDICT: reject
FAMILY: oracle_fail
SUMMARY: The official oracle writes subtraction code, so tests still fail after apply.
EVIDENCE_PATH: oracle/apply.py
EVIDENCE_SNIPPET: # Wrong oracle: subtracts instead of adding.
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=0 failed=1
```

## Step 4: agent_baseline.trial_3
- input: gpt-5.6-sol-medium
```
verdict=reject family=oracle_fail
The official oracle implements subtraction, so the required addition test still fails.
evidence=ORACLE: AssertionError: -1 != 9
NOP passed=0 failed=1
ORACLE passed=0 failed=1
VERDICT: reject
FAMILY: oracle_fail
SUMMARY: The official oracle implements subtraction, so the required addition test still fails.
EVIDENCE_PATH: ORACLE
EVIDENCE_SNIPPET: AssertionError: -1 != 9
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=0 failed=1
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['oracle_fail'] votes=t1=reject/oracle_fail t2=reject/oracle_fail t3=reject/oracle_fail
```

## Final verdict: REJECT
families: oracle_fail
