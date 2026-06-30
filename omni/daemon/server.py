"""omnid: a localhost-only HTTP control API.

The AI agent (and the desktop UI) call this API instead of running raw shell
commands. Endpoints mirror the documented control surface:

    POST /v1/apps/open        {"name": "Firefox"}
    POST /v1/system/brightness {"value": 40}
    POST /v1/system/volume     {"value": 30}
    POST /v1/files/search      {"query": "resume"}

Bound to 127.0.0.1 by default so it is never exposed off-host.
"""
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Any, Dict

from ..registry import AppRegistry
from ..runtimes.manager import RuntimeManager
from ..system.controls import SystemControls


class _Handler(BaseHTTPRequestHandler):
    registry: AppRegistry
    runtimes: RuntimeManager
    controls: SystemControls

    def _send(self, code: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _body(self) -> Dict[str, Any]:
        length = int(self.headers.get("Content-Length", 0))
        if not length:
            return {}
        return json.loads(self.rfile.read(length).decode("utf-8"))

    def log_message(self, *_args) -> None:  # silence default logging
        pass

    def do_POST(self) -> None:  # noqa: N802 (http.server API)
        try:
            data = self._body()
        except json.JSONDecodeError:
            return self._send(400, {"error": "invalid json"})

        if self.path == "/v1/apps/open":
            app = self.registry.get(data.get("name", ""))
            if app is None:
                return self._send(404, {"error": "app not found"})
            res = self.runtimes.launch(app)
            return self._send(200, {"success": res.success, "message": res.message})

        if self.path == "/v1/system/brightness":
            res = self.controls.set_brightness(int(data.get("value", 0)))
            return self._send(200, {"success": res.success, "message": res.message})

        if self.path == "/v1/system/volume":
            res = self.controls.set_volume(int(data.get("value", 0)))
            return self._send(200, {"success": res.success, "message": res.message})

        if self.path == "/v1/files/search":
            hits = self.controls.search_files(data.get("query", ""))
            return self._send(200, {"matches": hits})

        return self._send(404, {"error": "unknown endpoint"})

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/v1/health":
            return self._send(200, {"status": "ok"})
        return self._send(404, {"error": "unknown endpoint"})


def build_server(host: str = "127.0.0.1", port: int = 8765) -> HTTPServer:
    _Handler.registry = AppRegistry()
    _Handler.runtimes = RuntimeManager()
    _Handler.controls = SystemControls()
    return HTTPServer((host, port), _Handler)


def main() -> None:
    parser = argparse.ArgumentParser(description="omnid — OmniOS local control daemon")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()
    server = build_server(args.host, args.port)
    print(f"omnid listening on http://{args.host}:{args.port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.shutdown()


if __name__ == "__main__":
    main()
