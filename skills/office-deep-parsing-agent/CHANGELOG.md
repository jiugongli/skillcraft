# Changelog

## Unreleased - High-fidelity lossless extraction gate

- Added a generic high-fidelity / lossless extraction mode for structurally dense Office files, including procedure sheets, requirement matrices, test matrices, visual annotations, and other documents where summaries can hide important details.
- Kept the skill domain-neutral: no SAP/RPA-specific classifier or business action interpretation is embedded in the Office parser.
- Added requirements for content, action-bearing statement, context, and coverage ledgers so downstream agents can perform domain interpretation without losing source evidence.
- Added quality gates for detected-vs-extracted count mismatches, mojibake or mixed encoding, visual evidence coverage, unreviewed action-bearing statements, and unanchored summary claims.
- Replaced the summary template with a readable, generic template that separates extraction evidence from interpretation.

## 0.3.0 - Rename to Office Deep Parsing Agent

- Renamed the skill from `excel-deep-parsing-agent` to `office-deep-parsing-agent` to match the current Office-wide scope.
- Updated skill metadata, folder path references, README install commands, examples, handoff notes, and runtime comments.
- Kept Excel-heavy Japanese SI specification handling as a primary strength while making Word/PPT and visual evidence support visible in the name.
- Treat this as a breaking path/name change for local installs; update symlinks and scripts from `excel-deep-parsing-agent` to `office-deep-parsing-agent`.

## 0.2.5 - Heavy-validation status semantics

- Added machine-readable workbook extraction status fields: `extraction_status`, `status_code`, `container_status`, and `vision_status`.
- Added summary-level pass criteria counters under `structured_data.json` and `final_summary.md`.
- Marked fail-soft workbooks without usable visual evidence as `blocked_non_processable_workbook` for Vision readiness.
- Marked workbooks with both queued and blocked visual assets as `partial_ready_with_blocked_assets` instead of full Vision readiness success.
- Added explicit `blocked_non_ooxml_container` status for non-OOXML or mismatched-extension `.xlsx` inputs.
- Added smoke regressions for malformed `.xlsx` fail-soft status and processable visual workbook Vision queue generation.
- Updated reports so orchestrators can distinguish pipeline execution success from extraction success and Vision readiness.

## 0.2.4 - Windows heavy-vision fail-soft follow-up

- Fixed malformed or mismatched-extension `.xlsx` files aborting the full pipeline during visual export.
- Added container preflight hints for non-OOXML `.xlsx` inputs, including OLE compound and HTML-like files.
- Preserved workbook-level visual exports in the Vision queue even when cell-level workbook parsing fails.
- Added `python -m markitdown` fallback so MarkItDown can run from the active virtual environment when the CLI is not on PATH.
- Added a smoke regression for malformed `.xlsx` fail-soft handling.

## 0.2.3 - Windows Excel render fallback

- Added Windows Microsoft Excel automation fallback for workbook PDF export when LibreOffice is unavailable.
- Added Windows Microsoft Excel automation fallback for `.xls -> .xlsx` spreadsheet conversion.
- Added PowerShell executable discovery and Windows Excel automation probe entries.
- Added optional Windows-only `pywin32` dependency marker.

## 0.2.2 - RPC visual corpus hardening

- Added Excel ZIP/DrawingML visual preflight for media counts, shape/connectors, object names, and shape text samples.
- Added raw `xl/media` extraction with magic-byte image suffix sniffing, so PNG files with `.tmp` names can still enter OCR.
- Added per-sheet embedded-image contact sheets and `ocr_results/vision_queue.jsonl` for Vision/LLM follow-up.
- Added Tesseract CLI fallback when `pytesseract` is not installed.
- Improved workbook inventory warnings for shape-heavy sheets that require sheet render/PDF for layout semantics.

## 0.2.1 - Release hardening

- Added fail-fast validation for missing or invalid input paths.
- Added collision-safe artifact names based on relative source paths plus short hashes.
- Added collision-safe OCR result names based on relative visual export paths plus short hashes.
- Removed absolute local paths from shared environment, markdown, OCR, and structured result artifacts.
- Added subprocess timeouts for `markitdown` and `soffice` calls.
- Added PDF OCR page cap to avoid unbounded local OCR runs.
- Added cross-platform executable discovery for common LibreOffice and Tesseract install locations.
- Documented offline/proxy dependency installation and legacy Office conversion limits.

## 0.2.0 - Office-wide deep parsing upgrade

- Added Office scope support for `.docx/.doc/.pptx/.ppt` in runtime.
- Added `.xls -> .xlsx` conversion path via LibreOffice for deep spreadsheet parse.
- Added `document_inventory.md` output.
- Upgraded environment probe to include OCR-related modules and executables.
- Upgraded smoke test to core-vs-optional graded checks.

## 0.1.0 - Initial portable release

- Added portable skill runtime under `runtime/`
- Added executable scripts under `scripts/`
  - `run_pipeline.py`
  - `export_visuals.py`
  - `ocr_runner.py`
- Added documentation set:
  - `README.md`
  - `reference.md`
  - `examples.md`
  - `output_template.md`
  - `checklist.md`
  - `troubleshooting.md`
  - `handoff.md`
  - `FAQ.md`
- Added packaging/project files:
  - `VERSION`
  - `CONTRIBUTING.md`
  - `LICENSE`
