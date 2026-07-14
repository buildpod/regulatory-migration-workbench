"""Small local HTTP server exposing the workbench API and browser UI."""

from __future__ import annotations

import json
import mimetypes
import os
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

from . import __version__
from .learning import LEARNING_CONTENT
from .quality import analyse_csv
from .sources import SOURCE_CATALOG, check_sources


ROOT = Path(__file__).resolve().parent
WEB_ROOT = ROOT / "web"
SAMPLE_FILE = ROOT.parent / "sample_data" / "sample_application_extract.csv"


def _json_bytes(payload: object) -> bytes:
    return json.dumps(payload, ensure_ascii=False).encode("utf-8")


class WorkbenchHandler(BaseHTTPRequestHandler):
    server_version = "RegulatoryMigrationWorkbench/0.1"

    def log_message(self, format: str, *args: object) -> None:
        return

    def _send(self, status: int, body: bytes, content_type: str = "application/json; charset=utf-8") -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        content_length = int(self.headers.get("Content-Length", "0"))
        if content_length > 8_000_000:
            raise ValueError("Request is too large for the local MVP")
        raw = self.rfile.read(content_length)
        value = json.loads(raw.decode("utf-8"))
        if not isinstance(value, dict):
            raise ValueError("Request body must be a JSON object")
        return value

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/api/health":
            self._send(200, _json_bytes({"status": "ok", "service": "regulatory-migration-workbench", "version": __version__}))
            return
        if path == "/api/sources":
            self._send(200, _json_bytes({"sources": SOURCE_CATALOG}))
            return
        if path == "/api/learning":
            self._send(200, _json_bytes(LEARNING_CONTENT))
            return
        if path == "/api/sample":
            self._send(200, _json_bytes({"filename": SAMPLE_FILE.name, "content": SAMPLE_FILE.read_text(encoding="utf-8")}))
            return
        self._serve_static(path)

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        try:
            body = self._read_json()
            if path == "/api/analyse":
                content = body.get("content")
                if not isinstance(content, str):
                    raise ValueError("content must be a string")
                result = analyse_csv(content, str(body.get("filename") or "uploaded dataset"), body.get("delimiter"))
                self._send(200, _json_bytes(result))
                return
            if path == "/api/source-health":
                ids = body.get("source_ids")
                if ids is not None and not isinstance(ids, list):
                    raise ValueError("source_ids must be a list")
                self._send(200, _json_bytes({"checked_at": datetime.now(timezone.utc).isoformat(timespec="seconds"), "results": check_sources(ids)}))
                return
            self._send(404, _json_bytes({"error": "Not found"}))
        except (ValueError, json.JSONDecodeError) as exc:
            self._send(400, _json_bytes({"error": str(exc)}))
        except Exception as exc:  # Keep the local utility readable instead of leaking a traceback to the browser.
            self._send(500, _json_bytes({"error": f"Unexpected server error: {exc}"}))

    def _serve_static(self, path: str) -> None:
        relative = "index.html" if path in {"", "/"} else path.lstrip("/")
        candidate = (WEB_ROOT / relative).resolve()
        if WEB_ROOT not in candidate.parents and candidate != WEB_ROOT:
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        if not candidate.is_file():
            self._send(404, b"Not found", "text/plain; charset=utf-8")
            return
        content_type = mimetypes.guess_type(candidate.name)[0] or "application/octet-stream"
        self._send(200, candidate.read_bytes(), f"{content_type}; charset=utf-8" if content_type.startswith("text/") else content_type)


def main() -> None:
    host = os.environ.get("WORKBENCH_HOST", "127.0.0.1")
    port = int(os.environ.get("WORKBENCH_PORT", "4174"))
    print(f"Regulatory Migration Workbench running at http://{host}:{port}")
    ThreadingHTTPServer((host, port), WorkbenchHandler).serve_forever()


if __name__ == "__main__":
    main()
