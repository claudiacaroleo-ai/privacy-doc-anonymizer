# Privacy Doc Anonymizer

[English](README.md)

Applicazione desktop locale per anonimizzare documenti aziendali prima di usarli in workflow con LLM.

Questo progetto portfolio nasce come applicazione pratica ispirata al rilascio di [OpenAI Privacy Filter](https://openai.com/index/introducing-openai-privacy-filter/), modello open-weight per rilevare e oscurare dati personali nel testo. L'idea qui e trasformare quella direzione tecnica in un flusso operativo semplice: rilevamento locale, revisione umana, cartella sicura per l'LLM e mapping separato.

> Progetto indipendente, non affiliato a OpenAI.

## Perche e utile

I modelli linguistici sono utili per analizzare documenti, ma molti file aziendali contengono nomi, email, telefoni, indirizzi, codici fiscali, P.IVA, fornitori e clienti.

Questa app aiuta a creare un flusso piu sicuro:

1. scegli documenti locali;
2. rilevi possibili dati personali in locale;
3. controlli i risultati prima di salvare;
4. esporti solo file anonimizzati in una cartella chiaramente sicura;
5. tieni mapping e log in una cartella riservata.

## Funzionalita principali

- Interfaccia desktop in Python e Tkinter.
- Rilevamento PII con OpenAI Privacy Filter e regole aggiuntive per casi italiani.
- Revisione manuale prima del salvataggio.
- Formati supportati: PDF, DOCX, XLSX, TXT, CSV, TSV.
- Riconoscimento automatico di campi come `Fornitore`, `Cliente`, `Ragione sociale`, `Azienda`.
- Output separato:
  - `01_DA_CARICARE_NELL_LLM`: solo file anonimizzati.
  - `99_RISERVATO_NON_CARICARE`: mapping, indice audit e log.
- Placeholder coerenti tra file, per esempio `[PERSONA_1]`, `[EMAIL_1]`, `[ORGANIZZAZIONE_1]`.
- Mapping locale per eventuale ripristino controllato.
- Test automatici su redazione, Excel, output separato e rilevamento fornitori.

## Flusso

```text
Documenti originali
        |
        v
Rilevamento locale + regole italiane
        |
        v
Revisione umana nella GUI
        |
        +--> 01_DA_CARICARE_NELL_LLM
        |       file .txt anonimizzati
        |
        +--> 99_RISERVATO_NON_CARICARE
                mapping, indice audit, log
```

## Avvio rapido

```powershell
py -m venv .venv
.\.venv\Scripts\activate
py -m pip install --upgrade pip
py -m pip install -r requirements.txt
py -m pip install -r requirements-opf.txt
py verifica_ambiente.py
py gui.py
```

## Dati demo

La cartella `examples/synthetic/` contiene solo dati sintetici. Non caricare nel repository documenti veri, fatture vere, output reali o file di mapping.

## Test

```powershell
py -m unittest discover -s tests -v
```

## Note privacy

Questo progetto aiuta un workflow privacy-by-design, ma non e una garanzia legale di anonimizzazione.

Regole importanti:

- carica nell'LLM solo i file dentro `01_DA_CARICARE_NELL_LLM`;
- non caricare mai `99_RISERVATO_NON_CARICARE`;
- controlla sempre i risultati prima di condividere documenti;
- usa solo dati sintetici nel repository pubblico;
- non trattare il risultato come certificazione di conformita.

OpenAI descrive Privacy Filter come un componente di un sistema privacy-by-design piu ampio, non come sostituto della revisione umana in contesti sensibili. Questa app mantiene infatti una revisione manuale e separa i file sicuri dal mapping riservato.

## Documentazione

- [Architettura](docs/architecture.it.md)
- [Modello privacy](docs/privacy-model.it.md)
- [Roadmap](docs/roadmap.it.md)
- [Bozza post LinkedIn](docs/linkedin-post.it.md)

## Stato progetto

Progetto portfolio / prototipo funzionante.

L'obiettivo e mostrare product thinking, workflow AI attenti alla privacy, sviluppo desktop Python, processing documentale e pratiche ingegneristiche testabili.

## Licenza

MIT. Vedi [LICENSE](LICENSE).
