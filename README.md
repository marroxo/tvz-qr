# TVZ QR

Simple, unofficial QR display for TVZ physical education attendance.

**Live website:** https://tzk.tvz.lol/

Enter a 10-digit JMBAG, display its QR code, or explicitly download a PNG for offline display. Preserve leading zeros.

## QR content

The QR encodes this exact URL:

```text
https://kinezioloska-kultura.tvz.hr/YOUR_10_DIGIT_JMBAG
```

This format was checked against a QR from the [official TVZ generator](https://kinezioloska-kultura.tvz.hr/) using a synthetic all-zero identifier. Matching QR content has been tested; acceptance by a professor's scanner has not been physically tested. This tool does not enroll students or record attendance.

## Privacy

Generation runs entirely in the browser using a locally bundled QR library. JMBAG is not sent to this website's server or TVZ during generation. No analytics, cookies, localStorage, sessionStorage, IndexedDB, service worker, or automatic persistence are used. Input and QR are cleared when edited, cleared, reloaded, or the page is hidden. Saving a PNG happens only after clicking the download button.

Site deployment disables access logs and sends `Cache-Control: no-store`. Its CSP blocks connections and form submissions. Clicking an official website or app-store link leaves this site.

## Run locally

No installation or build step is required to serve the committed static files:

```sh
python3 -m http.server 8080 --bind 127.0.0.1 --directory dist
```

Open http://localhost:8080/. Publish the contents of `dist/` as the website root. Assets use root-relative paths.

## QR dependency

`qrcode-generator` 2.0.4 is bundled under `dist/vendor/`. Its MIT license is included in `dist/vendor/LICENSE.txt`. The lockfile records the exact package. To refresh the vendor copy after an intentional dependency update:

```sh
npm ci --ignore-scripts
cp node_modules/qrcode-generator/dist/qrcode.js dist/vendor/qrcode.js
```

Keep the vendor license when redistributing.

## Browser checks

The optional browser test checks QR decoding, zero requests during generation and download, empty browser storage, offline generation, clearing/reloading, and narrow-screen layouts. It uses synthetic identifiers.

```sh
python3 -m venv .venv
.venv/bin/pip install playwright opencv-python-headless
.venv/bin/playwright install chromium
TVZ_QR_BASE_URL=http://localhost:8080/ .venv/bin/python test_browser.py
```

Run the local server first. Set `TVZ_QR_CDP_URL` to reuse an existing Chrome debugging session instead of launching Chromium. Optional `TVZ_QR_AXE_PATH` enables an accessibility check using a local axe script. Evidence goes into ignored `test-results/`.

Not affiliated with TVZ or Quick Response j.d.o.o. QR Student remains a separate official application.
