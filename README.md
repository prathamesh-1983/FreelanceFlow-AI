# FreelanceFlow AI

**A local-first invoice and receipt management assistant powered by open-weight AI.**

FreelanceFlow AI helps freelancers and small businesses organize receipts and invoices, extract useful fields, review expense records, visualize spending, and export reports. It is built with Python, Streamlit, SQLite, and an optional locally running Ollama model.

> **Project status:** Starter MVP. AI extraction and document parsing require local setup and should be reviewed before relying on results.

## Key features

- Upload PDF, TXT, PNG, JPG, and JPEG documents.
- Extract text from text-based PDFs and TXT files.
- Optional OCR for receipt images when Tesseract OCR is installed.
- Optional local AI extraction using Ollama and a compatible local model.
- Review and correct extracted fields before saving.
- Add, search, edit, and delete expense records.
- Store records in a local SQLite database.
- View expense totals, category breakdowns, and monthly spending.
- Export expense records and monthly summaries as CSV.
- Enter expenses manually when AI is unavailable.

## Tech stack

| Technology | Purpose |
|---|---|
| Python | Application logic |
| Streamlit | Local web interface |
| SQLite | Local expense database |
| Ollama | Local model runtime |
| Qwen2.5 3B (default example) | Invoice-field extraction |
| PyMuPDF | Text extraction from digital PDFs |
| Tesseract OCR + pytesseract | OCR for images |
| Pandas | Data processing and summaries |
| Plotly | Dashboard charts |
| Pytest | Automated tests |

Check the selected model's license and usage terms before redistribution or commercial use. Open weights do not automatically mean an OSI-approved open-source license.

## How it works

1. Upload a receipt or invoice.
2. Extract text from the document.
3. Optionally ask a locally running Ollama model to identify fields such as vendor, invoice number, date, amount, currency, and category.
4. Review and correct the extracted values.
5. Save the approved record to SQLite.
6. Explore expenses in the dashboard and export reports as CSV.

```text
Receipt / Invoice
       |
       v
Text Extraction (PDF parser / OCR)
       |
       v
Optional Local AI (Ollama)
       |
       v
Review and Validate Fields
       |
       v
SQLite Database
       |
       +----> Dashboard and Charts
       |
       +----> CSV Reports
```

## Project structure

```text
freelanceflow-ai/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── .env.example
├── src/
│   ├── __init__.py
│   ├── ai_extractor.py
│   ├── document_parser.py
│   ├── database.py
│   ├── validators.py
│   ├── reports.py
│   └── analytics.py
├── assets/
│   └── logo.png
├── data/
│   └── .gitkeep
├── samples/
│   └── sample_receipt.txt
└── tests/
    ├── test_validators.py
    └── test_database.py
```

The app creates its SQLite database and upload folder locally. Do not commit uploaded documents, database files, or sensitive financial data to a public repository.

## Requirements

- Windows, macOS, or Linux
- Python 3.10 or newer
- pip
- Ollama for local AI extraction (optional)
- Tesseract OCR for image OCR (optional)
- Internet access for initial package and model downloads; local inference can work offline after setup

## Installation on Windows

### 1. Install prerequisites

Install [Python](https://www.python.org/downloads/), [Visual Studio Code](https://code.visualstudio.com/), [Ollama](https://ollama.com/) (optional), and [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki) (optional). During Python installation, enable **Add Python to PATH**.

### 2. Open the project

Extract the project ZIP, open the `freelanceflow-ai` folder in VS Code, then select **Terminal → New Terminal**.

### 3. Create a virtual environment

In PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### 4. Install dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Set up Ollama (optional)

Make sure Ollama is running, then download the example model:

```powershell
ollama pull qwen2.5:3b
```

The default configuration uses model `qwen2.5:3b` and Ollama endpoint `http://localhost:11434`. You can change the `OLLAMA_MODEL` and `OLLAMA_URL` environment variables before starting the app, or edit the defaults in `src/ai_extractor.py`.

Example PowerShell settings:

```powershell
$env:OLLAMA_MODEL = "qwen2.5:3b"
$env:OLLAMA_URL = "http://localhost:11434"
```

Without Ollama, you can still enter expenses manually and use the database, dashboard, and reports.

## Run the application

From the project root, with the virtual environment activated:

```powershell
streamlit run app.py
```

Open the local address printed by Streamlit, usually `http://localhost:8501`.

## Test with sample data

1. Open **Upload & Extract**.
2. Upload `samples/sample_receipt.txt`.
3. Enable local AI if Ollama is running.
4. Review the extracted fields carefully.
5. Save the record.
6. Open **Dashboard** to view the summary.
7. Open **Reports** to download CSV files.

The sample receipt contains synthetic data for testing.

## Run tests

```powershell
pytest -q
```

The tests cover basic field validation and database create/read/update/delete operations.

## Privacy and security

- Expense records are stored in a local SQLite database.
- Uploaded documents are stored in the app's local `data/uploads/` folder.
- When local AI is enabled, this app sends the prompt to the configured Ollama runtime rather than a cloud AI API.
- The SQLite database and uploaded files are **not encrypted at rest**.
- Initial package/model downloads require internet access. Local inference can work offline after setup if the required components are installed locally.

**Do not use this starter MVP for sensitive production financial records without reviewing and improving its security.** Protect your computer, avoid shared machines, and never commit real invoices, receipts, database files, or credentials to a public repository.

## Limitations

- AI can misread totals, dates, vendors, or currencies. Verify every extracted field.
- OCR quality depends on image quality and a working Tesseract installation.
- Text-based PDFs are supported; scanned/image-only PDFs need an OCR enhancement.
- The MVP does not include user accounts, access controls, database encryption, or a complete audit history.
- Amounts in different currencies are not converted into a common currency. Do not treat them as directly comparable.
- This is an organizer and reporting tool, not accounting, tax, legal, or investment advice.

## Future improvements

- Add OCR for scanned PDF pages.
- Add duplicate-document detection.
- Add extraction confidence indicators and better error reporting.
- Support currency-aware reports.
- Add stronger data protection and access controls.
- Add customizable expense categories and more export formats.
- Collect feedback from freelancers and small-business users.

## Contributing

Contributions and suggestions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Make a focused change and add tests where appropriate.
4. Run `pytest -q`.
5. Open a pull request describing the change.

Do not include real customer documents or personal financial information in issues, tests, or pull requests.

## License

Choose and add a license before publishing the repository. For example, you may license your original project code under the MIT License after checking compatibility with dependencies, assets, and the selected model's license. The model license may differ from the license used for this repository's code.
