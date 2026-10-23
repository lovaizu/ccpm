"""Property-based tests: each behavior over a kind of input, checked on many inputs Hypothesis
makes, new on every run, CI included."""

import json
import os
import shutil
import tempfile
import unittest

# Hypothesis is installed on the newest Python alone, so the type check on 3.9 finds it missing.
try:
    from hypothesis import given  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]
except ImportError:
    raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None

from helpers import CALL, CAN, QUESTION, RESULT, WAITS, RepoTest, forms, records, run, testing

call = run.call

testing.load_hypothesis_profile()

FORMS = (forms.CHECK, forms.CLAIM, forms.FIRST_READING, forms.HELD, forms.LEFT, forms.LEARNT)
ITEMS = [{"checklist": "checklists/readme.md", "item": "F-1"}]
# JSON values of any shape, with the keys the forms look for among others.
KEYS = st.sampled_from(
    ["items", "questions", "checklist", "item", "good", "lines", "question", "can", "holds"]
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
        keys = [(i["checklist"], i["item"]) for i in ITEMS] if each else []
        said = forms.check(json.dumps(value), ITEMS, ["README.md"], form, each=keys)
        self.assertIsInstance(said, list)
        self.assertTrue(all(isinstance(s, str) and s for s in said))

    @given(st.lists(st.sampled_from(["# t", "## h", "### s", "```", "x", ""]), max_size=30))
    def test_a_document_s_parts_take_every_line_once_in_order(self, lines):
        # Given: a document of any lines of headings, fences and text
        # When: it is split into its parts
        # Then: the parts run from its first line to its last, each starting where the one before
        # ends, and each but the first opens at a top heading
        self.write("README.md", "".join(line + "\n" for line in lines))
        spans = [forms.span(p)[1:] for p in forms.parts(["README.md"])]
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
        self.assertEqual(forms.parse(fenced, forms.CLAIM), forms.parse(text, forms.CLAIM))

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


class TestRecords(RepoTest):
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


class TestAnswer(RepoTest):
    @given(st.text(max_size=200))
    def test_any_answer_of_words_is_kept_as_it_came(self, answer):
        # Given: a run whose check asked a question, started anew for each answer
        # When: the calling AI's answer, any text, is handed on
        # Then: an answer of words is kept as it came, the blanks at its ends aside; one of blanks
        # alone is asked for again, and the run still waits on it
        if os.path.exists(run.state_path(RESULT)):
            os.remove(run.state_path(RESULT))
        self.turn("start", json.dumps(CALL))
        self.next()
        self.next({"items": [CAN[0], WAITS], "questions": [QUESTION]})
        self.next()
        code, _ = self.turn("next", RESULT, stdin=answer)
        kept = self.state()
        if answer.strip():
            self.assertEqual((code, kept["answers"][-1]["answer"]), (0, answer.strip()))
        else:
            self.assertEqual((code, "asked" in kept), (1, True))


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
        # such a folder
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
            given_now = run.without_run_files(asked, result)
            self.assertEqual(reached(given_now), kept)
            self.assertFalse({os.path.realpath(p) for p in given_now} & on_way)
        finally:
            os.chdir(self.base)
            shutil.rmtree(place)
