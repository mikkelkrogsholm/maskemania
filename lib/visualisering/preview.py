"""Tiny live-preview HTTP server with browser auto-reload.

Pure stdlib (no ``watchdog``). Polls ``os.stat`` mtimes on a watched set
of files every ~0.5 s; the served HTML embeds a small JS snippet that
polls ``/_changed?since=<ts>`` and reloads when the server reports a
newer mtime.

Usage from a skill::

    from lib.visualisering.preview import serve_pattern
    serve_pattern(lambda: render_html(generate_hue(...)),
                  watch=[lib_dir / "components", skill_dir / "knitlib"])
"""

from __future__ import annotations

import http.server
import os
import threading
import time
from pathlib import Path
from typing import Callable, Iterable
from urllib.parse import urlparse, parse_qs


# JS injected into rendered HTML. Polls /_changed and reloads when the
# server reports a newer mtime than the one captured at page load.
_RELOAD_JS = """
<script>
(function() {
  var since = Date.now() / 1000;
  setInterval(async function() {
    try {
      var r = await fetch("/_changed?since=" + since, {cache: "no-store"});
      if (!r.ok) return;
      var j = await r.json();
      if (j.changed) { location.reload(); }
    } catch (e) {}
  }, 600);
})();
</script>
"""


def _scan_mtimes(paths: Iterable[Path]) -> float:
    """Return the most recent mtime across all files under the given paths."""
    latest = 0.0
    for p in paths:
        if not p.exists():
            continue
        if p.is_file():
            latest = max(latest, p.stat().st_mtime)
            continue
        for root, _dirs, files in os.walk(p):
            for f in files:
                full = os.path.join(root, f)
                try:
                    latest = max(latest, os.stat(full).st_mtime)
                except OSError:
                    pass
    return latest


def reload_script_tag() -> str:
    """Return the small JS snippet to inject before ``</body>``."""
    return _RELOAD_JS


def serve_pattern(render: Callable[[], str], *,
                  watch: Iterable[Path] = (),
                  host: str = "127.0.0.1",
                  port: int = 8765,
                  paged_js_path: Path | None = None) -> None:
    """Serve the result of ``render()`` at ``http://<host>:<port>/`` and
    reload the browser automatically when any watched path changes.

    ``render`` is re-invoked on every request, so editing a construction
    file produces a fresh pattern on the next reload.

    Pure-stdlib: ``http.server.ThreadingHTTPServer`` + ``os.stat``-based
    polling. No external deps.
    """
    watch_paths = [Path(p).resolve() for p in watch]

    state = {"start_mtime": _scan_mtimes(watch_paths)}

    class PreviewRequestHandler(http.server.BaseHTTPRequestHandler):
        def log_message(self, fmt: str, *args) -> None:  # quiet noise
            pass

        def do_GET(self) -> None:
            url = urlparse(self.path)
            if url.path == "/" or url.path == "/index.html":
                try:
                    html = render()
                except Exception as exc:  # show the error in the browser
                    msg = (f"<h1>Render error</h1><pre>{type(exc).__name__}: "
                           f"{exc}</pre>")
                    self._respond(500, "text/html", msg.encode("utf-8"))
                    return
                self._respond(200, "text/html; charset=utf-8",
                              html.encode("utf-8"))
                return

            if url.path == "/_changed":
                qs = parse_qs(url.query)
                since = float((qs.get("since") or ["0"])[0])
                latest = _scan_mtimes(watch_paths)
                changed = latest > since
                body = b'{"changed": true}' if changed else b'{"changed": false}'
                self._respond(200, "application/json", body)
                return

            if url.path == "/paged.polyfill.js" and paged_js_path is not None:
                if paged_js_path.exists():
                    self._respond(200, "application/javascript",
                                  paged_js_path.read_bytes())
                    return

            # Try to serve a file from the cwd if it matches a watched path
            for w in watch_paths:
                candidate = w / url.path.lstrip("/")
                if candidate.exists() and candidate.is_file():
                    self._respond(200, _guess_mime(candidate),
                                  candidate.read_bytes())
                    return

            self._respond(404, "text/plain", b"not found")

        def _respond(self, code: int, ctype: str, body: bytes) -> None:
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(body)

    srv = http.server.ThreadingHTTPServer((host, port), PreviewRequestHandler)
    print(f"Live preview at http://{host}:{port}/  (Ctrl-C to stop)")
    print(f"Watching: {', '.join(str(p) for p in watch_paths) or '(nothing)'}")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\nstopped.")
    finally:
        srv.server_close()


def _guess_mime(path: Path) -> str:
    suffix = path.suffix.lower()
    return {
        ".html": "text/html; charset=utf-8",
        ".css": "text/css",
        ".js": "application/javascript",
        ".svg": "image/svg+xml",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".json": "application/json",
    }.get(suffix, "application/octet-stream")
