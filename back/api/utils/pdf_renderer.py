import threading

from django.conf import settings
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

_lock = threading.Lock()
_playwright = None
_browser = None


class PdfExportTimeout(Exception):
    pass


def get_browser():
    global _playwright, _browser
    with _lock:
        if _browser is None or not _browser.is_connected():
            if _playwright is not None:
                try:
                    _playwright.stop()
                except Exception:
                    pass
            _playwright = sync_playwright().start()
            _browser = _playwright.chromium.launch(args=["--no-sandbox"])
    return _browser


def render_dashboard_pdf(token: str, frontend_url: str) -> bytes:
    timeout_ms = settings.PDF_EXPORT_TIMEOUT_S * 1000
    url = f"{frontend_url}/dashboard?print=1&export_token={token}"
    context = get_browser().new_context()
    try:
        page = context.new_page()
        page.goto(url, wait_until="networkidle", timeout=timeout_ms)
        page.wait_for_function(
            "() => window.__DASHBOARD_READY__ === true", timeout=timeout_ms
        )
        return page.pdf(print_background=True, prefer_css_page_size=True)
    except PlaywrightTimeoutError as exc:
        raise PdfExportTimeout(str(exc))
    finally:
        context.close()
