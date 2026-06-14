# Privacy Model

This project is built around one rule:

> Only anonymized files should leave the local workflow.

## Trust boundaries

```text
Local machine
  raw documents
  detection
  review
  mapping
  restored results

LLM workspace
  anonymized text only
```

## Safe to upload

Files inside:

```text
01_DA_CARICARE_NELL_LLM/
```

These files contain placeholders such as:

```text
[PERSONA_1]
[EMAIL_1]
[ORGANIZZAZIONE_1]
```

## Do not upload

Files inside:

```text
99_RISERVATO_NON_CARICARE/
```

This folder may contain original values through mapping and audit files.

## Limitations

- PII detection can produce false positives and false negatives.
- Human review is required before sharing outputs.
- OCR for scanned documents is not implemented yet.
- The project does not provide legal compliance certification.
- Output files are text-based; preserving original PDF/DOCX/XLSX layout is future work.

## Design choices

- Local-first processing.
- Explicit human review.
- Conservative output naming.
- Separate safe and reserved folders.
- Synthetic examples only in the public repository.
