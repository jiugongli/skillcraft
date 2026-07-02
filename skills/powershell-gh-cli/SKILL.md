---
name: powershell-gh-cli
description: Use when running GitHub CLI (`gh`) from Windows PowerShell, especially `gh pr view`, `gh pr list`, `gh api`, loops, `--json`, `--jq`, `--template`, formatted strings, redirection or pipe symbols, dollar variables, quotes, backticks, braces, or GitHub PR metadata. Prevents PowerShell quoting and argument parsing bugs by preferring native JSON parsing and array arguments.
---

# PowerShell GH CLI

## Default Pattern

Prefer `gh --json ... | ConvertFrom-Json` over inline `--jq` or `--template` in PowerShell.

```powershell
$prs = @(1650, 1660, 1663, 1700)
foreach ($number in $prs) {
  $pr = gh pr view $number --json number,title,headRefName,baseRefName,mergedAt,mergeCommit,files,url |
    ConvertFrom-Json

  [pscustomobject]@{
    Number = $pr.number
    Flow = "$($pr.headRefName) -> $($pr.baseRefName)"
    MergedAt = $pr.mergedAt
    MergeCommit = $pr.mergeCommit.oid
    Title = $pr.title
    Files = ($pr.files.path -join "`n")
  }
}
```

Reason: this keeps `>`, `|`, `$`, quotes, braces, and newlines inside PowerShell object handling instead of shell argument parsing.

## Safer Invocation Rules

- Use PowerShell arrays for arguments when the command is complex.
- Do not build a single command string and run it with `Invoke-Expression`.
- Use `ConvertFrom-Json` for filtering, joins, grouping, and formatted output.
- Use `--jq` only for short expressions with no shell-sensitive characters.
- If `--jq` is necessary, wrap the expression in single quotes and keep output formatting outside jq.
- Treat errors like `unknown shorthand flag: '>' in ->` as shell quoting/argument splitting symptoms first, not as GitHub CLI semantics.
- After a quoting-related failure, rerun with the safer JSON pattern before drawing conclusions.

## Preferred Examples

PR metadata:

```powershell
$pr = gh pr view 1650 --json number,title,headRefName,baseRefName,mergedAt,mergeCommit,url |
  ConvertFrom-Json
"#$($pr.number) $($pr.headRefName) -> $($pr.baseRefName) $($pr.mergedAt)"
```

Changed files:

```powershell
$pr = gh pr view 1660 --json files | ConvertFrom-Json
$pr.files | Select-Object -ExpandProperty path
```

Merged PR search:

```powershell
$items = gh pr list --state merged --search 'crowdstrike repo:Mitsubishi-Chemical-Group/oas2-src' `
  --json number,title,headRefName,baseRefName,mergedAt,mergeCommit,url --limit 30 |
  ConvertFrom-Json
$items | Sort-Object mergedAt | Select-Object number,headRefName,baseRefName,mergedAt,title
```

## When Inline `--jq` Is Acceptable

Accept short, plain extraction:

```powershell
gh pr view 1650 --json number,title --jq '.number'
```

Avoid inline jq for formatted strings such as:

```powershell
# Avoid this shape in PowerShell.
gh pr view 1650 --json number,headRefName,baseRefName --jq '... -> ...'
```

Use JSON parsing instead.
