# Troubleshooting

## `python` command cannot run

Symptoms:

- `python` returns launcher error or command not found.
- smoke test reports missing core package such as `openpyxl`.

Actions:

1. verify interpreter path
2. activate the intended virtual environment or run with an explicit executable path
3. install requirements into that exact interpreter
4. re-run `smoke_test.py` and `run_pipeline.py`

## Dependency install fails behind proxy or offline

Symptoms:

- `pip install` cannot reach PyPI.
- packages time out or fail TLS/proxy checks.

Actions:

1. use the company-approved package mirror, proxy, or wheelhouse
2. retry with `--no-index --find-links "<wheelhouse_dir>"` when using offline wheels
3. keep the install command in the handoff notes so another team can reproduce it

## Input path fails immediately

Symptoms:

- `run_pipeline.py` exits with `input path does not exist`.

Actions:

1. verify the path in the same shell/session that runs the script
2. avoid relying on shell aliases or unmapped network drives
3. create the output directory separately from the input directory

## `markitdown` not found

Symptoms:

- markdown extraction status is `skipped` or `failed`.
- log mentions `markitdown CLI` or `python -m markitdown`.

Actions:

1. install MarkItDown into the same Python environment used to run the pipeline
2. prefer `python -m pip install "markitdown[all]"`
3. rerun pipeline or markdown stage

## Visual export missing PDF

Symptoms:

- no sheet PDF export output.
- `ocr_results/vision_queue.jsonl` contains `blocked_missing_render_backend`.

Actions:

1. verify `soffice` availability, or on Windows verify Microsoft Excel is installed
2. on Windows, run `smoke_test.py` and check `powershell`, `module:win32com`, and `windows_excel_automation`
3. confirm LibreOffice/Excel can open the source file manually if conversion keeps failing
4. keep embedded-image extraction as fallback where available
5. review `workbook_inventory.md` visual preflight counts for shapes/connectors/unsupported media
6. log warning and affected workbook

## OCR outputs empty

Symptoms:

- OCR files exist but texts are empty or weak.

Actions:

1. check OCR backend and language data
2. if `pytesseract` is unavailable, verify the `tesseract` executable is installed and visible
3. increase export resolution before OCR
4. split large visuals into tiles and rerun

## Workbook parse failure

Symptoms:

- workbook has warnings in analysis output.
- `.xlsx` warning says `File is not a zip file` or `not an OOXML ZIP container`.
- `workbook_inventory.md` or `structured_data.json` shows `status_code: blocked_non_ooxml_container`.

Actions:

1. record exact file and failure reason
2. check whether the file is encrypted, a legacy `.xls` renamed to `.xlsx`, HTML saved with `.xlsx`, or corrupt
3. on Windows, verify Excel can open the file and let the pipeline attempt PDF export through Excel automation
4. treat `pipeline_execution_status: success` as runtime success only; check `workbook_extraction_status` and `vision_readiness_status` before release validation
5. continue processing remaining files
6. mark summary sections as `不确定` where evidence is missing

## Duplicate-looking artifact names

Symptoms:

- output files include source extension and an 8-character hash.

Explanation:

- this is expected hardening behavior; it prevents `sample.xlsx`, `sample.docx`, and `folder/sample.xlsx` from overwriting each other.
