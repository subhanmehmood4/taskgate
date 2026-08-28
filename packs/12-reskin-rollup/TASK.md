# Customer totals

Fix `workspace/rollup.py` so `totals(path)` returns the total amount **per customer** from `orders.csv`.

Columns are `customer` and `amount`. Group, then sum. Do not hard-code any customer's total.

Return a dict mapping customer name to a float total. Do not include an `"all"` key.
