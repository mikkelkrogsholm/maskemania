"""Tests for the PDF renderer routing (WeasyPrint primary, Chrome fallback).

The actual ``weasyprint`` package is not assumed to be installed in CI,
so every test mocks both the WeasyPrint-availability flag and the
Chrome-availability probe. This way the suite passes regardless of the
host environment.
"""

from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

_HERE = Path(__file__).resolve().parent
_REPO = _HERE.parent.parent.parent
sys.path.insert(0, str(_REPO))

from lib.visualisering import pdf as _pdf  # noqa: E402
from lib.visualisering import pdf_weasy as _pdf_weasy  # noqa: E402
from lib.visualisering.pdf import (  # noqa: E402
    ChromeNotFoundError, render_pdf,
)


_HTML = "<!doctype html><html><body><p>hi</p></body></html>"


class WeasyPreferredTests(unittest.TestCase):
    """When WeasyPrint is importable it must always win in 'auto' mode."""

    def test_auto_uses_weasyprint_when_available(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "out.pdf"
            with mock.patch.object(_pdf_weasy, "weasyprint_available", True):
                with mock.patch.object(
                    _pdf_weasy, "render_pdf_weasy",
                    return_value=out,
                ) as weasy_mock:
                    with mock.patch.object(_pdf, "html_to_pdf") as chrome_mock:
                        result = render_pdf(_HTML, out, renderer="auto")
            weasy_mock.assert_called_once()
            chrome_mock.assert_not_called()
            self.assertEqual(result, out)

    def test_force_weasy_succeeds_when_available(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "forced.pdf"
            with mock.patch.object(_pdf_weasy, "weasyprint_available", True):
                with mock.patch.object(
                    _pdf_weasy, "render_pdf_weasy",
                    return_value=out,
                ) as weasy_mock:
                    result = render_pdf(_HTML, out, renderer="weasy")
            weasy_mock.assert_called_once()
            self.assertEqual(result, out)


class ChromeFallbackTests(unittest.TestCase):
    """When WeasyPrint is missing, 'auto' must fall back to Chrome."""

    def test_auto_falls_back_to_chrome_when_weasy_missing(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "fallback.pdf"
            with mock.patch.object(_pdf_weasy, "weasyprint_available", False):
                with mock.patch.object(_pdf, "find_chrome",
                                        return_value="/usr/bin/chrome"):
                    with mock.patch.object(
                        _pdf, "html_to_pdf",
                        return_value=out,
                    ) as chrome_mock:
                        with mock.patch.object(
                            _pdf_weasy, "render_pdf_weasy",
                        ) as weasy_mock:
                            result = render_pdf(
                                _HTML, out, renderer="auto",
                            )
            weasy_mock.assert_not_called()
            chrome_mock.assert_called_once()
            self.assertEqual(result, out)


class ForcedRendererErrorTests(unittest.TestCase):
    """Forcing a specific renderer must fail loudly when it's unavailable."""

    def test_force_weasy_fails_when_missing(self):
        with mock.patch.object(_pdf_weasy, "weasyprint_available", False):
            with self.assertRaises(ValueError) as ctx:
                render_pdf(_HTML, "/tmp/never.pdf", renderer="weasy")
        msg = str(ctx.exception)
        self.assertIn("WeasyPrint", msg)
        # Hint must mention the install command so the user can fix it.
        self.assertIn("pip install weasyprint", msg)

    def test_force_chrome_propagates_chrome_not_found(self):
        with mock.patch.object(_pdf, "find_chrome",
                                side_effect=ChromeNotFoundError("nope")):
            with self.assertRaises(ChromeNotFoundError):
                render_pdf(_HTML, "/tmp/never.pdf", renderer="chrome")

    def test_unknown_renderer_raises_value_error(self):
        with self.assertRaises(ValueError) as ctx:
            render_pdf(_HTML, "/tmp/never.pdf", renderer="prince")
        self.assertIn("prince", str(ctx.exception))


class NoRendererAvailableTests(unittest.TestCase):
    """If neither WeasyPrint nor Chrome is available we must raise a
    clear, actionable error — not a cryptic FileNotFoundError downstream."""

    def test_no_renderer_available_raises_value_error(self):
        with mock.patch.object(_pdf_weasy, "weasyprint_available", False):
            with mock.patch.object(_pdf, "find_chrome",
                                    side_effect=ChromeNotFoundError("nope")):
                with self.assertRaises(ValueError) as ctx:
                    render_pdf(_HTML, "/tmp/never.pdf", renderer="auto")
        msg = str(ctx.exception)
        # Must mention both install paths so the user can pick one.
        self.assertIn("weasyprint", msg.lower())
        self.assertIn("chrome", msg.lower())


class HelperProbeTests(unittest.TestCase):
    """The ``weasyprint_available()`` and ``chrome_available()`` helpers
    must reflect the underlying probes."""

    def test_weasyprint_available_helper_reflects_module_flag(self):
        with mock.patch.object(_pdf_weasy, "weasyprint_available", True):
            self.assertTrue(_pdf.weasyprint_available())
        with mock.patch.object(_pdf_weasy, "weasyprint_available", False):
            self.assertFalse(_pdf.weasyprint_available())

    def test_chrome_available_helper_reflects_find_chrome(self):
        with mock.patch.object(_pdf, "find_chrome",
                                return_value="/path/to/chrome"):
            self.assertTrue(_pdf.chrome_available())
        with mock.patch.object(_pdf, "find_chrome",
                                side_effect=ChromeNotFoundError("nope")):
            self.assertFalse(_pdf.chrome_available())


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
