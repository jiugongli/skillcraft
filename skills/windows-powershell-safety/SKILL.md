---
name: windows-powershell-safety
description: Use when running commands in Windows PowerShell, especially shell searches with `rg`, `git grep`, `Select-String`, `findstr`, Git revision path syntax, fixed-string patterns, quoted code snippets, native CLI arguments, npm/node/playwright commands, variable interpolation, or commands copied from Bash. Prevents quoting, escaping, wildcard, pipeline, stderr, secret-log, and argument-boundary mistakes.
---

# Windows PowerShell Safety

## Default Checks

Before running a non-trivial PowerShell command, check these points:

- Use single quotes for literal search patterns.
- Do not backslash-escape double quotes inside single-quoted strings.
- Use `${var}` when interpolating a variable before `:` or another name character.
- Prefer separate CLI arguments over one composed command string.
- Do not use Bash here-doc syntax in PowerShell.
- For file operations, use native PowerShell cmdlets with `-LiteralPath`.
- Treat `-like` and `-notlike` as wildcard operators, not literal string operators.
- Wrap generated output in `& { ... }` before piping a `foreach` loop.
- For native CLIs that may write benign stderr (`npm`, `node`, `playwright`, `python`, `gh`), capture output explicitly and check `$LASTEXITCODE`.
- For secret-bearing commands, write raw output to a temp log, redact before display, then remove the temp log.

## Literal Search Patterns

Distinguish PowerShell cmdlets from native executables.
PowerShell stores double quotes inside single-quoted strings literally, but native executables receive arguments through Windows argv parsing.
For native executables such as `git.exe`, `rg.exe`, and `python.exe`, embedded double quotes may be stripped unless escaped for native argv.

For PowerShell cmdlets such as `Select-String`, do not escape double quotes:

```powershell
$pattern = 'name="delivery_outside_tel"'
Select-String -Path .\src\file.tsx -Pattern $pattern -SimpleMatch
```

For native CLIs, either escape embedded double quotes or search for a shorter quote-free token:

```powershell
git grep -n -F 'name=\"delivery_outside_tel\"' origin/main -- src
git grep -n -F 'restrictInput(e.target.value' origin/pr/1701 -- src
rg -n -F 'setValue(\"address2\"' src
```

To inspect what a native executable receives, print argv:

```powershell
python -c "import sys; print(repr(sys.argv[1]))" 'setValue(\"address2\"'
```

Expected output:

```text
'setValue("address2"'
```

If this prints `setValue(address2`, the quotes were stripped before the target CLI received the argument.

## Variable Interpolation

PowerShell treats `:` after a variable name as part of scoped variable syntax.
Use `${var}` when a variable is followed by `:`.

Good:

```powershell
"--- ${file}:$($line)"
```

Bad:

```powershell
"--- $file:$($line)"
```

The bad form can fail with `Variable reference is not valid`.

## Literal Versus Wildcard Matching

PowerShell wildcard operators interpret `*`, `?`, and `[]`.
Do not use `-like` for literal markers that contain square brackets, such as GitHub issue tags.

Good:

```powershell
$comment.body.StartsWith('[controller-key-rotation-published][mcc]')
$comment.body.Contains('[mcc-e2e-complete]')
$comment.body -match ('^' + [regex]::Escape('[review-complete]'))
```

Bad:

```powershell
$comment.body -like '[controller-key-rotation-published][mcc]*'
```

The bad form treats bracketed text as wildcard character classes and can throw `WildcardPatternException`.

## Piping Loop Output

PowerShell does not pipe directly from a `foreach` statement.
Wrap the loop in a script block when generated objects should flow into another command.

Good:

```powershell
& {
  foreach ($path in $paths) {
    [pscustomobject]@{
      Path = $path
      Exists = (Test-Path -LiteralPath $path)
    }
  }
} | Format-Table -AutoSize
```

Bad:

```powershell
foreach ($path in $paths) {
  [pscustomobject]@{ Path = $path }
} | Format-Table -AutoSize
```

The bad form can fail with `An empty pipe element is not allowed`.

## Git Revision Paths

Use a backtick before `:` when constructing `rev:path` inside an interpolated string.

Good:

```powershell
git show "origin/main`:src/components/atomic/ActiveTextField.tsx"
git show "${rev}`:${path}"
```

For a literal rev path, no backtick is needed:

```powershell
git show origin/main:src/components/atomic/ActiveTextField.tsx
```

## Native CLI Arguments

Prefer direct argument lists.
Do not compose one large command string unless there is no alternative.

Good:

```powershell
git grep -n -F 'restrictInput(e.target.value' origin/pr/1701 -- src/components
rg -n -F 'field.onChange(filteredValue)' src/components
```

Avoid:

```powershell
$cmd = "git grep -n -F 'restrictInput(e.target.value' origin/pr/1701 -- src/components"
Invoke-Expression $cmd
```

## Native CLI Stderr And Exit Codes

Windows PowerShell can surface native stderr as `NativeCommandError`, especially under `$ErrorActionPreference = 'Stop'`.
Do not let warning text from `node`, `npm`, `playwright`, `python`, or similar tools decide whether a command succeeded.
Capture stdout and stderr to a log, then check `$LASTEXITCODE`.

For commands where raw output may include secrets, do not stream output to the chat.
Write to a temp log, redact, summarize, and remove the log.

Preferred pattern:

```powershell
$logPath = Join-Path $env:TEMP ('tool-' + [guid]::NewGuid().ToString('N') + '.log')
$command = 'npm run test > "' + $logPath + '" 2>&1'
& cmd.exe /d /s /c $command
$exitCode = $LASTEXITCODE

$raw = Get-Content -LiteralPath $logPath -Raw
$redacted = $raw `
  -replace 'Bearer\s+[^\s''"\}\],)]+', 'Bearer [REDACTED]' `
  -replace '(ATH_(E2E_)?MACHINE_KEY\s*=\s*)[^\s]+', '$1[REDACTED]'

Remove-Item -LiteralPath $logPath -Force -ErrorAction SilentlyContinue
if ($exitCode -ne 0) {
  throw "Command failed with exit code ${exitCode}`n${redacted}"
}
```

Use this pattern for Playwright or staging tests that may include auth headers, API keys, cookies, traces, screenshots, or replayable requests.

## Bash Syntax To Avoid

PowerShell does not support Bash here-docs:

```powershell
python - <<'PY'
```

Use `python -c`, a temporary file, or a script already in the repository.

## Recovery Rule

If a search returns no matches but the pattern is expected to exist:

1. Identify whether the search tool is a PowerShell cmdlet or native executable.
2. Print the exact native argv with `python -c "import sys; print(repr(sys.argv[1]))" <pattern>`.
3. Try a shorter quote-free fixed string first.
4. Use `git show rev:path` or `Get-Content -Encoding UTF8` to inspect the target lines.
