# Changelog

## 0.1.0 - Portfolio release

- Added local document anonymization workflow.
- Added Tkinter GUI for non-technical users.
- Added support for PDF, DOCX, XLSX, TXT, CSV, and TSV input.
- Added Italian-aware deterministic rules for fiscal identifiers, IBAN, phone numbers, and supplier/customer fields.
- Added human review before saving.
- Added output separation:
  - `01_DA_CARICARE_NELL_LLM`
  - `99_RISERVATO_NON_CARICARE`
- Added mapping and audit exports.
- Added unit tests and GitHub Actions workflow.
- Added bilingual documentation.
