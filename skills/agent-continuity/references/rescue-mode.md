# Rescue Mode

Use this when an agent is stalled, looping, timing out, drifting, or over-context.

## Short Rescue Prompt

```text
Use agent-continuity rescue mode.

The current agent is stalled or unsafe to continue. Within 90 seconds:
1. Read `handoff.md` first; create it if missing.
2. Read only directly referenced task files.
3. Pick exactly one safe highest-priority action that can advance or clarify the task.
4. Execute that action, or record the blocker once.
5. Update `handoff.md` with confirmed state, blockers, do-not-retry notes, and exact next steps.

No long-running commands. No broad search. No destructive operations. No retry loops without new evidence.
If 90 seconds is not enough, publish a partial handoff first.
```

## Full Rescue Output Structure

Use this after the short rescue has stabilized the task:

```text
Start with one status label:
- READY TO CONTINUE
- NEEDS REVIEW
- BLOCKED ON <specific blocker>

Then update `handoff.md` with:
1. Confirmed State with evidence
2. Unfinished Work by priority
3. Blockers and likely causes
4. Minimal Next Executable Steps
5. Guardrails / What NOT to Do
6. Decision Log
7. Quick Resume Note
```

## Hard Limits

- Timebox each action to 90 seconds.
- If a command or tool blocks, stop and write the blocker.
- If permission/session/read-only issues appear, do not keep retrying.
- Do not edit unrelated business files.
- Do not attempt large refactors in rescue mode.

## Completion Criteria

- `handoff.md` exists.
- It has a clear status.
- It has enough evidence for a new agent to trust it.
- It names the exact next minimal step.
