# Trajectory — 08-partial-oracle (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=reject family=incomplete_oracle
Official oracle only raises the tax rate to 10% and still truncates 218.9 to 218, so test_half_up fails after apply.
evidence=oracle/apply.py: # Fixes tax only. Still truncates 218.9 -> 218.
NOP passed=0 failed=2
ORACLE passed=1 failed=1
VERDICT: reject
FAMILY: incomplete_oracle
SUMMARY: Official oracle only raises the tax rate to 10% and still truncates 218.9 to 218, so test_half_up fails after apply.
EVIDENCE_PATH: oracle/apply.py
EVIDENCE_SNIPPET: # Fixes tax only. Still truncates 218.9 -> 218.
NOP: passed=0 failed=2
ORACLE: apply_ok=true passed=1 failed=1
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=incomplete_oracle
Oracle apply leaves half-up rounding broken, so one test still fails after the official fix.
evidence=oracle/apply.py: Fixes tax only. Still truncates 218.9 -> 218.
NOP passed=1 failed=1
ORACLE passed=1 failed=1
VERDICT: reject
FAMILY: incomplete_oracle
SUMMARY: Oracle apply leaves half-up rounding broken, so one test still fails after the official fix.
EVIDENCE_PATH: oracle/apply.py
EVIDENCE_SNIPPET: Fixes tax only. Still truncates 218.9 -> 218.
NOP: passed=1 failed=1
ORACLE: apply_ok=true passed=1 failed=1
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=reject family=incomplete_oracle
The official fix leaves the required round-half-up behavior failing.
evidence=oracle/apply.py: Fixes tax only. Still truncates 218.9 -> 218.
NOP passed=0 failed=2
ORACLE passed=1 failed=1
VERDICT: reject
FAMILY: incomplete_oracle
SUMMARY: The official fix leaves the required round-half-up behavior failing.
EVIDENCE_PATH: oracle/apply.py
EVIDENCE_SNIPPET: Fixes tax only. Still truncates 218.9 -> 218.
NOP: passed=0 failed=2
ORACLE: apply_ok=true passed=1 failed=1
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['incomplete_oracle'] votes=t1=reject/incomplete_oracle t2=reject/incomplete_oracle t3=reject/incomplete_oracle
```

## Final verdict: REJECT
families: incomplete_oracle
