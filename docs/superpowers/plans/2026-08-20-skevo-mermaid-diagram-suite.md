# Skevo Mermaid Diagram Suite Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the empty legacy Mermaid sources with nine code-backed Chinese-first diagrams, render matching SVG/PNG assets, and update the diagram documentation and root README reference.

**Architecture:** The suite uses one architecture diagram, one sequence diagram, and seven focused flowcharts. Each source is self-contained with Mermaid frontmatter, maintenance metadata, high-contrast styles, and a narrow responsibility defined by the approved design spec.

**Tech Stack:** Mermaid CLI 11.16.0 (`mmdc`), Mermaid flowcharts and sequence diagrams, Markdown, SVG, PNG, Git.

**Design spec:** `docs/superpowers/specs/2026-08-20-skevo-mermaid-diagram-suite-design.md`

---

## File map

**Delete obsolete empty sources:**

- `docs/diagrams/mmd/01-overall-architecture.mmd`
- `docs/diagrams/mmd/03-permission-and-plan-mode.mmd`
- `docs/diagrams/mmd/04-context-folding.mmd`
- `docs/diagrams/mmd/05-memory-and-skills.mmd`
- `docs/diagrams/mmd/06-skill-evolution.mmd`
- `docs/diagrams/mmd/07-skill-evaluation.mmd`
- `docs/diagrams/mmd/08-mcp-and-subagents.mmd`

**Create or replace sources:**

- `docs/diagrams/mmd/01-system-architecture.mmd`
- `docs/diagrams/mmd/02-agent-loop.mmd`
- `docs/diagrams/mmd/03-tool-loading-and-dispatch.mmd`
- `docs/diagrams/mmd/04-permissions-and-plan-mode.mmd`
- `docs/diagrams/mmd/05-context-and-sessions.mmd`
- `docs/diagrams/mmd/06-skill-runtime.mmd`
- `docs/diagrams/mmd/07-skill-evolution.mmd`
- `docs/diagrams/mmd/08-skill-evaluation.mmd`
- `docs/diagrams/mmd/09-mcp-and-subagents.mmd`

**Regenerate outputs:**

- `docs/diagrams/svg/*.svg`
- `docs/diagrams/png/*.png`

**Modify documentation:**

- `docs/diagrams/README.md`
- `README.md` — change only the architecture image path and preserve all unrelated user edits.

## Shared implementation rules

- Keep Mermaid frontmatter as the first bytes of every MMD file.
- Use Chinese labels first; preserve exact module, function, protocol, and state identifiers in English.
- Every `classDef` must set `fill`, `stroke`, `stroke-width`, and `color`.
- Use `-->` for direct calls/control, `-.->` for async or non-blocking work, and labeled solid edges for persistence.
- Render with white background. Do not pass `-t neutral`; the source frontmatter owns the theme.
- Validate each source immediately after creating it. Do not update Markdown references until all nine sources render.
- Preserve the existing uncommitted root `README.md` change except for replacing `01-overall-architecture.svg` with `01-system-architecture.svg`.

### Task 1: Create the system architecture diagram

**Files:**

- Delete: the seven obsolete empty MMD files listed in the file map
- Create: `docs/diagrams/mmd/01-system-architecture.mmd`

- [ ] **Step 1: Remove only the obsolete empty sources**

For each of the seven exact paths listed above that exists in the execution workspace, use `apply_patch` with `*** Delete File`. A dedicated worktree may not contain these currently untracked empty files; absence is already the desired state. Do not delete `02-agent-loop.mmd`, because it remains part of the new suite.

- [ ] **Step 2: Create the architecture source**

Write `docs/diagrams/mmd/01-system-architecture.mmd` with this complete content:

```mermaid
---
title: Skevo 系统架构
config:
  theme: base
  look: classic
  flowchart:
    curve: basis
---
%% Purpose: 展示 Skevo 的静态系统边界、内部责任和外部依赖。
%% Audience: both
%% Sources: agents/main.py, agents/agent.py, agents/prompt.py, agents/tools.py, agents/memory.py, agents/skills.py, agents/session.py, agents/mcp_client.py, agents/subagent.py
%% Anchors: main, Agent.chat, build_system_prompt, check_permission
%% Out of scope: Agent Loop 时序、权限决策树、Skill 评测细节。

flowchart TB
    USER(["👤 用户"])
    CLI["⌨ CLI / REPL / one-shot<br/>agents/main.py"]

    subgraph SKEVO["Skevo Harness Runtime"]
        direction TB
        AGENT["⚙ Agent Runtime<br/>Agent.chat"]
        MODEL_ADAPTER["◇ Prompt 与模型适配<br/>prompt.py / OpenAI / Anthropic"]
        TOOL_CONTROL["🔐 工具调度与权限<br/>tools.py"]
        CONTEXT["◆ 上下文、Memory 与 Session"]
        SKILLS["★ Skills 与在线演化"]
        EXTENSIONS["🔌 MCP 与子 Agent"]
    end

    OPENAI["☁ OpenAI-compatible"]
    ANTHROPIC["☁ Anthropic-compatible"]
    LOCAL["■ 本地文件系统与 Shell"]
    MCP_SERVER["🔌 外部 MCP Server"]
    USER_STATE[("💾 ~/.skevo")]
    PROJECT_STATE[("💾 项目 .skevo")]
    SESSION_STATE[("💾 Session 数据")]

    USER --> CLI --> AGENT
    AGENT --> MODEL_ADAPTER
    MODEL_ADAPTER -->|推理请求 / 流式响应| OPENAI
    MODEL_ADAPTER -->|推理请求 / 流式响应| ANTHROPIC
    AGENT --> TOOL_CONTROL
    AGENT --> CONTEXT
    AGENT --> SKILLS
    AGENT --> EXTENSIONS
    TOOL_CONTROL -->|获准的环境操作| LOCAL
    EXTENSIONS -->|stdio JSON-RPC| MCP_SERVER
    CONTEXT -->|读写| SESSION_STATE
    CONTEXT -->|读取长期记忆| USER_STATE
    SKILLS -->|发现 / 演化| USER_STATE
    SKILLS -->|发现 / 演化| PROJECT_STATE

    classDef actor fill:#FFF2B2,stroke:#9A6700,stroke-width:2px,color:#3B2A00
    classDef runtime fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef model fill:#DDF4FF,stroke:#0B6B8A,stroke-width:2px,color:#073B4C
    classDef state fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef external fill:#ECEFF3,stroke:#53606F,stroke-width:2px,color:#202833

    class USER,CLI actor
    class AGENT runtime
    class MODEL_ADAPTER model
    class TOOL_CONTROL control
    class CONTEXT,USER_STATE,PROJECT_STATE,SESSION_STATE state
    class SKILLS,EXTENSIONS extension
    class OPENAI,ANTHROPIC,LOCAL,MCP_SERVER external
```

- [ ] **Step 3: Render the source to a temporary SVG**

Run:

```bash
mmdc -i docs/diagrams/mmd/01-system-architecture.mmd -o /tmp/01-system-architecture.svg -b white
```

Expected: exit code 0 and `/tmp/01-system-architecture.svg` is non-empty.

- [ ] **Step 4: Inspect the SVG**

Open `/tmp/01-system-architecture.svg` with the available image viewer. Confirm that the four layers are legible, no label is clipped, and the central runtime boundary is visually dominant.

- [ ] **Step 5: Commit the architecture source**

```bash
git add docs/diagrams/mmd/01-system-architecture.mmd
git commit -m "docs: add Skevo system architecture diagram"
```

### Task 2: Create the Agent Loop sequence diagram

**Files:**

- Replace: `docs/diagrams/mmd/02-agent-loop.mmd`

- [ ] **Step 1: Write the complete sequence source**

```mermaid
---
title: Agent Loop：一次请求的完整生命周期
config:
  theme: base
  look: classic
---
%% Purpose: 按真实顺序展示一次用户请求从 CLI 到模型、工具、Session 和后台任务的生命周期。
%% Audience: both
%% Sources: agents/main.py, agents/agent.py
%% Anchors: run_repl, run_one_shot, Agent.chat, Agent._chat_openai, Agent._chat_anthropic, Agent._check_budget
%% Out of scope: 权限决策细节、具体工具实现、Skill 演化内部判断。

sequenceDiagram
    autonumber
    actor User as 👤 用户
    participant CLI as ⌨ CLI / REPL
    participant Runtime as ⚙ Agent Runtime
    participant Skills as ★ Skills
    participant Memory as ◆ Memory
    participant Model as ◇ 模型后端
    participant Tools as 🔐 工具运行时
    participant State as 💾 Session / 后台任务

    User->>CLI: 输入任务
    CLI->>Runtime: Agent.chat(user_message)
    opt 主 Agent 首次 chat
        Runtime->>Runtime: 懒加载 MCP 工具定义
        Note right of Runtime: MCP 失败只记录错误，不阻断对话
    end
    Runtime->>Runtime: 消费上一轮 pending extraction window
    Runtime->>Skills: BM25 检索相关 Skill 摘要
    Skills-->>Runtime: top 3 metadata / 无命中

    alt OpenAI-compatible
        Runtime->>Memory: 启动异步预取
    else Anthropic-compatible
        Runtime->>Memory: 启动异步预取
    end

    loop 文本或 tool call 驱动的 Agent Loop
        Runtime->>Runtime: compression pipeline
        opt Memory 已返回且尚未消费
            Memory-->>Runtime: 非阻断注入相关长期记忆
        end
        Runtime->>Model: 流式模型调用（可重试错误指数退避）
        Model-->>Runtime: text + tool calls
        alt 无 tool call
            Runtime-->>CLI: 最终文本
        else 达到 max_turns / max_cost_usd
            Runtime->>Runtime: 跳过工具并记录预算原因
        else 有 tool call 且预算允许
            Runtime->>Tools: 权限检查与执行
            Tools-->>Runtime: tool result / denied / error
            Runtime->>Model: 回写 tool result 并继续推理
            Runtime->>Runtime: 工具批次后检查自动 compaction
        end
        opt abort 或 context break
            Runtime->>Runtime: 终止相应循环
        end
    end

    Runtime->>State: 自动保存 Session
    Runtime--)State: Skill usage tracking
    Runtime--)State: 已成熟窗口的 online evolution
    Runtime->>State: 保存当前轮为下一 pending window
    CLI-->>User: 输出完成
```

- [ ] **Step 2: Validate and render**

Run:

```bash
mmdc -i docs/diagrams/mmd/02-agent-loop.mmd -o /tmp/02-agent-loop.svg -b white
```

Expected: exit code 0; sequence participants and `loop`/`alt` blocks render without overlap.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/02-agent-loop.mmd
git commit -m "docs: document the Agent Loop sequence"
```

### Task 3: Create the tool loading and dispatch diagram

**Files:**

- Create: `docs/diagrams/mmd/03-tool-loading-and-dispatch.mmd`

- [ ] **Step 1: Write the complete flowchart**

```mermaid
---
title: 工具加载、按需激活与执行路由
config:
  theme: base
  look: classic
  flowchart:
    curve: basis
---
%% Purpose: 展示工具来源、deferred tool 激活和获准调用的执行路由。
%% Audience: maintainer
%% Sources: agents/tools.py, agents/prompt.py, agents/agent.py
%% Anchors: tool_definitions, get_active_tool_definitions, get_deferred_tool_names, execute_tool, Agent._execute_tool_call
%% Out of scope: 权限决策树、MCP 握手、子 Agent 类型。

flowchart LR
    accTitle: 工具加载、按需激活与执行路由
    accDescr: 三个阶段从左到右展示工具来源、当前 Agent 工具集合的模型可见性与 deferred 按需激活，以及获准调用的执行路由；未知内置工具返回错误文本，而 OpenAI 路径未捕获的执行异常可能终止循环
    subgraph SOURCES["阶段 1 · 工具来源"]
        direction TB
        EAGER["⚙ default eager tools"]
        DEFERRED["◌ default deferred tools"]
        CUSTOM["◎ custom_tools<br/>Skill / 子 Agent fork 注入"]
        MCPDEF["🔌 MCP definitions<br/>主 Agent 首次 chat 成功发现"]
    end

    subgraph VISIBILITY["阶段 2 · 模型可见性与按需激活"]
        direction TB
        PROMPT["build_system_prompt<br/>列出未激活的默认 deferred 名称"]
        SEARCH["tool_search<br/>eager tool"]
        ACTIVE["active tool definitions<br/>当前 self.tools 中非 deferred<br/>或已激活的成员"]
        MODEL["◇ 模型请求"]
    end

    subgraph EXECUTION["阶段 3 · 获准调用的执行路由"]
        direction TB
        CALL["模型产生 tool call"]
        PERMISSION["🔐 check_permission<br/>详见图 04"]
        DISPATCH{"⚙ _execute_tool_call 路由"}
        SPECIAL["compact / plan 特殊工具"]
        SKILL["★ skill"]
        AGENT["◎ agent"]
        MCP["🔌 mcp__server__tool"]
        BUILTIN["内置 execute_tool"]
        UNKNOWN["❌ unknown tool<br/>execute_tool 返回错误文本"]
        RESULT["tool result<br/>按路径截断或大结果落盘"]
        RISK["⚠ OpenAI 路径风险<br/>未捕获执行异常可终止 loop"]
    end

    EAGER -->|无 custom_tools：初始 self.tools| ACTIVE
    EAGER -->|包含| SEARCH -->|当前 self.tools 包含时暴露| ACTIVE
    CUSTOM -->|非空时替换 default<br/>成为初始 self.tools| ACTIVE
    MCPDEF -->|成功后追加到当前 self.tools| ACTIVE
    DEFERRED -->|未使用 custom_system_prompt| PROMPT --> MODEL
    ACTIVE -->|完整 schemas| MODEL
    MODEL --> CALL --> PERMISSION
    PERMISSION -->|allow| DISPATCH
    DISPATCH --> SPECIAL --> RESULT
    DISPATCH --> SKILL --> RESULT
    DISPATCH --> AGENT --> RESULT
    DISPATCH --> MCP --> RESULT
    DISPATCH --> BUILTIN
    BUILTIN -->|普通结果或完整 schema| RESULT
    BUILTIN -->|tool_search 命中：记录 activated name| ACTIVE
    BUILTIN -->|未找到 handler| UNKNOWN --> RESULT
    DISPATCH -->|OpenAI sequential / gather<br/>未捕获执行异常| RISK
    RESULT -->|回写；下一次请求| MODEL

    classDef runtime fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef model fill:#DDF4FF,stroke:#0B6B8A,stroke-width:2px,color:#073B4C
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B

    class EAGER,DEFERRED,ACTIVE,CALL,DISPATCH,BUILTIN,RESULT runtime
    class PROMPT,MODEL model
    class SEARCH,PERMISSION,SPECIAL control
    class MCPDEF,CUSTOM,SKILL,AGENT,MCP extension
    class UNKNOWN,RISK error

    style SOURCES fill:#F8FAFC,stroke:#53606F,stroke-width:2px,color:#202833
    style VISIBILITY fill:#F5FAFF,stroke:#0B6B8A,stroke-width:2px,color:#073B4C
    style EXECUTION fill:#FFF9F0,stroke:#A85D00,stroke-width:2px,color:#4A2900
```

Runtime semantics: unknown tool 仅由 built-in `execute_tool` 转成错误文本并作为结果回写；Anthropic 路径捕获执行异常并归一为 tool result；OpenAI sequential/concurrent 路径当前未捕获的执行异常可能终止 Agent Loop，因此 `RISK` 不连接到 `RESULT`。

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/03-tool-loading-and-dispatch.mmd -o /tmp/03-tool-loading-and-dispatch.svg -b white
```

Expected: exit code 0; the three phases read left-to-right and the return edge does not obscure the source subgraph.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/03-tool-loading-and-dispatch.mmd
git commit -m "docs: add tool loading and dispatch diagram"
```

### Task 4: Create the permissions and Plan Mode diagram

**Files:**

- Create: `docs/diagrams/mmd/04-permissions-and-plan-mode.mmd`

- [ ] **Step 1: Write the complete flowchart**

> 实现核对（以此说明和下面的审阅版源码为准）：`--plan` 和显式进入只生成唯一 plan 路径，文件要到工具写入时才创建；只有 `/plan` 或 `enter_plan_mode` 显式进入会保存 `_pre_plan_mode`，CLI `--plan` 初始化不会保存。再次 `/plan` 和无审批回调的 `exit_plan_mode` 都执行 `permission_mode = _pre_plan_mode or "default"`，因此 CLI `--plan` 退出落到 `default`。REPL 的异步审批回调当前未被 `await`，四个审批选择分支实际不可达。图中还必须标出 plan 正文未读取、审批分支未更新 `permission_mode`、Plan Mode enforcement 范围偏宽，以及 `/plan` 进入时未同步 OpenAI system message。主权限流必须保持 `check_permission` 的真实短路顺序。

```mermaid
---
title: 权限决策与 Plan Mode 状态转换
config:
  theme: base
  look: classic
  layout: elk
  flowchart:
    curve: basis
---
%% Purpose: 严格展示 check_permission 的短路判断顺序，以及 Plan Mode 的实际状态转换与已知风险。
%% Audience: maintainer
%% Sources: agents/main.py, agents/tools.py, agents/agent.py
%% Anchors: _resolve_permission_mode, check_permission, Agent.toggle_plan_mode, Agent._execute_plan_mode_tool, run_repl.plan_approval_fn
%% Out of scope: 工具 schema 加载、工具内部实现、权限规则文件格式细节。

flowchart TB
    accTitle: 权限决策与 Plan Mode 状态转换
    accDescr: 先按三个阶段自上而下展示 check_permission 的真实短路顺序，再展示 Plan Mode 的进入和退出状态；显式进入会保存原模式，命令行 plan 初始化不会保存，因此退出时的相同赋值可能得到不同结果

    subgraph STAGE1["A1 · 优先短路"]
        direction TB
        CALL(["收到 tool call"])
        BYPASS{"mode = bypassPermissions?"}
        RULE_DENY{"命中 deny rule?"}
        RULE_ALLOW{"命中 allow rule?"}
        READ{"属于 READ_TOOLS?"}
        PLAN{"mode = plan?"}
        ALLOW_BYPASS(["返回 allow<br/>bypass 优先"])
        DENY_RULE(["返回 deny<br/>规则拒绝"])
        ALLOW_RULE(["返回 allow<br/>规则允许"])
        ALLOW_READ(["返回 allow<br/>READ_TOOLS"])

        CALL --> BYPASS
        BYPASS -->|否| RULE_DENY
        BYPASS -->|是| ALLOW_BYPASS
        RULE_DENY -->|否| RULE_ALLOW
        RULE_DENY -->|是| DENY_RULE
        RULE_ALLOW -->|否| READ
        RULE_ALLOW -->|是| ALLOW_RULE
        READ -->|否| PLAN
        READ -->|是| ALLOW_READ
    end

    subgraph STAGE2["A2 · Plan Mode 限制"]
        direction TB
        PLAN_EDIT{"属于 EDIT_TOOLS?"}
        PLAN_PATH{"file_path / path<br/>等于唯一 plan 路径?"}
        PLAN_SHELL{"工具是 run_shell?"}
        PLAN_PASS["未被 Plan Mode 限制拦截"]
        ALLOW_PLAN_FILE(["返回 allow<br/>唯一 plan 路径"])
        DENY_PLAN_EDIT(["返回 deny<br/>plan 禁止该编辑"])
        DENY_PLAN_SHELL(["返回 deny<br/>plan 禁止 Shell"])

        PLAN -->|否：跳过本阶段| PLAN_PASS
        PLAN -->|是| PLAN_EDIT
        PLAN_EDIT -->|否| PLAN_SHELL
        PLAN_EDIT -->|是| PLAN_PATH
        PLAN_SHELL -->|否| PLAN_PASS
        PLAN_SHELL -->|是| DENY_PLAN_SHELL
        PLAN_PATH -->|是| ALLOW_PLAN_FILE
        PLAN_PATH -->|否| DENY_PLAN_EDIT
    end

    subgraph STAGE3["A3 · 确认与默认策略"]
        direction TB
        PLAN_TOOL{"enter_plan_mode<br/>或 exit_plan_mode?"}
        ACCEPT{"mode = acceptEdits<br/>且属于 EDIT_TOOLS?"}
        NEED_CONFIRM{"危险 Shell / 新文件 write_file /<br/>不存在文件 edit_file /<br/>skill_create / skill_evolve?"}
        DONTASK{"mode = dontAsk?"}
        ALLOW_PLAN_TOOL(["返回 allow<br/>计划模式工具"])
        ALLOW_EDIT(["返回 allow<br/>acceptEdits"])
        ALLOW_DEFAULT(["返回 allow<br/>默认放行"])
        DENY_DONTASK(["返回 deny<br/>dontAsk 自动拒绝"])
        ASK["返回 confirm + 摘要"]
        RUNTIME_CONFIRM["调用端处理 confirm<br/>已确认摘要可复用；否则询问用户"]
        EXECUTE(["调用端获准执行"])
        REJECT(["调用端拒绝并回写 tool result"])

        PLAN_PASS --> PLAN_TOOL
        PLAN_TOOL -->|否| ACCEPT
        PLAN_TOOL -->|是| ALLOW_PLAN_TOOL
        ACCEPT -->|否| NEED_CONFIRM
        ACCEPT -->|是| ALLOW_EDIT
        NEED_CONFIRM -->|是| DONTASK
        NEED_CONFIRM -->|否| ALLOW_DEFAULT
        DONTASK -->|否| ASK
        DONTASK -->|是：自动拒绝| DENY_DONTASK
        ASK --> RUNTIME_CONFIRM
        RUNTIME_CONFIRM -->|已缓存或用户同意| EXECUTE
        RUNTIME_CONFIRM -->|用户拒绝| REJECT
    end

    subgraph PLAN_STATE["B1 · Plan Mode 状态转换"]
        direction TB
        MODE_RESOLVE["CLI 初始模式优先级<br/>--yolo → --plan → --accept-edits<br/>→ --dont-ask → default"]
        NON_PLAN["初始为非 plan mode"]
        CLI_PLAN["CLI --plan 初始化<br/>生成唯一 plan 路径并注入 prompt<br/>_pre_plan_mode 仍为 None"]
        EXPLICIT_ENTER["显式进入：/plan 或 enter_plan_mode<br/>_pre_plan_mode = 当前 mode<br/>切换 plan、生成路径并注入 prompt"]
        ACTIVE["Plan Mode active<br/>prompt 声明只读意图<br/>check_permission 部分强制"]
        TOGGLE_EXIT["再次 /plan<br/>permission_mode =<br/>_pre_plan_mode or default"]
        HAS_CALLBACK{"exit_plan_mode<br/>存在审批回调?"}
        FALLBACK_EXIT["无回调 fallback<br/>permission_mode =<br/>_pre_plan_mode or default"]
        EXITED(["退出完成<br/>清除路径与 Plan prompt"])
        ASYNC_BUG["当前失败点<br/>异步审批回调未 await<br/>随后对 coroutine 调用 .get"]
        EXPECTED["设计中的审批选择（当前不可达）<br/>继续规划 / 执行 / 清上下文后执行 / 手工执行"]
        CLI_DEFAULT["CLI --plan 未保存 _pre_plan_mode<br/>因此上述赋值退出时落到 default"]

        MODE_RESOLVE -->|结果非 plan| NON_PLAN
        MODE_RESOLVE -->|结果为 plan| CLI_PLAN --> ACTIVE
        NON_PLAN -->|显式进入| EXPLICIT_ENTER --> ACTIVE
        ACTIVE -->|REPL toggle| TOGGLE_EXIT --> EXITED
        ACTIVE -->|模型工具退出| HAS_CALLBACK
        HAS_CALLBACK -->|否| FALLBACK_EXIT --> EXITED
        HAS_CALLBACK -->|是| ASYNC_BUG
        ASYNC_BUG -.->|若修复 await 后才会进入| EXPECTED
        CLI_PLAN -.->|退出结果说明| CLI_DEFAULT
    end

    subgraph RISKS["B2 · 当前实现风险"]
        direction TB
        RISK_NOTE["1. READ_TOOLS 含 compact_context；plan 仅显式拒绝 EDIT_TOOLS 与 run_shell，其他工具可能默认允许<br/>2. exit_plan_mode 把文件路径当作 plan_content，未读取正文<br/>3. 审批分支未把 target_mode 赋给 permission_mode<br/>4. /plan 进入时未同步 OpenAI 已有 system message"]
    end

    RUNTIME_CONFIRM -.->|继续阅读 B（非控制流）| MODE_RESOLVE
    EXITED -.->|退出路径风险汇总| RISK_NOTE
    EXPECTED -.->|审批路径风险汇总| RISK_NOTE

    classDef actor fill:#FFF2B2,stroke:#9A6700,stroke-width:2px,color:#3B2A00
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef state fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef success fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B
    classDef note fill:#FFF4CC,stroke:#A15C00,stroke-width:2px,color:#3A2600
    classDef external fill:#ECEFF3,stroke:#53606F,stroke-width:2px,color:#202833

    class CALL actor
    class BYPASS,RULE_DENY,RULE_ALLOW,READ,PLAN,PLAN_EDIT,PLAN_PATH,PLAN_SHELL,PLAN_TOOL,ACCEPT,NEED_CONFIRM,DONTASK,ASK,RUNTIME_CONFIRM,HAS_CALLBACK control
    class PLAN_PASS,MODE_RESOLVE,NON_PLAN,CLI_PLAN,EXPLICIT_ENTER,ACTIVE,TOGGLE_EXIT,FALLBACK_EXIT,EXITED state
    class ALLOW_BYPASS,ALLOW_RULE,ALLOW_READ,ALLOW_PLAN_FILE,ALLOW_PLAN_TOOL,ALLOW_EDIT,ALLOW_DEFAULT,EXECUTE success
    class DENY_RULE,DENY_PLAN_EDIT,DENY_PLAN_SHELL,DENY_DONTASK,REJECT,ASYNC_BUG error
    class CLI_DEFAULT,RISK_NOTE note
    class EXPECTED external

    style STAGE1 fill:#FFF9F0,stroke:#A85D00,stroke-width:2px,color:#4A2900
    style STAGE2 fill:#FFF9F0,stroke:#A85D00,stroke-width:2px,color:#4A2900
    style STAGE3 fill:#FFF9F0,stroke:#A85D00,stroke-width:2px,color:#4A2900
    style PLAN_STATE fill:#F5FAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    style RISKS fill:#FFFBEB,stroke:#A15C00,stroke-width:2px,color:#3A2600
```

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/04-permissions-and-plan-mode.mmd -o /tmp/04-permissions-and-plan-mode.svg -b white
mmdc -i docs/diagrams/mmd/04-permissions-and-plan-mode.mmd -o /tmp/04-permissions-and-plan-mode.png -b white -s 2
mmdc -i docs/diagrams/mmd/04-permissions-and-plan-mode.mmd -o /tmp/04-permissions-and-plan-mode-800.png -b white -s 1
```

Expected: exit code 0；每个决策分支都有标签；按 A1 → A2 → A3 → B1 → B2 纵向阅读；800px 宽预览仍可识别主路径和阶段；当前失败点和风险注记不被画成成功路径；无裁切、重叠或边穿节点。

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/04-permissions-and-plan-mode.mmd
git commit -m "docs: document permissions and Plan Mode"
```

### Task 5: Create the context and sessions diagram

**Files:**

- Create: `docs/diagrams/mmd/05-context-and-sessions.mmd`

- [ ] **Step 1: Write the complete flowchart**

```mermaid
---
title: 上下文、长期记忆与会话生命周期
config:
  theme: base
  look: classic
  layout: elk
  elk:
    mergeEdges: true
    nodePlacementStrategy: SIMPLE
  flowchart:
    curve: basis
---
%% Purpose: 展示模型上下文的组装、运行中缩减、structured folding，以及 Session 的持久化与恢复。
%% Audience: maintainer
%% Sources: agents/prompt.py, agents/memory.py, agents/agent.py, agents/session_memory.py, agents/session.py, agents/main.py
%% Anchors: build_system_prompt, start_memory_prefetch, Agent.chat, Agent._run_compression_pipeline, Agent.compact, Agent._execute_compact_context_tool, Agent._check_and_compact, Agent._compact_conversation, Agent._auto_save, get_latest_session_id, load_session, Agent.restore_session
%% Out of scope: Skill 执行、权限决策、模型协议请求字段和长期 Memory 写入策略。

flowchart TB
    accTitle: 上下文、长期记忆与会话生命周期
    accDescr: 分三个阶段展示首轮模型与 Memory 预取的真实并发边界、工具结果缩减与 structured folding 的持久化顺序，以及 Session best-effort 保存和 resume 的全局选择、backend、旧 system prompt 与状态恢复风险

    subgraph ASSEMBLY["阶段 1 · 上下文组装"]
        direction TB
        BASE["系统模板、运行环境与项目指令<br/>cwd / date / platform / shell / Git<br/>CLAUDE.md + includes / .skevo/rules"]
        CATALOG["静态目录信息<br/>Memory index / Skill 与 Agent 描述<br/>deferred tool names"]
        SYSTEM["build_system_prompt<br/>+ 可选 Plan prompt<br/>+ Runtime Fold Guidance"]
        CURRENT["① 追加本轮 user message<br/>当前历史 + retrieved_skills"]
        SKILL_CONTEXT["★ retrieved_skills 摘要<br/>追加到本轮 user message"]
        LONG_MEMORY[("跨 Session 长期 Memory<br/>~/.skevo/projects/&lt;hash&gt;/memory/*.md")]
        PREFETCH{"主 Agent 且有 side query？<br/>多词输入 / 已注入 &lt; 60 KiB / 存在 Memory？"}
        PREFETCH_TASK["② create_task 启动 prefetch<br/>异步召回最多 5 条；与首轮 API 并发"]
        MODEL["◇ ③ 首轮模型 API<br/>create_task 后至 settled 检查前无 await<br/>不等待、首轮不可能注入 Memory 正文"]
        FIRST_FINAL["首轮直接 final / 无 tool call<br/>召回结果不进入本次 chat"]

        BASE --> SYSTEM
        CATALOG --> SYSTEM
        LONG_MEMORY -->|MEMORY.md 索引| CATALOG
        SYSTEM --> MODEL
        SKILL_CONTEXT --> CURRENT
        CURRENT --> PREFETCH
        PREFETCH -->|不满足：不创建 task| MODEL
        PREFETCH -->|条件满足| PREFETCH_TASK
        LONG_MEMORY -.->|后台扫描与读取| PREFETCH_TASK
        PREFETCH_TASK -->|create_task 返回；无 await| MODEL
        MODEL -->|final answer| FIRST_FINAL
    end

    subgraph REDUCTION["阶段 2 · 运行中缩减与 structured folding"]
        direction TB
        TOOL_RESULT["工具执行结果"]
        LARGE{"UTF-8 结果 &gt; 30 KiB？"}
        LARGE_STORE[("~/.skevo/tool-results<br/>保存全文；上下文仅保留路径与前 200 行")]
        NEXT_MESSAGES["写入当前 backend messages<br/>供下一次模型调用"]
        NEXT_ITERATION["下一迭代汇合<br/>所有 chat 内路径从此回到 loop 顶部"]
        PIPELINE["每次模型调用前<br/>_run_compression_pipeline"]
        BUDGET["① 单结果字符预算<br/>利用率 ≥50%：30k chars<br/>利用率 &gt;70%：15k chars"]
        SNIP["② stale-result snipping<br/>利用率 ≥60%，保留近 3 条<br/>OpenAI：全部符合条件的历史 role=tool<br/>Anthropic：read_file / grep_search<br/>list_files / run_shell"]
        MICRO["③ idle microcompact<br/>距上次 API 调用 ≥5 min<br/>清旧结果并保留近 3 条"]
        MEMORY_CHECK{"仅进入下一轮时检查上阶段 task<br/>prefetch settled + unconsumed<br/>且成功返回非空结果？"}
        MEMORY_INJECT["追加到最近 user message<br/>标记 consumed；最多一次"]
        MEMORY_SKIP["未完成 / 失败 / 无结果<br/>不等待；继续本轮"]
        MANUAL["REPL /compact（chat 外）<br/>Agent.compact → trigger=manual"]
        TOOL_FOLD["模型调用 compact_context<br/>执行中 trigger=tool"]
        AUTO{"工具批次结束后 auto check<br/>last input &gt; 70% effective window？"}
        FOLD_GATE{"对应 messages ≥ 4<br/>且 transcript 非空？"}
        NO_FOLD_KIND{"未执行 folding 的 trigger？"}
        MANUAL_NO_FOLD["REPL /compact 返回<br/>Nothing to compact"]
        TRANSCRIPT["OpenAI / Anthropic → transcript<br/>普通 message content 按 12k clip<br/>总 transcript 按 80k clip<br/>OpenAI tool_call.arguments 不单独 12k clip"]
        SIDE_QUERY{"side query 可用<br/>且返回 JSON 可解析？"}
        FALLBACK["⚠ fallback_folded_memory<br/>保留最多 6k transcript 摘要"]
        FOLDED["folded session state<br/>episode / working / tool memory"]
        APPEND_FOLD["追加内存列表<br/>_folded_session_memories"]
        SAVE_FOLD["尝试 save_folded_session_memory<br/>项目 .skevo/sessions/<br/>写 JSONL + latest artifacts"]
        FOLD_SAVE_FAIL["⚠ artifacts 写入失败<br/>异常吞掉，不阻断 folding"]
        REPLACE["替换当前原始历史<br/>OpenAI：system + folded user<br/>Anthropic：单条 folded user"]
        FOLD_KIND{"本次 trigger 来源？"}
        MANUAL_DONE["REPL /compact 返回<br/>不产生 tool result / context break"]
        TOOL_BREAK["Anthropic / OpenAI 共同行为<br/>_context_cleared = True<br/>工具结果写为新 user message<br/>停止剩余工具 / context break"]
        NEXT_MODEL["◇ 后续模型 API"]
        NEXT_TOOL_BATCH["后续模型返回 tool call<br/>进入对应工具分支"]
        CHAT_END["主 Agent chat 正常收尾"]

        TOOL_RESULT --> LARGE
        LARGE -->|是：写入全文| LARGE_STORE
        LARGE -->|否：保留原结果| NEXT_MESSAGES
        LARGE_STORE -->|引用 + preview| NEXT_MESSAGES
        NEXT_MESSAGES --> AUTO
        AUTO -->|否| NEXT_ITERATION
        AUTO -->|是：trigger=auto| FOLD_GATE
        NEXT_ITERATION --> PIPELINE --> BUDGET --> SNIP --> MICRO --> MEMORY_CHECK
        MEMORY_CHECK -->|是| MEMORY_INJECT --> NEXT_MODEL
        MEMORY_CHECK -->|否| MEMORY_SKIP --> NEXT_MODEL
        MANUAL -->|trigger=manual| FOLD_GATE
        TOOL_FOLD -->|trigger=tool| FOLD_GATE
        FOLD_GATE -->|否| NO_FOLD_KIND
        NO_FOLD_KIND -->|manual| MANUAL_NO_FOLD
        NO_FOLD_KIND -->|tool：产生结果| TOOL_RESULT
        NO_FOLD_KIND -->|auto| NEXT_ITERATION
        FOLD_GATE -->|是| TRANSCRIPT --> SIDE_QUERY
        SIDE_QUERY -->|是| FOLDED
        SIDE_QUERY -->|否 / 异常| FALLBACK --> FOLDED
        FOLDED --> APPEND_FOLD --> SAVE_FOLD
        SAVE_FOLD -->|save 返回| REPLACE
        SAVE_FOLD -.->|异常吞掉| FOLD_SAVE_FAIL -.->|仍继续| REPLACE
        REPLACE --> FOLD_KIND
        FOLD_KIND -->|manual| MANUAL_DONE
        FOLD_KIND -->|tool| TOOL_BREAK --> NEXT_ITERATION
        FOLD_KIND -->|auto| NEXT_ITERATION
    end

    subgraph PERSISTENCE["阶段 3 · 持久化与恢复"]
        direction TB
        AUTOSAVE["尝试 _auto_save<br/>best-effort"]
        SESSION[("用户级全局 Session JSON<br/>~/.skevo/sessions/&lt;session_id&gt;.json<br/>messages + folded list + metadata")]
        SAVE_FAIL["⚠ Session JSON 写入失败<br/>异常忽略"]
        MANUAL_BOUNDARY["⚠ /compact 后若无正常 chat 收尾<br/>folded list 不进入 Session JSON<br/>artifacts 已尝试保存"]
        NEW_AGENT["当前 CLI 先创建新 Agent<br/>采用当前 backend / prompt / metadata"]
        SELECT["--resume：get_latest_session_id<br/>仅按 startTime 取用户级全局 latest<br/>不按 cwd / project / backend 筛选"]
        RESTORE["load_session → restore_session<br/>只传两种 backend messages<br/>不校验或转换 backend"]
        BACKEND{"保存 backend = 当前 backend？"}
        RESTORED["同 backend：恢复活动 messages<br/>folded user message 可随历史恢复"]
        BACKEND_GAP["⚠ backend 不匹配<br/>历史进入非活动消息列表<br/>当前模型看不到"]
        OPENAI_STALE["⚠ 同 backend OpenAI<br/>保存的旧 system message 覆盖新 prompt<br/>恢复后首轮不 refresh：日期 / cwd / Git /<br/>rules / Memory index 等可能过期"]
        RESUME_GAP["⚠ 其余恢复缺口<br/>不读取 artifacts；不恢复 folded list<br/>id / model / cwd / startTime 等<br/>仍为新 Agent 当前值"]

        CHAT_END --> AUTOSAVE
        AUTOSAVE -->|成功写入| SESSION
        AUTOSAVE -.->|异常忽略| SAVE_FAIL
        SESSION --> SELECT -->|latest by startTime| RESTORE
        NEW_AGENT --> RESTORE --> BACKEND
        BACKEND -->|是| RESTORED
        BACKEND -->|否| BACKEND_GAP
        RESTORE -->|同 backend OpenAI| OPENAI_STALE
        SESSION -.->|folded list / metadata 未传入| RESUME_GAP
    end

    MODEL -->|普通 tool call 执行后| TOOL_RESULT
    MODEL -->|compact_context tool| TOOL_FOLD
    NEXT_MODEL -->|final answer / 无 tool call| CHAT_END
    NEXT_MODEL -->|tool call| NEXT_TOOL_BATCH
    NEXT_TOOL_BATCH -->|普通工具| TOOL_RESULT
    NEXT_TOOL_BATCH -->|compact_context| TOOL_FOLD
    FIRST_FINAL --> CHAT_END
    MANUAL_DONE -.->|若之后无正常 chat 收尾| MANUAL_BOUNDARY
    MANUAL_DONE -.->|后续主 Agent chat 正常收尾时| CHAT_END

    classDef model fill:#DDF4FF,stroke:#0B6B8A,stroke-width:2px,color:#073B4C
    classDef runtime fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef state fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B
    classDef external fill:#ECEFF3,stroke:#53606F,stroke-width:2px,color:#202833

    class MODEL,NEXT_MODEL model
    class SYSTEM,CURRENT,NEXT_MESSAGES,NEXT_ITERATION,PIPELINE,BUDGET,SNIP,MICRO,TRANSCRIPT,REPLACE,MANUAL_DONE,TOOL_BREAK,NEXT_TOOL_BATCH,RESTORED runtime
    class CATALOG,LONG_MEMORY,PREFETCH_TASK,TOOL_RESULT,LARGE_STORE,MEMORY_INJECT,FOLDED,APPEND_FOLD,SESSION state
    class PREFETCH,LARGE,MEMORY_CHECK,MANUAL,TOOL_FOLD,AUTO,FOLD_GATE,NO_FOLD_KIND,SIDE_QUERY,SAVE_FOLD,FOLD_KIND,AUTOSAVE,BACKEND control
    class SKILL_CONTEXT extension
    class FALLBACK,FOLD_SAVE_FAIL,SAVE_FAIL,MANUAL_BOUNDARY,BACKEND_GAP,OPENAI_STALE,RESUME_GAP error
    class BASE,FIRST_FINAL,MEMORY_SKIP,MANUAL_NO_FOLD,CHAT_END,NEW_AGENT,SELECT,RESTORE external

    style ASSEMBLY fill:#F5FAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    style REDUCTION fill:#FFF9F0,stroke:#A85D00,stroke-width:2px,color:#4A2900
    style PERSISTENCE fill:#F4FBF5,stroke:#26733D,stroke-width:2px,color:#123D20
```

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/05-context-and-sessions.mmd -o /tmp/05-context-and-sessions.svg -b white
```

Expected: exit code 0; assembly, reduction, and persistence are distinct; Memory and folded Session state are not visually conflated.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/05-context-and-sessions.mmd
git commit -m "docs: add context and session lifecycle diagram"
```

### Task 6: Create the Skill runtime diagram

**Files:**

- Create: `docs/diagrams/mmd/06-skill-runtime.mmd`

- [ ] **Step 1: Write the complete flowchart**

```mermaid
---
title: Skill 发现、检索、调用与执行
config:
  theme: base
  look: classic
  flowchart:
    curve: basis
---
%% Purpose: 区分 Skill 发现、自动检索、显式调用和 inline/fork 执行。
%% Audience: both
%% Sources: agents/skills.py, agents/main.py, agents/agent.py, agents/skill_evolution.py
%% Anchors: discover_skills, retrieve_relevant_skills, format_retrieved_skill_context, execute_skill, Agent._execute_skill_tool
%% Out of scope: 在线 add/merge/discard、评测和 MCP 初始化。

flowchart TD
    USER_SKILLS[("💾 ~/.skevo/skills")]
    PROJECT_SKILLS[("💾 项目 .skevo/skills")]
    LOAD["加载 SKILL.md frontmatter"]
    DEFINITIONS["★ SkillDefinition cache<br/>用户级同名项优先；项目级不覆盖"]
    REQUEST["👤 用户请求"]
    BM25["BM25 检索<br/>metadata 词频 ×3 + 正文前 2500 chars<br/>score ≥ 0.08，最多 top 3"]
    HITS{"有相关 Skill?"}
    SUMMARY["top 3 metadata<br/>retrieved_skills"]
    MODEL["◇ 模型判断是否调用"]
    EXPLICIT["/<skill-name> args"]
    LOOKUP["get_skill_by_name"]
    USER_OK{"存在且 user_invocable?"}
    FALLBACK["按普通文本进入 Agent.chat<br/>不直接返回 Unknown"]
    FORK_REQUEST["fork slash：请求模型调用 skill tool"]
    TOOL_CALL["模型调用 skill tool"]
    EXECUTE["execute_skill<br/>按 name 再次查找"]
    KNOWN{"Skill 存在?"}
    STATS["记录 invocation stats"]
    RESOLVE["resolve_skill_prompt<br/>参数与 Skill 目录占位符"]
    MODE{"context mode"}
    INLINE["inline：Prompt 回到当前 Agent Loop"]
    FORK["fork：按 allowed_tools 当前真值语义选工具<br/>隔离 system prompt / history；详见图 09"]
    ERROR["❌ Unknown Skill / Skill fork error"]

    USER_SKILLS --> LOAD
    PROJECT_SKILLS --> LOAD
    LOAD --> DEFINITIONS
    REQUEST --> BM25
    DEFINITIONS --> BM25
    BM25 --> HITS
    HITS -->|否| MODEL
    HITS -->|是| SUMMARY --> MODEL
    MODEL -->|调用 skill| TOOL_CALL --> EXECUTE
    EXPLICIT --> LOOKUP --> USER_OK
    USER_OK -->|否| FALLBACK --> REQUEST
    USER_OK -->|是：inline| EXECUTE
    USER_OK -->|是：fork| FORK_REQUEST --> MODEL
    DEFINITIONS --> LOOKUP
    EXECUTE --> KNOWN
    KNOWN -->|否| ERROR
    KNOWN -->|是| STATS --> RESOLVE --> MODE
    MODE -->|inline| INLINE
    MODE -->|fork| FORK

    classDef actor fill:#FFF2B2,stroke:#9A6700,stroke-width:2px,color:#3B2A00
    classDef model fill:#DDF4FF,stroke:#0B6B8A,stroke-width:2px,color:#073B4C
    classDef state fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B

    class REQUEST,EXPLICIT actor
    class MODEL model
    class USER_SKILLS,PROJECT_SKILLS,LOAD,DEFINITIONS,STATS state
    class BM25,HITS,LOOKUP,USER_OK,KNOWN,MODE control
    class SUMMARY,FORK_REQUEST,TOOL_CALL,EXECUTE,RESOLVE,INLINE,FORK extension
    class FALLBACK state
    class ERROR error
```

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/06-skill-runtime.mmd -o /tmp/06-skill-runtime.svg -b white
```

Expected: exit code 0; the automatic and explicit entry paths converge only at execution; retrieval does not imply activation.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/06-skill-runtime.mmd
git commit -m "docs: add Skill runtime diagram"
```

### Task 7: Create the online Skill evolution diagram

**Files:**

- Create: `docs/diagrams/mmd/07-skill-evolution.mmd`

- [ ] **Step 1: Write the complete flowchart**

```mermaid
---
title: 在线 Skill 演化闭环
config:
  theme: base
  look: classic
  flowchart:
    curve: basis
---
%% Purpose: 展示连续对话与用户反馈如何形成 add/merge/discard 决策和审计记录。
%% Audience: both
%% Sources: agents/agent.py, agents/online_skill_evolution.py, agents/skills.py, agents/skill_evolution.py
%% Anchors: Agent._set_pending_skill_extraction_window, extract_online_skill_candidate, maintain_online_skill_candidate, online_ingest
%% Out of scope: replay 评测和 Champion promotion。

flowchart TD
    TURN["本轮用户输入 + assistant reply"]
    PENDING["保存 pending extraction window"]
    FEEDBACK["下一轮用户输入作为反馈"]
    READY["上一窗口成熟"]
    EXTRACT["Extractor<br/>最多一个 durable candidate"]
    CANDIDATE{"产生候选?"}
    NONE["none"]
    REFERENCES["现有 Skills<br/>identity / BM25 / retrieved reference"]
    MANAGER["Manager 决策"]
    RULES["规则修正<br/>exact match → merge<br/>高相似 add → merge<br/>非法 action → discard"]
    ACTION{"add / merge / discard"}
    DISCARD["discard"]
    CONFIRM{"写入权限允许?"}
    DENIED["❌ add_denied / merge_denied"]
    ADD["create_skill<br/>项目级 inline Skill"]
    MERGE["evolve_skill<br/>active Skill 新版本"]
    AUDIT["版本快照与 lifecycle stats"]
    PROVENANCE[("💾 provenance log / index")]
    POLICY["⚠ Plan Mode 不调度后台演化<br/>后台仅 bypassPermissions / acceptEdits 自动写<br/>extract_now 可交互确认"]

    TURN --> PENDING
    FEEDBACK --> READY
    PENDING --> READY
    READY --> EXTRACT --> CANDIDATE
    CANDIDATE -->|否| NONE --> PROVENANCE
    CANDIDATE -->|是| MANAGER
    REFERENCES --> MANAGER
    MANAGER --> RULES --> ACTION
    ACTION -->|discard / 非法 action| DISCARD --> PROVENANCE
    ACTION -->|add / merge| CONFIRM
    POLICY -.-> CONFIRM
    CONFIRM -->|否| DENIED --> PROVENANCE
    CONFIRM -->|add| ADD --> AUDIT
    CONFIRM -->|merge| MERGE --> AUDIT
    AUDIT --> PROVENANCE

    classDef actor fill:#FFF2B2,stroke:#9A6700,stroke-width:2px,color:#3B2A00
    classDef runtime fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef state fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B
    classDef note fill:#FFF4CC,stroke:#A15C00,stroke-width:2px,color:#3A2600

    class TURN,FEEDBACK actor
    class PENDING,READY,EXTRACT,MANAGER runtime
    class REFERENCES,AUDIT,PROVENANCE state
    class CANDIDATE,RULES,ACTION,CONFIRM control
    class NONE,DISCARD,ADD,MERGE extension
    class DENIED error
    class POLICY note
```

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/07-skill-evolution.mmd -o /tmp/07-skill-evolution.svg -b white
```

Expected: exit code 0; every terminal action reaches provenance; the policy note is non-blocking and visually secondary.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/07-skill-evolution.mmd
git commit -m "docs: add online Skill evolution diagram"
```

### Task 8: Create the Skill evaluation diagram

**Files:**

- Create: `docs/diagrams/mmd/08-skill-evaluation.mmd`

- [ ] **Step 1: Write the complete flowchart**

```mermaid
---
title: Skill 评测、候选比较与 Champion 晋升
config:
  theme: base
  look: classic
  flowchart:
    curve: basis
---
%% Purpose: 展示评测数据如何进入 lifecycle status gate 和 Champion promotion gate。
%% Audience: maintainer
%% Sources: agents/online_skill_eval.py, agents/skill_evolution.py
%% Anchors: _build_replay_pool, _assign_replay_splits, _compile_eval_rules, _build_candidate_eval_bundle_async, _skill_status, _promotion_decision, _persist_eval_artifacts
%% Out of scope: 在线候选提取和 Skill 执行。

flowchart LR
    INPUTS["评测输入<br/>provenance / usage / lifecycle<br/>active Skill snapshot"]
    LINEAGE["稳定 lineage ID"]
    REPLAY["构建并冻结 replay pool"]
    SPLIT["mutate_dev / promotion_test"]
    RULES["确定性规则<br/>+ 可选 LLM binary judge"]
    VARIANTS["heuristic variants<br/>+ 可选 LLM variant"]
    DEV["mutate_dev 生成与评估"]
    BEST["选择最佳候选"]
    TEST["promotion_test 独立评估"]
    STATUS{"lifecycle status gate"}
    NOT_HEALTHY["unobserved / incubating<br/>watch / pruned"]
    HEALTHY["healthy"]
    CHAMPION{"已有 Champion?"}
    FIRST["首个健康候选"]
    BEAT{"平均分提升 ≥ min_score_delta<br/>且 hard failures 不增加?"}
    PROMOTE["active_champion"]
    REJECT["rejected"]
    ARTIFACTS[("💾 dataset / eval spec / runs / report<br/>champion registry / JSON / SKILL.md")]
    NOTE["Champion 不覆盖 active Skill"]

    INPUTS --> LINEAGE --> REPLAY --> SPLIT
    SPLIT --> RULES
    SPLIT --> VARIANTS
    RULES --> DEV
    VARIANTS --> DEV --> BEST --> TEST --> STATUS
    STATUS -->|非 healthy| NOT_HEALTHY --> REJECT
    STATUS -->|healthy| HEALTHY --> CHAMPION
    CHAMPION -->|否| FIRST --> PROMOTE
    CHAMPION -->|是| BEAT
    BEAT -->|是| PROMOTE
    BEAT -->|否| REJECT
    PROMOTE --> ARTIFACTS
    REJECT --> ARTIFACTS
    ARTIFACTS -.-> NOTE

    classDef runtime fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef state fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef control fill:#FFE8C2,stroke:#A85D00,stroke-width:2px,color:#4A2900
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B
    classDef note fill:#FFF4CC,stroke:#A15C00,stroke-width:2px,color:#3A2600

    class INPUTS,LINEAGE,REPLAY,SPLIT,RULES,VARIANTS,DEV,BEST,TEST runtime
    class ARTIFACTS state
    class STATUS,CHAMPION,BEAT control
    class HEALTHY,FIRST,PROMOTE extension
    class NOT_HEALTHY,REJECT error
    class NOTE note
```

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/08-skill-evaluation.mmd -o /tmp/08-skill-evaluation.svg -b white
```

Expected: exit code 0; mutate-dev selection and promotion-test evaluation are visibly separate; rejected and promoted paths both persist artifacts.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/08-skill-evaluation.mmd
git commit -m "docs: add Skill evaluation and promotion diagram"
```

### Task 9: Create the MCP and sub-agent boundaries diagram

**Files:**

- Create: `docs/diagrams/mmd/09-mcp-and-subagents.mmd`

- [ ] **Step 1: Write the complete flowchart**

```mermaid
---
title: MCP 进程边界与子 Agent 上下文边界
config:
  theme: base
  look: classic
  flowchart:
    curve: basis
---
%% Purpose: 展示 Runtime 跨越 MCP 进程边界和子 Agent 上下文边界的方式。
%% Audience: maintainer
%% Sources: agents/mcp_client.py, agents/subagent.py, agents/agent.py
%% Anchors: McpManager.load_and_connect, McpManager.get_tool_definitions, McpManager.call_tool, get_sub_agent_config, Agent._execute_agent_tool, Agent._execute_skill_tool
%% Out of scope: 通用权限决策和 Skill 检索。

flowchart LR
    RUNTIME["⚙ 主 Agent Runtime"]

    subgraph MCP_BOUNDARY["MCP 进程边界"]
        CONFIG["配置覆盖<br/>用户 settings → 项目 settings → .mcp.json"]
        MANAGER["🔌 McpManager"]
        PROCESS["stdio MCP 子进程"]
        HANDSHAKE["initialize → initialized → tools/list"]
        DEFINITIONS["mcp__server__tool definitions"]
        ROUTE["解析 server / tool name<br/>tools/call"]
        MCP_RESULT["MCP content → tool result"]
        MCP_FAIL["⚠ 单 server 失败只关闭自身"]
        CONFIG --> MANAGER --> PROCESS --> HANDSHAKE --> DEFINITIONS
        ROUTE --> PROCESS --> MCP_RESULT
        PROCESS -.-> MCP_FAIL
    end

    subgraph SUB_BOUNDARY["子 Agent 上下文边界"]
        ENTRY["agent tool / Skill fork"]
        CONFIG_AGENT["get_sub_agent_config"]
        TYPES["explore / plan / general / custom"]
        TOOLS["只读集合 / allowed-tools<br/>或除 agent 外的工具"]
        CHILD["◎ 新 Agent<br/>独立 prompt / messages / loop"]
        ISOLATION["is_sub_agent = True<br/>无 Memory 注入 / MCP 懒加载 / 在线演化"]
        CHILD_RESULT["最终文本 + token 增量"]
        CHILD_FAIL["❌ Sub-agent / Skill fork error"]
        ENTRY --> CONFIG_AGENT --> TYPES --> TOOLS --> CHILD
        CHILD --> ISOLATION --> CHILD_RESULT
        CHILD --> CHILD_FAIL
    end

    RUNTIME -->|首次 chat| MANAGER
    DEFINITIONS -->|追加 self.tools| RUNTIME
    RUNTIME -->|mcp__server__tool| ROUTE
    MCP_RESULT --> RUNTIME
    RUNTIME --> ENTRY
    CHILD_RESULT --> RUNTIME
    CHILD_FAIL --> RUNTIME
    RISK["⚠ 子 Agent 可继承 MCP definitions<br/>但新的 McpManager 未连接<br/>definition 不等于可用 connection"]
    DEFINITIONS -.-> TOOLS
    TOOLS -.-> RISK

    classDef runtime fill:#DCEAFF,stroke:#2855B5,stroke-width:2px,color:#102A5C
    classDef state fill:#E2F5E7,stroke:#26733D,stroke-width:2px,color:#123D20
    classDef extension fill:#EFE3FF,stroke:#7040A8,stroke-width:2px,color:#32184F
    classDef error fill:#FFE0E0,stroke:#B42318,stroke-width:2px,color:#5A0B0B
    classDef note fill:#FFF4CC,stroke:#A15C00,stroke-width:2px,color:#3A2600

    class RUNTIME runtime
    class CONFIG,CONFIG_AGENT,TOOLS,ISOLATION state
    class MANAGER,PROCESS,HANDSHAKE,DEFINITIONS,ROUTE,MCP_RESULT,ENTRY,TYPES,CHILD,CHILD_RESULT extension
    class CHILD_FAIL error
    class MCP_FAIL,RISK note
```

- [ ] **Step 2: Validate and render**

```bash
mmdc -i docs/diagrams/mmd/09-mcp-and-subagents.mmd -o /tmp/09-mcp-and-subagents.svg -b white
```

Expected: exit code 0; MCP and sub-agent boundaries share the central Runtime but remain visually distinct; both risk notes are legible.

- [ ] **Step 3: Commit**

```bash
git add docs/diagrams/mmd/09-mcp-and-subagents.mmd
git commit -m "docs: add MCP and sub-agent boundaries diagram"
```

### Task 10: Regenerate all SVG and PNG outputs

**Files:**

- Create: `docs/diagrams/svg/01-system-architecture.svg` through `09-mcp-and-subagents.svg`
- Create: `docs/diagrams/png/01-system-architecture.png` through `09-mcp-and-subagents.png`

- [ ] **Step 1: Ensure output directories exist**

```bash
mkdir -p docs/diagrams/svg docs/diagrams/png
```

- [ ] **Step 2: Render every MMD to SVG**

```bash
for source in docs/diagrams/mmd/*.mmd; do
  name=${source##*/}
  name=${name%.mmd}
  mmdc -i "$source" -o "docs/diagrams/svg/$name.svg" -b white
done
```

Expected: nine successful Mermaid CLI runs and nine non-empty SVG files.

- [ ] **Step 3: Render every MMD to 2× PNG**

```bash
for source in docs/diagrams/mmd/*.mmd; do
  name=${source##*/}
  name=${name%.mmd}
  mmdc -i "$source" -o "docs/diagrams/png/$name.png" -b white -s 2
done
```

Expected: nine successful Mermaid CLI runs and nine non-empty PNG files.

- [ ] **Step 4: Verify file counts and image types**

```bash
find docs/diagrams/mmd -maxdepth 1 -type f -name '*.mmd' | wc -l
find docs/diagrams/svg -maxdepth 1 -type f -name '*.svg' | wc -l
find docs/diagrams/png -maxdepth 1 -type f -name '*.png' | wc -l
file docs/diagrams/png/*.png
```

Expected: `9`, `9`, `9`; every PNG is reported as PNG image data.

- [ ] **Step 5: Visually inspect every generated image**

Create a temporary contact sheet or open the images individually. Check node overlap, clipped Chinese text, edge-label collisions, excessive width, white background, and readability at thumbnail size. If a diagram fails visual review, edit only its MMD and rerender both formats before continuing.

- [ ] **Step 6: Commit rendered assets**

```bash
git add docs/diagrams/svg docs/diagrams/png
git commit -m "docs: render Mermaid diagram assets"
```

### Task 11: Rewrite the diagram index and update the root README

**Files:**

- Replace: `docs/diagrams/README.md`
- Modify: `README.md`

- [ ] **Step 1: Replace the diagram README**

Write `docs/diagrams/README.md` with this content:

```markdown
# Skevo Mermaid 图集

本目录以当前 Python 实现为事实来源，管理 Skevo 的 Mermaid 图源和渲染产物。

- `mmd/`：可维护的 Mermaid 源文件。
- `svg/`：用于 Markdown 和网页的矢量图。
- `png/`：用于预览、汇报和不支持 SVG 的场景，按 2 倍缩放生成。

全部图源均使用 Mermaid CLI 11.16.0 验证，并以白色背景生成 SVG 和 PNG。

## 快速理解

| 图 | 说明 | 主要读者 |
| --- | --- | --- |
| [01 系统架构](svg/01-system-architecture.svg) | Skevo 的系统边界、内部职责和外部依赖 | 所有人 |
| [02 Agent Loop](svg/02-agent-loop.svg) | 一次请求从输入到保存和后台任务的完整生命周期 | 所有人 |

## Runtime 机制

| 图 | 说明 | 主要读者 |
| --- | --- | --- |
| [03 工具加载与路由](svg/03-tool-loading-and-dispatch.svg) | eager/deferred/MCP/custom 工具如何进入模型并被执行 | 维护者 |
| [04 权限与 Plan Mode](svg/04-permissions-and-plan-mode.svg) | `check_permission` 顺序和 Plan Mode 状态 | 维护者 |
| [05 上下文与会话](svg/05-context-and-sessions.svg) | Prompt、Memory、压缩、folding、保存与恢复 | 维护者 |

## 能力与扩展

| 图 | 说明 | 主要读者 |
| --- | --- | --- |
| [06 Skill Runtime](svg/06-skill-runtime.svg) | Skill 发现、检索、调用与 inline/fork 执行 | 所有人 |
| [07 Skill 演化](svg/07-skill-evolution.svg) | 用户反馈驱动的 add/merge/discard 闭环 | 所有人 |
| [08 Skill 评测](svg/08-skill-evaluation.svg) | replay、规则、候选比较和 Champion 晋升 | 维护者 |
| [09 MCP 与子 Agent](svg/09-mcp-and-subagents.svg) | MCP 进程边界和子 Agent 上下文边界 | 维护者 |

每张图都有同 basename 的三种文件：

```text
mmd/01-system-architecture.mmd
svg/01-system-architecture.svg
png/01-system-architecture.png
```

## 推荐阅读路径

- 项目访客：`01 → 02 → 06 → 07`
- Runtime 维护者：`01 → 02 → 03 → 04 → 05 → 09`
- 自进化机制研究者：`06 → 07 → 08`
- 完整维护者：按编号阅读 `01 → 09`

## 重新渲染

```bash
mkdir -p docs/diagrams/svg docs/diagrams/png
for source in docs/diagrams/mmd/*.mmd; do
  name=${source##*/}
  name=${name%.mmd}
  mmdc -i "$source" -o "docs/diagrams/svg/$name.svg" -b white
  mmdc -i "$source" -o "docs/diagrams/png/$name.png" -b white -s 2
done
```

## 权威代码

- Runtime 与 Agent Loop：`agents/agent.py`
- CLI 与 Plan 审批入口：`agents/main.py`
- Prompt 构建：`agents/prompt.py`
- 工具与权限：`agents/tools.py`
- Memory 与 Session：`agents/memory.py`、`agents/session_memory.py`、`agents/session.py`
- Skill Runtime 与演化：`agents/skills.py`、`agents/online_skill_evolution.py`、`agents/skill_evolution.py`
- Skill 评测：`agents/online_skill_eval.py`
- MCP 与子 Agent：`agents/mcp_client.py`、`agents/subagent.py`

图中带 `⚠` 的节点表示当前实现的已知风险或降级边界，不代表已修复行为。
```

- [ ] **Step 2: Update only the architecture image path in the root README**

Replace the existing architecture image line. In the shared workspace it currently reads:

```markdown
![Skevo Agent 总体架构](docs/diagrams/svg/01-overall-architecture.svg)
```

A clean worktree created from the committed baseline may instead contain:

```markdown
![Skevo Agent 总体架构](wiki/assets/architecture/01-overall-architecture.svg)
```

Replace whichever one is present with:

```markdown
![Skevo Agent 系统架构](docs/diagrams/svg/01-system-architecture.svg)
```

Do not alter any other root README lines.

- [ ] **Step 3: Verify every Markdown image link exists**

Run:

```bash
rg -n 'docs/diagrams|svg/' README.md docs/diagrams/README.md
```

Expected: the root README references only `01-system-architecture.svg`; the diagram README references all nine new SVG basenames and no legacy basename.

- [ ] **Step 4: Commit documentation integration**

```bash
git add README.md docs/diagrams/README.md
git commit -m "docs: publish the Mermaid diagram suite"
```

### Task 12: Run the final verification gate

**Files:**

- Verify all files created or modified by Tasks 1–11

- [ ] **Step 1: Revalidate every MMD from source**

```bash
for source in docs/diagrams/mmd/*.mmd; do
  name=${source##*/}
  name=${name%.mmd}
  mmdc -i "$source" -o "/tmp/$name.verify.svg" -b white
done
```

Expected: nine exit-code-0 runs.

- [ ] **Step 2: Compare MMD, SVG, and PNG basename sets**

```bash
find docs/diagrams/mmd -maxdepth 1 -type f -name '*.mmd' -printf '%f\n' | sed 's/\.mmd$//' | sort > /tmp/skevo-mmd.names
find docs/diagrams/svg -maxdepth 1 -type f -name '*.svg' -printf '%f\n' | sed 's/\.svg$//' | sort > /tmp/skevo-svg.names
find docs/diagrams/png -maxdepth 1 -type f -name '*.png' -printf '%f\n' | sed 's/\.png$//' | sort > /tmp/skevo-png.names
diff -u /tmp/skevo-mmd.names /tmp/skevo-svg.names
diff -u /tmp/skevo-mmd.names /tmp/skevo-png.names
```

Expected: both `diff` commands produce no output and exit 0.

- [ ] **Step 3: Verify source metadata, title coverage, and legacy-name removal**

```bash
rg -L '^---$' docs/diagrams/mmd/*.mmd
rg -L '^%% Purpose:' docs/diagrams/mmd/*.mmd
rg -L '^%% Sources:' docs/diagrams/mmd/*.mmd
rg -n 'overall-architecture|permission-and-plan-mode|context-folding|memory-and-skills' README.md docs/diagrams
```

Expected: the first three commands produce no missing-file output; the legacy-name search returns no matches.

- [ ] **Step 4: Verify output files and repository whitespace**

```bash
test "$(find docs/diagrams/mmd -maxdepth 1 -type f -name '*.mmd' -size +0c | wc -l)" -eq 9
test "$(find docs/diagrams/svg -maxdepth 1 -type f -name '*.svg' -size +0c | wc -l)" -eq 9
test "$(find docs/diagrams/png -maxdepth 1 -type f -name '*.png' -size +0c | wc -l)" -eq 9
git diff --check
```

Expected: all `test` commands exit 0 and `git diff --check` produces no output.

- [ ] **Step 5: Review the final diff without disturbing unrelated work**

```bash
git status --short
git diff 899302f..HEAD -- README.md docs/diagrams
git log --oneline -12
```

Expected: the committed diff from the approved design commit contains only the requested README and diagram-suite changes in these paths; no Python file is modified; unrelated user changes are preserved.

- [ ] **Step 6: Record verification evidence in the handoff**

Report the Mermaid CLI version, nine successful source validations, `9/9/9` file counts, basename-set equality, visual-review result, README link result, and any implementation risks shown in diagrams. Do not claim completion if any render or visual check failed.
