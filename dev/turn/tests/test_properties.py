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

from helpers import RepoTest, forms, records, run, shell

call = run.call

# Hypothesis fixes its inputs where the CI variable is set; here they are new on every run, CI
# included, and a failure prints the input that made it.
settings.register_profile("ci", derandomize=False, deadline=None, database=None, print_blob=True)
settings.load_profile("ci" if os.environ.get("CI") else "default")

FORMS = (
    forms.CHECK,
    forms.DECISION,
    forms.CLAIM,
    forms.GOOD,
    forms.FIRST_READING,
    forms.LEARNT,
)
ITEMS = [{"checklist": "checklists/readme.md", "item": "F-1"}]
# JSON values of any shape, with the keys the forms look for among others.
KEYS = st.sampled_from(
    ["items", "questions", "checklist", "item", "good", "lines", "question", "gets", "can"]
    + ["process", "role", "lesson", "grounds", "record", "quote", "checked", "recommended"]
    + ["parts", "part", "places", "did", "lacking"]
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
        # When: the hooks read its words, and the paths it names, writes and prints whole
        # Then: they read it without breaking, each path whole
        self.assertIsInstance(shell.words(command), list)
        for paths in (shell.named, shell.written, shell.printed):
            self.assertTrue(all(os.path.isabs(p) for p in paths(command, "/r")))

    @given(st.lists(NAMES, min_size=1, max_size=5))
    def test_cat_reads_each_file_it_names(self, names):
        # Given: files of any plain names
        # When: a command prints them with cat
        # Then: each is taken as read whole
        found = shell.printed("cat " + " ".join(names), "/r")
        self.assertEqual(found, [os.path.realpath(os.path.join("/r", n)) for n in names])
