# Shunshou / 顺手

## Active Backend Work

The metadata-only Python/yt-dlp API lives in [`services/resolver`](services/resolver/README.md) and is deployed at https://shunshou.miaowu.org. [The single signed Shunshou 0.2 shortcut and installation instructions](shortcuts/README.md) are available. Connection checking is built in, and text comparisons are fixed. Replace an installed older version and enter the private access code again. Actual iPhone/WeChat execution of this update remains to be validated. The Next.js HTML-only implementation below remains unchanged and is not wired to this service.

## Deployment Layout

Read [AGENTS.md](AGENTS.md) for contributor/agent guardrails and [production acceptance](docs/acceptance.md) for dated verification and remaining iPhone gates. The custom-domain API and both signed installers passed 13 live checks on 2026-09-08.

- GitHub: https://github.com/oiahoon/shunshou
- Vercel project: `shunshou-resolver`, root directory `services/resolver`, framework FastAPI.
- Production branch: `main`. Use the native Vercel GitHub integration; no deployment token belongs in GitHub or source code.
- Keep production `API_TOKENS` in Vercel's sensitive environment variables. Never commit local environment files or `shortcuts/private-access-code.txt`.
- Signed, token-free shortcut installers are published from `services/resolver/public`.
- `prototypes/shunshou` is a separate UI prototype, not the production API.
- `ops/oracle-cobalt` is an archived deployment experiment, not active infrastructure.

## Legacy Next.js Reference

**Everything below documents the earlier implementation, not the deployed FastAPI service or current signed shortcuts.** For current API behavior and installation, use the links above. The legacy Photos save/delete flow below is not used by the current shortcut.

Private Vercel-hosted API for an iOS Shortcut that turns a public Instagram post, Reel, TV URL, or Threads post URL into downloadable media item URLs. The API returns JSON metadata only. It does not proxy, stream, cache, store, transcode, or return media bytes.

## Architecture

- Next.js App Router with TypeScript.
- Vercel Serverless Functions for API routes.
- Static bearer-token allowlist from `API_TOKENS`.
- Simple in-memory per-token rate limit for V1.
- Lightweight HTML metadata parser behind a `MediaResolverProvider` interface.
- Provider router with Instagram and Threads HTML providers.
- No database, storage, user registration, queue, Redis, or media proxy.

## Local Development

```bash
pnpm install
cp .env.example .env.local
pnpm dev
```

The app will run at `http://localhost:3000`.

For future Codex/agent work, read [`codex.md`](./codex.md) before changing resolver behavior.

## Environment Variables

```bash
API_TOKENS=joey-dev-token,friend-test-token
MAX_ITEMS_PER_REQUEST=10
REQUEST_TIMEOUT_MS=8000
ENABLE_DEBUG_LOGS=false
```

- `API_TOKENS`: comma-separated token allowlist. Every resolve request must send `Authorization: Bearer <token>`.
- `MAX_ITEMS_PER_REQUEST`: caps the number of returned media items.
- `REQUEST_TIMEOUT_MS`: timeout for fetching public Instagram or Threads HTML.
- `ENABLE_DEBUG_LOGS`: optional debug logging. Keep this `false` unless actively debugging.

## API

### Health

```bash
curl "http://localhost:3000/api/health"
```

Response:

```json
{
  "status": "ok",
  "service": "instagram-wechat-helper",
  "version": "1.0.0"
}
```

### Resolve

```bash
curl -X POST "http://localhost:3000/api/resolve" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer joey-dev-token" \
  -d '{"url":"https://www.instagram.com/reel/SHORTCODE/"}'
```

Success response:

```json
{
  "status": "ok",
  "source": "instagram",
  "inputUrl": "https://www.instagram.com/reel/SHORTCODE/",
  "items": [
    {
      "type": "video",
      "url": "https://example-cdn-url/video.mp4",
      "filename": "instagram-reel-SHORTCODE.mp4",
      "mimeType": "video/mp4"
    }
  ],
  "warnings": []
}
```

Error response:

```json
{
  "status": "error",
  "code": "UNSUPPORTED_URL",
  "message": "Only public Instagram post, Reel, TV, and Threads post URLs are supported."
}
```

Stable error codes:

- `UNAUTHORIZED`
- `INVALID_JSON`
- `MISSING_URL`
- `UNSUPPORTED_URL`
- `RESOLVE_FAILED`
- `NO_MEDIA_FOUND`
- `TIMEOUT`
- `RATE_LIMITED`
- `INTERNAL_ERROR`

## iOS Shortcut Setup

1. Create a Shortcut that receives `URL` or `Text` from the share sheet.
2. Extract the Instagram URL from the Shortcut input.
3. Add `Get Contents of URL`.
4. Use `POST`.
5. Set URL to `https://your-vercel-domain.vercel.app/api/resolve`.
6. Add headers:
   - `Authorization`: `Bearer YOUR_TOKEN`
   - `Content-Type`: `application/json`
7. Set request body to JSON:

```json
{
  "url": "Shortcut Input URL"
}
```

8. If `status` is `ok`, read `items`.
9. If there is more than one item, show a list and allow multiple selection.
10. For each selected item, use `Get Contents of URL` with the returned `url`.
11. Save the downloaded files to the photo album `IG Temp Share`.
12. Open the iOS Share Sheet and share to WeChat.
13. Ask `Delete temporary Instagram media?`
14. If yes, delete the saved temporary media.

If `status` is `error`, show:

```text
Could not resolve this media.
Reason: {message}
```

## Local Proxy Testing

Node fetch only uses `HTTP_PROXY` / `HTTPS_PROXY` when Node is started with env-proxy support. For local testing through Clash/Mihomo on `127.0.0.1:7897`, use:

```bash
NODE_OPTIONS=--use-env-proxy \
HTTPS_PROXY=http://127.0.0.1:7897 \
HTTP_PROXY=http://127.0.0.1:7897 \
ALL_PROXY=socks5://127.0.0.1:7897 \
pnpm dev
```

`curl` may work with proxy env vars even when Node fetch does not; test the API through the dev server before assuming the resolver can reach Instagram or Threads.

## Resolver Reality Check

Two live Reel samples were manually confirmed to contain video, but Instagram's public logged-out HTML only exposed `og:image` during local proxy testing. The V1 HTML provider therefore returns `NO_MEDIA_FOUND` for those Reels. That result means "no direct downloadable media URL was exposed to this resolver," not "the post has no video."

The current HTML provider intentionally filters platform UI assets such as `static.cdninstagram.com/rsrc.php`. Returning a cover image or Instagram UI asset for a Reel would be a false success for the Shortcut workflow.

## Existing Resolver Options

Cobalt is the most promising existing provider candidate, but hosted instances such as `api.cobalt.tools` are not intended for other projects without explicit permission. Use a self-hosted or authorized instance before adding a Cobalt provider. Cobalt responses can be `redirect`, `picker`, `tunnel`, or `local-processing`; tunnel/local-processing means the provider is proxying or processing files, which conflicts with the current backend constraint unless handled outside this API contract.

yt-dlp supports Instagram, but it is not a small Vercel Serverless dependency and its supported-sites list does not currently show Threads support.

## Deploy to Vercel

1. Push this repository to GitHub.
2. Import it in Vercel.
3. Add the environment variables from `.env.example`.
4. Deploy.
5. Test:

```bash
curl "https://your-vercel-domain.vercel.app/api/health"
```

## Personal Cobalt Instance

The separate Oracle Cloud deployment package lives in
[`ops/oracle-cobalt`](./ops/oracle-cobalt). It runs an API-key-protected Cobalt
instance for personal Reel resolution. Cobalt may tunnel and remux media; that
processing happens on the separate Oracle VM, not inside this Vercel API.

## Known Limitations

- Only public Instagram and Threads URLs are supported.
- Private posts are not supported.
- Stories and highlights are not supported.
- Instagram may show a Reel video in the app/browser while logged-out public HTML exposes only a cover image.
- Instagram may change its page structure, which can break lightweight parsing.
- Some media URLs may expire quickly.
- The backend does not proxy media, so the iPhone must be able to access the returned media URL directly.
- V1 does not include user registration.
- V1 does not include durable rate limiting.
- V1 does not include Cobalt or yt-dlp.
- Threads HTML fetching may fail from some networks/proxies; the URL contract is implemented, but live provider success depends on public HTML accessibility.

## Future Roadmap

- V2: Add optional Cobalt provider for a self-hosted or authorized instance.
- V2: Add provider interface expansion with explicit response-mode policy: direct URL only, picker URL list if direct, no backend media tunneling in this app.
- V2: Investigate whether a browser-based or authorized provider can expose Reel video URLs without storing or proxying media.
- V2: Add Vercel KV / Upstash Redis rate limiting.
- V2: Add user-specific tokens.
- V2: Add invite-based registration.
- V2: Add usage dashboard.
- V2: Add token revoke/regenerate.
- V2: Add support for Cobalt picker response.
- V2: Add fallback provider.

## Development Checks

```bash
pnpm typecheck
pnpm test
pnpm build
```
