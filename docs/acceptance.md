# Production Acceptance

## 2026-09-08: Custom Domain

Production is https://shunshou.miaowu.org. Git-triggered deployment of `02cabfb` passed all 13 checks in `ops/production-acceptance.json`:

| Gate | Result |
| --- | --- |
| Health without token / with token | 401 / 200 |
| Resolve without token | 401 |
| Missing URL, malformed JSON, private-network URL | 400 |
| Oversized request | 413 |
| Unsupported method | 405 |
| Private environment-file URL | 404 |
| Reel DZsVvmmkqXA | 200, one direct video item |
| Reel DZwITAaBfBE | 200, one direct video item |
| Two signed shortcut downloads | 200, hashes match local signed artifacts |

The shortcuts now target the custom domain, not the Vercel fallback alias. Local checks: 45 backend tests and 5 shortcut structural tests passed. The backend suite includes a real subprocess test with a runtime-added module path and a diagnostic redaction test.

## Failure And Repair

The initial Git deployment returned `RESOLVE_FAILED` for both Reels despite successful health checks. The worker did not explicitly inherit the parent Python runtime's module search paths. Passing those paths via `PYTHONPATH` restored both live samples without changing extractor version or adding cookies/proxies. Raw child stderr remains suppressed; only fixed diagnostic categories are logged. API tokens are removed from the worker environment.

This establishes a successful repair for the sampled deployment, not a guarantee that future Instagram restrictions cannot cause the same public error code.

## Pending Device Acceptance

- Install both newly signed files on a real iPhone using Safari/Files/Shortcuts.
- Configure a private access code and allow the custom-domain request.
- Run Connection Check, then each Reel from clipboard and the share sheet.
- Verify direct CDN download, picture and audio on the phone's actual network.
- Share to WeChat and verify receipt and playback on the receiving device.

No iPhone or WeChat completion is claimed. Earlier independent CDN codec probes are historical evidence, not injected metadata or a guarantee for later requests.

A later custom-domain smoke run again resolved both videos successfully, but direct local ffprobe requests failed on the current network. This is recorded as a failed CDN probe, not successful playback. Phone-network CDN download remains a separate acceptance gate.

## Repeat

Run `node ops/accept-production.mjs` from the repository root. It writes only sanitized status, counts and hashes, and exits nonzero on failure. Do not publish the local private access-code file. Run tests before release and verify the Git deployment SHA before interpreting a live report.

## Homepage Acceptance

The following homepage results describe the earlier two-installer release; see the 0.2 update below for current installation behavior.

The Git deployment `e231c75` reached READY at the custom production domain. All 14 cloud checks (the earlier 13 plus the public homepage) passed; see the current dated `ops/production-acceptance.json`. Deployment records identify the application commit tested, not a promise that later documentation commits change behavior.

The same five-viewport browser interaction suite also passed against `https://shunshou.miaowu.org`, including actual downloads of both signed files. A final CSS-only refinement isolates the artwork from the smallest phone's copy and blends its dark edges into the page.

The black/yellow homepage adds actual signed downloads, copyable installation-page URL, keyboard-accessible installation help and privacy disclosures. There is no token form, fake installation state, analytics or live public resolver. Backend suite now has 47 passing tests, including public homepage/assets/downloads and retained API authentication; shortcut suite has 5 passing tests.

Browser-first testing loaded the page in Codex IAB. Viewport screenshot capture became incorrectly scaled after resizing even though DOM viewport measurements were correct, so visual and repeated interaction checks used the repository's installed Playwright Chromium instead. Local viewports: 1536x1024, 1920x1080, 768x1024, 390x844 and 320x700. Each passed asset loading, no horizontal overflow, hero text/button separation, next-section visibility, reduced-motion behavior, install anchor, clipboard copy, both real downloads, all disclosures and no page exceptions.

Visual comparison covered the generated hero and downstream concepts: black/yellow/silver palette, oversized product name, full-bleed metallic art, open three-step flow, yellow installation band and ruled privacy rows. Intentional refinements include a separately generated arrow sculpture, responsive title/CTA sizing, a yellow title dot, readable opaque navigation background, a secondary outlined diagnostic download and additional truthful installation/privacy details. The mobile artwork edge and desktop navigation contrast were corrected after screenshot inspection. This is a concept-guided implementation, not a pixel-identical copy of the generated mockups.

## Shortcut 0.2 Regression Fix (2026-09-08)

See the 0.3 clipboard experiment section below for the latest delivery behavior.

- A real iPhone exposed `If status is not` with a missing comparison parameter. Version 0.1 signing and structural tests did not detect the dictionary-output typing issue.
- All string comparisons now consume a native Text action, including the `ok` success/error checks. Existence checks retain their distinct semantics.
- A single workflow handles sharing and connection checking. No valid input/clipboard link runs authenticated health and exits; a valid link goes directly to resolve. API credentials remain absent from CDN requests.
- The homepage advertises only the main installer. The old diagnostic download URL serves the identical merged signed bytes. Installed shortcuts do not auto-update; replace the old copy and re-enter the private code.
- Local verification: 47 backend tests and 7 shortcut tests passed. Apple system signing succeeded for the merged token-free artifact.
- Native macOS verification used an isolated, no-network JSON fixture built with the same conditional helper. The editor showed `If Comparison text is not ok`; native CLI execution returned `OK_BRANCH` for status `ok` and `ERROR_BRANCH` for status `error`.
- These native checks exercise the reported condition, not the entire iPhone workflow. iPhone installation, permissions, direct CDN download and WeChat receipt/playback remain pending for 0.2.
- Application commit `ec0a836` reached Vercel READY (`dpl_Hh3QYBHNTgjAPqQ5456XxM4ySBGH`). All 14 production API/download checks passed on retry; the first run had one TLS timeout. Both public installer paths matched the new 27,526-byte signed artifact.
- Browser checks against production timed out twice during navigation. The identical local release passed the five-viewport interaction suite (320, 390, 768, 1536 and 1920 pixels), including exactly one advertised download, actual file download, install/help/clipboard controls, assets, reduced motion and no overflow or page exceptions. Live browser rendering is not claimed for this update.

## Shortcut 0.3 Clipboard Experiment (2026-09-09)

- Adds an opt-in menu after download: copy the first media object and open WeChat, or use system sharing for all media. No text conversion of the media, Photos writes, persistent Files writes, deletion or automatic sending is added.
- Clipboard mode warns before overwriting, sets local-only and an expiry five minutes from the current time. Clipboard expiry is not proof of file-cache deletion or recipient delivery.
- A no-network native macOS fixture verified both menu branches and the five-minute quantity render correctly. Inspection exposed missing legacy input wiring: production uses `WFDate` for the date operand, token strings for date fields, and an explicit `weixin://` URL instead of the empty legacy Open App selector. Final device execution remains pending.
- Local Chromium checks at widths 320, 390 and 1440 passed: one installer, 0.3 label, no horizontal overflow and the Chinese suggested download filename. This follows the previously documented browser fallback path.
- 47 backend tests and 8 shortcut structure tests pass. iPhone clipboard types, WeChat launch/paste/video-message presentation, five-minute expiry behavior and same-name replacement still require device acceptance. Signing and editor inspection do not prove these behaviors.
- Both download routes now request the filename `顺手.shortcut`. The shortcut name stays fixed; users should choose replacement when offered. Silent self-updates and preservation of user-edited credentials across imports are not implemented or promised.
