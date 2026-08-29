# Trajectory — 07-impl-detail-tests (agent_baseline)

## Step 1: agent_baseline.prompt
- input: eval/agent_baseline_prompt.md
```
full pack + shell; no skill file; no mechanics.yml; no gold labels
```

## Step 2: agent_baseline.trial_1
- input: gp-agent-A
```
verdict=reject family=impl_detail
Tests require the exact name compute_widget_score and a private _scratch attribute, which TASK.md never specifies as behavior.
evidence=tests/test_task.py: self.assertEqual(stats.compute_widget_score.__name__, "compute_widget_score")
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: impl_detail
SUMMARY: Tests require the exact name compute_widget_score and a private _scratch attribute, which TASK.md never specifies as behavior.
EVIDENCE_PATH: tests/test_task.py
EVIDENCE_SNIPPET: self.assertEqual(stats.compute_widget_score.__name__, "compute_widget_score")
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 3: agent_baseline.trial_2
- input: gp-agent-B
```
verdict=reject family=impl_detail
Tests require the locked function name compute_widget_score and private _scratch, neither stated in TASK.md.
evidence=tests/test_task.py: self.assertEqual(stats.compute_widget_score.__name__, "compute_widget_score")
NOP passed=1 failed=0
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: impl_detail
SUMMARY: Tests require the locked function name compute_widget_score and private _scratch, neither stated in TASK.md.
EVIDENCE_PATH: tests/test_task.py
EVIDENCE_SNIPPET: self.assertEqual(stats.compute_widget_score.__name__, "compute_widget_score")
NOP: passed=1 failed=0
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 4: agent_baseline.trial_3
- input: gp-agent-C
```
verdict=reject family=impl_detail
Tests enforce an unstated function name and private mutable state.
evidence=tests/test_task.py: self.assertTrue(hasattr(stats, "_scratch"))
NOP passed=0 failed=1
ORACLE passed=1 failed=0
VERDICT: reject
FAMILY: impl_detail
SUMMARY: Tests enforce an unstated function name and private mutable state.
EVIDENCE_PATH: tests/test_task.py
EVIDENCE_SNIPPET: self.assertTrue(hasattr(stats, "_scratch"))
NOP: passed=0 failed=1
ORACLE: apply_ok=true passed=1 failed=0
```

## Step 5: agent_baseline.majority
- input: 3 trials
```
verdict=reject families=['impl_detail'] votes=t1=reject/impl_detail t2=reject/impl_detail t3=reject/impl_detail
```

## Final verdict: REJECT
families: impl_detail
