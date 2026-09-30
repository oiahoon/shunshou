# Social sharing — 2026-09-30

Homepage and four shortcut detail pages now have unique titles, concise descriptions, canonical Open Graph URLs, Chinese locale, square JPEG previews, and landscape Twitter cards. Cards reuse the existing product art in the black, ivory and yellow identity.

- Generate: `python3 ops/share/build.py` (ImageMagick + librsvg required).
- Validate locally: `python3 ops/share/check.py`.
- Validate production HTML and exact JPEG delivery: `python3 ops/share/check.py --live`.
- Local validation: five page checks passed, 48 backend tests and 16 shortcut tests passed. Existing Avatar Studio page inspected in a real browser; visible layout and installer remain intact. Card raster previews inspected.
- No Shortcut workflow/version change.

Open Graph metadata provides crawler previews. Actual WeChat client sharing is still an external acceptance gate: cached previews or plain pasted URLs may differ. There is no configured WeChat official account or JS-SDK signature service in this project. Do not claim deterministic WeChat share cards from metadata alone. Account-based JS-SDK integration requires an authorized account and its JS security domain/signature configuration.
