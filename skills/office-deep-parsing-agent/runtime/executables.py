"""Cross-platform executable discovery without third-party imports."""

from __future__ import annotations

import os
import shutil
from pathlib import Path


EXECUTABLE_CANDIDATES: dict[str, tuple[str, ...]] = {
    "soffice": (
        "soffice",
        "libreoffice",
        "/Applications/LibreOffice.app/Contents/MacOS/soffice",
        "/usr/local/bin/soffice",
        "/opt/homebrew/bin/soffice",
        r"C:\Program Files\LibreOffice\program\soffice.exe",
        r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
    ),
    "tesseract": (
        "tesseract",
        "/usr/local/bin/tesseract",
        "/opt/homebrew/bin/tesseract",
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ),
    "powershell": (
        "powershell",
        "pwsh",
        r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe",
        r"C:\Program Files\PowerShell\7\pwsh.exe",
    ),
}


def find_executable(name: str) -> str | None:
    candidates = EXECUTABLE_CANDIDATES.get(name, (name,))
    for candidate in candidates:
        if os.path.sep not in candidate and (os.path.altsep is None or os.path.altsep not in candidate):
            resolved = shutil.which(candidate)
            if resolved:
                return resolved
            continue
        path = Path(candidate).expanduser()
        if path.is_file():
            return str(path)
    return None
