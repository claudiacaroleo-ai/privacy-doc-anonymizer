# Architettura

Privacy Doc Anonymizer e volutamente piccolo e local-first.

## Componenti

```text
gui.py
  interfaccia desktop Tkinter
  flusso utente, tabella revisione, anteprime, salvataggio

core.py
  estrazione testo
  orchestrazione rilevamento PII
  regole specifiche italiane
  registro placeholder
  redazione
  separazione output

tests/
  test automatici sul comportamento del core
```

## Flusso di elaborazione

1. Raccoglie i file supportati dalla cartella scelta.
2. Estrae testo da PDF, DOCX, XLSX, TXT, CSV o TSV.
3. Usa OpenAI Privacy Filter in locale.
4. Aggiunge regole deterministiche per identificativi italiani e campi fornitore/cliente.
5. Unisce span sovrapposti per non corrompere l'output.
6. Assegna placeholder stabili per entita normalizzata.
7. Lascia l'utente revisionare ogni dato trovato.
8. Salva file anonimizzati e mapping riservati in cartelle separate.

## Perche desktop

L'app e pensata per persone che lavorano con documenti locali e non vogliono caricare file grezzi su un servizio web prima dell'anonimizzazione.

Tkinter riduce le dipendenze e permette di avviare l'app con una normale installazione Python.

## Modello di output

```text
cartella risultati scelta/
  01_DA_CARICARE_NELL_LLM/
    file .txt anonimizzati

  99_RISERVATO_NON_CARICARE/
    mapping_entities.csv
    mapping_entities.json
    index_occurrences.csv
    processing_log.txt
```

La separazione riduce il rischio che l'utente carichi per errore nell'LLM i dati di re-identificazione.
