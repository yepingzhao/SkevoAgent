# Thinking-to-Answer Boundary Design

**Date:** 2026-08-04

**Status:** Approved for implementation planning

## Problem

Bear Code can stream Anthropic-compatible Thinking content and final answer text in the same response. The current handler uses one `first_text` flag for both delta types. The first Thinking delta clears that flag, so the first final-text delta no longer creates its own output boundary.

For an event sequence equivalent to:

```text
thinking("reasoning")
text("answer")
```

the current emitted fragments are:

```python
["\n  [thinking] ", "reasoning", "answer"]
```

and the rendered result is:

```text
  [thinking] reasoninganswer
```

The existing UI boundary state correctly separates streamed assistant output from later Rich panels, but it cannot distinguish Thinking content from final answer content inside a single assistant stream.

## Desired Behavior

Keep Thinking visible and insert one blank line before final answer text:

```text
  [thinking] reasoning

answer
```

One blank line means two newline characters between the final non-newline Thinking character and the first answer character.

The transition must add only the missing newline characters:

| Thinking suffix before answer | Separator added | Result before answer |
| --- | --- | --- |
| no newline | `\n\n` | exactly one blank line |
| one newline | `\n` | exactly one blank line |
| two or more newlines | nothing | preserve existing spacing |

Already-rendered extra newlines cannot be retracted. The implementation therefore guarantees that the transition supplies at least one blank line without duplicating a blank line that Thinking already supplied.

## Goals

- Separate visible Thinking from final answer text in Anthropic-compatible streams.
- Preserve exactly the missing part of a one-blank-line boundary.
- Handle newline suffixes split across multiple Thinking delta fragments.
- Keep interactive output, `run_once()` output, and sub-agent buffered output consistent.
- Preserve text-only responses, spinner behavior, structured-panel spacing, and tool rendering.
- Add a deterministic regression suite at the real Anthropic stream-event seam.

## Non-Goals

- Hiding Thinking or changing the `[thinking]` label.
- Rendering Thinking inside a Rich panel.
- Changing OpenAI-compatible streaming, which currently has no separately rendered Thinking delta path.
- Changing Cost, Tool Call, Tool Result, divider, retry, or spinner presentation.
- Changing persisted conversation history or the existing removal of Anthropic Thinking blocks from final history.
- Refactoring unrelated Agent streaming or UI code.

## Considered Approaches

### 1. Track the Thinking-to-text transition in the Anthropic stream handler

The handler already knows whether each delta carries `thinking` or `text`. It can track the current output phase and the trailing-newline suffix of Thinking, then emit only the missing boundary when the first final-text delta arrives.

This approach applies the rule at the layer with complete protocol information and sends the separator through `_emit_text()`, so terminal and buffered consumers behave identically.

**Decision:** Use this approach.

### 2. Add a Thinking-specific terminal UI API

The UI could expose separate Thinking and answer writers and insert a boundary when the writer type changes.

This would make the generic terminal UI depend on Anthropic stream semantics. It would also fail to cover `run_once()` and sub-agent buffering without duplicating equivalent state in `Agent`.

**Decision:** Reject.

### 3. Emit a fixed separator at Thinking `content_block_stop`

The handler could always emit two newlines when a Thinking block stops.

This depends on a specific stop-event sequence, can duplicate newlines already supplied by Thinking, and creates spacing even when the next block is a tool call rather than final answer text.

**Decision:** Reject.

## Architecture

The change stays inside the Anthropic-compatible stream-processing path in `agents/agent.py`.

The stream handler maintains per-call, local state:

- an output phase indicating whether no visible output, Thinking, or final text has been emitted;
- a Thinking trailing-newline count capped at two.

No module-level or cross-turn state is added. Every stream call starts with a fresh phase and suffix count.

All visible text and inserted separators continue through `Agent._emit_text()`. This preserves the existing fan-out behavior:

```text
Anthropic delta classification
        |
        v
Thinking/text transition state
        |
        v
Agent._emit_text()
        |
        +--> terminal: print_assistant_text()
        |
        +--> run_once(): _output_buffer
        |
        +--> turn/sub-agent output buffers
```

The UI-layer structured-output boundary remains responsible only for the later streamed-text-to-panel transition.

## State Transitions

### First Thinking delta

When Thinking is the first visible content:

1. Stop the spinner using the existing call.
2. Emit the existing `"\n  [thinking] "` prefix.
3. Set the phase to Thinking.
4. Emit the Thinking fragment.
5. Update the Thinking trailing-newline suffix.

### Additional Thinking deltas

Emit each fragment unchanged and update the suffix of the complete Thinking stream:

- if the fragment contains only newline characters, add its count to the existing suffix and cap at two;
- otherwise replace the suffix with that fragment's own trailing-newline count, capped at two;
- an empty fragment does not change the suffix.

This is the same suffix model already proven by the UI boundary tests, but it remains local to the Anthropic stream call rather than sharing UI state.

### First final-text delta after Thinking

Before emitting the first final-text fragment:

1. Compute `max(0, 2 - thinking_trailing_newlines)`.
2. Emit that many newline characters through `_emit_text()`.
3. Change the phase to final text.
4. Emit the final-text fragment unchanged.

Later final-text fragments stream without additional boundaries.

### Text-only response

When final text is the first visible content, preserve current behavior:

1. Stop the spinner.
2. Emit the existing single leading newline.
3. Set the phase to final text.
4. Emit the fragment.

### Thinking followed by a tool block

Do not emit a Thinking-to-answer separator unless a final-text delta actually arrives. If the stream moves directly from Thinking to a tool call, the existing structured-output preparation adds only the spacing needed before the Tool Call panel.

## Buffering and History

The boundary is emitted with `_emit_text()` rather than written directly to stdout. Consequently:

- interactive terminal output receives the separator and records its trailing suffix in the UI layer;
- `run_once()` returns Thinking and answer with the same separation;
- turn and sub-agent buffers receive the same formatting;
- no protocol-specific terminal function is required.

The existing final-message filtering remains unchanged:

```python
final_message.content = [b for b in final_message.content if b.type != "thinking"]
```

The display separator affects rendered/buffered output only and does not reinsert Thinking into persisted Anthropic history.

## Testing Strategy

Create a deterministic standard-library `unittest` suite at the real `Agent._call_anthropic_stream()` seam. Use a fake Anthropic async stream that yields controlled `content_block_delta` events and a minimal final message. Patch only spinner output as needed; capture `_emit_text()` fragments directly.

Required regression cases:

1. Thinking with no trailing newline followed by text produces `thinking\n\nanswer`.
2. Thinking with one trailing newline followed by text adds only one newline.
3. Thinking with two trailing newlines followed by text adds none.
4. Two newline characters split across separate Thinking deltas are accumulated and not duplicated.
5. A text-only stream preserves its existing single leading newline and contains no `[thinking]` label.
6. Thinking followed by a tool block does not manufacture an answer separator before a final-text delta.

The first case must be observed failing against the current implementation with the exact `reasoninganswer` adjacency before production code changes.

After the focused suite passes, rerun:

- the original fake-stream reproduction;
- the complete repository `unittest` discovery suite;
- whitespace, changed-file scope, worktree, and `uv.lock` integrity checks.

## File Scope

Expected implementation files:

- Modify `agents/agent.py` for per-stream phase and Thinking suffix handling.
- Create `tests/test_agent_stream_output.py` for fake Anthropic stream regression coverage.

This design document is the only file changed during the design phase.

## Acceptance Criteria

- The demonstrated greeting scenario renders one blank line between `[thinking] ...` and `你好！...`.
- Thinking ending in zero, one, or at least two newline characters receives only the missing separator characters.
- Newline-only Thinking fragments accumulate correctly across delta boundaries.
- Text-only Anthropic output is unchanged.
- Thinking followed directly by a tool call does not receive an answer-only separator.
- Interactive, `run_once()`, and sub-agent buffer consumers receive the same boundary because it flows through `_emit_text()`.
- Existing UI panel boundaries, spinner synchronization, retry formatting, and OpenAI-compatible streaming remain unchanged.
- Focused and full regression suites pass.
- Only the approved implementation files change, and `uv.lock` remains byte-for-byte unchanged.
