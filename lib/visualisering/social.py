"""Social-media preview cards.

Renders a Pattern as a single-page social card (1080×1080 square or
1080×1920 story) and screenshots it via headless Chrome. Uses a separate
HTML template (``templates/social_card.html``) and CSS
(``assets/social.css``) — *not* the print pattern template — because the
visual language is completely different (display fonts, dramatic colors,
big stats, no Paged.js pagination).

Public API:

    generate_social_preview(pattern, *, format, output_path) -> Path
    build_social_html(pattern, *, format, lang="da") -> str

The first runs Chrome and writes a PNG. If Chrome is unavailable, it
falls back: writes the standalone HTML next to ``output_path`` (with a
``.html`` extension) and raises :class:`ChromeNotFoundError` so the CLI
can surface the situation.

Format aliases:

    * ``"square"`` / ``"1:1"``   → 1080 × 1080 (Instagram feed)
    * ``"story"``  / ``"9:16"``  → 1080 × 1920 (Story / TikTok)
"""

from __future__ import annotations
import html as _htmllib
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Iterable

from .pattern import Pattern
from .lang import t
from .pdf import find_chrome, ChromeNotFoundError


_HERE = Path(__file__).resolve().parent
_ASSETS = _HERE / "assets"
_TEMPLATES = _HERE / "templates"


# Format → (width, height in pixels, css class suffix).
_FORMATS: dict[str, tuple[int, int, str]] = {
    "square": (1080, 1080, "square"),
    "1:1":    (1080, 1080, "square"),
    "1x1":    (1080, 1080, "square"),
    "story":  (1080, 1920, "story"),
    "9:16":   (1080, 1920, "story"),
}


def _resolve_format(fmt: str) -> tuple[int, int, str]:
    key = fmt.strip().lower()
    if key not in _FORMATS:
        raise ValueError(
            f"unknown social format {fmt!r}; expected one of "
            f"{sorted(set(_FORMATS))}"
        )
    return _FORMATS[key]


# ---------------------------------------------------------------------------
# Templating
# ---------------------------------------------------------------------------

def _h(s) -> str:
    return _htmllib.escape(str(s))


def _fill(template: str, **kwargs) -> str:
    out = template
    for key in set(re.findall(r"\{\{(\w+)\}\}", template)):
        out = out.replace("{{" + key + "}}", str(kwargs.get(key, "")))
    return out


def _stat_lines(p: Pattern, lang: str) -> list[tuple[str, str]]:
    """Return up to 4 (label, value) tuples that work as bullet stats."""
    inputs = p.inputs or {}
    g = inputs.get("gauge", {}) or {}
    sts10 = int(g.get("sts_per_10cm", 0))
    rows10 = int(g.get("rows_per_10cm", 0))
    out: list[tuple[str, str]] = []

    if "finished_bust_cm" in inputs:
        out.append((t("cover.label.bust_finished", lang),
                    f"{inputs['finished_bust_cm']:.0f} cm"))
    if "finished_circumference_cm" in inputs:
        out.append((t("cover.label.head_finished", lang),
                    f"{inputs['finished_circumference_cm']:.0f} cm"))
    if "width_cm" in inputs and "length_cm" in inputs:
        out.append((t("cover.label.width", lang) + " / "
                    + t("cover.label.length", lang),
                    f"{inputs['width_cm']:.0f} × {inputs['length_cm']:.0f} cm"))
    if "actual_diameter_cm" in inputs:
        out.append((t("cover.label.diameter_actual", lang),
                    f"{inputs['actual_diameter_cm']:.1f} cm"))
    elif "diameter_cm" in inputs:
        out.append((t("cover.label.diameter_target", lang),
                    f"{inputs['diameter_cm']:.1f} cm"))
    if "foot_length_cm" in inputs:
        out.append((t("cover.label.foot_length", lang),
                    f"{inputs['foot_length_cm']:.0f} cm"))

    # Always include gauge as one of the bullets.
    is_crochet = inputs.get("_domain") == "crochet"
    gauge_label = t(
        "cover.label.gauge_crochet" if is_crochet else "cover.label.gauge",
        lang,
    )
    if lang == "en":
        gauge_value = f"{sts10} sts × {rows10} rows / 10 cm"
    else:
        unit_rows = "omg" if is_crochet else "p"
        gauge_value = f"{sts10} m × {rows10} {unit_rows} / 10 cm"
    out.append((gauge_label, gauge_value))

    # Dedupe, keep first 4.
    seen: set[str] = set()
    deduped: list[tuple[str, str]] = []
    for lbl, val in out:
        if lbl in seen:
            continue
        seen.add(lbl)
        deduped.append((lbl, val))
        if len(deduped) >= 4:
            break
    return deduped


def build_social_html(pattern: Pattern, *, format: str = "square",
                      lang: str = "da",
                      handle: str = "@strikkeopskrift") -> str:
    """Build the standalone HTML for a social-card screenshot.

    ``format`` accepts the same aliases as :func:`generate_social_preview`.
    """
    _w, _h_px, css_class = _resolve_format(format)
    template = (_TEMPLATES / "social_card.html").read_text(encoding="utf-8")
    css = (_ASSETS / "social.css").read_text(encoding="utf-8")

    inputs = pattern.inputs or {}
    is_crochet = inputs.get("_domain") == "crochet"
    eyebrow = t("skill.crochet.eyebrow" if is_crochet
                else "skill.knit.eyebrow", lang)
    subtitle = t(f"construction.{pattern.construction}", lang)

    diff = (pattern.difficulty or "").strip() or "intermediate"
    diff_label = t("difficulty", lang)
    diff_value = t(f"difficulty.{diff}", lang)

    md = inputs.get("metadata") or {}
    yarn = md.get("yarn", "")
    yarn_badge = (f'<span class="badge yarn">{_h(yarn)}</span>'
                  if yarn else "")
    designer = md.get("designer") or ""
    if md.get("year"):
        designer = (f"{designer} · {md['year']}".strip(" ·")
                    if designer else str(md["year"]))

    stats = _stat_lines(pattern, lang)
    stats_html = "".join(
        f'<li><span class="stat-label">{_h(lbl)}</span>'
        f'<span class="stat-value">{_h(val)}</span></li>'
        for lbl, val in stats
    )

    footer = t("skill.crochet.generator" if is_crochet
               else "skill.knit.generator", lang).split("·")[0].strip()

    return _fill(
        template,
        HTML_LANG=("en" if lang == "en" else "da"),
        TITLE=_h(pattern.name),
        FORMAT=css_class,
        INLINE_CSS=css,
        EYEBROW=_h(eyebrow),
        HANDLE=_h(handle),
        NAME=_h(pattern.name),
        SUBTITLE=_h(subtitle),
        DIFFICULTY_LABEL=_h(diff_label),
        DIFFICULTY_VALUE=_h(diff_value),
        YARN_BADGE=yarn_badge,
        STATS_HTML=stats_html,
        FOOTER=_h(footer),
        DESIGNER=_h(designer),
    )


# ---------------------------------------------------------------------------
# PNG via headless Chrome
# ---------------------------------------------------------------------------

def generate_social_preview(pattern: Pattern, *, format: str,
                             output_path: Path | str,
                             lang: str = "da",
                             handle: str = "@strikkeopskrift",
                             wait_seconds: float = 1.5) -> Path:
    """Render a social-card PNG.

    Always writes the standalone HTML next to ``output_path`` (with a
    ``.html`` suffix replacing ``.png``) — that way users without Chrome
    can still open the file in any browser and screenshot manually.

    If Chrome is available, also writes the PNG. Returns the resolved
    PNG path on success. Raises :class:`ChromeNotFoundError` (after the
    HTML is written) if no Chrome binary can be located.
    """
    width, height, _css = _resolve_format(format)
    output_path = Path(output_path).resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    html_text = build_social_html(pattern, format=format, lang=lang,
                                  handle=handle)
    fallback_html = output_path.with_suffix(".html")
    fallback_html.write_text(html_text, encoding="utf-8")

    try:
        chrome = find_chrome()
    except ChromeNotFoundError:
        # HTML fallback is already on disk; re-raise so the CLI can tell
        # the user.
        raise

    with tempfile.TemporaryDirectory(prefix="strikke-social-") as tdir:
        tdir_p = Path(tdir)
        html_path = tdir_p / "card.html"
        html_path.write_text(html_text, encoding="utf-8")
        cmd = [
            chrome,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--hide-scrollbars",
            f"--window-size={width},{height}",
            f"--virtual-time-budget={int(wait_seconds * 1000)}",
            f"--screenshot={output_path}",
            html_path.as_uri(),
        ]
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=60,
            )
        except FileNotFoundError as e:
            raise ChromeNotFoundError(
                f"Chrome path resolved to {chrome!r} but couldn't be "
                f"executed: {e}"
            ) from e
        except subprocess.TimeoutExpired as e:
            raise RuntimeError(
                f"Chrome timed out after 60 s rendering the social card: {e}"
            ) from e

        if not output_path.exists():
            stderr = (proc.stderr.decode("utf-8", errors="replace")
                      if proc.stderr else "")
            raise RuntimeError(
                f"Chrome did not produce a PNG at {output_path}.\n"
                f"Command: {' '.join(cmd)}\n"
                f"stderr:\n{stderr}"
            )
    return output_path


def available_formats() -> list[str]:
    """Return all accepted format aliases (square, 1:1, story, 9:16, …)."""
    return sorted(_FORMATS)


def format_dimensions(format: str) -> tuple[int, int]:
    """Return ``(width, height)`` for a format alias."""
    w, h, _ = _resolve_format(format)
    return w, h
