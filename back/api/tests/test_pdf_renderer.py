from unittest import mock
from django.test import SimpleTestCase, override_settings
from api.utils import pdf_renderer


@override_settings(PDF_EXPORT_TIMEOUT_S=5)
class RenderDashboardPdfTest(SimpleTestCase):
    def test_navigates_to_print_url_and_returns_pdf(self):
        page = mock.MagicMock()
        page.pdf.return_value = b"%PDF-1.7 fake"
        context = mock.MagicMock()
        context.new_page.return_value = page
        browser = mock.MagicMock()
        browser.new_context.return_value = context

        with mock.patch.object(pdf_renderer, "get_browser", return_value=browser):
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
        context = mock.MagicMock()
        context.new_page.return_value = page
        browser = mock.MagicMock()
        browser.new_context.return_value = context

        with mock.patch.object(pdf_renderer, "get_browser", return_value=browser):
            with self.assertRaises(pdf_renderer.PdfExportTimeout):
                pdf_renderer.render_dashboard_pdf("tok123", "http://frontend:4173")
