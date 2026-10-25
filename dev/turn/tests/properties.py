"""Property-based tests: each behavior over a kind of input, checked on many inputs Hypothesis
makes, new on every run, CI included."""

import json
import os
import runpy
import shutil
import tempfile
import unittest

from helpers import (
    CALL,
    CAN,
    ITEM_F1,
    QUESTION,
    RESULT,
    TURN,
    WAITS,
    RepoTest,
    call,
    forms,
    prompts,
    records,
    state,
    testing,
)

hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

FORMS = (forms.CHECK, forms.CLAIM, forms.FIRST_READING, forms.LEFT)
ITEMS = [ITEM_F1]
# JSON values of any shape, with the keys the forms look for among others.
KEYS = st.sampled_from(
    ["items", "questions", "checklist", "item", "good", "lines", "question", "can"]
    + ["lessons", "whose", "lesson", "grounds", "record", "quote", "checked", "recommended"]
    + ["parts", "part", "places", "did", "lacking"]
) | st.text(max_size=5)
LEAVES = st.none() | st.booleans() | st.integers() | st.text(max_size=20)
VALUES = st.recursive(
    LEAVES,
    lambda inner: st.lists(inner, max_size=4) | st.dictionaries(KEYS, inner, max_size=5),
    max_leaves=20,
)


class TestForms(RepoTest):
    @given(VALUES, st.sampled_from(FORMS), st.booleans())
    def test_any_reply_is_told_what_is_wrong_and_never_breaks_the_run(self, value, form, each):
        # Given: a reply of any shape, as JSON, on an item of its part or one asked of each part
        # When: it is checked by any form
        # Then: what is wrong is said in words, and nothing else happens
        said = forms.check(json.dumps(value), ITEMS, ["README.md"], form, ITEMS if each else [])
        self.assertIsInstance(said, list)
        self.assertTrue(all(isinstance(s, str) and s for s in said))

    @given(VALUES)
    def test_any_reply_of_the_learner_is_told_what_is_wrong(self, value):
        # Given: a learner's reply of any shape, as JSON, on a record kept
        # When: it is checked
        # Then: what is wrong is said in words, and nothing else happens
        said = forms.learnt(json.dumps(value), [self.given_record("a1", "{}")])
        self.assertTrue(all(isinstance(s, str) and s for s in said))

    @given(st.lists(st.sampled_from(["# t", "## h", "### s", "```", "x", ""]), max_size=30))
    def test_a_document_s_parts_take_every_line_once_in_order(self, lines):
        # Given: a document of any lines of headings, fences and text
        # When: it is split into its parts
        # Then: the parts run from its first line to its last, each starting where the one before
        # ends, and each but the first opens at a top heading
        self.write("README.md", "".join(line + "\n" for line in lines))
        spans = [s[1:] for s in map(forms.span, forms.parts(["README.md"])) if s]
        starts = [a for a, _ in spans]
        self.assertEqual(
            [n for a, b in spans for n in range(a, b + 1)], list(range(1, len(lines) + 1))
        )
        self.assertTrue(all(lines[a - 1].startswith("## ") for a in starts[1:]))

    @given(st.dictionaries(KEYS, VALUES, max_size=4))
    def test_a_reply_in_a_json_fence_is_read_as_the_reply(self, value):
        # Given: a reply of any object
        # When: it is given inside a ```json fence
        # Then: it is read as if given bare
        text = json.dumps(value)
        fenced = f"```json\n{text}\n```"
        lists = ("items", "questions")
        self.assertEqual(forms.parsed(fenced, lists), forms.parsed(text, lists))

    @given(st.integers(1, 30), st.integers(0, 40), st.integers(0, 40))
    def test_lines_are_taken_when_they_lie_inside_the_work(self, count, start, end):
        # Given: a work of any number of lines
        # When: a Good names any range of lines
        # Then: it is taken when the range runs forwards inside the work, and named otherwise
        self.write("README.md", "x\n" * count)
        lines = f"README.md:{start}-{end}"
        self.assertEqual(forms.in_files(lines, ["README.md"]), 1 <= start <= end <= count)


class TestCall(unittest.TestCase):
    @given(st.text(max_size=200))
    def test_any_call_is_taken_or_stopped_with_words(self, text):
        # Given: any text as a call
        # When: it is parsed
        # Then: it gives an object, or stops saying what to give
        try:
            self.assertIsInstance(call.parse(text), dict)
        except call.Stop as stop:
            self.assertIn("give it as", str(stop))


# Lines a checklist is made of: items of each scope, the line of a scope, headings of other levels,
# fences of each mark, and text.
CHECKLIST_LINES = st.sampled_from(
    ["### B-1: x", "### B-2: y", "## B-3: z", "#### B-4: w", "", "Scope: its part"]
    + ["Scope: each part", "```", "~~~", "  ```", "x"]
)


# Parts of a checklist for turn's adapter of the items port: items with their scope, and what is
# not an item, a heading of another level or with no ID, the frontmatter's mark, fences and text.
CHECKLIST_PARTS = st.sampled_from(
    [
        "### B-1: x\n\nScope: whole",
        "### B-2: y ###\n\nScope: whole",
        "   ### B-5: v\n\nScope: whole",
    ]
    + ["## B-3: z", "#### B-4: w", "### Notes", "###B-6: u", "### B-7:", "### b-8: t"]
    + ["---", "```", "````", "~~~", "```md", "    ```", "x", ""]
)
# turn's adapter of lane's items port, read from its file, as its name is no module's: its reading.
ITEMS_READ = runpy.run_path(os.path.join(TURN, "hooks", "adapters", "items-checklist.py"))["ids"]


class TestItems(RepoTest):
    @given(st.lists(CHECKLIST_LINES, max_size=30))
    def test_any_checklist_gives_its_items_outside_fences_or_stops_with_words(self, lines):
        # Given: a checklist of any lines of items, scopes, other headings, fences and text
        self.write("checklist.md", "".join(line + "\n" for line in lines))
        # When: its items are read
        try:
            found = call.items("checklist.md")
        except call.Stop as stop:
            # Then: it stops saying what to put, or each item is a heading of an item's level
            # outside a fence, as lane's template reads them, with the scope its line says
            self.assertIn("turn: checklist.md", str(stop))
            return
        outside = {n for n, level, _ in call.template.headings(lines, 0) if level == 3}
        self.assertEqual(len(found), len([n for n in outside if lines[n - 1][4:6] == "B-"]))
        self.assertTrue(all(i["scope"] in call.SCOPES for i in found))

    @given(st.lists(CHECKLIST_PARTS, max_size=20))
    def test_turn_s_adapter_gives_the_items_turn_reads_in_any_checklist(self, parts):
        # Given: a checklist of any parts: items with their scope, as written plainly, closed or
        # indented, headings of other levels or with no ID, frontmatter marks, fences and text
        text = "".join(part + "\n" for part in parts)
        self.write("checklist.md", text)
        # When: turn reads its items, and turn's adapter of lane's items port reads them
        try:
            read = [i["item"] for i in call.items("checklist.md")]
        except call.Stop as stop:
            self.assertIn("holds no item", str(stop))
            read = []
        # Then: the adapter gives the IDs turn reads, in the same order
        self.assertEqual(ITEMS_READ(text), read)


# Entries a record holds: messages of text and of parts, attachments, Claude Code's copies, and
# values of no shape.
ENTRIES = st.lists(
    st.dictionaries(
        st.sampled_from(["type", "message", "attachment"]),
        st.sampled_from(["user", "assistant", "attachment", "api-request-blob"])
        | st.dictionaries(st.sampled_from(["content", "type", "filename", "snippet"]), VALUES),
        max_size=3,
    ),
    max_size=8,
)


class TestRecords(RepoTest):
    @given(ENTRIES)
    def test_any_record_is_shown_as_text_of_its_own_entries(self, entries):
        # Given: a record of any entries, as Claude Code might write them
        self.write("agent.jsonl", "".join(json.dumps(e) + "\n" for e in entries))
        # When: it is shown as text for the learner
        shown = records.as_text("agent.jsonl")
        # Then: it is text, a line for each message or part shown, ending a line
        self.assertIsInstance(shown, str)
        self.assertTrue(shown.endswith("\n"))

    @given(st.text(max_size=5000))
    def test_a_record_wrapped_keeps_every_word_on_lines_a_read_shows(self, text):
        # Given: a record shown as any text
        # When: it is wrapped for the learner to read
        # Then: its words are the same, in order, and a line is longer than a read shows only
        # where it is one word
        wrapped = records.wrapped(text)
        self.assertEqual(forms.spaced(wrapped), forms.spaced(text))
        for line in wrapped.splitlines():
            self.assertTrue(len(line) <= records.WIDTH or len(line.split()) <= 1, line)


class TestCallTest(unittest.TestCase):
    @given(st.text(max_size=50))
    def test_any_test_of_words_is_taken_as_it_is_and_one_of_blanks_stops(self, test):
        # Given: a call whose test is any text
        # When: the call is checked
        # Then: a test of words is taken as it came, blanks at its ends and all; one of blanks
        # alone, or empty, stops, saying the test is not a command
        asked = dict(CALL, test=test)
        if test.strip():
            self.assertEqual(call.checked(asked)["test"], test)
        else:
            with self.assertRaises(call.Stop) as stop:
                call.checked(asked)
            self.assertIn('"test" is not a command', str(stop.exception))


class TestAnswer(RepoTest):
    @given(st.text(max_size=200))
    def test_any_answer_of_words_is_kept_as_it_came(self, answer):
        # Given: a run whose check asked a question, started anew for each answer
        # When: the calling AI's answer, any text, is handed on
        # Then: an answer of words is kept as it came, the blanks at its ends aside; one of blanks
        # alone is asked for again, and the run still waits on it
        if os.path.exists(state.state_path(RESULT)):
            os.remove(state.state_path(RESULT))
        self.turn("start", json.dumps(CALL))
        self.next()
        self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]})
        self.next()
        code, _ = self.turn("next", RESULT, stdin=answer)
        kept = self.state()
        if answer.strip():
            self.assertEqual((code, kept["answers"][-1]["answer"]), (0, answer.strip()))
        else:
            self.assertEqual((code, kept["stage"]), (1, "asked"))


# Names a layout is made of: folders and files, some named as the result or as one of its run's
# files, and some only beginning like them.
NAMES = st.sampled_from(["a", "b", "r.json", "r.json.run.json", "r.json.x", "r.jsonx"])


def reached(paths):
    """Every file and folder at or under the paths, as real paths."""
    found = set()
    for path in paths:
        found.add(os.path.realpath(path))
        for folder, folders, files in os.walk(path):
            found.update(os.path.realpath(os.path.join(folder, n)) for n in folders + files)
    return found


class TestGiven(RepoTest):
    @given(
        st.lists(st.lists(NAMES, min_size=1, max_size=3), max_size=12),
        st.lists(st.sampled_from(["a", "b"]), max_size=2),
        st.lists(st.lists(NAMES, max_size=3), min_size=1, max_size=3),
    )
    def test_the_paths_given_reach_all_they_reached_but_the_run_s_files(self, files, down, paths):
        # Given: any layout of files and folders, the result at any depth with its state and a
        # record beside it, and any paths that are there in it
        # When: the paths are given without the run's files
        # Then: they reach every file and folder the paths reached but the run's files and what is
        # in them, and the folders opened on the way to the result's folder; and none of them is
        # such a folder. What the paths reach is found here by walking the layout, apart from how
        # without_run_files opens folders, so the two cannot share a slip.
        place = tempfile.mkdtemp(dir=self.base)
        os.chdir(place)
        try:
            result = os.path.join(*down, "r.json")
            for path in (result, result + ".run.json", result + ".records/1.txt"):
                self.write(path, "")
            for names in files:
                try:
                    self.write(os.path.join(*names), "")
                except OSError:
                    pass
            asked = [os.path.join(".", *p) for p in paths if os.path.exists(os.path.join(".", *p))]
            folder = os.path.realpath(os.path.dirname(result) or ".")
            ours = {
                os.path.join(folder, n)
                for n in os.listdir(folder)
                if n == "r.json" or n.startswith("r.json.")
            }
            on_way = {p for p in reached(asked) if folder == p or folder.startswith(p + os.sep)}
            kept = {
                p
                for p in reached(asked) - on_way
                if not any(p == o or p.startswith(o + os.sep) for o in ours)
            }
            given_now = prompts.without_run_files(asked, result)
            self.assertEqual(reached(given_now), kept)
            self.assertFalse({os.path.realpath(p) for p in given_now} & on_way)
        finally:
            os.chdir(self.base)
            shutil.rmtree(place)
