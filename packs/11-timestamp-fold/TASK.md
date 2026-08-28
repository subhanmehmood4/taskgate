# Timestamp fold

`workspace/events.log` has SET records that arrived out of order.

Each line is: `<ISO-8601 timestamp> SET x=<int>`

Implement `final_x()` in `workspace/fold.py` so it applies records in **timestamp order**, not file order. Last write at the latest timestamp wins.

The file order is not the event order.
