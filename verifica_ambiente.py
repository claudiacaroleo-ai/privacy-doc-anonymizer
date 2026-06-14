"""
Verifica che tutte le dipendenze necessarie siano installate.
Esegui con:  py verifica_ambiente.py
"""
from __future__ import annotations

import importlib
import sys


REQUIRED = {
    "tkinter": "installa Python con supporto Tcl/Tk",
    "pdfplumber": "py -m pip install pdfplumber",
    "docx": "py -m pip install python-docx",
    "openpyxl": "py -m pip install openpyxl",
    "opf": "py -m pip install -r requirements-opf.txt",
}


def main() -> int:
    print(f"Python: {sys.version.split()[0]}")

    ok = True
    for module, install_cmd in REQUIRED.items():
        try:
            importlib.import_module(module)
            print(f"  OK        {module}")
        except ImportError:
            print(f"  MANCANTE  {module}  ->  {install_cmd}")
            ok = False

    try:
        import core  # noqa: F401
        print("  OK        core.py")
    except Exception as exc:
        print(f"  ERRORE    core.py  ->  {exc}")
        ok = False

    if ok:
        print("\nAmbiente pronto. Avvia l'app con:  py gui.py")
        return 0

    print("\nInstalla i moduli mancanti e riprova.")
    print("Comandi rapidi:")
    print("  py -m pip install -r requirements.txt")
    print("  py -m pip install -r requirements-opf.txt")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
