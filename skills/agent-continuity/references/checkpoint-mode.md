# Checkpoint Mode

Use this when the task is still healthy but should remain restartable.

## Prompt

```text
Use agent-continuity checkpoint mode.

The current task is still progressing. Update `handoff.md` so another agent can take over later without hidden context.

Do not expand scope. Do not perform unrelated work.

Record:
- original goal
- confirmed current state with evidence
- recent 1-2 steps completed
- exact next minimal step
- next 3 steps
- unfinished work by priority
- blockers or risks
- do-not-retry notes
- key files/artifacts
- decisions and assumptions
- 15-second quick resume note
```

## Rules

- Checkpoint after every 1-2 meaningful steps in long tasks.
- Prefer concrete artifact references over prose memory.
- Keep `Next Minimal Step` to one action.
- Preserve prior blockers and do-not-retry notes unless they are explicitly resolved.
- If a claim has no evidence, mark it as `Assumption`.

## Bad Checkpoint

```text
We made progress and should continue fixing things.
```

## Good Checkpoint

```text
`src/importer.ts` now parses quoted CSV fields; `npm test -- importer` passes.
Next minimal step: update `docs/import.md` with the new quote-handling behavior.
Do not retry `npm test` for the full suite until dependency install issue in `packages/ui` is resolved.
```
