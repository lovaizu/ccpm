"""The cases of the lanes that the guard checks as a role gives its result: test_after, end_when,
and every_item."""

from typing import ClassVar

from helpers import end_when, every_item, lanes, test_after, testing

CONTEXT = lanes.Context((), ())


def call(tool, **given):
    return lanes.Call(tool, given, "/")


class TestTestAfter(testing.FolderTest):
    GIVEN: ClassVar[dict] = {"output": ["/p/notes"], "test": ["python3 /p/check.py"]}

    def test_an_output_never_changed_needs_no_test(self):
        self.assertIsNone(test_after.end(self.GIVEN, [], CONTEXT))

    def test_a_test_passed_after_the_last_change_keeps_the_lane(self):
        calls = [
            call("Write", file_path="/p/notes/a.md"),
            call("Bash", command="python3 /p/check.py"),
        ]
        self.assertIsNone(test_after.end(self.GIVEN, calls, CONTEXT))

    def test_a_change_after_the_last_pass_breaks_the_lane(self):
        calls = [
            call("Bash", command="python3 /p/check.py"),
            call("Edit", file_path="/p/notes/a.md"),
        ]
        self.assertEqual(
            test_after.end(self.GIVEN, calls, CONTEXT),
            "`/p/notes` changed after the last pass of `python3 /p/check.py`.",
        )

    def test_a_change_with_no_pass_breaks_the_lane(self):
        calls = [call("Write", file_path="/p/notes/a.md")]
        self.assertIsNotNone(test_after.end(self.GIVEN, calls, CONTEXT))

    def test_a_test_given_null_keeps_the_lane(self):
        calls = [call("Write", file_path="/p/notes/a.md")]
        self.assertIsNone(test_after.end({"output": ["/p/notes"], "test": []}, calls, CONTEXT))


class TestEndWhen(testing.FolderTest):
    def test_an_output_that_is_there_keeps_the_lane(self):
        self.write("notes.json", "{}")
        self.assertIsNone(end_when.end({"output": [f"{self.base}/notes.json"]}, [], CONTEXT))

    def test_an_output_that_isnt_there_breaks_the_lane(self):
        self.assertEqual(
            end_when.end({"output": [f"{self.base}/notes.json"]}, [], CONTEXT),
            f"`{self.base}/notes.json` isn't there.",
        )


class TestEveryItem(testing.FolderTest):
    REVIEW = (
        "# Review\n\n- **B-1** is missing.\n- `B-2` is wrong.\n  - B-9 is a sub-item.\n- No ID.\n"
    )

    def given(self):
        self.write("review.md", self.REVIEW)
        return {"input": [f"{self.base}/review.md"]}

    def wrote(self, text, name="answers.md"):
        self.write(name, text)
        return call("Write", file_path=f"{self.base}/{name}")

    def test_the_items_of_a_markdown_list_are_its_top_level_items_beginning_with_an_id(self):
        self.assertEqual(every_item.items(self.REVIEW), ["B-1", "B-2"])

    def test_an_id_in_brackets_is_an_item(self):
        self.assertEqual(every_item.items("- [KR1.1] holds.\n* R33\n"), ["KR1.1", "R33"])

    def test_each_item_named_in_a_file_written_keeps_the_lane(self):
        given = self.given()
        self.assertIsNone(every_item.end(given, [self.wrote("B-1 added. B-2 fixed.")], CONTEXT))

    def test_an_item_no_file_written_names_breaks_the_lane(self):
        given = self.given()
        self.assertEqual(
            every_item.end(given, [self.wrote("B-1 added.")], CONTEXT),
            f"No file written since the last change of `{self.base}/review.md` answers `B-2`.",
        )

    def test_an_id_within_a_longer_one_answers_nothing(self):
        given = self.given()
        found = every_item.end(given, [self.wrote("B-12, B-2.1, AB-1, B-2.")], CONTEXT)
        self.assertEqual(
            found,
            f"No file written since the last change of `{self.base}/review.md` answers `B-1`.",
        )

    def test_the_input_itself_answers_nothing(self):
        given = self.given()
        self.assertIsNotNone(
            every_item.end(given, [call("Edit", file_path=f"{self.base}/review.md")], CONTEXT)
        )

    def test_a_file_written_before_the_last_change_of_the_input_answers_nothing(self):
        given = self.given()
        calls = [self.wrote("B-1 B-2"), call("Edit", file_path=f"{self.base}/review.md")]
        self.assertIsNotNone(every_item.end(given, calls, CONTEXT))

    def test_a_call_that_writes_nothing_answers_nothing(self):
        given = self.given()
        calls = [call("Bash", command="ls"), self.wrote("B-1 B-2")]
        self.assertIsNone(every_item.end(given, calls, CONTEXT))

    def test_a_file_written_twice_counts_once(self):
        given = self.given()
        self.assertIsNone(
            every_item.end(given, [self.wrote("B-1 B-2"), self.wrote("B-1 B-2")], CONTEXT)
        )

    def test_a_file_written_and_gone_since_answers_nothing(self):
        given = self.given()
        calls = [call("Write", file_path=f"{self.base}/gone.md")]
        self.assertIsNotNone(every_item.end(given, calls, CONTEXT))

    def test_an_input_with_no_item_keeps_the_lane(self):
        self.write("review.md", "Nothing to answer.\n")
        self.assertIsNone(every_item.end({"input": [f"{self.base}/review.md"]}, [], CONTEXT))

    def test_an_input_that_isnt_there_breaks_the_lane(self):
        self.assertEqual(
            every_item.end({"input": [f"{self.base}/gone.md"]}, [], CONTEXT),
            f"`{self.base}/gone.md` isn't there to read its items.",
        )
