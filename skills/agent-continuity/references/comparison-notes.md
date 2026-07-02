# Comparison Notes

This skill is about continuity, not orchestration.

## What It Is

- Externalizing task state from agent context into `handoff.md`.
- Making long tasks restartable.
- Allowing a new agent to continue when context is too large, degraded, or unavailable.
- Providing emergency rescue when an agent stalls, loops, or times out.

## What It Is Not

- Not a multi-agent routing framework.
- Not background-agent scheduling.
- Not task queue management.
- Not a replacement for project documentation.

## Related Public Patterns

- Cursor community examples include background-agent handoff workflows with handoff files and resume prompts.
- OpenAI Agents SDK and Microsoft Agent Framework use "handoff" for multi-agent orchestration.
- Long-running agent harnesses often use checkpoint/resume ideas.

This skill differs by focusing on a simple file contract: `handoff.md` as the continuity surface for any coding or research agent.
