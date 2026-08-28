# Restore discount

`workspace/app.py` used to apply a discount after summing an order.

A previous version of the discount helper is preserved in `workspace/backup.log`.
Restore that behavior: orders whose pre-discount total is over 100 get 10 percent off.

Do not change the rounding of undiscounted orders.
