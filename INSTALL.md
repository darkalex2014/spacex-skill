# Installation

This repo contains 8 production-ready 投标 (tender) skills plus the tool
used to optimize them. Pick what you need.

## Option A: Use the skills in Mavis / Claude Code

Each skill under `skills/` is a self-contained directory. To install one:

```bash
# Mavis (recommended location on Windows)
cp -r skills/投标评分点拆解 ~/.minimax/skills/

# Or Claude Code (any Anthropic-compatible runtime that loads from .claude/skills/)
cp -r skills/投标评分点拆解 ~/.claude/skills/
```

Restart Mavis / Claude Code — the skill becomes available as `投标评分点拆解`.

To install all 8:

```bash
cp -r skills/* ~/.minimax/skills/
```

## Option B: Use the tool to optimize your own skills

```bash
cd tools/my-skill-creator
pip install anthropic

# Set env vars (User-level on Windows, or shell profile on Linux/Mac)
export ANTHROPIC_BASE_URL="https://api.minimaxi.com/anthropic"
export ANTHROPIC_API_KEY="<your-key>"
export LLM_MODEL="MiniMax-M2.7-highspeed"
export LLM_IMPROVE_MODEL="MiniMax-M3"

# Write 20-query evals (10 should + 10 should_not)
# Then run the loop
python scripts/run_loop.py \
  --skill-path /path/to/your-skill \
  --eval-set /path/to/evals.json \
  --num-workers 2 \
  --max-iterations 5 \
  --holdout 0.4 \
  --model MiniMax-M2.7-highspeed
```

See `tools/my-skill-creator/README.md` for full documentation.

## What "optimized" means

Each skill in `skills/` was run through 5 iterations of `run_loop.py`
against MiniMax-M2.7-highspeed as the trigger judge. Heldout accuracy
on 8 queries (40% of 20) is the key number — see the table in the root
README.
