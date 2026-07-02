#!/usr/bin/env python3
"""Run OCR stage over visual exports."""

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
        description="Run OCR on visual exports and write OCR logs."
    )
    parser.add_argument(
        "--visual-root",
        required=True,
        help="Directory containing visual exports (images/PDFs).",
    )
    parser.add_argument(
        "--ocr-output",
        required=True,
        help="Directory where OCR result files are written.",
    )
    parser.add_argument("--backend", default="local", help="OCR backend name.")
    return parser


def main() -> int:
    parser = _build_parser()
    args = parser.parse_args()
    skill_root = _skill_root()
    if str(skill_root) not in sys.path:
        sys.path.insert(0, str(skill_root))

    from runtime.pipeline import run_ocr_for_exports

    visual_root = Path(args.visual_root).expanduser().resolve()
    ocr_output = Path(args.ocr_output).expanduser().resolve()
    if not visual_root.exists() or not visual_root.is_dir():
        print(f"error: visual root does not exist or is not a directory: {visual_root.name}", file=sys.stderr)
        return 2
    ocr_output.mkdir(parents=True, exist_ok=True)

    results = run_ocr_for_exports(
        export_root=visual_root,
        output_root=ocr_output,
        backend=args.backend,
        display_root=visual_root,
    )
    payload = {
        "visual_root": visual_root.name or "visual_root",
        "ocr_output": ocr_output.name or "ocr_output",
        "backend": args.backend,
        "result_count": len(results),
        "results": [asdict(item) for item in results],
    }
    (ocr_output / "ocr_run_log.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
