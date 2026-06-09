#!/usr/bin/env python3
"""Run trigger evaluation for a skill description.

Localized version: instead of spawning a `claude -p` subprocess per query and
parsing stream-json events for tool calls, we directly call the Anthropic SDK
in-process and inspect the response content blocks for the `Read`/`Skill` tool
use. This is much simpler, faster, and works with any Anthropic-compatible
endpoint (MiniMax, Anthropic, local vLLM, etc.).

Auth: ANTHROPIC_BASE_URL / ANTHROPIC_API_KEY env vars.
Model: LLM_MODEL env var (default: MiniMax-M2.7-highspeed for fast trigger eval).
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import anthropic

from scripts.utils import parse_skill_md


# Module-level client (reused across calls — handles connection pooling).
_client: anthropic.Anthropic | None = None


def _get_client() -> anthropic.Anthropic:
    """Lazily construct an Anthropic client.

    Reads ANTHROPIC_BASE_URL / ANTHROPIC_API_KEY from the User environment
    block (registry) as well as the current process env, so the client works
    even when the variables were set after the Mavis session was launched.
    Falls back gracefully if either is unset.
    """
    global _client
    if _client is None:
        # Merge User env into the process env so the SDK picks them up
        # (the SDK reads os.environ at request time).
        for var in ("ANTHROPIC_BASE_URL", "ANTHROPIC_API_KEY"):
            if not os.environ.get(var):
                user_val = _read_user_env(var)
                if user_val:
                    os.environ[var] = user_val
        _client = anthropic.Anthropic()
    return _client


def _read_user_env(name: str) -> str | None:
    """Read a User-level environment variable from the Windows registry.

    Used as a fallback when the variable is set at the User level (via
    `[Environment]::SetEnvironmentVariable(..., 'User')`) but hasn't been
    picked up by the current process's environment block.
    """
    if os.name != "nt":
        return None
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment") as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except (OSError, FileNotFoundError):
        return None


def find_project_root() -> Path:
    """Find the project root by walking up from cwd looking for .claude/.

    Kept for API compatibility with upstream. We no longer need a project root
    for subprocess launching, but downstream callers may still inspect it.
    """
    current = Path.cwd()
    for parent in [current, *current.parents]:
        if (parent / ".claude").is_dir():
            return parent
    return current


def _skill_prompt(query: str, skill_name: str, skill_description: str) -> str:
    """Construct the trigger-eval prompt.

    Tells the model that a skill called X exists, gives it the description, and
    asks the model to decide whether to consult it. We use a tool_use schema
    with a single `consult_skill` tool, and look for the model to call it
    with our skill name as the answer. This mirrors how upstream detect
    triggering via Read/Skill tool calls in `claude -p`.
    """
    return f"""You are deciding whether a Claude Code skill should be triggered for a user query.

The skill is named: {skill_name}
Skill description: {skill_description}

User query: {query}

Decide whether to consult this skill. Call the `consult_skill` tool with the
skill name if yes, or skip the tool entirely if no.

If the user is asking about something the skill description covers (or closely
related, even with casual phrasing), trigger it. If the query is about a
different domain, has nothing to do with the skill, or is better served by a
different tool, do not trigger."""


def _build_tools(skill_name: str) -> list[dict]:
    """Single-tool schema: a consult_skill tool that takes a skill name arg."""
    return [{
        "name": "consult_skill",
        "description": "Call this tool to consult a Claude Code skill for a user query.",
        "input_schema": {
            "type": "object",
            "properties": {
                "skill_name": {
                    "type": "string",
                    "description": "The name of the skill to consult.",
                }
            },
            "required": ["skill_name"],
        },
    }]


def _run_single_query_llm(
    query: str,
    skill_name: str,
    skill_description: str,
    model: str | None,
    timeout: int,
) -> bool:
    """Call the LLM once and return True iff it called consult_skill with our skill_name.

    The model may emit a `thinking` block first (M2.x always, M3 with
    `thinking: adaptive`); we just look at the final tool_use blocks.
    """
    client = _get_client()
    model_name = model or os.environ.get("LLM_MODEL") or "MiniMax-M2.7-highspeed"

    try:
        msg = client.messages.create(
            model=model_name,
            max_tokens=512,
            tools=_build_tools(skill_name),
            tool_choice={"type": "any"},  # force the model to either call the tool or actively decline
            messages=[{"role": "user", "content": _skill_prompt(query, skill_name, skill_description)}],
            timeout=timeout,
        )
    except Exception as e:
        print(f"Warning: LLM call failed for query: {e}", file=sys.stderr)
        return False

    # Look for a consult_skill tool_use with our skill_name
    for block in msg.content:
        if getattr(block, "type", None) == "tool_use" and getattr(block, "name", None) == "consult_skill":
            input_data = getattr(block, "input", {}) or {}
            called_name = input_data.get("skill_name", "")
            if called_name == skill_name:
                return True
    return False


def run_eval(
    eval_set: list[dict],
    skill_name: str,
    description: str,
    num_workers: int,
    timeout: int,
    project_root: Path,  # noqa: ARG001 — kept for API compat with upstream
    runs_per_query: int = 1,
    trigger_threshold: float = 0.5,
    model: str | None = None,
) -> dict:
    """Run the full eval set and return results."""
    results: list[dict] = []
    # Build a flat list of (item, run_idx) so each call goes through the same code path.
    tasks: list[tuple[dict, int]] = []
    for item in eval_set:
        for run_idx in range(runs_per_query):
            tasks.append((item, run_idx))

    # ThreadPoolExecutor because our calls are I/O-bound and we want to share one client.
    query_triggers: dict[str, list[bool]] = {}
    query_items: dict[str, dict] = {}

    def _worker(item: dict, _run_idx: int) -> tuple[str, bool]:
        triggered = _run_single_query_llm(
            query=item["query"],
            skill_name=skill_name,
            skill_description=description,
            model=model,
            timeout=timeout,
        )
        return item["query"], triggered

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        futures = [executor.submit(_worker, item, ridx) for item, ridx in tasks]
        for future in as_completed(futures):
            try:
                query, triggered = future.result()
            except Exception as e:
                print(f"Warning: query failed: {e}", file=sys.stderr)
                continue
            query_items.setdefault(query, _find_item(eval_set, query))
            query_triggers.setdefault(query, []).append(triggered)

    if not query_triggers:
        return {
            "skill_name": skill_name,
            "description": description,
            "results": [],
            "summary": {"total": 0, "passed": 0, "failed": 0},
        }

    for query, triggers in query_triggers.items():
        item = query_items[query]
        trigger_rate = sum(triggers) / len(triggers)
        should_trigger = item["should_trigger"]
        if should_trigger:
            did_pass = trigger_rate >= trigger_threshold
        else:
            did_pass = trigger_rate < trigger_threshold
        results.append({
            "query": query,
            "should_trigger": should_trigger,
            "trigger_rate": trigger_rate,
            "triggers": sum(triggers),
            "runs": len(triggers),
            "pass": did_pass,
        })

    elapsed = time.time() - t0
    passed = sum(1 for r in results if r["pass"])
    total = len(results)

    return {
        "skill_name": skill_name,
        "description": description,
        "results": results,
        "elapsed_seconds": round(elapsed, 2),
        "summary": {
            "total": total,
            "passed": passed,
            "failed": total - passed,
        },
    }


def _find_item(eval_set: list[dict], query: str) -> dict:
    for item in eval_set:
        if item["query"] == query:
            return item
    return {"query": query, "should_trigger": False}


def main():
    parser = argparse.ArgumentParser(description="Run trigger evaluation for a skill description")
    parser.add_argument("--eval-set", required=True, help="Path to eval set JSON file")
    parser.add_argument("--skill-path", required=True, help="Path to skill directory")
    parser.add_argument("--description", default=None, help="Override description to test")
    parser.add_argument("--num-workers", type=int, default=10, help="Number of parallel workers")
    parser.add_argument("--timeout", type=int, default=30, help="Timeout per query in seconds")
    parser.add_argument("--runs-per-query", type=int, default=3, help="Number of runs per query")
    parser.add_argument("--trigger-threshold", type=float, default=0.5, help="Trigger rate threshold")
    parser.add_argument("--model", default=None, help="Model for trigger eval (default: LLM_MODEL env var)")
    parser.add_argument("--verbose", action="store_true", help="Print progress to stderr")
    args = parser.parse_args()

    eval_set = json.loads(Path(args.eval_set).read_text())
    skill_path = Path(args.skill_path)

    if not (skill_path / "SKILL.md").exists():
        print(f"Error: No SKILL.md found at {skill_path}", file=sys.stderr)
        sys.exit(1)

    name, original_description, _content = parse_skill_md(skill_path)
    description = args.description or original_description
    project_root = find_project_root()

    if args.verbose:
        print(f"Evaluating: {description}", file=sys.stderr)
        print(f"Model: {args.model or os.environ.get('LLM_MODEL') or 'MiniMax-M2.7-highspeed'}", file=sys.stderr)

    output = run_eval(
        eval_set=eval_set,
        skill_name=name,
        description=description,
        num_workers=args.num_workers,
        timeout=args.timeout,
        project_root=project_root,
        runs_per_query=args.runs_per_query,
        trigger_threshold=args.trigger_threshold,
        model=args.model,
    )

    if args.verbose:
        summary = output["summary"]
        print(f"Results: {summary['passed']}/{summary['total']} passed in {output.get('elapsed_seconds', '?')}s", file=sys.stderr)
        for r in output["results"]:
            status = "PASS" if r["pass"] else "FAIL"
            rate_str = f"{r['triggers']}/{r['runs']}"
            print(f"  [{status}] rate={rate_str} expected={r['should_trigger']}: {r['query'][:70]}", file=sys.stderr)

    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
