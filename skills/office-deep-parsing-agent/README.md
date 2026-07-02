# office-deep-parsing-agent

Portable Cursor Skill for deep Office analysis with traceable outputs.

Formerly `excel-deep-parsing-agent`. The rename reflects that the skill now handles Office-wide specification packages, not just Excel workbooks. Update local installs and prompts to use `office-deep-parsing-agent`.

## What this skill does

- Deep parse Office files (`.xlsx/.xlsm/.xls/.csv/.docx/.doc/.pptx/.ppt`)
- Run MarkItDown as a default first-pass Markdown extractor when available
- Inspect spreadsheet workbook/sheet/cell structures (including hidden sheet/object signals)
- Preflight Excel `xl/media` and DrawingML so shape/object-heavy sheets are flagged instead of silently flattened
- Inspect Word/PPT structures (paragraphs/tables/slides/notes/image signals)
- Export visual artifacts (raw embedded media, contact sheets, PDF/PNG when available)
- Run OCR over visual exports
- Produce `ocr_results/vision_queue.jsonl` for screenshots, flowcharts, sheet renders, and blocked visual follow-up
- Produce human summary and machine-readable JSON
- Report workbook extraction and Vision readiness status separately so fail-soft runs are visible to orchestrators

## Directory

```text
office-deep-parsing-agent/
├── SKILL.md
├── reference.md
├── examples.md
├── output_template.md
├── troubleshooting.md
├── checklist.md
├── handoff.md
├── FAQ.md
├── CHANGELOG.md
├── VERSION
├── CONTRIBUTING.md
├── LICENSE
├── runtime/
│   ├── __init__.py
│   ├── executables.py
│   └── pipeline.py
└── scripts/
    ├── run_pipeline.py
    ├── export_visuals.py
    ├── ocr_runner.py
    ├── smoke_test.py
    └── requirements.txt
```

## Quick start

Use a virtual environment or other Python runtime that already has the required packages. `openpyxl` is the only core package for spreadsheet parsing; the rest improve markdown, document, visual, and OCR coverage.

Install dependencies:

```bash
python -m pip install -r .cursor/skills/office-deep-parsing-agent/scripts/requirements.txt
```

If the network is restricted, install from an internal mirror or wheelhouse, for example:

```bash
python -m pip install --no-index --find-links "<wheelhouse_dir>" -r .cursor/skills/office-deep-parsing-agent/scripts/requirements.txt
```

Smoke test:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/smoke_test.py
```

Full run:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py --input-path "<input_path>" --output-root "<output_root>"
```

Operator choices:

- Keep MarkItDown enabled by default for broad first-pass text extraction.
- Use `--no-markitdown` only for isolated visual/export regression tests or when the dependency is intentionally unavailable.
- Use local OCR when speed/cost matters and OCR quality is acceptable.
- Use `--no-ocr` when visuals should be handed to an LLM Vision workflow through `ocr_results/vision_queue.jsonl`.

## Known limitations

- File type handling is extension-driven first, then parser-validated. Unsupported or corrupt files are reported with warnings instead of treated as success.
- Malformed, encrypted, corrupt, or extension-mismatched `.xlsx` files can fail soft. Check `status_code` for values such as `blocked_non_ooxml_container` before treating a run as fully extracted.
- `markitdown` is a useful first-pass extractor, not the source of truth for screenshots, shapes, connectors, or object-heavy sheets.
- `markitdown` base install may not include all format extras (`xlsx`, `docx`), so markdown extraction can fail for some files while deep parsing still continues.
- `.xls` can be converted through LibreOffice or Windows Microsoft Excel automation. `.doc/.ppt` still require LibreOffice conversion before deep parsing.
- Full workbook/sheet PDF export uses LibreOffice first, then Windows Microsoft Excel automation when available. Without either renderer, embedded-image extraction, DrawingML preflight, shape text sampling, contact sheets, and explicit Vision queue entries still run where possible.
- Local OCR uses `pytesseract` when installed, then falls back to the `tesseract` executable. The runtime checks common `tesseract` locations on macOS, Windows, and PATH. If both paths are unavailable, OCR artifacts record a skipped status.
- Scripts are cross-platform Python, but example paths may use Windows `D:/...` because many source design packages are Windows-authored.
- Runtime output avoids absolute source paths in result artifacts. Use the original command line or file inventory root to map relative paths back to local files.

Recommended optional setup:

```bash
python -m pip install "markitdown[all]"
```

On Windows, installing requirements includes `pywin32`; if it is unavailable, the runtime falls back to PowerShell COM for Excel PDF export/conversion.

## Output artifacts

- `file_inventory.md`
- `workbook_inventory.md`
- `document_inventory.md`
- `extracted_markdown/`
- `visual_exports/`
- `ocr_results/`
  - `vision_queue.jsonl`
- `deep_reading_notes/`
- `final_summary.md`
- `structured_data.json`

Important machine-readable status fields:

- `summary.pipeline_execution_status`: whether the pipeline completed.
- `summary.workbook_extraction_status`: `success`, `partial`, `failed`, or `not_applicable`.
- `summary.vision_readiness_status`: `success`, `partial`, `blocked`, or `not_applicable`.
- `workbook_results[].extraction_status`: `processed`, `fail_soft`, or `unsupported`.
- `workbook_results[].status_code`: for example `processed`, `blocked_non_ooxml_container`, `blocked_conversion_unavailable`, or `unsupported_spreadsheet_extension`.
- `workbook_results[].vision_status`: `ready`, `partial_ready_with_blocked_assets`, `blocked_non_processable_workbook`, `blocked_missing_render_backend`, `blocked_requires_render_or_conversion`, `not_ready`, or `not_needed`.

## Documentation map

- Execution rules: [`SKILL.md`](SKILL.md)
- Full policy text: [`reference.md`](reference.md)
- Practical examples: [`examples.md`](examples.md)
- QA gate: [`checklist.md`](checklist.md)
- Troubleshooting: [`troubleshooting.md`](troubleshooting.md)
- Team handoff: [`handoff.md`](handoff.md)
- FAQ: [`FAQ.md`](FAQ.md)
