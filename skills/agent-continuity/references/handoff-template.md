# Handoff Template

Use this structure for `handoff.md`.

```markdown
# Handoff

## Status
READY TO CONTINUE / NEEDS REVIEW / BLOCKED ON <specific blocker>

## Original Goal
State the user's original task in one or two sentences.

## Current State
- Confirmed fact with evidence: `<file path>`, command result, or output artifact.
- Confirmed fact with evidence.
- Assumption: clearly mark unverified but currently useful assumptions.

## Recent Progress
- Last meaningful step completed.
- Last meaningful step completed.

## Next Minimal Step
One highest-priority action that the next agent should do first.

## Next 3 Steps
1. Minimal executable step.
2. Minimal executable step.
3. Minimal executable step.

## Unfinished Work
### High
- Item, dependency, and verification method.

### Medium
- Item, dependency, and verification method.

### Low
- Item, dependency, and verification method.

## Blockers
- Blocker:
  - Likely cause:
  - Impact:
  - Confidence:
  - Possible workaround:

## Do Not Retry Without New Evidence
- Failed action and why it should not be repeated blindly.

## Files And Artifacts
- Path: purpose / status.
- Path: purpose / status.

## Decisions
- Decision:
  - Reason:
  - Evidence:

## Assumptions
- Assumption:
  - Why it is plausible:
  - How to verify:

## Quick Resume
One short paragraph that a new agent can read in 15 seconds to continue safely.
```

## Quality Bar

- A new agent should be able to act from `Next Minimal Step` without asking for clarification.
- The handoff should be useful even if the old conversation context is unavailable.
- Uncertainty must be explicit.
