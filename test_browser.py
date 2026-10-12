from pathlib import Path
import json, os, cv2
from playwright.sync_api import sync_playwright
ROOT = os.environ.get("TVZ_QR_BASE_URL", "http://localhost:8080/")
OUT = Path(__file__).resolve().parent / "test-results"
OUT.mkdir(exist_ok=True)
with sync_playwright() as pw:
    cdp = os.environ.get("TVZ_QR_CDP_URL")
    browser = pw.chromium.connect_over_cdp(cdp) if cdp else pw.chromium.launch(headless=True)
    context = browser.new_context(accept_downloads=True, viewport={"width":390,"height":844})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    response = page.goto(ROOT)
    page.wait_for_selector("#generate:not([disabled])")
    calls = []
    page.on("request", lambda req: calls.append(req.url))
    page.locator("#jmbag").fill("123")
    page.locator("#generate").click()
    assert page.locator("#error").is_visible()
    assert not page.locator("#result").is_visible()
    page.locator("#jmbag").fill("0246000000")
    page.locator("#generate").click()
    assert page.locator("#result").is_visible()
    assert page.locator("#display-jmbag").inner_text() == "0246000000"
    with page.expect_download() as saved:
        page.locator("#download").click()
    png = OUT / "synthetic-qr.png"
    saved.value.save_as(png)
    decoded, points, _ = cv2.QRCodeDetector().detectAndDecode(cv2.imread(str(png)))
    assert decoded == "https://kinezioloska-kultura.tvz.hr/0246000000", decoded
    assert saved.value.suggested_filename == "tvz-tzk-qr.png"
    for width in (390,320):
        page.set_viewport_size({"width":width,"height":844})
        assert page.evaluate("document.documentElement.scrollWidth <= window.innerWidth")
        page.screenshot(path=str(OUT / f"mobile-{width}.png"),full_page=True)
    storage = page.evaluate("async () => ({local:localStorage.length,session:sessionStorage.length,databases:(await indexedDB.databases()).length,caches:(await caches.keys()).length,workers:(await navigator.serviceWorker.getRegistrations()).length})")
    assert all(n == 0 for n in storage.values()), storage
    assert not calls, calls
    page.locator("#jmbag").fill("0246000001")
    assert not page.locator("#result").is_visible()
    context.set_offline(True)
    page.locator("#generate").click()
    assert page.locator("#result").is_visible()
    page.locator("#clear").click()
    assert page.locator("#jmbag").input_value() == ""
    assert not page.locator("#result").is_visible()
    context.set_offline(False)
    page.locator("#jmbag").fill("0246000000")
    page.locator("#generate").click()
    page.reload()
    page.wait_for_selector("#generate:not([disabled])")
    assert page.locator("#jmbag").input_value() == ""
    assert not page.locator("#result").is_visible()
    assert not errors, errors
    axe = Path(os.environ["TVZ_QR_AXE_PATH"]) if os.environ.get("TVZ_QR_AXE_PATH") else None
    violations = []
    if axe and axe.exists():
        page.evaluate(axe.read_text())
        violations = page.evaluate("async()=> (await axe.run(document,{runOnly:{type:'tag',values:['wcag2a','wcag2aa','wcag21aa','wcag22aa']}})).violations.map(v=>({id:v.id,impact:v.impact}))")
        assert not violations, violations
    evidence = {"url":ROOT,"http":response.status,"decoded_synthetic_payload":decoded,"zero_requests_during_generation_and_download":True,"storage":storage,"offline_generation":True,"clear_and_reload_remove_input":True,"download":saved.value.suggested_filename,"widths":[390,320],"accessibility_violations":violations,"js_errors":errors}
    (OUT / "results.json").write_text(json.dumps(evidence,indent=2))
    print(json.dumps(evidence,indent=2))
    context.close()
    if not cdp:
        browser.close()
