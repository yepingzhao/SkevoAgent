# Terminal Output Boundaries Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ensure streamed assistant and Thinking text has one blank line before the next Rich structured terminal block whenever the stream has not already supplied that boundary, without duplicating an existing blank line.

**Architecture:** Keep terminal-boundary state entirely in `agents/ui.py`. `print_assistant_text()` records whether streamed assistant output is pending and how many newline characters terminate it; every block-level renderer passes through one preparation helper that writes only the missing newlines before delegating to Rich.

**Tech Stack:** Python 3.11+, Rich, standard-library `io` and `unittest`, uv-managed project environment.

---

## File Structure

- Modify `agents/ui.py`: track assistant-output suffix state and centralize structured-block preparation.
- Create `tests/test_ui.py`: reproduce streamed-text-to-panel adjacency through the real public UI functions using an in-memory Rich console.

### Task 1: Add terminal-boundary regression coverage and the UI-layer fix

**Files:**
- Modify: `agents/ui.py:20-341`
- Create: `tests/test_ui.py`

- [ ] **Step 1: Add the failing UI regression suite**

Create `tests/test_ui.py` with:

```python
"""Regression tests for streamed text and structured terminal boundaries."""

from __future__ import annotations

import io
import unittest

from rich.console import Console

from agents import ui


class TerminalOutputBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.output = io.StringIO()
        self.original_console = ui.console
        self.original_stdout_write = ui._safe_stdout_write
        self.had_pending_state = hasattr(ui, "_assistant_text_pending")
        self.had_newline_state = hasattr(ui, "_assistant_trailing_newlines")
        self.original_pending_state = getattr(ui, "_assistant_text_pending", False)
        self.original_newline_state = getattr(ui, "_assistant_trailing_newlines", 0)

        ui.console = Console(
            file=self.output,
            force_terminal=False,
            color_system=None,
            width=80,
        )
        ui._safe_stdout_write = lambda value: self.output.write(ui._safe_text(value))
        ui._assistant_text_pending = False
        ui._assistant_trailing_newlines = 0

    def tearDown(self) -> None:
        ui.console = self.original_console
        ui._safe_stdout_write = self.original_stdout_write

        if self.had_pending_state:
            ui._assistant_text_pending = self.original_pending_state
        else:
            delattr(ui, "_assistant_text_pending")

        if self.had_newline_state:
            ui._assistant_trailing_newlines = self.original_newline_state
        else:
            delattr(ui, "_assistant_trailing_newlines")

    def rendered(self) -> str:
        return self.output.getvalue()

    def test_thinking_has_one_blank_line_before_tool_call(self) -> None:
        ui.print_assistant_text("  [thinking] inspect")
        ui.print_tool_call("list_files", {"path": "*"})

        self.assertIn("[thinking] inspect\n\n╭", self.rendered())

    def test_one_trailing_newline_is_completed_before_panel(self) -> None:
        ui.print_assistant_text("answer\n")
        ui.print_cost(10, 5)

        self.assertTrue(self.rendered().startswith("answer\n\n╭"))

    def test_existing_blank_line_is_not_duplicated(self) -> None:
        ui.print_assistant_text("answer\n\n")
        ui.print_cost(10, 5)

        self.assertTrue(self.rendered().startswith("answer\n\n╭"))
        self.assertNotIn("answer\n\n\n╭", self.rendered())

    def test_final_markdown_has_one_blank_line_before_cost(self) -> None:
        ui.print_assistant_text("- Docker support")
        ui.print_cost(10, 5)

        self.assertIn("- Docker support\n\n╭", self.rendered())

    def test_consecutive_panels_do_not_gain_a_blank_line(self) -> None:
        ui.print_tool_call("list_files", {"path": "*"})
        ui.print_tool_result("list_files", "README.md")

        self.assertIn("╯\n╭", self.rendered())
        self.assertNotIn("╯\n\n╭", self.rendered())

    def test_empty_assistant_fragment_does_not_add_spacing(self) -> None:
        ui.print_assistant_text("")
        ui.print_cost(10, 5)

        self.assertTrue(self.rendered().startswith("╭"))


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the focused suite and verify the real defect is red**

Run:

```bash
.venv/bin/python -m unittest tests.test_ui -v
```

Expected: four adjacency/spacing tests fail because current output contains forms such as:

```text
[thinking] inspect╭
answer\n╭
- Docker support╭
```

The consecutive-panel and empty-fragment tests may already pass; the suite as a whole must fail before implementation.

- [ ] **Step 3: Add assistant-boundary state and preparation helpers**

In `agents/ui.py`, immediately after `_safe_stdout_write()`, add:

```python
_assistant_text_pending = False
_assistant_trailing_newlines = 0


def _record_assistant_text(text: str) -> None:
    global _assistant_text_pending, _assistant_trailing_newlines
    if not text:
        return
    _assistant_text_pending = True
    _assistant_trailing_newlines = min(2, len(text) - len(text.rstrip("\n")))


def _prepare_structured_output() -> None:
    global _assistant_text_pending, _assistant_trailing_newlines
    if not _assistant_text_pending:
        return
    missing_newlines = max(0, 2 - _assistant_trailing_newlines)
    if missing_newlines:
        _safe_stdout_write("\n" * missing_newlines)
    _assistant_text_pending = False
    _assistant_trailing_newlines = 0


def _print_structured(renderable: object) -> None:
    _prepare_structured_output()
    console.print(renderable)
```

This state records only assistant fragments; do not update it inside `_safe_stdout_write()`, because that writer is also used by the spinner and ANSI clear-line sequences.

- [ ] **Step 4: Record streamed assistant fragments**

Replace `print_assistant_text()` with:

```python
def print_assistant_text(text: str) -> None:
    text = _safe_text(text)
    _safe_stdout_write(text)
    _record_assistant_text(text)
```

The write stays immediate, so streaming behavior does not change. Empty fragments remain inert.

- [ ] **Step 5: Route every block-level panel through the structured printer**

Within these functions, replace the outer `console.print(Panel(...))` call with `_print_structured(Panel(...))` while preserving the complete existing `Panel` content and styling:

```text
print_tool_call
print_tool_result
_print_file_change_result
print_error
print_confirmation
print_cost
print_info
print_warning
print_goodbye
print_plan_for_approval
print_plan_approval_options
print_sub_agent_start
print_sub_agent_end
print_memory_entries
print_skill_entries
```

For example, `print_tool_call()` becomes:

```python
def print_tool_call(name: str, inp: dict) -> None:
    icon = _get_tool_icon(name)
    summary = _get_tool_summary(name, inp)
    table = Table.grid(padding=(0, 1))
    table.add_column(style="bold yellow", no_wrap=True)
    table.add_column(style="white")
    table.add_row("tool", f"{icon} {name}")
    if summary:
        table.add_row("input", _safe_text(summary))
    _print_structured(Panel(
        table,
        title="[bold yellow]Tool Call[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED,
        padding=(0, 1),
    ))
```

For one-line panel calls such as plan options, memories, and skills, preserve the panel unchanged and replace only the outer function name:

```python
_print_structured(Panel(table, title="...", border_style="...", box=box.ROUNDED))
```

Do not route the diff-detail `console.print(...)` calls inside `_print_file_change_result()` through `_print_structured()`: the file-change panel has already consumed the pending assistant boundary.

- [ ] **Step 6: Cover non-panel structured boundaries**

Replace `print_divider()` with:

```python
def print_divider() -> None:
    _prepare_structured_output()
    console.rule("[dim]turn complete[/dim]", style="dim")
```

Replace `print_retry()` with:

```python
def print_retry(attempt: int, max_retries: int, reason: str) -> None:
    _prepare_structured_output()
    console.print(_safe_text(f"  [yellow]↻ Retry {attempt}/{max_retries}: {reason}[/yellow]"))
```

Removing the retry string's unconditional leading newline prevents it from creating two empty lines after boundary preparation. A retry with no pending assistant text now starts at the current structured line boundary rather than manufacturing an unrelated blank line.

- [ ] **Step 7: Run focused tests and confirm the boundary behavior is green**

Run:

```bash
.venv/bin/python -m unittest tests.test_ui -v
```

Expected: all six tests pass.

- [ ] **Step 8: Rerun the original minimal reproduction**

Run:

```bash
.venv/bin/python -c 'import io; from rich.console import Console; import agents.ui as ui; buffer = io.StringIO(); ui.console = Console(file=buffer, force_terminal=False, color_system=None, width=80); ui._safe_stdout_write = lambda text: buffer.write(str(text)); ui._assistant_text_pending = False; ui._assistant_trailing_newlines = 0; ui.print_assistant_text("  [thinking] inspect"); ui.print_tool_call("list_files", {"path": "*"}); ui.print_assistant_text("- Docker support"); ui.print_cost(10, 5); output = buffer.getvalue(); print(repr(output)); assert "[thinking] inspect\n\n╭" in output; assert "- Docker support\n\n╭" in output'
```

Expected: exit 0; both original adjacency points now contain exactly one empty line.

- [ ] **Step 9: Run the complete regression suite**

Run:

```bash
env PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m unittest discover -s tests -p "test_*.py" -v
```

Expected: all 13 tests pass: two CLI tests, five VS Code configuration tests, and six UI boundary tests.

- [ ] **Step 10: Commit the regression-tested fix**

```bash
git add agents/ui.py tests/test_ui.py
git commit -m "fix(ui): separate streamed text from panels"
```

### Task 2: Verify scope and repository integrity

**Files:**
- Verify: `agents/ui.py`
- Verify: `tests/test_ui.py`
- Verify: `uv.lock`

- [ ] **Step 1: Validate whitespace and the exact implementation scope**

Run:

```bash
git diff --check HEAD^..HEAD
git diff --name-status HEAD^..HEAD
```

Expected:

```text
M agents/ui.py
A tests/test_ui.py
```

No other implementation file may appear.

- [ ] **Step 2: Confirm the project lock file is untouched**

Run:

```bash
git hash-object uv.lock
git rev-parse HEAD:uv.lock
```

Expected: both commands print the same blob hash. Do not run plain `uv run`, `uv sync`, or `uv lock`; UI tests use the already synchronized `.venv` directly.

- [ ] **Step 3: Confirm the worktree is clean and preserve unrelated user changes**

Run:

```bash
git status --short --branch
git log --oneline -4
```

Expected in the isolated implementation worktree:

- the feature branch is clean;
- the latest subject is `fix(ui): separate streamed text from panels`;
- the main worktree's pre-existing `.idea` and documentation deletions and untracked `.DS_Store` were never copied into, staged by, or committed from the feature branch.
