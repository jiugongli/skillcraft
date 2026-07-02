#!/usr/bin/env python3
"""Export workbook visual assets for OCR/Vision stages."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path


def _skill_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Export embedded images and optional PDF from workbook."
    )
    parser.add_argument("--workbook", required=True, help="Workbook path.")
    parser.add_argument("--output-dir", required=True, help="Export output directory.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    skill_root = _skill_root()
    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))

    from runtime.pipeline import analyze_workbook, export_visual_assets

    workbook = Path(args.workbook).expanduser().resolve()
    output_dir = Path(args.output_dir).expanduser().resolve()
    if not workbook.exists() or not workbook.is_file():
        print(f"error: workbook does not exist or is not a file: {workbook.name}", file=sys.stderr)
        return 2
    output_dir.mkdir(parents=True, exist_ok=True)

    workbook_analysis = analyze_workbook(workbook)
    exported = export_visual_assets(workbook, workbook_analysis, output_dir)
    for item in exported:
        if item.export_path:
            try:
                item.export_path = str(Path(item.export_path).resolve().relative_to(output_dir))
            except ValueError:
                item.export_path = Path(item.export_path).name
    payload = {
        "workbook": workbook.name,
        "output_dir": output_dir.name or "output_dir",
        "exported_count": len(exported),
        "exports": [asdict(item) for item in exported],
        "warnings": workbook_analysis.extraction_warnings,
    }
    (output_dir / "visual_export_log.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
