<h1 align="center">Table Analysis：自我进化的表格分析 AI 智能体技能</h1>

<p align="center">
  <a href="README.md">English</a> · <strong>中文</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/pandas-2.1+-green.svg" alt="Pandas">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="MIT License">
</p>

> **千人千面 · 越用越强 · 终端原生**
>
> 一个面向对话式表格分析的 AI 智能体技能——拖入 CSV 或 Excel 文件，用自然语言说出你想要什么。它会先展示执行计划，再并行调度多个智能体处理你的表格，跨会话记住你的偏好，并从每次交互中提炼可复用技能。用得越多，它就越懂你。

---

## 与众不同之处

### 拿不准就先问
当你的请求存在多种合理解读时，智能体会暂停并列出简明的澄清选项，由你选择后再继续——不会在沉默中猜错方向。

### 先规划，再动手
在操作数据之前，智能体会生成分步执行计划并展示给你。你可以调整后确认执行。任务完成后还会自动复查，确保没有遗漏。

### 多智能体并行分析
当你提供多张表并提出对比类问题时，智能体自动为每张表分配独立的子智能体并行处理，最后汇总结论——一致之处标记为**共识**，存在分歧则标记为**分歧**。

### 越用越聪明
每完成一项有一定复杂度的任务，智能体都会回顾过程、总结规律，并将其提炼为可复用的技能。下次遇到类似问题时可直接调用。技能经历演化阶段：试探 → 萌芽 → 待确认 → 已确认。

### 记住你的习惯
智能体会捕捉你的工作偏好——常用指标、输出格式、领域术语——并通过三级记忆体系（HOT / WARM / COLD）将其沉淀为持久记忆，自动带入后续会话。

### 自我反思，自我纠正
每次多步骤任务完成后，智能体会在呈现结果前先评估自身输出。如果发现不足，自动修正。你的每一次纠正都会被记录，反复确认后晋升为永久规则。

---

## 架构

```
table-analysis/
├── SKILL.md                  # 智能体指令（< 500 行）
├── examples/                 # 测试用示例数据集
│   ├── sales_2023.csv
│   ├── employees.csv
│   ├── orders.csv
│   ├── products.csv
│   └── survey_nps.csv
├── references/
│   ├── operations.md         # 完整命令参考（16 种操作）
│   └── prompts.md            # 规划、反思、学习的提示词模板
└── scripts/
    ├── table_ops.py          # 封装 16 种 pandas 操作的 CLI 工具
    ├── analyze.py            # 快速数据画像
    ├── memory_mgr.py         # 三级记忆管理器（HOT/WARM/COLD）
    └── skill_store.py        # 带生命周期管理的技能存储
```

### 核心工作流

```
1. 加载        →  读取 HOT 记忆 + 检查已学技能（强制）
2. 澄清        →  如有歧义，向用户确认
3. 画像        →  运行 analyze.py 分析输入文件
4. 规划        →  展示执行计划，等待确认
5. 执行        →  使用脚本或内联 Python 逐步执行
6. 反思        →  自我评估结果（强制）
7. 呈现        →  结构化结论 + 关键发现
8. 学习        →  记录纠正、更新记忆、提炼技能（强制）
```

### 记忆架构

```
~/.table-analysis/
├── memory.json          # HOT：≤80 条，每次加载
├── corrections.json     # 最近 50 条纠正记录，带晋升追踪
├── domains/             # WARM：按领域存放，按上下文加载
└── archive/             # COLD：衰减的模式
```

### 技能生命周期

```
新模式 ──> 试探 ──(2次使用)──> 萌芽 ──(3次使用)──> 待确认
                                                       │
                                    用户确认 ───────────┘
                                         │
                                         v
 闲置90天 ──> 归档 <──(30天)── 已确认 ──(反思)──> 改进
```

---

## 快速开始

### 环境要求

Python 3.9+，安装以下依赖：

```bash
pip install pandas openpyxl numpy tabulate
```

### 安装

```bash
git clone https://github.com/YOUR_USERNAME/table-analysis.git

# 初始化三级记忆结构
python table-analysis/scripts/memory_mgr.py init
```

### 作为 Cursor 智能体技能使用

将 `table-analysis/` 文件夹复制或软链接到 Cursor 技能目录：

```bash
# 个人技能（所有项目可用）
cp -r table-analysis ~/.cursor/skills/table-analysis

# 或项目级技能
cp -r table-analysis .cursor/skills/table-analysis
```

当你向智能体提出表格/数据分析相关的需求时，它会自动检测并使用该技能。

### 独立脚本使用

这些脚本也可以脱离 AI 智能体独立运行：

```bash
# 数据画像
python scripts/analyze.py data.csv -f markdown

# 筛选行
python scripts/table_ops.py filter data.csv 'revenue > 100000' -f markdown

# 聚合
python scripts/table_ops.py aggregate data.csv --group-by region --agg revenue:sum profit:mean -f markdown

# 透视表
python scripts/table_ops.py pivot data.csv --index region --values revenue --pivot-columns quarter -f markdown
```

---

## 16 种内置操作

| 操作 | 说明 |
|------|------|
| `info` | 表元数据：形状、列名、类型、缺失值 |
| `filter` | 使用 pandas 查询表达式筛选行 |
| `select` | 选择列子集 |
| `aggregate` | 分组聚合（sum、mean、count、min、max 等） |
| `sort` | 按一列或多列排序 |
| `merge` | 合并/连接两张表（inner、left、right、outer） |
| `pivot` | 创建透视表 |
| `add-column` | 通过表达式添加计算列 |
| `describe` | 描述性统计（计数、均值、标准差、分位数） |
| `find` | 按精确值或正则表达式查找行 |
| `dedup` | 去除重复行 |
| `rename` | 重命名列 |
| `sample` | 随机抽样 N 行 |
| `value-counts` | 列值频次统计 |
| `correlation` | 皮尔逊相关矩阵 |
| `head` | 前 N 行 |

所有操作支持 CSV、Excel (.xlsx/.xls)、TSV、JSON、Parquet 输入格式，输出支持 CSV、Markdown、JSON。

---

## 自我进化系统

该技能实现了完整的自我改进闭环，灵感来自 [self-improving](https://github.com/openclaw/openclaw) 智能体模式：

- **纠正追踪** — 用户的每次纠正都会记录类型、次数和时间戳。同一纠正出现 3 次后自动晋升为永久记忆。
- **分级记忆** — HOT（常驻加载，≤80 条）、WARM（按领域加载）、COLD（归档，仅显式查询时加载）。基于使用频率自动晋升/降级。
- **技能蒸馏** — 成功完成多步骤任务后，自动提取可复用的分析模式。技能经历完整生命周期（试探 → 已确认），闲置的技能自动衰减归档。
- **自我反思** — 每次任务后强制自我评估，在呈现结果前检查是否真正回答了用户的问题、方法是否高效。
- **透明性** — 使用已学习的偏好或模式时，始终引用来源（如"使用 Markdown 格式，来自 HOT 记忆"）。

---

## 示例数据集

`examples/` 目录包含用于测试的示例数据：

| 文件 | 说明 |
|------|------|
| `sales_2023.csv` | 358 行销售数据（区域、产品、收入、利润等） |
| `employees.csv` | 85 行员工数据（部门、薪资、绩效等） |
| `orders.csv` | 订单记录（客户、产品详情） |
| `products.csv` | 产品目录（分类、定价） |
| `survey_nps.csv` | NPS 调查问卷回复 |

---

## 致谢

本项目深受 [**TabClaw**](https://github.com/fishsure/TabClaw) 的启发。TabClaw 是由中国科学技术大学认知智能全国重点实验室团队开发的交互式表格分析 AI 智能体。其"先规划后执行、多智能体并行分析、技能学习、持久记忆"的设计哲学直接塑造了本技能的架构。

自我进化机制借鉴了 [OpenClaw](https://github.com/openclaw/openclaw) 的 [**self-improving**](https://clawic.com/skills/self-improving) 智能体技能模式，该模式开创了面向 AI 智能体的分级记忆、纠正追踪和技能生命周期管理方法。

### 引用

```bibtex
@misc{tabclaw2026,
  title        = {TabClaw: A Local AI Agent for Conversational Table Analysis},
  author       = {Yu, Shuo and Wang, Daoyu and Li, Qingchuan and Tao, Xiaoyu and Mao, Qingyang and Zhou, Yitong and Cheng, Mingyue and Liu, Qi and Chen, Enhong},
  year         = {2026},
  howpublished = {\url{https://github.com/fishsure/TabClaw}}
}
```

---

## 许可证

MIT
