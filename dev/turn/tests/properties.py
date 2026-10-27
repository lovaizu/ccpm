"""Property-based tests: each behavior over a kind of input, checked on many inputs Hypothesis
makes, new on every run, CI included."""

import json
import os
import shutil
import tempfile
import unittest

from helpers import (
    CALL,
    ITEM_F1,
    RESULT,
    TURN,
    WAITS,
    RepoTest,
    call,
    forms,
    prompts,
    state,
    testing,
    work_parts,
)

(template,) = testing.lane_code(TURN, "template")
hypothesis = testing.hypothesis()
given = hypothesis.given
st = hypothesis.strategies

FORMS = (forms.CLAIM, forms.FIRST_READING, forms.LEFT)
ITEMS = [ITEM_F1]
# JSON values of any shape, with the keys the forms look for among others.
KEYS = st.sampled_from(
    ["items", "questions", "checklist", "item", "lines", "need", "question", "recommended"]
    + ["chosen", "blocked"]
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

    @given(st.lists(st.sampled_from(["# t", "## h", "### s", "```", "x", ""]), max_size=30))
    def test_a_document_s_parts_take_every_line_once_in_order(self, lines):
        # Given: a document of any lines of headings, fences and text
        # When: it is split into its parts
        # Then: the parts run from its first line to its last, each starting where the one before
        # ends, and each but the first opens at a top heading
        self.write("README.md", "".join(line + "\n" for line in lines))
        spans = [s[1:] for s in map(forms.span, work_parts.parts(["README.md"])) if s]
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
        # When: an item names any range of lines
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
        outside = {n for n, level, _ in template.headings(lines, 0) if level == 3}
        self.assertEqual(len(found), len([n for n in outside if lines[n - 1][4:6] == "B-"]))
        self.assertTrue(all(i["scope"] in call.SCOPES for i in found))


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
        # Given: a run whose generator asked a question, started anew for each answer
        # When: the calling AI's answer, any text, is handed on
        # Then: an answer of words is kept as it came, the blanks at its ends aside; one of blanks
        # alone is asked for again, and the run still waits on it
        if os.path.exists(state.state_path(RESULT)):
            os.remove(state.state_path(RESULT))
        self.started()
        self.made(WAITS)
        code, _ = self.turn("next", RESULT, stdin=answer)
        kept = self.state()
        if answer.strip():
            self.assertEqual((code, kept["answers"][-1]["answer"]), (0, answer.strip()))
        else:
            self.assertEqual((code, kept["stage"]), (1, "asked"))


# Names of a result's folders and of the result, some holding what the name of a run's folder
# writes `/` and `%` as, or a pattern of file names reads as a set of letters.
PARTS = st.sampled_from(["a", "b", "%", "2F", "%2F", "%25", "-", "a-b", "[a]"])


class TestRunFolders(RepoTest):
    @given(st.lists(PARTS, min_size=1, max_size=3), st.lists(PARTS, min_size=1, max_size=3))
    def test_two_results_share_a_run_s_folder_only_where_they_are_one(self, one, other):
        # Given: any two results in the repository, each by its folders and its name
        # When: the folder of each one's run is asked for, the first given from the root, the
        # second as a whole path
        # Then: the two are one folder where the results are one path, and two otherwise, each in
        # turn's folder at the root
        first = state.folder(os.path.join(*one))
        second = state.folder(self.here(os.path.join(*other)))
        self.assertEqual(first == second, one == other)
        self.assertEqual({os.path.dirname(first), os.path.dirname(second)}, {self.here(".turn")})


# Names a layout is made of: folders and files, some named as the result or as turn's folder, and
# some only beginning like the result.
NAMES = st.sampled_from(["a", "b", "r.json", ".turn", "r.json.x", "r.jsonx"])


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
        # Given: any layout of files and folders in a repository, the result at any depth, a run's
        # state in turn's folder at the root, and any paths that are there in it
        # When: the paths are given without the run's files
        # Then: they reach every file and folder the paths reached but the result, turn's folder
        # at the root and what is in it, and the folders opened on the way to the result's folder;
        # and none of them is such a folder. What the paths reach is found here by walking the
        # layout, apart from how without_run_files opens folders, so the two cannot share a slip.
        place = tempfile.mkdtemp(dir=self.base)
        os.chdir(place)
        try:
            os.mkdir(".git")
            result = os.path.join(*down, "r.json")
            for path in (result, ".turn/20261025-r.json/run.json"):
                self.write(path, "")
            for names in files:
                try:
                    self.write(os.path.join(*names), "")
                except OSError:
                    pass
            asked = [os.path.join(".", *p) for p in paths if os.path.exists(os.path.join(".", *p))]
            folder = os.path.realpath(os.path.dirname(result) or ".")
            ours = {os.path.realpath(result), os.path.realpath(".turn")}
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
