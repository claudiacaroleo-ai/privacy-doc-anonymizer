# GitHub publishing checklist

Recommended repository:

```text
claudiacaroleo-ai/privacy-doc-anonymizer
```

Recommended visibility:

```text
Public
```

Recommended description:

```text
Local-first desktop app for anonymizing business documents before LLM analysis.
```

Recommended topics:

```text
python
tkinter
privacy
pii
anonymization
redaction
llm
document-processing
gdpr
excel
pdf
docx
portfolio
```

## Before the first push

- Check that no real documents are present.
- Check that `.gitignore` excludes generated mappings and real files.
- Run tests.
- Add clean screenshots if available.

## Option A - create repository from the GitHub website

1. Go to `https://github.com/new`.
2. Owner: `claudiacaroleo-ai`.
3. Repository name: `privacy-doc-anonymizer`.
4. Visibility: `Public`.
5. Do not add README, license, or `.gitignore` from GitHub, because they already exist locally.
6. Create repository.
7. Run locally:

```bash
git init -b main
git add .
git commit -m "Initial portfolio release"
git remote add origin https://github.com/claudiacaroleo-ai/privacy-doc-anonymizer.git
git push -u origin main
```

## Option B - GitHub CLI

If `gh` is installed and authenticated:

```bash
git init -b main
git add .
git commit -m "Initial portfolio release"
gh repo create claudiacaroleo-ai/privacy-doc-anonymizer --public --source . --remote origin --push
```

## After publishing

- Enable secret scanning and Dependabot alerts if available.
- Add a social preview image.
- Pin the repository on your GitHub profile.
- Link it from LinkedIn and from `prompt-engineering-portfolio`.
- Add screenshots or a short GIF demo.
