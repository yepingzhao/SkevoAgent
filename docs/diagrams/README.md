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
