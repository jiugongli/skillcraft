# Output Template

Use this as a consistency template for `final_summary.md`.

`final_summary.md` is a navigation aid. It must not be the only place where detailed evidence exists.

## <office_file_name>

- file name:
- extraction status:
- encoding/readability status:
- file purpose:
- business/system/document scope:
- major sheets / sections / slides:
- key process or document structure:
- inputs:
- outputs:
- systems/screens/forms/documents mentioned:
- action-bearing statement candidates:
  - read/query/search:
  - input/set:
  - select/click/navigation:
  - save/register/update/delete:
  - copy/move/archive:
  - download/export/print/PDF:
  - send/notify:
  - branch/loop/wait:
  - error/exception:
  - external-system handoff:
- data/table/field candidates:
- branch conditions:
- exception handling:
- visual evidence summary:
- unconfirmed or uncertain items:
- confidence:

## Required Ledgers For High-Fidelity / Lossless Extraction

- content ledger:
  - every meaningful cell/paragraph/shape/OCR text has a source anchor.
- action-bearing statement ledger:
  - every possible action signal is listed with source anchor and concrete context.
  - the ledger extracts and anchors candidate statements; it does not interpret business meaning.
- context ledger:
  - screen/window/form/section context spans are listed with start/end anchors.
  - uncertain boundaries are marked as `不确定`.
- coverage report:
  - detected source unit count, extracted count, visual object count, OCR/Vision queued count, skipped count, unresolved failure count.
  - material detected-vs-extracted count mismatches are explicitly reported.

## Traceability Checklist

- Every critical conclusion has at least one source pointer:
  - workbook/sheet/cell, or
  - document section/table/slide/note, or
  - visual export page/region plus OCR/Vision result.
- Inferences are explicitly marked as `推定`.
- Unclear points are explicitly marked as `不确定`.
- No unresolved parse failure is silently omitted.
- No summary claim is accepted if it cannot resolve to an anchor in the content ledger.
- No high-confidence summary is allowed if important text is mojibake, mixed/ambiguous in encoding, visually unreviewed, truncated, or only partially covered.
