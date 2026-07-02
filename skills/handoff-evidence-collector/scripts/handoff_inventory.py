#!/usr/bin/env python3
import argparse
import json
import os
import subprocess
import time
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ROOTS = [Path.cwd()]
VALIDATOR = REPO_ROOT / "skills" / "agent-continuity" / "scripts" / "validate_handoff.py"
SKIP_DIRS = {
    ".git",
    "node_modules",
    ".venv",
    "venv",
    "__pycache__",
    "models",
    "checkpoints",
    "cache",
    ".cache",
    "outputs",
    "data",
}
MAX_DEPTH = 6


def classify(path: Path, text: str) -> str:
    if "references" in path.parts or "template" in path.name.lower():
        return "template_or_reference"
    if "## Status" in text and "## Quick Resume" in text and "## Next Minimal Step" in text:
        return "agent_continuity_handoff"
    if "cursor" in path.name.lower() or "/cursor-" in str(path).lower():
        return "cursor_handoff"
    if "handoff guide" in text.lower() or "install" in text.lower()[:1200]:
        return "usage_handoff_or_guide"
    return "handoff_like"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-root", default="handoff-evidence-smoke-output")
    parser.add_argument("--root", action="append", default=[])
    args = parser.parse_args()

    out = Path(args.output_root).resolve()
    (out / "work").mkdir(parents=True, exist_ok=True)
    env_roots = [p for p in os.environ.get("HANDOFF_EVIDENCE_ROOTS", "").split(os.pathsep) if p]
    roots_arg = args.root or env_roots
    roots = [Path(p).expanduser().resolve() for p in roots_arg] if roots_arg else DEFAULT_ROOTS

    paths = []
    for root in roots:
        if not root.exists():
            continue
        for current, dirnames, filenames in os.walk(root, topdown=True):
            cur = Path(current)
            try:
                depth = len(cur.relative_to(root).parts)
            except ValueError:
                depth = MAX_DEPTH + 1
            if depth >= MAX_DEPTH:
                dirnames[:] = []
            dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
            for fname in filenames:
                low = fname.lower()
                if low == "handoff.md" or ("handoff" in low and low.endswith(".md")):
                    paths.append(cur / fname)
    paths = sorted(set(p for p in paths if ".git" not in p.parts), key=lambda p: str(p).lower())

    records = []
    for path in paths:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
            st = path.stat()
        except Exception as exc:
            records.append({"path": str(path), "read_error": repr(exc)})
            continue
        kind = classify(path, text)
        validation = {"attempted": False}
        if kind == "agent_continuity_handoff" and VALIDATOR.exists():
            proc = subprocess.run(
                ["python3", str(VALIDATOR), str(path)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10,
            )
            validation = {
                "attempted": True,
                "returncode": proc.returncode,
                "stdout": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            }
        records.append({
            "path": str(path),
            "kind": kind,
            "size": st.st_size,
            "mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(st.st_mtime)),
            "has_status": "## Status" in text,
            "has_quick_resume": "## Quick Resume" in text,
            "has_next_minimal_step": "## Next Minimal Step" in text,
            "validation": validation,
        })

    counts = {}
    for rec in records:
        counts[rec.get("kind", "unreadable")] = counts.get(rec.get("kind", "unreadable"), 0) + 1
    data = {
        "roots": [str(r) for r in roots],
        "validator": str(VALIDATOR),
        "counts": counts,
        "records": records,
    }
    (out / "work" / "handoff_inventory.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        "# Handoff Inventory",
        "",
        "TASK: Collect and classify local Codex/Cursor/project handoff files.",
        "",
        "Goal: make local handoff files usable as evidence for Codex self-distillation and project continuation.",
        "",
        "Objective: collect handoffs without editing source projects, classify each file, and validate only true agent-continuity handoffs.",
        "",
        "STATUS: real_execution_smoke",
        "",
        "Outcome: generated a Markdown inventory plus JSON evidence index for the requested roots.",
        "",
        "Execution mode: real_execution. This is not mock and not dry_run. This script only reads project files and writes this inventory to the requested output directory; it does not edit project files.",
        "",
        "Evidence: each record below includes a concrete file path, mtime, classification, and validator result when applicable. `evidence_missing` is used only when a root is unavailable or a file cannot be read.",
        "",
        "## Input / Workflow / Output",
        "",
        "Input roots:",
        "",
    ]
    for root in roots:
        lines.append(f"- `{root}`")
    lines += [
        "",
        "Workflow:",
        "",
        "1. Bounded walk under input roots.",
        "2. Skip dependency, cache, model, checkpoint, data, and output directories.",
        "3. Classify matching handoff Markdown files.",
        "4. Validate true `agent_continuity_handoff` files with the configured validator.",
        "5. Write Markdown and JSON inventory artifacts.",
        "",
        "Output artifacts:",
        "",
        f"- `{out / 'Handoff_Inventory.md'}`",
        f"- `{out / 'work' / 'handoff_inventory.json'}`",
        "",
        "Acceptance:",
        "",
        "- The script exits 0.",
        "- Every collected file has a `kind` classification.",
        "- Cursor handoffs are indexed but not forced through the agent-continuity validator.",
        "- Project files are not modified.",
        "",
        "Repair / rollback:",
        "",
        "- If this inventory is wrong, rerun with narrower `--root` values or inspect `handoff_inventory.json`.",
        "- Rollback is not needed for project files because this is read-only against source roots.",
        "- If a live agent-continuity handoff fails validation, generate a patch candidate before editing the handoff.",
        "",
        "Human entrypoint:",
        "",
        f"- `{out / 'Handoff_Inventory.md'}`",
        "",
        "Roots:",
        "",
    ]
    for root in roots:
        lines.append(f"- `{root}`")
    lines += [
        "",
        f"Validator: `{VALIDATOR}`",
        "",
        "## Counts",
        "",
        "| Kind | Count |",
        "|---|---:|",
    ]
    for key, value in sorted(counts.items()):
        lines.append(f"| {key} | {value} |")
    lines += [
        "",
        "## Records",
        "",
        "| Path | Kind | mtime | agent-continuity fields | Validation |",
        "|---|---|---|---|---|",
    ]
    for rec in records:
        fields = ",".join(
            key for key in ["has_status", "has_next_minimal_step", "has_quick_resume"] if rec.get(key)
        ) or "none"
        val = rec.get("validation", {})
        if val.get("attempted"):
            validation = f"rc={val.get('returncode')} {val.get('stdout') or val.get('stderr')}"
        else:
            validation = "not_applicable"
        lines.append(f"| `{rec['path']}` | {rec.get('kind')} | {rec.get('mtime','')} | {fields} | {validation} |")
    (out / "Handoff_Inventory.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps({"output_root": str(out), "handoffs": len(records), "counts": counts}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
