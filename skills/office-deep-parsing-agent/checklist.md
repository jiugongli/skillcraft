# QA Checklist (Cross-Team)

Use this checklist to keep delivery quality consistent across teams.

## Before Run

- [ ] Input scope is explicit (single file / directory / recursive scope).
- [ ] Output root path is agreed.
- [ ] Input path exists before execution.
- [ ] Output root is separate from the input directory, or generated output exclusion is acknowledged.
- [ ] Python runtime and dependency source are explicit (venv, internal mirror, or wheelhouse).
- [ ] MarkItDown policy is explicit: default enabled, or intentionally disabled for a scoped test.
- [ ] Visual recognition policy is explicit: local OCR, LLM Vision via `vision_queue.jsonl`, or both.
- [ ] Required outputs are confirmed:
  - [ ] `file_inventory.md` or `file_inventory.csv`
  - [ ] `workbook_inventory.md`
  - [ ] `document_inventory.md`
  - [ ] `extracted_markdown/`
  - [ ] `visual_exports/`
  - [ ] `ocr_results/`
  - [ ] `ocr_results/vision_queue.jsonl`
  - [ ] `deep_reading_notes/`
  - [ ] `final_summary.md`
  - [ ] `structured_data.json`
- [ ] Environment probe result is recorded (python / markitdown / OCR / optional visual-export backend).
- [ ] Failure logging policy is clear (no silent skip).
- [ ] Shared artifacts do not expose absolute local paths, secrets, or environment dumps.

## During Run

- [ ] File inventory includes processed/skipped state and skip reasons.
- [ ] Archive files are recorded as pending (if not expanded by scope).
- [ ] Same-named files in different folders or with different extensions produce distinct artifact names.
- [ ] Workbook structure extraction includes:
  - [ ] sheet order
  - [ ] hidden sheets
  - [ ] merged ranges
  - [ ] formulas and cached values (if available)
  - [ ] comments/hyperlinks
  - [ ] named ranges
  - [ ] validations/conditional formatting
  - [ ] charts/images/shapes/object signals
  - [ ] visual preflight counts for media, DrawingML, shapes, connectors, unsupported media
- [ ] Word/PPT extraction includes:
  - [ ] section/paragraph or slide text
  - [ ] table or note extraction when available
  - [ ] image signals
- [ ] Visual-heavy sheets are exported to raw media/contact sheets/PDF/PNG when layout is needed and the backend exists.
- [ ] OCR/Vision results or queued Vision tasks are mapped to workbook/sheet/page/region.
- [ ] Any parse/tool failure is logged with affected file scope.

## High-Fidelity / Lossless Extraction Gate

Use this gate when the input has dense instruction tables, requirement/test matrices, repeated step rows, visual annotations, or enough structure that a short summary could hide important details.

- [ ] `final_summary.md` is treated only as a summary; detailed source evidence exists elsewhere.
- [ ] A content ledger exists or is clearly identified in `structured_data.json` or another output.
- [ ] The content ledger can recover all non-empty cells, merged ranges, formulas/cached values, comments, hyperlinks, validation signals, shape text, image references, OCR text, and visual anchors where available.
- [ ] A coverage report exists and compares detected source units against extracted source units.
- [ ] Material detected-vs-extracted count mismatches are explicitly reported.
- [ ] Encoding/readability is checked, including mojibake, mixed/ambiguous encoding, and CJK text under non-CJK locale assumptions.
- [ ] An action-bearing statement ledger exists when action signals are detected.
- [ ] The action-bearing statement ledger extracts and anchors candidate statements only; it does not interpret business meaning or domain ownership.
- [ ] Candidate statements include read/query/search, input/set, navigation, save/register/update/delete, copy/move/archive, download/export/print/PDF, send/notify, branch/loop/wait, error/exception, and external-system handoff when present.
- [ ] A context ledger exists when rows/pages appear to share a screen/window/form/document/section context.
- [ ] Context boundaries are concrete: same section heading, row group, merged region, repeated screen title, visual region, or table block.
- [ ] Context spans continue until an explicit context change, close, reset, return, new heading, or uncertain boundary.
- [ ] No process is summarized only up to its first visible action when later rows in the same concrete context contain save/update/download/error handling.
- [ ] Visual annotations such as arrows, callouts, highlighted buttons, screenshots, and embedded UI images are linked to nearby rows/cells or marked as unresolved.
- [ ] Any "read-only", "no update", "no download", or "not in scope" statement has been checked against counter-signals in the same concrete context.
- [ ] Every summary claim resolves to an anchor in the content ledger.
- [ ] Confidence is not marked high when major sheets, visual objects, source-unit counts, action-bearing statements, or summary anchors remain unreviewed.

## After Run

- [ ] `final_summary.md` exists and each target Excel includes:
  - [ ] file name
  - [ ] file purpose
  - [ ] business/system scope
  - [ ] major sheets
  - [ ] key process flow
  - [ ] input
  - [ ] output
  - [ ] system/screen operations
  - [ ] data update/query/download actions
  - [ ] branch conditions
  - [ ] exception handling
  - [ ] key fields
  - [ ] key OCR/visual conclusions
  - [ ] unconfirmed items
  - [ ] confidence
- [ ] `structured_data.json` includes enough source anchors for traceability.
- [ ] Inferences are marked as `推定`.
- [ ] Unclear points are marked as `不确定`.
- [ ] Conflicting evidence is explicitly listed.
- [ ] No critical conclusion lacks source evidence.
- [ ] No high-confidence conclusion is based on a mojibake, truncated, unanchored, or visually unreviewed artifact.

## Release Gate

Only consider the run complete when:

- [ ] All required outputs exist.
- [ ] Artifact names can be mapped back to source rows in `file_inventory.md` / `structured_data.json`.
- [ ] Major failures are either fixed or explicitly reported with impact.
- [ ] Summary is human-readable (not raw extraction fragments only).
