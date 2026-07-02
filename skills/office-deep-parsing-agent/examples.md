# Examples

## Smoke Check

Run this first with the same Python interpreter that will run the pipeline:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/smoke_test.py
```

Then confirm arguments resolve:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py --help
```

## Example 1: Single Excel file

Use this when the input is one workbook.

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py \
  --input-path "D:/designs/ZU1A3-D511ACA126.xls" \
  --output-root "D:/analysis/aca126"
```

Expected outputs:

- `file_inventory.md`
- `workbook_inventory.md`
- `extracted_markdown/`
- `visual_exports/`
- `ocr_results/`
- `deep_reading_notes/`
- `final_summary.md`
- `structured_data.json`

## Example 2: Directory (recursive)

Use this when the input includes subfolders with mixed files.

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py \
  --input-path "D:/design-packages/AP-support" \
  --output-root "D:/analysis/ap-support"
```

Notes:

- Inventory must include handled/skipped files and reasons.
- Archive files should be recorded as pending, not silently ignored.

## Example 3: Upload-design focused run

Use this when user asks specifically for upload/download design books.

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py \
  --input-path "D:/design-packages/AP-support" \
  --output-root "D:/analysis/ap-upload" \
  --ocr-backend local
```

Then review:

1. `upload-related` filenames in `file_inventory` / notes
2. `final_summary.md` fields for `Input`, `Output`, `Conditions`, `ExceptionHandling`
3. source traceability in `deep_reading_notes/` and `structured_data.json`

## Example 4: Staged execution (visual + OCR only)

Use this when workbook analysis is already done and only visual understanding must be retried.

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/export_visuals.py \
  --workbook "D:/designs/ZU1A3-D511ACL017.xls" \
  --output-dir "D:/analysis/retry-visuals"
```

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/ocr_runner.py \
  --visual-root "D:/analysis/retry-visuals" \
  --ocr-output "D:/analysis/retry-ocr" \
  --backend local
```

## Example 5: Mixed Office folder (Excel + Word + PowerPoint)

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py \
  --input-path "D:/design-packages/mixed-office" \
  --output-root "D:/analysis/mixed-office"
```

Check both inventories:

- `workbook_inventory.md` for spreadsheet structures
- `document_inventory.md` for Word/PPT structures

If the folder contains `sample.xlsx`, `sample.docx`, and `sample.pptx`, generated deep-reading filenames intentionally include the source extension and a short hash so the three files do not overwrite each other.
