"""Tests for visible output emitted by the Anthropic streaming event seam."""

import unittest
from types import SimpleNamespace
from unittest.mock import patch

from agents.agent import Agent


class FakeAnthropicStream:
    def __init__(self, events):
        self.events = list(events)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        return False

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.events:
            raise StopAsyncIteration
        return self.events.pop(0)

    async def get_final_message(self):
        return SimpleNamespace(content=[])


class FakeAnthropicMessages:
    def __init__(self, events):
        self.events = list(events)
        self.create_params = []

    def stream(self, **create_params):
        self.create_params.append(create_params)
        return FakeAnthropicStream(self.events)


def thinking_delta(text, index=0):
    return SimpleNamespace(
        type="content_block_delta",
        index=index,
        delta=SimpleNamespace(thinking=text),
    )


def text_delta(text, index=1):
    return SimpleNamespace(
        type="content_block_delta",
        index=index,
        delta=SimpleNamespace(text=text),
    )


def tool_start(index=1):
    return SimpleNamespace(
        type="content_block_start",
        index=index,
        content_block=SimpleNamespace(
            type="tool_use",
            id="tool-1",
            name="list_files",
        ),
    )


def block_stop(index=1):
    return SimpleNamespace(type="content_block_stop", index=index)


class AgentAnthropicStreamOutputTest(unittest.IsolatedAsyncioTestCase):
    async def emit_events(self, events):
        agent = Agent.__new__(Agent)
        agent.model = "claude-sonnet-4-6"
        agent._thinking_mode = "enabled"
        agent._system_prompt = ""
        agent.tools = []
        agent._anthropic_messages = []
        agent._anthropic_client = SimpleNamespace(
            messages=FakeAnthropicMessages(events)
        )
        fragments = []
        agent._emit_text = fragments.append

        with patch("agents.agent.stop_spinner") as stop_spinner:
            await agent._call_anthropic_stream()

        stop_spinner.assert_called_once_with()
        return "".join(fragments), fragments

    async def test_thinking_without_newline_gets_one_blank_line_before_answer(self):
        output, _ = await self.emit_events(
            [thinking_delta("reasoning"), text_delta("answer")]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")

    async def test_thinking_with_one_newline_gets_one_blank_line_before_answer(self):
        output, _ = await self.emit_events(
            [thinking_delta("reasoning\n"), text_delta("answer")]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")

    async def test_thinking_with_two_newlines_gets_no_third_newline_before_answer(self):
        output, _ = await self.emit_events(
            [thinking_delta("reasoning\n\n"), text_delta("answer")]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")
        self.assertNotIn("reasoning\n\n\nanswer", output)

    async def test_split_thinking_newlines_get_no_third_newline_before_answer(self):
        output, _ = await self.emit_events(
            [
                thinking_delta("reasoning\n"),
                thinking_delta("\n"),
                text_delta("answer"),
            ]
        )

        self.assertEqual(output, "\n  [thinking] reasoning\n\nanswer")
        self.assertNotIn("reasoning\n\n\nanswer", output)

    async def test_text_only_stream_keeps_existing_prefix_and_fragments(self):
        output, fragments = await self.emit_events([text_delta("answer")])

        self.assertEqual(output, "\nanswer")
        self.assertEqual(fragments, ["\n", "answer"])
        self.assertNotIn("[thinking]", output)

    async def test_thinking_then_tool_has_no_answer_separator(self):
        output, fragments = await self.emit_events(
            [thinking_delta("reasoning"), tool_start(), block_stop()]
        )

        self.assertEqual(output, "\n  [thinking] reasoning")
        self.assertEqual(fragments, ["\n  [thinking] ", "reasoning"])


if __name__ == "__main__":
    unittest.main()
