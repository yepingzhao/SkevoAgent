# Terminal Output Boundaries Design

## Context

BearCode renders two kinds of terminal output through different mechanisms. Model text and Thinking deltas stream through `sys.stdout.write()` without an automatic line ending, while Tool Call, Tool Result, Cost, Info, Error, and other structured blocks render through Rich's `Console.print()`. Rich cannot infer that a preceding raw write left the cursor in the middle of a line.

This produces visible boundary defects when the model's final streamed chunk has no trailing newline:

```text
[thinking] Let me inspect the project.╭─ Tool Call ─╮
```

and:

```text
- Docker support╭─ Cost ─╮
```

A deterministic in-memory terminal reproduction confirms both failures without starting a model, MCP server, spinner, or interactive terminal. Routing the streamed text through Rich with `end=""` does not fix the defect. Explicitly closing an unfinished assistant line before structured output fixes both reproductions.

## Goals

- Keep exactly one blank line between streamed assistant text and the next structured terminal block.
- Apply the same boundary rule to normal model text and Thinking text.
- Cover both Anthropic and OpenAI execution paths without duplicating protocol-specific formatting logic.
- Avoid inserting additional blank lines when the model already emitted the required spacing.
- Keep consecutive structured blocks compact.
- Add a deterministic, network-free regression suite at the real UI rendering seam.

## Non-goals

- Changing model prompts, Thinking content, tool execution, permissions, MCP behavior, or Agent Loop semantics.
- Changing Rich panel colors, borders, titles, widths, padding, or Cost calculations.
- Buffering complete model responses before display.
- Replacing Rich or routing all streamed text through Rich.
- Normalizing whitespace inside model-generated Markdown.
- Changing spinner behavior or ANSI control sequences.
- Committing, reverting, or otherwise altering the unrelated deletions and `.DS_Store` already present in the main worktree.

## Root Cause

`print_assistant_text()` delegates to `_safe_stdout_write()`, which writes a fragment exactly as received and flushes immediately. Structured renderers call `console.print()` or `console.rule()`. Neither layer records whether the last assistant fragment ended at a line boundary.

The defect is not specific to Tool Call or Cost panels. Any structured renderer can follow streamed text, so repairing only the two observed call sites would leave the same failure possible for Tool Result, Info, Warning, Error, Confirmation, Divider, plan approval, memory, skill, and sub-agent displays.

The spinner is not the cause: the minimal reproduction does not start a spinner and still reproduces both adjacency failures. Using `Console.print(..., end="")` for streamed text also reproduces the defect, so merely unifying the output object is insufficient.

## Boundary State

Keep the formatting responsibility inside `agents/ui.py`. Track two internal values:

- whether assistant text has been emitted since the previous structured-output boundary;
- how many newline characters terminate the current assistant stream, capped at two.

`print_assistant_text()` writes the fragment immediately, then updates those values from the fragment's suffix. Empty fragments do not change the state. A later non-newline fragment resets the trailing-newline count to zero even if an earlier fragment ended with a newline.

The state is intentionally about assistant text only. Spinner writes continue through `_safe_stdout_write()` without changing assistant-boundary state, so carriage-return and clear-line control sequences cannot be mistaken for model content.

## Structured Output Preparation

Add one internal helper that prepares the terminal for a structured block:

1. If no assistant text has been emitted since the last boundary, do nothing.
2. If the assistant text ends with no newline, write two newline characters.
3. If it ends with one newline, write one additional newline character.
4. If it ends with two or more newline characters, write nothing.
5. Mark the assistant text as consumed by the structured boundary.

This yields exactly one empty line between streamed content and the next block:

```text
[thinking] Let me inspect the project.

╭─ Tool Call ─╮
```

```text
- Docker support

╭─ Cost ─╮
```

After preparation, a second structured renderer sees no pending assistant text and adds no spacing. Consecutive panels therefore remain compact:

```text
╭─ Tool Call ─╮
╰─────────────╯
╭─ result ────╮
╰─────────────╯
```

## Renderer Coverage

Every block-level UI function that can follow assistant output must prepare the structured boundary before rendering. This includes:

- Tool Call and Tool Result panels;
- file-change panels;
- Cost panels and turn-complete dividers;
- Info, Warning, Error, Confirmation, Goodbye, and plan-approval panels;
- sub-agent, memory, and skill panels.

The implementation should centralize preparation through the smallest practical helper rather than duplicating newline arithmetic at every call site. Plain lines rendered after an already-prepared file-change panel do not need to prepare the boundary again.

`print_user_prompt()` may also prepare a pending assistant boundary defensively, but it must retain its existing prompt-leading newline and `end=""` behavior.

## Buffered and Sub-agent Output

When `Agent._emit_text()` is collecting a `run_once()` result in `_output_buffer`, it does not call `print_assistant_text()`. Therefore buffered output does not alter terminal-boundary state and does not receive terminal-only whitespace.

Sub-agent output remains governed by its existing visibility rules. If streamed text is rendered through the shared UI, it receives the same block separation; if it is buffered, it remains unchanged.

## Error and Interruption Behavior

Boundary preparation is formatting-only and must never swallow or rewrite model text. It writes only the missing newline characters before a structured block.

If a stream is interrupted after emitting partial text, the next Warning, Error, Divider, or user prompt must begin after the same one-blank-line boundary. No exception handling or retry behavior changes are required.

## Regression Tests

Add `tests/test_ui.py` using `unittest`, `io.StringIO`, and a Rich `Console` configured to write to memory. Patch the module-level console and raw writer only within each test, then restore them so tests do not leak global UI state.

The regression suite must verify:

1. Thinking text with no trailing newline is followed by exactly two newline characters before a Tool Call panel.
2. Assistant text with one trailing newline receives exactly one additional newline before a structured panel.
3. Assistant text with two trailing newlines receives no additional newline.
4. Final Markdown text is separated from the Cost panel by one empty line.
5. Consecutive structured panels receive no artificial blank line between them.
6. Empty assistant fragments do not create spacing.

The tests must exercise the actual public UI rendering functions rather than a detached newline utility. This preserves the real failure pattern: streamed raw output followed by Rich block output.

## Verification

Implementation verification will include:

```bash
.venv/bin/python -m unittest tests.test_ui -v
.venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Also rerun the original in-memory reproduction and confirm these substrings are present:

```text
[thinking] inspect\n\n╭
- Docker support\n\n╭
```

Inspect the complete diff to confirm it changes only `agents/ui.py`, `tests/test_ui.py`, and approved design/plan documentation. Existing unrelated worktree changes must remain unstaged and untouched.

## Acceptance Criteria

1. Tool Call, Cost, and every other structured UI block starts on a new block after exactly one empty line when preceded by streamed assistant text.
2. Text that already ends with one blank line is not given additional vertical spacing.
3. Consecutive structured blocks remain adjacent without an inserted blank line.
4. Thinking and normal assistant text use the same boundary behavior.
5. Buffered `run_once()` text remains free of terminal-only added whitespace.
6. The deterministic UI regression suite and the complete repository test suite pass without credentials or network access.
7. No application behavior outside terminal block separation changes.
