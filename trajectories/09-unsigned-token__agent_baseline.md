# Trajectory — 09-unsigned-token (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: cursor-grok-4.6
```
verdict=submit family=none
Starter fails both hidden tests, the oracle makes them pass, and TASK.md states the HS256 accept and unsigned-reject behavior the tests check.
evidence=TASK.md: Accept HS256 tokens whose signature matches `secret`. Reject tokens that use `alg=none`
NOP passed=0 failed=2
ORACLE passed=2 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: Starter fails both hidden tests, the oracle makes them pass, and TASK.md states the HS256 accept and unsigned-reject behavior the tests check.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: Accept HS256 tokens whose signature matches `secret`. Reject tokens that use `alg=none`
NOP: passed=0 failed=2
ORACLE: apply_ok=true passed=2 failed=0
```

## Step 3: agent_baseline.trial_2
- input: composer-2.5-fast
```
verdict=reject family=too_easy
Starter already implements full JWT verification; NOP passes all tests without modification.
evidence=NOP: Ran 2 tests in 0.000s OK
NOP passed=2 failed=0
ORACLE passed=2 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: Starter already implements full JWT verification; NOP passes all tests without modification.
EVIDENCE_PATH: NOP
EVIDENCE_SNIPPET: Ran 2 tests in 0.000s OK
NOP: passed=2 failed=0
ORACLE: apply_ok=true passed=2 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gpt-5.6-sol-medium
```
verdict=submit family=none
The starter fails both behavioral tests, while the official fix passes both.
evidence=ORACLE: Ran 2 tests / OK
NOP passed=0 failed=2
ORACLE passed=2 failed=0
VERDICT: submit
FAMILY: none
SUMMARY: The starter fails both behavioral tests, while the official fix passes both.
EVIDENCE_PATH: ORACLE
EVIDENCE_SNIPPET: Ran 2 tests / OK
NOP: passed=0 failed=2
ORACLE: apply_ok=true passed=2 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=submit families=[] votes=t1=submit/- t2=reject/too_easy t3=submit/-
```

## Final verdict: SUBMIT
