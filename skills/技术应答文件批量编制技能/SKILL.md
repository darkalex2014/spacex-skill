---
name: 技术应答文件批量编制技能
description: |
  生成或扩写技术应答文件，支持单公司模式和多公司差异化模式（主公司/A公司/B公司防围标串标）。

Use this skill when you need to: generate complete technical bid documents from scratch; create differentiated versions for multiple affiliated bidding companies; expand draft chapters to meet minimum word counts; detect and rewrite plagiarized/collusive passages in multi-company bids.

Do NOT use this skill for: document formatting (fonts, headers, footers, margins); project scheduling or task breakdown from scoring tables; evaluating company qualifications or matching products to requirements.

---

# 技术应答文件批量编制技能

## 技能描述

生成技术应答文件，支持单公司模式和多公司差异化模式，适用于投标场景全生命周期。

**前置依赖**：本技能的"生成应答文件"模块依赖 **SKILL-投标评分点拆解** 的评分点分析结果——必须先拆解评分点，再基于评分点生成应答文件章节，确保每个得分点都有对应应答内容。

---

## 模式选择

| 模式 | 说明 | 触发条件 |
|------|------|---------|
| **单公司模式** | 只写主公司一份文件，无需差异化 | 招标文件要求单一主体应答 |
| **多公司模式** | 主公司 + A/B/AB 公司，多份差异化 | 围标要求多家主体、陪标、需要拉多公司凑数 |

**判断依据**：看招标文件要求几家主体应答，再决定走哪个模式。

---

## 单公司模式

只需主公司一份文件，直接基于招标技术要求生成应答文档。

**流程**：
```
读取招标文件（技术要求）.docx
↓
提取章节结构 + 关键参数
↓
生成主公司技术应答文件（V5.docx）
↓
验证章节完整性 + 关键参数一致性
↓
交付
```

**适用项目**：江西银行、中石油等项目（单一主体投标）

---

## 多公司模式

主公司 + A/B 公司，多份文件需要差异化表述，防止围标串标审查。

**差异化策略组合**：

| 公司 | 开篇 | 叙述风格 | 段落组织 | 表格形式 |
|------|------|---------|---------|---------|
| 主公司（基准） | A-1 业务本质分析 | B-1 传统严谨 | C-1 自然段落 | D-1 标准行列 |
| 公司A | A-2 项目定位理解 | B-2 深度展开 | C-2 分段论述 | D-2 网格行列 |
| 公司B | A-3 核心要点概括 | B-3 简洁概括 | C-3 分点罗列 | D-3 总分/分项 |

**完整流程**：
```
1. 读取主公司V4.docx（基准版）
2. 提取章节结构树 + 关键技术参数
3. 按差异化策略生成 A/B 版本
4. 运行串标检测（≥70% 相似度标红）
5. 对雷同段落执行五倍扩写
6. 输出：公司A_V5.docx、公司B_V5.docx
7. 输出检测报告
8. 交付前：AB/ 子目录统一存档
```

**适用项目**：国网信通（主公司 + 亿力科技 + 其他关联公司）

---

## 项目目录规范

### 目录结构模板

```
06标书制作专区/
└── [项目名称]/
    ├── [主公司]V4.docx          # 主参考文件
    ├── [主公司]V4_content.md    # 主文件文本内容（用于脚本处理）
    ├── [主公司]V5.docx          # 当前版本
    ├── [主公司]V5_内容.txt      # 当前版本纯文本
    ├── [公司A]技术应答文件V5.docx
    ├── [公司B]技术应答文件V5.docx
    ├── [公司A]_技术应答文件_新.docx  # 扩写中间版
    ├── [公司B]_技术应答文件_新.docx
    ├── regenerate_v5.py         # 批量重新生成脚本
    ├── generate_companyA_v5.py  # 公司A专属脚本
    ├── generate_companyB_v5.py   # 公司B专属脚本
    ├── [标书原始文件].docx       # 招标方技术要求文件
    └── info/                    # 参考资料
        ├── 一标/
        └── 二标/
```

### 版本命名规则

| 版本 | 用途 | 命名示例 |
|------|------|---------|
| V4 | 主参考文件（基准版） | 主公司V4.docx |
| V5 | 当前交付版 | 主公司V5.docx |
| _扩写版 | 中间处理版本 | 技术应答文件_扩写版_第26-28章.docx |
| _扩写版_expanded | 扩写后版本 | 技术应答文件_扩写版_第26-28章_expanded.md |
| _new | 脚本处理中间产物 | xxx.docx.new |
| backup_日期时间 | 自动备份 | xxx.docx.backup.20260515225931 |
| bak | 手动备份 | 技术应答文件-主公司_bak.docx |

### 备份规范

```
每次脚本处理前：自动创建 .backup.时间戳 备份
每次交付前：手动创建 _bak 备份
重要版本节点：复制一份到 AB/ 子目录统一管理
```

---

## 完整工作流

### 模块一：文件生成（主公司 → 多公司差异化）

#### 差异化策略库

**开篇方式**

| 代号 | 策略 | 适用场景 |
|------|------|---------|
| A-1 | 业务本质分析 | 强调行业背景和需求痛点 |
| A-2 | 项目定位理解 | 强调战略意义和价值目标 |
| A-3 | 核心要点概括 | 强调关键环节和重点任务 |
| A-4 | 问题导向切入 | 强调痛点分析和解决方案 |

**叙述风格**

| 代号 | 策略 | 特征 |
|------|------|------|
| B-1 | 传统严谨 | 长复合句、完整论证、层层递进 |
| B-2 | 深度展开 | 中长段落、多角度论述、细节丰富 |
| B-3 | 简洁概括 | 短句分点、直击要点、重点突出 |
| B-4 | 案例实证 | 引用案例、数据支撑、实证分析 |

**段落组织**

| 代号 | 策略 | 呈现特点 |
|------|------|---------|
| C-1 | 自然段落式 | 段落完整、逻辑连贯 |
| C-2 | 分段论述式 | 段落分明、角度多样 |
| C-3 | 分点罗列式 | 要点明确、层次清晰 |
| C-4 | 混合组织式 | 段落与列表结合 |

**表格形式**

| 代号 | 策略 | 呈现形式 |
|------|------|---------|
| D-1 | 标准行列式 | 横向排列、清晰简洁 |
| D-2 | 网格行列式 | 行列网格、增强可读性 |
| D-3 | 总分结构式 | 先总览后明细、层次分明 |
| D-4 | 分项列表式 | 分项独立、关联呈现 |

#### 典型策略组合

**主公司（基准）**：
- A-1 + B-1 + C-1 + D-1

**公司A（差异化）**：
- A-2 + B-2 + C-2 + D-2

**公司B（高度差异化）**：
- A-3 + B-3 + C-3 + D-3/D-4

#### 必保一致的参数

| 参数类别 | 示例 | 规则 |
|---------|------|------|
| 工作量 | 24人·月 | 数值完全一致 |
| 工期 | 6个月 | 数值完全一致 |
| 性能指标 | 200笔/秒、200毫秒 | 数值完全一致 |
| 可用性 | 99.9% | 数值完全一致 |
| 安全标准 | HTTPS+TLS1.2、AES-256 | 标准代号一致 |
| 服务承诺 | 7×24小时、24小时恢复 | 数值完全一致 |

---

### 模块二：围标串标检测

#### 检测维度

| 检测项 | 方法 | 阈值 |
|--------|------|------|
| 句子相似度 | 8-gram重叠率 | ≥70% → 疑似 |
| 段落雷同 | 连续相同字符≥20个 | 直接标红 |
| 100%雷同 | 文字完全一致 | 最高风险 |
| 关键词重叠 | 高频业务词组共现 | 出现在2份以上 |

#### 关键词风险分级

| 风险 | 关键词类型 |
|------|---------|
| 🔴 高 | 项目经理、技术负责人、自有人员、正式员工 |
| 🔴 高 | 项目组、核心组织单元、全过程管理 |
| 🔴 高 | 分层架构、分布式架构、高可用 |
| 🔴 高 | HA技术、故障侦测、主备切换 |
| 🟡 中 | 并发处理能力、响应时间、弹性扩缩容 |
| 🟡 中 | 安全第一、质量管理、进度计划 |

#### 检测脚本模式

```python
import zipfile, re

def extract_text_from_docx(filepath):
    """提取DOCX正文文本"""
    with zipfile.ZipFile(filepath, 'r') as z:
        with z.open('word/document.xml') as f:
            tree = ET.parse(f)
            return ''.join(e.text for e in tree.iter() if e.tag.endswith('}t') and e.text)

def ngram_similarity(s1, s2, n=8):
    """计算n-gram重叠率"""
    def get_ngrams(s, n):
        return set(s[i:i+n] for i in range(len(s)-n+1))
    ng1 = get_ngrams(s1, n)
    ng2 = get_ngrams(s2, n)
    if not ng1 or not ng2:
        return 0
    return len(ng1 & ng2) / max(len(ng1), len(ng2))
```

---

### 模块三：差异化扩写

#### 扩写原则（五倍扩写法）

| 维度 | 扩写方法 |
|------|---------|
| 背景维度 | 增加历史背景、行业环境、现实需求描述 |
| 现状维度 | 增加市场现状、数据统计、参与主体分析 |
| 目标维度 | 增加战略目标、量化指标、验收条件描述 |
| 措施维度 | 增加具体任务、实施路径、责任主体说明 |
| 技术维度 | 增加技术路线、架构设计、部署方案细节 |
| 保障维度 | 增加组织保障、制度保障、人才保障措施 |

#### 扩写比例要求

| 雷同程度 | 扩写目标 |
|---------|---------|
| 100%完全雷同 | 深度扩写5倍以上 |
| 90%-99%高度雷同 | 扩写4倍以上 |
| 70%-89%中度雷同 | 扩写2倍以上 |

#### 扩写示例

**原雷同段落**：
> 项目经理、技术负责人、安全管理等关键岗位人员必须为我司自有人员，且必须为正式员工。

**扩写版本A**（B-2深度展开风格）：
> 关于关键岗位人员配置，我公司设定如下准入标准：项目经理须为本公司正式员工，具备PMP认证资质及三年以上同类大型项目管理经验，近五年内担任过不少于5个同等规模项目的项目经理职务；技术负责人须为本公司正式员工，应持有系统架构师或软件评测师等专业资质认证；安全管理人员须为本公司正式员工，具备CISP或CISSP认证资质。上述人员均需与本公司签订正式劳动合同并缴纳社保，禁止以劳务派遣、外包或挂靠形式替代。

**扩写版本B**（B-3简洁概括风格）：
> 关键岗位人员配置要求：项目经理须具PMP+3年经验，技术负责人须具系统架构师资质，安全管理员须具CISP/CISSP认证，所有人员须为本公司正式员工，禁止外包。

---

### 模块四：章节扩写（expand_sections模式）

用于对招标文件的特定章节进行方法论级扩充。

#### 脚本命名规范

| 脚本 | 用途 |
|------|------|
| `expand_sections_v2.py` | 基础章节扩写 |
| `expand_sections_5x.py` | 五倍扩写版本（更详细） |
| `extract_docx.py` | 从DOCX提取文本内容 |
| `improve_technical_section.py` | 优化技术章节 |
| `update_scenario_mapping.py` | 更新场景映射 |

#### 扩写章节结构

```
章节X.X 名称
├── X.X.X 方法论概述
│   ├── 方法论介绍
│   └── 本项目应用方案
├── X.X.X 执行明细
│   ├── 子任务一
│   │   ├── 步骤1
│   │   ├── 步骤2
│   │   └── 步骤3
│   └── 子任务二
└── X.X.X 交付成果
    ├── 核心交付物
    └── 过程交付物
```

---

## 版本管理流程

### V4 → V5 迭代规范

```
1. 读取主公司V4.docx
2. 创建 backup.V4 时间戳备份
3. 按差异化策略生成V5
4. 运行串标检测
5. 如有雷同 → 执行扩写
6. 生成V5.docx
7. 同时生成 V5_内容.txt（纯文本备查）
```

### 多轮修订流程

```
需求变更 → regenerate_*.py 重新生成 → check_*.py 验证 → 交付
```

**常用验证脚本**：

| 脚本 | 用途 |
|------|------|
| `check_sizes.py` | 检查各章节字数是否均衡 |
| `check_structure.py` | 验证章节结构完整性 |
| `check_expanded.py` | 验证扩写是否充分 |
| `verify_doc.py` | 综合验证DOCX |
| `verify_chapters.py` | 按章节验证完整性 |

---

## 输出规范

### 文件命名规范

```
[公司名][产品]V[版本号].[扩展名]
示例：
  主公司V5.docx
  公司A技术应答文件V5.docx
  公司B技术应答文件V5.docx
  技术应答文件_扩写版_第26-28章_expanded.md
```

### 检测报告格式

```markdown
## 围标串标分析报告

### 文件概览
| 文件 | 字符数 | 主要内容 |

### 疑似围标串标证据
#### 共用雷同词组
| 关键词 | 涉及文件数 | 风险等级 |

#### 高度相似段落
| # | 内容摘要 | 相似度 | 来源文件 |
|---|---------|--------|---------|
```

---

## 调用模板

### 单公司模式
```
用户：基于招标文件生成[项目名]的应答文件
助手：
  1. 读取招标文件（技术要求）.docx
  2. 提取章节结构 + 关键参数
  3. 生成主公司技术应答文件
  4. 验证完整性
  5. 输出：主公司V5.docx
```

### 多公司模式
```
用户：基于主公司V5.docx，生成公司A和公司B的差异化版本
助手：
  1. 读取主参考文件，提取章节结构树
  2. 提取关键技术参数清单
  3. 为公司A应用 A-2+B-2+C-2+D-2 策略
  4. 为公司B应用 A-3+B-3+C-3+D-3 策略
  5. 执行串标检测（≥70%相似度标红）
  6. 对雷同段落执行五倍扩写
  7. 输出：公司A_V5.docx、公司B_V5.docx
  8. 输出检测报告
```

---

## DOCX 脚本模式参考

本技能使用的 Python 脚本遵循以下通用模式，来自投标项目积累：

### 内容提取（extract_docx.py）

```python
# 提取DOCX全部内容为JSON结构
from docx import Document
import json

def extract_docx(docx_path):
    doc = Document(docx_path)
    result = {"paragraphs": [], "tables": []}
    for p in doc.paragraphs:
        result["paragraphs"].append({
            "style": p.style.name,
            "text": p.text,
            "alignment": str(p.alignment)
        })
    for tbl in doc.tables:
        result["tables"].append([[c.text for c in row.cells] for row in tbl.rows])
    return result
```

### 样式深度检查（inspect_styles.py）

```python
# 直接读取DOCX内部XML检查字体/字号/行距
import zipfile, re

def inspect_styles(docx_path):
    with zipfile.ZipFile(docx_path, 'r') as z:
        styles_xml = z.read('word/styles.xml').decode('utf-8')
        doc_xml = z.read('word/document.xml').decode('utf-8')
    # 用正则提取 w:ascii w:hAnsi w:eastAsia sz spacing 等属性
    # 提取 pgSz(页面尺寸) pgMar(页边距)
```

### 章节定位插入（improve_technical_section.py）

```python
# 找到关键词段落，在其后插入格式化内容和表格
from docx import Document
from docx.shared import Pt, Cm
from docx.oxml.ns import qn

def insert_after_keyword(doc, keyword, new_content):
    for i, p in enumerate(doc.paragraphs):
        if keyword in p.text:
            # 逆序插入（防止index偏移）
            for j, item in enumerate(reversed(new_content)):
                p.insert_paragraph_before(item)
```

### 术语批量修正（correct_bid_document.py）

```python
# 遍历全部段落，应用上下文感知的术语替换和补充插入
# 原则：检查邻接段落避免重复插入
def batch_correct(doc):
    corrections = [
        ("11类", "11+N类"),
        ("1个月", "合同签订后1个月内"),
    ]
    for p in doc.paragraphs:
        for old, new in corrections:
            if old in p.text:
                p.text = p.text.replace(old, new)
```

### 文档重建（regenerate_v*.py）

```python
# python-docx删除元素复杂时，从头重建文档
from docx import Document

def rebuild_doc(input_path, output_path):
    old_doc = Document(input_path)
    new_doc = Document()
    for p in old_doc.paragraphs:
        # 过滤+重组，输出到new_doc
    new_doc.save(output_path)
```

### 表格创建

```python
# 带表头底色的表格
table = doc.add_table(rows=1, cols=n)
table.style = 'Table Grid'
header = table.rows[0].cells
for cell in header:
    cell._tc.get_or_add_tcPr().append(shading_element)
```

---

## 注意事项

1. **参数一致性**：关键技术参数（人·月、工期、毫秒、%）数值必须完全一致
2. **每次处理前备份**：脚本会自动创建 .backup.时间戳，无需手动备份
3. **DOCX是ZIP**：读取时用zipfile，解压后操作word/document.xml
4. **扩写不偏离业务**：扩写基于原始素材延展，不改变业务语义
5. **检测阈值可调**：70%相似度为建议值，可根据招标要求调整

---

## 下一步建议（路由到下游技能）

生成应答初稿后，建议按顺序调用以下下游技能完善投标文件：

1. **差异化扩写Prompt模板**（多公司模式时必选）— 对雷同段落做 B-1/B-2/B-3/B-4 风格化扩写，防围标串标
2. **Word文档扩写与标题优化技能**（单公司或多公司初稿完成后）— 对单个章节做五倍深度扩写 + 标题精简到三级
3. **投标文件格式规范手册**（提交前必选）— 对字体字号、行距、页眉页脚做格式自检
4. **串标检测工程化封装**（终版提交前必选）— 多公司模式下做围标合规性自检

---

**版本**：v3.0 (2026-05-27) - 整合版本管理规范，新增expand_sections扩写模式，补全目录结构模板
