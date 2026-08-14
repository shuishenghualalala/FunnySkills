<h1 align="center">FunnySkills</h1>

<p align="center">
  <a href="README.md">English</a> · <strong>中文</strong>
</p>

<p align="center">
  一个精心策划的 AI 智能体技能合集——实用、自我进化、开箱即用。
</p>

---

## 技能列表

| 技能 | 说明 | 状态 |
|------|------|------|
| [table-analysis](table-analysis/) | 自我进化的表格分析智能体。16 种内置 pandas 操作、三级记忆、技能学习、多表并行分析。 | 可用 |
| [project-dissector](project-dissector/) | 深度拆解陌生代码仓库并输出架构导读：核心循环、数据流、关键抽象、扩展点与设计取舍。 | 可用 |

## 什么是智能体技能？

智能体技能是模块化的指令集，用于扩展 AI 编程智能体（如 Cursor、Codex、OpenClaw）的专业能力。每个技能包含：

- **SKILL.md** — 智能体遵循的核心指令
- **scripts/** — 预构建的可靠工具脚本
- **references/** — 按需加载的详细文档
- **examples/** — 用于测试的示例数据

## 如何使用

### 在 Cursor 中

将技能文件夹复制到 Cursor 技能目录：

```bash
# 个人技能（所有项目可用）
cp -r table-analysis ~/.cursor/skills/table-analysis

# 项目级技能
cp -r table-analysis .cursor/skills/table-analysis
```

### 在 Codex / OpenClaw 中

复制到技能目录：

```bash
cp -r table-analysis ~/.codex/skills/table-analysis
```

智能体会在遇到相关任务时自动检测并激活技能。

## 贡献

想添加新技能？每个技能应遵循以下结构：

```
skill-name/
├── SKILL.md              # 必须 — 智能体指令
├── README.md             # 项目文档
├── scripts/              # 可选 — 工具脚本
├── references/           # 可选 — 详细文档
└── examples/             # 可选 — 示例数据
```

## 许可证

MIT
