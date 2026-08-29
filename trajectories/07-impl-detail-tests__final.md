# Trajectory — 07-impl-detail-tests (final)

## Step 1: skill.eval_task_review
- input: taskgate/skills/eval_task_review.md
```
# Eval task review skill

You are a pre-submit reviewer for Harbor-style coding-agent evaluation packs.

A pack is SUBMIT only if every statement below is true:

1. TASK.md does not contain expected outputs, flags, or numeric answers that hidden tests check.
2. Filenames do not advertise the answer.
3. NOP (run tests on the starter, change nothing) is red.
4. Oracle (apply the official fix, then run tests) is green.
5. TASK.md states every requirement the tests enforce. Comments and leftover files do not count.
6. Tests assert observable behavior, not function names or private attributes.
7. The solving mechanic is not a reskin of a pack already in reviewer memory.

If any statement is false, REJECT and name the family:
leak | too_easy | oracle_fail | incomplete_oracle | unfair | impl_detail | similarity | malformed

Every claim must cite a path and a snippet. If you cannot point at a fi
```

## Step 2: inspector.list_files
- input: 07-impl-detail-tests
```
TASK.md
oracle/apply.py
tests/test_task.py
workspace/stats.py
```

## Step 3: inspector.structure
- input: 07-impl-detail-tests
```
ok
```

## Step 4: leak.scan
- input: TASK.md + filenames vs test literals
```
0 finding(s)
```

## Step 5: runner.nop
- input: unittest on starter
```
passed=0 failed=1
cent call last):
  File "tests/test_task.py", line 13, in test_locked_name_and_private
    self.assertEqual(stats.compute_widget_score.__name__, "compute_widget_score")
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^
AttributeError: module 'stats' has no attribute 'compute_widget_score'

----------------------------------------------------------------------
Ran 1 test in 0.000s

FAILED (errors=1)

```

## Step 6: runner.oracle
- input: apply.py then unittest
```
apply_ok=True passed=1 failed=0
.
----------------------------------------------------------------------
Ran 1 test in 0.000s

OK

```

## Step 7: fairness.scan
- input: tests vs TASK.md vs comments
```
2 finding(s)
```

## Step 8: memory.mechanics
- input: taskgate/memory/mechanics.yml
```
0 finding(s)
```

## Step 9: verifier.citations
- input: 2 findings
```
kept=2 dropped=0
```

## Final verdict: REJECT
families: impl_detail
