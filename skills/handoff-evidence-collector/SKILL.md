---
name: handoff-evidence-collector
description: Collect, classify, and validate local handoff files across Codex, Cursor, and project directories as evidence for continuation, audits, skill evolution, and project status. Use when the user says handoffs can be collected, mentions agent-continuity handoff, asks to audit project continuity, or wants Codex to learn from Cursor/Codex handoff files under project roots supplied by the user.
---

# Handoff Evidence Collector

## Goal

Turn scattered `handoff.md`, `*handoff*.md`, Cursor handoff docs, and agent-continuity handoffs into a usable evidence index without rewriting project files.

## Inputs

- Project roots supplied with `--root`; if omitted, the scanner defaults to the current working directory. `HANDOFF_EVIDENCE_ROOTS` may provide an `os.pathsep`-separated root list.
- Known continuity tooling, especially the sibling `skills/agent-continuity/scripts/validate_handoff.py` validator in this repository.
- User-provided project priority or time range.

## Workflow

1. Bounded scan:
   - walk only approved project roots;
   - skip `.git`, `node_modules`, model/checkpoint/cache/data/output directories;
   - cap depth unless the user approves a deeper scan.
2. Classify each handoff:
   - `agent_continuity_handoff`;
   - `cursor_handoff`;
   - `usage_handoff_or_guide`;
   - `handoff_like`;
   - `template_or_reference`.
3. Validate only true `agent_continuity_handoff` files with the project validator.
4. Keep non-continuity handoffs as evidence, but do not fail them against the continuity template.
5. Output a Markdown inventory and JSON index with path, kind, mtime, validation status, and recommended next action.

## Bundled Resources

- `scripts/handoff_inventory.py`: bounded scanner/classifier for user-supplied roots or the current workspace.
- `scripts/validate_artifact_quality.py`: local artifact quality validator used after inventory generation.
- `references/handoff_quality_validator.md`: classification and repair rules for handoff files.
- `references/artifact_quality_validator.md`: scoring table for output quality.
- `references/artifact_quality_schema.json`: JSON schema for validator output.

## Smoke Test

Run from the `skillcraft` repository root or another writable workspace:

```sh
python3 skills/handoff-evidence-collector/scripts/handoff_inventory.py --output-root /tmp/handoff-evidence-smoke-output --root .
python3 skills/handoff-evidence-collector/scripts/validate_artifact_quality.py /tmp/handoff-evidence-smoke-output/Handoff_Inventory.md
```

Execution mode: `real_execution` for the local scan and validator commands. The scanner is read-only against source project roots and writes only to the requested output root. If a future run uses mock, fixture, dry-run, or candidate-only data, label that explicitly in the inventory.

Expected:

- finds handoff-like files under the supplied roots;
- validates true agent-continuity handoffs only;
- writes JSON/Markdown inventory to the configured output root;
- does not edit project files.

## Output Contract

- `handoff_inventory.json`
- `Handoff_Inventory.md`
- validation results for agent-continuity handoffs
- repair candidates for failed handoffs
- skip list for templates/reference guides

## Evidence Handling

Use repo-relative paths, generated inventory paths, validator stdout/stderr, and explicit `evidence_missing` markers when source roots are unavailable or unreadable.

References: use `references/handoff_quality_validator.md` for classification rules, `references/artifact_quality_validator.md` for output-quality scoring, and `references/artifact_quality_schema.json` for machine-readable validator output.

Concrete local evidence examples include `skills/handoff-evidence-collector/scripts/handoff_inventory.py`, `skills/agent-continuity/scripts/validate_handoff.py`, `handoff_inventory.json`, and `Handoff_Inventory.md`.

## Completion Criteria

- Every collected file has a kind.
- Every true agent-continuity handoff has validator output.
- Templates are not counted as live project handoffs.
- Cursor handoffs are preserved as evidence but not forced into the agent-continuity schema.

## Failure Recovery

- If scan is too slow, stop and switch to max-depth bounded scanning.
- If a handoff fails validation, generate a patch candidate, not an automatic edit.
- If a project root is huge or unreadable, mark it as `scan_limited` or `permission_denied`.
