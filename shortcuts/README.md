# Shunshou iPhone Shortcuts

Production API: https://shunshou-resolver.vercel.app/api/resolve

## Install on iPhone

1. In Safari, download [Shunshou](https://shunshou-resolver.vercel.app/shunshou.shortcut) and [Connection Check](https://shunshou-resolver.vercel.app/shunshou-check.shortcut).
2. Open the downloaded `.shortcut` in Shortcuts. If Safari only downloads the file, open it from Files > Downloads.
3. Add the shortcut and enter your private access code when prompted. The code is in the local, git-ignored `private-access-code.txt`; transfer it privately. Do not enter an Instagram password.
4. Run Connection Check first. Permit the request to `shunshou-resolver.vercel.app` when iOS asks.
5. Copy an Instagram Reel URL, then run Shunshou. Alternatively, select it in the iOS share sheet. Allow clipboard/CDN network access when prompted. When the downloaded file's share sheet opens, choose WeChat and the intended recipient yourself.

These workflows use native iOS actions, not JavaScript pasted into Safari. They contain no access code until configured at import. Never publicly share a configured copy; revoke and replace a leaked token on the server.

The server currently returns video URLs, not photos. Quality is a preference, not a transcoding promise. The Shortcut does not save media to Photos or a persistent Files directory. iOS owns temporary download caches; immediate physical deletion is not guaranteed. Dismissing the share sheet does not prove WeChat sent the file.

## Build and Sign

```sh
python3 shortcuts/build.py
python3 -m unittest discover -s shortcuts -p 'test_*.py'
shortcuts sign --mode anyone --input shortcuts/build/shunshou.unsigned.shortcut --output shortcuts/build/shunshou.shortcut
shortcuts sign --mode anyone --input shortcuts/build/shunshou-check.unsigned.shortcut --output shortcuts/build/shunshou-check.shortcut
```

Signing uses Apple's system tool and sends only the token-free workflow definition to Apple for validation. The signed binary, not the unsigned plist, is the installable artifact. Definitions include an import question pointing to the access-code text action.

## Validation Status

- Both workflows signed successfully with Apple's local tool; system importer recognizes the signed main file and its share-sheet capability.
- Structural tests cover output references, token-string ranges, balanced control flow, import questions and separation of API/CDN authorization headers.
- Production auth: no token returns 401; valid token returns 200.
- Both supplied Reels resolve with HTTP 200 from Vercel, and an independent client probed H.264 720 x 1280 plus AAC for both returned files on 2026-09-08. The second Reel's audio differs from the earlier local extraction; future results may depend on upstream response and region.
- Full iPhone execution, iOS permissions and WeChat receipt still require device validation. A signed/importable package is not a claim of end-to-end phone success.
