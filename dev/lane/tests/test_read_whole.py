"""read_whole: once the subagent has begun reading an input the lane takes, a call that writes while
lines of it are left unread is a drift, held from the subagent's record; every other call is not."""

from __future__ import annotations

import json
import os
import unittest

import helpers
from helpers import NO_PLUGIN, read_whole
from test_guard import GuardTest

# The input of 100 lines, as the Read tool gives back the lines from the first to the last, each
# after its number and a tab, and a line after the last for the file's closing line break.
TEXT = "".join(f"line {n}\n" for n in range(1, 101))


def shown(first, last):
    """What the Read tool gives back of the input's lines from the first to the last."""
    return "".join(f"{n}\tline {n}\n" for n in range(first, last + 1))


class ReadWholeTest(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        self.input = os.path.join(self.base, "in.md")
        self.write(self.input, TEXT)

    def drifts(self, tool: str = "Write", given: dict | None = None) -> bool:
        """Whether a call of the tool with the input, a Write where none is given, drifts from
        read_whole taking `in.md`."""
        given = {"file_path": "out.md", "content": "x"} if given is None else given
        return read_whole.drifts(helpers.call_of(self.called(tool, given)), ["in.md"], NO_PLUGIN)


class TestDrift(ReadWholeTest):
    def test_a_write_after_reading_the_input_in_part_drifts(self):
        too_large = "File content (1.9MB) exceeds maximum allowed size (256KB)."
        for what, calls in {
            "the first lines": [("Read", {"file_path": self.input, "limit": 50}, shown(1, 50))],
            "all but the first": [("Read", {"file_path": "in.md", "offset": 2}, shown(2, 101))],
            "all but the last": [("Read", {"file_path": "in.md"}, shown(1, 99))],
            "all but a gap": [
                ("Read", {"file_path": "in.md", "limit": 10}, shown(1, 10)),
                ("Read", {"file_path": "in.md", "offset": 12}, shown(12, 101)),
            ],
            "a read too large to give back": [("Read", {"file_path": "in.md"}, too_large)],
            "the lines a search finds": [helpers.bash("grep -n line in.md")],
            "all but the line before the last 51": [
                helpers.bash("head -n 48 in.md"),
                helpers.bash("tail -51 in.md"),
            ],
            "all but the line before the last 5": [
                helpers.bash("head -n 94 in.md"),
                helpers.bash("tail -5 in.md"),
            ],
            "all but the line before the last": [
                helpers.bash("head -n 98 in.md"),
                helpers.bash("tail -n 1 in.md"),
            ],
            "the first lines and none from the end": [
                helpers.bash("head -50 in.md"),
                helpers.bash("tail -0 in.md"),
            ],
        }.items():
            with self.subTest(what=what):
                # Given: a record of the input read in part
                self.record(calls)
                # When: the subagent writes
                # Then: it is a drift
                self.assertTrue(self.drifts())

    def test_a_write_after_reading_all_but_the_last_of_an_odd_count_of_lines_drifts(self):
        # Given: an input of three lines, and a record of its first two read
        self.write(self.input, "a\nb\nc\n")
        self.record([("Read", {"file_path": "in.md", "limit": 2}, "1\ta\n2\tb")])
        # When: the subagent writes
        # Then: it is a drift
        self.assertTrue(self.drifts())

    def test_each_way_of_writing_drifts(self):
        # Given: a record of the input read in part
        self.record([("Read", {"file_path": "in.md"}, shown(1, 50))])
        for tool, given in (
            ("Edit", {"file_path": "out.md", "old_string": "a", "new_string": "b"}),
            ("NotebookEdit", {"notebook_path": "out.ipynb", "new_source": "x"}),
            ("Bash", {"command": "echo x > out.md"}),
            ("Bash", {"command": "echo x > /data/out.md"}),
            ("Write", {"file_path": os.devnull, "content": "x"}),
        ):
            with self.subTest(tool=tool, given=given):
                # When: the subagent writes by the tool or a command, by a command out of the
                # folder, or by a tool writing even the null device
                # Then: it is a drift
                self.assertTrue(self.drifts(tool, given))


class TestLetThrough(ReadWholeTest):
    def test_a_write_after_reading_the_input_to_its_end_is_no_drift(self):
        for what, calls in {
            "at once": [("Read", {"file_path": "in.md"}, shown(1, 101))],
            "in two reads": [
                ("Read", {"file_path": "in.md", "limit": 50}, shown(1, 50)),
                ("Read", {"file_path": "in.md", "offset": 51}, shown(51, 101)),
            ],
            "in reads that overlap": [
                ("Read", {"file_path": "in.md", "limit": 60}, shown(1, 60)),
                ("Read", {"file_path": "in.md", "offset": 40}, shown(40, 101)),
            ],
            "from both ends": [helpers.bash("head -n 49 in.md"), helpers.bash("tail -n 51 in.md")],
            "by sed after a part": [
                ("Read", {"file_path": "in.md", "limit": 50}, shown(1, 50)),
                helpers.bash("sed -n '51,$p' in.md"),
            ],
            "by sed in two parts": [
                helpers.bash("sed -n 1,51p in.md"),
                helpers.bash("sed -n 52,100p in.md"),
            ],
            "by tail of more lines than it has": [helpers.bash("tail -n 200 in.md")],
            "whole by cat": [helpers.bash("cat in.md")],
        }.items():
            with self.subTest(what=what):
                # Given: a record of the input read to its end
                self.record(calls)
                # When: the subagent writes
                # Then: it is no drift
                self.assertFalse(self.drifts())

    def test_a_write_before_the_input_is_begun_is_no_drift(self):
        for other in ("a.md", "other.md"):
            with self.subTest(other=other):
                # Given: a record of another file read in part, and none of the input
                self.write(os.path.join(self.base, other), TEXT)
                self.record([("Read", {"file_path": other}, shown(1, 50))])
                # When: the subagent writes
                # Then: it is no drift, as the lane tells only an input begun and left
                self.assertFalse(self.drifts())

    def test_a_call_that_writes_nothing_is_no_drift(self):
        # Given: a record of the input read in part
        self.record([("Read", {"file_path": "in.md"}, shown(1, 50))])
        for tool, given in (
            ("Read", {"file_path": "other.md"}),
            ("Bash", {"command": "cat other.md && echo --- && ls"}),
            ("Bash", {"command": "sed -n '51,60p' in.md 2>/dev/null"}),
        ):
            with self.subTest(tool=tool, given=given):
                # When: the subagent reads on, or runs what writes nothing but the null device
                # Then: it is no drift
                self.assertFalse(self.drifts(tool, given))

    def test_an_input_not_there_is_no_drift(self):
        # Given: the input read in part, then removed
        self.record([("Read", {"file_path": "in.md"}, shown(1, 50))])
        os.remove(self.input)
        # When: the subagent writes
        # Then: it is no drift, as nothing is there to read
        self.assertFalse(self.drifts())

    def test_an_input_empty_is_no_drift(self):
        # Given: the input empty, read
        self.write(self.input, "")
        self.record([("Read", {"file_path": "in.md"}, "Warning: the file exists but is empty.")])
        # When: the subagent writes
        # Then: it is no drift, as nothing is left to read
        self.assertFalse(self.drifts())

    def test_an_input_the_words_do_not_settle_is_no_drift(self):
        # Given: a lane taking an input named by a variable, which no path settles
        self.record([("Read", {"file_path": "in.md"}, shown(1, 50))])
        # When: the subagent writes
        # Then: it is no drift
        self.assertFalse(
            read_whole.drifts(helpers.call_of(self.called("Write", {})), ["$IN"], NO_PLUGIN)
        )


class TestGuard(GuardTest):
    """read_whole laid on step 1 of changelog-writer, run as Claude Code runs the hook."""

    LAID = ((1, "read_whole", ["in.md"]),)

    def setUp(self) -> None:
        super().setUp()
        self.write(os.path.join(self.base, "in.md"), TEXT)
        self.part = [("Read", {"file_path": "in.md", "limit": 50}, shown(1, 50))]

    def written_after(self, calls):
        """What the guard does on a write after the calls in the subagent's record."""
        self.record(calls)
        event = self.called("Write", {"file_path": "out.md", "content": "x"})
        return self.guard(json.dumps(event))

    def test_a_write_after_reading_a_part_is_stopped_with_the_sentence(self):
        # Given: changelog-writer's record of the first 50 lines of in.md read
        # When: it writes
        # Then: the call is stopped, and the subagent told the sentence headed by the plugin
        self.assertEqual(self.written_after(self.part), ("told", "notes: Read `in.md` to its end."))

    def test_a_write_after_reading_the_rest_goes_on(self):
        # Given: changelog-writer's record of in.md read in two parts to its end
        rest = [*self.part, ("Read", {"file_path": "in.md", "offset": 51}, shown(51, 101))]
        # When: it writes
        # Then: the call goes on, nothing said
        self.assertEqual(self.written_after(rest), ("", ""))


if __name__ == "__main__":
    unittest.main()
