# Metadata Resolver

The new private backend for the iOS Shortcut. This standalone Python service replaces the HTML-only resolution path for Instagram video testing; it does not call the old Next.js API. No UI or Next.js proxy is required. The original implementation remains in the repository for reference and existing Threads behavior.

## Boundaries

- Python 3.12 or newer; FastAPI and pinned yt-dlp 2026.08.19.
- Only canonical public Instagram `/p`, `/reel`, `/reels`, `/tv` inputs. Tracking parameters are removed. This iteration targets videos, not Threads or photo downloading. A cover image never counts as video success. Album results carry a video-only warning because the extractor can omit photos; album completeness has not been validated.
- `download=False`, no cookies, no media proxy, storage, transcoding or FFmpeg in the server. A hard 40-second subprocess deadline kills unfinished extraction.
- URL responses are limited to HTTPS Instagram/Facebook CDN hosts. Sensitive headers are not returned. All responses are `private, no-store`.
- A valid Bearer token is required, including for health checks. Unset `API_TOKENS` rejects all requests. Tokens belong in server environment variables and the private iOS Shortcut, never frontend source, logs or query strings.
- At most two active extractions and 30 requests per token per hour **per process**. This is not a durable/global quota on multi-instance serverless hosting and is not a zero-cost guarantee. Before sharing with friends, add platform-level request limits or a durable quota, plus token revocation. Never enable billing upgrades automatically.

## Run Locally

From this directory:

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements-dev.txt
export API_TOKENS='your-private-random-token'
# Only when your local network needs the existing proxy:
export RESOLVER_PROXY='http://127.0.0.1:7897'
.venv/bin/python -m uvicorn app:app --host 127.0.0.1 --port 8021 --no-access-log
```

Local validation should be bound to loopback only. A temporary test token is not suitable for public deployment. An iPhone cannot reach a Mac service through `127.0.0.1`.

## Contract

`POST /api/resolve`

```http
Authorization: Bearer <private-token>
Content-Type: application/json
```

```json
{"url":"https://www.instagram.com/reel/DZsVvmmkqXA/","quality":"720p"}
```

Quality values: `720p` (default), `best`, `data-saver` (480 preferred). Resolution uses the shorter edge for portrait videos. Compatible audio is prioritized over the resolution preference. No resizing is performed. If metadata omits dimensions, the preference cannot be guaranteed.

Success retains `{status, source, inputUrl, items, warnings}` from the old API. Each item has `url`, `filename`, `mimeType`, `width`, `height`, `hasAudio`, `videoCodec`, `audioCodec`, `compatibility`, and `downloadHeaders`.

- `compatibility: metadata-compatible` means metadata reports a direct H.264 MP4 with AAC or explicitly absent audio. It does not mean device playback has been tested.
- `compatibility: unverified` is a direct progressive MP4 whose metadata is incomplete. Unknown fields remain `null`, never fabricated. This fallback excludes manifests and known VP9, DRM or separate video-only tracks with a known separate audio track.
- `hasAudio: false` means the selected format is reported as silent; `null` means unknown.
- `downloadHeaders` contains only optional User-Agent, Referer and Accept values. The Shortcut should use these when downloading directly from `items[].url`.
- CDN URLs expire and may depend on location/network. Resolve immediately before downloading. A server-side success is not proof that the iPhone can download from a different network.

Errors are `{status:"error", code, message}` with 400 validation, 401 auth, 404 no media, 413 oversized body, 422 incompatible/merge-required, 429 limited, 502 upstream failure, 503 busy or 504 timeout. Original upstream exception text is never exposed.

`GET /api/health` checks authorization and API availability only, not Instagram availability or CDN playback.

## Validation

```sh
.venv/bin/python -m pytest -q
SMOKE_API_TOKEN="$API_TOKENS" SMOKE_PROBE=1 .venv/bin/python smoke.py
```

`smoke.py` is a developer-only client, not part of the API. It calls the API and optionally uses local ffprobe to inspect CDN metadata without saving media files. It prints neither signed URLs nor tokens.

On 2026-09-08 both supplied Reels returned HTTP 200 via the local proxy:

| Reel | Independent CDN probe | Audio | Duration |
| --- | --- | --- | --- |
| DZsVvmmkqXA | H.264 MP4, 720 x 1280 | AAC | 48.087 s |
| DZwITAaBfBE | H.264 MP4, 720 x 1280 | No audio stream in returned file | 20.792 s |

The extractor omitted codec/dimension metadata for these direct formats, so API responses correctly remain `unverified`; the independent probe result is not injected or hardcoded into future responses. The second result does not establish whether Instagram's original post was intentionally silent.

## Production Deployment

Deployed on 2026-09-08 with explicit user approval to https://shunshou-resolver.vercel.app under the verified active Hobby team `joey-huangs-projects`. No paid upgrade, database, storage add-on or paid proxy was enabled. Project ID: `prj_mS9wxcp7OsjAufGuMORpKzEWLcjc`. Project root is **this directory**, not the repository root. Production `API_TOKENS` is stored as a sensitive Vercel environment variable; the git-ignored local copy is not uploaded. `RESOLVER_PROXY` is unset in the cloud.

Cloud verification: unauthenticated health returned 401, authenticated health returned 200, and both sample Reel requests returned 200. Independent client-side probes of both cloud-returned URLs found H.264 720 x 1280 and AAC audio. The second sample differs from the earlier local result, so no fixed audio assumption is made. See [shortcut installation](../../shortcuts/README.md).

For redeployment use `vercel deploy --prod --yes --scope joey-huangs-projects` from this directory. See [official FastAPI deployment documentation](https://vercel.com/docs/frameworks/backend/fastapi) and [yt-dlp embedding guidance](https://github.com/yt-dlp/yt-dlp#embedding-yt-dlp).

Remaining acceptance gates: iPhone download with returned headers, iOS Shortcut execution, and actual WeChat receipt/playback. Mac signing/importer recognition and cloud API checks do not establish those gates.
