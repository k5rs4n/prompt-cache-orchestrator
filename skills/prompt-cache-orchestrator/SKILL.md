---
name: prompt-cache-orchestrator
description: 'Orchestrates sub-agent task execution using deterministic prompt prefix-caching optimization. Automatically compiles raw user prompts into cache-optimized subagent prompts (Static Prefix -> Stable Context -> Dynamic Suffix) to maximize LLM prompt cache hits and minimize token costs across Anthropic Claude, OpenAI, and Google Gemini.'
version: "1.0.0"
---

# Prompt Cache Orchestrator

This skill enables Antigravity to act as an intelligent **Prompt Compiler & Orchestrator**. Instead of solving every user task directly in the main conversation (which accumulates context and consumes high tokens) or passing raw, unoptimized prompts to sub-agents, this skill structures every sub-agent prompt to achieve **maximal Prompt Cache Hits (up to 80-90% token savings)**.

## Core Architecture: The 3-Tier Prefix Cache

Modern LLMs (Anthropic Claude 3.5 Sonnet/Haiku, OpenAI GPT-4o, Google Gemini 2.5/3.8) utilize **Prefix Caching**. The cache is evaluated strictly from left to right (from top to bottom). Any alteration in the prefix breaks the cache chain.

```
┌─────────────────────────────────────────────────────────────┐
│ TIER 1: CACHE-STATIC PREFIX (Byte-for-Byte Deterministic)   │ <-- CACHE HIT (90% savings)
│ - System Role, Core Constraints, Code Standards, Rules      │     Must be >= 1024 tokens
├─────────────────────────────────────────────────────────────┤
│ TIER 2: STABLE CONTEXT (Shared Across Sub-Tasks)            │ <-- CACHE HIT (when repeating)
│ - Target File Contents, Data Schemas, Architectural Context │     Shared by related workers
├─────────────────────────────────────────────────────────────┤
│ TIER 3: DYNAMIC SUFFIX (Ephemeral Task Instructions)        │ <-- FULL PRICE (Only this part)
│ - Specific user prompt, exact bug/feature, output format    │     Placed strictly at the end
└─────────────────────────────────────────────────────────────┘
```

## Orchestration Workflow

Whenever the user gives a task (whether raw, informal, or complex):

### Step 1: Analyze & Identify Context
1. Determine the relevant code files, functions, or documentation needed for the task.
2. Read the project's static rules or Obsidian template (if available at `obsidian-template/SubAgent_Cache_Template.md` or in the workspace).
3. Do NOT let the worker sub-agent browse the entire repository blindly. Provide targeted file boundaries.

### Step 2: Compile the Sub-Agent Prompt
Construct the sub-agent prompt adhering strictly to the 3-Tier layout:

#### 1. Tier 1: Static Prefix (`[CACHE-STATIC-PREFIX]`)
- Must never change between sub-agent invocations in the same project.
- Contains the sub-agent role, security rules, formatting rules, and standard conventions.
- Ensure the static block is sufficiently rich (>= 1024 tokens) to trigger provider caching thresholds.

#### 2. Tier 2: Stable Context (`[STABLE-CONTEXT]`)
- Embed the target files, type definitions, or schema snippets needed.
- If multiple sub-agents work on the same module, keep this section identical across all of them.

#### 3. Tier 3: Dynamic Task (`[DYNAMIC-TASK]`)
- The user's specific request translated into an actionable, scoped instruction.
- Explicit constraints (e.g. "Do not change function signatures", "Do not add new dependencies", "Only modify line X to Y").
- Place strictly at the very end of the prompt.

### Step 3: Dispatch Sub-Agent
Invoke the sub-agent via `invoke_subagent`:
- **TypeName**: `self` or a dedicated specialized worker.
- **Role**: Meaningful 2-5 word description (e.g. `Discount Logic Debugger`).
- **Prompt**: The compiled 3-tier cache-optimized prompt.

### Step 4: Reconcile & Report
1. Receive the sub-agent output.
2. Review the diff or code changes.
3. Present the result concisely to the user, highlighting the token/cache efficiency achieved.

---

## Standard Prompt Template

```markdown
# [CACHE-STATIC-PREFIX: DO NOT MODIFY]
You are a senior software engineering sub-agent.
Your objective is to execute the assigned task with high precision and minimal token overhead.

GENERAL OPERATING CONSTRAINTS:
1. Scope Discipline: Work strictly on the target files and functions provided in the context.
2. Dependency Integrity: Do not introduce external packages, dependencies, or rewrite project build setups.
3. Code Signature Stability: Maintain existing interfaces, exported symbols, and public function signatures unless explicitly requested.
4. Tool Efficiency: Do not perform repository-wide searches or unnecessary directory scans. Work directly with the provided files.
5. Deterministic Output: Provide concise diffs or updated code snippets with clear explanations.

CODING STANDARDS:
- Maintain full typing and strict lint compliance.
- Keep comments and docstrings intact.
- Follow existing project conventions, formatting, and naming patterns.
# [/CACHE-STATIC-PREFIX]

# [STABLE-CONTEXT]
Target Files and Project Reference:
Path: {{FILE_PATH}}
Content:
```{{LANG}}
{{FILE_CONTENT}}
```
# [/STABLE-CONTEXT]

# [DYNAMIC-TASK]
Task: {{TASK_DESCRIPTION}}
Specific Instructions: {{SPECIFIC_INSTRUCTIONS}}
Expected Output: {{OUTPUT_FORMAT}}
# [/DYNAMIC-TASK]
```

## Obsidian Integration
If an Obsidian vault or template file is configured:
1. Locate `SubAgent_Cache_Template.md` in the user's Obsidian vault or `.agents/` folder.
2. Extract the static prefix verbatim without altering whitespace or line breaks.
3. Inject the dynamic task and context into the respective placeholders.
