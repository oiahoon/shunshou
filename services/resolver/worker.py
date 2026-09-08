"""Runs in a killable subprocess. Never downloads media or writes extraction files."""

import json
import os
import sys

from yt_dlp import YoutubeDL
from core import ResolveError, build_result, normalize_url


class QuietLogger:
    def debug(self, *_): pass
    def warning(self, *_): pass
    def error(self, *_): pass


def main():
    try:
        request = json.loads(sys.stdin.read(4096))
        url, shortcode = normalize_url(request["url"])
        options = {
            "quiet": True, "no_warnings": True, "logger": QuietLogger(),
            "skip_download": True, "cachedir": False, "socket_timeout": 10,
            "retries": 0, "extractor_retries": 0, "ignoreerrors": False,
            "playlistend": 11, "noprogress": True,
            "proxy": os.getenv("RESOLVER_PROXY", ""),
        }
        with YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=False, ie_key="Instagram")
        result = build_result(info, url, shortcode, request["quality"])
    except ResolveError as error:
        result = {"status": "error", "code": error.code}
    except Exception:
        # Upstream exceptions can contain signed URLs; never forward or log them.
        result = {"status": "error", "code": "RESOLVE_FAILED"}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
