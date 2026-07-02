---
name: "asana-mcp-codex"
description: "Use when configuring, validating, or troubleshooting Asana V2 MCP access from Codex or another local coding agent, especially OAuth failures, missing MCP tools, direct HTTP versus mcp-remote choices, token-safety concerns, or deciding when to fall back to Asana REST API checks."
---

# Asana MCP for Codex

Use this skill to connect Codex-style agents to Asana's official V2 MCP server without leaking credentials or confusing MCP startup failures with Asana task failures.

## Core Model

- Treat MCP as the default execution path for agent-driven Asana work: read tasks, inspect projects, add comments, and update task fields through exposed MCP tools when available.
- Treat Skills as workflow guidance, not as a secret holder or an API client. Do not put access tokens, OAuth client secrets, personal access tokens, or `.mcp-auth` contents in a skill.
- Use REST API or PAT-based scripts only as a narrow fallback for verification or explicitly requested automation when MCP is unavailable.
- Keep private workspace names, task IDs, local paths, and project-specific comment rules in a private overlay skill or local instructions, not in reusable public skill content.

## Connection Decision

1. Check the current Codex client capability before choosing a transport.
   - If Codex supports static OAuth client credentials for streamable HTTP MCP servers, use the official Asana V2 MCP endpoint directly.
   - If Codex only supports generic OAuth or dynamic client registration for remote MCP login, prefer an MCP bridge such as `mcp-remote` with static OAuth client info.
2. Use Asana V2 MCP endpoint:
   - MCP URL: `https://mcp.asana.com/v2/mcp`
   - OAuth resource: `https://mcp.asana.com/v2`
3. Use a registered Asana MCP app, not a standard Asana API app, for V2 MCP OAuth.
4. Configure the redirect URI exactly as required by the MCP client or bridge.
5. Keep the MCP server disabled until its OAuth flow has been validated if a broken server would slow down agent startup.

## Known Failure Pattern

When Asana returns an error like:

```text
invalid_token
Invalid token signature - token was not issued by Asana OAuth
```

Interpret it as an OAuth-token provenance problem first, not as a task/project permission problem.

Common causes:

- The client attempted dynamic client registration against an Asana V2 MCP flow that requires a pre-registered client.
- The client completed a browser login but did not use the registered Asana MCP app's client ID and client secret during token exchange.
- A standard Asana API OAuth token or PAT was sent to the MCP server. Tokens for standard Asana API access and tokens for Asana MCP apps are separate.
- The OAuth resource or server URL does not match Asana's V2 MCP expectations.

Do not keep retrying task reads until the MCP handshake and `tools/list` work.

## Validation Workflow

1. Inspect the effective MCP configuration without printing secrets.
2. Confirm whether the Asana server is stdio bridge or streamable HTTP.
3. Use shell commands that match the user's current platform; do not assume PowerShell, Bash, macOS, Linux, or Windows unless the environment shows it.
4. Start a fresh agent or a minimal MCP client session; current Codex turns often do not hot-reload newly added MCP tools.
5. Perform MCP `initialize`, then `tools/list`.
6. Only after tools are listed, perform a low-risk read call such as fetching one known task or listing a small set of tasks.
7. If the tool is missing in the current turn but the server validates externally, treat it as a tool-injection/session-refresh issue.
8. If validation fails, record:
   - Transport used
   - Whether OAuth completed in browser
   - Exact redacted error class
   - Whether `initialize` or `tools/list` failed
   - Whether a fresh agent session was tested

## Security Rules

- Never print PATs, OAuth client secrets, refresh tokens, access tokens, `.mcp-auth` files, or raw authorization headers.
- Prefer environment variables, OS keychains, or local secret files excluded from version control.
- Do not commit generated OAuth caches.
- Do not pass real secrets through shell commands that will be saved in terminal history unless there is no safer mechanism.
- Redact bearer tokens and connection strings in logs and summaries.
- If a public skill or PR is being prepared, remove all local paths, account identifiers, workspace names, task IDs, and organization-specific workflow rules.

## REST API Fallback

Use REST fallback only when MCP is not available or when deterministic scripting is explicitly better than an agent tool call.

Appropriate fallback uses:

- Confirm a task exists and the credential can read it.
- Compare whether an MCP failure is authentication, authorization, or tool-discovery related.
- Run a small, explicit, read-only diagnostic.

Avoid fallback for routine agent work when MCP is available. If writing through REST, require a clear user request and keep the mutation narrowly scoped.

## Public Documentation To Check

- Asana MCP server overview and OAuth app setup: `https://developers.asana.com/docs/integrating-with-asanas-mcp-server`
- Asana V2 MCP coding-client setup: `https://developers.asana.com/docs/connecting-mcp-clients-to-asanas-v2-server`
- Codex MCP configuration: `https://developers.openai.com/codex/mcp`
