# FAQ

## Q1. Can this skill run in any repository?

Yes. Runtime is bundled under `runtime/`, so scripts do not depend on repository-specific `tools/` paths.

## Q2. Is `markitdown` mandatory?

No. If missing, markdown extraction is logged as skipped, and other stages continue.

## Q2-0. Should I keep MarkItDown enabled?

Yes for normal runs. It gives a broad first-pass Markdown view for arbitrary Office files. Do not use it as the only evidence source for screenshots, DrawingML shapes, connectors, or visual layouts.

## Q2-1. Why can markitdown fail even when installed?

Some file converters are optional extras in MarkItDown.
If `.xlsx` or `.docx` markdown extraction fails, install:

```bash
python -m pip install "markitdown[all]"
```

## Q3. How is `.xls` handled?

The pipeline attempts `.xls -> .xlsx` conversion via LibreOffice (`soffice`) first. On Windows it can fall back to Microsoft Excel automation through `pywin32` or PowerShell COM.
If conversion is unavailable, it logs warnings and marks uncertainty.

## Q3-1. How are `.doc` and `.ppt` handled?

They use the same legacy conversion pattern via LibreOffice:

- `.doc -> .docx`
- `.ppt -> .pptx`

The runtime checks common `soffice` locations on macOS, Windows, and PATH. If LibreOffice is unavailable or conversion fails, the document is still listed, but deep structure extraction is limited and warnings are written.

## Q4. Why are OCR results weak?

Likely image quality, language model data, or OCR backend setup. See `troubleshooting.md`.

## Q4-0. Should visuals always go to an LLM Vision model?

That is an operator decision. Use local OCR when token budget or speed matters. Use `--no-ocr` plus `ocr_results/vision_queue.jsonl` when completeness and visual understanding matter more than cost or latency.

## Q4-1. Do I need `soffice` and `tesseract`?

Recommended, not always mandatory:

- `soffice`: improves legacy conversion (`.xls/.doc/.ppt`) and PDF export
- Windows Microsoft Excel: can export workbook PDFs and convert `.xls` when `soffice` is unavailable
- `tesseract`: enables local OCR extraction

The Python package `pytesseract` is preferred for local OCR, but the runtime falls back to the `tesseract` executable. The runtime checks common `tesseract` locations on macOS, Windows, and PATH. If both OCR paths are unavailable, OCR result files use `skipped` or `failed` status.

## Q5. What is the minimum output set to share with stakeholders?

At least:

- `file_inventory.md`
- `workbook_inventory.md`
- `deep_reading_notes/`
- `final_summary.md`
- `structured_data.json`

## Q6. Where should I check quality before delivery?

Use `checklist.md` and validate all required fields in `final_summary.md`.

## Q7. Why do output filenames contain hashes?

Hashes prevent collisions when different source files share a basename, such as `sample.xlsx`, `sample.docx`, and `subdir/sample.xlsx`.

## Q8. Do result artifacts include absolute local paths?

No. Shared outputs use relative source paths and relative output artifact paths to avoid leaking local usernames, mount points, or customer folder structure outside the agreed input scope.
