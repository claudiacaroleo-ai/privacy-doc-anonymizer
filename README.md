# Privacy Doc Anonymizer

[Italian version](README.it.md)

Local-first desktop app for anonymizing business documents before using them in LLM workflows.

This portfolio project was inspired by OpenAI's release of [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/), an open-weight model for detecting and redacting personally identifiable information (PII) in text. The project turns that technical direction into a practical workflow: local detection, human review, safe files for LLM use, and reserved mapping files kept separate.

> Not affiliated with OpenAI. This is an independent educational and portfolio project.

## Demo

The demo below uses synthetic data only.

![Privacy Doc Anonymizer review screen](docs/assets/review.png)

<details>
<summary>More screenshots</summary>

![Privacy Doc Anonymizer start screen](docs/assets/home.png)

![Privacy Doc Anonymizer final report](docs/assets/final-report.png)

</details>

## What It Solves

LLMs are useful for summarizing, classifying, and analyzing documents, but business files often contain names, emails, phone numbers, addresses, fiscal identifiers, suppliers, customers, and other sensitive references.

Privacy Doc Anonymizer helps users work with documents more safely:

1. Select local documents.
2. Detect possible PII locally.
3. Review findings in a simple desktop interface.
4. Save only anonymized text files in an LLM-safe folder.
5. Keep mappings and audit files in a reserved folder that should not be uploaded.

## Key Features

- English-first desktop GUI built with Python and Tkinter.
- Italian-aware detection rules for fiscal identifiers, VAT numbers, IBANs, addresses, and supplier/customer fields.
- OpenAI Privacy Filter integration for model-based PII detection.
- Human review step before saving anonymized copies.
- Supported input formats: PDF, DOCX, XLSX, TXT, CSV, TSV.
- Clear output separation:
  - `01_LLM_SAFE_FILES`: anonymized files only.
  - `99_RESERVED_DO_NOT_UPLOAD`: mapping, audit index, and processing log.
- Consistent placeholders across files, for example `[PERSON_1]`, `[EMAIL_1]`, `[ORGANIZATION_1]`.
- Mapping export for controlled local re-identification after LLM analysis.
- Unit tests for redaction, Excel extraction, output separation, and supplier detection.
- Bilingual documentation: English as the main project language, Italian for local users and context.

## Workflow

```text
Original documents
        |
        v
Local detection + Italian-aware rules
        |
        v
Human review in the desktop GUI
        |
        +--> 01_LLM_SAFE_FILES
        |       anonymized .txt files
        |
        +--> 99_RESERVED_DO_NOT_UPLOAD
                mapping, audit index, processing log
```

## Quick Start

Windows:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install -r requirements-opf.txt
py check_environment.py
py gui.py
```

macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-opf.txt
python check_environment.py
python gui.py
```

If OpenAI Privacy Filter is not installed, the app will clearly explain what dependency is missing.

## Demo Data

The `examples/synthetic/` folder contains synthetic files only. Do not commit real documents, invoices, reports, spreadsheets, generated outputs, mapping files, or screenshots containing personal data.

## Tests

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs the unit tests on push and pull request.

## Privacy And Safety Notes

This project is designed as a privacy-by-design workflow aid, not as a legal guarantee of anonymization.

Important rules:

- Upload to an LLM only files from `01_LLM_SAFE_FILES`.
- Never upload `99_RESERVED_DO_NOT_UPLOAD`.
- Always review findings manually before sharing documents.
- Use synthetic files in the public repository.
- Do not treat model output as compliance certification.

OpenAI describes Privacy Filter as one component in a broader privacy-by-design system. This app follows that framing by keeping a manual review step and separating LLM-safe files from reserved re-identification files.

## Documentation

- [Architecture](docs/architecture.en.md)
- [Privacy model](docs/privacy-model.en.md)
- [Roadmap](docs/roadmap.en.md)
- [Italian documentation](README.it.md)

## Portfolio Focus

This project demonstrates product thinking, privacy-aware AI workflows, local document processing, Python desktop development, user-centered interface design, and testable engineering practices.

## License

MIT. See [LICENSE](LICENSE).
