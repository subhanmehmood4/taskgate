# Trajectory — 09-unsigned-token (iter4)

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
- input: 09-unsigned-token
```
TASK.md
oracle/apply.py
tests/test_task.py
workspace/auth.py
workspace/config.json
```

## Step 3: inspector.structure
- input: 09-unsigned-token
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
passed=0 failed=2
-----------------------------------------------------------
Traceback (most recent call last):
  File "tests/test_task.py", line 35, in test_rejects_unsigned
    with self.assertRaises(ValueError):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
AssertionError: ValueError not raised

----------------------------------------------------------------------
Ran 2 tests in 0.001s

FAILED (failures=1, errors=1)

```

## Step 6: runner.oracle
- input: apply.py then unittest
```
apply_ok=True passed=2 failed=0
..
----------------------------------------------------------------------
Ran 2 tests in 0.000s

OK

```

## Step 7: fairness.scan
- input: tests vs TASK.md vs comments
```
0 finding(s)
```

## Step 8: memory.mechanics
- input: taskgate/memory/mechanics.yml
```
0 finding(s)
```

## Final verdict: SUBMIT
