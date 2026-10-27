"""turn.py run from the shell and the call it starts the run on: the usage, the run started, and
each call turn cannot take stopped with what to give instead."""

import contextlib
import copy
import io
import json
import os
import runpy
import subprocess
import sys
import unittest
from unittest import mock

from helpers import (
    CALL,
    CCS,
    CHECKLIST,
    EACH,
    EACH_ITEM,
    ITEMS,
    RUN,
    SCRIPTS,
    TODAY,
    RepoTest,
)

# The usage written out as the user is to read it, not taken from turn.py, so a change to it in
# turn.py by mistake fails the tests; the duplicate-code check leaves it out, as the user chose.
# pylint: disable=duplicate-code
USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py next <result> [< <the agent ID as JSON, your questions as JSON, or the answer"
    " as it came>]\n"
    "       turn.py next <result> <page>\n"
    "       turn.py questions <result>\n"
    "       turn.py parts <result>"
)
# pylint: enable=duplicate-code


def call_with(**change):
    """The run's call with each key or kind changed to the value given, or left out for None."""
    call = copy.deepcopy(CALL)
    for key, value in change.items():
        if key in call["kind"]:
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
        # Each command also with one argument too many, and words sorting before and after every
        # command with as many arguments as a command takes.
        for argv in [
            [],
            ["go"],
            ["aaa", "r"],
            ["zzz", "r"],
            ["aaa", "r", "1"],
            ["aaa", "r", "1", "1"],
            ["zzz", "r", "1", "1"],
            ["start"],
            ["start", "{}", "x"],
            ["next"],
            ["next", "r", "1", "x"],
            ["questions"],
            ["questions", "r", "x"],
            ["parts"],
            ["parts", "r", "x"],
        ]:
            with self.subTest(argv=argv):
                self.assertEqual(self.turn(*argv), (1, USAGE + "\n"))

    def test_the_script_finds_its_own_modules_before_any_of_the_same_name(self):
        # Given: a folder on PYTHONPATH holding a module named as one of turn's scripts, which
        # breaks when imported
        # When: the orchestrator runs the script by its path from the shell, with no command
        # Then: it prints the usage, as its own modules are found first
        self.write("elsewhere/run.py", "raise SystemExit('not turn')\n")
        done = subprocess.run(
            [sys.executable, os.path.join(SCRIPTS, "turn.py")],
            check=False,
            env=dict(os.environ, PYTHONPATH="elsewhere"),
            capture_output=True,
            text=True,
        )
        self.assertEqual((done.returncode, done.stdout), (1, USAGE + "\n"))

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        # Given: no run going
        # When: the orchestrator runs the script by its path with a command and its argument
        # Then: the command is run on that argument, and stops on the run not going
        out = io.StringIO()
        argv = ["turn.py", "parts", "none.json"]
        with (
            mock.patch.object(sys, "argv", argv),
            contextlib.redirect_stdout(out),
            self.assertRaises(SystemExit) as end,
        ):
            runpy.run_path(os.path.join(SCRIPTS, "turn.py"), run_name="__main__")
        self.assertEqual(end.exception.code, 1)
        self.assertIn("no run is going with its result at none.json", out.getvalue())

    def test_what_is_printed_keeps_letters_beyond_ascii_as_they_are(self):
        # Given: a call whose checklist, work and result are named in Japanese
        # When: the run is started, its generator told and started
        # Then: each is printed with the names as they are written
        os.rename("checklists/readme.md", "checklists/読む.md")
        ccs = dict(CCS, retrieved_artifacts=[{"checklist": "checklists/読む.md"}, {"page": "docs"}])
        ccs["focal_entities"] = [{"deliverable": "はじめに.md"}, CCS["focal_entities"][1]]
        self.write_json(CALL["ccs"], ccs)
        result = ".tasks/結果.json"
        call = dict(CALL, result=result)
        code, out = self.turn("start", json.dumps(call))
        self.assertEqual(code, 0, out)
        self.assertIn("結果.json", out)
        with open(f".turn/{TODAY}-.tasks%2F結果.json/run.json", encoding="utf-8") as kept:
            self.assertIn("checklists/読む.md", kept.read())
        code, out = self.turn("next", result)
        self.assertEqual(code, 0, out)
        self.assertIn("はじめに.md", out)
        code, out = self.turn("next", result)
        self.assertEqual(code, 0, out)
        self.assertIn("checklists/読む.md", out)
        self.write("はじめに.md", "# 始め\n")
        code, out = self.turn("parts", result)
        self.assertEqual(code, 0, out)
        self.assertIn("はじめに.md:1-1", out)


class TestStart(RepoTest):
    def test_a_call_whose_kinds_all_have_entries_starts_the_run(self):
        # Given: a call naming the CCS, the kinds of the work, the checklist and the receiver, and
        # where the result goes
        # When: the run is started
        # Then: it prints where the result goes alone, as a whole path, and the generator is due
        # first, as it asks first what only the user can decide
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual((code, json.loads(out)), (0, {"result": self.here(CALL["result"])}))
        self.assertEqual(self.state()["next"]["agent"], "turn:generator")

    def test_a_run_started_starts_the_generator(self):
        # Given: a run started
        # When: the orchestrator goes on, and on once the line is sent
        # Then: the generator is to be started with its prompt as the flow keeps it
        move = self.started()
        self.assertEqual(move["input"]["subagent_type"], "turn:generator")
        self.assertEqual(json.loads(move["input"]["prompt"]), self.prompt())

    def test_the_run_keeps_every_item_of_every_checklist(self):
        # Given: a checklist with an item under Format and one under Benefit
        # When: the run is started
        # Then: the run keeps both items, each by its checklist and its ID
        self.started()
        running = self.state()
        self.assertEqual(
            running["items"],
            ITEMS,
        )

    def test_the_run_keeps_the_items_asked_of_each_part(self):
        # Given: a checklist with an item asked of each part, beside one of its part and one of
        # the whole
        # When: the run is started
        # Then: the run keeps the item asked of each part, by its checklist and ID, and only it
        self.write("checklists/readme.md", CHECKLIST + EACH)
        self.turn("start", json.dumps(CALL))
        running = self.state()
        self.assertEqual(running["each"], [EACH_ITEM])

    def test_the_run_keeps_what_the_roles_may_read(self):
        # Given: a CCS whose entries name existing files, and text that names none
        # When: the run is started
        # Then: the run keeps the CCS, each file its entries name and the work as what may be read
        self.started()
        running = self.state()
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
        # Given: a call naming the kind of what the receiver has
        # When: the run is started
        # Then: the run keeps the work, what the receiver has and the checklists as what the first
        # user may read, and not the CCS or the decisions
        self.turn("start", json.dumps(CALL))
        running = self.state()
        self.assertEqual(
            running["readable"], ["README.md", "docs/start.md", "checklists/readme.md"]
        )

    def test_the_use_and_what_the_receiver_has_are_taken(self):
        # Given: a call naming the kinds of the use and of what the receiver has
        # When: the run is started
        # Then: the run keeps each kind's entries
        self.turn("start", json.dumps(CALL))
        running = self.state()
        self.assertEqual(running["use"], ["to try it on their own files"])
        self.assertEqual(running["has"], ["docs/start.md"])

    def test_a_folder_the_receiver_has_is_taken(self):
        # Given: a CCS whose entry of what the receiver has names a folder, as the repository is
        # for a maintainer
        # When: the run is started
        # Then: the run keeps the folder as what the readers may read
        self.write_json(
            CALL["ccs"], dict(CCS, goal_orientation=CCS["goal_orientation"] + [{"page": "docs"}])
        )
        self.turn("start", json.dumps(CALL))
        running = self.state()
        self.assertEqual(running["has"], ["docs", "docs/start.md"])
        self.assertIn("docs", running["readable"])

    def test_a_folder_named_with_a_trailing_slash_is_kept_as_the_folder(self):
        # Given: a CCS naming a folder with a trailing slash, as a caller names a folder
        # When: the run is started
        # Then: the run keeps the folder without the slash, so the files inside it are found within
        # it, as what the readers and the roles may read
        self.write_json(
            CALL["ccs"], dict(CCS, goal_orientation=CCS["goal_orientation"] + [{"page": "docs/"}])
        )
        self.turn("start", json.dumps(CALL))
        running = self.state()
        self.assertEqual(running["has"], ["docs", "docs/start.md"])
        self.assertIn("docs", running["given"])
        self.assertNotIn("docs/", running["given"])

    def test_the_generator_is_given_the_calls_test_or_null(self):
        for test in ("make check", None):
            with self.subTest(test=test):
                # Given: a call whose test is a command, or null, the caller saying the work has
                # none
                # When: the run is started and checked
                self.started(dict(CALL, test=test))
                # Then: the generator is to start from the call's test as it was given
                self.assertEqual(self.prompt()["test"], test)
                os.remove(f"{RUN}/run.json")

    def test_a_call_again_with_another_test_is_another_call(self):
        # Given: a run started on a call whose test is a command
        self.turn("start", json.dumps(CALL))
        # When: turn is called again with the same call but its test null
        code, out = self.turn("start", json.dumps(dict(CALL, test=None)))
        # Then: it stops, saying a run of another call is kept at the result
        self.assertEqual(code, 1)
        self.assertIn("a run of another call is kept", out)

    def test_a_result_in_a_folder_not_yet_there_starts_its_run(self):
        # Given: a call whose result goes in a folder not yet there
        # When: the run is started and checked
        # Then: the run is kept in turn's folder at the root, named by the result's path from it,
        # and the generator is due
        move = self.started(call_with(result="out/new/result.json"))
        self.assertTrue(os.path.exists(f".turn/{TODAY}-out%2Fnew%2Fresult.json/run.json"))
        self.assertEqual(move["input"]["subagent_type"], "turn:generator")


class TestStartStops(RepoTest):
    def stops(self, call, *said):
        """The start of the call stops, saying each of the words, and starts no run."""
        code, out = self.turn("start", call if isinstance(call, str) else json.dumps(call))
        self.assertEqual(code, 1)
        for words in said:
            self.assertIn(words, out)
        # No run is started: neither the result nor the state is written.
        self.assertFalse(os.path.exists(CALL["result"]))
        self.assertFalse(os.path.exists(".turn"))

    def test_a_call_that_is_not_json_stops(self):
        # Given: a call that is not JSON
        # When: the run is started
        # Then: it stops, saying the call is not JSON and the shape to give
        self.stops("ccs: x", "the call is not JSON", '{"ccs": "<path>"')

    def test_a_call_without_ccs_kind_result_or_test_stops(self):
        # Given: a call missing where the CCS is, its kinds, where the result goes, or its test
        # When: the run is started
        # Then: it stops, naming what is missing
        for key in ("ccs", "result", "kind", "test"):
            with self.subTest(key=key):
                self.stops(call_with(**{key: None}), f'the call has no "{key}"')

    def test_a_call_whose_ccs_or_result_is_no_path_stops(self):
        # Given: a call whose CCS or result is no text, or empty
        # When: the run is started
        # Then: it stops, naming the key and the shape to give
        for key in ("ccs", "result"):
            for value in (5, ["x"], " "):
                with self.subTest(key=key, value=value):
                    self.stops(call_with(**{key: value}), f'"{key}" is not a path', '{"ccs"')

    def test_a_call_whose_test_is_empty_or_no_command_stops(self):
        # Given: a call whose test is an empty text, blanks alone, a number, a list of commands,
        # an object or true
        # When: the run is started
        # Then: it stops, saying the test is not a command and that null says there is none
        for value in ("", " ", 5, ["make check"], {"run": "make check"}, True):
            with self.subTest(value=value):
                self.stops(
                    dict(CALL, test=value),
                    'the call\'s "test" is not a command',
                    "null",
                    '"test": "<command> or null"',
                )

    def test_a_call_with_an_unknown_key_stops(self):
        # Given: a call with a key turn does not take, at the top or among the kinds
        # When: the run is started
        # Then: it stops, naming the key, the first of them by name, and those turn takes
        self.stops(dict(CALL, out="x.json"), '"out"', '"ccs", "kind", "result" and "test"')
        self.stops(dict(CALL, out="x.json", extra="y"), 'holds "extra"')
        call = copy.deepcopy(CALL)
        call["kind"]["reader"] = "audience"
        self.stops(call, '"reader"', '"receiver"')
        call["kind"]["also"] = "audience"
        self.stops(call, 'the kind of "also"')

    def test_a_call_without_a_kind_stops(self):
        # Given: a call that leaves out the kind of the work, the checklist, the receiver, what the
        # receiver uses the work for or what they have with it
        # When: the run is started
        # Then: it stops, naming the kind to give
        for kind in ("work", "checklist", "receiver", "use", "has"):
            with self.subTest(kind=kind):
                self.stops(call_with(**{kind: None}), f'no kind for "{kind}"')

    def test_a_kind_without_an_entry_stops(self):
        # Given: a call naming, for each of its kinds, one the CCS has no entry of
        # When: the run is started
        # Then: it stops, naming the kind and the CCS
        for kind in ("work", "checklist", "receiver", "use", "has"):
            with self.subTest(kind=kind):
                self.stops(call_with(**{kind: "reader"}), '"reader"', CALL["ccs"], f'"{kind}"')

    def test_a_ccs_that_is_missing_or_not_a_ccs_stops(self):
        # Given: a CCS that is not there, not JSON, or not parts of entries of one kind each, the
        # rest of it a CCS of the call's kinds
        # When: the run is started
        # Then: it stops, saying the CCS is not there, or what a CCS must be
        self.stops(call_with(ccs="missing.json"), "the CCS missing.json is not there")
        bad = {
            "text.json": "not json",
            "list.json": "[]",
            "part.json": {"notes": {"deliverable": "README.md"}},
            "entry.json": {"notes": [{"a": "x", "b": "y"}]},
            "empty.json": {"notes": [{}]},
            "word.json": {"notes": ["x"]},
            "value.json": {"notes": [{"deliverable": 3}]},
        }
        for name, text in bad.items():
            with self.subTest(name=name):
                if isinstance(text, dict):
                    text = json.dumps(dict(CCS, **text))
                self.write(name, text)
                self.stops(call_with(ccs=name), f"{name} is not a CCS")

    def test_a_checklist_that_is_missing_or_has_no_items_stops(self):
        # Given: a CCS naming a checklist that is not there, or one with no items
        # When: the run is started
        # Then: it stops, naming the checklist, and for the one with no items, saying it holds none
        empty = "---\nname: other\nversion: 0.1.0\n---\n\n# Nothing\n"
        for text in (None, empty):
            with self.subTest(text=text):
                ccs = copy.deepcopy(CCS)
                ccs["retrieved_artifacts"][0] = {"checklist": "checklists/other.md"}
                if text is not None:
                    self.write("checklists/other.md", text)
                self.write_json(CALL["ccs"], ccs)
                self.stops(CALL, "checklists/other.md", *(["holds no item"] if text else []))

    def test_an_item_without_its_scope_stops(self):
        # Given: a checklist item with no Scope line under its heading, or one of no scope turn
        # takes, or the line further down
        # When: the run is started
        # Then: it stops, naming the checklist, the item and the scopes it takes
        for text in (
            CHECKLIST.replace("Scope: its part\n\n", ""),
            CHECKLIST.replace("Scope: its part", "Scope: some part"),
            CHECKLIST.replace(
                "Scope: its part\n\nOn opening it,", "On opening it,\n\nScope: its part"
            ),
        ):
            with self.subTest(text=text):
                self.write("checklists/readme.md", text)
                self.stops(
                    CALL,
                    "checklists/readme.md B-1 does not say where it is answered",
                    "`Scope: its part`, `Scope: each part` or `Scope: whole`",
                )

    def test_a_file_the_receiver_has_that_is_missing_stops(self):
        # Given: a call naming the kind of what the receiver has, whose file is not there
        # When: the run is started
        # Then: it stops, naming the file
        os.remove("docs/start.md")
        self.stops(CALL, "docs/start.md")

    def test_kinds_that_are_not_an_object_stop(self):
        # Given: a call whose kinds are a list, not an object of names
        # When: the run is started
        # Then: it stops, giving the shape of the call
        self.stops(dict(CALL, kind=["deliverable"]), '"kind" is not an object', '{"ccs"')

    def test_a_kind_that_is_not_a_name_stops(self):
        # Given: a call whose kind is not a word but a list
        # When: the run is started
        # Then: it stops, saying a kind is a name
        self.stops(call_with(work=["deliverable"]), 'the kind for "work" is not a name')


if __name__ == "__main__":
    unittest.main()
