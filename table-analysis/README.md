<h1 align="center">Table Analysis: Self-Improving AI Agent Skill for Tabular Data</h1>

<p align="center">
  <strong>English</strong> · <a href="README_zh.md">中文</a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python 3.9+">
  <img src="https://img.shields.io/badge/pandas-2.1+-green.svg" alt="Pandas">
  <img src="https://img.shields.io/badge/license-MIT-orange.svg" alt="MIT License">
</p>

> **Personalized. Self-evolving. Terminal-native.**
>
> An AI agent skill for conversational table analysis — drop in a CSV or Excel file and describe what you want in natural language. It plans before acting, runs parallel agents across multiple tables, remembers your preferences across sessions, and distills reusable skills from every interaction. The more you use it, the smarter it gets.

---

## What Makes This Different

### It asks when it's not sure
If a request could mean several different things, the agent pauses and presents clarification options before proceeding. No silent wrong assumptions.

### It plans before it acts
Before touching your data, the agent drafts a step-by-step execution plan and shows it to you. You can adjust, then approve and execute. After finishing, it does a self-check to make sure nothing was missed.

### It runs multiple agents in parallel
When you provide multiple tables and ask a comparative question, the agent automatically dispatches parallel sub-agents — one per table — then synthesizes findings, highlighting **consensus** and **divergence**.

### It learns from every session
After completing a non-trivial task, the agent reflects on what it did and distills the pattern into a reusable skill. Next time you ask something similar, it applies that skill directly. Skills evolve through stages: tentative → emerging → pending → confirmed.

### It remembers your preferences
The agent picks up on how you like to work — preferred metrics, output format, domain terminology — and carries that context into every future session via tiered memory (HOT / WARM / COLD).

### It self-reflects and self-corrects
After every multi-step task, the agent evaluates its own output before presenting it. If gaps are found, it fixes them automatically. Every correction from you is logged and promoted into permanent rules after repeated confirmation.

---

## Architecture

```
table-analysis/
├── SKILL.md                  # Agent instructions (< 500 lines)
├── examples/                 # Sample datasets for testing
│   ├── sales_2023.csv
│   ├── employees.csv
│   ├── orders.csv
│   ├── products.csv
│   └── survey_nps.csv
├── references/
│   ├── operations.md         # Full command reference (16 operations)
│   └── prompts.md            # Prompt templates for planning, reflection, learning
└── scripts/
    ├── table_ops.py          # CLI wrapping 16 pandas operations
    ├── analyze.py            # Quick table profiling
    ├── memory_mgr.py         # Tiered memory manager (HOT/WARM/COLD)
    └── skill_store.py        # Learned skill store with lifecycle management
```

### Core Workflow

```
1. LOAD        →  Read HOT memory + check learned skills (mandatory)
2. CLARIFY     →  If ambiguous, ask the user
3. PROFILE     →  Run analyze.py on input files
4. PLAN        →  Present execution plan, wait for approval
5. EXECUTE     →  Run steps using scripts or inline Python
6. REFLECT     →  Self-evaluate the outcome (mandatory)
7. PRESENT     →  Structured conclusion with key findings
8. LEARN       →  Log corrections, update memory, distill skills (mandatory)
```

### Memory Architecture

```
~/.table-analysis/
├── memory.json          # HOT: ≤80 entries, always loaded
├── corrections.json     # Last 50 corrections with promotion tracking
├── domains/             # WARM: per-domain, loaded on context match
└── archive/             # COLD: decayed patterns
```

### Skill Lifecycle

```
New pattern ──> tentative ──(2 uses)──> emerging ──(3 uses)──> pending
                                                                  │
                                        user confirms ────────────┘
                                             │
                                             v
 unused 90d ──> archived <──(30d)── confirmed ──(reflection)──> improved
```

---

## Quick Start

### Prerequisites

Python 3.9+ with the following packages:

```bash
pip install pandas openpyxl numpy tabulate
```

### Setup

```bash
git clone https://github.com/YOUR_USERNAME/table-analysis.git

# Initialize tiered memory structure
python table-analysis/scripts/memory_mgr.py init
```

### As a Cursor Agent Skill

Copy or symlink the `table-analysis/` folder to your Cursor skills directory:

```bash
# Personal skill (available in all projects)
cp -r table-analysis ~/.cursor/skills/table-analysis

# Or project-level skill
cp -r table-analysis .cursor/skills/table-analysis
```

The agent will automatically detect and use this skill when you ask about table/data analysis tasks.

### Standalone Script Usage

The scripts also work independently without an AI agent:

```bash
# Profile a dataset
python scripts/analyze.py data.csv -f markdown

# Filter rows
python scripts/table_ops.py filter data.csv 'revenue > 100000' -f markdown

# Aggregate
python scripts/table_ops.py aggregate data.csv --group-by region --agg revenue:sum profit:mean -f markdown

# Pivot table
python scripts/table_ops.py pivot data.csv --index region --values revenue --pivot-columns quarter -f markdown
```

---

## 16 Built-in Operations

| Operation | Description |
|-----------|-------------|
| `info` | Table metadata: shape, columns, dtypes, missing values |
| `filter` | Filter rows with pandas query expressions |
| `select` | Select a subset of columns |
| `aggregate` | Group by + aggregate (sum, mean, count, min, max, etc.) |
| `sort` | Sort by one or more columns |
| `merge` | Join/merge two tables (inner, left, right, outer) |
| `pivot` | Create pivot tables |
| `add-column` | Add computed columns via expressions |
| `describe` | Descriptive statistics (count, mean, std, quartiles) |
| `find` | Find rows by exact value or regex pattern |
| `dedup` | Remove duplicate rows |
| `rename` | Rename columns |
| `sample` | Random sample of N rows |
| `value-counts` | Frequency counts for a column |
| `correlation` | Pearson correlation matrix |
| `head` | First N rows |

All operations support CSV, Excel (.xlsx/.xls), TSV, JSON, and Parquet input formats, with output in CSV, Markdown, or JSON.

---

## Self-Improvement System

The skill implements a complete self-improvement loop inspired by [self-improving](https://github.com/openclaw/openclaw) agent patterns:

- **Correction Tracking** — Every user correction is logged with type, count, and timestamp. After 3 identical corrections, the pattern is promoted to permanent memory.
- **Tiered Memory** — HOT (always loaded, ≤80 entries), WARM (domain-specific, loaded on match), COLD (archived, loaded on explicit query). Automatic promotion and demotion based on usage frequency.
- **Skill Distillation** — Reusable analysis patterns are extracted after successful multi-step tasks. Skills evolve through a lifecycle (tentative → confirmed) with decay for unused patterns.
- **Self-Reflection** — Mandatory self-evaluation after every task, before presenting results. The agent checks whether the result actually answers the question and whether the approach was efficient.
- **Transparency** — When applying a learned preference or pattern, the agent always cites the source (e.g., "Using markdown format from HOT memory").

---

## Example Datasets

The `examples/` directory includes sample datasets for testing:

| File | Description |
|------|-------------|
| `sales_2023.csv` | 358 rows of sales data (region, product, revenue, profit, etc.) |
| `employees.csv` | 85 rows of employee data (department, salary, performance, etc.) |
| `orders.csv` | Order records with customer and product details |
| `products.csv` | Product catalog with categories and pricing |
| `survey_nps.csv` | NPS survey responses |

---

## Acknowledgements

This project is deeply inspired by [**TabClaw**](https://github.com/fishsure/TabClaw), an interactive AI agent for table analysis created by the team at the State Key Laboratory of Cognitive Intelligence, University of Science and Technology of China. TabClaw's design philosophy — planning before execution, multi-agent parallel analysis, skill learning, and persistent memory — directly shaped the architecture of this skill.

The self-improvement mechanism draws from the [**self-improving**](https://clawic.com/skills/self-improving) agent skill pattern by [OpenClaw](https://github.com/openclaw/openclaw), which pioneered tiered memory, correction tracking, and skill lifecycle management for AI agents.

### References

```bibtex
@misc{tabclaw2026,
  title        = {TabClaw: A Local AI Agent for Conversational Table Analysis},
  author       = {Yu, Shuo and Wang, Daoyu and Li, Qingchuan and Tao, Xiaoyu and Mao, Qingyang and Zhou, Yitong and Cheng, Mingyue and Liu, Qi and Chen, Enhong},
  year         = {2026},
  howpublished = {\url{https://github.com/fishsure/TabClaw}}
}
```

---

## License

MIT
