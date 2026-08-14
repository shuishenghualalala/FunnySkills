---
name: project-dissector
description: Analyze and document an unfamiliar software project or repository in a deep architecture-walkthrough style. Use when the user asks to 拆解项目, 解读源码, 分析仓库, 写架构导读, produce documentation like "how-claude-code-works", explain how a system works end to end, map code paths, identify core loops/modules, or turn source code into structured technical docs.
---

# Project Dissector

## Goal

Turn a real codebase into readable architecture documentation: not a file-by-file summary, but a guided explanation of what problem the system solves, how the core loop/data flow works, what abstractions matter, and why the design choices make sense.

Read `references/writing-style.md` before drafting substantial documentation or when the user asks for docs in the style of `how-claude-code-works`.

## Workflow

1. Establish the reader goal.
   - Identify the target project path, expected output language, and desired artifact shape.
   - Default to Chinese Markdown docs when the user writes in Chinese.
   - If unspecified, create a concise chapter plan first, then write the most important chapter(s).

2. Build a project map before explaining.
   - Inspect root files: README, package/build config, lockfiles, entrypoints, docs, examples, tests.
   - Use `rg --files`, `rg`, dependency manifests, and tree slices to identify frameworks, runtimes, commands, and major directories.
   - Locate the executable entrypoints, central orchestration code, public APIs, extension points, config loaders, persistence boundaries, and tests.

3. Find the core mechanism.
   - Trace one or two representative user workflows from entrypoint to side effects.
   - Prefer concrete code paths over naming-based guesses.
   - Record file anchors with line numbers for claims that depend on implementation details.
   - Separate verified facts from inference. Mark inference explicitly when code evidence is incomplete.

4. Design the documentation structure.
   - Start with a "10-minute overview" or "chapter 1 overview" when the project is large.
   - Group chapters by architectural responsibility, not by source directory.
   - Put foundational chapters first: positioning, main loop/data flow, context/state, tool/plugin/extension systems, security or persistence, UX/API surface, minimal rebuild guide.
   - Keep a sidebar or table of contents if producing multiple files.

5. Write in explanatory layers.
   - Begin each chapter with what the reader will learn and why it matters.
   - Use progressive depth: concept -> concrete code path -> design rationale -> tradeoffs/failure modes.
   - Include diagrams or ASCII flows for loops, pipelines, state transitions, and boundaries.
   - Use tables for role comparisons, lifecycle phases, module responsibilities, and configuration matrices.
   - Prefer design-mechanism explanation over source-index narration: make the reader understand the architecture before naming files.
   - Keep inline file/line anchors sparse. Put most implementation entrypoints in a compact "key files" or source map section instead of interrupting every paragraph.

6. Validate the writeup against the code.
   - Re-open referenced files after drafting high-impact claims.
   - Check that commands, file paths, function/class names, and line anchors still match.
   - Avoid inventing internals when the code is minified, generated, or unavailable; state the evidence limit and explain the observable behavior instead.

## Output Rules

- Prefer Markdown.
- Use a direct, architecture-review tone.
- Explain "why this design exists", not only "what the code does".
- Quote code sparingly; short snippets should support a specific argument.
- Use exact file/line anchors only for claims that truly need auditability. For high-level architecture chapters, prefer file-level references and a consolidated implementation-entry table.
- When the user wants a reusable documentation site, create `docs/`, `_sidebar.md`, and a quick-start overview mirroring the chapter plan.
- When the user only asks for an analysis, return the chapter plan plus the highest-value findings instead of creating many files.

## Quality Bar

A good project dissection should let a new engineer answer:

- What category of system is this, and what problem does it solve?
- What is the central loop, request path, or execution pipeline?
- Which abstractions are stable contracts, and which are implementation details?
- Where does state live, and how does it move?
- Where are side effects controlled: file system, network, shell, database, user approvals?
- What are the main extension points?
- What tradeoffs did the authors choose, and what alternatives were likely rejected?
- How would someone rebuild the minimal version of this project?
