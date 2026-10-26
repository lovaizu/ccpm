"""turn's adapter of lane's items port, turn's one reading of a checklist's items, which every_item
counts and call.py takes, each item a heading `### <ID>: <title>` outside a code fence, where lane's
own reading takes list items; run as the guard runs it, through lane's port, which holds what it
gives to the port's JSON."""

import contextlib
import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from unittest import mock

from helpers import CHECKLIST, TURN, checklist_items, testing

(ports,) = testing.lane_code(TURN, "ports")

ADAPTER = os.path.join(TURN, "hooks", "adapters", "items-checklist.py")


def items(text, path="checklists/readme.md"):
    """The IDs the adapter gives for the text of the checklist at the path."""
    return ports.run(ADAPTER, "items", {"input": path, "text": text}, TURN, ports.TIME)["items"]


class TestItems(unittest.TestCase):
    def test_an_item_heading_gives_its_id(self):
        # Given: a checklist of one item, its heading `### B-1: <title>`
        # When: the adapter reads it
        # Then: it gives the item's ID
        self.assertEqual(items("### B-1: Who it is for\n\nScope: its part\n"), ["B-1"])

    def test_each_item_is_read_with_the_line_its_heading_stands_on(self):
        # Given: a checklist with frontmatter, a fence holding a heading, and two items
        text = "---\nname: readme\n---\n```\n### B-7: x\n```\n### F-1: Shape\n\n### B-1: Who\n"
        # When: the adapter's reading is given it
        # Then: it gives each item by the line of its heading, counted from 1, and its ID
        self.assertEqual(checklist_items.items(text), [(7, "F-1"), (9, "B-1")])

    def test_the_items_under_format_and_benefit_are_given_in_order(self):
        # Given: a checklist with frontmatter, an item under Format and one under Benefit
        # When: the adapter reads it
        # Then: it gives both IDs, in the order they stand
        self.assertEqual(items(CHECKLIST), ["F-1", "B-1"])

    def test_a_heading_in_the_frontmatter_is_not_an_item(self):
        # Given: frontmatter holding a line written as an item heading, and an item after it
        text = "---\nname: readme\n### B-7: Kept out\n---\n### B-1: After\n"
        # When: the adapter reads it
        # Then: it gives the item after the frontmatter alone
        self.assertEqual(items(text), ["B-1"])

    def test_frontmatter_never_closed_is_read_as_text(self):
        # Given: a text opening with the frontmatter's mark and never closing it, an item after
        text = "---\nname: readme\n### B-1: Read\n"
        # When: the adapter reads it
        # Then: it gives the item, as turn reads a checklist whose frontmatter is not closed
        self.assertEqual(items(text), ["B-1"])

    def test_frontmatter_closed_on_its_second_line_ends_there(self):
        # Given: frontmatter of no key, closed on the line after it opens, an item, and a rule of
        # the frontmatter's mark after the item
        text = "---\n---\n### B-1: After\n---\n"
        # When: the adapter reads it
        # Then: it gives the item, the frontmatter ending at its own close
        self.assertEqual(items(text), ["B-1"])

    def test_a_mark_after_the_first_line_opens_no_frontmatter(self):
        for first in ("# Plan", "Plan"):
            with self.subTest(first=first):
                # Given: a text opening with a title, or with a word, an item, and a rule of the
                # frontmatter's mark after it
                text = f"{first}\n### B-1: Before\n---\n"
                # When: the adapter reads it
                # Then: it gives the item, as the text opens with no frontmatter
                self.assertEqual(items(text), ["B-1"])

    def test_a_heading_of_another_level_is_not_an_item(self):
        # Given: headings written as items are, at the level above an item's and the level below
        text = "## B-8: Above\n\n#### B-9: Below\n"
        # When: the adapter reads them
        # Then: it gives nothing
        self.assertEqual(items(text), [])

    def test_an_item_heading_in_a_fence_is_not_an_item(self):
        for fence in ("```", "~~~", "   ```", "````"):
            with self.subTest(fence=fence):
                # Given: an item heading inside a fence of backticks, of tildes, indented or
                # longer, and one after the fence closes
                text = f"{fence}markdown\n### B-7: <Item name>\n{fence}\n\n### B-1: After\n"
                # When: the adapter reads it
                # Then: it gives the item after the fence alone
                self.assertEqual(items(text), ["B-1"])

    def test_a_fence_closes_only_on_its_own_mark_at_its_length_or_more(self):
        for text in (
            "````\n```\n~~~~\n### B-7: Inside\n````\n### B-1: After\n",
            "~~~\n```\n### B-7: Inside\n~~~\n### B-1: After\n",
            "```\n~~~\n### B-7: Inside\n```\n### B-1: After\n",
            "```\n### B-7: Inside\n`````\n### B-1: After\n",
        ):
            with self.subTest(text=text):
                # Given: a fence of four backticks with a line of three inside it and one of
                # tildes, a fence of tildes with a line of backticks inside it, one of backticks
                # with a line of tildes, or one of three backticks closed by five; an item heading
                # inside, and one after the fence closes
                # When: the adapter reads it
                # Then: the fence holds until its own close, and only the item after it is given
                self.assertEqual(items(text), ["B-1"])

    def test_a_heading_with_no_id_is_not_an_item(self):
        # Given: headings of an item's level with no ID, an ID in small letters, an ID with no
        # hyphen, one with no colon after it, and one with no blank after the marks
        text = "### Notes\n### b-1: Small\n### B1: Joined\n### B-1 Title\n###B-2: Close\n"
        # When: the adapter reads them
        # Then: it gives nothing
        self.assertEqual(items(text), [])

    def test_an_indented_heading_or_one_with_closing_marks_is_an_item(self):
        # Given: an item heading indented by three blanks, and one closed by marks
        text = "   ### B-3: Indented\n### B-4: Closed ###\n"
        # When: the adapter reads them
        # Then: it gives both IDs
        self.assertEqual(items(text), ["B-3", "B-4"])

    def test_a_text_with_no_item_heading_gives_nothing(self):
        for text in ("", "# Plan\n\nSome words.\n\n- B-1: a list item\n"):
            with self.subTest(text=text):
                # Given: an empty text, or one of a title, words and a list item with an ID, the
                # form lane's own reading takes
                # When: the adapter reads it
                # Then: it gives nothing
                self.assertEqual(items(text), [])

    def test_the_adapter_reads_by_turns_items_before_a_module_of_the_same_name(self):
        # Given: a module named items, found first on sys.path, none yet imported, and the adapter
        # run as a script in this process, as lane runs it, with turn's folder as
        # CLAUDE_PLUGIN_ROOT, given a checklist of one item on stdin
        out = io.StringIO()
        with tempfile.TemporaryDirectory() as shadow:
            with open(os.path.join(shadow, "items.py"), "w", encoding="utf-8") as f:
                f.write("raise ImportError('not turn')\n")
            given = io.StringIO(json.dumps({"input": "c.md", "text": "### B-1: x\n"}))
            path = mock.patch.object(sys, "path", [shadow, *sys.path])
            modules = mock.patch.dict(sys.modules)
            root = mock.patch.dict(os.environ, {"CLAUDE_PLUGIN_ROOT": TURN})
            with path, modules, root, mock.patch.object(sys, "stdin", given):
                sys.modules.pop("items", None)
                with contextlib.redirect_stdout(out):
                    # When: the adapter is run
                    runpy.run_path(ADAPTER, run_name="__main__")
        # Then: it reads the checklist by turn's items.py, printing its item
        self.assertEqual(json.loads(out.getvalue()), {"items": ["B-1"]})

    def test_the_adapter_gives_each_of_its_cases(self):
        # Given: the cases kept beside the adapter, which lane's layer runs it on
        with open(os.path.splitext(ADAPTER)[0] + ".json", encoding="utf-8") as f:
            cases = json.load(f)
        for number, case in enumerate(cases, 1):
            with self.subTest(case=number):
                # When: the adapter is given the case
                # Then: it gives what the case gives
                self.assertEqual(
                    ports.run(ADAPTER, "items", case["given"], TURN, ports.TIME), case["gives"]
                )


if __name__ == "__main__":
    unittest.main()
