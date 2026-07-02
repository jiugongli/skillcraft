# Handoff Quality Validator Candidate

Mode: `candidate_only`

## Purpose

Use `agent-continuity` validation for real continuity handoffs, while avoiding false failures on Cursor handoffs, usage guides, templates, and handoff-like docs.

## Classification Rules

| Kind | Required Signals | Validator |
|---|---|---|
| agent_continuity_handoff | `## Status`, `## Next Minimal Step`, `## Quick Resume`, not under `references/` | `skillcraft/skills/agent-continuity/scripts/validate_handoff.py` |
| cursor_handoff | filename or path contains `cursor` | classify and index only |
| usage_handoff_or_guide | title says guide, install/run instructions dominate | classify and index only |
| template_or_reference | under `references/` or contains placeholders | exclude from live handoff counts |
| handoff_like | file name matches handoff but schema unknown | index and inspect manually |

## Repair Rules

- If a live agent-continuity handoff fails status prefix, propose changing status to one of:
  - `READY TO CONTINUE`
  - `NEEDS REVIEW`
  - `BLOCKED ON <specific blocker>`
- If sections are missing, generate a patch candidate with missing headings.
- Do not auto-edit project handoffs without user confirmation.

## Evidence From This Run

- `<project-root>/source-lingo/handoff.md` failed current validator because its status does not start with the required prefix.
- `skills/agent-continuity/references/handoff-template.md` matched the structural pattern but is a template/reference and should not be counted as a live project handoff.
- Cursor handoffs under `<project-root>/source-lingo/docs/agent-workflow/` should be collected as implementation evidence, not validated as agent-continuity handoffs.
