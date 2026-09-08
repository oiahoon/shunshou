# Shunshou iPhone Shortcuts

Production API: https://shunshou.miaowu.org/api/resolve

## Install on iPhone

1. In Safari, download the single [Shunshou 0.2 shortcut](https://shunshou.miaowu.org/shunshou.shortcut).
2. Open the downloaded `.shortcut` in Shortcuts. If Safari only downloads the file, open it from Files > Downloads.
3. Add the shortcut and enter your private access code when prompted. The code is in the local, git-ignored `private-access-code.txt`; transfer it privately. Do not enter an Instagram password.
4. Connection checking is built in: running without an Instagram link in the input/clipboard checks the service. Permit the request to `shunshou.miaowu.org` when iOS asks. With a valid link, it goes directly to resolution without a separate health request.
5. Copy an Instagram Reel URL, then run Shunshou. Alternatively, select it in the iOS share sheet. Allow clipboard/CDN network access when prompted. When the downloaded file's share sheet opens, choose WeChat and the intended recipient yourself.

This workflow uses native iOS actions, not JavaScript pasted into Safari. It contains no access code until configured at import. Never publicly share a configured copy; revoke and replace a leaked token on the server.

The production [homepage](https://shunshou.miaowu.org/) provides one installer and Safari/Files instructions. Installed copies do not update themselves: replace the old Shunshou with the newly signed file and enter your code again. The old Connection Check shortcut can be deleted. Its old download URL now serves the same merged installer for compatibility.

Version 0.2 fixes the iPhone `If status is not` missing-parameter error by converting every string-comparison input to a native Text action before comparing against a literal such as `ok`. Do not replace the comparison with a has-value check: error responses also have a status value.

The server currently returns video URLs, not photos. Quality is a preference, not a transcoding promise. The Shortcut does not save media to Photos or a persistent Files directory. iOS owns temporary download caches; immediate physical deletion is not guaranteed. Dismissing the share sheet does not prove WeChat sent the file.

## Build and Sign

```sh
python3 shortcuts/build.py
python3 -m unittest discover -s shortcuts -p 'test_*.py'
shortcuts sign --mode anyone --input shortcuts/build/shunshou.unsigned.shortcut --output shortcuts/build/shunshou.shortcut
cp shortcuts/build/shunshou.shortcut services/resolver/public/shunshou.shortcut
cp shortcuts/build/shunshou.shortcut services/resolver/public/shunshou-check.shortcut
```

Signing uses Apple's system tool and sends only the token-free workflow definition to Apple for validation. The signed binary, not the unsigned plist, is the installable artifact. Definitions include an import question pointing to the access-code text action.

## Validation Status

- Version 0.1 was signed/importable but a real iPhone exposed a missing comparison parameter. Signing is not runtime acceptance.
- Structural tests cover output references, token-string ranges, balanced control flow, import questions, typed string comparisons, the merged health branch and separation of API/CDN authorization headers.
- Production auth: no token returns 401; valid token returns 200.
- Both supplied Reels resolve with HTTP 200 from Vercel, and an independent client probed H.264 720 x 1280 plus AAC for both returned files on 2026-09-08. The second Reel's audio differs from the earlier local extraction; future results may depend on upstream response and region.
- Full iPhone execution, iOS permissions and WeChat receipt still require device validation. A signed/importable package is not a claim of end-to-end phone success.
