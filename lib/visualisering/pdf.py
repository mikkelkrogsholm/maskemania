"""PDF export — routes between WeasyPrint (primary) and headless Chrome.

Per the design research (``research/fase-1-agent-c-design.md``) we now
prefer **WeasyPrint** as the rendering engine: it's Python-native,
actively maintained, supports CSS Paged Media + variable fonts (v60+),
and removes the Chromium dependency from CI / new-developer setups.
Chrome remains as a fallback for environments where WeasyPrint isn't
installed (it has Cairo/Pango system-deps on some platforms).

Public surface
--------------

* :func:`render_pdf` — primary entry point. Picks WeasyPrint if
  available, else Chrome, else raises a clear :class:`ValueError`.
  ``renderer`` may be forced to ``"weasy"`` or ``"chrome"`` via the
  CLI ``--pdf-renderer`` flag.
* :func:`html_to_pdf` — legacy Chrome-only entry point, retained for
  the social-preview pipeline (which intentionally uses Chrome to
  rasterise to PNG via ``--screenshot``, not for PDF).
* :func:`find_chrome` — cross-platform Chrome detection, also reused
  by ``social.py``.

Chrome detection order:

* ``shutil.which`` for any of ``google-chrome``, ``google-chrome-stable``,
  ``chromium``, ``chromium-browser``, ``chrome``, ``msedge``.
* macOS fallback: ``/Applications/Google Chrome.app/Contents/MacOS/Google Chrome``,
  Brave, Edge.
* Windows fallback: typical ``Program Files`` paths.

If nothing is found we raise :class:`ChromeNotFoundError` with an
actionable message.
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


class ChromeNotFoundError(RuntimeError):
    """Raised when no headless-Chrome-capable browser is available."""


_CANDIDATE_NAMES = (
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "chrome",
    "brave-browser",
    "msedge",
    "microsoft-edge",
)


_MAC_PATHS = (
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
)


_WINDOWS_PATHS = (
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
)


def find_chrome() -> str:
    """Return the path to a Chrome-compatible browser, else raise.

    Search order:

    1. ``CHROME`` environment variable if set.
    2. ``shutil.which`` for each known executable name.
    3. Platform-specific filesystem fallbacks.
    """
    env = os.environ.get("CHROME")
    if env and Path(env).exists():
        return env

    for name in _CANDIDATE_NAMES:
        found = shutil.which(name)
        if found:
            return found

    if sys.platform == "darwin":
        for path in _MAC_PATHS:
            if Path(path).exists():
                return path
    elif sys.platform.startswith("win"):
        for path in _WINDOWS_PATHS:
            if Path(path).exists():
                return path

    raise ChromeNotFoundError(
        "No Chrome / Chromium / Edge / Brave executable found. "
        "Install one of them, or set the CHROME environment variable to "
        "the absolute path of the binary, then retry."
    )


def html_to_pdf(html: str, out_path: Path | str, *,
                paged_js_path: Path | str | None = None,
                wait_seconds: float = 2.0) -> Path:
    """Write ``html`` to a temporary file and run headless Chrome to convert
    it to a PDF at ``out_path``.

    Parameters
    ----------
    html
        The full HTML document. It can reference ``paged.polyfill.js``.
    out_path
        Target PDF path (will be overwritten).
    paged_js_path
        If given, copies that file next to the temporary HTML so the
        ``<script src="paged.polyfill.js">`` reference resolves locally.
    wait_seconds
        How long the renderer should wait before printing (Paged.js does
        its layout asynchronously). Chrome supports
        ``--virtual-time-budget=Nms`` for this.
    """
    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    chrome = find_chrome()  # may raise ChromeNotFoundError

    with tempfile.TemporaryDirectory(prefix="strikke-pdf-") as tdir:
        tdir_p = Path(tdir)
        html_path = tdir_p / "pattern.html"
        html_path.write_text(html, encoding="utf-8")
        if paged_js_path is not None:
            shutil.copy2(str(paged_js_path), tdir_p / "paged.polyfill.js")

        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            f"--virtual-time-budget={int(wait_seconds * 1000)}",
            f"--print-to-pdf={out_path}",
            html_path.as_uri(),
        ]
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=120,
            )
        except FileNotFoundError as e:
            raise ChromeNotFoundError(
                f"Chrome path resolved to {chrome!r} but couldn't be executed: {e}"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                f"Chrome timed out after 120 s rendering the PDF: {e}"
            ) from e

        # Some Chrome builds exit with a non-zero status even on success
        # if there were warnings. Trust the file.
        if not out_path.exists():
            stderr = proc.stderr.decode("utf-8", errors="replace") if proc.stderr else ""
            raise RuntimeError(
                f"Chrome did not produce a PDF at {out_path}.\n"
                f"Command: {' '.join(cmd)}\n"
                f"stderr:\n{stderr}"
            )
    return out_path


# ---------------------------------------------------------------------------
# Routing layer — WeasyPrint primary, Chrome fallback.
# ---------------------------------------------------------------------------

# Importing the WeasyPrint helper is cheap (the module just probes for
# weasyprint at import-time). The actual ``weasyprint`` package import
# can fail silently and surface as ``weasyprint_available = False``.
from . import pdf_weasy as _pdf_weasy  # noqa: E402

# Renderers callers can request via ``--pdf-renderer``.
_VALID_RENDERERS = ("auto", "weasy", "chrome")


def weasyprint_available() -> bool:
    """Return whether WeasyPrint is importable in this interpreter.

    Re-exported as a callable (rather than a constant) so tests can
    monkeypatch :data:`pdf_weasy.weasyprint_available` and have the
    routing layer pick up the change without reimporting :mod:`pdf`.
    """
    return bool(_pdf_weasy.weasyprint_available)


def chrome_available() -> bool:
    """Return whether a headless-capable Chrome/Chromium binary exists."""
    try:
        find_chrome()
    except ChromeNotFoundError:
        return False
    return True


def render_pdf(html: str, out_path: Path | str, *,
               paged_js_path: Path | str | None = None,
               renderer: str = "auto",
               wait_seconds: float = 2.0) -> Path:
    """Render ``html`` to a PDF at ``out_path``.

    Picks WeasyPrint if available, else Chrome. Pass ``renderer="weasy"``
    or ``renderer="chrome"`` to force one specific engine; ``"auto"``
    (default) probes WeasyPrint first.

    Parameters
    ----------
    html
        Full HTML document. May reference ``style.css`` /
        ``paged.polyfill.js`` either inlined (preferred) or relatively.
    out_path
        Target PDF path.
    paged_js_path
        Only used by the Chrome path. WeasyPrint implements Paged Media
        natively and ignores this.
    renderer
        ``"auto"`` (default), ``"weasy"``, or ``"chrome"``.
    wait_seconds
        Chrome-only: how long Paged.js gets to lay out before printing.

    Raises
    ------
    ValueError
        If ``renderer`` is unknown, or if no renderer is available
        (neither WeasyPrint nor Chrome).
    ChromeNotFoundError
        If ``renderer="chrome"`` is forced and Chrome isn't installed.
    """
    if renderer not in _VALID_RENDERERS:
        raise ValueError(
            f"Unknown PDF renderer {renderer!r}; "
            f"valid choices: {', '.join(_VALID_RENDERERS)}."
        )

    if renderer == "weasy":
        if not weasyprint_available():
            raise ValueError(
                "PDF renderer 'weasy' was forced but WeasyPrint is not "
                "installed. Run `pip install weasyprint` or pass "
                "--pdf-renderer chrome (requires Chrome / Chromium)."
            )
        return _pdf_weasy.render_pdf_weasy(html, out_path)

    if renderer == "chrome":
        # Let ChromeNotFoundError propagate; callers in generate.py
        # catch it and print a clear hint.
        return html_to_pdf(html, out_path,
                           paged_js_path=paged_js_path,
                           wait_seconds=wait_seconds)

    # renderer == "auto": prefer WeasyPrint, fall back to Chrome,
    # else raise a clear actionable error.
    if weasyprint_available():
        return _pdf_weasy.render_pdf_weasy(html, out_path)

    if chrome_available():
        return html_to_pdf(html, out_path,
                           paged_js_path=paged_js_path,
                           wait_seconds=wait_seconds)

    raise ValueError(
        "No PDF renderer available. Install WeasyPrint with "
        "`pip install weasyprint` (recommended), or install Chrome / "
        "Chromium / Edge / Brave so headless rendering can fall back "
        "to a browser."
    )
