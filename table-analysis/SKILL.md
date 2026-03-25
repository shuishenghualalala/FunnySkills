---
name: table-analysis
description: Self-improving AI agent for table and data analysis. Analyzes CSV, Excel, TSV, JSON, Parquet files with natural language. Supports filter, sort, aggregate, merge, pivot, correlate, and custom pandas operations. Learns from every interaction — logs corrections, distills reusable skills, remembers preferences across sessions. Use when the user asks to analyze tabular data, explore datasets, compute statistics, compare tables, or perform any data manipulation. Also use when the user corrects your analytical approach or states a data analysis preference.
---

# Table Analysis

Self-improving table analysis agent. Learns from corrections, distills reusable patterns, remembers preferences — gets smarter the more you use it.

## Prerequisites

Python 3.9+ with: `pandas`, `openpyxl`, `numpy`, `tabulate`. Install if missing:

```bash
pip install pandas openpyxl numpy tabulate
```

First-time setup (creates tiered memory structure):

```bash
python SKILL_DIR/scripts/memory_mgr.py init
```

Scripts are at `SKILL_DIR/scripts/` (resolve `SKILL_DIR` from this file's location).

## Core Workflow

```
1. LOAD        →  Read HOT memory + check learned skills (MANDATORY)
2. CLARIFY     →  If ambiguous, ask the user
3. PROFILE     →  Run analyze.py on input files
4. PLAN        →  Present execution plan, wait for approval
5. EXECUTE     →  Run steps using scripts or inline Python
6. REFLECT     →  Self-evaluate the outcome (MANDATORY)
7. PRESENT     →  Structured conclusion with key findings
8. LEARN       →  Log corrections, update memory, distill skills (MANDATORY)
```

Steps 1, 6, and 8 are **non-negotiable** — they drive self-improvement.

### Step 1: Load Memory and Skills (MANDATORY)

Before ANY analysis, load context from previous sessions:

```bash
python SKILL_DIR/scripts/memory_mgr.py hot
python SKILL_DIR/scripts/skill_store.py match "<keywords from user request>"
```

If a **confirmed** learned skill matches, follow its stored pattern. If memory contains preferences (output format, preferred metrics, domain terms), apply them throughout.

When applying a learned preference, **always cite the source**:
- "Using markdown format (from HOT memory: preferences/output_format)"
- "Applying quarterly-breakdown pattern (learned skill, used 5x)"

### Step 2: Clarify Ambiguous Requests

Use AskQuestion when the request has multiple valid interpretations. See [references/prompts.md](references/prompts.md) for triggers.

Do NOT clarify when: request is specific, memory resolves the ambiguity, or only one interpretation is reasonable.

### Step 3: Profile the Data

```bash
python SKILL_DIR/scripts/analyze.py <file> -f markdown
```

### Step 4: Plan Before Executing

For tasks with 2+ steps, present a plan and wait for confirmation:

```
## Execution Plan: [Title]
1. **[Step]** — [What + which script]
2. ...
N. **Present results** — Summary with key numbers

Proceed?
```

Skip planning for single-step tasks.

### Step 5: Execute

**Pre-built scripts** (for standard operations):

| Operation | Command |
|-----------|---------|
| Profile | `analyze.py <file> -f markdown` |
| Metadata | `table_ops.py info <file>` |
| Filter | `table_ops.py filter <file> '<condition>' -f markdown` |
| Select | `table_ops.py select <file> "col1,col2" -f markdown` |
| Aggregate | `table_ops.py aggregate <file> --group-by col --agg col:func` |
| Sort | `table_ops.py sort <file> --by col --desc` |
| Merge | `table_ops.py merge left.csv right.csv --on col` |
| Pivot | `table_ops.py pivot <file> --index col --values col --pivot-columns col` |
| Add column | `table_ops.py add-column <file> --name new --expression "a * b"` |
| Statistics | `table_ops.py describe <file> -f markdown` |
| Find rows | `table_ops.py find <file> --column col --pattern "regex"` |
| Deduplicate | `table_ops.py dedup <file>` |
| Rename | `table_ops.py rename <file> --mapping old:new` |
| Sample | `table_ops.py sample <file> -n 20 -f markdown` |
| Value counts | `table_ops.py value-counts <file> --column col -f markdown` |
| Correlation | `table_ops.py correlation <file> -f markdown` |
| Head | `table_ops.py head <file> -n 10 -f markdown` |

All support `-o <output>` and `-f csv|markdown|json`. Full syntax in [references/operations.md](references/operations.md).

**Inline Python** for complex/multi-step operations, custom logic, visualization, or statistical modeling.

### Step 6: Self-Reflect (MANDATORY)

After executing, before presenting results, pause and evaluate:

```
TASK: [what was requested]
OUTCOME: [success|partial|needs_improvement]
REFLECTION: [what I noticed]
LESSON: [what to do differently — or "approach was solid"]
ACTION: [none|log_correction|distill_skill|update_memory]
```

Checklist:
1. Did the result actually answer the question?
2. Was the approach efficient?
3. Did I apply relevant memory/learned skills?
4. Would this approach generalize?

If the self-check reveals gaps, fix them BEFORE presenting.

### Step 7: Present Results

**For analysis:** End with `## Key Findings` (3-6 bullets with specific numbers).

**For table operations:** End with `## Result` (filename, shape, description).

### Step 8: Learn (MANDATORY)

After EVERY interaction, execute the applicable learning actions:

#### 8a. Log Corrections (when user corrects you)

Detect these signals and log IMMEDIATELY:

| User says | Action |
|-----------|--------|
| "No, that's not right" / "Actually, use X" | `memory_mgr.py correct <type> "<what>" "<fix>"` |
| "Always do X" / "Never do Y" | `memory_mgr.py set preferences <key> "<value>" --confirmed` |
| "For this kind of data, use..." | `memory_mgr.py set domain_knowledge <key> "<value>"` |
| "I told you before..." | Check corrections log, bump count, consider promotion |
| Same correction 3x | Promote: `memory_mgr.py promote "<key>"` |

Correction types: `metric`, `format`, `method`, `interpretation`, `domain`.

#### 8b. Update Memory (when you learn something new)

Save noteworthy preferences or domain knowledge:

```bash
python SKILL_DIR/scripts/memory_mgr.py set <category> <key> "<value>"
```

Categories: `preferences`, `analysis_patterns`, `domain_knowledge`, `user_context`.

Only save when: user states a preference, defines a domain term, corrects your approach, or a self-reflection reveals an improvement.

Never save: one-time instructions, hypotheticals, inferences from silence.

#### 8c. Distill Skills (when a reusable pattern emerges)

After tasks with 3+ steps that worked well (no major corrections):

```bash
python SKILL_DIR/scripts/skill_store.py add "<name>" "<description>" "<pattern>"
```

After using an existing learned skill:
```bash
python SKILL_DIR/scripts/skill_store.py use "<name>"
```

If the execution improved on the stored pattern:
```bash
python SKILL_DIR/scripts/skill_store.py reflect "<name>" "<improvement>"
```

Skills evolve: tentative (1x) -> emerging (2x) -> pending (3x, ask user) -> confirmed.

## Skill Lifecycle

```
 New pattern ──> tentative ──(2 uses)──> emerging ──(3 uses)──> pending
                                                                   │
                                         user confirms ────────────┘
                                              │
                                              v
  unused 90d ──> archived <──(30d)── confirmed ──(reflection)──> improved
```

When a skill reaches **pending**, ask the user: "I've used this pattern N times. Should I make it permanent?"

Confirmed skills survive decay. Unused tentative/emerging skills archive after 90 days.

Run periodic maintenance: `python SKILL_DIR/scripts/skill_store.py decay`

## Memory Architecture

```
~/.table-analysis/
├── memory.json          # HOT: ≤80 entries, always loaded
├── corrections.json     # Last 50 corrections with promotion tracking
├── domains/             # WARM: per-domain files, loaded on context match
│   ├── finance.json
│   └── marketing.json
└── archive/             # COLD: decayed patterns, loaded on explicit query
```

| Tier | Behavior | Limit |
|------|----------|-------|
| HOT | Always loaded at session start | ≤80 entries |
| WARM | Loaded when domain matches context | ≤200 entries per file |
| COLD | Loaded only on explicit user query | Unlimited |

Promotion: correction used 3x in 7 days -> HOT. Demotion: HOT unused 30d -> WARM, 90d -> COLD.

Compact when HOT overflows: `python SKILL_DIR/scripts/memory_mgr.py compact`

## Multi-Table Parallel Analysis

When comparing multiple tables, use Task tool to launch parallel subagents:

```
Analyze [path] to extract [metric] grouped by [dimension].
Scripts: python [SKILL_DIR]/scripts/analyze.py [path] -f markdown
         python [SKILL_DIR]/scripts/table_ops.py [command] [path] [args]
Return: markdown summary + key findings.
```

Synthesize: **Consensus** (tables agree) vs **Divergence** (tables differ).

## Common Traps

| Trap | Fix |
|------|-----|
| Learning from silence | Wait for explicit correction or 3x evidence |
| Promoting too fast | Keep tentative until 3 uses + user confirmation |
| Skipping memory load | ALWAYS load HOT at start, even for "simple" tasks |
| Not citing sources | ALWAYS say where a preference/pattern came from |
| Forgetting self-reflection | Do it BEFORE presenting results, every time |

## References

- [operations.md](references/operations.md) — Full command reference with examples
- [prompts.md](references/prompts.md) — Templates for planning, reflection, learning signals, distillation
