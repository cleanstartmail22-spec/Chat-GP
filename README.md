# PDF Document Extraction to Excel Tool

This project now supports both:

- **Browser app** (upload PDF in a web page, download `.xlsx`)
- **CLI script** (`python pdf_to_excel.py input.pdf output.xlsx`)

## Features

- Extracts detected tables from PDF pages into separate Excel sheets.
- Adds an `Extracted_Text` sheet with page text lines.
- Adds a `No_Data` sheet if nothing is extracted.
- Auto-sizes column widths for readability.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Run in Browser (recommended)

```bash
python app.py
```

Then open `http://127.0.0.1:5000` in your browser, upload a PDF, and download the converted Excel file.

## CLI usage

```bash
python pdf_to_excel.py <input.pdf> <output.xlsx>
```

Example:

```bash
python pdf_to_excel.py invoice.pdf extracted.xlsx
```

## Notes

- Table extraction quality depends on the PDF structure.
- Scanned/image-only PDFs usually require OCR before extraction.
