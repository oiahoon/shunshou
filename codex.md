# Codex Context

## Project

`instagram-wechat-helper` is a private Next.js App Router API for an iOS Shortcut that resolves public Instagram or Threads links into downloadable media URLs. The Shortcut downloads the media on the iPhone, saves it briefly to `IG Temp Share`, opens the iOS Share Sheet for WeChat, and then deletes temporary media.

## Hard Boundaries

- Do not proxy, stream, tunnel, cache, store, transcode, base64 encode, or upload media files from this backend.
- Do not add a public downloader UI or arbitrary URL input form.
- Do not scrape third-party downloader websites.
- Do not require Instagram login cookies for V1 behavior.
- Do not expose API tokens in client-side code or logs.
- Do not treat cover images or platform UI assets as successful Reel downloads.

## Current Architecture

The active Instagram video implementation is now `services/resolver/app.py` (FastAPI) with a bounded metadata-only yt-dlp worker. Read `services/resolver/README.md` first for its contract and validation limits. It is a standalone deployment root, not a Next.js child process or proxy. Production is https://shunshou-resolver.vercel.app on the user's verified Hobby team. Local and cloud tests passed for both sample Reels on 2026-09-08; iPhone/WeChat execution remains pending. Signed, token-free installer downloads and instructions live in `shortcuts/README.md`. Private access codes are git-ignored and must never be copied into published shortcuts or public files. Unknown codec/audio/dimension metadata must remain null and carry a warning, not be inferred from sample probe results. Threads remains on the old HTML path below.

- `app/api/resolve/route.ts`: authenticates, rate limits, normalizes supported URLs, calls the provider router, and returns stable JSON.
- `lib/url.ts`: normalizes Instagram and Threads URLs. Supported inputs are Instagram `/p`, `/reel`, `/reels`, `/tv`, and Threads `@user/post/id` URLs.
- `lib/resolver.ts`: provider router.
- `lib/instagram.ts`: Instagram HTML provider.
- `lib/threads.ts`: Threads HTML provider.
- `lib/htmlMedia.ts`: shared logged-out HTML fetch and metadata extraction, plus filtering for non-media platform assets.
- `lib/response.ts`: stable API error bodies.

## Important Live Finding

The two sampled Instagram Reels were manually confirmed by the user to contain video:

- `https://www.instagram.com/reel/DZsVvmmkqXA/?igsh=MTM2d3d5cmdqZmQ1aQ==`
- `https://www.instagram.com/reel/DZwITAaBfBE/?igsh=cXFkZ3hraHNha24x`

With local proxy enabled, logged-out public HTML returned `HTTP 200` but exposed only `og:image` and no `og:video`, `video_url`, or `.mp4`. The API now returns `404 NO_MEDIA_FOUND` for these Reels. This is a resolver limitation, not proof that the Reel has no video.

Do not regress to returning the cover image for a Reel just to produce `status: ok`. For the Shortcut, that is a false success.

## Local Proxy Testing

The user's local proxy is Clash/Mihomo on `127.0.0.1:7897`. `curl` can use proxy env vars directly, but Node fetch also needs `NODE_OPTIONS=--use-env-proxy`.

Use:

```bash
NODE_OPTIONS=--use-env-proxy \
HTTPS_PROXY=http://127.0.0.1:7897 \
HTTP_PROXY=http://127.0.0.1:7897 \
ALL_PROXY=socks5://127.0.0.1:7897 \
API_TOKENS=joey-dev-token \
REQUEST_TIMEOUT_MS=15000 \
pnpm dev
```

Then test:

```bash
curl -s -i -X POST http://localhost:3000/api/resolve \
  -H 'Content-Type: application/json' \
  -H 'Authorization: Bearer joey-dev-token' \
  -d '{"url":"https://www.instagram.com/reel/DZsVvmmkqXA/"}'
```

## Resolver Direction

The likely next step is not more regex over the same logged-out HTML. Better options:

- Add a `CobaltProvider` only for a self-hosted or explicitly authorized Cobalt instance.
- Accept only direct media URLs or picker lists of direct media URLs from a provider.
- Reject provider modes that tunnel/proxy media through this backend unless the product constraint changes.
- Investigate browser-based extraction or another authorized provider if direct public HTML keeps hiding Reel video URLs.
- Keep Threads support behind the same provider interface; URL normalization is implemented, but live HTML fetching may fail depending on proxy/network behavior.

## Verification Checklist

Run these before handoff when code changes:

```bash
corepack pnpm test
corepack pnpm typecheck
corepack pnpm lint
corepack pnpm build
```

For live resolver changes, also run proxy-backed API checks against the sample Reel URLs and a Threads URL. Record exact HTTP status and JSON response; do not collapse `NO_MEDIA_FOUND`, `RESOLVE_FAILED`, and true success into one bucket.
