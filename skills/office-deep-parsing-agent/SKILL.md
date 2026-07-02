---
name: office-deep-parsing-agent
description: Deeply parses Office files (.xlsx/.xlsm/.xls/.csv/.docx/.doc/.pptx/.ppt), including workbook/cell/object analysis and document structure analysis, and performs visual understanding by exporting pages/sheets to PDF/PNG and applying OCR/Vision to images, screenshots, and flow diagrams. Use when users need traceable business-level interpretation, not just text extraction.
disable-model-invocation: true
---

# Office Deep Parsing Agent

## Purpose

Use this skill when the user wants deep, business-meaningful analysis of Office files, not a shallow text dump.

## Required Behavior

1. Inventory first, then analyze.
2. Run MarkItDown as the default first-pass Markdown extraction when available; do not use it as the source of truth for visual coverage.
3. Parse spreadsheet workbook -> sheet -> cell/range with coordinates.
4. Parse Word/PPT document structure (sections, tables/slide text, notes, image signals).
5. Capture structural elements (hidden sheets, merged cells, formulas, comments, hyperlinks, named ranges, validations, conditional formats, charts, images, shapes, objects).
6. For Excel visuals, preflight the Office ZIP (`xl/media`, DrawingML, anchors, shape text, object names) before relying on parser output.
7. For visual-heavy sheets/pages, export raw media/contact sheets/PDF where available, optionally run local OCR, and write `ocr_results/vision_queue.jsonl` for user-selected Vision/LLM follow-up.
8. Merge all evidence into traceable outputs.
9. Mark uncertainty explicitly (`推定`, `不确定`) instead of guessing.

## High-Fidelity / Lossless Extraction Mode

When an Office file shows structural signals that downstream consumers may need to inspect in detail, prioritize complete, anchored extraction over concise interpretation.

This mode is generic. Do not add SAP, RPA, accounting, medical, legal, or any other domain-specific classifier to this skill. Domain interpretation belongs to a separate downstream agent. This skill must preserve evidence and expose candidate semantics without deciding business meaning too early.

Trigger this mode when one or more of these structural signals are present:

- dense instruction tables, procedure sheets, requirement matrices, test matrices, or handoff tables
- repeated step numbers, row-grouped procedures, sectioned instructions, or branch/error rows
- embedded screenshots, arrows, callouts, highlighted controls, or visual annotations
- many non-empty cells/paragraphs/slides where a short summary could hide important details

Required behavior in this mode:

1. Treat `final_summary.md` as a navigational summary, not the source of truth.
2. Preserve a lossless evidence layer: every non-empty cell, merged range, formula/cached value, comment, hyperlink, validation, shape text, image reference, OCR text, and visual anchor must be recoverable from the outputs.
3. Produce or clearly identify a downstream-ready content ledger with these generic columns where applicable: source file, sheet/section/page, row/column or page region, step number, visible text, normalized text, object kind, nearby heading, visual anchor, extraction method, uncertainty, and notes.
4. Produce an action-bearing statement ledger when action signals are detected. The ledger only extracts and anchors candidate action text; it does not interpret business meaning. Candidate action signals include imperative verbs, state-changing language, read/query/search, input/set, select/click/navigation, save/register/update/delete, copy/move/archive, download/export/print/PDF, send/notify, branch/loop/wait, error/exception, and external-system handoff.
5. Produce a context ledger when rows or pages appear to share a screen, window, form, document, or section context. Use concrete boundaries: same section heading, row group, merged region, repeated screen title, visual region, or table block. Continue the context until an explicit context change, close, reset, return, new heading, or uncertain boundary. If the boundary is unclear, mark it as `不确定`.
6. Produce a coverage report comparing detected source units against extracted units: non-empty cells/paragraphs/slides, merged ranges, images/shapes/objects, OCR/Vision queue items, skipped objects, unresolved parse failures, and any material count mismatch.
7. Do not collapse a process to the first obvious action. Continue extracting until the next major heading, context change, or terminal action.
8. Visual annotations are evidence. Arrows, callouts, highlighted buttons, screenshots, and embedded UI images must be linked back to nearby rows/cells and listed as visual signals, even when OCR is incomplete.
9. A "read-only", "no update", "no download", or "not in scope" conclusion is forbidden unless the same concrete context was checked for counter-signals such as save, register, update, delete, set, input, confirm, execute, issue, output, download, print, error handling, or visual save/export icons.
10. Never report high confidence when key sheets have mojibake, mixed/ambiguous encoding, missing visual extraction, skipped OCR/Vision, unresolved parse failures, material extracted-vs-detected count mismatch, unanchored summary claims, or unreviewed action-bearing statements.
11. If the summary is not human-readable because of encoding damage, the run is not complete. Report encoding damage and repair or regenerate the affected artifact before using it for analysis.

Non-goals:

- Do not classify business meaning.
- Do not infer domain ownership.
- Do not replace downstream domain review.

## Environment Probe and Failure Logging

Before full run, probe required capabilities and record status in logs:

- Python runtime
- markitdown availability
- Excel automation availability on Windows (if needed)
- LibreOffice/soffice availability (if needed)
- OCR backend availability

If a capability is missing:

- do not silently skip
- keep processing with available paths
- write explicit warnings and affected-file scope in intermediate outputs
- do not record absolute local paths or environment secrets in shared artifacts

Input/output safety:

- fail fast when `--input-path` does not exist or is not a regular file/directory
- use a separate output directory; if it is inside the input tree, generated output is excluded from the next inventory pass
- artifact filenames are derived from relative source paths plus a short hash to avoid collisions between same-named files
- legacy `.xls` parsing can use LibreOffice or Windows Microsoft Excel automation; `.doc/.ppt` still depend on LibreOffice conversion
- executable discovery checks PATH plus common macOS and Windows install locations for LibreOffice, PowerShell, and Tesseract

## Standard Workflow

1. Build `file_inventory` for input scope.
2. Run markdown extraction (`markitdown`) per Office file where applicable.
3. Build workbook inventory and document inventory.
4. Export visual pages/regions, embedded media, and contact sheets for OCR/Vision when layout is important.
5. Run local OCR only when the operator wants a cheap/fast OCR pass; otherwise use `--no-ocr` and consume `vision_queue.jsonl` with an LLM Vision workflow.
6. Fuse all evidence and produce final human summary + structured JSON.

## Executable Scripts

Use these scripts as defaults instead of ad-hoc one-liners:

- `scripts/run_pipeline.py`: End-to-end run with environment probe log.
- `scripts/export_visuals.py`: Export workbook visuals (embedded images/PDF).
- `scripts/ocr_runner.py`: OCR pass on visual exports.

These scripts use bundled runtime code under `runtime/` so the skill can be shared across repositories without requiring a project-local parser module.

Install baseline dependencies:

```bash
python -m pip install -r .cursor/skills/office-deep-parsing-agent/scripts/requirements.txt
```

For offline or proxied environments, install from an approved mirror or wheelhouse:

```bash
python -m pip install --no-index --find-links "<wheelhouse_dir>" -r .cursor/skills/office-deep-parsing-agent/scripts/requirements.txt
```

Run full pipeline:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py --input-path "<input_path>" --output-root "<output_root>"
```

Run only visual export:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/export_visuals.py --workbook "<workbook_path>" --output-dir "<visual_output_dir>"
```

Run only OCR stage:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/ocr_runner.py --visual-root "<visual_output_dir>" --ocr-output "<ocr_output_dir>" --backend local
```

## Required Output Set

- `file_inventory.md` (or `file_inventory.csv`)
- `workbook_inventory.md`
- `document_inventory.md`
- `extracted_markdown/`
- `visual_exports/`
- `ocr_results/`
- `ocr_results/vision_queue.jsonl`
- `deep_reading_notes/`
- `final_summary.md`
- `structured_data.json`

For high-fidelity / lossless extraction, also produce or clearly identify equivalent downstream-ready ledgers:

- content ledger: all extracted text/objects with stable source anchors
- action-bearing statement ledger: candidate actions and possible read/input/save/update/download/error signals without domain interpretation
- context ledger: inferred screen/window/form/section context spans with uncertainty
- coverage report: detected-vs-extracted counts and unresolved failures

These ledgers may be composed by the agent from pipeline outputs such as `structured_data.json`, visual exports, OCR/Vision queues, and summary artifacts. They are required deliverables for the skill run, but they are not necessarily emitted as separate files by `scripts/run_pipeline.py` alone.

## Final Summary Minimum Fields (Per Workbook)

- file name
- file purpose
- business/system scope
- major sheets
- key process flow
- input
- output
- system/screen operations
- data update/query/download actions
- branch conditions
- exception handling
- key fields
- key OCR/visual conclusions
- unconfirmed items
- confidence

## Quality Bar

- Accuracy before speed.
- Do not rely on one tool.
- Do not ignore images/objects.
- Keep conclusions traceable to workbook/sheet/cell or visual page/region.
- If parse fails, explain reason and impact.
- Keep extraction and interpretation separate. Downstream agents may classify business meaning; this skill must first make the source document fully inspectable.
- Completeness beats elegance for dense or procedural documents. A long but anchored ledger is preferred over a short summary that hides steps.
- A summary that omits action-bearing statements present in the evidence is a quality failure, even if raw cell extraction exists elsewhere.
- Do not mark confidence as high if required evidence is garbled, visually unreviewed, truncated, unanchored, or only partially covered.

## Additional Reference

For full detailed policy text, read [reference.md](reference.md) and apply it directly.

Practical companion files:

- [README.md](README.md)
- [examples.md](examples.md)
- [output_template.md](output_template.md)
- [troubleshooting.md](troubleshooting.md)
- [checklist.md](checklist.md)
- [handoff.md](handoff.md)
- [FAQ.md](FAQ.md)
- [CHANGELOG.md](CHANGELOG.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
