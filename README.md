<h1 align="center">FunnySkills</h1>

<p align="center">
  <strong>English</strong> · <a href="README_zh.md">中文</a>
</p>

<p align="center">
  A curated collection of AI agent skills — practical, self-improving, and ready to use.
</p>

---

## Skills

| Skill | Description | Status |
|-------|-------------|--------|
| [table-analysis](table-analysis/) | Self-improving table analysis agent. 16 built-in pandas operations, tiered memory, skill learning, multi-table parallel analysis. | Available |

## What Are Agent Skills?

Agent skills are modular instruction sets that extend AI coding agents (like Cursor, Codex, OpenClaw) with specialized capabilities. Each skill contains:

- **SKILL.md** — Core instructions the agent follows
- **scripts/** — Pre-built tools for reliable, repeatable operations
- **references/** — Detailed documentation loaded on demand
- **examples/** — Sample data for testing

## How to Use

### In Cursor

Copy any skill folder to your Cursor skills directory:

```bash
# Personal (all projects)
cp -r table-analysis ~/.cursor/skills/table-analysis

# Project-level
cp -r table-analysis .cursor/skills/table-analysis
```

### In Codex / OpenClaw

Copy to your skills directory:

```bash
cp -r table-analysis ~/.codex/skills/table-analysis
```

The agent will automatically detect and activate the skill when relevant tasks arise.

## Contributing

Want to add a new skill? Each skill should follow this structure:

```
skill-name/
├── SKILL.md              # Required — agent instructions
├── README.md             # Project documentation
├── scripts/              # Optional — utility scripts
├── references/           # Optional — detailed docs
└── examples/             # Optional — sample data
```

## License

MIT
