# Thinking-to-Answer Boundary Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Insert exactly the missing part of one blank line when an Anthropic-compatible stream transitions from visible Thinking content to final answer text.

**Architecture:** Keep protocol semantics inside `Agent._call_anthropic_stream()` by replacing the shared first-text flag with per-stream output-phase and Thinking-suffix state. Emit the separator through `_emit_text()` so terminal, `run_once()`, and sub-agent buffers receive identical formatting while the existing UI panel boundary remains unchanged.

**Tech Stack:** Python 3.11+, standard-library `unittest` and `unittest.mock`, Anthropic-compatible async stream events, existing uv-managed virtual environment.

---

## File Structure

- Modify `agents/agent.py`: classify the visible stream phase, track the complete Thinking newline suffix, and emit only the missing Thinking-to-answer boundary.
- Create `tests/test_agent_stream_output.py`: replay deterministic fake Anthropic events through the real `_call_anthropic_stream()` method.

No UI, OpenAI-compatible stream, dependency, lock, documentation, or configuration file changes are part of implementation.

## Execution Prerequisites

Implement in an isolated project-local worktree created from the main commit containing this plan. Recommended branch and path:

```text
branch: fix/thinking-answer-boundary
path:   .worktrees/thinking-answer-boundary
```

Before setup, verify `.worktrees/` is ignored. If the isolated worktree has no `.venv`, synchronize only from the committed lock file and canonical index:

```bash
env -u UV_INDEX -u UV_INDEX_URL -u UV_EXTRA_INDEX_URL \
  UV_DEFAULT_INDEX=https://pypi.org/simple/ \
  UV_CACHE_DIR=/tmp/bearcode-thinking-answer-cache \
  UV_LINK_MODE=copy \
  uv sync --locked --no-progress
```

Run the clean baseline:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected before this plan is implemented: 15 tests pass. Do not proceed on a failing baseline without reporting it. Do not run plain `uv run`, `uv sync`, `uv lock`, or another command that can rewrite `uv.lock` using inherited mirror settings.

### Task 1: Add stream-transition regression tests and the protocol-layer fix

**Files:**
- Create: `tests/test_agent_stream_output.py`
- Modify: `agents/agent.py:1405-1441`

- [ ] **Step 1: Create the fake Anthropic stream test harness**

Create `tests/test_agent_stream_output.py` with the complete content below:

```python
"""Regression tests for Anthropic Thinking-to-answer stream boundaries."""

from __future__ import annotations

from types import SimpleNamespace
import unittest
from unittest.mock import patch

from agents.agent import Agent


class FakeAnthropicStream:
    def __init__(self, events: list[SimpleNamespace]) -> None:
        self.events = list(events)
        self.final_message = SimpleNamespace(content=[])

    async def __aenter__(self) -> "FakeAnthropicStream":
        return self

    async def __aexit__(
        self,
        _exc_type: object,
        _exc_value: object,
        _traceback: object,
    ) -> None:
        return None

    def __aiter__(self) -> "FakeAnthropicStream":
        return self

    async def __anext__(self) -> SimpleNamespace:
        if not self.events:
            raise StopAsyncIteration
        return self.events.pop(0)

    async def get_final_message(self) -> SimpleNamespace:
        return self.final_message


class FakeAnthropicMessages:
    def __init__(self, events: list[SimpleNamespace]) -> None:
        self.events = events
        self.create_params: dict[str, object] | None = None

    def stream(self, **create_params: object) -> FakeAnthropicStream:
        self.create_params = create_params
        return FakeAnthropicStream(self.events)


def thinking_delta(text: str, index: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        type="content_block_delta",
        index=index,
        delta=SimpleNamespace(thinking=text),
    )


def text_delta(text: str, index: int = 1) -> SimpleNamespace:
    return SimpleNamespace(
        type="content_block_delta",
        index=index,
        delta=SimpleNamespace(text=text),
    )


def tool_start(index: int = 1) -> SimpleNamespace:
    return SimpleNamespace(
        type="content_block_start",
        index=index,
        content_block=SimpleNamespace(
            type="tool_use",
            id="tool-1",
            name="list_files",
        ),
    )


def block_stop(index: int = 1) -> SimpleNamespace:
    return SimpleNamespace(type="content_block_stop", index=index)


class AnthropicStreamOutputTests(unittest.IsolatedAsyncioTestCase):
    async def render_events(self, events: list[SimpleNamespace]) -> tuple[str, list[str]]:
        agent = Agent.__new__(Agent)
        agent.model = "claude-sonnet-4-6"
        agent._thinking_mode = "enabled"
        agent._system_prompt = ""
        agent.tools = []
        agent._anthropic_messages = []
        agent._anthropic_client = SimpleNamespace(
            messages=FakeAnthropicMessages(events),
        )

        fragments: list[str] = []
        agent._emit_text = fragments.append

        with patch("agents.agent.stop_spinner") as stop_spinner:
            await agent._call_anthropic_stream()

        stop_spinner.assert_called_once_with()
        return "".join(fragments), fragments

    async def test_thinking_and_answer_have_one_blank_line(self) -> None:
        output, _fragments = await self.render_events(
            [thinking_delta("reasoning"), text_delta("answer")]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")

    async def test_one_thinking_newline_is_completed_before_answer(self) -> None:
        output, _fragments = await self.render_events(
            [thinking_delta("reasoning\n"), text_delta("answer")]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")

    async def test_existing_thinking_blank_line_is_not_duplicated(self) -> None:
        output, _fragments = await self.render_events(
            [thinking_delta("reasoning\n\n"), text_delta("answer")]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")
        self.assertNotIn("reasoning\n\n\nanswer", output)

    async def test_thinking_blank_line_split_across_deltas_is_not_duplicated(self) -> None:
        output, _fragments = await self.render_events(
            [
                thinking_delta("reasoning\n"),
                thinking_delta("\n"),
                text_delta("answer"),
            ]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")
        self.assertNotIn("reasoning\n\n\nanswer", output)

    async def test_text_only_stream_preserves_existing_leading_newline(self) -> None:
        output, fragments = await self.render_events([text_delta("answer", index=0)])

        self.assertEqual(output, "\nanswer")
        self.assertEqual(fragments, ["\n", "answer"])
        self.assertNotIn("[thinking]", output)

    async def test_thinking_before_tool_does_not_add_answer_separator(self) -> None:
        output, fragments = await self.render_events(
            [thinking_delta("reasoning"), tool_start(), block_stop()]
        )

        self.assertEqual(output, "\n  [thinking] reasoning")
        self.assertEqual(fragments, ["\n  [thinking] ", "reasoning"])


if __name__ == "__main__":
    unittest.main()
```

The fake client exercises the real event-classification loop, `_emit_text()` call ordering, spinner stop boundary, and final-message Thinking filter without a network call.

- [ ] **Step 2: Run the focused suite and verify the current defect is red**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest tests.test_agent_stream_output -v
```

Expected: six tests run and the suite fails with exactly two boundary failures:

```text
test_thinking_and_answer_have_one_blank_line ... FAIL
test_one_thinking_newline_is_completed_before_answer ... FAIL
```

The first failure must show the current adjacency:

```text
'\n  [thinking] reasoninganswer'
```

The second failure must show only one newline before `answer`. The other four cases already match current behavior and should pass. Do not modify production code until these failures are observed for the expected reason.

- [ ] **Step 3: Replace the shared first-text flag with local stream-phase state**

In `Agent._call_anthropic_stream()` inside `_do()`, replace:

```python
first_text = True
```

with:

```python
output_phase = "none"
thinking_trailing_newlines = 0

def record_thinking_suffix(text: str) -> None:
    nonlocal thinking_trailing_newlines
    if not text:
        return
    trailing_newlines = len(text) - len(text.rstrip("\n"))
    if trailing_newlines == len(text):
        thinking_trailing_newlines = min(
            2,
            thinking_trailing_newlines + trailing_newlines,
        )
    else:
        thinking_trailing_newlines = min(2, trailing_newlines)
```

This state is local to one stream attempt. Do not reuse the module-level UI suffix state and do not add Agent instance fields that can leak across turns or retry attempts.

- [ ] **Step 4: Implement the Thinking-to-answer transition**

Within the `content_block_delta` branch, replace the existing `text` and `thinking` cases with:

```python
if hasattr(delta, "text"):
    text = _safe_utf8_text(delta.text)
    if output_phase == "none":
        stop_spinner()
        self._emit_text("\n")
    elif output_phase == "thinking":
        missing_newlines = max(0, 2 - thinking_trailing_newlines)
        if missing_newlines:
            self._emit_text("\n" * missing_newlines)
    output_phase = "text"
    self._emit_text(text)
elif hasattr(delta, "thinking"):
    thinking_text = _safe_utf8_text(delta.thinking)
    if output_phase == "none":
        stop_spinner()
        self._emit_text("\n  [thinking] ")
        output_phase = "thinking"
    if output_phase == "thinking":
        record_thinking_suffix(thinking_text)
    self._emit_text(thinking_text)
```

Keep the existing `partial_json` branch immediately after these cases unchanged.

This preserves the current behavior for an unexpected Thinking delta after final text: it is emitted as received but does not reset the standard `text` phase or manufacture another answer boundary. The Anthropic protocol's supported order remains Thinking before text.

- [ ] **Step 5: Run the focused suite and verify all transition cases are green**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest tests.test_agent_stream_output -v
```

Expected: all six tests pass.

- [ ] **Step 6: Rerun the original minimal fake-stream reproduction**

Run:

```bash
.venv/bin/python -c 'import asyncio; from types import SimpleNamespace as NS; from unittest.mock import patch; from agents.agent import Agent; from tests.test_agent_stream_output import FakeAnthropicMessages, thinking_delta, text_delta; agent = Agent.__new__(Agent); agent.model = "claude-sonnet-4-6"; agent._thinking_mode = "enabled"; agent._system_prompt = ""; agent.tools = []; agent._anthropic_messages = []; agent._anthropic_client = NS(messages=FakeAnthropicMessages([thinking_delta("reasoning"), text_delta("answer")])); fragments = []; agent._emit_text = fragments.append; stopper = patch("agents.agent.stop_spinner"); stopper.start(); asyncio.run(agent._call_anthropic_stream()); stopper.stop(); output = "".join(fragments); print(repr(output)); assert output == "\n  [thinking] reasoning\n\nanswer"'
```

Expected: exit 0 and output equivalent to:

```text
'\n  [thinking] reasoning\n\nanswer'
```

- [ ] **Step 7: Run the complete regression suite**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all 21 tests pass: two CLI tests, five VS Code configuration tests, eight terminal UI tests, and six Anthropic stream-output tests.

- [ ] **Step 8: Verify implementation scope and lock integrity**

Run:

```bash
git diff --check
git diff --name-status
git hash-object uv.lock
git rev-parse HEAD:uv.lock
```

Expected changed-file scope before commit:

```text
M agents/agent.py
A tests/test_agent_stream_output.py
```

Both `uv.lock` commands must print the same blob hash:

```text
b5085d309bc4a4a9e1e3847dafe70865c4788b25
```

- [ ] **Step 9: Commit the regression-tested fix**

Stage only the two implementation files and commit with the exact English message:

```bash
git add agents/agent.py tests/test_agent_stream_output.py
git commit -m "fix(agent): separate thinking from final answer"
```

### Task 2: Verify the committed result and repository integrity

**Files:**
- Verify: `agents/agent.py`
- Verify: `tests/test_agent_stream_output.py`
- Verify: `uv.lock`

- [ ] **Step 1: Verify committed whitespace and exact file scope**

Run:

```bash
git diff --check HEAD^..HEAD
git diff --name-status HEAD^..HEAD
```

Expected:

```text
M agents/agent.py
A tests/test_agent_stream_output.py
```

No UI, OpenAI stream, dependency, documentation, configuration, or lock file may appear in the implementation commit.

- [ ] **Step 2: Re-run focused and full tests from the committed state**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest tests.test_agent_stream_output -v
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: focused suite passes 6/6 and complete suite passes 21/21.

- [ ] **Step 3: Confirm lock, branch, and worktree integrity**

Run:

```bash
git hash-object uv.lock
git rev-parse HEAD:uv.lock
git status --short --branch
git log --oneline -4
```

Expected in the isolated implementation worktree:

- both lock hashes are `b5085d309bc4a4a9e1e3847dafe70865c4788b25`;
- the feature worktree is clean;
- the latest subject is `fix(agent): separate thinking from final answer`;
- the main worktree's pre-existing `.idea` and documentation deletions and untracked `.DS_Store` were never staged, committed, restored, deleted, or copied into the feature branch.
