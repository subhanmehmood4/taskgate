# Hold-out (written after the gates)

Scored by `python3 -m taskgate eval --holdout`. Not part of the 12/12 fixture.

| pack | gold | pred | verdict |
|---|---|---|---|
| 13-sensor-already-green | reject / too_easy | reject / too_easy | ok |
| 14-tiebreak-in-notes | reject / unfair | submit | MISS |
| 15-window-peak | submit | submit | ok |

**2/3.** The miss is an unfair first-name tie-break that only lives in `notes.txt`. The fairness scanner only hunts UTC/Z leftovers.
