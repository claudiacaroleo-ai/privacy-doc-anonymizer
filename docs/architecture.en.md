# Architecture

Privacy Doc Anonymizer is intentionally small and local-first.

## Components

```text
gui.py
  Tkinter desktop interface
  user flow, review table, previews, save actions

core.py
  file extraction
  PII detection orchestration
  Italian-specific rules
  placeholder registry
  redaction
  output separation

tests/
  unit tests for core behavior
```

## Processing flow

1. Collect supported files from the selected input folder.
2. Extract text from PDF, DOCX, XLSX, TXT, CSV, or TSV.
3. Run OpenAI Privacy Filter locally.
4. Add deterministic rules for Italian identifiers and supplier/customer fields.
5. Merge overlapping spans to avoid corrupting output.
6. Assign stable placeholders by normalized entity.
7. Let the user review each finding.
8. Save anonymized files separately from reserved mapping files.

## Why a desktop app

The app is designed for users who handle documents locally and may not want to upload raw files to a web service before anonymization.

Tkinter keeps the dependency footprint small and makes the application easy to run on standard Python installations.

## Output model

```text
selected output folder/
  01_LLM_SAFE_FILES/
    anonymized .txt files

  99_RESERVED_DO_NOT_UPLOAD/
    mapping_entities.csv
    mapping_entities.json
    index_occurrences.csv
    processing_log.txt
```

The split is deliberate: it reduces the chance that a user accidentally uploads re-identification data to an LLM.
