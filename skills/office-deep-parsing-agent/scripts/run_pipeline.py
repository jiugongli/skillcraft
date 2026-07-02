#!/usr/bin/env python3
"""Executable entrypoint for office-deep-parsing-agent skill."""

from __future__ import annotations

import argparse
import json
import platform
import sys
from dataclasses import asdict
from pathlib import Path


def _skill_root() -> Path:
    # .../.cursor/skills/office-deep-parsing-agent
    return Path(__file__).resolve().parents[1]


def _probe_environment() -> dict[str, dict[str, str]]:
    from runtime.executables import find_executable

    def _state(executable: str) -> dict[str, str]:
        path = find_executable(executable)
        return {"status": "ok" if path else "missing", "detail": "available" if path else ""}

    probe: dict[str, dict[str, str]] = {
        "python": {"status": "ok", "detail": f"{sys.implementation.name} {sys.version.split()[0]}"},
        "markitdown": _state("markitdown"),
        "soffice": _state("soffice"),
        "powershell": _state("powershell"),
        "tesseract": _state("tesseract"),
        "windows_excel_automation": {
            "status": "available_if_excel_installed" if platform.system() == "Windows" else "not_applicable",
            "detail": "uses pywin32 when installed, otherwise PowerShell COM on Windows",
        },
    }
    for module in ("openpyxl", "pytesseract", "PIL", "pypdfium2", "docx", "pptx", "win32com"):
        try:
            __import__(module)
            probe[f"module:{module}"] = {"status": "ok", "detail": ""}
        except Exception as exc:  # noqa: BLE001
            probe[f"module:{module}"] = {"status": "missing_or_failed", "detail": str(exc)}
    return probe


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run deep Office parsing pipeline with environment probe logs."
    )
    parser.add_argument("--input-path", required=True, help="Input file or directory.")
    parser.add_argument("--output-root", required=True, help="Output directory.")
    parser.add_argument("--ocr-backend", default="local", help="OCR backend name.")
    parser.add_argument("--no-markitdown", action="store_true")
    parser.add_argument("--no-visual-export", action="store_true")
    parser.add_argument("--no-ocr", action="store_true")
    parser.add_argument("--no-attachments", action="store_true")
    parser.add_argument("--no-recurse", action="store_true")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    skill_root = _skill_root()
    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))

    from runtime.pipeline import PipelineConfig, run_pipeline

    config = PipelineConfig(
        input_path=Path(args.input_path),
        output_root=Path(args.output_root),
        enable_markitdown=not args.no_markitdown,
        enable_visual_export=not args.no_visual_export,
        enable_ocr=not args.no_ocr,
        ocr_backend=args.ocr_backend,
        recurse=not args.no_recurse,
        extract_attachments=not args.no_attachments,
    )
    try:
        config.normalize()
        config.output_root.mkdir(parents=True, exist_ok=True)
        env_probe = _probe_environment()
        (config.output_root / "environment_probe.json").write_text(
            json.dumps(env_probe, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        result = run_pipeline(config)
        (config.output_root / "pipeline_result_snapshot.json").write_text(
            json.dumps(asdict(result), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
