# PDF Document Extraction to Excel Tool

This project supports both:

- **Browser app** via a built-in Python web server (`app.py`)
- **CLI script** (`pdf_to_excel.py`)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run in Browser

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

If port 5000 is busy:

```bash
PORT=8000 python app.py
```

Then open `http://127.0.0.1:8000`.

## CLI usage

```bash
python pdf_to_excel.py <input.pdf> <output.xlsx>
```

## Notes

- The browser tool itself runs on Python stdlib (no Flask required).
- PDF extraction still requires `pdfplumber` and `openpyxl`.
- Scanned/image-only PDFs usually require OCR first.
