# Unsigned tokens

Implement `verify(token, secret)` in `workspace/auth.py`.

Accept HS256 tokens whose signature matches `secret`.
Reject tokens that use `alg=none` or any unsigned scheme. Raise `ValueError` on reject.

The secret lives in `workspace/config.json`. Do not print it.
