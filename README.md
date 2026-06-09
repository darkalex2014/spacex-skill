# my-skill-creator (Localized)

A localized fork of [anthropics/skills/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) for users in regions where the official Anthropic API is unavailable or for those who want to use a different model provider.

## What changed

- `scripts/improve_description.py` — replaced the `claude -p` subprocess call with a direct call to the [Anthropic Python SDK](https://github.com/anthropics/anthropic-sdk-python). Auth is read from environment variables.
- `scripts/run_eval.py` — same change. Trigger evaluation now calls the SDK in-process and inspects the response content blocks for a `consult_skill` tool_use, instead of spawning a `claude -p` subprocess and parsing stream-json events.

Upstream functionality is preserved:
- All CLI args (`--eval-set`, `--skill-path`, `--num-workers`, `--timeout`, `--runs-per-query`, `--max-iterations`, `--holdout`, `--model`, etc.) work the same way.
- `run_loop.py` (the orchestrator) is **unchanged** — it still imports the same function signatures from `run_eval` and `improve_description`.
- Output schemas (`evals.json`, `grading.json`, `benchmark.json`, `analysis.json`) are unchanged — the eval viewer (`eval-viewer/generate_review.py`) still works.
- The skill's agents (`analyzer.md`, `comparator.md`, `grader.md`) and references (`schemas.md`) are unchanged.

## Setup

### 1. Install dependencies

```bash
pip install anthropic
```

(`anthropic` is the only new dep; `pyyaml` and `requests` are already required by upstream.)

### 2. Configure environment variables

This fork uses the Anthropic Python SDK pointed at an Anthropic-compatible endpoint. Set the following env vars (User-level on Windows, or in your shell profile on Linux/Mac):

| Variable | Required | Default | Description |
|---|---|---|---|
| `ANTHROPIC_BASE_URL` | yes | (Anthropic's) | e.g. `https://api.minimaxi.com/anthropic` for MiniMax |
| `ANTHROPIC_API_KEY` | yes | — | Your API key |
| `LLM_MODEL` | no | `MiniMax-M2.7-highspeed` | Model used for trigger eval (fast, short responses) |
| `LLM_IMPROVE_MODEL` | no | falls back to `LLM_MODEL`, then `MiniMax-M3` | Model used for description rewriting (longer, more thoughtful) |

**Windows (PowerShell, no admin needed):**
```powershell
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_BASE_URL", "https://api.minimaxi.com/anthropic", "User")
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-cp-your-key-here", "User")
[System.Environment]::SetEnvironmentVariable("LLM_MODEL", "MiniMax-M2.7-highspeed", "User")
[System.Environment]::SetEnvironmentVariable("LLM_IMPROVE_MODEL", "MiniMax-M3", "User")
```

> **Note on env propagation:** Windows User-level env vars are read by new processes at launch time. If a process is already running (e.g. Mavis) when you set them, it won't see them in its env block. The `_get_client()` helper in both scripts reads from the registry as a fallback — but if you want zero ceremony, just open a new PowerShell before running the tools.

## Usage

Same as upstream:

```bash
# Just run trigger eval (no improvement loop):
python -m scripts.run_eval \
  --eval-set path/to/evals.json \
  --skill-path path/to/target-skill \
  --description "the description you want to test" \
  --num-workers 10 \
  --runs-per-query 3 \
  --verbose

# Run the full eval + improve loop:
python -m scripts.run_loop \
  --eval-set path/to/evals.json \
  --skill-path path/to/target-skill \
  --model MiniMax-M2.7-highspeed \
  --max-iterations 5 \
  --verbose
```

The `--model` arg now selects the **improve_description** model. Trigger eval uses `LLM_MODEL`. If you want both to use the same model, just set `LLM_MODEL` and pass `--model` to match (or omit `--model` from `run_eval`).

## Tested with

- Python 3.12
- `anthropic` SDK 0.107.1
- MiniMax-M2.7-highspeed, MiniMax-M3 via the Anthropic-compatible endpoint at `https://api.minimaxi.com/anthropic`
- Smoke test: 1 query, 1 tool_use, ~2s round trip. ✅

## Why "Localized"

The official skill-creator assumes you have `claude` (Claude Code's CLI) installed and authenticated. In regions where the Anthropic API is not directly available, or for users on a custom proxy / different provider, this assumption breaks. This fork:

1. **Removes the `claude` CLI dependency** entirely.
2. **Speaks plain Anthropic-protocol HTTP** via the official SDK, so any compatible endpoint works.
3. **Doesn't change the algorithm** — the eval / improve / aggregate / view pipeline is identical.

## Backporting upstream changes

If anthropics/skills updates their skill-creator, the cleanest way to merge is:

```bash
# Add the upstream as a remote
git remote add upstream https://github.com/anthropics/skills.git

# Fetch just the skill-creator subtree
git fetch upstream main

# Diff against your base commit
git log --oneline -1  # e.g. abc1234 (your last sync point)
git diff abc1234 upstream/main -- skills/skill-creator > upstream-changes.patch

# Inspect, then apply selectively
git apply --check upstream-changes.patch
# (don't auto-apply — you want to keep the localized _get_client and ignore upstream's _call_claude)
```

Files most likely to need re-syncing on each upstream bump:
- `SKILL.md` (the workflow doc — copy wholesale)
- `agents/analyzer.md`, `agents/comparator.md`, `agents/grader.md` (agent prompts — copy wholesale)
- `references/schemas.md` (copy wholesale)
- `scripts/utils.py`, `scripts/generate_report.py`, `scripts/aggregate_benchmark.py` (copy if changed)

Files you should **NOT** blindly overwrite:
- `scripts/improve_description.py` (you have your own `_call_llm` and `_get_client` here)
- `scripts/run_eval.py` (you have your own in-process trigger eval here)

## License

Inherits from upstream Apache 2.0.


## Run history (2026-06-09)

This fork was used to optimize 8 local 投标 skills end-to-end:

| Skill | Train (best) | Test (best) | Iterations |
|-------|--------------|-------------|------------|
| 投标评分点拆解 | 11/12 | 8/8 | 4 |
| 投标项目全流程管理 | 9/12 | 7/8 | 4 |
| 技术应答文件批量编制技能 | 12/12 | 7/8 | 5 (all_passed) |
| 差异化扩写Prompt模板 | 11/12 | 8/8 | 5 (all_passed) |
| Word文档扩写与标题优化 | 12/12 | 7/8 | 5 (all_passed) |
| 串标检测工程化封装 | 12/12 | 8/8 | 2 (all_passed) |
| 投标文件格式规范手册 | 12/12 | 8/8 | 4 (all_passed) |
| 招标资质快速识别与提取 | 12/12 | 8/8 | 1 (all_passed) |

See `examples/README.md` for a before/after frontmatter diff.
