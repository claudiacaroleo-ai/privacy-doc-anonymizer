# Contributing

Thanks for your interest in improving Privacy Doc Anonymizer.

## Ground rules

- Use synthetic data only.
- Do not add real invoices, contracts, spreadsheets, emails, or personal information.
- Do not commit generated mapping files or reserved output folders.
- Keep the interface understandable for non-technical users.
- Add or update tests when changing core redaction logic.

## Development setup

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -r requirements-opf.txt
python -m unittest discover -s tests -v
```

On Windows PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install -r requirements-opf.txt
py -m unittest discover -s tests -v
```

## Pull request checklist

- The change uses synthetic data only.
- `python -m unittest discover -s tests -v` passes.
- Documentation is updated when user-facing behavior changes.
- Privacy-sensitive outputs remain excluded from git.
