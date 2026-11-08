"""The cases of the read lanes' checks. read_only lets a role read only its inputs, read_never stops
a read of the files it names, and read_whole holds a step done once the role reads a file to its
end."""

from typing import ClassVar

from helpers import lanes, read_never, read_only, read_whole, testing


def read(path, cwd="/p", **more):
    return lanes.Call("Read", {"file_path": path, **more}, cwd)


def kept(path, **more):
    return lanes.Call("Read", {"file_path": path, **more}, "/")


class TestReadOnly(testing.FolderTest):
    GIVEN: ClassVar[dict] = {"input": ["/p/CHANGELOG.md", "/p/notes"]}
    CONTEXT = lanes.Context((), ("/plugin/forms/notes.json",))

    def test_a_read_of_an_input_goes_on(self):
        self.assertIsNone(read_only.check(read("CHANGELOG.md"), self.GIVEN, self.CONTEXT))

    def test_a_read_under_an_input_folder_goes_on(self):
        self.assertIsNone(read_only.check(read("/p/notes/a.md"), self.GIVEN, self.CONTEXT))

    def test_a_read_of_a_file_the_lanes_let_beside_the_inputs_goes_on(self):
        call = read("/plugin/forms/notes.json")
        self.assertIsNone(read_only.check(call, self.GIVEN, self.CONTEXT))

    def test_a_read_of_any_other_file_is_broken(self):
        self.assertEqual(
            read_only.check(read("README.md"), self.GIVEN, self.CONTEXT),
            "The call reads /p/README.md.",
        )

    def test_a_grep_of_the_folder_it_runs_in_reads_that_folder(self):
        call = lanes.Call("Grep", {"pattern": "x"}, "/p")
        self.assertEqual(read_only.check(call, self.GIVEN, self.CONTEXT), "The call reads /p.")

    def test_a_write_goes_on(self):
        call = lanes.Call("Write", {"file_path": "/p/x"}, "/p")
        self.assertIsNone(read_only.check(call, self.GIVEN, self.CONTEXT))


class TestReadNever(testing.FolderTest):
    GIVEN: ClassVar[dict] = {"input": ["/p/tree.json", "/p/secret"]}
    CONTEXT = lanes.Context((), ())

    def test_a_read_of_a_file_it_names_is_broken(self):
        self.assertEqual(
            read_never.check(read("tree.json"), self.GIVEN, self.CONTEXT),
            "The call reads /p/tree.json.",
        )

    def test_a_grep_under_a_folder_it_names_is_broken(self):
        call = lanes.Call("Grep", {"pattern": "x", "path": "secret/a"}, "/p")
        self.assertEqual(
            read_never.check(call, self.GIVEN, self.CONTEXT), "The call reads /p/secret/a."
        )

    def test_a_read_of_any_other_file_goes_on(self):
        self.assertIsNone(read_never.check(read("README.md"), self.GIVEN, self.CONTEXT))

    def test_a_write_of_a_file_it_names_goes_on(self):
        call = lanes.Call("Write", {"file_path": "/p/tree.json"}, "/p")
        self.assertIsNone(read_never.check(call, self.GIVEN, self.CONTEXT))

    def test_a_grep_of_a_folder_above_one_it_names_goes_on(self):
        call = lanes.Call("Grep", {"pattern": "x"}, "/p")
        self.assertIsNone(read_never.check(call, self.GIVEN, self.CONTEXT))


class TestReadWhole(testing.FolderTest):
    def given(self, lines):
        self.write("a.md", "".join(f"line {n}\n" for n in range(1, lines + 1)))
        return {"input": [f"{self.base}/a.md"]}

    def test_a_read_of_the_input_is_its_trace(self):
        self.assertTrue(read_whole.traced(read(f"{self.base}/a.md"), self.given(1)))

    def test_a_read_of_another_file_is_no_trace(self):
        self.assertFalse(read_whole.traced(read(f"{self.base}/b.md"), self.given(1)))

    def test_a_read_with_no_limit_covers_a_file_of_2000_lines(self):
        given = self.given(2000)
        self.assertIsNone(read_whole.done(given, [kept(f"{self.base}/a.md")]))

    def test_a_read_with_no_limit_leaves_line_2001_unread(self):
        given = self.given(2001)
        self.assertEqual(
            read_whole.done(given, [kept(f"{self.base}/a.md")]),
            f"`{self.base}/a.md` has lines 2001 to 2001 unread.",
        )

    def test_reads_by_offset_and_limit_that_cover_every_line_read_it_whole(self):
        given = self.given(30)
        calls = [
            kept(f"{self.base}/a.md", limit=10),
            kept(f"{self.base}/a.md", offset=11, limit=20),
        ]
        self.assertIsNone(read_whole.done(given, calls))

    def test_a_line_between_two_reads_is_unread(self):
        given = self.given(30)
        calls = [
            kept(f"{self.base}/a.md", limit=10),
            kept(f"{self.base}/a.md", offset=12, limit=20),
        ]
        self.assertEqual(
            read_whole.done(given, calls), f"`{self.base}/a.md` has lines 11 to 11 unread."
        )

    def test_the_unread_lines_are_told_from_the_first_to_the_last_of_their_run(self):
        given = self.given(30)
        calls = [
            kept(f"{self.base}/a.md", limit=10),
            kept(f"{self.base}/a.md", offset=15, limit=20),
        ]
        self.assertEqual(
            read_whole.done(given, calls), f"`{self.base}/a.md` has lines 11 to 14 unread."
        )

    def test_a_file_never_read_is_unread(self):
        self.assertEqual(read_whole.done(self.given(3), []), f"`{self.base}/a.md` is unread.")

    def test_an_empty_file_read_once_is_read_whole(self):
        self.write("a.md", "")
        self.assertIsNone(
            read_whole.done({"input": [f"{self.base}/a.md"]}, [kept(f"{self.base}/a.md")])
        )

    def test_the_lines_a_kept_read_gives_count_in_place_of_the_files_now(self):
        given = self.given(5)
        self.assertIsNone(read_whole.done(given, [kept(f"{self.base}/a.md", lines=3, limit=3)]))

    def test_a_file_that_isnt_there_cant_be_read_whole(self):
        self.assertEqual(
            read_whole.done({"input": [f"{self.base}/gone.md"]}, []),
            f"`{self.base}/gone.md` isn't there to read.",
        )

    def test_one_input_read_whole_of_several_is_enough(self):
        given = {"input": [f"{self.base}/gone.md", *self.given(1)["input"]]}
        self.assertIsNone(read_whole.done(given, [kept(f"{self.base}/a.md")]))
