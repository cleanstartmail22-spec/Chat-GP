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

## Run in Browser (Local)

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

If port 5000 is busy:

```bash
PORT=8000 python app.py
```

Then open `http://127.0.0.1:8000`.

## Deploy in Browser (Public URL)

This repo includes a `Dockerfile` so you can deploy to any container host (Render, Railway, Fly.io, Azure Web App, etc.).

### Example: Docker run locally

```bash
docker build -t pdf2excel-web .
docker run -p 8080:8080 -e PORT=8080 pdf2excel-web
```

Open `http://127.0.0.1:8080`.

### Example: Render/Railway

- Create a new **Web Service** from this repository.
- Use **Docker** deployment (auto-detected by `Dockerfile`).
- Expose port `8080`.
- After deploy completes, open the generated public URL from your hosting provider.

## CLI usage

```bash
python pdf_to_excel.py <input.pdf> <output.xlsx>
```

## Notes

- The browser tool itself runs on Python stdlib (no Flask required).
- PDF extraction requires `pdfplumber` and `openpyxl`.
- Scanned/image-only PDFs usually require OCR first.
