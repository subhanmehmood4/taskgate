import base64
import hashlib
import hmac
import json
import unittest
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "workspace"))

from auth import verify  # noqa: E402


def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode()


def _token(header: dict, payload: dict, secret: str | None) -> str:
    h = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    if secret is None:
        return f"{h}.{p}."
    sig = hmac.new(secret.encode(), f"{h}.{p}".encode(), hashlib.sha256).digest()
    return f"{h}.{p}.{_b64url(sig)}"


class AuthTests(unittest.TestCase):
    def setUp(self):
        cfg = json.loads((ROOT / "workspace" / "config.json").read_text(encoding="utf-8"))
        self.secret = cfg["secret"]

    def test_rejects_unsigned(self):
        token = _token({"alg": "none", "typ": "JWT"}, {"sub": "ada"}, None)
        with self.assertRaises(ValueError):
            verify(token, self.secret)

    def test_accepts_signed(self):
        token = _token({"alg": "HS256", "typ": "JWT"}, {"sub": "ada"}, self.secret)
        self.assertEqual(verify(token, self.secret)["sub"], "ada")


if __name__ == "__main__":
    unittest.main()
