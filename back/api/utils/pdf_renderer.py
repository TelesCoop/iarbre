from concurrent.futures import ThreadPoolExecutor

from django.conf import settings
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright


class PdfExportTimeout(Exception):
    pass


def _render(token: str, frontend_url: str) -> bytes:
    timeout_ms = settings.PDF_EXPORT_TIMEOUT_S * 1000
    url = f"{frontend_url}/dashboard?print=1&export_token={token}"
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(args=["--no-sandbox"])
        try:
            page = browser.new_page()
            page.goto(url, wait_until="networkidle", timeout=timeout_ms)
            page.wait_for_function(
                "() => window.__DASHBOARD_READY__ === true", timeout=timeout_ms
            )
            return page.pdf(print_background=True, prefer_css_page_size=True)
        except PlaywrightTimeoutError as exc:
            raise PdfExportTimeout(str(exc))
        finally:
            browser.close()


def render_dashboard_pdf(token: str, frontend_url: str) -> bytes:
    # Playwright's sync API runs an asyncio loop on the thread that starts it.
    # On a request thread that loop makes every later ORM call raise
    # SynchronousOnlyOperation, so give each export its own throwaway thread.
    with ThreadPoolExecutor(max_workers=1) as executor:
        return executor.submit(_render, token, frontend_url).result()
