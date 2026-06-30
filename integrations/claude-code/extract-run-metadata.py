#!/usr/bin/env python3
"""
Rule-based extractor for Claude Code session JSONL files.
No API key required — infers retro fields from session structure and content.

Usage: python3 extract-run-metadata.py <session.jsonl>
"""

import json
import os
import re
import sys
import pathlib
from datetime import datetime, timezone

# ── helpers ──────────────────────────────────────────────────────────────────

def slug_to_project(slug: str) -> str:
    parts = slug.lstrip("-").split("-")
    try:
        idx = next(i for i, p in enumerate(parts) if p == "code")
        return "-".join(parts[idx + 1:]) or slug
    except StopIteration:
        return slug


def slug_to_path(slug: str) -> str:
    return "/" + slug.replace("-", "/").lstrip("/")


def parse_ts(ts: str):
    for fmt in ("%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(ts, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def duration_mins(start_ts, end_ts):
    s, e = parse_ts(start_ts), parse_ts(end_ts)
    if s and e:
        return max(1, int((e - s).total_seconds() / 60))
    return ""


# ── session parsing ───────────────────────────────────────────────────────────

def parse_session(path: pathlib.Path) -> dict:
    lines = path.read_text().strip().split("\n")

    user_messages = []   # first user enqueue / user type messages
    assistant_texts = [] # assistant text content
    tool_calls = []      # list of tool names used
    tool_errors = []     # error strings from tool results
    timestamps = []

    for raw in lines:
        try:
            entry = json.loads(raw)
        except json.JSONDecodeError:
            continue

        ts = entry.get("timestamp")
        if ts:
            timestamps.append(ts)

        etype = entry.get("type", "")

        # Content lives at entry["content"] for queue-ops/user,
        # but at entry["message"]["content"] for assistant messages.
        raw_content = entry.get("content", "")
        msg_content = entry.get("message", {}).get("content", raw_content)

        # First user message comes from queue-operation enqueue
        if etype == "queue-operation" and entry.get("operation") == "enqueue" and raw_content:
            user_messages.append(str(raw_content))

        elif etype == "user":
            content = msg_content if isinstance(msg_content, list) else raw_content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_result":
                            for inner in block.get("content", []):
                                if isinstance(inner, dict) and inner.get("type") == "text":
                                    txt = inner.get("text", "")
                                    if any(k in txt.lower() for k in ("error", "failed", "exception", "traceback", "cannot", "not found")):
                                        tool_errors.append(txt[:200])
                        elif block.get("type") == "text" and block.get("text"):
                            user_messages.append(block["text"])
            elif isinstance(content, str) and content:
                user_messages.append(content)

        elif etype == "assistant":
            content = msg_content if isinstance(msg_content, list) else raw_content
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict):
                        if block.get("type") == "text":
                            assistant_texts.append(block.get("text", ""))
                        elif block.get("type") == "tool_use":
                            tool_calls.append(block.get("name", "unknown"))
            elif isinstance(content, str) and content:
                assistant_texts.append(content)

    return {
        "user_messages": user_messages,
        "assistant_texts": assistant_texts,
        "tool_calls": tool_calls,
        "tool_errors": tool_errors,
        "timestamps": timestamps,
    }


# ── inference rules ───────────────────────────────────────────────────────────

FEATURE_KEYWORDS = re.compile(r"\b(add|implement|build|create|new|feature|support)\b", re.I)
BUGFIX_KEYWORDS  = re.compile(r"\b(fix|bug|broken|error|fail|issue|crash|wrong|not working)\b", re.I)
REFACTOR_KW      = re.compile(r"\b(refactor|clean|simplify|reorgani[sz]e|rename|move)\b", re.I)
REVIEW_KW        = re.compile(r"\b(review|check|look at|audit|assess|evaluate)\b", re.I)
EXPLAIN_KW       = re.compile(r"\b(explain|what is|how does|understand|describe|why)\b", re.I)
TEST_KW          = re.compile(r"\b(test|spec|unit test|coverage|assert)\b", re.I)
OPS_KW           = re.compile(r"\b(deploy|ci|cd|pipeline|docker|infra|config|setup|install)\b", re.I)

EDIT_TOOLS   = {"edit", "write", "multiedit", "notebookedit"}
READ_TOOLS   = {"read", "ls", "glob", "grep", "find"}
BASH_TOOLS   = {"bash", "terminal", "computer"}
SEARCH_TOOLS = {"websearch", "webfetch"}
AGENT_TOOLS  = {"agent", "task"}

ERROR_PATTERNS = re.compile(
    r"\b(error|exception|traceback|failed|cannot|not found|undefined|invalid|permission denied)\b", re.I
)
SUCCESS_PATTERNS = re.compile(
    r"\b(done|complete|success|finished|implemented|fixed|works|all tests pass|lgtm)\b", re.I
)


def infer_task_type(first_prompt: str) -> str:
    if BUGFIX_KEYWORDS.search(first_prompt):  return "bugfix"
    if FEATURE_KEYWORDS.search(first_prompt): return "feature"
    if REFACTOR_KW.search(first_prompt):      return "refactor"
    if REVIEW_KW.search(first_prompt):        return "review"
    if EXPLAIN_KW.search(first_prompt):       return "explain"
    if TEST_KW.search(first_prompt):          return "test"
    if OPS_KW.search(first_prompt):           return "ops"
    return "other"


def infer_coding_intensity(tool_calls: list) -> str:
    names = {t.lower() for t in tool_calls}
    edit_count = sum(1 for t in tool_calls if t.lower() in EDIT_TOOLS)
    if not tool_calls:                        return "planning-only"
    if edit_count >= 3:                       return "coding-heavy"
    if edit_count >= 1:                       return "mixed"
    if names & BASH_TOOLS:                    return "workflow"
    return "planning-only"


def infer_outcome(tool_errors: list, assistant_texts: list, tool_calls: list) -> str:
    last_assistant = " ".join(assistant_texts[-3:]).lower() if assistant_texts else ""
    error_count = len(tool_errors)

    if SUCCESS_PATTERNS.search(last_assistant) and error_count == 0:
        return "success"
    if error_count >= 3 or ERROR_PATTERNS.search(last_assistant):
        return "failure" if error_count >= 5 else "partial"
    if not tool_calls:
        return "uncertain"
    if SUCCESS_PATTERNS.search(last_assistant):
        return "success"
    return "uncertain"


def infer_retry_count(tool_errors: list, tool_calls: list) -> int:
    # Count meaningful error-recovery loops (not raw tool calls)
    return min(len(tool_errors), 10)


def build_tool_summary(tool_calls: list) -> str:
    seen = []
    categories = []
    mapping = {
        **{t: "edit" for t in EDIT_TOOLS},
        **{t: "read" for t in READ_TOOLS},
        **{t: "bash" for t in BASH_TOOLS},
        **{t: "web" for t in SEARCH_TOOLS},
        **{t: "agent" for t in AGENT_TOOLS},
    }
    for t in tool_calls:
        cat = mapping.get(t.lower(), t.lower())
        if cat not in seen:
            seen.append(cat)
            categories.append(cat)
    return "|".join(categories)


def infer_flags(tool_errors: list, retry_count: int, outcome: str) -> str:
    flags = []
    if retry_count >= 3:
        flags.append("loop_detected")
    if outcome in ("failure", "partial") and not tool_errors:
        flags.append("verification_missing")
    return "|".join(flags)


def sampling_reason(outcome: str, retry_count: int) -> str:
    if retry_count >= 3:    return "heavy_retry_signal"
    if outcome == "failure": return "failure_or_partial_signal"
    if outcome == "partial": return "failure_or_partial_signal"
    if outcome == "success": return "sampled_clean_win"
    return "failure_or_partial_signal"


# ── main ──────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: extract-run-metadata.py <session.jsonl>", file=sys.stderr)
        sys.exit(1)

    session_path = pathlib.Path(sys.argv[1])
    if not session_path.exists():
        print(f"File not found: {session_path}", file=sys.stderr)
        sys.exit(1)

    data = parse_session(session_path)

    if not data["user_messages"]:
        print("No user messages found", file=sys.stderr)
        sys.exit(1)

    first_prompt = data["user_messages"][0]
    timestamps   = data["timestamps"]
    tool_calls   = data["tool_calls"]
    tool_errors  = data["tool_errors"]

    task_title = (first_prompt[:80].split("\n")[0]).strip()
    user_prompt_summary = first_prompt[:200].replace("\n", " ").strip()

    task_type        = infer_task_type(first_prompt)
    coding_intensity = infer_coding_intensity(tool_calls)
    outcome          = infer_outcome(tool_errors, data["assistant_texts"], tool_calls)
    retry_count      = infer_retry_count(tool_errors, tool_calls)
    tool_summary_str = build_tool_summary(tool_calls)
    flags            = infer_flags(tool_errors, retry_count, outcome)
    error_summary    = tool_errors[0][:150] if tool_errors else ""
    needs_review     = "yes" if outcome in ("failure", "partial", "uncertain") or retry_count >= 3 else "no"

    project_slug = session_path.parent.name

    result = {
        "session_ref":                session_path.stem,
        "project":                    slug_to_project(project_slug),
        "workspace_path":             slug_to_path(project_slug),
        "run_started_at":             timestamps[0] if timestamps else "",
        "run_last_updated_at":        timestamps[-1] if timestamps else "",
        "duration_minutes_inferred":  duration_mins(timestamps[0], timestamps[-1]) if len(timestamps) >= 2 else "",
        "task_title":                 task_title,
        "user_prompt_summary":        user_prompt_summary,
        "task_type_inferred":         task_type,
        "outcome_inferred":           outcome,
        "accepted_without_edit_inferred": "uncertain",
        "retry_count_inferred":       retry_count,
        "error_summary_inferred":     error_summary,
        "tool_summary":               tool_summary_str,
        "coding_intensity":           coding_intensity,
        "needs_review":               needs_review,
        "sampling_reason":            sampling_reason(outcome, retry_count),
        "flags":                      flags,
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
