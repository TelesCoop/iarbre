import threading
from unittest import mock
from django.test import SimpleTestCase, override_settings
from api.utils import pdf_renderer


def _patch_playwright(page):
    sync_playwright = mock.MagicMock()
    browser = (
        sync_playwright.return_value.__enter__.return_value.chromium.launch.return_value
    )
    browser.new_page.return_value = page
    return mock.patch.object(pdf_renderer, "sync_playwright", sync_playwright)


@override_settings(PDF_EXPORT_TIMEOUT_S=5)
class RenderDashboardPdfTest(SimpleTestCase):
    def test_navigates_to_print_url_and_returns_pdf(self):
        page = mock.MagicMock()
        page.pdf.return_value = b"%PDF-1.7 fake"

        with _patch_playwright(page):
            result = pdf_renderer.render_dashboard_pdf("tok123", "http://frontend:4173")

        self.assertEqual(result, b"%PDF-1.7 fake")
        url = page.goto.call_args.args[0]
        self.assertIn("http://frontend:4173/dashboard", url)
        self.assertIn("print=1", url)
        self.assertIn("export_token=tok123", url)
        self.assertIn("timeout", page.goto.call_args.kwargs)
        self.assertIn("timeout", page.wait_for_function.call_args.kwargs)
        page.pdf.assert_called_once()

    def test_timeout_raises_pdf_export_timeout(self):
        from playwright.sync_api import TimeoutError as PWTimeout

        page = mock.MagicMock()
        page.wait_for_function.side_effect = PWTimeout("boom")

        with _patch_playwright(page):
            with self.assertRaises(pdf_renderer.PdfExportTimeout):
                pdf_renderer.render_dashboard_pdf("tok123", "http://frontend:4173")

    def test_render_runs_off_the_calling_thread(self):
        seen = {}

        def fake_sync_playwright():
            seen["thread"] = threading.current_thread()
            raise pdf_renderer.PdfExportTimeout("stop")

        with mock.patch.object(pdf_renderer, "sync_playwright", fake_sync_playwright):
            with self.assertRaises(pdf_renderer.PdfExportTimeout):
                pdf_renderer.render_dashboard_pdf("tok123", "http://frontend:4173")

        self.assertIsNot(seen["thread"], threading.current_thread())
