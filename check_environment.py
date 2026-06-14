"""
Check whether the local environment has the required dependencies.
Run with:  py check_environment.py
"""
from __future__ import annotations

import importlib
import sys


REQUIRED = {
    "tkinter": "install Python with Tcl/Tk support",
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
            print(f"  MISSING   {module}  ->  {install_cmd}")
            ok = False

    try:
        import core  # noqa: F401
        print("  OK        core.py")
    except Exception as exc:
        print(f"  ERROR     core.py  ->  {exc}")
        ok = False

    if ok:
        print("\nEnvironment ready. Start the app with:  py gui.py")
        return 0

    print("\nInstall the missing modules and try again.")
    print("Quick commands:")
    print("  py -m pip install -r requirements.txt")
    print("  py -m pip install -r requirements-opf.txt")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
