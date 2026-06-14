# Modello privacy

Il progetto segue una regola semplice:

> Solo i file anonimizzati dovrebbero uscire dal flusso locale.

## Confini di fiducia

```text
Computer locale
  documenti originali
  rilevamento
  revisione
  mapping
  risultati ripristinati

Ambiente LLM
  solo testo anonimizzato
```

## Sicuro da caricare

File dentro:

```text
01_DA_CARICARE_NELL_LLM/
```

Questi file contengono placeholder come:

```text
[PERSONA_1]
[EMAIL_1]
[ORGANIZZAZIONE_1]
```

## Non caricare

File dentro:

```text
99_RISERVATO_NON_CARICARE/
```

Questa cartella puo contenere valori originali tramite mapping e file di audit.

## Limiti

- Il rilevamento PII puo generare falsi positivi e falsi negativi.
- La revisione umana resta necessaria prima della condivisione.
- L'OCR per documenti scansionati non e ancora implementato.
- Il progetto non fornisce certificazione legale di conformita.
- Gli output sono testuali; preservare layout PDF/DOCX/XLSX e lavoro futuro.

## Scelte progettuali

- Elaborazione local-first.
- Revisione umana esplicita.
- Nomi output conservativi.
- Cartelle sicure e riservate separate.
- Solo esempi sintetici nel repository pubblico.
