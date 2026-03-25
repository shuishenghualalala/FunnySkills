# Prompt Templates

Templates for planning, clarification, self-reflection, learning, and skill distillation.

## Planning Template

```
## Execution Plan: [Brief Title]

1. **Understand the data** — Run `analyze.py` on each input file
2. **[Specific step]** — [What to do + which script/command]
3. ...
N. **Present results** — Summarize findings with key numbers

Estimated complexity: [simple|moderate|complex]
```

Rules: 2-8 steps, each = one concrete action, include which script to use, logical order, end with summary.

## Clarification Template

Triggers:
- Multiple valid metrics (e.g., "analyze sales" — by region? time? product?)
- Unclear aggregation (sum vs mean vs count)
- Ambiguous column mapping
- "Compare" without specifying dimension

Format: Present options via AskQuestion tool. Do NOT clarify when request is specific, unambiguous, or memory resolves it.

## Self-Reflection Template

MANDATORY after completing any multi-step task. Evaluate before presenting final results:

```
TASK: [what was requested]
OUTCOME: [success|partial|needs_improvement]
REFLECTION: [what I noticed about my approach]
LESSON: [what to do differently — or "approach was solid"]
ACTION: [none|log_correction|distill_skill|update_memory]
```

Reflection checklist:
1. Did the result actually answer the user's question?
2. Was the approach efficient, or were there wasted steps?
3. Did I apply relevant memory/learned skills?
4. Would this approach generalize to similar data?
5. Did the user have to correct me? If so, what triggered the error?

## Learning Signals — What to Capture

### MUST log (immediately):

| Signal | Example | Action |
|--------|---------|--------|
| Explicit correction | "No, use net revenue not gross" | `memory_mgr.py correct metric ...` |
| "Always/Never" rule | "Always show percentages" | `memory_mgr.py set preferences ... --confirmed` |
| Repeated correction | Same fix 3 times | Promote to HOT memory |
| Domain definition | "Churn = inactive >90 days" | `memory_mgr.py set domain_knowledge ...` |
| Method preference | "Use median not mean for salaries" | `memory_mgr.py correct method ...` |

### SHOULD log (after reflection):

| Signal | Example | Action |
|--------|---------|--------|
| Effective approach | Multi-step analysis that worked well | `skill_store.py add ...` |
| Output format preference | User liked the markdown table format | `memory_mgr.py set preferences ...` |
| Data quirk | "This dataset's dates are in DD/MM format" | `memory_mgr.py set domain_knowledge ...` |
| Tool preference | User preferred inline Python over scripts | `memory_mgr.py set preferences ...` |

### NEVER log:

- Silence (not confirmation)
- One-time instructions ("just this once")
- Hypotheticals
- Inferred preferences (never guess)
- Raw data values

## Correction Types

Use these types when logging corrections:

| Type | When | Example |
|------|------|---------|
| `metric` | Wrong measurement or calculation | "Use net revenue, not gross" |
| `format` | Output style issue | "Show as percentage, not decimal" |
| `method` | Wrong analytical approach | "Use median for skewed distributions" |
| `interpretation` | Misread the user's intent | "I meant compare regions, not products" |
| `domain` | Business logic error | "Q4 is Oct-Dec, not Sep-Nov for us" |

## Skill Distillation Template

After completing a non-trivial task (3+ steps), evaluate for distillation:

**Criteria (ALL must be true):**
1. Task involved a reusable pattern (not a one-off query)
2. The steps could apply to different datasets
3. The approach worked well (no major corrections needed)

**If criteria met:**
```bash
python SKILL_DIR/scripts/skill_store.py add \
  "<verb>-<noun>-<qualifier>" \
  "<One sentence: what this pattern does>" \
  "<Step-by-step instructions that work with different data>"
```

**After using a learned skill**, always:
```bash
python SKILL_DIR/scripts/skill_store.py use "<name>"
```

**If the execution improved on the stored pattern:**
```bash
python SKILL_DIR/scripts/skill_store.py reflect "<name>" "<what improved>"
```

## Memory Transparency Template

When applying a learned preference or pattern, ALWAYS cite the source:

```
Using [preference/pattern] from [HOT memory / learned skill "name"]
```

Examples:
- "Using markdown table format (from HOT memory: preferences/output_format)"
- "Applying quarterly-breakdown pattern (from learned skill, used 5x)"
- "Using net revenue per your correction (from corrections log, 3x confirmed)"

## Multi-Table Comparison Template

When comparing multiple tables:

1. Launch parallel subagents — one per table
2. Each subagent prompt:
   ```
   Analyze [path] to extract [metric] grouped by [dimension].
   Scripts: python [SKILL_DIR]/scripts/analyze.py [path] -f markdown
   Return: markdown summary + key findings as bullets.
   ```
3. Synthesize results:
   - **Consensus**: Where tables agree
   - **Divergence**: Where tables differ
4. Present unified comparison

## Output Format Template

**For analysis/Q&A:**
```
## Key Findings
- [Finding 1 with specific numbers]
- [Finding 2 with specific numbers]
```

**For table operations:**
```
## Result
- Generated: **[filename]** ([N] rows x [M] cols)
- [Description]
```
