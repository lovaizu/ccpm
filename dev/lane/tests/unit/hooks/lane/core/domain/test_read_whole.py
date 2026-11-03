"""read_whole: a result is given only once each input the lane names was read to its end by the
subagent's Read calls, by their offset and limit."""

import unittest

import helpers
from helpers import done, read_whole


class TestMissing(helpers.PluginTest):
    def missing(self, *reads: dict) -> str:
        """What read_whole taking long.md finds missing, after the Read calls of the inputs."""
        calls = [helpers.kept_call("Read", **given) for given in reads]
        return read_whole.missing(
            {"input": ["long.md"]}, helpers.did(self.base, self.plugin, calls)
        )

    def setUp(self) -> None:
        super().setUp()
        self.write("long.md", "".join(f"line {n}\n" for n in range(1, 11)))

    def test_a_file_read_to_its_end_is_read_whole(self):
        for reads in (
            [{"file_path": "long.md"}],
            [{"file_path": "long.md", "limit": 4}, {"file_path": "long.md", "offset": 5}],
            [{"file_path": "long.md", "offset": 0, "limit": 10}],
            [{"file_path": f"{self.base}/long.md", "offset": 1, "limit": 10}],
        ):
            with self.subTest(reads=reads):
                # Given: the file read once whole, in two parts, from offset 0, or by its whole
                # path
                # When: the subagent gives its result
                # Then: nothing is missing
                self.assertEqual(self.missing(*reads), "")

    def test_a_file_read_in_part_or_not_at_all_is_missing_from_its_first_line_unread(self):
        for reads, said in (
            ([{"file_path": "long.md", "limit": 4}], "`long.md` unread from line 5"),
            ([{"file_path": "long.md", "offset": 3}], "`long.md` unread from line 1"),
            ([{"file_path": "other.md"}], "`long.md` unread from line 1"),
            ([], "`long.md` unread from line 1"),
        ):
            with self.subTest(reads=reads):
                # Given: the file's first four lines read, all but its first two, another file,
                # or nothing
                # When: the subagent gives its result
                # Then: the first line left unread is named
                self.assertEqual(self.missing(*reads), said)

    def test_a_read_naming_no_limit_covers_as_many_lines_as_the_read_tool_gives(self):
        # Given: a file one line longer than a Read gives by default, read with no limit
        self.write("long.md", "x\n" * (done.READ_LINES + 1))
        # When: the subagent gives its result
        # Then: its last line is unread
        self.assertEqual(
            self.missing({"file_path": "long.md"}),
            f"`long.md` unread from line {done.READ_LINES + 1}",
        )

    def test_an_empty_file_read_is_read_whole_and_an_input_not_there_is_named(self):
        # Given: an empty input, read
        self.write("long.md", "")
        # When: the subagent gives its result
        # Then: nothing is missing
        self.assertEqual(self.missing({"file_path": "long.md"}), "")
        # And: an input not there is named so
        given = {"input": ["gone.md"]}
        said = read_whole.missing(given, helpers.did(self.base, self.plugin))
        self.assertEqual(said, "`gone.md` is no file to read")


if __name__ == "__main__":
    unittest.main()
