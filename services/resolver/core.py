"""Metadata-only Instagram extraction and phone-compatible format selection."""

import re
from urllib.parse import urlsplit


class ResolveError(Exception):
    def __init__(self, code):
        self.code = code
        super().__init__(code)


def normalize_url(value):
    if not isinstance(value, str) or not value.strip():
        raise ResolveError("MISSING_URL")
    try:
        parsed = urlsplit(value.strip())
        if (parsed.scheme not in ("https", "http") or parsed.username
                or parsed.password or parsed.port not in (None, 80, 443)):
            raise ValueError()
        if parsed.hostname not in {
            "instagram.com", "www.instagram.com", "m.instagram.com",
            "instagr.am", "www.instagr.am",
        }:
            raise ValueError()
        match = re.fullmatch(r"/(p|reel|reels|tv)/([A-Za-z0-9_-]{1,64})/?", parsed.path)
        if not match:
            raise ValueError()
    except ValueError:
        raise ResolveError("UNSUPPORTED_URL") from None
    kind, shortcode = match.groups()
    return f"https://www.instagram.com/{'reel' if kind == 'reels' else kind}/{shortcode}/", shortcode


def safe_cdn_url(value):
    try:
        parsed = urlsplit(value)
        return (parsed.scheme == "https" and not parsed.username and not parsed.password
                and parsed.port in (None, 443)
                and any((parsed.hostname or "").endswith("." + domain)
                        for domain in ("cdninstagram.com", "fbcdn.net")))
    except (ValueError, TypeError):
        return False


def dimension(fmt):
    return min(fmt.get("width") or 0, fmt.get("height") or 0)


def audio_kind(fmt):
    codec = fmt.get("acodec")
    if codec == "none":
        return "none"
    if isinstance(codec, str) and codec.startswith(("mp4a", "aac")):
        return "aac"
    return "unknown"


def select_format(formats, quality):
    direct = [f for f in formats if isinstance(f, dict)
                  and f.get("ext") == "mp4"
                  and f.get("protocol") == "https"
                  and not f.get("has_drm") and not f.get("fragments")
                  and not f.get("manifest_url")
                  and safe_cdn_url(f.get("url"))]
    candidates = [f for f in direct
                  if str(f.get("vcodec", "")).startswith(("avc1", "h264"))
                  and dimension(f) > 0
                  and audio_kind(f) in ("aac", "none")]
    # Never discard existing audio just to meet the preferred resolution.
    muxed = [f for f in candidates if audio_kind(f) == "aac"]
    if muxed:
        candidates = muxed
    else:
        # Instagram's progressive video_url entries often omit all codec metadata.
        # Preserve unknowns, rather than inventing codecs, dimensions or audio.
        has_separate_audio = any(isinstance(f, dict) and f.get("acodec") not in (None, "none") for f in formats)
        unknown = [f for f in direct if f.get("vcodec") is None
                   and (f.get("acodec") is None or (f.get("acodec") == "none" and not has_separate_audio))
                   and not str(f.get("format_id", "")).startswith("dash-")]
        if unknown:
            return unknown[-1]
        if any(isinstance(f, dict) and f.get("acodec") not in (None, "none") for f in formats):
            if candidates:
                raise ResolveError("MERGE_REQUIRED")
        if not candidates:
            raise ResolveError("NO_COMPATIBLE_MEDIA")
    target = {"720p": 720, "data-saver": 480}.get(quality)
    if target:
        under = [f for f in candidates if dimension(f) <= target]
        if under:
            candidates = under
        else:
            return min(candidates, key=dimension)
    return max(candidates, key=lambda f: (dimension(f), f.get("tbr") or 0))


def build_result(info, url, shortcode, quality):
    if not isinstance(info, dict):
        raise ResolveError("NO_MEDIA_FOUND")
    entries = info.get("entries") if info.get("_type") == "playlist" else [info]
    entries = list(entries or [])
    if not entries:
        raise ResolveError("NO_MEDIA_FOUND")
    warnings = ["DIRECT_URL_EXPIRES: Download promptly; resolve again if the CDN rejects it."]
    if info.get("_type") == "playlist":
        warnings.append("VIDEO_ITEMS_ONLY: The extractor may omit photos; album completeness is not guaranteed.")
    if len(entries) > 10:
        warnings.append("ITEM_LIMIT: Only the first 10 items were resolved.")
    items = []
    for entry in entries[:10]:
        if not isinstance(entry, dict):
            raise ResolveError("NO_MEDIA_FOUND")
        fmt = select_format(entry.get("formats") or [], quality)
        unknown = audio_kind(fmt) == "unknown" or fmt.get("vcodec") is None
        has_audio = None if audio_kind(fmt) == "unknown" else audio_kind(fmt) == "aac"
        if has_audio is False:
            warnings.append(f"NO_AUDIO: Item {len(items) + 1} has no reported audio track.")
        if unknown:
            warnings.append(f"COMPATIBILITY_UNVERIFIED: Item {len(items) + 1} is a direct MP4; some codec, audio or quality metadata is missing. Null fields mean unknown.")
        headers = {**(entry.get("http_headers") or {}), **(fmt.get("http_headers") or {})}
        if any(key.lower() in ("cookie", "authorization") for key in headers):
            raise ResolveError("NO_COMPATIBLE_MEDIA")
        items.append({
            "type": "video", "url": fmt["url"],
            "filename": f"instagram_{shortcode}_{len(items) + 1}.mp4",
            "mimeType": "video/mp4", "width": fmt.get("width"),
            "height": fmt.get("height"), "hasAudio": has_audio,
            "videoCodec": fmt.get("vcodec"), "audioCodec": fmt.get("acodec"),
            "compatibility": "unverified" if unknown else "metadata-compatible",
            "downloadHeaders": {k: v for k, v in headers.items()
                                if k.lower() in ("user-agent", "referer", "accept")},
        })
    return {"status": "ok", "source": "instagram", "inputUrl": url,
            "items": items, "warnings": warnings}
