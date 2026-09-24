# TableBridge

**Fixed-layout PDF tables to a reviewable Excel workbook.**

TableBridge is a small local Python application with a browser interface. It extracts one ruled table per page, checks the expected column headers, and exports an `.xlsx` workbook with typed data, original extracted text, and review notes.

[中文说明](README.zh-CN.md) · [Template guide](docs/TEMPLATES.md) · [Test report](docs/TEST-REPORT.md)

## What it does

- Combine multiple same-layout PDFs into one Excel file.
- Keep identifiers such as `001` as text; convert explicitly designated numeric columns.
- Record source filename, page number and table row for each record.
- Flag quantity × unit-price discrepancies without changing source amounts.
- Stop the entire batch when any file fails the layout checks, rather than silently dropping its pages.
- Preserve text that looks like an Excel formula as literal text.
- Run on your computer without API keys, a cloud account, or an AI inference service.

## Scope

This release supports **selectable-text PDFs, visible table borders, one table per selected page area, one header row repeated on every page, no merged cells**. It is not a general PDF converter. Scanned images, handwriting, borderless tables, mixed page layouts and password-protected files are outside its scope. Empty or missing pages/tables fail conversion; there is no automatic page skipping.

The included template fits the synthetic quotation samples in `examples/`. A different document layout needs its own template and manual validation. A passed layout check is not a guarantee of extraction accuracy.

## Quick start

Requires Python **3.11+** (Python 3.11 or 3.12 recommended).

### Windows

1. Install Python from [python.org](https://www.python.org/downloads/), including the Python launcher.
2. Download this repository using **Code → Download ZIP** and extract it.
3. Double-click `start-windows.bat`. The first run creates `.venv` and installs the dependencies; internet access is needed for that installation.
4. Keep the terminal open. The app opens at `http://127.0.0.1:8765`.
5. Click **使用示例报价单**, then **转换并预览**, then **下载 Excel**.

If the launcher fails, use the manual commands below. The Windows launcher has not been executed on Windows in this development environment.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python app.py
```

### Windows manual commands

```powershell
py -3 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe app.py
```

Open the address printed in the terminal if the browser does not open. To use another port: `python app.py --port 8766`. Press Ctrl+C to stop.

## Try the three examples

| File | Expected result |
| --- | --- |
| `demo-quotation.pdf` | Two pages, eight data rows, no arithmetic warnings |
| `demo-amount-warning.pdf` | Two rows, one arithmetic warning; source amount remains 160.00 |
| `demo-wrong-layout.pdf` | Rejected because the headers differ from the template |

All example company names, products and prices are fictional. They are test fixtures, not paid client work or evidence of commercial use.

## Excel output

| Sheet | Contents |
| --- | --- |
| Data | Whitespace-normalized text and explicitly typed numeric columns, with source references |
| Raw text | Extracted text before whitespace/numeric normalization, with source references |
| Review | Per-file page/row counts, scope notes and any arithmetic warnings |

Raw text means the PDF library's extracted text, not a pixel-perfect reconstruction of the PDF. The workbook contains no macros or generated formulas. Numeric parsing accepts `1234.56` and `1,234.56`; currency signs, decimal commas and numbers exceeding the supported precision must be handled through an adapted template or manual processing.

## Privacy and limits

PDFs are sent only to the local Python process. The application does not call external APIs, store uploaded files on disk, or log their contents. The downloaded Excel contains source filenames and data; review it before sharing. Dependency installation requires network access. Browser and operating-system behavior is outside this application's control.

The built-in server binds to `127.0.0.1`. **Do not expose it to the internet or treat it as a production service.** Limits: 10 files, 10 MB per file, 20 MB per batch, 50 pages and 10,000 data rows per file. Preview displays the first 100 combined rows; Excel includes all accepted rows. There is no authentication, OCR, cloud deployment, conversion timeout or hostile-file sandbox.

GitHub hosts the source code; GitHub Pages cannot run this Python backend.

## Development

```bash
python -m pip install -r requirements-dev.txt
python scripts/create_samples.py
python -m unittest discover -s tests -v
```

GitHub Actions is configured for Python 3.11 and 3.12; workflow status should be checked on GitHub after the first push. Do not assume a configured workflow has already run. The core converter and HTTP download flow were tested locally; interactive browser and Windows checks remain to be completed on a suitable machine.

## Implementation and AI assistance

This project was developed with substantial AI assistance for code, documentation and test design. It uses [pdfplumber](https://github.com/jsvine/pdfplumber) for extraction and [openpyxl](https://openpyxl.readthedocs.io/) for XLSX export. Its interface is static HTML/CSS/JavaScript served locally by Python. AI is not used during conversion. See the test report for verified behavior and remaining limitations.

## License

MIT for this project's code. Third-party packages retain their own licenses. See [LICENSE](LICENSE).
