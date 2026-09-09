import asyncio
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
import sys
import time

from fastapi import FastAPI, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from core import ResolveError, normalize_url

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
public_dir = Path(__file__).with_name("public")
app.mount("/assets", StaticFiles(directory=public_dir / "assets", check_dir=False), name="assets")
slots = asyncio.Semaphore(2)
requests_by_token = {}
ERRORS = {
    "UNAUTHORIZED": (401, "Missing or invalid authorization token."),
    "INVALID_JSON": (400, "Request body must be a JSON object."),
    "MISSING_URL": (400, "Request body must include a url string."),
    "UNSUPPORTED_URL": (400, "This version supports public Instagram post, Reel and TV URLs only."),
    "INVALID_QUALITY": (400, "quality must be 720p, best or data-saver."),
    "BODY_TOO_LARGE": (413, "Request body exceeds 4096 bytes."),
    "RATE_LIMITED": (429, "Too many requests. Try again later."),
    "BUSY": (503, "Resolver is busy. Try again shortly."),
    "TIMEOUT": (504, "The upstream resolver timed out. Try again later."),
    "NO_MEDIA_FOUND": (404, "No video could be resolved; this is not proof the post has no video."),
    "NO_COMPATIBLE_MEDIA": (422, "No direct H.264 MP4 with known compatible audio was found."),
    "MERGE_REQUIRED": (422, "Audio and video require merging; this service does not merge media."),
    "RESOLVE_FAILED": (502, "Upstream extraction failed. The post may be restricted or the extractor may need updating."),
    "INTERNAL_ERROR": (500, "Unexpected resolver error."),
}


def error_response(code):
    status, message = ERRORS.get(code, ERRORS["INTERNAL_ERROR"])
    if code not in ERRORS:
        code = "INTERNAL_ERROR"
    return JSONResponse({"status": "error", "code": code, "message": message}, status_code=status)


@app.middleware("http")
async def no_cache(request, call_next):
    response = await call_next(request)
    response.headers["Cache-Control"] = "private, no-store"
    response.headers["X-Content-Type-Options"] = "nosniff"
    if request.url.path == "/":
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self'; "
            "img-src 'self' data:; object-src 'none'; base-uri 'self'; "
            "frame-ancestors 'none'; form-action 'none'"
        )
    return response


def authenticate(request):
    value = request.headers.get("authorization", "")
    parts = value.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise ResolveError("UNAUTHORIZED")
    token = parts[1].encode()
    allowed = [s.strip().encode() for s in os.getenv("API_TOKENS", "").split(",") if s.strip()]
    if not any(hmac.compare_digest(token, candidate) for candidate in allowed):
        raise ResolveError("UNAUTHORIZED")
    return hashlib.sha256(token).hexdigest()


def rate_limit(key):
    now = time.monotonic()
    for old in [k for k, (start, _) in requests_by_token.items() if now - start >= 3600]:
        del requests_by_token[old]
    start, count = requests_by_token.get(key, (now, 0))
    if count >= 30:
        raise ResolveError("RATE_LIMITED")
    requests_by_token[key] = (start, count + 1)


async def run_worker(url, quality):
    process = None
    try:
        # A thread timeout would leave extraction running; a subprocess can be killed.
        async with asyncio.timeout(40):
            # Serverless runtimes extend sys.path in-process; children need it too.
            worker_env = dict(os.environ)
            worker_env["PYTHONPATH"] = os.pathsep.join(str(Path(p).resolve()) for p in sys.path if isinstance(p, str))
            worker_env.pop("API_TOKENS", None)
            process = await asyncio.create_subprocess_exec(
                sys.executable, str(Path(__file__).with_name("worker.py")),
                stdin=asyncio.subprocess.PIPE, stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                env=worker_env,
            )
            output, _ = await process.communicate(json.dumps({"url": url, "quality": quality}).encode())
            if process.returncode != 0 or len(output) > 1024 * 1024:
                logging.getLogger(__name__).warning("resolver_worker_failed: process_exit_or_output_limit")
                raise ResolveError("RESOLVE_FAILED")
            result = json.loads(output)
            if result.get("status") != "ok":
                diagnostic = result.get("diagnostic")
                if diagnostic in {"dependency_import", "upstream_extraction", "worker_internal"}:
                    logging.getLogger(__name__).warning("resolver_worker_failed: %s", diagnostic)
                raise ResolveError(result.get("code", "RESOLVE_FAILED"))
            return result
    except TimeoutError:
        raise ResolveError("TIMEOUT") from None
    finally:
        if process is not None and process.returncode is None:
            try:
                process.kill()
            except ProcessLookupError:
                pass
            await process.wait()


@app.get("/api/health")
async def health(request: Request):
    try:
        authenticate(request)
        return {"status": "ok", "service": "metadata-resolver", "mediaProxy": False}
    except ResolveError as error:
        return error_response(error.code)


@app.get("/", include_in_schema=False)
async def homepage():
    return FileResponse(public_dir / "index.html", media_type="text/html")


@app.get("/shunshou.shortcut", include_in_schema=False)
@app.get("/shunshou-check.shortcut", include_in_schema=False)
async def shortcut_download(request: Request):
    # These two fixed routes also support local installation checks.
    name = request.url.path.rsplit("/", 1)[-1]
    return FileResponse(public_dir / name, media_type="application/octet-stream", filename="顺手.shortcut")


@app.post("/api/resolve")
async def resolve(request: Request):
    try:
        key = authenticate(request)
        rate_limit(key)
        body = bytearray()
        async with asyncio.timeout(5):
            async for chunk in request.stream():
                body.extend(chunk)
                if len(body) > 4096:
                    raise ResolveError("BODY_TOO_LARGE")
        try:
            data = json.loads(body)
        except (ValueError, UnicodeDecodeError):
            raise ResolveError("INVALID_JSON") from None
        if not isinstance(data, dict):
            raise ResolveError("INVALID_JSON")
        url, _ = normalize_url(data.get("url"))
        quality = data.get("quality", "720p")
        if quality not in ("720p", "best", "data-saver"):
            raise ResolveError("INVALID_QUALITY")
        if slots.locked():
            raise ResolveError("BUSY")
        async with slots:
            return JSONResponse(await run_worker(url, quality))
    except ResolveError as error:
        return error_response(error.code)
    except TimeoutError:
        return error_response("TIMEOUT")
    except Exception:
        return error_response("INTERNAL_ERROR")
