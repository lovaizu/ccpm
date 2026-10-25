"""The adapters a proposal names, as the layer takes them: each found beside the proposal, in the
folder it is in, or laid before in the plugin, run on each of its cases before anything is printed or
written, shown in the print, and written into the plugin with the lanes once approved, its copies
beside the proposal then removed."""

from __future__ import annotations

import json
import os

import helpers
from laying import AGAIN, LayTest

# An adapter of the items port reading a checklist's items as its headings, `### <ID>: <title>`,
# its path in the plugin, and the cases it must give: one of each form and one that gives nothing.
HEADINGS = """import json, re, sys
given = json.load(sys.stdin)
print(json.dumps({"items": re.findall(r"^### ([A-Z]+-[0-9]+):", given["text"], re.M)}))
"""
PATH = "hooks/adapters/items-headings.py"
CASES = [
    {
        "given": {"input": "c.md", "text": "### B-1: one\n### B-2: two\n"},
        "gives": {"items": ["B-1", "B-2"]},
    },
    {"given": {"input": "c.md", "text": "No items.\n"}, "gives": {"items": []}},
]
# every_item on step 3 reading its checklist by the adapter.
EVERY = {"lane": "every_item", "takes": ["checklist.md"], "adapter": PATH}


class AdapterTest(LayTest):
    """A proposal of every_item on step 3 of changelog-writer, read by the adapter beside the
    proposal, in `<plugin>/adapters/` of the folder it is in, with its cases."""

    def setUp(self) -> None:
        super().setUp()
        self.beside = os.path.join(self.base, "data", "notes", "adapters")
        self.adapter(HEADINGS, CASES)
        self.propose(self.proposal([EVERY]))

    def adapter(self, text: str | None, cases: object, where: str = "") -> None:
        """Writes the adapter of the text and its cases, as JSON where they are not text, beside the
        proposal, or in the folder given; none of either that is None."""
        folder = where or self.beside
        if text is not None:
            self.write(os.path.join(folder, "items-headings.py"), text)
        if cases is not None:
            given = cases if isinstance(cases, str) else json.dumps(cases)
            self.write(os.path.join(folder, "items-headings.json"), given)


class TestPrint(AdapterTest):
    def test_the_adapter_is_shown_beside_its_lane_and_with_its_text_and_cases(self):
        # Given: the proposal and its adapter
        # When: it is printed
        code, said = self.lay("print", self.proposal_file)
        # Then: the lane's hook names the adapter, and the adapter is shown, its text and cases
        self.assertEqual(code, 0)
        self.assertIn(f"hook every_item, adapter {PATH}\n", said)
        self.assertIn(
            f"Adapter {PATH} of the items port, for every_item on step 3 of changelog-writer,"
            " giving each case below:\n    import json, re, sys\n",
            said,
        )
        self.assertIn('  case 2: given {"input": "c.md", "text": "No items.\\n"}\n', said)
        self.assertTrue(said.endswith('    gives {"items": []}\n'), said)


class TestCases(AdapterTest):
    def test_an_adapter_or_its_cases_not_as_lane_reads_them_stop_before_anything(self):
        wrong = {
            "no adapter": (None, CASES, "which is neither"),
            "no cases": (HEADINGS, None, "gives the adapter no cases"),
            "cases of no JSON": (HEADINGS, "[", "gives the adapter no cases"),
            "an empty list": (HEADINGS, [], "gives the adapter no cases"),
            "a case out of the port": (
                HEADINGS,
                [CASES[0], {"given": {"input": "c.md"}, "gives": {"items": []}}],
                ' is out of the items port at $.given: expected the key "text"',
            ),
            "a case it does not give": (
                HEADINGS,
                [
                    CASES[0],
                    {"given": {"input": "c.md", "text": "### B-1: x\n"}, "gives": {"items": []}},
                ],
                "given case 2 of",
            ),
            "an adapter failing": (
                "import sys\nsys.exit('broken')\n",
                CASES,
                "exited 1: broken, where the case gives",
            ),
        }
        for what, (text, cases, named) in wrong.items():
            with self.subTest(what=what):
                # Given: the adapter or its cases missing, not as lane reads them, or an adapter
                # giving on a case other than the case gives
                for name in ("items-headings.py", "items-headings.json"):
                    if os.path.exists(os.path.join(self.beside, name)):
                        os.remove(os.path.join(self.beside, name))
                self.adapter(text, cases)
                for action in ("print", "write"):
                    # When: the proposal is printed or written
                    code, said = self.lay(action, self.proposal_file)
                    # Then: it exits 1 saying what is wrong and what to do, nothing written
                    self.assertEqual(code, 1)
                    self.assertIn(named, said)
                    self.assertIn("run again", said)
                    if what == "a case out of the port":
                        self.assertIn("case 2 of", said)
                    if what == "a case it does not give":
                        expected = 'gave {"items": ["B-1"]}, where the case gives {"items": []}'
                        self.assertIn(expected, said)
                self.assertEqual(self.read(self.agent_file), helpers.STEPS)

    def test_an_adapter_named_out_of_its_lanes_port_stops(self):
        for lane, named in (
            ({**EVERY, "adapter": "hooks/adapters/move-x.py"}, "not hooks/adapters/items-"),
            ({**EVERY, "adapter": 1}, "`1`, not hooks/adapters/items-"),
            (
                {"lane": "hands_off", "takes": ["git push"], "adapter": PATH},
                "names an adapter for hands_off on step 3 of changelog-writer",
            ),
        ):
            with self.subTest(lane=lane):
                # Given: an adapter named as another port's, by no path, or for a lane reading none
                self.propose(self.proposal([lane]))
                # When: the proposal is printed
                code, said = self.lay("print", self.proposal_file)
                # Then: it exits 1 saying so and to write it again
                self.assertEqual(code, 1)
                self.assertIn(named, said)
                self.assertTrue(said.endswith(f"; {AGAIN}.\n"), said)

    def test_a_values_adapter_named_out_of_its_port_stops(self):
        # Given: a subagent naming an adapter of another port for its values
        given = self.proposal([EVERY])
        given["subagents"][0]["adapter"] = PATH
        self.propose(given)
        # When: the proposal is printed
        code, said = self.lay("print", self.proposal_file)
        # Then: it exits 1 saying so
        self.assertEqual(code, 1)
        self.assertIn("names an adapter for the values of changelog-writer", said)


class TestWrite(AdapterTest):
    def test_the_adapter_is_written_with_the_lanes_and_its_copies_beside_removed(self):
        # Given: the proposal and its adapter beside it, and a values adapter laid before in the
        # plugin, for the subagent
        given = self.proposal([EVERY])
        given["subagents"][0]["adapter"] = "hooks/adapters/values-words.py"
        self.propose(given)
        words = os.path.join(self.plugin, "hooks", "adapters")
        self.write(os.path.join(words, "values-words.py"), "print('{\"values\": {}}')\n")
        cases = [{"given": {"texts": ["x"]}, "gives": {"values": {}}}]
        self.write_json(os.path.join(words, "values-words.json"), cases)
        # When: it is written
        code, said = self.lay("write", self.proposal_file)
        # Then: the adapter and its cases are in the plugin's hooks/adapters/, hooks/lanes.json
        # names each, the copies beside the proposal and their folders are gone, and it is said
        self.assertEqual(code, 0, said)
        self.assertEqual(self.read(os.path.join(self.plugin, PATH)), HEADINGS)
        self.assertEqual(self.read_json(os.path.join(words, "items-headings.json")), CASES)
        [agent] = self.laid()["subagents"]
        self.assertEqual(agent["adapter"], "hooks/adapters/values-words.py")
        self.assertEqual(agent["steps"][0]["lanes"], [EVERY])
        self.assertFalse(os.path.exists(os.path.join(self.base, "data", "notes")))
        self.assertIn(f"Wrote the adapter {PATH} with its cases.\n", said)
        self.assertIn(f"Removed the adapter {self.beside}/items-headings.py", said)
        # And: laid again from the plugin, the adapters are kept and found there
        self.propose(given)
        self.assertEqual(self.lay("print", self.proposal_file)[0], 0)
        self.lay("write", self.proposal_file)
        self.assertTrue(os.path.isfile(os.path.join(self.plugin, PATH)))

    def test_the_adapters_folder_holding_more_is_kept(self):
        # Given: another file beside the adapter, in the adapters' folder beside the proposal
        self.write(os.path.join(self.beside, "other.txt"), "x")
        # When: the proposal is written
        self.lay("write", self.proposal_file)
        # Then: that file and its folder are kept, the adapter's copies gone
        self.assertEqual(os.listdir(self.beside), ["other.txt"])

    def test_up_keeps_the_adapters_and_says_the_values_adapter_laid_before(self):
        # Given: the proposal written, its subagent naming a values adapter
        given = self.proposal([EVERY])
        given["subagents"][0]["adapter"] = "hooks/adapters/values-words.py"
        self.propose(given)
        words = os.path.join(self.plugin, "hooks", "adapters")
        self.write(os.path.join(words, "values-words.py"), "print('{\"values\": {}}')\n")
        cases = [{"given": {"texts": ["x"]}, "gives": {"values": {}}}]
        self.write_json(os.path.join(words, "values-words.json"), cases)
        self.lay("write", self.proposal_file)
        laid = self.laid()
        # When: the plugin is brought up
        code, said = self.lay("up", self.plugin)
        # Then: the lanes laid and the adapters are kept, and the values adapter is said
        self.assertEqual(code, 0)
        self.assertEqual(self.laid(), laid)
        self.assertTrue(os.path.isfile(os.path.join(self.plugin, PATH)))
        self.assertIn(
            'Laid before in changelog-writer, its values read by: {"adapter":'
            ' "hooks/adapters/values-words.py"}\n',
            said,
        )
