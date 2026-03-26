#!/usr/bin/env python3
"""Browser-based PDF to Excel extraction tool."""

from __future__ import annotations

import os
import shutil
from pathlib import Path
from tempfile import mkdtemp

from flask import (
    Flask,
    after_this_request,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    url_for,
)
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 25 * 1024 * 1024  # 25 MB
app.secret_key = os.getenv("FLASK_SECRET_KEY", "pdf-to-excel-dev-key")


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/convert")
def convert():
    uploaded = request.files.get("pdf_file")

    if uploaded is None or uploaded.filename == "":
        flash("Please choose a PDF file.", "error")
        return redirect(url_for("index"))

    filename = secure_filename(uploaded.filename)
    if not filename.lower().endswith(".pdf"):
        flash("Only .pdf files are supported.", "error")
        return redirect(url_for("index"))

    output_name = f"{Path(filename).stem}_extracted.xlsx"

    temp_dir = Path(mkdtemp(prefix="pdf2excel_"))
    input_path = temp_dir / filename
    output_path = temp_dir / output_name

    @after_this_request
    def cleanup_temp_dir(response):
        shutil.rmtree(temp_dir, ignore_errors=True)
        return response

    uploaded.save(input_path)

    try:
        from pdf_to_excel import extract_pdf_to_excel

        extract_pdf_to_excel(input_path, output_path)
    except ModuleNotFoundError:
        flash("Server dependencies are missing. Install requirements and try again.", "error")
        return redirect(url_for("index"))
    except Exception:
        flash("Failed to process PDF. Please verify the file and try again.", "error")
        return redirect(url_for("index"))

    return send_file(
        output_path,
        as_attachment=True,
        download_name=output_name,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )


if __name__ == "__main__":
    app.run(debug=False)
