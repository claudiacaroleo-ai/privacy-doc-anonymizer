# LinkedIn launch draft - English

I started from a simple question:

How can we use LLMs on business documents without casually exposing personal data?

After reading OpenAI's introduction of Privacy Filter, I built a small local-first desktop tool that turns the idea into a practical workflow:

- select PDF, Word, Excel, TXT or CSV files;
- detect possible personal data locally;
- review every finding before saving;
- export only anonymized files to a clearly marked LLM-safe folder;
- keep mapping and audit files in a separate reserved folder.

The project is intentionally practical: it is not a compliance guarantee, and it does not pretend that automation removes the need for human review. Instead, it focuses on the operational layer that teams often miss: making the safer path the easy path.

What I learned while building it:

- privacy features need UX, not just models;
- output folders and naming matter more than they seem;
- synthetic examples and tests are essential when working on privacy tooling;
- local-first workflows are still very relevant in the LLM era.

Repository:
https://github.com/claudiacaroleo-ai/privacy-doc-anonymizer

#AI #Privacy #Python #LLM #DocumentProcessing #PortfolioProject
