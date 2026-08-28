import base64
import hashlib
import hmac
import json


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _b64url_decode(text: str) -> bytes:
    pad = "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(text + pad)


def verify(token: str, secret: str) -> dict:
    header_b64, payload_b64, _sig = token.split(".")
    header = json.loads(_b64url_decode(header_b64))
    # BUG: unsigned tokens are trusted.
    if str(header.get("alg", "")).lower() == "none":
        return json.loads(_b64url_decode(payload_b64))
    raise ValueError("unverified")
