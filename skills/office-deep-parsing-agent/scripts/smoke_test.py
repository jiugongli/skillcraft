#!/usr/bin/env python3
"""Quick validation for skill runtime and dependencies."""

from __future__ import annotations

import json
import platform
import sys
import zipfile
from pathlib import Path
from tempfile import TemporaryDirectory


PNG_1X1 = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\rIDATx\x9cc\xf8\xff"
    b"\xff?\x00\x05\xfe\x02\xfeA\xe2%\xb5\x00\x00\x00\x00IEND\xaeB`\x82"
)


def _run_malformed_workbook_regression(skill_root: Path) -> dict[str, str]:
    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))
    from runtime.pipeline import (
        ObjectRecord,
        analyze_workbook,
        build_vision_tasks,
        export_visual_assets,
    )

    with TemporaryDirectory(prefix="excel_skill_smoke_") as temp_dir:
        temp_root = Path(temp_dir)
        bad_workbook = temp_root / "not_ooxml.xlsx"
        bad_workbook.write_bytes(b"this is not an OOXML zip workbook")
        analysis = analyze_workbook(bad_workbook, "not_ooxml.xlsx")
        export_visual_assets(bad_workbook, analysis, temp_root / "visuals")
    ok = analysis.extraction_status == "fail_soft"
    ok = ok and analysis.status_code == "blocked_non_ooxml_container"
    ok = ok and any("workbook load failed" in warning for warning in analysis.extraction_warnings)
    ok = ok and any(
        "embedded image export via openpyxl skipped" in warning for warning in analysis.extraction_warnings
    )
    analysis.workbook_object_records.append(
        ObjectRecord(
            object_type="sheet_pdf_export",
            sheet_name="*",
            export_path="visual_exports/not_ooxml.pdf",
        )
    )
    vision_tasks = build_vision_tasks([analysis])
    ok = ok and len(vision_tasks) == 1 and vision_tasks[0].status == "queued"
    return {"status": "ok" if ok else "failed", "detail": "malformed .xlsx handled without aborting"}


def _run_visual_workbook_queue_regression(skill_root: Path) -> dict[str, str]:
    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))
    from openpyxl import Workbook
    from runtime.pipeline import (
        analyze_workbook,
        assign_workbook_vision_statuses,
        build_vision_tasks,
        export_visual_assets,
    )

    with TemporaryDirectory(prefix="excel_skill_smoke_") as temp_dir:
        temp_root = Path(temp_dir)
        workbook_path = temp_root / "visual.xlsx"
        wb = Workbook()
        wb.active["A1"] = "visual evidence workbook"
        wb.save(workbook_path)
        with zipfile.ZipFile(workbook_path, "a") as zf:
            zf.writestr("xl/media/image1.png", PNG_1X1)
        analysis = analyze_workbook(workbook_path, "visual.xlsx")
        exported = export_visual_assets(workbook_path, analysis, temp_root / "visuals")
        analysis.workbook_object_records.extend([item for item in exported if item.sheet_name == "*"])
        vision_tasks = build_vision_tasks([analysis])
        assign_workbook_vision_statuses([analysis], vision_tasks)
    ok = analysis.extraction_status == "processed"
    ok = ok and any(task.status == "queued" for task in vision_tasks)
    ok = ok and analysis.vision_status == "ready"
    return {"status": "ok" if ok else "failed", "detail": "processable visual workbook queues Vision task"}


def main() -> int:
    skill_root = Path(__file__).resolve().parents[1]
    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))

    from runtime.executables import find_executable

    report = {
        "python": {"status": "ok", "detail": f"{sys.implementation.name} {sys.version.split()[0]}"},
        "imports": {"core": {}, "optional": {}},
        "executables": {},
    }

    for module in ("openpyxl", "runtime.pipeline"):
        try:
            __import__(module)
            report["imports"]["core"][module] = {"status": "ok"}
        except Exception as exc:  # noqa: BLE001
            report["imports"]["core"][module] = {"status": "missing_or_failed", "detail": str(exc)}

    for module in ("pytesseract", "PIL", "pypdfium2", "docx", "pptx", "win32com"):
        try:
            __import__(module)
            report["imports"]["optional"][module] = {"status": "ok"}
        except Exception as exc:  # noqa: BLE001
            report["imports"]["optional"][module] = {"status": "missing_or_failed", "detail": str(exc)}

    for exe in ("markitdown", "soffice", "powershell", "tesseract"):
        path = find_executable(exe)
        report["executables"][exe] = {"status": "ok" if path else "missing", "detail": "available" if path else ""}
    report["executables"]["windows_excel_automation"] = {
        "status": "available_if_excel_installed" if platform.system() == "Windows" else "not_applicable",
        "detail": "uses pywin32 when installed, otherwise PowerShell COM on Windows",
    }
    report["regressions"] = {
        "malformed_xlsx_fail_soft": _run_malformed_workbook_regression(skill_root),
        "processable_visual_workbook_vision_queue": _run_visual_workbook_queue_regression(skill_root),
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

    failed_core = [k for k, v in report["imports"]["core"].items() if v["status"] != "ok"]
    failed_regressions = [k for k, v in report["regressions"].items() if v["status"] != "ok"]
    return 1 if failed_core or failed_regressions else 0


if __name__ == "__main__":
    raise SystemExit(main())
