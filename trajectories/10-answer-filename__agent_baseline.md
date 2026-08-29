# Trajectory — 10-answer-filename (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=reject family=leak
The workspace filename THE_TOTAL_MUST_BE_128.txt gives away the exact sum the hidden test asserts.
evidence=workspace/THE_TOTAL_MUST_BE_128.txt: THE_TOTAL_MUST_BE_128
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: leak
SUMMARY: The workspace filename THE_TOTAL_MUST_BE_128.txt gives away the exact sum the hidden test asserts.
EVIDENCE_PATH: workspace/THE_TOTAL_MUST_BE_128.txt
EVIDENCE_SNIPPET: THE_TOTAL_MUST_BE_128
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=too_easy
Starter summing.py already reads numbers.txt and returns 128, so hidden tests pass without any changes.
evidence=workspace/summing.py: return sum(int(line) for line in lines if line.strip())
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: too_easy
SUMMARY: Starter summing.py already reads numbers.txt and returns 128, so hidden tests pass without any changes.
EVIDENCE_PATH: workspace/summing.py
EVIDENCE_SNIPPET: return sum(int(line) for line in lines if line.strip())
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=reject family=leak
A workspace filename reveals the exact answer asserted by the test.
evidence=workspace/THE_TOTAL_MUST_BE_128.txt: THE_TOTAL_MUST_BE_128
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: leak
SUMMARY: A workspace filename reveals the exact answer asserted by the test.
EVIDENCE_PATH: workspace/THE_TOTAL_MUST_BE_128.txt
EVIDENCE_SNIPPET: THE_TOTAL_MUST_BE_128
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['leak'] votes=t1=reject/leak t2=reject/too_easy t3=reject/leak
```

## Final verdict: REJECT
families: leak
