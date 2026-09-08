"""Verify public signed downloads exactly match local signed artifacts."""
import hashlib
from pathlib import Path
import httpx

root = Path(__file__).resolve().parent.parent
token = (root / "services/resolver/.env.production.local").read_text().strip().split("=",1)[1]
with httpx.Client(proxy="http://127.0.0.1:7897",timeout=30,trust_env=False) as client:
    for name in ("shunshou", "shunshou-check"):
        signed = (root / f"shortcuts/build/{name}.shortcut").read_bytes()
        unsigned = (root / f"shortcuts/build/{name}.unsigned.shortcut").read_bytes()
        assert token.encode() not in unsigned
        response = client.get(f"https://shunshou-resolver.vercel.app/{name}.shortcut")
        response.raise_for_status()
        assert len(signed) > 1000
        assert hashlib.sha256(response.content).digest() == hashlib.sha256(signed).digest()
        assert response.headers.get("content-type", "").startswith("application/octet-stream")
        assert "attachment" in response.headers.get("content-disposition", "")
        print(f"{name}: HTTP {response.status_code}, {len(signed)} bytes, signed artifact hash matches; no token in source.")
