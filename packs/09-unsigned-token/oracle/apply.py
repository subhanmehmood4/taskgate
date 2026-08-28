from pathlib import Path

FIXED = r'''import base64
import hashlib
import hmac
import json


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def verify(token: str, secret: str) -> dict:
    header_b64, payload_b64, sig_b64 = token.split(".")
    header = json.loads(_b64url_decode(header_b64))
    alg = str(header.get("alg", ""))
    if alg.lower() == "none" or not sig_b64:
        raise ValueError("unsigned")
    if alg != "HS256":
        raise ValueError("alg")
    msg = f"{header_b64}.{payload_b64}".encode()
    expected = hmac.new(secret.encode(), msg, hashlib.sha256).digest()
    got = _b64url_decode(sig_b64)
    if not hmac.compare_digest(got, expected):
        raise ValueError("sig")
    return json.loads(_b64url_decode(payload_b64))
'''


def main() -> None:
    (Path("workspace") / "auth.py").write_text(FIXED, encoding="utf-8")


if __name__ == "__main__":
    main()
