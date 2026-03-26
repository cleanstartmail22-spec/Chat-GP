#!/usr/bin/env python3
"""Simple browser-based PDF to Excel tool with stdlib HTTP server.

Run:
    python app.py
Open:
    http://127.0.0.1:5000
"""

from __future__ import annotations

import html
import io
import os
import shutil
import socketserver
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler
from pathlib import Path
from tempfile import mkdtemp
from urllib.parse import parse_qs, urlparse

HTML_PAGE = """<!doctype html>
<html lang=\"en\">
<head>
  <meta charset=\"UTF-8\" />
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
  <title>PDF to Excel Extractor</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f4f7fb; margin: 0; display: grid; place-items: center; min-height: 100vh; }
    .card { width: min(560px, 92vw); background: #fff; border-radius: 12px; padding: 24px; box-shadow: 0 10px 30px rgba(0,0,0,.08); }
    .flash { margin: 12px 0; padding: 10px; border-radius: 8px; }
    .error { background: #ffe9e9; color: #8d1e1e; }
    .ok { background: #e8f8ec; color: #0d6b2d; }
    button { margin-top: 12px; background: #2663eb; color: #fff; border: 0; border-radius: 8px; padding: 10px 14px; cursor: pointer; }
  </style>
</head>
<body>
  <main class=\"card\">
    <h1>PDF to Excel</h1>
    <p>Upload a PDF and download an Excel file with extracted tables and text.</p>
    __MESSAGE_BLOCK__
    <form method=\"post\" action=\"/convert\" enctype=\"multipart/form-data\">
      <input type=\"file\" name=\"pdf_file\" accept=\"application/pdf,.pdf\" required />
      <br />
      <button type=\"submit\">Convert to Excel</button>
    </form>
  </main>
</body>
</html>
"""


class PDFToExcelHandler(BaseHTTPRequestHandler):
    def do_GET(self):  # noqa: N802
        parsed = urlparse(self.path)
        if parsed.path != "/":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        params = parse_qs(parsed.query)
        message = params.get("msg", [""])[0]
        kind = params.get("kind", [""])[0]
        block = ""
        if message:
            safe = html.escape(message)
            css = "ok" if kind == "ok" else "error"
            block = f'<div class="flash {css}">{safe}</div>'

        body = HTML_PAGE.replace("__MESSAGE_BLOCK__", block).encode("utf-8")
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):  # noqa: N802
        if self.path != "/convert":
            self.send_error(HTTPStatus.NOT_FOUND, "Not found")
            return

        content_type = self.headers.get("Content-Type", "")
        if "multipart/form-data" not in content_type:
            self._redirect_with_message("Invalid request encoding.")
            return

        try:
            import cgi

            form = cgi.FieldStorage(
                fp=self.rfile,
                headers=self.headers,
                environ={
                    "REQUEST_METHOD": "POST",
                    "CONTENT_TYPE": content_type,
                },
            )
        except Exception:
            self._redirect_with_message("Failed to read upload payload.")
            return

        field = form.getfirst("pdf_file")
        upload = form["pdf_file"] if "pdf_file" in form else None
        if upload is None or not getattr(upload, "filename", None):
            self._redirect_with_message("Please choose a PDF file.")
            return

        filename = Path(str(upload.filename)).name
        if not filename.lower().endswith(".pdf"):
            self._redirect_with_message("Only .pdf files are supported.")
            return

        temp_dir = Path(mkdtemp(prefix="pdf2excel_"))
        input_path = temp_dir / filename
        output_name = f"{Path(filename).stem}_extracted.xlsx"
        output_path = temp_dir / output_name

        try:
            file_data = upload.file.read()
            input_path.write_bytes(file_data)

            from pdf_to_excel import extract_pdf_to_excel

            extract_pdf_to_excel(input_path, output_path)
            out_data = output_path.read_bytes()
        except ModuleNotFoundError:
            self._redirect_with_message("Missing dependencies. Run: pip install -r requirements.txt")
            return
        except Exception:
            self._redirect_with_message("Failed to process PDF. Please verify the file and try again.")
            return
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        self.send_response(HTTPStatus.OK)
        self.send_header(
            "Content-Type",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        self.send_header("Content-Disposition", f'attachment; filename="{output_name}"')
        self.send_header("Content-Length", str(len(out_data)))
        self.end_headers()
        self.wfile.write(out_data)

    def log_message(self, fmt: str, *args):
        # Keep stdout readable.
        return

    def _redirect_with_message(self, message: str):
        encoded = message.replace(" ", "+")
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header("Location", f"/?msg={encoded}&kind=error")
        self.end_headers()


class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True


def main() -> None:
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))

    with ThreadedTCPServer((host, port), PDFToExcelHandler) as httpd:
        print(f"Server running on {host}:{port}")
        if host == "0.0.0.0":
            print(f"Open locally: http://127.0.0.1:{port}")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
