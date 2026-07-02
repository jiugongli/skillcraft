#!/usr/bin/env python3
import argparse
import json
import re
from pathlib import Path


DIMENSIONS = {
    "user_goal_answered": 15,
    "evidence_bound": 20,
    "structure": 10,
    "input_process_output_contract": 15,
    "verification": 15,
    "real_mock_distinction": 10,
    "repair_rollback": 10,
    "human_entrypoint": 5,
}


def hits(text, patterns):
    found = []
    low = text.lower()
    for pat in patterns:
        if pat.startswith("re:"):
            if re.search(pat[3:], text, re.I):
                found.append(pat)
        elif pat.lower() in low:
            found.append(pat)
    return found


def cap(max_points, count, step):
    return min(max_points, count * step)


def classify(score):
    if score >= 90:
        return "ready"
    if score >= 75:
        return "usable"
    if score >= 60:
        return "draft"
    return "fail"


def score_text(text):
    dimensions = {}
    issues = []
    rework = []

    goal_e = hits(text, ["task", "goal", "status", "outcome", "objective", "完成", "目标", "状态"])
    dimensions["user_goal_answered"] = {
        "points": cap(15, len(goal_e), 4),
        "max_points": 15,
        "evidence": goal_e,
    }

    evidence_patterns = [
        "evidence_missing",
        "references:",
        "evidence",
        "验证",
        "证据",
        "re:/(?:Users|Volumes)/[^\\s)`]+",
        "re:/Volumes/[^\\s)`]+",
        "re:`[^`]+\\.(md|json|py|ts|tsx|txt|html|csv|xlsx|docx|pptx|pdf)`",
    ]
    ev = hits(text, evidence_patterns)
    dimensions["evidence_bound"] = {
        "points": cap(20, len(ev), 4),
        "max_points": 20,
        "evidence": ev,
    }

    headings = len(re.findall(r"(?m)^#{1,4}\s+", text))
    bullets = len(re.findall(r"(?m)^\s*(-|\d+\.)\s+", text))
    tables = text.count("|---")
    dimensions["structure"] = {
        "points": min(10, headings * 2 + min(4, bullets // 4) + min(2, tables)),
        "max_points": 10,
        "evidence": [f"headings={headings}", f"bullets={bullets}", f"tables={tables}"],
    }

    contract_e = hits(text, ["input", "output", "workflow", "when to use", "when not to use", "acceptance", "completion", "输入", "输出", "验收", "流程"])
    dimensions["input_process_output_contract"] = {
        "points": cap(15, len(contract_e), 3),
        "max_points": 15,
        "evidence": contract_e,
    }

    verify_e = hits(text, ["validator", "validate", "test", "smoke", "verify", "verification", "eval", "assertion", "检查", "验证", "测试"])
    dimensions["verification"] = {
        "points": cap(15, len(verify_e), 3),
        "max_points": 15,
        "evidence": verify_e,
    }

    mode_e = hits(text, ["real execution", "real_execution", "dry-run", "dry_run", "mock", "fixture", "candidate", "candidate_only", "真实", "候选"])
    dimensions["real_mock_distinction"] = {
        "points": cap(10, len(mode_e), 3),
        "max_points": 10,
        "evidence": mode_e,
    }

    repair_e = hits(text, ["rollback", "repair", "failure", "recover", "blocked", "rework", "回滚", "修复", "失败", "返工"])
    dimensions["repair_rollback"] = {
        "points": cap(10, len(repair_e), 3),
        "max_points": 10,
        "evidence": repair_e,
    }

    entry_e = hits(text, ["receipt", "handoff", "clickable", "index", "entrypoint", "回执", "入口", "交接"])
    dimensions["human_entrypoint"] = {
        "points": cap(5, len(entry_e), 2),
        "max_points": 5,
        "evidence": entry_e,
    }

    for name, max_points in DIMENSIONS.items():
        got = dimensions[name]["points"]
        if got < max_points * 0.6:
            issues.append(f"{name} is weak: {got}/{max_points}")

    if dimensions["evidence_bound"]["points"] < 12:
        rework.append("Add concrete evidence paths, command outputs, source dates, or explicit evidence_missing markers.")
    if dimensions["verification"]["points"] < 9:
        rework.append("Add a smoke test, validator result, or verification section.")
    if dimensions["real_mock_distinction"]["points"] < 6:
        rework.append("Label the execution mode as real_execution, dry_run, mock, fixture, or candidate_only.")
    if dimensions["input_process_output_contract"]["points"] < 9:
        rework.append("Add input, workflow, output, and acceptance/completion conditions.")
    if dimensions["repair_rollback"]["points"] < 6:
        rework.append("Add rollback, repair, or blocked-state next steps.")

    score = sum(v["points"] for v in dimensions.values())
    return {
        "score": score,
        "threshold": classify(score),
        "mode": "heuristic_local_validator",
        "dimensions": dimensions,
        "issues": issues,
        "rework_tasks": rework,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--json-out")
    args = parser.parse_args()
    text = Path(args.path).read_text(encoding="utf-8", errors="replace")
    result = score_text(text)
    result["path"] = str(Path(args.path).resolve())
    data = json.dumps(result, ensure_ascii=False, indent=2)
    if args.json_out:
        Path(args.json_out).write_text(data + "\n", encoding="utf-8")
    print(data)


if __name__ == "__main__":
    main()
