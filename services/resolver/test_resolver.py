import asyncio
import json

import pytest
from fastapi.testclient import TestClient

import app as api
from core import ResolveError, build_result, normalize_url, safe_cdn_url, select_format

URL = "https://www.instagram.com/reel/DZsVvmmkqXA/"
CDN = "https://scontent.cdninstagram.com/video.mp4?signature=example"


def fmt(width=720, codec="avc1.4D401F", audio="mp4a.40.2", **extra):
    return {"url": CDN, "width": width, "height": width * 16 // 9 if width else None,
            "vcodec": codec, "acodec": audio, "ext": "mp4", "protocol": "https", **extra}


@pytest.mark.parametrize("url", ["https://localhost/reel/a/", "https://instagram.com.evil.test/reel/a/",
    "https://user:pass@instagram.com/reel/a/", "https://instagram.com:999/reel/a/",
    "file:///etc/passwd", "https://instagram.com/stories/a", "https://threads.com/@a/post/b"])
def test_reject_unsupported_inputs(url):
    with pytest.raises(ResolveError, match="UNSUPPORTED_URL"):
        normalize_url(url)


def test_normalization():
    assert normalize_url("https://m.instagram.com/reels/ABC/?igsh=tracking") == (
        "https://www.instagram.com/reel/ABC/", "ABC")


@pytest.mark.parametrize("url", ["http://s.cdninstagram.com/v.mp4", "https://127.0.0.1/v.mp4",
    "https://s.cdninstagram.com.evil.test/v.mp4", "https://u:p@s.fbcdn.net/v.mp4"])
def test_cdn_guard(url):
    assert not safe_cdn_url(url)


def test_prefer_muxed_720_over_video_only_1080():
    assert select_format([fmt(1080, audio="none"), fmt()], "720p")["width"] == 720


def test_portrait_resolution_is_short_edge():
    assert select_format([fmt(1080), fmt(), fmt(480)], "720p")["width"] == 720
    assert select_format([fmt(1080), fmt()], "best")["width"] == 1080
    assert select_format([fmt(), fmt(480)], "data-saver")["width"] == 480


def test_resolution_is_preference_not_silent_audio_loss():
    assert select_format([fmt(1080), fmt(480, audio="none")], "720p")["width"] == 1080


@pytest.mark.parametrize("formats", [[fmt(codec="vp9")], [fmt(protocol="m3u8_native")],
    [fmt(has_drm=True)], [fmt(audio=None)], [], [fmt(url="https://example.com/video.mp4")]])
def test_reject_incompatible_media(formats):
    with pytest.raises(ResolveError, match="NO_COMPATIBLE_MEDIA"):
        select_format(formats, "720p")


def test_do_not_drop_separate_audio():
    with pytest.raises(ResolveError, match="MERGE_REQUIRED"):
        select_format([fmt(audio="none"), fmt(codec="none")], "720p")


def test_silent_video_is_explicit():
    result = build_result({"formats": [fmt(audio="none")]}, URL, "ABC", "720p")
    assert result["items"][0]["hasAudio"] is False
    assert any(w.startswith("NO_AUDIO") for w in result["warnings"])


def test_cover_is_never_video():
    with pytest.raises(ResolveError, match="NO_COMPATIBLE_MEDIA"):
        build_result({"thumbnail": CDN}, URL, "ABC", "720p")


def test_unknown_progressive_metadata_remains_unknown():
    unknown = fmt(codec=None, audio=None, width=None, height=None)
    result = build_result({"formats": [unknown]}, URL, "ABC", "720p")
    item = result["items"][0]
    assert item["hasAudio"] is None
    assert item["width"] is None
    assert item["videoCodec"] is None
    assert item["compatibility"] == "unverified"
    assert any(w.startswith("COMPATIBILITY_UNVERIFIED") for w in result["warnings"])


def test_unknown_manifest_is_not_progressive_fallback():
    with pytest.raises(ResolveError, match="NO_COMPATIBLE_MEDIA"):
        select_format([fmt(codec=None, audio=None, manifest_url=CDN)], "720p")


def test_unknown_video_with_known_absent_audio():
    result = build_result({"formats": [fmt(codec=None, audio="none")]}, URL, "ABC", "720p")
    assert result["items"][0]["hasAudio"] is False
    assert result["items"][0]["compatibility"] == "unverified"


def test_unknown_video_must_not_drop_separate_audio():
    with pytest.raises(ResolveError):
        select_format([fmt(codec=None, audio="none"), fmt(codec="none")], "720p")


def test_no_sensitive_headers():
    with pytest.raises(ResolveError, match="NO_COMPATIBLE_MEDIA"):
        build_result({"formats": [fmt(http_headers={"Cookie": "secret"})]}, URL, "ABC", "720p")


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("API_TOKENS", "test-only-token")
    api.requests_by_token.clear()
    async def fake_worker(url, quality):
        return build_result({"formats": [fmt()]}, url, "ABC", quality)
    monkeypatch.setattr(api, "run_worker", fake_worker)
    with TestClient(api.app) as client:
        client.headers["Authorization"] = "Bearer test-only-token"
        yield client


def test_authentication_fail_closed(client, monkeypatch):
    assert client.post("/api/resolve", headers={"Authorization": "Bearer bad"}, json={"url":URL}).status_code == 401
    monkeypatch.delenv("API_TOKENS")
    assert client.get("/api/health").status_code == 401


def test_success_contract(client):
    r = client.post("/api/resolve", json={"url": URL})
    assert r.status_code == 200
    assert r.headers["cache-control"] == "private, no-store"
    assert r.json()["items"][0]["url"] == CDN
    assert r.json()["status"] == "ok"


@pytest.mark.parametrize("body,code", [(None,"INVALID_JSON"), ([],"INVALID_JSON"),
    ({},"MISSING_URL"), ({"url":URL,"quality":"bad"},"INVALID_QUALITY"),
    ({"url":URL,"quality":{}},"INVALID_QUALITY")])
def test_bad_requests(client, body, code):
    assert client.post("/api/resolve", content=json.dumps(body)).json()["code"] == code


def test_body_limit_and_invalid_json(client):
    assert client.post("/api/resolve", content="x" * 4097).status_code == 413
    assert client.post("/api/resolve", content="{").json()["code"] == "INVALID_JSON"


def test_rate_limit(client):
    for _ in range(30):
        assert client.post("/api/resolve", json={"url":URL}).status_code == 200
    assert client.post("/api/resolve", json={"url":URL}).status_code == 429


def test_upstream_errors_are_sanitized(client, monkeypatch):
    async def broken(*_):
        raise RuntimeError("secret signed URL and token")
    monkeypatch.setattr(api, "run_worker", broken)
    response = client.post("/api/resolve", json={"url":URL})
    assert response.status_code == 500
    assert "secret" not in response.text


def test_timeout_response(client, monkeypatch):
    async def slow(*_):
        raise ResolveError("TIMEOUT")
    monkeypatch.setattr(api, "run_worker", slow)
    assert client.post("/api/resolve", json={"url":URL}).status_code == 504


def test_busy_response(client, monkeypatch):
    monkeypatch.setattr(api, "slots", asyncio.Semaphore(0))
    assert client.post("/api/resolve", json={"url":URL}).status_code == 503


def test_worker_is_reaped_after_timeout(monkeypatch):
    class Process:
        returncode = None
        killed = False
        waited = False
        async def communicate(self, _):
            raise TimeoutError()
        def kill(self):
            self.killed = True
        async def wait(self):
            self.waited = True
            self.returncode = -9
    process = Process()
    async def spawn(*args, **kwargs):
        assert args[1].endswith("worker.py")
        assert kwargs["stderr"] == asyncio.subprocess.DEVNULL
        return process
    monkeypatch.setattr(api.asyncio, "create_subprocess_exec", spawn)
    with pytest.raises(ResolveError, match="TIMEOUT"):
        asyncio.run(api.run_worker(URL, "720p"))
    assert process.killed and process.waited


def test_worker_success_without_shell(monkeypatch):
    expected = build_result({"formats": [fmt()]}, URL, "ABC", "720p")
    class Process:
        returncode = 0
        async def communicate(self, body):
            assert json.loads(body) == {"url":URL, "quality":"720p"}
            return json.dumps(expected).encode(), b""
    async def spawn(*args, **kwargs):
        assert len(args) == 2
        return Process()
    monkeypatch.setattr(api.asyncio, "create_subprocess_exec", spawn)
    assert asyncio.run(api.run_worker(URL, "720p")) == expected
