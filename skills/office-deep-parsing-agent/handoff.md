# Handoff Guide

This page is for first-time users of this skill.

## 1) Install

```bash
python -m pip install -r .cursor/skills/office-deep-parsing-agent/scripts/requirements.txt
```

If direct internet access is blocked, use your approved package mirror or wheelhouse:

```bash
python -m pip install --no-index --find-links "<wheelhouse_dir>" -r .cursor/skills/office-deep-parsing-agent/scripts/requirements.txt
```

## 2) Verify environment quickly

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/smoke_test.py
```

## 3) Run the pipeline

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py --input-path "<input_path>" --output-root "<output_root>"
```

Rules:

- `<input_path>` must already exist and must be a file or directory.
- Prefer an output directory outside the input tree.
- Shared artifacts use relative source paths, not absolute local machine paths.
- MarkItDown is enabled by default for first-pass Markdown extraction.
- Choose the visual recognition mode up front: local OCR for speed/cost, or `--no-ocr` plus `ocr_results/vision_queue.jsonl` for LLM Vision review.

## 4) Check expected outputs

- `file_inventory.md`
- `workbook_inventory.md`
- `document_inventory.md`
- `extracted_markdown/`
- `visual_exports/`
- `ocr_results/`
- `deep_reading_notes/`
- `final_summary.md`
- `structured_data.json`

## 5) Quality check before sharing results

Use [`checklist.md`](checklist.md) and ensure all mandatory items are complete.

## 6) If something fails

Start from [`troubleshooting.md`](troubleshooting.md) and keep warnings visible in output artifacts.

## 7) Known limitations to share with users

- `markitdown` base package may miss format extras (`xlsx`, `docx`), causing markdown-only failures.
- MarkItDown is not the source of truth for visual layouts; DrawingML preflight and visual exports still decide whether screenshots/objects need review.
- LibreOffice missing means no `.doc/.ppt` conversion. For spreadsheets, Windows Microsoft Excel automation can still handle `.xls` conversion and workbook PDF export. The runtime checks common `soffice`, PowerShell, and Tesseract locations.
- If both Python `pytesseract` and the `tesseract` executable are missing, OCR outputs are skipped or limited.

Optional reinforcement:

```bash
python -m pip install "markitdown[all]"
```
