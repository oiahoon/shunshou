# Production Acceptance

## 国庆头像 1.1.2 方形头像流程（2026-09-26）

- 用户在 macOS 运行 1.1.1 的“国庆头像 1”副本后，预览得到 0 KB PNG，并提示运行失败。1.1.1 的原生导入和结构测试未能证明实际合成。
- 使用只含自制旗帜图的临时诊断捷径分段运行：Base64 解码得到 38,557 字节 PNG；直接缩放得到 62,466 字节 PNG；固定尺寸裁切也得到 62,466 字节 PNG；直接缩放后叠加渐变得到 241,812 字节 PNG。含自动边长计算的裁切链输出 0 字节。由此移除自动边长计算和裁切，要求用户先在“照片”中裁成正方形，再直接缩放、叠图、预览和保存。删除了额外的格式转换动作；诊断的叠图结果本身为 PNG。
- 本地自动化：48 项 FastAPI 测试、16 项捷径结构测试通过；Apple 重新签名成功。公开副本与签名源 SHA-256 一致。原生中性图片分段运行覆盖了直接缩放及渐变叠图，但完整菜单、预览、相册保存和 iPhone 运行仍需验收。
- 提交 `88e61ce6b5d5bcffab9939ec6fcbfce6435506af` 的部署 `dpl_BKJmr4kuj2kdqhe8GX9FsEcSQc1L` 达到 READY；构建日志确认来源提交 `88e61ce`，正式别名为 `shunshou.miaowu.org`。22 项线上检查全部通过，包括公开签名捷径与本地文件 SHA-256 一致；报告在 `ops/production-acceptance.json`。这不证明用户设备上的头像合成。

## 国庆头像 1.1.1 图片输入修复（2026-09-26）

- 用户在 iPhone 上运行 1.1.0 后提供截图：“快速查看”提示 No Items，说明预览动作未收到图片。对照本机已有捷径，发现“调整图像大小”应使用 `WFImage` 接收图像，1.1.0 错写为 `WFInput`；原先“列表”的两项宽高变量在原生导入后也变成了空文本。1.1.1 改正两个参数格式并增加结构回归检查。重新导入后，macOS 捷径库保留了两个宽高变量和 `WFImage` 绑定。
- 公开详情页三款效果图改用用户提供的方形头像作为底图；该图片不进入捷径安装包。原参考图和报错截图均未公开。
- 本地自动化：48 项 FastAPI 测试、16 项捷径结构测试通过；Apple 重新签名成功，公开副本与签名源 SHA-256 一致。真实浏览器显示了用户提供的照片与渐变叠图。
- 原生运行诊断尚未完成：临时测试捷径把用户照片嵌入安装包后送往 Apple 签名服务的动作被自动审批拒绝，理由是用户只授权将照片用作本站占位图，并未授权向 Apple 披露该照片。没有继续签名此诊断包。仍需用户在 iPhone 上重新安装，验证三款实际合成、预览和相册保存。
- 1.1.1 提交 `b3bd288461c2215bb602b023fbc4c51b9cb30c6c` 的生产部署达到 READY，别名为 `shunshou.miaowu.org`，22 项线上检查通过；这只验证了网页、服务与下载文件一致，随后 macOS 运行仍复现 0 KB 图片。

## 国庆头像 1.1.0 渐变与状态样式（2026-09-26）

- 新增柔和渐变和「国庆在线」两款本地透明装饰图，保留 1.0.0 的经典旗帜。用户先选照片，再从三款样式中选择；借鉴本机“微信在线状态”的模板选择和叠图/保存流程。没有复制其远程素材、联系人卡片、网络请求或个人数据。
- 渐变 PNG 的左上红色不透明度约 91%，中心约 3.5%，远端为零；黄色星星保持不透明。三个样式均打包在签名捷径内，不依赖网站或第三方服务运行。
- 本地自动化：48 项 FastAPI 测试、16 项捷径结构测试通过；Apple `shortcuts sign --mode anyone` 成功，macOS 捷径应用显示了签名文件的导入预览。真实浏览器检查三款预览图、安装下载，以及 320、390、768、1440 px 页面无横向溢出；下载文件与签名源 SHA-256 一致。
- 提交 `29fd42c07e6ac6f58972351a08b159ffed471f91` 的部署 `dpl_7GwcQtNcQPMmHUSwT9mL9oAAhysP` 达到 READY；构建日志确认来源提交 `29fd42c`，正式别名为 `shunshou.miaowu.org`。`node ops/accept-production.mjs` 的 22 项线上检查全部通过，包括新版安装包与签名源的 SHA-256 一致；报告见 `ops/production-acceptance.json`。
- iPhone 的三款合成、照片权限和相册保存仍需实机验收。

## 国庆头像 1.0.0（2026-09-26）

- 新捷径使用系统照片选择器，从本机图片获取宽高、按较短边居中裁成正方形，缩放为 1024 × 1024，叠加内置透明国旗主题图，转换为不保留元数据的 PNG，预览后保存到照片；没有任何网络动作。参考图片未收录进公开源码、页面或安装包。
- Apple `shortcuts sign --mode anyone` 成功，macOS 捷径应用显示并接受了签名文件的导入预览。公开安装文件与签名源 SHA-256 一致；本地真实浏览器下载的 `国庆头像.shortcut` 也与签名文件一致。透明图中心完全透明，五角星为不透明黄色。
- 本地自动化：48 项 FastAPI 测试、16 项捷径结构测试通过。浏览器确认首页入口、详情页图像加载、安装与更新锚点、真实下载；320、390、768 px 无横向溢出。IAB 不能扩大到 1440 px，桌面断点尚未用真实浏览器复核。
- Git 提交 `a480a05d541d104f400d813eca61b3d932233955` 触发的生产部署 `dpl_4znWc9HjHLdfnPoTcnAUCURfMbKm` 达到 READY；构建日志确认提交 `a480a05`，别名包含 `shunshou.miaowu.org`。两次 `node ops/accept-production.mjs` 均有 20/22 项通过：首页、新详情页、新签名下载及其哈希全部通过；既有的两个 Instagram Reel 样例均返回 502 `RESOLVE_FAILED`，所以报告按要求为失败，记录在 `ops/production-acceptance.json`。这不影响国庆头像的本地合成路径，但当前不能宣称全站验收通过。
- 待 iPhone 实机验收：导入、照片权限、方图/横图/竖图裁切、预览、相册保存及手动设置微信头像。签名不证明这些设备步骤。

## 出差开销 1.0.0（2026-09-26）

- 从本机原版 Business Trip 的 31 个动作检查出个人 iCloud 文件引用、直接拼接 CSV 和两次取时间等问题。优化版是 28 个动作，使用每位使用者自己的 iCloud Drive／Shortcuts／BusinessTripExpenses.csv、单次取时间、金额大于零校验、CSV 引号转义、创建或追加分支。旧版 Documents／BusinessExpenses.csv 不自动迁移。
- 通过 Apple `shortcuts sign --mode anyone` 生成无账号、无访问码的签名文件；发布副本与签名文件 SHA-256 一致。原生 macOS 捷径编辑器确认导入问题、金额数字比较、默认 Shortcuts 目录、CSV 文件名、首次创建和追加动作均正确呈现。签名与编辑器展示不证明 iPhone 写入结果。
- 本地自动化：15 项捷径结构测试、48 项 FastAPI 测试通过。Playwright Chromium 在 320、390、768、1440 px 验证首页和详情页无横向溢出、安装锚点和实际下载文件名；三个公开下载路径均在本地返回 200。键盘首个焦点为“跳转到正文”，减少动态效果时滚动为 `auto`。移动和桌面完整截图经视觉检查，并修复了长文件名在步骤列表中的布局。
- Git 应用提交 `7fb6c3ec9bd07ab3ba6cff6df9c43dd1dbe01020` 自动部署为 `dpl_3rQDLx3TEP1VR2QNSFWU4bciNhiz`。Vercel 构建日志确认来源提交 `7fb6c3e`，状态 READY，别名包含 `shunshou.miaowu.org`。`node ops/accept-production.mjs` 的 20 项线上检查全部通过；报告在 `ops/production-acceptance.json`。生产页面在 390、1440 px 的 Chromium 渲染无横向溢出或页面脚本错误，下载入口存在。
- 待实机验收：iPhone 导入、iCloud Drive 权限、首次创建、重复追加、Numbers 对含逗号及引号内容的解析、旧记录手动迁移。尚未声称这些环节已经完成。

## Shortcut 0.4.0 Install And Update (2026-09-26)

- The homepage keeps the black/yellow/silver identity while presenting separate first-install and update paths. The long setup text is reduced to three short help disclosures. The same signed installer URL remains the sole download link.
- A public `/release.json` contains only version, release date and the fixed update-page URL. A no-link Shortcut run checks service health, compares the embedded version and offers to open the update page if different. Shared Instagram links do not make the extra request. Updates still require Safari download and user-confirmed import; credential retention or same-name replacement is not guaranteed.
- Local tests: 12 Shortcut structural tests and 48 resolver tests passed. Five Playwright Chromium widths (320, 390, 768, 1440, 1920) passed install/update anchors, keyboard help disclosure, public version response, clipboard copy, reduced motion, real installer download, no horizontal overflow and no page errors. Geometry checks confirmed help text does not overlap the summary. The full-page screenshot's focus/scroll artifact is not a rendered element overlap.
- The token-free 83-action Shortcut was Apple-signed. Native iPhone version comparison, import replacement, permission prompts and WeChat sending still need device acceptance; avoid treating structural tests and signing as proof of these outcomes.
- Application commit `2b0175d178896980df3d3df7d6ee9435fe43c1ef` reached Vercel READY as `dpl_4738TkcCH9MMGWmG65weMcU94vUL` with `shunshou.miaowu.org` attached. All 15 production checks passed, including the 0.4.0 manifest, both baseline Reels and byte-identical 29,945-byte installers. A direct homepage read confirmed the visible version, update guide and single installer. This is cloud acceptance only.

## Shortcut 0.3.3 Flow Polish (2026-09-26)

- The user reports that the installed Shortcut has generally worked well over time, with occasional videos unavailable to the resolver. This is user-reported experience rather than a measured resolution rate.
- Homepage instructions now lead with Instagram's share sheet and describe clipboard/WeChat paste and system sharing accurately. The Shortcut menu includes the clipboard overwrite and five-minute expiry notice, and the redundant post-selection alert is removed. The download, server request and clipboard actions remain unchanged.
- Snapinsta is not part of this release. Preserve separate cloud and device acceptance for the signed 0.3.3 package.
- Local checks: 11 shortcut tests and 47 resolver tests passed. Apple signed the token-free 70-action installer; both public download filenames match the signed 29,050-byte artifact by SHA-256.
- Playwright Chromium checked the homepage at widths 320, 390, 768 and 1440. Each viewport showed the revised flow and 0.3.3 installer, opened the install instructions, downloaded `顺手.shortcut`, and had no horizontal overflow or page errors. Visual review of mobile and desktop screenshots showed no overlapping text or controls. The Playwright CLI wrapper stalled on initial npm startup, so the already-installed repository Playwright runtime was used.
- Removing a duplicate menu alert has not yet been verified on the user's iPhone. The preceding version's positive usage report is not evidence of 0.3.3 installation or WeChat delivery.
- Git commit `fc20d4f26ff2f92fe05ad89394d51dc4b0e1de5c` reached Vercel READY as `dpl_7u4QZNBY4dQHKkJ3dDFJ1iLqfst7` with `shunshou.miaowu.org` attached. All 14 production checks passed: auth and validation guards, two baseline Reel resolutions, and both 29,050-byte installer downloads matching the signed local artifact. A direct homepage read confirmed the 0.3.3 label and revised share/WeChat flow. This is cloud acceptance, not physical iPhone acceptance.

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

## Shortcut Hub Redesign (2026-09-26)

- Replaced the single Shortcut homepage with a two-item collection and separate Insta Share and 大众点评快写 detail/install/update pages. The existing Shunshou installer, release manifest and `/#update` entry remain stable.
- Moved the local 大众点评 source, build script, unsigned output and signed installer into `shortcuts/dianping/`, with a public signed copy at `/dianping.shortcut`. The workflow uses the user's own DeepSeek API Key and sends the submitted merchant information and experience to DeepSeek from the iPhone. It copies a draft; it does not publish the review.
- Local checks: 48 resolver tests and 12 Shortcut tests passed. The new routes, assets and download links returned HTTP 200 in FastAPI tests. The signed 大众点评 public copy is byte-identical to the archived signed file.
- Browser checks: the Codex in-app browser opened both detail pages at 390 px, downloaded both installers, and showed no horizontal overflow. The browser became unresponsive during repeated viewport changes, so Playwright Chromium checked all three pages at 320, 390, 768 and 1440 px with reduced motion, one H1, loaded imagery and no horizontal overflow. The desktop and mobile screenshots were reviewed against the generated visual concept; an initially visible skip link was fixed.
- First cloud deployment (`7ef1152`) served the homepage and installers, but both detail paths returned 500 because Vercel published the HTML as static output outside the FastAPI function bundle. Static rewrites in `d76c156` fixed both routes.
- Production deployment `dpl_3bvrWH9DpASffzE9SGPhJZgxXv2C` reached READY with `shunshou.miaowu.org` attached; Vercel build logs confirmed source commit `d76c156`. `node ops/accept-production.mjs` passed all 18 live checks on 2026-09-26, including both detail pages, three byte-checked installers, API authorization and two baseline Reel resolutions. The sanitized machine-readable result is `ops/production-acceptance.json`.
- Actual iPhone import, DeepSeek response quality, Instagram CDN access and WeChat delivery remain separate device gates.

## Shortcut Detail Visual Guides (2026-09-26)

- The three public detail pages now use separate visual treatments and vector hero artwork for video sharing, review writing, and trip expenses. The hub and shared controls use fixed SVG icons, avoiding platform-dependent emoji rendering.
- Each page includes a three-step, annotated phone-style concept guide. The pages explicitly label these as illustrations rather than device screenshots; exact system wording varies by iOS version.
- Local FastAPI tests: 48 passed. Shortcut structure tests: 15 passed. Asset and tutorial routes are covered by the public-page test.
- Playwright Chromium checked homepage and all three detail pages at 390 px and 1440 px using local route fulfillment because loopback server binding was unavailable in the sandbox. All images loaded, no horizontal overflow was reported, and all detail pages retained their signed installer links.
- The visual guide does not establish actual iPhone import, permission prompts, CDN download, DeepSeek response, iCloud write, or WeChat delivery.

- Production deployment `dpl_AMYQTZpxLXwkNVwsGfcGCqc1rv1Z` reached READY with `shunshou.miaowu.org` attached. Build logs confirm application commit `e8d742e`. The live acceptance script passed all 20 checks, including the three detail pages and signed installer hashes; the sanitized report is `ops/production-acceptance.json`.

## Shortcut Artwork Refresh (2026-09-26)

- Replaced the three simple detail illustrations and hub symbols with nine Codex-generated, optimized WebP assets: three hero artworks, three transparent product icons, and three workflow concept images. The guide keeps separately rendered HTML action labels and an explicit illustration disclaimer so generated imagery is not presented as an exact iOS screenshot.
- Browser review of the homepage and all three detail pages at 320, 390 and 1440 px found no horizontal overflow or missing image assets. The signed Shortcut download routes and the three tutorial anchors remained present. The 320 px hero layout was checked after correcting a CSS override that initially forced a two-column composition.

- Production deployment `dpl_2K3VFunhmdrctQKdRLwRjCxtRY2M` reached READY with `shunshou.miaowu.org` attached. Build logs identify application commit `7eb398c`; the live acceptance script passed all 20 checks. The generated images are illustrative, and exact iPhone dialogs remain a device acceptance gate.

## Detail Hero Edge Fix (2026-09-26)

- Moved each detail Hero background from the constrained content wrapper to a full-width section, while retaining the text and artwork in an inner wrapper. The light Dianping header now also paints across the viewport.
- Local browser screenshots at 320, 390 and 1440 px confirmed continuous Hero edges, no horizontal overflow, all assets loaded, and installer links present. Resolver tests: 48 passed; Shortcut structural tests: 15 passed.

- Production deployment `dpl_5RVU85xnEn2P1pCeY994ij9WyPEo` reached READY with `shunshou.miaowu.org` attached. Build logs confirm application commit `f08f7ff`; all 20 live acceptance checks passed. The sanitized result is `ops/production-acceptance.json`.

## Detail Page Edge Audit (2026-09-26)

- A desktop review found the same constrained-background issue in the tutorial section: its dark surface stopped at the `.wrap` edges, leaving visible vertical seams. The section now owns the full-width background, with an inner wrapper for text and steps. Workflow concept images span the viewport; nonfunctional outlines around hero artwork and concept captions were removed.
- Local browser checks covered homepage and all three detail pages at 320, 390, and 1440 px. No horizontal overflow or failed image loads were found; installer links remained present. Resolver tests: 48 passed. Shortcut tests: 15 passed.

- Production deployment `dpl_9hbw8AKdqLc3MiMzRGK92UXAvn1A` reached READY with `shunshou.miaowu.org` attached. Build logs confirm application commit `2df6d41`; all 20 live acceptance checks passed. The sanitized report is `ops/production-acceptance.json`.
