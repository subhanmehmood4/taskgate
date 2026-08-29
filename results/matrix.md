# Per-pack verdict matrix

Checkmark means the predicted verdict matches gold. Generated from `results/*.json`.

| pack | gold | baseline | removed | iter1 | iter2 | iter3 | iter4 | final | agent |
|---|---|---|---|---|---|---|---|---|---|
| 01-hours-rollup | submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit |
| 02-leak-in-instruction | reject | yes reject | yes reject | yes reject | yes reject | yes reject | yes reject | yes reject | yes reject |
| 03-nop-already-green | reject | no submit | no submit | no submit | yes reject | yes reject | yes reject | yes reject | yes reject |
| 04-oracle-broken | reject | no submit | no submit | no submit | yes reject | yes reject | yes reject | yes reject | yes reject |
| 05-unfair-hidden-comment | reject | no submit | no submit | no submit | no submit | yes reject | yes reject | yes reject | yes reject |
| 06-restore-discount | submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | no reject |
| 07-impl-detail-tests | reject | no submit | no submit | no submit | no submit | yes reject | yes reject | yes reject | yes reject |
| 08-partial-oracle | reject | no submit | no submit | no submit | yes reject | yes reject | yes reject | yes reject | yes reject |
| 09-unsigned-token | submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit |
| 10-answer-filename | reject | no submit | yes reject | yes reject | yes reject | yes reject | yes reject | yes reject | yes reject |
| 11-timestamp-fold | submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit | yes submit |
| 12-reskin-rollup | reject | no submit | no submit | no submit | no submit | no submit | yes reject | yes reject | no submit |
