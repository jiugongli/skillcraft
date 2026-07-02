---
name: "agent-continuity"
description: "Use when a long-running agent task needs continuity across context resets, agent restarts, or takeover by another agent. Supports proactive checkpointing during healthy execution and emergency rescue handoff when an agent is stalled, drifting, looping, over-context, or timing out. Produces or updates handoff.md so a new agent can continue without relying on hidden conversation context."
---

# Agent Continuity

This skill externalizes task state into `handoff.md`. It is not multi-agent orchestration and not background-agent management. It is for preserving continuity when one agent may need to stop and another agent must resume safely.

## Modes

### 1. Checkpoint Mode

Use when the current agent is still healthy, but the task is long, context is growing, or the user wants restartability.

Goal: update `handoff.md` after meaningful progress, usually every 1-2 steps.

Rules:

- Record confirmed state, not vague memory.
- Keep the next step minimal and executable.
- Include evidence: file paths, commands, outputs, decisions.
- Do not expand scope while checkpointing.
- Preserve important history; do not overwrite blockers or do-not-retry notes.

### 2. Rescue Mode

Use when the current agent is stalled, drifting, looping, over-context, timing out, or no longer safe to continue.

Goal: within 90 seconds, recover enough state for a fresh agent to continue.

Rules:

- Read `handoff.md` first. If missing, create a minimal one.
- Read only directly relevant files and files referenced by `handoff.md`.
- Pick exactly one safe highest-priority action that can be done within 90 seconds.
- Execute that action, or record the blocker once.
- Do not run long commands, broad searches, or retry loops.
- Do not perform destructive operations.
- Update `handoff.md` before stopping.

## Required Handoff File

Default path: `handoff.md` at the task root unless the user specifies another path.

Use the structure in `references/handoff-template.md`.

Required properties:

- Starts with a status label: `READY TO CONTINUE`, `NEEDS REVIEW`, or `BLOCKED ON <specific blocker>`.
- Every major claim includes evidence or is marked `Assumption`.
- Contains one highest-priority next step and three minimal next steps.
- Contains do-not-retry guidance for failed actions.
- Ends with a 15-second quick resume note.

## Operating Procedure

1. Identify mode: Checkpoint or Rescue.
2. Locate or create `handoff.md`.
3. Read only enough context to update it accurately.
4. Update the handoff using the required structure.
5. If code or files changed, include exact paths and verification status.
6. If blocked, record the blocker, likely cause, and safest next action.

## References

- `references/handoff-template.md`: canonical handoff structure.
- `references/checkpoint-mode.md`: prompt and rules for proactive checkpointing.
- `references/rescue-mode.md`: prompt and rules for emergency rescue.
- `references/comparison-notes.md`: why this differs from multi-agent handoff and background-agent management.

## Scripts

- `scripts/validate_handoff.py`: validates that a `handoff.md` contains the required sections.
