# Shunshou Agent Guide

## Read First

- Production: https://shunshou.miaowu.org
- Repository: https://github.com/oiahoon/shunshou
- Active backend: `services/resolver` (FastAPI + pinned yt-dlp).
- Public homepage and assets: `services/resolver/public`.
- Native iPhone shortcut source and signed artifacts: `shortcuts`.
- Read `services/resolver/README.md`, `shortcuts/README.md` and `docs/acceptance.md` before changing behavior.
- Root Next.js code and `codex.md` contain legacy context, not the active production architecture. `prototypes/shunshou` is an independent prototype. Oracle/Cobalt is an abandoned experiment; do not resume it.

## Security And Product Boundaries

- API returns metadata only. Never proxy, download, stream, store, transcode or upload media on the server.
- Never turn Reel cover images into successful video results. Unknown media properties remain null with warnings.
- Accept only supported public Instagram links; reject arbitrary hosts, private network targets, cookies and login credentials.
- Require Bearer authorization for health and resolve. Homepage and token-free installers are public.
- Never commit or log access codes, environment values, signed CDN URLs or Instagram cookies. Never put access codes in a public page, analytics, query strings or published shortcuts.
- Keep child processes killable, bounded and reaped after timeout. Preserve runtime module paths in `PYTHONPATH`; do not pass `API_TOKENS` to the worker. Log only allowlisted failure classifications, never raw upstream exceptions.
- The iPhone downloads directly from the returned CDN. API credentials must never reach the CDN.
- A signed shortcut is not proof of installation or playback. A closed share sheet is not proof of a WeChat delivery.
- Do not claim immediate physical cache deletion, guaranteed resolution/quality or universal platform support.

## Design

- Black, warm white, bright yellow with restrained silver details. No green, purple gradients or decorative card stacks.
- Preserve the selected modern geek identity and real download links. Do not add mock installation/connection success, invented metrics or a public URL resolver.
- Use semantic HTML, keyboard focus, responsive layouts and reduced-motion support. Keep marketing assets separate from live controls and text.

## Verification

From `services/resolver`: `.venv/bin/python -m pytest -q`.

From repository root:

```sh
python3 -m unittest discover -s shortcuts -p 'test_*.py'
node ops/accept-production.mjs
```

The live check reads the ignored local access-code file and writes a sanitized dated report. It must exit nonzero on failed acceptance. It does not prove iPhone CDN access or WeChat playback. Do not replace real checks with hardcoded successes. For homepage changes, also verify desktop/mobile, all download links, anchor navigation, keyboard interaction, assets and reduced motion in a real browser.

When changing legacy Next.js code, also run `corepack pnpm test`, `corepack pnpm typecheck`, `corepack pnpm lint`, and `corepack pnpm build`.

## Release

- Existing Vercel project: `shunshou-resolver`; scope: `joey-huangs-projects`; Root Directory: `services/resolver`; framework: FastAPI.
- `main` pushes trigger native Git production deployment. Verify READY, exact Git SHA and alias before claiming completion.
- Keep Hobby. No paid upgrades, add-ons, paid proxies or extra cloud instances without explicit authorization. Usage quotas still apply.
- Production `API_TOKENS` stays sensitive in Vercel; `RESOLVER_PROXY` stays unset in production. Preview deployments do not automatically receive production tokens.
- After shortcut changes, regenerate, test, sign using `shortcuts sign --mode anyone`, then copy both signed files to `services/resolver/public` before pushing.
- Update documentation and dated acceptance evidence. Separate automated, cloud, browser and actual iPhone/WeChat acceptance gates.
