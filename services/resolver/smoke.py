"""Explicit live API check. Prints metadata, never signed URLs or credentials."""

import json
import os
import subprocess

import httpx

base = os.getenv("RESOLVER_BASE_URL", "http://127.0.0.1:8021")
token = os.environ["SMOKE_API_TOKEN"]
failed = False
if os.getenv("SMOKE_HEALTH") == "1":
    with httpx.Client(timeout=30, trust_env=False, proxy=os.getenv("SMOKE_PROXY")) as client:
        for authorized in (False, True):
            r = client.get(base + "/api/health", headers={"Authorization": f"Bearer {token}"} if authorized else {})
            print(json.dumps({"health":True,"authorized":authorized,"status":r.status_code,"contentType":r.headers.get("content-type")}), flush=True)
            if r.status_code != (200 if authorized else 401):
                raise SystemExit("Unexpected API authentication response.")
for shortcode in ("DZsVvmmkqXA", "DZwITAaBfBE"):
    with httpx.Client(timeout=50, trust_env=False, proxy=os.getenv("SMOKE_PROXY")) as client:
        r = client.post(base + "/api/resolve", headers={"Authorization": f"Bearer {token}"},
                        json={"url": f"https://www.instagram.com/reel/{shortcode}/", "quality":"720p"})
    data = r.json()
    if r.status_code != 200 or data.get("status") != "ok" or not data.get("items"):
        failed = True
    summary = {"shortcode":shortcode, "httpStatus":r.status_code, "status":data.get("status"),
               "code":data.get("code"), "warnings":data.get("warnings")}
    summary["items"] = [{k:v for k,v in item.items() if k not in ("url","downloadHeaders")}
                        for item in data.get("items", [])]
    if os.getenv("SMOKE_PROBE") == "1" and data.get("items"):
        item = data["items"][0]
        command = ["ffprobe", "-v", "error"]
        if os.getenv("RESOLVER_PROXY"):
            command += ["-http_proxy", os.environ["RESOLVER_PROXY"]]
        headers = "".join(f"{k}: {v}\r\n" for k,v in item["downloadHeaders"].items())
        command += ["-headers",headers,"-rw_timeout","15000000","-show_entries",
                    "stream=codec_name,codec_type,width,height:format=duration", "-of","json",item["url"]]
        try:
            probe = subprocess.run(command, capture_output=True, timeout=25)
            summary["probe"] = json.loads(probe.stdout) if probe.returncode == 0 else {"status":"failed"}
        except (subprocess.TimeoutExpired, ValueError):
            summary["probe"] = {"status":"failed"}
        if summary["probe"].get("status") == "failed":
            failed = True
    print(json.dumps(summary, ensure_ascii=False), flush=True)
if failed:
    raise SystemExit(1)
