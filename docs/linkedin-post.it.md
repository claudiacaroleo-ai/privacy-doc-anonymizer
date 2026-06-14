# Bozza post LinkedIn - Italiano

Sono partita da una domanda semplice:

Come possiamo usare gli LLM su documenti aziendali senza esporre con leggerezza dati personali?

Dopo aver letto il rilascio di OpenAI Privacy Filter, ho costruito un piccolo strumento desktop local-first che trasforma quell'idea in un flusso pratico:

- selezioni file PDF, Word, Excel, TXT o CSV;
- rilevi possibili dati personali in locale;
- controlli ogni risultato prima del salvataggio;
- esporti solo i file anonimizzati in una cartella sicura per l'LLM;
- tieni mapping e log in una cartella riservata e separata.

Il progetto non vuole essere una garanzia legale di anonimizzazione. Il punto e diverso: rendere piu semplice un workflow prudente, dove l'automazione aiuta ma la revisione umana resta centrale.

Cosa mi ha insegnato:

- la privacy ha bisogno di UX, non solo di modelli;
- nomi delle cartelle e separazione degli output contano moltissimo;
- esempi sintetici e test sono fondamentali quando si lavora su strumenti privacy;
- i workflow local-first sono ancora molto importanti nell'era degli LLM.

Repository:
https://github.com/claudiacaroleo-ai/privacy-doc-anonymizer

#AI #Privacy #Python #LLM #DocumentProcessing #Portfolio
