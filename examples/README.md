# Examples

## Before / After: 投标评分点拆解 frontmatter

This is a real example of what `tools/my-skill-creator` produces when
iterating on a skill's description.

### Before (original)

```yaml
description: 投标评分点拆解——将评分标准逐条解析为可执行的应答任务清单。
```

### After (iter 4, all_passed)

```yaml
description: |
  投标场景下，将招标文件的评分标准逐条解析为可执行的应答任务清单，映射到应答文件章节，识别覆盖风险。
  适用：评分项满分/评分标准提取、强项弱项识别、章节映射、覆盖风险检查。
  上游：招标资质快速识别与提取。
  下游：技术应答文件批量编制技能。
  不适用于：投标后复盘分析、文档内容提取、差异化创新策略、产品匹配、资质预算分析。
```

### Iteration history

| Iter | Train | Test (heldout) | Notes |
|------|-------|----------------|-------|
| 1    | 9/12  | 5/8            | initial handwritten seed |
| 2    | 10/12 | 7/8            | improved exclusion clauses |
| 3    | 9/12  | 6/8            | regressed on test |
| 4    | 9/12  | **8/8**        | best — adopted |

Heldout size: 8 (40% of 20). Train size: 12.

### How to reproduce

```bash
# 1) Write 20-query evals.json (10 should_trigger + 10 should_not_trigger)
# 2) Run the loop
cd tools/my-skill-creator
python scripts/run_loop.py \
  --skill-path ../../skills/投标评分点拆解 \
  --eval-set ../../skills/投标评分点拆解/evals/evals.json \
  --results-dir ./results \
  --num-workers 2 \
  --max-iterations 5 \
  --holdout 0.4 \
  --model MiniMax-M2.7-highspeed
```

The script saves `results.json`, `report.html`, and per-iteration improve
logs to a timestamped subdirectory.
