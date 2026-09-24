"""Local-only browser UI; run: python app.py. Not an internet hosting server."""
from __future__ import annotations

import argparse
import base64
import json
import secrets
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from converter import ConversionError, clean, extract_pdf, export_excel, validate_template

ROOT = Path(__file__).resolve().parent
MAX_REQUEST = 30 * 1024 * 1024
TOKEN = secrets.token_urlsafe(32)


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass  # Never log filenames or document contents.

    def send(self, status, body, content_type="application/json; charset=utf-8"):
        if not isinstance(body, bytes):
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; object-src 'none'; frame-ancestors 'none'; base-uri 'none'")
        self.end_headers()
        self.wfile.write(body)

    def valid_host(self):
        return self.headers.get("Host") in {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}

    def do_GET(self):
        if not self.valid_host():
            return self.send(403, {"error": "Invalid host."})
        routes = {"/": ("web/index.html", "text/html; charset=utf-8"),
                  "/app.js": ("web/app.js", "application/javascript; charset=utf-8"),
                  "/style.css": ("web/style.css", "text/css; charset=utf-8"),
                  "/sample.pdf": ("examples/demo-quotation.pdf", "application/pdf")}
        if self.path == "/api/config":
            return self.send(200, {"token": TOKEN, "template": json.loads((ROOT / "templates/quotation.json").read_text(encoding="utf-8"))})
        if self.path in routes:
            file, mime = routes[self.path]
            return self.send(200, (ROOT / file).read_bytes(), mime)
        self.send(404, {"error": "Not found."})

    def do_POST(self):
        if not self.valid_host() or self.headers.get("X-TableBridge-Token") != TOKEN:
            return self.send(403, {"error": "Refresh this page to reconnect. / 请刷新页面后重试。"})
        if self.path != "/api/convert":
            return self.send(404, {"error": "Not found."})
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 0 < size <= MAX_REQUEST:
                raise ConversionError("Batch exceeds 20 MB total or request is empty. / 请减少文件数量或大小。")
            payload = json.loads(self.rfile.read(size))
            if not isinstance(payload, dict):
                raise ConversionError("Request must be a JSON object.")
            template = validate_template(payload.get("template"))
            files = payload.get("files")
            if not isinstance(files, list) or not 1 <= len(files) <= 10:
                raise ConversionError("Select 1–10 PDFs. / 请选择 1–10 个 PDF。")
            results, total_size, names = [], 0, set()
            for item in files:
                if not isinstance(item, dict) or not isinstance(item.get("name"), str) or not isinstance(item.get("data"), str):
                    raise ConversionError("Invalid file payload.")
                name = item["name"].replace("\\", "/").split("/")[-1]
                if not name or len(name) > 200 or not name.lower().endswith(".pdf"):
                    raise ConversionError("Each file needs a .pdf name shorter than 200 characters.")
                if name in names:
                    raise ConversionError("Duplicate filenames; rename files before importing. / 文件名重复，请先重命名。")
                names.add(name)
                data = base64.b64decode(item["data"], validate=True)
                total_size += len(data)
                if total_size > 20 * 1024 * 1024:
                    raise ConversionError("Batch exceeds 20 MB. / 批次总大小超过 20 MB。")
                results.append(extract_pdf(data, name, template))
            workbook = export_excel(results, template)
            headers = [clean(c["name"]) for c in template["columns"]] + ["Source file", "Page", "Table row"]
            records = [row for result in results for row in result["records"]]
            self.send(200, {"headers": headers, "rows": records[:100], "row_count": len(records),
                            "files": len(results), "pages": sum(r["pages"] for r in results),
                            "warnings": [w for r in results for w in r["warnings"]],
                            "xlsx": base64.b64encode(workbook).decode("ascii")})
        except (ValueError, KeyError, TypeError) as exc:
            self.send(400, {"error": str(exc)})
        except Exception:
            self.send(500, {"error": "Conversion failed. Check the PDF and template. / 转换失败，请检查文件和模板。"})


def main():
    parser = argparse.ArgumentParser(description="TableBridge: local PDF tables to Excel")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--no-browser", action="store_true")
    args = parser.parse_args()
    try:
        server = HTTPServer(("127.0.0.1", args.port), Handler)
    except OSError:
        raise SystemExit("Port unavailable. Try: python app.py --port 8766")
    url = f"http://127.0.0.1:{server.server_port}"
    print(f"TableBridge is running at {url}\nKeep this terminal open. Press Ctrl+C to stop.")
    if not args.no_browser:
        threading.Timer(0.5, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
