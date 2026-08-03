import io
import threading
import time
import unittest

from rich.console import Console

from agents import ui


class TerminalOutputBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.output = io.StringIO()
        self.original_console = ui.console
        self.original_safe_stdout_write = ui._safe_stdout_write
        self.had_assistant_text_pending = hasattr(ui, "_assistant_text_pending")
        self.had_assistant_trailing_newlines = hasattr(ui, "_assistant_trailing_newlines")
        self.original_assistant_text_pending = getattr(ui, "_assistant_text_pending", None)
        self.original_assistant_trailing_newlines = getattr(ui, "_assistant_trailing_newlines", None)

        ui.console = Console(file=self.output, color_system=None, width=80)
        ui._safe_stdout_write = self.output.write
        ui._assistant_text_pending = False
        ui._assistant_trailing_newlines = 0

    def tearDown(self) -> None:
        ui.console = self.original_console
        ui._safe_stdout_write = self.original_safe_stdout_write

        if self.had_assistant_text_pending:
            ui._assistant_text_pending = self.original_assistant_text_pending
        else:
            del ui._assistant_text_pending

        if self.had_assistant_trailing_newlines:
            ui._assistant_trailing_newlines = self.original_assistant_trailing_newlines
        else:
            del ui._assistant_trailing_newlines

    def test_thinking_text_is_separated_from_tool_call(self) -> None:
        ui.print_assistant_text("  [thinking] inspect")
        ui.print_tool_call("list_files", {"path": "*"})

        self.assertIn("[thinking] inspect\n\n╭", self.output.getvalue())

    def test_single_trailing_newline_is_completed_before_cost(self) -> None:
        ui.print_assistant_text("answer\n")
        ui.print_cost(10, 5)

        self.assertTrue(self.output.getvalue().startswith("answer\n\n╭"))

    def test_existing_blank_line_is_not_duplicated_before_cost(self) -> None:
        ui.print_assistant_text("answer\n\n")
        ui.print_cost(10, 5)

        output = self.output.getvalue()
        self.assertTrue(output.startswith("answer\n\n╭"))
        self.assertNotIn("answer\n\n\n╭", output)

    def test_blank_line_split_across_fragments_is_not_duplicated_before_cost(self) -> None:
        ui.print_assistant_text("answer\n")
        ui.print_assistant_text("\n")
        ui.print_cost(10, 5)

        output = self.output.getvalue()
        self.assertTrue(output.startswith("answer\n\n╭"))
        self.assertNotIn("answer\n\n\n╭", output)

    def test_markdown_list_text_is_separated_from_cost(self) -> None:
        ui.print_assistant_text("- Docker support")
        ui.print_cost(10, 5)

        self.assertIn("- Docker support\n\n╭", self.output.getvalue())

    def test_consecutive_structured_panels_remain_compact(self) -> None:
        ui.print_tool_call("list_files", {"path": "*"})
        ui.print_tool_result("list_files", "README.md")

        output = self.output.getvalue()
        self.assertIn("╯\n╭", output)
        self.assertNotIn("╯\n\n╭", output)

    def test_empty_assistant_text_adds_no_leading_space_before_cost(self) -> None:
        ui.print_assistant_text("")
        ui.print_cost(10, 5)

        self.assertTrue(self.output.getvalue().startswith("╭"))

    def test_retry_after_active_spinner_starts_on_a_new_line(self) -> None:
        main_thread = threading.current_thread()
        separator_written = threading.Event()
        spinner_lock_attempted = threading.Event()
        spinner_write_completed = threading.Event()
        original_spinner_thread = ui._spinner_thread
        original_spinner_stop_set = ui._spinner_stop.is_set()
        original_test_writer = ui._safe_stdout_write
        had_output_lock = hasattr(ui, "_output_lock")
        original_output_lock = getattr(ui, "_output_lock", None)
        self.assertIsNone(original_spinner_thread)

        class InstrumentedOutputLock:
            def __init__(self) -> None:
                self._lock = threading.Lock()

            def __enter__(self) -> "InstrumentedOutputLock":
                if threading.current_thread() is not main_thread and separator_written.is_set():
                    spinner_lock_attempted.set()
                self._lock.acquire()
                return self

            def __exit__(self, _exc_type: object, _exc_value: object, _traceback: object) -> None:
                self._lock.release()

        def coordinated_write(text: object) -> None:
            rendered = ui._safe_text(text)
            if threading.current_thread() is main_thread and rendered == "\n":
                self.output.write(rendered)
                separator_written.set()
                deadline = time.monotonic() + 1
                while not spinner_lock_attempted.is_set() and not spinner_write_completed.is_set():
                    if time.monotonic() >= deadline:
                        self.fail("spinner did not attempt output during retry")
                    time.sleep(0.01)
                return

            self.output.write(rendered)
            if threading.current_thread() is not main_thread and rendered.startswith("\r"):
                spinner_write_completed.set()

        ui._output_lock = InstrumentedOutputLock()
        ui._safe_stdout_write = coordinated_write

        try:
            ui.start_spinner()
            deadline = time.monotonic() + 1
            while "Thinking..." not in self.output.getvalue():
                if time.monotonic() >= deadline:
                    self.fail("spinner did not render its initial text")
                time.sleep(0.01)

            ui.print_retry(1, 3, "network error")
            self.assertTrue(spinner_write_completed.wait(timeout=1), "spinner frame was not rendered")

            output = self.output.getvalue()
            self.assertNotIn("Thinking...  ↻ Retry", output)
            self.assertIn("\n  ↻ Retry 1/3: network error", output)
            self.assertLess(output.index("↻ Retry 1/3: network error"), output.rfind("Thinking..."))
        finally:
            try:
                ui.stop_spinner()
            finally:
                ui._safe_stdout_write = original_test_writer
                ui._spinner_thread = original_spinner_thread
                if original_spinner_stop_set:
                    ui._spinner_stop.set()
                else:
                    ui._spinner_stop.clear()
                if had_output_lock:
                    ui._output_lock = original_output_lock
                else:
                    del ui._output_lock


if __name__ == "__main__":
    unittest.main()
