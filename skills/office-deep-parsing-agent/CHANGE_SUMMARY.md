# Change Summary

## What Changed

- Renamed the skill from `excel-deep-parsing-agent` to `office-deep-parsing-agent` to match the Office-wide parsing scope.
- Added RPC-style Excel visual corpus handling: ZIP/DrawingML preflight, media extension sniffing, raw media extraction, per-sheet contact sheets, shape/object text sampling, and Vision queue output.
- Added Windows Microsoft Excel automation fallback for workbook PDF export and `.xls -> .xlsx` conversion when LibreOffice is unavailable.
- Added Windows heavy-vision follow-up fixes: malformed or mismatched-extension `.xlsx` files now fail soft during visual export, non-OOXML container hints are recorded, and workbook-level visual exports still enter the Vision queue when cell parsing fails.
- Added machine-readable status semantics so orchestrators can distinguish pipeline execution success from workbook extraction success and Vision readiness.
- Added partial Vision readiness semantics when a workbook has queued assets plus blocked assets that still require conversion/rendering.
- Added MarkItDown fallback through `python -m markitdown` so markdown extraction can use the active virtual environment even when the CLI is not on PATH.
- Added Tesseract CLI fallback so local OCR can run when `pytesseract` is absent but the `tesseract` executable is available.
- Added input validation so missing or invalid `--input-path` fails with exit code `2` instead of generating empty success artifacts.
- Added collision-safe artifact naming for markdown, visual exports, attachment staging, OCR JSON, and deep-reading notes.
- Added collision-safe OCR result names based on relative visual export paths so same-named PDFs/images in different export folders do not overwrite each other.
- Changed shared runtime artifacts to use relative source/output paths and removed absolute interpreter paths from environment probes.
- Added a subprocess wrapper with a 120-second timeout for `markitdown` and `soffice`.
- Added a 25-page cap for local PDF OCR.
- Added executable discovery across PATH plus common macOS and Windows install locations for LibreOffice, PowerShell, and Tesseract.
- Escaped Markdown table cells in `file_inventory.md`.
- Clarified dependencies, optional tool behavior, proxy/offline install options, and legacy `.xls/.doc/.ppt` conversion limits.
- Updated `VERSION` to `0.3.0` and added a `0.3.0` rename changelog entry above the `0.2.x` hardening history.

## Why It Changed

- Prevent false-positive successful runs when the input path is wrong.
- Preserve traceability when a package contains same-named Office files.
- Make outputs safer to share across teams by avoiding local path leakage.
- Avoid unbounded local processing on untrusted or malformed Office/PDF files.
- Make setup and degradation behavior explicit for teams with different Python, proxy, LibreOffice, OCR, or markdown-extraction environments.
- Preserve object-heavy Excel evidence that normal openpyxl parsing cannot represent, especially SAP screenshots, flowcharts, connectors, and DrawingML shapes.
- Reduce Windows-specific release risk for teams that have Microsoft Excel installed but not LibreOffice.
- Keep one malformed or mislabeled workbook from invalidating a multi-workbook heavy Vision validation run.
- Avoid false-positive orchestration results when a workbook is fail-soft rather than truly processed.
- Avoid underselling the skill as Excel-only now that it covers Office-wide specification packages.

## Validation Results

- Syntax check: PASS
  - Command: `<python> -m py_compile runtime/pipeline.py scripts/run_pipeline.py scripts/export_visuals.py scripts/ocr_runner.py scripts/smoke_test.py`
- Smoke test: PASS
  - Command: `<python> scripts/smoke_test.py`
  - Result: exit `0`; core imports passed; optional missing dependencies were reported, not hidden; malformed `.xlsx` fail-soft regression passed; Windows Excel automation is `not_applicable` on this macOS run.
- Malformed `.xlsx` pipeline regression: PASS
  - Command: `<python> scripts/run_pipeline.py --input-path <directory_with_non_ooxml_xlsx> --output-root <output_root> --no-ocr`
  - Result: exit `0`; standard artifacts were written; `status_code: blocked_non_ooxml_container`, `vision_status: blocked_non_processable_workbook`, `workbook_extraction_status: failed`, and `vision_readiness_status: blocked` were recorded.
- Visual workbook queue regression: PASS
  - Command: `<python> scripts/smoke_test.py`
  - Result: processable workbook with raw media generated at least one queued Vision task and `vision_status: ready`.
- RPC Excel sample run: PASS
  - Command: `<python> scripts/run_pipeline.py --input-path <rpc RPA-184 xlsx> --output-root <output_root> --no-ocr`
  - Result: exit `0`; 53 media entries, 9 drawing XML files, 200 shapes, 22 connectors, and 113 Vision queue tasks were recorded; the workbook is `processed` and Vision readiness is `partial_ready_with_blocked_assets` on macOS without a render backend.
- Missing input failure check: PASS
  - Command: `<python> scripts/run_pipeline.py --input-path <missing_input> --output-root <output_root>`
  - Result: exit `2`; output root was not created.
- Mixed Office sample run: PASS
  - Command: `<python> scripts/run_pipeline.py --input-path <sample_input> --output-root <sample_output>`
  - Result: exit `0`; required artifacts existed.
- Windows Excel automation script static check: PASS
  - Command: `<python> -c "from runtime.pipeline import _excel_powershell_script; ..."`
  - Result: PowerShell script contains Excel COM creation, PDF export, and `.xlsx` SaveAs branches.
- Standalone visual export script: PASS
  - Command: `<python> scripts/export_visuals.py --workbook <sample_input>/sample.xlsx --output-dir <visual_output>`
  - Result: exit `0`; log written; no absolute workbook/output path in log.
- Standalone OCR script: PASS
  - Command: `<python> scripts/ocr_runner.py --visual-root <sample_output>/visual_exports --ocr-output <ocr_output> --backend local`
  - Result: exit `0`; OCR JSON written with `success` via Tesseract CLI fallback because `pytesseract` is unavailable in this environment.
- Artifact existence checklist: PASS
  - `file_inventory.md`, `workbook_inventory.md`, `document_inventory.md`, `extracted_markdown/`, `visual_exports/`, `ocr_results/`, `deep_reading_notes/`, `final_summary.md`, and `structured_data.json` all existed.
- Absolute-path leak check: PASS
  - Command: absolute-path scan over `<sample_output>`
  - Result: no matches.
