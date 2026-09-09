# Production Acceptance

## Shortcut 0.3.2 Polish (2026-09-09)

- Snapinsta remains a local research experiment only; no third-party fallback, cookies, new dependencies or resolver behavior changes are included in this release.
- Retains 0.3.1 Match Text binding and existing clipboard/share behavior. Adds a blank access-code guard before network/clipboard access and clearer connection/extraction failure guidance.
- 11 shortcut structural tests and 47 backend tests passed. Apple signed the token-free 71-action workflow; both public installer files are byte-identical, 29,211 bytes.
- Local Playwright Chromium checks at widths 320, 390 and 1440 passed the 0.3.2 label, single installer, no horizontal overflow and actual download with filename `顺手.shortcut`. The Browser skill is not available in this session, so the existing Playwright check was used. The initial local bind was sandbox-blocked; the authorized loopback server and repeat checks succeeded.
- Physical iPhone input-dialog repair, import replacement and this release's end-to-end WeChat behavior remain pending. The user's earlier successful copy/paste report is not a claim that all videos resolve. `Dc8QUY9gf1C` and `Dc_hg0CxYCQ` remain known yt-dlp failures from the earlier investigation.
- Run the production acceptance script after Git deployment reaches READY; the dated report identifies the exact tested commit and must not be interpreted as device acceptance.
- Application commit `be7dbc32c4e0bea60fd723810fa46186c0ff00c5` reached READY as `dpl_DHFfE71gVVTBpjYng8zZUdy23qZL`, with `shunshou.miaowu.org` in its aliases. All 14 production checks passed, including both baseline Reels and exact signed-installer hashes. Subsequent acceptance-record commits do not change application behavior.

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

## Shortcut 0.3.1 Input Binding Fix (2026-09-09)

- User device feedback: copying and pasting succeeds, but both Instagram Share to > Shunshou and direct launch show an unwanted Text/Cancel/Done dialog. This is user-reported behavior, not an independently observed WeChat delivery.
- The generated Match Text action incorrectly used `WFInput`; its text parameter is named `text`. Corrected that binding while preserving the named share-input/clipboard fallback and all download/clipboard behavior.
- Added regression coverage for the exact native parameter and named-variable binding; nine shortcut structure tests pass. The earlier tests validated references, not action-specific parameter names.
- A no-network native test fixture was generated and signed, but importing it was blocked by approval policy. No native runtime or iPhone fix acceptance is claimed until the import is authorized or the user retests the new artifact.
