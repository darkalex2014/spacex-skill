# spacex-skill

A collection of 8 production-ready 投标 (Chinese tender) skills, plus the
tool used to optimize them.

## What's in here

```
spacex-skill/
├── tools/my-skill-creator/    Localized skill-description optimizer (Anthropic SDK + MiniMax)
├── skills/                    8 optimized 投标 skills, ready to install
│   ├── 投标评分点拆解/
│   ├── 投标项目全流程管理/
│   ├── 技术应答文件批量编制技能/
│   ├── 差异化扩写Prompt模板/
│   ├── Word文档扩写与标题优化技能/
│   ├── 串标检测工程化封装/
│   ├── 投标文件格式规范手册/
│   └── 招标资质快速识别与提取/
├── examples/                  Before/after frontmatter diff for one skill
├── INSTALL.md                 How to install skills or use the tool
├── LICENSE.txt                Apache 2.0
└── README.md
```

## Quick start

```bash
# Install one skill (Mavis on Windows)
cp -r skills/投标评分点拆解 ~/.minimax/skills/

# Or all 8
cp -r skills/* ~/.minimax/skills/
```

See [INSTALL.md](./INSTALL.md) for details.

## The 8 skills

| Skill | Purpose | Heldout test score |
|-------|---------|--------------------|
| 投标评分点拆解 | Parse scoring rubric into per-item task list, mapped to response chapters | 8/8 |
| 投标项目全流程管理 | Lifecycle: pre-tender decision → in-flight execution → post-mortem | 7/8 |
| 技术应答文件批量编制技能 | Generate technical response, single-company or A/B multi-company mode | 7/8 |
| 差异化扩写Prompt模板 | B-1/B-2/B-3/B-4 style prompts to defeat bid-rigging similarity | 8/8 |
| Word文档扩写与标题优化技能 | 5x expand + 3-level heading trim, single-company mode | 7/8 |
| 串标检测工程化封装 | 5-dim bid-rigging audit: business registry, related-party, IP/MAC, file fingerprint, quote anomaly | 8/8 |
| 投标文件格式规范手册 | Font/spacing/margin/seal/binding spec + Python self-check script | 8/8 |
| 招标资质快速识别与提取 | A-class hard threshold / B-class bonus / C-class format separation | 8/8 |

Each skill was tuned for trigger accuracy against MiniMax-M2.7-highspeed
using `tools/my-skill-creator` to iterate 5 rounds with 40% heldout.
Heldout size: 8 queries. Train size: 12.

## The tool

`tools/my-skill-creator/` is a localized fork of
[anthropics/skills/skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator).
It runs trigger eval + iterative description improvement against any
Anthropic-compatible endpoint (default: MiniMax).

Auth: `ANTHROPIC_BASE_URL` + `ANTHROPIC_API_KEY` env vars.
Model: `LLM_MODEL` (default `MiniMax-M2.7-highspeed`).

See [INSTALL.md](./INSTALL.md) and [tools/my-skill-creator/README.md](./tools/my-skill-creator/README.md).

## Why

The official skill-creator assumes `claude` CLI is installed. In regions
where the Anthropic API is not directly available, this assumption breaks.
This fork:

1. Removes the `claude` CLI dependency.
2. Speaks plain Anthropic-protocol HTTP via the SDK.
3. Doesn't change the algorithm.

## License

Apache 2.0. See [LICENSE.txt](./LICENSE.txt).
