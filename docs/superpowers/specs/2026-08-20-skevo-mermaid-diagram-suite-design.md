# Skevo Mermaid 图集重建设计

日期：2026-08-20
状态：待书面审阅
事实来源：当前仓库中的 Python 实现

## 1. 背景

`docs/diagrams/mmd/` 原有 8 个 Mermaid 文件均为空，旧的 SVG 和 PNG 已被删除。现有 `docs/diagrams/README.md` 仍描述旧图集并声称图源已经过 Mermaid CLI 验证，因此文档状态与工作区事实不一致。

本次工作不恢复旧图布局，而是以当前 Python 实现为唯一事实来源，重新设计图集的数量、主题、文件名、图型、内容边界和渲染规范。图集同时服务两类读者：首次了解 Skevo 的项目访客，以及准备维护 Runtime、自进化机制和扩展系统的开发者。

## 2. 目标

- 用分层图集解释 Skevo 的静态架构、动态 Agent Loop、执行控制、上下文状态、Skills 和扩展边界。
- 每张图只回答一个稳定问题，避免跨抽象层和重复展开同一机制。
- 中文说明优先，保留必要的模块名、函数名、协议名和状态枚举。
- Mermaid 源文件可独立维护、验证和重新渲染。
- MMD、SVG、PNG 严格一一对应。
- 根 README 只展示系统主图，完整图集由 `docs/diagrams/README.md` 索引。
- 对当前实现中的疑点进行显式标注，不把疑似失效路径包装为已验证能力。

## 3. 非目标

- 不修改任何 Python 运行逻辑。
- 不修复 Plan Mode、MCP 或子 Agent 中发现的实现疑点。
- 不生成逐函数调用图、类图或完整目录树。
- 不复刻已经删除的 SVG/PNG 布局。
- 不在根 README 中嵌入全部图表。
- 不为未实现或仅存在于提示词中的能力补画理想化流程。

## 4. 设计原则

### 4.1 单一事实责任

每张图拥有唯一的展开责任。其他图只引用该机制，不复制完整子流程。

| 机制 | 权威图 |
| --- | --- |
| 系统边界与静态组件 | `01-system-architecture` |
| 一次请求的执行顺序 | `02-agent-loop` |
| 工具加载、激活和路由 | `03-tool-loading-and-dispatch` |
| 权限与 Plan Mode | `04-permissions-and-plan-mode` |
| Prompt、Memory、压缩和 Session | `05-context-and-sessions` |
| Skill 发现、检索和执行 | `06-skill-runtime` |
| 在线 Skill 变更 | `07-skill-evolution` |
| Skill 评测与 Champion 晋升 | `08-skill-evaluation` |
| MCP 与子 Agent 边界 | `09-mcp-and-subagents` |

### 4.2 一致的抽象层

- 架构图展示组件和边界，不混入函数内部条件。
- 时序图展示参与者交互，不展开完整决策树。
- 流程图展示实际控制分支，并标出主要失败或降级路径。
- 节点使用概念名作为主标签，必要时用次级标签注明模块或函数锚点。
- 普通流程图控制在约 15–20 个主节点；复杂阶段使用 `subgraph` 分组。

### 4.3 代码可追溯性

每个 MMD 文件记录：

- `Purpose`
- `Audience`
- `Sources`
- `Anchors`
- `Out of scope`

图中的关键机制必须能够追溯到当前 Python 模块和函数。未核实的行为使用 `⚠` 注记说明。

## 5. 文件集合与命名

最终图集包含 9 张图：

```text
docs/diagrams/
├── README.md
├── mmd/
│   ├── 01-system-architecture.mmd
│   ├── 02-agent-loop.mmd
│   ├── 03-tool-loading-and-dispatch.mmd
│   ├── 04-permissions-and-plan-mode.mmd
│   ├── 05-context-and-sessions.mmd
│   ├── 06-skill-runtime.mmd
│   ├── 07-skill-evolution.mmd
│   ├── 08-skill-evaluation.mmd
│   └── 09-mcp-and-subagents.mmd
├── svg/
│   └── 9 个同名 SVG
└── png/
    └── 9 个同名 PNG
```

命名格式为：

```text
<两位阅读序号>-<稳定技术主题>.<ext>
```

命名约束：

- 使用小写英文和 kebab-case。
- basename 使用 2–5 个语义词。
- 不把 `flowchart`、`sequence` 等 Mermaid 图型写入文件名。
- 不重复父目录已经提供的 `diagram` 或 `mermaid` 语境。
- MMD、SVG、PNG 使用完全相同的 basename。
- 编号表示默认阅读顺序，不表示组件优先级。

## 6. 图表规格

### 6.1 `01-system-architecture.mmd`

图内标题：Skevo 系统架构
图型：`flowchart TB`
读者：访客与维护者
目的：说明静态系统边界、内部责任和外部依赖。

内容分层：

- 交互层：用户、CLI、REPL、one-shot、`agents/main.py`。
- Harness Runtime：Agent Runtime、Prompt/模型适配、工具/权限、上下文/会话、Skills/自进化、MCP/子 Agent。
- 外部能力：OpenAI-compatible、Anthropic-compatible、文件系统、Shell、MCP Server。
- 持久化：用户级 `~/.skevo`、项目级 `.skevo`、Session 数据。

必须表达：

- 模型负责推理和产生 tool call。
- Runtime 负责权限、执行、结果回写、上下文压缩和持久化。
- OpenAI/Anthropic 是同一 Runtime 的两个协议路径。
- 本地环境和 MCP Server 位于 Skevo 系统边界之外。

排除：权限分支、Agent Loop、Skill promotion gate 和 MCP 消息细节。

权威源码：`agents/main.py`、`agents/agent.py`、`agents/prompt.py`、`agents/tools.py`、`agents/memory.py`、`agents/skills.py`、`agents/session.py`、`agents/mcp_client.py`、`agents/subagent.py`。

### 6.2 `02-agent-loop.mmd`

图内标题：Agent Loop：一次请求的完整生命周期
图型：`sequenceDiagram`
读者：访客与维护者
目的：按真实顺序展示一次用户请求的运行过程。

参与者：用户、CLI、Agent Runtime、Skills、Memory、模型后端、工具运行时、Session/后台任务。

核心时序：

1. `run_repl` 或 `run_one_shot` 调用 `Agent.chat`。
2. 主 Agent 首次对话时懒加载 MCP。
3. 消费上一轮 pending Skill extraction window。
4. BM25 检索 Skill 摘要并增强用户消息。
5. OpenAI/Anthropic 路径启动异步 Memory 预取。
6. 每轮模型调用前执行 compression pipeline。
7. Memory 已返回时最多注入一次。
8. 模型调用通过 `_with_retry` 处理可重试错误。
9. 流式输出文本并组装 tool calls。
10. 无 tool call 时结束当前回复。
11. 有 tool call 时检查 `max_turns` 和 `max_cost_usd`。
12. 超预算时跳过工具并结束；未超预算时进入工具运行时。
13. 工具结果写回模型并继续循环。
14. context break 或 abort 会终止相应循环。
15. 每个工具结果批次结束后检查自动 compaction；整个 `chat` 结束后保存 Session、调度 Skill 后台任务，并建立下一轮 pending window。

Mermaid 使用约束：

- 用一个 `alt` 表达 OpenAI/Anthropic 协议分支。
- 用一个 `loop` 表达 agentic tool loop。
- 用 `alt` 表达无工具、有工具和超预算。
- 用异步箭头表达后台任务。
- MCP 初始化失败和 Memory 预取失败只做非阻断降级注记。

排除：权限规则细节、built-in tool 内部实现、Skill add/merge/discard 和 folded-memory JSON 字段。

权威锚点：`Agent.chat`、`Agent._chat_anthropic`、`Agent._chat_openai`、`Agent._check_budget`、`Agent._check_and_compact`、`Agent._auto_save`。

### 6.3 `03-tool-loading-and-dispatch.mmd`

图内标题：工具加载、按需激活与执行路由
图型：`flowchart LR`
读者：维护者
目的：说明模型能看到哪些工具，以及获准的调用由谁执行。

三个子图：

1. 工具来源：eager tools、deferred tools、MCP tools、custom tools。
2. 按需激活：system prompt 列出 deferred 名称；`tool_search` 返回完整 schema；工具被记录为 active；后续模型请求包含该定义。
3. 执行路由：特殊上下文/计划工具、Skill、agent、MCP 和 built-in `execute_tool`。

必须表达：

- 默认 `tool_definitions` 中的 `tool_search` 是 eager tool；非空 `custom_tools` 替换默认集合时，不会自动保留它。
- `tool_search` 命中默认 deferred tool 时记录 activated name 并返回完整 schema；后续请求只会暴露当前 `self.tools` 中非 deferred 或同名已激活的成员。
- MCP 工具仅在主 Agent 首次 `chat` 成功完成加载、连接和发现后追加到当前 `self.tools`。
- 非空 custom tools 由子 Agent 或 Skill fork 注入，并替换默认 `tool_definitions` 成为初始 `self.tools`。
- built-in 工具结果会截断；大结果可能持久化后以引用返回。
- 未知工具由 built-in `execute_tool` 返回错误文本；Anthropic 路径会捕获执行异常并归一为 tool result；OpenAI sequential/concurrent 路径当前未捕获的执行异常可能终止 Agent Loop。

排除：权限模式决策、MCP initialize 细节和子 Agent 类型。

权威锚点：`tool_definitions`、`get_active_tool_definitions`、`get_deferred_tool_names`、`execute_tool`、`Agent._execute_tool_call`、`Agent._persist_large_result`。

### 6.4 `04-permissions-and-plan-mode.mmd`

图内标题：权限决策与 Plan Mode 状态转换
图型：`flowchart TD`
读者：维护者
目的：严格表达 `check_permission` 顺序和 Plan Mode 对工具权限的影响。

权限顺序：

1. `bypassPermissions` 直接允许。
2. permission rules 中 deny 优先于 allow。
3. `READ_TOOLS` 直接允许。
4. Plan Mode 允许 `READ_TOOLS` 和唯一 plan 文件，拒绝其他编辑与 Shell。
5. `enter_plan_mode`、`exit_plan_mode` 允许。
6. `acceptEdits` 自动允许 `EDIT_TOOLS`。
7. 危险 Shell、新文件写入、不存在文件编辑、`skill_create` 和 `skill_evolve` 需要确认。
8. `dontAsk` 对需要确认的操作自动拒绝。
9. 其余操作允许。

Plan Mode 状态：`--plan` 初始化或显式进入时生成唯一 plan 文件路径并注入 system prompt；只有通过 `/plan` 或 `enter_plan_mode` 显式进入时才执行 `_pre_plan_mode = 当前模式`，CLI `--plan` 初始化不会保存 `_pre_plan_mode`。plan 文件本身要到工具写入时才会创建。运行时由 system prompt 声明只读意图，并由 `check_permission` 执行部分约束。再次执行 `/plan`，以及无审批回调时执行 `exit_plan_mode`，都会通过 `permission_mode = _pre_plan_mode or "default"` 退出：显式进入通常恢复所保存的模式，而 CLI `--plan` 因 `_pre_plan_mode` 为 `None` 会落到 `default`。交互式审批原本提供继续规划、执行、清空上下文后执行和手工执行四种选择，但当前实现会先触发下述异步回调缺陷，因而这些选择分支实际不可达。

当前实现风险必须显式注记：

- `_plan_approval_fn` 是异步回调，但 `_execute_plan_mode_tool` 当前直接调用。
- `exit_plan_mode` 当前把 plan 文件路径赋给 `plan_content`，没有读取文件正文。
- 交互审批分支没有明确把 `target_mode` 赋给 `permission_mode`。
- `READ_TOOLS` 包含 `compact_context`；此外，当前权限函数只在 Plan Mode 中显式拒绝 `EDIT_TOOLS` 和 `run_shell`，其他未命中分支的工具仍会落到默认允许，因此实际 enforcement 比 Plan Mode prompt 宣称的“只读”范围更宽。
- `toggle_plan_mode` 通过 `/plan` 进入时会更新 `self._system_prompt`，但 OpenAI 路径没有同步已有消息历史中的 system message；通过 `enter_plan_mode` 工具进入时则会同步。

上述风险不得画成已验证成功路径，也不在本任务中修复。

权威锚点：`_resolve_permission_mode`、`check_permission`、`Agent.toggle_plan_mode`、`Agent._execute_plan_mode_tool`、`run_repl.plan_approval_fn`。

### 6.5 `05-context-and-sessions.mmd`

图内标题：上下文、长期记忆与会话生命周期
图型：`flowchart TB`
读者：维护者
目的：展示模型上下文的组装、缩减、structured folding、持久化与恢复。

三个数据域：

1. 上下文组装：system template、环境、Git context、`CLAUDE.md`、rules、Memory index、Skill descriptions、custom agents、deferred tool names、Plan Mode prompt、fold guidance、消息历史、Skill 摘要和异步 Memory 注入。
2. 上下文缩减：UTF-8 超过 30 KiB 的工具结果落盘并返回引用与前 200 行预览；每次模型调用前依次执行按利用率启用的单结果字符预算、stale-result snipping 和 idle microcompact；manual/tool/auto structured folding 是另一条替换原始消息历史的路径。stale-result snipping 在利用率至少 60% 时保留最近 3 条：OpenAI 处理全部符合条件的历史 `role=tool` messages，Anthropic 只处理来自 `read_file`、`grep_search`、`list_files`、`run_shell` 的 tool results。
3. 持久化与恢复：Session JSON 保存当前 backend messages 和 folded-memory 内存列表；每次 fold 另向项目 `.skevo/sessions/` 写入 JSONL/latest artifacts；长期 Memory Markdown 位于项目 hash 隔离的用户目录，并不由 folding 生成。

structured folding：manual 来自 REPL 在 `chat` 外直接调用的 `/compact` → `Agent.compact`；tool 来自模型工具执行中的 `compact_context` → `_compact_conversation(trigger="tool")`；auto 只在工具批次结束且上一次模型输入超过 effective window 的 70% 时检查。三种入口共用“对应 backend messages 至少 4 条且 transcript 非空”的 gate。成功 folding 会先记录 artifacts，再以 folded user message 替换原始历史；OpenAI 额外保留 system message。只有 tool folding 成功后会设置 `_context_cleared = True`，把该工具结果作为新的 user message，停止当前批次剩余工具并触发 context break；REPL `/compact` 不产生 tool result，也不进入 context-break 后果。

OpenAI/Anthropic messages 转为 transcript 时，普通 message content 按 12k chars clip，最终 transcript 按 80k chars clip；OpenAI `tool_call.arguments` 没有独立的 12k clip，只受最终总长限制。随后由 side query 生成 episode/working/tool memory；side query 不可用、调用失败或 JSON 解析失败时使用 fallback。

`--resume` 当前按 Session metadata 的 `startTime` 选择 latest Session JSON，并只把 `anthropicMessages` / `openaiMessages` 传给 `Agent.restore_session`。因此已写入消息历史的 folded user message 可以随当前 messages 恢复，但项目 folded-memory artifacts 不参与恢复，Session JSON 中的 `foldedSessionMemories` 列表也没有恢复；保存的 Session metadata（`id`、`model`、`cwd`、`startTime` 等）同样没有恢复，仍使用新建 Agent 的当前值。图中必须把这些实现缺口标为风险，不得画成完整恢复路径。

必须区分当前 messages、folded session memory、长期 Memory 和 Skill 的作用域。

权威锚点：`build_system_prompt`、`start_memory_prefetch`、`Agent._run_compression_pipeline`、`Agent.compact`、`Agent._execute_compact_context_tool`、`Agent._check_and_compact`、`Agent._compact_conversation`、`parse_folded_memory`、`fallback_folded_memory`、`save_session`、`save_folded_session_memory`、`Agent.restore_session`。

### 6.6 `06-skill-runtime.mmd`

图内标题：Skill 发现、检索、调用与执行
图型：`flowchart TD`
读者：访客与维护者
目的：区分 Skill 的发现、自动检索、显式调用和实际执行。

内容：

- 用户级 `~/.skevo/skills` 与项目级 `.skevo/skills`；项目同名 Skill 覆盖用户级。
- `SKILL.md` frontmatter 解析为 `SkillDefinition`，并进入发现缓存。
- 自动路径：用户请求经 tokenize/BM25 返回 top 3 摘要，注入 `<retrieved_skills>`，模型再决定是否调用。
- 显式路径：`/<skill-name> args` 通过 `get_skill_by_name` 调用。
- 共同路径：`execute_skill`、`resolve_skill_prompt`、invocation stats、`inline`/`fork`。
- `inline` 把完整 Prompt 返回当前 Agent Loop。
- `fork` 根据 `allowed_tools` 创建隔离 Agent，并将最终文本和 token 增量返回。
- 未知 Skill 和 fork 异常转换为明确错误文本。

排除：在线 add/merge/discard、replay、champion 和 MCP 初始化。

权威锚点：`discover_skills`、`retrieve_relevant_skills`、`format_retrieved_skill_context`、`execute_skill`、`Agent._execute_skill_tool`。

### 6.7 `07-skill-evolution.mmd`

图内标题：在线 Skill 演化闭环
图型：`flowchart TD`
读者：访客与维护者
目的：展示连续对话与用户反馈如何形成可复用 Skill 变更。

主路径：当前用户输入和回复形成 pending window；下一轮输入使上一窗口成熟；Extractor 最多提取一个 durable candidate；Manager 结合 identity、BM25 similarity、retrieved reference 和现有内容决策 add/merge/discard。

规则：exact match 强制 merge；高相似度 add 改为 merge；非法 action 降级为 discard。

写入门禁：Plan Mode 不调度后台演化；后台只在 `bypassPermissions`/`acceptEdits` 下自动允许；`/extract_now` 可交互确认。

所有 `none`、`discard`、`denied`、`failed`、`add`、`merge` 均记录 provenance。成功路径调用 `create_skill` 或 `evolve_skill`，并保留版本快照和生命周期统计。

权威锚点：`Agent._set_pending_skill_extraction_window`、`Agent._pop_pending_skill_extraction_window`、`extract_online_skill_candidate`、`maintain_online_skill_candidate`、`online_ingest`、`record_online_skill_provenance`。

### 6.8 `08-skill-evaluation.mmd`

图内标题：Skill 评测、候选比较与 Champion 晋升
图型：`flowchart LR`
读者：维护者及自进化机制研究者
目的：展示评测数据如何进入状态 gate 和 champion promotion gate。

输入：online provenance、provenance index、usage stats、lifecycle stats、active Skill snapshot。

流水线：稳定 lineage ID；构建并冻结 replay pool；划分 `mutate_dev` 和 `promotion_test`；编译确定性规则和可选 LLM judge；生成 heuristic/LLM variants；在 mutate-dev 上选择候选；在 promotion-test 上重新评估。

状态 gate：`unobserved`、`incubating`、`watch`、`healthy`、`pruned`。

Promotion gate：非 healthy 不晋升；首个健康候选可成为 champion；后续候选需要达到 `min_score_delta` 且不增加 hard failures；结果为 `active_champion` 或 `rejected`。

产物：frozen dataset、eval spec、run artifacts、report、champion registry、champion JSON 和独立 champion `SKILL.md`。Champion 不覆盖 active Skill。

权威锚点：`_build_replay_pool`、`_assign_replay_splits`、`_compile_eval_rules`、`_build_candidate_eval_bundle_async`、`_skill_status`、`_promotion_decision`、`_persist_eval_artifacts`、`_set_champion`。

### 6.9 `09-mcp-and-subagents.mmd`

图内标题：MCP 进程边界与子 Agent 上下文边界
图型：`flowchart LR`
读者：维护者
目的：解释 Runtime 如何跨越外部进程和隔离上下文边界。

MCP 侧：

- 配置覆盖顺序为用户级 settings、项目级 settings、项目 `.mcp.json`。
- 每个 server 经 stdio 子进程完成 initialize、initialized notification、tools/list 和 tools/call。
- 工具包装为 `mcp__server__tool`。
- 单 server 失败只关闭自身，不阻断其他 server 和主对话。
- 仅主 Agent 首次 `chat` 时懒加载 MCP。

子 Agent 侧：

- 入口为 `agent` tool 或 Skill fork。
- 内置类型为 `explore`、`plan`、`general`，另支持 custom agents。
- `explore`/`plan` 只获得读取工具；`general` 获得除 `agent` 外的工具；custom 和 Skill fork 可使用白名单。
- 子 Agent 拥有独立 system prompt、messages 和 Agent Loop；不执行主 Agent 的 Memory 注入、MCP 懒加载或在线演化。
- 子 Agent 不获得 `agent` 工具，阻止递归派生。
- 最终只返回文本和 token 增量；异常转换为错误文本。

必须标记的实现风险：子 Agent 可以继承主 Agent 的 MCP tool definitions，但新的 `McpManager` 不会在 `is_sub_agent=True` 时连接；因此继承 definition 不等于拥有可用 MCP connection。

权威锚点：`McpConnection`、`McpManager.load_and_connect`、`McpManager.get_tool_definitions`、`McpManager.call_tool`、`get_sub_agent_config`、`Agent._execute_agent_tool`、`Agent._execute_skill_tool`。

## 7. Mermaid 源码规范

### 7.1 文件骨架

Frontmatter 必须位于文件开头，维护注释放在 frontmatter 之后：

```mermaid
---
title: 中文图表标题
config:
  theme: base
  look: classic
---
%% Purpose: ...
%% Audience: ...
%% Sources: ...
%% Anchors: ...
%% Out of scope: ...

flowchart TD
```

时序图最后一行改为 `sequenceDiagram`。

### 7.2 色彩语义

统一使用高对比度样式，每个 `classDef` 必须包含 `fill`、`stroke`、`stroke-width` 和 `color`。

| 类别 | 语义 | 色系 |
| --- | --- | --- |
| `actor` | 用户与入口 | 浅黄/深棕 |
| `runtime` | Runtime 与核心编排 | 浅蓝/深蓝 |
| `model` | 模型与协议 | 浅青/深青 |
| `state` | 上下文、Memory、Session、存储 | 浅绿/深绿 |
| `control` | 权限、决策和门禁 | 浅橙/深棕 |
| `extension` | Skill、MCP、子 Agent | 浅紫/深紫 |
| `error` | 拒绝、失败和降级 | 浅红/深红 |
| `external` | 系统外部依赖 | 浅灰/深灰 |

### 7.3 连线语义

- `-->`：同步控制流或直接调用。
- `-.->`：异步、后台任务或非阻断注入。
- 数据持久化继续使用实线，并显式标注“读取”“写入”或“追加”。
- 时序图用 `->>` 表示调用、`-->>` 表示返回、`--)` 表示异步调度。

### 7.4 符号语义

Unicode 符号只用于增强扫描性，每个节点最多一个：

- `👤` 用户
- `⚙` Runtime/执行
- `🔐` 权限
- `💾` 持久化
- `★` Skill
- `🔌` MCP
- `◎` 子 Agent
- `❌` 拒绝或失败
- `⚠` 风险或降级

## 8. 文档集成

`docs/diagrams/README.md` 按三层组织：

- 快速理解：`01`、`02`
- Runtime 机制：`03`、`04`、`05`
- 能力与扩展：`06`、`07`、`08`、`09`

每个条目包含图的目的、主要读者、MMD/SVG/PNG 链接和权威代码模块。

根 README 只嵌入：

```text
docs/diagrams/svg/01-system-architecture.svg
```

Markdown 引用只能在对应 MMD 通过 Mermaid CLI 后更新。

## 9. 渲染与验证

### 9.1 渲染

- 使用当前环境中的 Mermaid CLI。
- SVG 使用白色背景。
- PNG 使用白色背景和 2 倍缩放。
- frontmatter 管理主题，不在命令行用另一主题覆盖。

### 9.2 自动验证

- 9 个 MMD 均非空。
- 每个 MMD 单独执行 `mmdc`，退出码为 0。
- 每个 SVG/PNG 存在且非空。
- MMD、SVG、PNG basename 集合完全一致。
- SVG 包含对应中文标题或关键节点文本。
- PNG 能被图像识别工具正常读取。
- 运行 `git diff --check` 检查空白错误。

### 9.3 视觉验证

逐张检查：

- 节点和子图不重叠。
- 中文文字不被裁剪。
- 边标签不覆盖节点或其他连线。
- 横向图宽度可接受。
- PNG 缩略图下仍能识别主流程。
- 颜色对比在白色背景下清晰。
- 风险注记不会被误解为正常路径。

## 10. 验收标准

1. 删除或重命名原有 8 个空 MMD，不保留失效占位文件。
2. 生成本设计规定的 9 个 MMD、9 个 SVG 和 9 个 PNG。
3. 三组文件 basename 严格一致。
4. 所有 MMD 通过 Mermaid CLI 验证。
5. 图中文字中文优先，技术标识保留英文。
6. 每张图遵守单一事实责任和节点预算。
7. 图中关键路径能追溯到当前 Python 实现。
8. Plan Mode 和 MCP/子 Agent 的实现风险得到显式标注。
9. `docs/diagrams/README.md` 与根 README 引用更新完成。
10. 不修改 Python 运行逻辑，不提交无关工作区改动。

## 11. 推荐阅读路径

- 项目访客：`01 → 02 → 06 → 07`
- Runtime 维护者：`01 → 02 → 03 → 04 → 05 → 09`
- 自进化机制研究者：`06 → 07 → 08`
- 完整维护者：按编号阅读 `01 → 09`
