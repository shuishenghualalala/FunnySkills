# Architecture Walkthrough Writing Style

Use this reference when producing project-dissection documentation inspired by `how-claude-code-works`.

## Core Style

- Write for engineers who want the system model, not trivia.
- Prefer "problem -> mechanism -> code evidence -> design rationale".
- Treat the project as a set of interacting systems rather than directories.
- Keep the prose explanatory and concrete. Avoid marketing language.
- Use Chinese chapter titles and section numbering when the surrounding request is Chinese.
- Optimize chapters for fast design understanding: start with the problem solved, architectural role, lifecycle, boundaries, and tradeoffs before implementation inventory.
- Avoid turning the body into a source-code breadcrumb trail. Use line anchors only where they materially support a disputed or subtle claim; otherwise collect source entrypoints in a final table or source map.

## Recommended Document Set

For a large project, use this shape:

```text
README.md or index.md
docs/
  quick-start.md
  01-overview.md
  02-main-loop-or-request-flow.md
  03-state-and-context.md
  04-capability-or-plugin-system.md
  05-core-workflow.md
  06-extension-points.md
  07-security-and-permissions.md
  08-user-experience-or-api.md
  09-minimal-rebuild.md
  reference.md
_sidebar.md
```

Adapt chapter names to the project. Do not force irrelevant chapters.

## Chapter Template

```markdown
# 第 N 章：主题名称

> 本章导读：用 2-4 句话说明本章解决什么问题、读者会理解哪些关键机制、建议先看哪些章节。

## N.1 这个模块解决什么问题

先给定位。说明它在整个系统中的角色，以及没有它会出现什么工程问题。

## N.2 全景流程

用 Mermaid、ASCII 流程或编号阶段展示主路径。

## N.3 核心接口/数据结构

列出真正承载设计的类型、函数、配置或协议。重点解释这些抽象为什么存在、如何协作；只在必要处用短代码片段或少量文件锚点支撑。

## N.4 生命周期或执行路径

按真实运行顺序解释。每一步都说明输入、处理、输出、失败处理。

## N.5 设计取舍

解释为什么这样设计。对比至少一个朴素方案或替代方案。

## N.6 小结

总结读者现在应该掌握的系统模型，并指向下一章。
```

For focused technical chapters, this lighter shape is often better:

```markdown
# 第 N 章：主题名称

开头直接说明该机制解决的问题，以及它在系统里的位置。

## N.1 设计目标
说明为什么需要这个机制，列出 3-5 个工程目标。

## N.2 核心抽象
解释主要组件、工具、状态机、profile、协议或调度器如何分工。

## N.3 生命周期 / 执行路径
用 Mermaid、ASCII 或阶段列表讲清从输入到输出的过程。

## N.4 边界与取舍
讲权限、状态、持久化、并发、失败恢复、UI 边界等设计选择。

## N.5 关键实现入口
用表格集中列文件级入口；避免在正文每段都塞 `file.ts:123`。

## N.6 小结
用几句话重建读者应带走的系统模型。
```

## Signature Patterns

Use these patterns when evidence supports them:

- "三级范式" or staged maturity model: compare simple approaches with the system's current architecture.
- "三层架构": design layer, assembly layer, execution layer.
- "生命周期": list 6-10 concrete phases from input to output.
- "纵深防御": show multiple independent safety layers.
- "渐进式处理": light-to-heavy pipeline for compression, validation, recovery, or loading.
- "单一事实来源": identify central registries, config loaders, routers, or schemas.
- "扩展点": explain how new capabilities are added without changing the core loop.
- "最小必要组件": end with what someone would implement to rebuild a simplified version.

## Evidence Rules

- Anchor implementation claims to files, functions, classes, schemas, or config keys.
- Use line numbers when available, stable, and useful for verification; do not overuse them in explanatory prose.
- For architecture walkthroughs, prefer a concise "关键实现入口" table with file-level paths, and reserve exact line anchors for subtle behavior, surprising constraints, or high-risk claims.
- Prefer reading tests to infer intended behavior when implementation is dense.
- If generated/minified code blocks clarity, say so and focus on observable interfaces.
- Never present speculation as fact. Use "从代码结构推断" or "看起来" only when evidence is indirect.

## Writing Moves

- Start sections with a direct thesis sentence.
- Follow with a concrete code path or data flow.
- Then explain why the design matters.
- Use tables for comparisons and inventories.
- Use diagrams for loops, pipelines, and state transitions.
- Keep code snippets short; the surrounding explanation should carry the insight.
- If a section begins to read like "file A line X calls file B line Y", rewrite it around lifecycle phases, responsibilities, and design consequences.

## Anti-patterns

- Do not summarize every file in directory order.
- Do not copy long source blocks.
- Do not over-index on naming without tracing execution.
- Do not make naming clarification the opening section unless the naming confusion is the user's primary problem. Fold naming into the first relevant mechanism section or a small table when needed.
- Do not scatter dense `file.ts:line` references through conceptual chapters; this slows readers who need the design model first.
- Do not write generic "best practices" unrelated to this codebase.
- Do not hide uncertainty.
- Do not create a huge doc set before the architecture map is clear.
