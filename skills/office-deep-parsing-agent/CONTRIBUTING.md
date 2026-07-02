# Contributing

Thanks for improving this skill.

## Scope

Contributions are welcome for:

- parsing accuracy
- output traceability
- OCR/visual robustness
- docs and onboarding quality

## Contribution rules

1. Keep `SKILL.md` concise. Put details in companion files.
2. Preserve output artifact contracts.
3. Do not silently skip failures; log impact.
4. Do not log absolute local paths, secrets, or full environment dumps in shared artifacts.
5. Preserve unique artifact naming for same-basename source files.
6. Update `CHANGELOG.md` and `VERSION` on meaningful changes.

## Recommended validation

1. Run:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/smoke_test.py
```

2. Run a small pipeline case:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py --input-path "<input_path>" --output-root "<output_root>"
```

3. Verify final outputs with [`checklist.md`](checklist.md).

4. Confirm failure signaling:

```bash
python .cursor/skills/office-deep-parsing-agent/scripts/run_pipeline.py --input-path "<missing_path>" --output-root "<output_root>"
```

Expected: non-zero exit with a clear error and no empty success artifact set.
