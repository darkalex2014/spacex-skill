# Examples

## before-after: 投标评分点拆解

This shows what `run_loop` produces when optimizing one skill's frontmatter.

### Before (iter 0, original)

```yaml
description: 为多公司投标模式提供可直接使用的差异化扩写 Prompt 模板。
```

### After (iter 5, optimized)

```yaml
description: |
  投标评分点拆解——将评分标准逐条解析为可执行的应答任务清单，
  映射到应答文件章节，识别覆盖风险。
  适用：评分项满分/评分标准提取、强项弱项识别、章节映射。
  上游：招标资质快速识别与提取。
  下游：技术应答文件批量编制技能。
  不适用于：投标后复盘分析、文档内容提取、差异化创新策略、...
```

### Result

- **Train:** 11/12 → 11/12 → 11/12 → 11/12 → 11/12
- **Test (heldout):** 5/8 → 7/8 → 7/8 → **8/8 (iter 4)**
- **All passed:** iteration 4

### How to reproduce

```bash
# 1) Write 20-query evals.json (10 should_trigger + 10 should_not_trigger)
# 2) Run the loop
python scripts/run_loop.py \
  --skill-path /path/to/your-skill \
  --eval-set /path/to/evals.json \
  --model MiniMax-M2.7-highspeed \
  --max-iterations 5 \
  --holdout 0.4 \
  --num-workers 2
```

The script saves `results.json`, `report.html`, and per-iteration improve logs
to a timestamped subdirectory under `--results-dir`.
