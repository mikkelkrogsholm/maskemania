"""WeasyPrint-based PDF renderer.

WeasyPrint is a Python-native HTML→PDF engine with no Chromium dependency
and active maintenance (variable fonts since v60). We use it as the
**primary** renderer, falling back to headless Chrome (see :mod:`pdf`) if
WeasyPrint isn't installed.

WeasyPrint differs from Chrome in two ways that affect us:

1. **No JavaScript.** ``paged.polyfill.js`` is irrelevant — WeasyPrint
   already implements the CSS Paged Media spec natively, so the polyfill
   simply isn't needed.
2. **Strict ``base_url`` resolution.** Relative ``<link rel="stylesheet">``
   hrefs resolve against the HTML file's directory, but if the caller
   passes raw HTML text (no on-disk file), we must hand WeasyPrint the
   ``assets/`` directory explicitly so ``style.css`` references resolve.

The renderer accepts either a raw HTML string or a path. Either way the
asset directory (``lib/visualisering/assets/``) is exposed as the
``base_url`` so any relative asset references resolve. In practice the
CLI inlines the CSS in :func:`lib.visualisering.html.render_html`, so
this is mostly defensive.

System dependencies (Cairo, Pango, GDK-PixBuf) are bundled with the
``weasyprint`` wheel on most platforms but on macOS may need
``brew install pango``. If import fails we set ``weasyprint_available``
to False and the routing layer in :mod:`pdf` falls back to Chrome.
"""

from __future__ import annotations

from pathlib import Path

# Probe for weasyprint at module-import time so the routing layer in
# pdf.py can branch without re-importing on every call. We swallow *all*
# exceptions here (not just ImportError) because some platforms raise
# OSError when the underlying Cairo/Pango libs aren't installed —
# treating that as "not available" lets us fall back to Chrome cleanly.
try:  # pragma: no cover - import-time probe is environment-dependent
    from weasyprint import HTML as _WeasyHTML  # type: ignore
    weasyprint_available = True
    _import_error: Exception | None = None
except Exception as e:  # pragma: no cover
    _WeasyHTML = None  # type: ignore[assignment]
    weasyprint_available = False
    _import_error = e


_ASSETS_DIR = Path(__file__).resolve().parent / "assets"


def render_pdf_weasy(html: str, out_path: Path | str, *,
                     base_url: Path | str | None = None) -> Path:
    """Render ``html`` to a PDF at ``out_path`` via WeasyPrint.

    Parameters
    ----------
    html
        Full HTML document as a string. CSS may be inlined (preferred —
        :func:`lib.visualisering.html.render_html` does this by default)
        or referenced relatively against ``base_url``.
    out_path
        Target PDF path. Parent directories are created if missing.
    base_url
        Directory used to resolve relative URLs in the HTML (``href``,
        ``src``). Defaults to ``lib/visualisering/assets/`` so a stray
        ``style.css`` reference still resolves. Pass an explicit path
        when the HTML pulls assets from a different location.

    Returns
    -------
    Path
        Resolved path of the written PDF.

    Raises
    ------
    RuntimeError
        If WeasyPrint isn't importable. Callers should check
        :data:`weasyprint_available` first; this guard is a defensive
        belt-and-braces.
    """
    if not weasyprint_available:
        raise RuntimeError(
            "WeasyPrint is not available "
            f"(import failed: {_import_error!r}). "
            "Install with `pip install weasyprint`, or use the Chrome "
            "fallback path."
        )

    out_path = Path(out_path).resolve()
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if base_url is None:
        base_url_str: str = str(_ASSETS_DIR)
    else:
        base_url_str = str(Path(base_url).resolve())

    # WeasyPrint API: HTML(string=..., base_url=...).write_pdf(path)
    _WeasyHTML(string=html, base_url=base_url_str).write_pdf(str(out_path))
    return out_path
