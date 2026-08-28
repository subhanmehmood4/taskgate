# Hours rollup

Fix `workspace/rollup.py` so `totals(path)` returns hours summed **per project** from a CSV with columns `project` and `hours`.

Do not hard-code any project's total. Read the file. Ignore unknown extra columns if they appear later.

Return a dict mapping project name to a float total. Do not include an `"all"` key.
