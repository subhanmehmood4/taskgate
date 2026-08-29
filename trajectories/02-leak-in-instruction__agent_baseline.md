# Trajectory — 02-leak-in-instruction (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=reject family=leak
TASK.md leaks the exact alpha/beta totals the hidden test asserts and invites hard-coding them.
evidence=TASK.md: Expected alpha total is 8.0. Beta is 2.0. You can hard-code these if you want.
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: leak
SUMMARY: TASK.md leaks the exact alpha/beta totals the hidden test asserts and invites hard-coding them.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: Expected alpha total is 8.0. Beta is 2.0. You can hard-code these if you want.
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=leak
TASK.md explicitly states the expected alpha and beta totals that the tests assert, leaking benchmark answers in the prompt.
evidence=TASK.md: Expected alpha total is 8.0. Beta is 2.0. You can hard-code these if you want.
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: leak
SUMMARY: TASK.md explicitly states the expected alpha and beta totals that the tests assert, leaking benchmark answers in the prompt.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: Expected alpha total is 8.0. Beta is 2.0. You can hard-code these if you want.
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=reject family=leak
TASK.md reveals exact totals directly asserted by the tests.
evidence=TASK.md: Expected alpha total is 8.0. Beta is 2.0.
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: leak
SUMMARY: TASK.md reveals exact totals directly asserted by the tests.
EVIDENCE_PATH: TASK.md
EVIDENCE_SNIPPET: Expected alpha total is 8.0. Beta is 2.0.
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['leak'] votes=t1=reject/leak t2=reject/leak t3=reject/leak
```

## Final verdict: REJECT
families: leak
