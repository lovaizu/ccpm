"""Property-based tests: each behavior over a kind of input, checked on many inputs Hypothesis
makes, new on every run, CI included."""

import json
import os
import string
import unittest

# Hypothesis is installed on the newest Python alone, so the type check on 3.9 finds it missing.
try:
    from hypothesis import given, settings  # pyrefly: ignore[missing-import]
    from hypothesis import strategies as st  # pyrefly: ignore[missing-import]
except ImportError:
    raise unittest.SkipTest("Hypothesis runs on the newest Python alone") from None

from helpers import RepoTest, forms, read_in_given, read_whole, records, run

call = run.call

# Hypothesis fixes its inputs where the CI variable is set; here they are new on every run, CI
# included, and a failure prints the input that made it.
settings.register_profile("ci", derandomize=False, deadline=None, database=None, print_blob=True)
settings.load_profile("ci" if os.environ.get("CI") else "default")

FORMS = (forms.CHECK, forms.READING, forms.DECISION, forms.CLAIM, forms.GOOD, forms.LEARNT)
ITEMS = [{"checklist": "checklists/readme.md", "item": "F-1"}]
# JSON values of any shape, with the keys the forms look for among others.
KEYS = st.sampled_from(
    ["items", "questions", "checklist", "item", "good", "lines", "question", "gets", "can"]
    + ["learnt", "statements", "kind", "unsourced", "quotes", "ran", "path", "quote", "command"]
    + ["output", "process", "role", "lesson", "grounds", "record", "checked", "recommended"]
) | st.text(max_size=5)
LEAVES = st.none() | st.booleans() | st.integers() | st.text(max_size=20)
VALUES = st.recursive(
    LEAVES,
    lambda inner: st.lists(inner, max_size=4) | st.dictionaries(KEYS, inner, max_size=5),
    max_leaves=20,
)
NAMES = st.text(string.ascii_letters + string.digits + "._/", min_size=1, max_size=12).filter(
    lambda s: not s.startswith("-")
)


class TestForms(RepoTest):
    @given(VALUES, st.sampled_from(FORMS))
    def test_any_reply_is_told_what_is_wrong_and_never_breaks_the_run(self, value, form):
        # Given: a reply of any shape, as JSON
        # When: it is checked by any form
        # Then: what is wrong is said in words, and nothing else happens
        said = forms.check(json.dumps(value), ITEMS, ["README.md"], form)
        self.assertIsInstance(said, list)
        self.assertTrue(all(isinstance(s, str) and s for s in said))

    @given(st.dictionaries(KEYS, VALUES, max_size=4))
    def test_a_reply_in_a_json_fence_is_read_as_the_reply(self, value):
        # Given: a reply of any object
        # When: it is given inside a ```json fence
        # Then: it is read as if given bare
        text = json.dumps(value)
        fenced = f"```json\n{text}\n```"
        self.assertEqual(forms.parse(fenced, forms.GOOD), forms.parse(text, forms.GOOD))

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
    @given(st.lists(st.text(max_size=3000), max_size=30))
    def test_a_record_s_pages_together_show_it_whole(self, texts):
        # Given: a record of any number of entries of any text
        # When: it is split into pages
        # Then: the pages joined are the record as shown, and none is longer than a page
        path = os.path.join(self.repo, "record.jsonl")
        with open(path, "w", encoding="utf-8") as f:
            entries = ({"type": "user", "message": {"content": text}} for text in texts)
            f.writelines(json.dumps(e) + "\n" for e in entries)
        pages = records.pages(path)
        self.assertEqual("".join(pages), records.shown(path))
        self.assertTrue(all(len(p) <= records.PAGE for p in pages))


class TestCommands(unittest.TestCase):
    @given(st.text(max_size=200))
    def test_any_command_is_read_into_words(self, command):
        # Given: any command
        # When: the hooks read its words and the files it prints whole
        # Then: they read it without breaking
        event = {"tool_input": {"command": command}}
        self.assertIsInstance(read_in_given.words(event), list)
        self.assertIsInstance(read_whole.catted(command), list)

    @given(st.lists(NAMES, min_size=1, max_size=5))
    def test_cat_reads_each_file_it_names(self, names):
        # Given: files of any plain names
        # When: a command prints them with cat
        # Then: each is taken as read whole
        self.assertEqual(read_whole.catted("cat " + " ".join(names)), names)
