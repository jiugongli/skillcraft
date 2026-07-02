# Review Report

## Findings

### Critical

No Critical findings remained after review.

### High

#### H-1 Missing input path returned a successful empty run

- File path: `scripts/run_pipeline.py`, `runtime/pipeline.py`
- Risk: A typo, missing mount, or unavailable network share could produce a complete-looking artifact set with empty inventories and summaries. Downstream teams could treat a failed parse as a successful release output.
- Reproduction: before the fix, running `python scripts/run_pipeline.py --input-path <missing_input> --output-root <output_root>` exited `0` and wrote empty success artifacts.
- Fix applied: `PipelineConfig.normalize()` now validates that input exists and is a regular file or directory. `run_pipeline.py` returns exit code `2` on validation failure and does not create an empty output artifact set.

#### H-2 Same-basename inputs overwrote traceability artifacts

- File path: `runtime/pipeline.py`
- Risk: Files such as `sample.xlsx`, `sample.docx`, and `sample.pptx` wrote to overlapping names like `deep_reading_notes/sample.md` and shared visual/OCR stems. This caused evidence loss and broke source-to-output traceability.
- Reproduction: before the fix, the mixed Office sample produced only one `deep_reading_notes/sample.md` for three Office files.
- Fix applied: artifact names now use the relative source path plus an 8-character SHA-256 prefix fragment, for example `sample.xlsx__c7ad6cd5.md`. Markdown, visual export, attachment staging, OCR, and deep-reading outputs use collision-safe names. OCR JSON filenames also include the relative visual export path hash so same-named exports in different folders do not overwrite each other.

#### H-3 Malformed or mismatched `.xlsx` aborted the full pipeline during visual export

- File path: `runtime/pipeline.py`, `scripts/smoke_test.py`, `troubleshooting.md`
- Risk: A real workbook with `.xlsx` extension but non-OOXML content could stop before `workbook_inventory.md`, `structured_data.json`, and `ocr_results/vision_queue.jsonl` were written. This made mixed workbook validation fail hard instead of preserving per-file evidence.
- Reproduction: Windows heavy-vision rerun on a real `RPA02-2002-0225` workbook exited `2` with `File is not a zip file`; a local malformed `.xlsx` regression reproduced the same vulnerable class.
- Fix applied: openpyxl-based visual export is now fail-soft, container preflight hints classify non-ZIP `.xlsx` inputs, workbook-level visual exports are preserved for Vision queueing even when cell parsing fails, and smoke tests now include a malformed `.xlsx` regression.

#### H-4 Fail-soft workbooks could look like full extraction success to orchestrators

- File path: `runtime/pipeline.py`, `scripts/smoke_test.py`, `README.md`, `troubleshooting.md`
- Risk: An upper-layer validation harness that checked only process exit code `0` could treat a fail-soft workbook as fully extracted, even when the workbook had no usable cell or Vision evidence.
- Reproduction: Windows re-review correctly noted that the fail-soft fix prevented aborts but did not expose a machine-readable unprocessed status.
- Fix applied: workbook outputs now include `extraction_status`, `status_code`, `container_status`, and `vision_status`; `structured_data.json` and `final_summary.md` include summary counters for pipeline execution, workbook extraction, and Vision readiness. Non-OOXML `.xlsx` is explicitly reported as `blocked_non_ooxml_container`, fail-soft workbooks without usable visual evidence are marked `blocked_non_processable_workbook`, and workbooks with mixed queued/blocked visual assets are marked `partial_ready_with_blocked_assets`.

### Medium

#### M-1 Shared artifacts exposed absolute local paths

- File path: `runtime/pipeline.py`, `scripts/run_pipeline.py`, `scripts/export_visuals.py`, `scripts/ocr_runner.py`, `scripts/smoke_test.py`
- Risk: Output artifacts leaked local usernames, temporary directories, mount names, and interpreter locations. This is inappropriate for cross-team distribution.
- Reproduction: before the fix, an absolute-path scan over `sample-output-before` found local temporary, home, and mount paths in `structured_data.json`, `pipeline_result_snapshot.json`, inventories, OCR JSON, and `environment_probe.json`.
- Fix applied: pipeline outputs now store relative source paths and relative output artifact paths. Environment probes report availability and Python version, not executable paths. Subprocess logs redact source/output paths.

#### M-2 External tools could run without timeout

- File path: `runtime/pipeline.py`
- Risk: Untrusted or malformed Office files could cause `markitdown` or `soffice` to hang indefinitely. Large PDFs could also create unbounded OCR work.
- Reproduction: static review found `subprocess.run(...)` calls without `timeout=` and PDF OCR iterating over all pages.
- Fix applied: all `markitdown` and `soffice` calls now go through a timeout wrapper with a 120-second limit. PDF OCR is capped at 25 pages and records a skipped residual-pages warning. LibreOffice and Tesseract discovery checks PATH plus common macOS and Windows install locations.

#### M-3 Dependency and offline install behavior were underspecified

- File path: `README.md`, `SKILL.md`, `handoff.md`, `troubleshooting.md`, `scripts/requirements.txt`
- Risk: Teams behind proxies or using a different Python interpreter could fail setup and misread optional dependency absence as runtime failure.
- Reproduction: system `python3 scripts/smoke_test.py` failed because that interpreter lacked `openpyxl`; the bundled Python passed core checks.
- Fix applied: docs now require using the intended interpreter/venv, document mirror and wheelhouse install commands, and separate core parser dependency from optional visual/OCR dependencies.

#### M-4 Legacy Office conversion and OCR degradation were not explicit enough

- File path: `README.md`, `FAQ.md`, `handoff.md`, `reference.md`, `output_template.md`
- Risk: Users could assume `.xls/.doc/.ppt`, PDF export, and OCR always work, even when `soffice`, `tesseract`, `pytesseract`, or `pypdfium2` are missing.
- Reproduction: smoke test in this environment showed `markitdown` and `soffice` missing, and optional OCR modules partially unavailable.
- Fix applied: docs now state the exact fallback behavior for `.xls/.doc/.ppt`, PDF export, markdown extraction, and OCR. The Office-wide extension beyond the original Excel prompt is documented.

#### M-5 Generated bytecode was present in the source zip

- File path: `runtime/__pycache__/`
- Risk: `.pyc` files add noise and can confuse reviewers about source of truth.
- Reproduction: the original zip contained `runtime/__pycache__/pipeline.cpython-312.pyc` and `runtime/__pycache__/__init__.cpython-312.pyc`.
- Fix applied: the hardened release zip is built with `__pycache__/` and `*.pyc` excluded.

#### M-6 Excel DrawingML/object evidence was underreported

- File path: `runtime/pipeline.py`, `README.md`, `SKILL.md`, `troubleshooting.md`
- Risk: Excel sheets containing SAP screenshots, grouped objects, connectors, and flow diagrams could look successfully parsed while openpyxl silently dropped shape/layout semantics.
- Reproduction: RPC workbook `RPA-184-A004-001_RPA少額売上審査.xlsx` contains 53 media parts, 9 drawing XML files, 200 shapes, and 22 connectors; openpyxl warned that DrawingML shapes would be lost.
- Fix applied: added ZIP/DrawingML preflight, raw media export with magic-byte sniffing, contact sheets, drawing object/text samples, explicit render warnings, and `ocr_results/vision_queue.jsonl`.

#### M-7 Windows Excel users still needed LibreOffice for sheet rendering

- File path: `runtime/pipeline.py`, `runtime/executables.py`, `scripts/run_pipeline.py`, `scripts/smoke_test.py`, `scripts/requirements.txt`
- Risk: Windows teams commonly have Microsoft Excel installed but not LibreOffice. Object-heavy workbooks would still miss workbook PDF rendering and stay in `blocked_missing_render_backend`.
- Reproduction: design review of the render path showed workbook PDF export only called `soffice`.
- Fix applied: added Windows Microsoft Excel automation fallback through `pywin32` first and PowerShell COM second for workbook PDF export and `.xls -> .xlsx` conversion.

#### M-8 MarkItDown depended too much on ambient CLI PATH

- File path: `runtime/pipeline.py`, `troubleshooting.md`
- Risk: A virtual environment could have `markitdown[all]` installed while the `markitdown` executable was not visible through PATH, causing markdown first-pass extraction to be skipped or fail unexpectedly.
- Reproduction: Windows feedback identified executable path/environment sensitivity in the heavy-run setup model.
- Fix applied: markdown extraction now tries the discovered CLI first, then falls back to `sys.executable -m markitdown`, keeping the fallback pinned to the active Python environment.

### Low

#### L-1 Markdown table cells were not escaped

- File path: `runtime/pipeline.py`
- Risk: Filenames containing `|` or newlines could corrupt `file_inventory.md` table rendering.
- Reproduction: static review found raw values inserted into Markdown table cells.
- Fix applied: file inventory cells now escape pipes and flatten newlines.

## Release Decision

GO for cross-team distribution after applying this hardening patch.

## Residual Known Limitations

- `markitdown`, `soffice`, `pytesseract`, and `pypdfium2` are optional in the tested environment; missing tools are reported and affected stages degrade instead of failing the whole run. Local OCR can use the `tesseract` executable without `pytesseract`.
- `.xls` deep parsing can use LibreOffice or Windows Microsoft Excel automation; `.doc/.ppt` still depend on successful LibreOffice conversion.
- Mismatched-extension, corrupt, or encrypted `.xlsx` files may still have no cell-level parse; the pipeline now records the reason and continues, and Windows Excel automation may still produce a workbook PDF if Excel can open the file.
- Full sheet rendering of DrawingML layouts requires LibreOffice, Windows Microsoft Excel automation, or another renderer; without one the runtime preserves media/object evidence and queues a blocked render task.
- Archive expansion remains intentionally out of scope; archives are inventoried as pending confirmation.
- File type selection is extension-driven first, then parser-validated by the relevant library.
- The runtime performs local OCR and writes a Vision queue; it does not call an external Vision LLM by itself.

## Verification Evidence

- Smoke test command: `<python> scripts/smoke_test.py`
- Smoke test result: exit `0`; core imports `openpyxl` and `runtime.pipeline` passed; optional `pytesseract`, `pypdfium2`, `markitdown`, and `soffice` were reported missing where applicable; malformed `.xlsx` fail-soft regression passed; `tesseract` executable was available; Windows Excel automation was `not_applicable` on this macOS run.
- Malformed `.xlsx` pipeline regression command: `<python> scripts/run_pipeline.py --input-path <directory_with_non_ooxml_xlsx> --output-root <output_root> --no-ocr`
- Malformed `.xlsx` pipeline regression result: exit `0`; standard artifacts existed; `structured_data.json` recorded `status_code: blocked_non_ooxml_container`, `vision_status: blocked_non_processable_workbook`, `workbook_extraction_status: failed`, and `vision_readiness_status: blocked`.
- Sample pipeline command: `<python> scripts/run_pipeline.py --input-path <sample_input> --output-root <sample_output>`
- Sample pipeline result: exit `0`; processed `sample.xlsx`, `sample.docx`, and `sample.pptx`.
- Windows Excel automation static check: PASS; the generated PowerShell script contains Excel COM creation, PDF export, and `.xlsx` SaveAs branches.
- RPC sample pipeline command: `<python> scripts/run_pipeline.py --input-path <rpc RPA-184 xlsx> --output-root <output_root> --no-ocr`
- RPC sample pipeline result: exit `0`; recorded 53 media parts, 9 drawing XML files, 200 shapes, 22 connectors, and 113 Vision queue tasks. On macOS without a renderer the workbook is `processed` with `vision_status: partial_ready_with_blocked_assets`.
- Artifact checklist result:
  - `file_inventory.md`: OK
  - `workbook_inventory.md`: OK
  - `document_inventory.md`: OK
  - `extracted_markdown/`: OK
  - `visual_exports/`: OK
  - `ocr_results/`: OK
  - `ocr_results/vision_queue.jsonl`: OK
  - `deep_reading_notes/`: OK
  - `final_summary.md`: OK
  - `structured_data.json`: OK
- Privacy check: an absolute-path scan over `sample-output-final` returned no local-path matches.

## Mandatory Files Reviewed

Reviewed: `SKILL.md`, `README.md`, `handoff.md`, `checklist.md`, `troubleshooting.md`, `FAQ.md`, `examples.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `VERSION`, `runtime/pipeline.py`, `scripts/run_pipeline.py`, `scripts/export_visuals.py`, `scripts/ocr_runner.py`, `scripts/smoke_test.py`, and `scripts/requirements.txt`.
