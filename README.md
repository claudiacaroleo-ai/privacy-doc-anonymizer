# Privacy Doc Anonymizer

[Italiano](README.it.md)

Local-first desktop app for anonymizing business documents before using them in LLM workflows.

This portfolio project was inspired by OpenAI's release of [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/), an open-weight model for detecting and redacting personally identifiable information (PII) in text. The project turns that idea into a practical document workflow: local detection, human review, safe output folders, and reserved mapping files.

> Not affiliated with OpenAI. This is an independent educational and portfolio project.

## Why it matters

LLMs are increasingly useful for document analysis, but business documents often contain names, emails, phone numbers, addresses, fiscal identifiers, suppliers, customers, and account-like data.

This app helps create a safer workflow:

1. Select local documents.
2. Detect possible PII locally.
3. Review each finding before saving.
4. Export only anonymized files to a clearly marked LLM-safe folder.
5. Keep mapping and audit files in a separate reserved folder.

## Key features

- Desktop GUI built with Python and Tkinter.
- Local PII detection using OpenAI Privacy Filter, with additional Italian-aware rules.
- Human review step before output generation.
- Supported input formats: PDF, DOCX, XLSX, TXT, CSV, TSV.
- Automatic detection of supplier/customer fields such as `Supplier`, `Fornitore`, `Client`, `Ragione sociale`.
- Safe output separation:
  - `01_DA_CARICARE_NELL_LLM`: anonymized files only.
  - `99_RISERVATO_NON_CARICARE`: mapping, audit index, and processing log.
- Consistent placeholders across files, for example `[PERSONA_1]`, `[EMAIL_1]`, `[ORGANIZZAZIONE_1]`.
- Mapping export for controlled local re-identification.
- Unit tests for redaction, Excel extraction, output separation, and supplier detection.

## Workflow

```text
Original documents
        |
        v
Local detection + Italian rules
        |
        v
Human review in the desktop GUI
        |
        +--> 01_DA_CARICARE_NELL_LLM
        |       anonymized .txt files
        |
        +--> 99_RISERVATO_NON_CARICARE
                mapping, audit index, processing log
```

## Quick start

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install -r requirements-opf.txt
py verifica_ambiente.py
py gui.py
```

On macOS/Linux:

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-opf.txt
python verifica_ambiente.py
python gui.py
```

## Demo data

The `examples/synthetic/` folder contains synthetic files only. Do not commit real documents, invoices, reports, spreadsheets, or generated mapping files.

## Tests

```bash
python -m unittest discover -s tests -v
```

The GitHub Actions workflow runs the unit tests on push and pull request.

## Privacy and safety notes

This project is designed as a privacy-by-design workflow aid, not as a legal guarantee of anonymization.

Important rules:

- Upload to an LLM only files from `01_DA_CARICARE_NELL_LLM`.
- Never upload `99_RISERVATO_NON_CARICARE`.
- Always review findings manually before sharing documents.
- Use synthetic files in the public repository.
- Do not treat model output as compliance certification.

OpenAI notes that Privacy Filter is one component in a broader privacy-by-design system and that human review remains important in sensitive settings. This app follows that framing by keeping a manual review step and separating safe files from reserved mapping files.

## Documentation

- [Architecture](docs/architecture.en.md)
- [Privacy model](docs/privacy-model.en.md)
- [Roadmap](docs/roadmap.en.md)
- [Italian documentation](README.it.md)

## Project status

Portfolio project / working prototype.

The goal is to demonstrate product thinking, privacy-aware AI workflows, Python desktop development, document processing, and testable engineering practices.

## License

MIT. See [LICENSE](LICENSE).
