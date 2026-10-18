import copy
import json
import os
import runpy
import sys
from unittest import mock

from helpers import CALL, CCS, SCRIPTS, RepoTest

USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py next <result> [< <your reading or decision as JSON>]\n"
    "       turn.py given <result>"
)


def call_with(**change):
    call = copy.deepcopy(CALL)
    for key, value in change.items():
        if key in call["kind"] or key in ("use", "opens"):
            if value is None:
                del call["kind"][key]
            else:
                call["kind"][key] = value
        elif value is None:
            del call[key]
        else:
            call[key] = value
    return call


class TestUsage(RepoTest):
    def test_an_unknown_command_or_a_wrong_count_of_arguments_prints_the_usage(self):
        # Given: turn's script run with no command, an unknown one, or a command short of its
        # arguments
        # When: it is run
        # Then: it prints the usage, which names every command with its arguments, and stops
        for argv in [[], ["go"], ["start"], ["next"], ["given"], ["start", "{}", "x"]]:
            with self.subTest(argv=argv):
                self.assertEqual(self.turn(*argv), (1, USAGE + "\n"))

    def test_the_script_runs_from_the_shell(self):
        # Given: the orchestrator runs the script by its path, as its steps say
        # When: it is run with no command
        # Then: it exits with the usage's code
        with mock.patch.object(sys, "argv", ["turn.py"]), self.assertRaises(SystemExit) as end:
            runpy.run_path(os.path.join(SCRIPTS, "turn.py"), run_name="__main__")
        self.assertEqual(end.exception.code, 1)


class TestStart(RepoTest):
    def test_a_call_whose_kinds_all_have_entries_starts_the_run(self):
        # Given: a call naming the CCS, the kinds of the work, the checklist and the receiver, and
        # where the result goes
        # When: the run is started
        # Then: the generator is to be started with where the run is kept alone, and is given
        # the CCS and the work, with nothing sent back yet
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual((code, json.loads(out)["agent"]), (0, "turn:generator"))
        self.assertEqual(json.loads(json.loads(out)["prompt"]), {"run": CALL["result"]})
        self.assertEqual(
            self.given(),
            {
                "ccs": CALL["ccs"],
                "work": ["README.md"],
                "sent_back": [],
                "learnt": [],
            },
        )

    def test_the_run_keeps_every_item_of_every_checklist(self):
        # Given: a checklist with an item under Format and one under Benefit
        # When: the run is started
        # Then: the run keeps both items, each by its checklist and its ID
        self.started()
        running = self.read_json(CALL["result"])["running"]
        self.assertEqual(
            running["items"],
            [
                {"checklist": "checklists/readme.md", "item": "F-1"},
                {"checklist": "checklists/readme.md", "item": "B-1"},
            ],
        )

    def test_the_run_keeps_what_the_roles_may_read(self):
        # Given: a CCS whose entries name existing files, and text that names none
        # When: the run is started
        # Then: the run keeps the CCS, each file its entries name and the work as what may be read
        self.started()
        running = self.read_json(CALL["result"])["running"]
        self.assertEqual(
            running["given"],
            [
                ".tasks/readme.json",
                "README.md",
                "checklists/readme.md",
                "notes/readme.decisions.md",
                "docs/start.md",
            ],
        )

    def test_the_run_keeps_what_the_readers_may_read(self):
        # Given: a call naming the kind of what the receiver opens
        # When: the run is started
        # Then: the run keeps the work, what the receiver opens and the checklists as what the
        # first user and the evaluator may read, and not the CCS or the decisions
        self.started(call_with(opens="page"))
        running = self.read_json(CALL["result"])["running"]
        self.assertEqual(running["shown"], ["README.md", "docs/start.md", "checklists/readme.md"])

    def test_the_optional_kinds_are_taken_when_named(self):
        # Given: a call that also names the kinds of the use and of what the receiver opens
        # When: the run is started
        # Then: the run keeps each kind's entries
        call = call_with(use="purpose", opens="page")
        self.started(call)
        running = self.read_json(CALL["result"])["running"]
        self.assertEqual(running["use"], ["to try it on their own files"])
        self.assertEqual(running["opens"], ["docs/start.md"])

    def test_a_result_in_a_new_folder_is_written(self):
        # Given: a call whose result goes in a folder not yet there
        # When: the run is started
        # Then: the folder is made and the run kept there
        self.started(call_with(result="out/new/result.json"))
        self.assertIn("running", self.read_json("out/new/result.json"))


class TestStartStops(RepoTest):
    def stops(self, call, *said):
        code, out = self.turn("start", call if isinstance(call, str) else json.dumps(call))
        self.assertEqual(code, 1)
        for words in said:
            self.assertIn(words, out)
        self.assertFalse(os.path.exists(CALL["result"]))

    def test_a_call_that_is_not_json_stops(self):
        # Given: a call that is not JSON
        # When: the run is started
        # Then: it stops, saying the call is not JSON and the shape to give
        self.stops("ccs: x", "the call is not JSON", '{"ccs": "<path>"')

    def test_a_call_without_ccs_or_result_stops(self):
        # Given: a call missing where the CCS is, or where the result goes
        # When: the run is started
        # Then: it stops, naming what is missing
        for key in ("ccs", "result", "kind"):
            with self.subTest(key=key):
                self.stops(call_with(**{key: None}), f'"{key}"')

    def test_a_call_with_an_unknown_key_stops(self):
        # Given: a call with a key turn does not take, at the top or among the kinds
        # When: the run is started
        # Then: it stops, naming the key and those turn takes
        self.stops(dict(CALL, out="x.json"), '"out"', '"ccs", "kind" and "result"')
        call = copy.deepcopy(CALL)
        call["kind"]["reader"] = "audience"
        self.stops(call, '"reader"', '"receiver"')

    def test_a_call_without_a_required_kind_stops(self):
        # Given: a call that leaves out the kind of the work, the checklist or the receiver
        # When: the run is started
        # Then: it stops, naming the kind to give
        for kind in ("work", "checklist", "receiver"):
            with self.subTest(kind=kind):
                self.stops(call_with(**{kind: None}), f'"{kind}"')

    def test_a_required_kind_without_an_entry_stops(self):
        # Given: a call naming a kind the CCS has no entry of
        # When: the run is started
        # Then: it stops, naming the kind and the CCS
        self.stops(call_with(receiver="reader"), '"reader"', CALL["ccs"])

    def test_a_ccs_that_is_missing_or_not_a_ccs_stops(self):
        # Given: a CCS that is not there, not JSON, or not parts of entries of one kind each
        # When: the run is started
        # Then: it stops, saying what the CCS must be
        bad = {
            "missing.json": None,
            "text.json": "not json",
            "list.json": "[]",
            "part.json": json.dumps({"focal_entities": {"deliverable": "README.md"}}),
            "entry.json": json.dumps({"focal_entities": [{"a": "x", "b": "y"}]}),
            "value.json": json.dumps({"focal_entities": [{"deliverable": 3}]}),
        }
        for name, text in bad.items():
            with self.subTest(name=name):
                if text is not None:
                    self.write(name, text)
                self.stops(call_with(ccs=name), name)

    def test_a_checklist_that_is_missing_or_has_no_items_stops(self):
        # Given: a CCS naming a checklist that is not there, or one with no items
        # When: the run is started
        # Then: it stops, naming the checklist
        for text in (None, "# Nothing\n"):
            with self.subTest(text=text):
                ccs = copy.deepcopy(CCS)
                ccs["retrieved_artifacts"][0] = {"checklist": "checklists/other.md"}
                if text is not None:
                    self.write("checklists/other.md", text)
                self.write_json(CALL["ccs"], ccs)
                self.stops(CALL, "checklists/other.md")

    def test_a_file_the_receiver_opens_that_is_missing_stops(self):
        # Given: a call naming the kind of what the receiver opens, whose file is not there
        # When: the run is started
        # Then: it stops, naming the file
        os.remove("docs/start.md")
        self.stops(call_with(opens="page"), "docs/start.md")

    def test_kinds_that_are_not_an_object_stop(self):
        # Given: a call whose kinds are a list, not an object of names
        # When: the run is started
        # Then: it stops, giving the shape of the call
        self.stops(dict(CALL, kind=["deliverable"]), '"kind" is not an object', '{"ccs"')

    def test_a_kind_that_is_not_a_name_stops(self):
        # Given: a call whose kind is not a word but a list
        # When: the run is started
        # Then: it stops, saying a kind is a name
        self.stops(call_with(work=["deliverable"]), '"work"')
