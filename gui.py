"""
Interfaccia semplice per l'anonimizzatore documenti.

La GUI evita termini tecnici: le label interne restano nel core, ma l'utente
vede categorie comprensibili e scelte guidate.
"""
from __future__ import annotations

import json
import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from typing import Optional

import core


APP_TITLE = "Anonimizzatore Documenti"
PAD = 8
FILTER_ALL = "Tutti i dati"

DATA_TYPES = [
    ("private_person", "Nomi di persone", "Mario Rossi, dott.ssa Bianchi"),
    ("private_email", "Email", "nome@azienda.it"),
    ("private_phone", "Telefoni", "+39 333 1234567"),
    ("private_address", "Indirizzi", "Via Roma 12"),
    ("private_organization", "Aziende ed enti", "fornitori, clienti, societa"),
    ("private_id", "Codici personali", "Codice fiscale, P.IVA, IBAN"),
    ("private_date", "Date", "date di nascita o eventi"),
    ("private_location", "Luoghi", "citta, sedi, localita"),
]

LABEL_NAME = {label: name for label, name, _ in DATA_TYPES}
NAME_TO_LABEL = {name: label for label, name, _ in DATA_TYPES}

DETECTION_MODES = {
    "recommended": {
        "title": "Consigliato",
        "description": "Buon equilibrio: controlli finali facili e pochi dati saltati.",
        "min_score": 0.20,
    },
    "complete": {
        "title": "Trova piu dati",
        "description": "Mostra anche risultati incerti: utile se il documento e delicato.",
        "min_score": 0.00,
    },
    "selective": {
        "title": "Meno falsi allarmi",
        "description": "Mostra solo risultati piu sicuri: rischia di perdere qualcosa.",
        "min_score": 0.60,
    },
}

SOURCE_NAME = {
    "opf": "automatico",
    "regex": "regola",
    "context": "campo",
    "manual": "manuale",
    "merged": "unito",
}


def display_label(label: str) -> str:
    return LABEL_NAME.get(label, label)


def label_from_display(name: str) -> str:
    return NAME_TO_LABEL.get(name, name)


def score_label(score: Optional[float]) -> str:
    if score is None:
        return "-"
    if score >= 0.80:
        return "Alta"
    if score >= 0.50:
        return "Media"
    return "Bassa"


class App(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title(APP_TITLE)
        self.minsize(1000, 680)
        self.resizable(True, True)

        style = ttk.Style(self)
        style.theme_use("clam")
        self._configure_styles(style)

        self._spans: list[core.Span] = []
        self._files: list[str] = []
        self._unsupported_files: list[str] = []
        self._text_cache: dict[str, str] = {}
        self._preview_file: str = ""
        self._sort_col: Optional[str] = None
        self._sort_reverse = False

        self._build_notebook()
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    # ------------------------------------------------------------------
    # Stili
    # ------------------------------------------------------------------

    def _configure_styles(self, style: ttk.Style) -> None:
        bg = "#f5f5f5"
        accent = "#2563eb"
        self.configure(bg=bg)
        style.configure("TNotebook", background=bg)
        style.configure("TNotebook.Tab", padding=(14, 7), font=("Segoe UI", 10))
        style.configure("TFrame", background=bg)
        style.configure("TLabel", background=bg, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=bg, foreground="#475569", font=("Segoe UI", 9))
        style.configure("Title.TLabel", background=bg, font=("Segoe UI", 13, "bold"))
        style.configure("TButton", font=("Segoe UI", 10), padding=(10, 5))
        style.configure(
            "Accent.TButton",
            foreground="white",
            background=accent,
            font=("Segoe UI", 10, "bold"),
            padding=(12, 6),
        )
        style.map("Accent.TButton", background=[("active", "#1d4ed8"), ("disabled", "#93c5fd")])
        style.configure("TCheckbutton", background=bg, font=("Segoe UI", 10))
        style.configure("TRadiobutton", background=bg, font=("Segoe UI", 10))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=24)
        style.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"))

    # ------------------------------------------------------------------
    # Struttura
    # ------------------------------------------------------------------

    def _build_notebook(self) -> None:
        self.notebook = ttk.Notebook(self)
        self.notebook.grid(row=0, column=0, sticky="nsew", padx=PAD, pady=PAD)

        self.tab_config = ttk.Frame(self.notebook)
        self.tab_review = ttk.Frame(self.notebook)
        self.tab_report = ttk.Frame(self.notebook)

        self.notebook.add(self.tab_config, text="  1. Scegli documenti  ")
        self.notebook.add(self.tab_review, text="  2. Controlla risultati  ", state="disabled")
        self.notebook.add(self.tab_report, text="  3. Salvataggio  ", state="disabled")

        self._build_tab_config()
        self._build_tab_review()
        self._build_tab_report()

    # ------------------------------------------------------------------
    # Tab 1
    # ------------------------------------------------------------------

    def _build_tab_config(self) -> None:
        f = self.tab_config
        f.columnconfigure(0, weight=1)
        f.rowconfigure(2, weight=1)

        ttk.Label(f, text="Anonimizza documenti in pochi passaggi", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=PAD, pady=(PAD * 2, 2))
        ttk.Label(
            f,
            text="Scegli una cartella, controlla cosa e stato trovato, poi salva le copie anonime. Gli originali non vengono modificati.",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", padx=PAD, pady=(0, PAD))

        main = ttk.Frame(f)
        main.grid(row=2, column=0, sticky="nsew", padx=PAD)
        main.columnconfigure(0, weight=1)
        main.columnconfigure(1, weight=1)
        main.rowconfigure(0, weight=1)

        left = ttk.Frame(main)
        right = ttk.Frame(main)
        left.grid(row=0, column=0, sticky="nsew", padx=(0, PAD))
        right.grid(row=0, column=1, sticky="nsew", padx=(PAD, 0))
        left.columnconfigure(1, weight=1)
        left.rowconfigure(7, weight=1)
        right.columnconfigure(0, weight=1)

        ttk.Label(left, text="1. Documenti", style="Title.TLabel").grid(row=0, column=0, columnspan=3, sticky="w")

        ttk.Label(left, text="Cartella da controllare").grid(row=1, column=0, sticky="w", pady=(PAD, 2))
        self.var_input = tk.StringVar()
        ttk.Entry(left, textvariable=self.var_input).grid(row=1, column=1, sticky="ew", padx=(4, 4), pady=(PAD, 2))
        ttk.Button(left, text="Scegli", command=self._pick_input).grid(row=1, column=2, pady=(PAD, 2))

        ttk.Label(left, text="Cartella risultati").grid(row=2, column=0, sticky="w", pady=2)
        self.var_output = tk.StringVar()
        ttk.Entry(left, textvariable=self.var_output).grid(row=2, column=1, sticky="ew", padx=(4, 4), pady=2)
        ttk.Button(left, text="Scegli", command=self._pick_output).grid(row=2, column=2, pady=2)

        ttk.Label(left, text="Documenti trovati", font=("Segoe UI", 10, "bold")).grid(
            row=5, column=0, columnspan=3, sticky="w", pady=(PAD * 2, 0))
        ttk.Label(left, text="Formati: PDF, Word, Excel (.xlsx), TXT, CSV, TSV", style="Muted.TLabel").grid(
            row=6, column=0, columnspan=3, sticky="w")
        self.listbox_files = tk.Listbox(left, height=8, font=("Segoe UI", 9), selectmode="browse", activestyle="none")
        self.listbox_files.grid(row=7, column=0, columnspan=3, sticky="nsew", pady=(2, 0))

        self.label_file_status = ttk.Label(left, text="", style="Muted.TLabel", wraplength=440)
        self.label_file_status.grid(row=8, column=0, columnspan=3, sticky="w", pady=(4, 0))

        profile_bar = ttk.Frame(left)
        profile_bar.grid(row=9, column=0, columnspan=3, sticky="w", pady=(PAD, 0))
        ttk.Button(profile_bar, text="Carica impostazioni", command=self._load_profile).pack(side="left")
        ttk.Button(profile_bar, text="Salva impostazioni", command=self._save_profile).pack(side="left", padx=(4, 0))

        ttk.Label(right, text="2. Dati da nascondere", style="Title.TLabel").grid(row=0, column=0, sticky="w")
        ttk.Label(
            right,
            text="La scelta consigliata e gia pronta. Potrai cambiare ogni risultato prima del salvataggio.",
            style="Muted.TLabel",
            wraplength=450,
        ).grid(row=1, column=0, sticky="w", pady=(0, PAD // 2))

        self._label_vars: dict[str, tk.BooleanVar] = {}
        data_frame = ttk.Frame(right)
        data_frame.grid(row=2, column=0, sticky="ew")
        data_frame.columnconfigure(0, weight=1)
        data_frame.columnconfigure(1, weight=1)
        for idx, (label, name, example) in enumerate(DATA_TYPES):
            row = idx // 2
            col = idx % 2
            var = tk.BooleanVar(value=(label in core.DEFAULT_LABELS))
            self._label_vars[label] = var
            cell = ttk.Frame(data_frame)
            cell.grid(row=row, column=col, sticky="ew", padx=(0, PAD), pady=2)
            ttk.Checkbutton(cell, text=name, variable=var).pack(anchor="w")
            ttk.Label(cell, text=example, style="Muted.TLabel").pack(anchor="w", padx=(22, 0))

        btn_bar = ttk.Frame(right)
        btn_bar.grid(row=3, column=0, sticky="w", pady=(PAD // 2, PAD))
        ttk.Button(btn_bar, text="Scelta consigliata", command=self._select_recommended_labels).pack(side="left")
        ttk.Button(btn_bar, text="Seleziona tutto", command=self._select_all_labels).pack(side="left", padx=(4, 0))

        ttk.Separator(right, orient="horizontal").grid(row=4, column=0, sticky="ew", pady=PAD)

        ttk.Label(right, text="3. Tipo di controllo", style="Title.TLabel").grid(row=5, column=0, sticky="w")
        ttk.Label(right, text="Lascia 'Consigliato' se non sei sicuro.", style="Muted.TLabel").grid(
            row=6, column=0, sticky="w")
        self.var_detection_mode = tk.StringVar(value="recommended")
        mode_frame = ttk.Frame(right)
        mode_frame.grid(row=7, column=0, sticky="ew", pady=(2, PAD))
        for key in ("recommended", "complete", "selective"):
            ttk.Radiobutton(
                mode_frame,
                text=DETECTION_MODES[key]["title"],
                value=key,
                variable=self.var_detection_mode,
            ).pack(side="left", padx=(0, PAD))

        ttk.Label(right, text="Parole da lasciare visibili", font=("Segoe UI", 10, "bold")).grid(
            row=8, column=0, sticky="w")
        ttk.Label(
            right,
            text="Opzionale: esempi come Cuneo, Comune di Alba. Separale con una virgola.",
            style="Muted.TLabel",
        ).grid(row=9, column=0, sticky="w")
        self.var_exceptions = tk.StringVar()
        ttk.Entry(right, textvariable=self.var_exceptions).grid(row=10, column=0, sticky="ew", pady=(2, 0))

        footer = ttk.Frame(f)
        footer.grid(row=3, column=0, sticky="ew", padx=PAD, pady=(PAD, PAD))
        footer.columnconfigure(0, weight=1)
        self.progress_var = tk.DoubleVar()
        self.progressbar = ttk.Progressbar(footer, variable=self.progress_var, maximum=100)
        self.progressbar.grid(row=0, column=0, sticky="ew", padx=(0, PAD))
        self.btn_analyze = ttk.Button(
            footer,
            text="Controlla documenti",
            style="Accent.TButton",
            command=self._start_analysis,
        )
        self.btn_analyze.grid(row=0, column=1, sticky="e")
        self.label_status = ttk.Label(footer, text="")
        self.label_status.grid(row=1, column=0, columnspan=2, sticky="w", pady=(4, 0))

        self.var_include_kept_index = tk.BooleanVar(value=False)

    def _select_recommended_labels(self) -> None:
        for label, var in self._label_vars.items():
            var.set(label in core.DEFAULT_LABELS)

    def _select_all_labels(self) -> None:
        for var in self._label_vars.values():
            var.set(True)

    def _pick_input(self) -> None:
        folder = filedialog.askdirectory(title="Scegli la cartella con i documenti")
        if folder:
            self.var_input.set(folder)
            self._refresh_file_list(folder)

    def _pick_output(self) -> None:
        folder = filedialog.askdirectory(title="Scegli dove salvare le copie anonime")
        if folder:
            self.var_output.set(folder)

    def _refresh_file_list(self, folder: str) -> None:
        self.listbox_files.delete(0, "end")
        try:
            files = core.collect_files(folder)
            unsupported = core.collect_unsupported_files(folder)
        except OSError as exc:
            self.listbox_files.insert("end", f"Errore lettura cartella: {exc}")
            self.label_file_status.config(text="")
            return

        self._unsupported_files = unsupported

        if not files:
            self.listbox_files.insert("end", "Nessun documento che posso controllare.")
        else:
            self.listbox_files.insert("end", "Verranno controllati:")
            self.listbox_files.itemconfig("end", foreground="#166534")
            for path in files:
                self.listbox_files.insert("end", f"  {os.path.basename(path)}")

        if unsupported:
            if files:
                self.listbox_files.insert("end", "")
            self.listbox_files.insert("end", "Non supportati, verranno ignorati:")
            self.listbox_files.itemconfig("end", foreground="#b45309")
            for path in unsupported[:12]:
                self.listbox_files.insert("end", f"  {os.path.basename(path)}")
            if len(unsupported) > 12:
                self.listbox_files.insert("end", f"  ... altri {len(unsupported) - 12} file")

        if files and unsupported:
            self.label_file_status.config(
                text=f"{len(files)} file verranno controllati. {len(unsupported)} file non supportati saranno ignorati."
            )
        elif files:
            self.label_file_status.config(text=f"{len(files)} file pronti per il controllo.")
        elif unsupported:
            self.label_file_status.config(
                text="Ho trovato file nella cartella, ma nessuno e in un formato supportato."
            )
        else:
            self.label_file_status.config(text="La cartella non contiene file.")

    def _selected_labels(self) -> set[str]:
        return {label for label, var in self._label_vars.items() if var.get()}

    def _min_score(self) -> float:
        mode = DETECTION_MODES.get(self.var_detection_mode.get(), DETECTION_MODES["recommended"])
        return float(mode["min_score"])

    def _exclude_terms(self) -> set[str]:
        raw = self.var_exceptions.get()
        return {part.strip() for part in raw.split(",") if part.strip()}

    def _profile_payload(self) -> dict:
        return {
            "labels": sorted(self._selected_labels()),
            "detection_mode": self.var_detection_mode.get(),
            "exceptions": self.var_exceptions.get(),
            "include_kept_in_index": self.var_include_kept_index.get(),
        }

    def _apply_profile(self, profile: dict) -> None:
        labels = set(profile.get("labels", []))
        for label, var in self._label_vars.items():
            var.set(label in labels)
        mode = str(profile.get("detection_mode", "recommended"))
        if mode not in DETECTION_MODES:
            mode = "recommended"
        self.var_detection_mode.set(mode)
        self.var_exceptions.set(str(profile.get("exceptions", "")))
        self.var_include_kept_index.set(bool(profile.get("include_kept_in_index", False)))

    def _save_profile(self) -> None:
        path = filedialog.asksaveasfilename(
            title="Salva impostazioni",
            defaultextension=".json",
            filetypes=[("Impostazioni", "*.json"), ("Tutti i file", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self._profile_payload(), f, ensure_ascii=False, indent=2)
            messagebox.showinfo("Impostazioni", "Impostazioni salvate.")
        except Exception as exc:
            messagebox.showerror("Errore", str(exc))

    def _load_profile(self) -> None:
        path = filedialog.askopenfilename(
            title="Carica impostazioni",
            filetypes=[("Impostazioni", "*.json"), ("Tutti i file", "*.*")],
        )
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                self._apply_profile(json.load(f))
            messagebox.showinfo("Impostazioni", "Impostazioni caricate.")
        except Exception as exc:
            messagebox.showerror("Errore", str(exc))

    # ------------------------------------------------------------------
    # Analisi
    # ------------------------------------------------------------------

    def _start_analysis(self) -> None:
        input_dir = self.var_input.get().strip()
        if not input_dir or not os.path.isdir(input_dir):
            messagebox.showerror("Cartella mancante", "Scegli prima la cartella con i documenti.")
            return

        output_dir = self.var_output.get().strip()
        if not output_dir:
            messagebox.showerror("Cartella mancante", "Scegli dove salvare le copie anonime.")
            return

        labels = self._selected_labels()
        if not labels:
            messagebox.showwarning("Nessun dato scelto", "Seleziona almeno un tipo di dato da nascondere.")
            return

        self._files = core.collect_files(input_dir)
        self._unsupported_files = core.collect_unsupported_files(input_dir)
        if not self._files:
            if self._unsupported_files:
                sample = "\n".join(f"- {os.path.basename(path)}" for path in self._unsupported_files[:10])
                messagebox.showwarning(
                    "Formato non supportato",
                    "Ho trovato file nella cartella, ma non posso controllarli.\n\n"
                    "Formati supportati: PDF, Word, Excel .xlsx, TXT, CSV, TSV.\n\n"
                    f"File ignorati:\n{sample}",
                )
            else:
                messagebox.showwarning("Nessun documento", "Non ho trovato documenti supportati in quella cartella.")
            return

        if self._unsupported_files:
            sample = "\n".join(f"- {os.path.basename(path)}" for path in self._unsupported_files[:8])
            extra = "" if len(self._unsupported_files) <= 8 else f"\n... e altri {len(self._unsupported_files) - 8} file"
            messagebox.showinfo(
                "Alcuni file saranno ignorati",
                "Procedo con i documenti supportati.\n\n"
                "Questi file non sono in un formato leggibile dall'app e saranno ignorati:\n"
                f"{sample}{extra}\n\n"
                "Formati supportati: PDF, Word, Excel .xlsx, TXT, CSV, TSV.",
            )

        self.btn_analyze.state(["disabled"])
        self.progress_var.set(0)
        min_score = self._min_score()
        exclusions = self._exclude_terms()

        def run() -> None:
            def progress(current: int, total: int, name: str) -> None:
                pct = (current / total * 100) if total else 100
                self.after(0, self.progress_var.set, pct)
                msg = f"Controllo: {name}" if name else "Controllo completato."
                self.after(0, self.label_status.config, {"text": msg})

            try:
                result = core.detect_spans(
                    self._files,
                    labels,
                    progress,
                    min_score=min_score,
                    exclude_terms=exclusions,
                )
                self.after(0, self._on_analysis_done, result)
            except Exception as exc:
                self.after(0, messagebox.showerror, "Errore durante il controllo", str(exc))
                self.after(0, self.btn_analyze.state, ["!disabled"])

        threading.Thread(target=run, daemon=True).start()

    def _on_analysis_done(self, result: core.ProcessingResult) -> None:
        self._spans = result.spans
        self._rebuild_codes()
        self.btn_analyze.state(["!disabled"])
        if result.errors:
            error_text = "\n".join(result.errors)
            if "Dipendenza mancante" in error_text:
                error_text += (
                    "\n\nPer sistemare, chiudi l'app e apri il prompt nella cartella del progetto, poi esegui:\n"
                    "py -m pip install -r requirements.txt\n\n"
                    "Se manca OpenAI Privacy Filter, esegui anche:\n"
                    "py -m pip install -r requirements-opf.txt\n\n"
                    "Dopo l'installazione riapri l'app con:\n"
                    "py gui.py"
                )
            messagebox.showwarning(
                "Alcuni documenti non sono stati controllati",
                error_text,
            )

        self._populate_review_table()
        self.notebook.tab(1, state="normal")
        self.notebook.select(1)

    # ------------------------------------------------------------------
    # Tab 2
    # ------------------------------------------------------------------

    def _build_tab_review(self) -> None:
        f = self.tab_review
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=3)
        f.rowconfigure(3, weight=2)

        toolbar = ttk.Frame(f)
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=PAD, pady=(PAD, 0))

        ttk.Label(toolbar, text="Mostra:").pack(side="left")
        self.var_filter_label = tk.StringVar(value=FILTER_ALL)
        self.combo_filter = ttk.Combobox(toolbar, textvariable=self.var_filter_label, state="readonly", width=24)
        self.combo_filter.pack(side="left", padx=(4, PAD))
        self.combo_filter.bind("<<ComboboxSelected>>", lambda _: self._apply_filter())

        ttk.Button(toolbar, text="Nascondi visibili", command=self._select_all).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Lascia visibili", command=self._deselect_all).pack(side="left", padx=2)

        ttk.Label(
            toolbar,
            text="Clicca nella colonna Nascondi per cambiare decisione.",
            style="Muted.TLabel",
        ).pack(side="right", padx=PAD)

        cols = ("oscura", "codice", "file", "tipo", "testo", "affidabilita", "origine")
        self.tree = ttk.Treeview(f, columns=cols, show="headings", selectmode="browse")
        headings = {
            "oscura": "Nascondi",
            "codice": "Codice",
            "file": "Documento",
            "tipo": "Tipo di dato",
            "testo": "Testo trovato",
            "affidabilita": "Affidabilita",
            "origine": "Trovato da",
        }
        for col, title in headings.items():
            self.tree.heading(col, text=title, command=lambda c=col: self._sort_by(c))

        self.tree.column("oscura", width=80, anchor="center", stretch=False)
        self.tree.column("codice", width=120, anchor="center", stretch=False)
        self.tree.column("file", width=170)
        self.tree.column("tipo", width=155)
        self.tree.column("testo", width=300)
        self.tree.column("affidabilita", width=90, anchor="center", stretch=False)
        self.tree.column("origine", width=85, anchor="center", stretch=False)

        self.tree.tag_configure("redact", background="#fef2f2")
        self.tree.tag_configure("keep", background="#f0fdf4")

        vsb = ttk.Scrollbar(f, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=(PAD, 0), pady=(PAD, 0))
        vsb.grid(row=1, column=1, sticky="ns", pady=(PAD, 0))

        self.tree.bind("<ButtonRelease-1>", self._on_tree_click)

        ttk.Separator(f, orient="horizontal").grid(
            row=2, column=0, columnspan=2, sticky="ew", padx=PAD, pady=(PAD, 0))

        preview_header = ttk.Frame(f)
        preview_header.grid(row=2, column=0, columnspan=2, sticky="ew", padx=PAD)
        self.label_preview_title = ttk.Label(
            preview_header,
            text="Anteprima: seleziona una riga",
            style="Muted.TLabel",
        )
        self.label_preview_title.pack(side="left", pady=(2, 0))

        preview_frame = ttk.Frame(f)
        preview_frame.grid(row=3, column=0, columnspan=2, sticky="nsew", padx=PAD, pady=(2, 0))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.columnconfigure(1, weight=1)
        preview_frame.rowconfigure(1, weight=1)

        ttk.Label(preview_frame, text="Originale").grid(row=0, column=0, sticky="w")
        ttk.Label(preview_frame, text="Come verra salvato").grid(row=0, column=1, sticky="w", padx=(PAD, 0))

        self.preview_original = self._build_preview_text(preview_frame)
        self.preview_redacted = self._build_preview_text(preview_frame)
        self.preview_original.grid(row=1, column=0, sticky="nsew", pady=(2, 0))
        self.preview_redacted.grid(row=1, column=1, sticky="nsew", padx=(PAD, 0), pady=(2, 0))

        ttk.Separator(f, orient="horizontal").grid(
            row=4, column=0, columnspan=2, sticky="ew", padx=PAD, pady=(PAD, 0))

        manual_frame = ttk.Frame(f)
        manual_frame.grid(row=5, column=0, columnspan=2, sticky="ew", padx=PAD, pady=(2, 0))

        ttk.Label(manual_frame, text="Manca qualcosa?", font=("Segoe UI", 9, "bold")).pack(side="left")
        ttk.Label(manual_frame, text=" Testo da nascondere:").pack(side="left")
        self.var_manual_text = tk.StringVar()
        ttk.Entry(manual_frame, textvariable=self.var_manual_text, width=28).pack(side="left", padx=(2, PAD))

        ttk.Label(manual_frame, text="Tipo:").pack(side="left")
        self.var_manual_type = tk.StringVar(value=display_label("private_organization"))
        manual_combo = ttk.Combobox(
            manual_frame,
            textvariable=self.var_manual_type,
            values=[name for _, name, _ in DATA_TYPES],
            state="readonly",
            width=22,
        )
        manual_combo.pack(side="left", padx=(2, PAD))

        ttk.Button(manual_frame, text="Aggiungi", command=self._add_manual_span).pack(side="left")

        self.label_manual_status = ttk.Label(manual_frame, text="", foreground="#2563eb")
        self.label_manual_status.pack(side="left", padx=(PAD, 0))

        footer = ttk.Frame(f)
        footer.grid(row=6, column=0, columnspan=2, sticky="ew", padx=PAD, pady=(PAD // 2, PAD))
        self.label_summary = ttk.Label(footer, text="")
        self.label_summary.pack(side="left")
        self.btn_save = ttk.Button(footer, text="Salva copie anonime", style="Accent.TButton", command=self._start_save)
        self.btn_save.pack(side="right")

    def _build_preview_text(self, parent: ttk.Frame) -> tk.Text:
        widget = tk.Text(
            parent,
            font=("Consolas", 9),
            wrap="word",
            relief="flat",
            bg="#fafafa",
            state="disabled",
            height=8,
        )
        widget.tag_configure("highlight_redact", background="#fecaca", foreground="#000000")
        widget.tag_configure("highlight_keep", background="#bbf7d0", foreground="#000000")
        return widget

    def _populate_review_table(self) -> None:
        labels_found = sorted({display_label(s.label) for s in self._spans})
        self.combo_filter["values"] = [FILTER_ALL] + labels_found
        self._render_tree()
        self._update_summary()

    def _visible_indices(self) -> list[int]:
        filter_value = self.var_filter_label.get()
        filter_label = label_from_display(filter_value)
        indices = [
            i for i, span in enumerate(self._spans)
            if filter_value == FILTER_ALL or span.label == filter_label
        ]
        if self._sort_col:
            indices.sort(key=lambda i: self._sort_key(i, self._sort_col), reverse=self._sort_reverse)
        return indices

    def _sort_key(self, idx: int, col: str):
        span = self._spans[idx]
        if col == "oscura":
            return span.will_redact
        if col == "codice":
            return span.codice
        if col == "file":
            return span.file.casefold()
        if col == "tipo":
            return display_label(span.label).casefold()
        if col == "testo":
            return span.text.casefold()
        if col == "affidabilita":
            return span.score if span.score is not None else -1
        if col == "origine":
            return SOURCE_NAME.get(span.source, span.source).casefold()
        return idx

    def _render_tree(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for idx in self._visible_indices():
            self._insert_tree_row(idx, self._spans[idx])

    def _insert_tree_row(self, idx: int, span: core.Span) -> None:
        check = "Si" if span.will_redact else "No"
        tag = "redact" if span.will_redact else "keep"
        text = span.text if len(span.text) <= 140 else span.text[:137] + "..."
        self.tree.insert(
            "",
            "end",
            iid=str(idx),
            values=(
                check,
                span.codice,
                span.file,
                display_label(span.label),
                text,
                score_label(span.score),
                SOURCE_NAME.get(span.source, span.source),
            ),
            tags=(tag,),
        )

    def _apply_filter(self) -> None:
        self._render_tree()

    def _sort_by(self, col: str) -> None:
        if self._sort_col == col:
            self._sort_reverse = not self._sort_reverse
        else:
            self._sort_col = col
            self._sort_reverse = False
        self._render_tree()

    def _on_tree_click(self, event: tk.Event) -> None:
        region = self.tree.identify_region(event.x, event.y)
        if region != "cell":
            return
        iid = self.tree.identify_row(event.y)
        if not iid:
            return
        idx = int(iid)
        span = self._spans[idx]

        col = self.tree.identify_column(event.x)
        if col == "#1":
            span.will_redact = not span.will_redact
            self._rebuild_codes()
            self._render_tree()
            self._update_summary()
            if self._preview_file == span.file:
                self._show_preview(span.file, span.start)
        else:
            self._show_preview(span.file, span.start)

    def _show_preview(self, basename: str, scroll_to: Optional[int] = None) -> None:
        self._preview_file = basename
        if basename not in self._text_cache:
            filepath = next((f for f in self._files if os.path.basename(f) == basename), None)
            if not filepath:
                return
            try:
                self._text_cache[basename] = core.extract_text(filepath)
            except Exception as exc:
                self._text_cache[basename] = f"Errore lettura: {exc}"

        text = self._text_cache[basename]
        file_spans = [s for s in self._spans if s.file == basename]
        redacted = core.preview_redacted_text(text, file_spans)

        self.label_preview_title.config(text=f"Anteprima: {basename}")
        self._set_text(self.preview_original, text)
        self._set_text(self.preview_redacted, redacted)

        self.preview_original.config(state="normal")
        for span in file_spans:
            tag = "highlight_redact" if span.will_redact else "highlight_keep"
            self.preview_original.tag_add(tag, f"1.0 + {span.start} chars", f"1.0 + {span.end} chars")
        self.preview_original.config(state="disabled")

        if scroll_to is None and file_spans:
            scroll_to = min(file_spans, key=lambda s: s.start).start
        if scroll_to is not None:
            self.preview_original.see(f"1.0 + {scroll_to} chars")
            self.preview_redacted.see("1.0")

    def _set_text(self, widget: tk.Text, text: str) -> None:
        widget.config(state="normal")
        widget.delete("1.0", "end")
        widget.insert("end", text)
        widget.config(state="disabled")

    def _select_all(self) -> None:
        self._set_all(True)

    def _deselect_all(self) -> None:
        self._set_all(False)

    def _set_all(self, value: bool) -> None:
        for idx in self._visible_indices():
            self._spans[idx].will_redact = value
        self._rebuild_codes()
        self._render_tree()
        self._update_summary()
        if self._preview_file:
            self._show_preview(self._preview_file)

    def _rebuild_codes(self) -> None:
        for span in self._spans:
            span.codice = ""
        core.build_entity_registry(self._spans, redacted_only=True)

    def _update_summary(self) -> None:
        total = len(self._spans)
        to_redact = sum(1 for s in self._spans if s.will_redact)
        self.label_summary.config(
            text=f"Dati trovati: {total}  |  Da nascondere: {to_redact}  |  Lasciati visibili: {total - to_redact}"
        )

    def _add_manual_span(self) -> None:
        search_text = self.var_manual_text.get().strip()
        label = label_from_display(self.var_manual_type.get().strip())
        if not search_text:
            self.label_manual_status.config(text="Scrivi il testo da cercare.", foreground="#dc2626")
            return

        added = 0
        for filepath in self._files:
            basename = os.path.basename(filepath)
            if basename not in self._text_cache:
                try:
                    self._text_cache[basename] = core.extract_text(filepath)
                except Exception:
                    continue
            text = self._text_cache[basename]

            start = 0
            while True:
                pos = text.find(search_text, start)
                if pos == -1:
                    break
                already = any(
                    s.file == basename and s.start == pos and s.end == pos + len(search_text) and s.label == label
                    for s in self._spans
                )
                if not already:
                    self._spans.append(core.Span(
                        file=basename,
                        label=label,
                        text=search_text,
                        start=pos,
                        end=pos + len(search_text),
                        score=None,
                        will_redact=True,
                        source="manual",
                    ))
                    added += 1
                start = pos + max(1, len(search_text))

        if added == 0:
            self.label_manual_status.config(text=f'"{search_text}" non trovato.', foreground="#dc2626")
            return

        self._spans = core.dedupe_spans(self._spans)
        self._rebuild_codes()
        self._populate_review_table()
        self.label_manual_status.config(text=f"Aggiunto {added} volta/e.", foreground="#16a34a")
        self.var_manual_text.set("")
        if self._preview_file:
            self._show_preview(self._preview_file)

    # ------------------------------------------------------------------
    # Salvataggio
    # ------------------------------------------------------------------

    def _start_save(self) -> None:
        output_dir = self.var_output.get().strip()
        if not output_dir:
            messagebox.showerror("Cartella mancante", "Scegli dove salvare le copie anonime.")
            return

        self.btn_save.state(["disabled"])
        self.btn_analyze.state(["disabled"])
        self._rebuild_codes()
        include_kept = self.var_include_kept_index.get()

        def run() -> None:
            def progress(current: int, total: int, name: str) -> None:
                pct = (current / total * 100) if total else 100
                self.after(0, self.progress_var.set, pct)
                msg = f"Salvataggio: {name}" if name else "Salvataggio completato."
                self.after(0, self.label_status.config, {"text": msg})

            try:
                errors = core.save_outputs(
                    self._files,
                    self._spans,
                    output_dir,
                    progress,
                    include_kept_in_index=include_kept,
                )
                self.after(0, self._on_save_done, errors, output_dir)
            except Exception as exc:
                self.after(0, messagebox.showerror, "Errore salvataggio", str(exc))
            finally:
                self.after(0, self.btn_save.state, ["!disabled"])
                self.after(0, self.btn_analyze.state, ["!disabled"])

        threading.Thread(target=run, daemon=True).start()

    def _on_save_done(self, errors: list[str], output_dir: str) -> None:
        self._populate_report(errors, output_dir)
        self.notebook.tab(2, state="normal")
        self.notebook.select(2)

    # ------------------------------------------------------------------
    # Tab 3
    # ------------------------------------------------------------------

    def _build_tab_report(self) -> None:
        f = self.tab_report
        f.columnconfigure(0, weight=1)
        f.rowconfigure(1, weight=1)

        ttk.Label(f, text="Copie anonime salvate", style="Title.TLabel").grid(
            row=0, column=0, sticky="w", padx=PAD * 2, pady=(PAD * 2, PAD))

        self.text_report = tk.Text(
            f,
            font=("Consolas", 9),
            wrap="word",
            relief="flat",
            bg="#f9f9f9",
            state="disabled",
        )
        self.text_report.grid(row=1, column=0, sticky="nsew", padx=PAD, pady=(0, PAD))

        footer = ttk.Frame(f)
        footer.grid(row=2, column=0, sticky="ew", padx=PAD, pady=(0, PAD))
        ttk.Button(footer, text="Apri cartella da caricare", command=self._open_output_folder).pack(side="left")
        ttk.Button(footer, text="Nuovo lavoro", command=self._reset).pack(side="right")

    def _populate_report(self, errors: list[str], output_dir: str) -> None:
        redacted = sum(1 for s in self._spans if s.will_redact)
        kept = len(self._spans) - redacted

        lines = [
            f"Documenti controllati : {len(self._files)}",
            f"Dati trovati          : {len(self._spans)}",
            f"Dati nascosti         : {redacted}",
            f"Lasciati visibili     : {kept}",
            "",
            f"Cartella da caricare nell'LLM: {core.safe_output_dir(output_dir)}",
            "",
            "Carica nell'LLM solo i file dentro:",
            f"  {core.SAFE_OUTPUT_SUBDIR}",
            "",
            "I file di recupero e controllo sono separati in:",
            f"  {core.RESERVED_OUTPUT_SUBDIR}",
            "Non caricare questa cartella nell'LLM: contiene dati originali e mapping.",
            "",
        ]
        if errors:
            lines.append("Attenzione: alcuni documenti hanno dato errore:")
            lines.extend(f"  - {e}" for e in errors)
        else:
            lines.append("Nessun errore riscontrato.")

        self.text_report.config(state="normal")
        self.text_report.delete("1.0", "end")
        self.text_report.insert("end", "\n".join(lines))
        self.text_report.config(state="disabled")

    def _open_output_folder(self) -> None:
        folder = self.var_output.get().strip()
        safe_folder = core.safe_output_dir(folder) if folder else ""
        if safe_folder and os.path.isdir(safe_folder):
            os.startfile(safe_folder)

    def _reset(self) -> None:
        self._spans = []
        self._files = []
        self._unsupported_files = []
        self._text_cache = {}
        self._preview_file = ""
        self._sort_col = None
        self._sort_reverse = False
        self.label_preview_title.config(text="Anteprima: seleziona una riga")
        self._set_text(self.preview_original, "")
        self._set_text(self.preview_redacted, "")
        self.progress_var.set(0)
        self.label_status.config(text="")
        self.label_file_status.config(text="")
        self.listbox_files.delete(0, "end")
        self.tree.delete(*self.tree.get_children())
        self.text_report.config(state="normal")
        self.text_report.delete("1.0", "end")
        self.text_report.config(state="disabled")
        self.notebook.tab(1, state="disabled")
        self.notebook.tab(2, state="disabled")
        self.notebook.select(0)


if __name__ == "__main__":
    app = App()
    app.mainloop()
