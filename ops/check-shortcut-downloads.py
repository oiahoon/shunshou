"""Verify public signed downloads exactly match local signed artifacts."""
import hashlib
import os
from pathlib import Path
import httpx

root = Path(__file__).resolve().parent.parent
token = (root / "services/resolver/.env.production.local").read_text().strip().split("=",1)[1]
with httpx.Client(proxy=os.getenv("SMOKE_PROXY"),timeout=30,trust_env=False) as client:
    for name in ("shunshou", "shunshou-check"):
        signed = (root / "shortcuts/build/shunshou.shortcut").read_bytes()
        unsigned = (root / "shortcuts/build/shunshou.unsigned.shortcut").read_bytes()
        assert token.encode() not in unsigned
        response = client.get(f"https://shunshou.miaowu.org/{name}.shortcut")
        response.raise_for_status()
        assert len(signed) > 1000
        assert hashlib.sha256(response.content).digest() == hashlib.sha256(signed).digest()
        assert response.headers.get("content-type", "").startswith("application/octet-stream")
        assert "attachment" in response.headers.get("content-disposition", "")
        print(f"{name}: HTTP {response.status_code}, {len(signed)} bytes, signed artifact hash matches; no token in source.")
