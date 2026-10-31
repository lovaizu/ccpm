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
    CLAIM,
    FIRST_READ,
    ITEM_B1,
    RESULT,
    RUN,
    SCRIPTS,
    TODAY,
    RepoTest,
    call,
)

# The usage written out as the user is to read it, not taken from turn.py, so a change to it in
# turn.py by mistake fails the tests; the duplicate-code check leaves it out, as the user chose.
# pylint: disable=duplicate-code
USAGE = (
    "usage: turn.py start '<call JSON>'\n"
    "       turn.py generator <result>\n"
    "       turn.py first-user <result>\n"
    "       turn.py parts <result>\n"
    "       turn.py claim <result>\n"
    "       turn.py reading <result>\n"
    "       turn.py wait <result> generator|first-user\n"
    "       turn.py end <result>"
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
        # argument or with one too many, the wait short of its role or with one too many
        # When: it is run
        # Then: it prints the usage, which names every command with its argument, and stops
        # Words sorting before and after every command are among the unknown ones.
        commands = ["start", "generator", "first-user", "parts", "claim", "reading", "end"]
        for argv in [
            [],
            ["go"],
            ["aaa", "r"],
            ["zzz", "r"],
            *([c] for c in commands),
            *([c, "r", "x"] for c in commands),
            ["wait"],
            ["wait", "r"],
            ["wait", "r", "generator", "x"],
            ["aaa", "r", "x"],
            ["zzz", "r", "x"],
        ]:
            with self.subTest(argv=argv):
                self.assertEqual(self.turn(*argv), (1, USAGE + "\n"))

    def test_the_script_finds_its_own_modules_before_any_of_the_same_name(self):
        # Given: a folder on PYTHONPATH holding a module named as one of turn's scripts, which
        # breaks when imported
        # When: a role runs the script by its path from the shell, with no command
        # Then: it prints the usage, as its own modules are found first
        self.write("elsewhere/folder.py", "raise SystemExit('not turn')\n")
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
        # When: a role runs the script by its path with a command and its argument
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
        # When: the run is started, and the generator and the first user are given their files
        # Then: each is printed with the names as they are written
        os.rename("checklists/readme.md", "checklists/読む.md")
        ccs = dict(CCS, retrieved_artifacts=[{"checklist": "checklists/読む.md"}, {"page": "docs"}])
        ccs["focal_entities"] = [{"deliverable": "はじめに.md"}, CCS["focal_entities"][1]]
        self.write_json(CALL["ccs"], ccs)
        call = dict(CALL, result=".tasks/結果.json")
        code, out = self.turn("start", json.dumps(call))
        self.assertEqual(code, 0, out)
        self.assertIn("結果.json", out)
        result = json.loads(out)["result"]
        self.write("はじめに.md", "# 始め\n")
        for command, name in (("generator", "はじめに.md"), ("first-user", "checklists/読む.md")):
            with self.subTest(command=command):
                code, out = self.turn(command, result)
                self.assertEqual(code, 0, out)
                self.assertIn(name, out)
        code, out = self.turn("parts", result)
        self.assertEqual(code, 0, out)
        self.assertIn("はじめに.md:1-1", out)


class TestStart(RepoTest):
    def test_a_call_whose_kinds_all_have_entries_starts_the_run(self):
        # Given: a call naming the CCS, the kinds of the work, the checklist and the receiver, and
        # where the result goes
        # When: the run is started
        # Then: it prints where the result goes alone, as a whole path, and keeps the call and the
        # folder it was made from in the run's folder, beside nothing else
        code, out = self.turn("start", json.dumps(CALL))
        self.assertEqual((code, json.loads(out)), (0, {"result": self.here(CALL["result"])}))
        self.assertEqual(self.read_json(f"{RUN}/call.json"), {"call": CALL, "root": self.base})
        self.assertEqual(os.listdir(RUN), ["call.json"])

    def test_a_call_again_keeps_what_the_run_s_folder_holds(self):
        # Given: a run started, its generator's claim and its first user's reading in its folder
        self.started()
        self.claimed(CLAIM)
        self.read_as(FIRST_READ)
        # When: turn is called again with the same call
        result = self.started()
        # Then: it prints the same result, and the claim and the reading are kept as they were
        self.assertEqual(result, self.here(CALL["result"]))
        self.assertEqual(self.read_json(self.kept("generator.json")), CLAIM)
        self.assertEqual(self.read_json(self.kept("first-user.json")), FIRST_READ)

    def test_a_call_again_from_another_folder_reads_the_call_from_where_it_was_first_made(self):
        # Given: a run started from the root on a call naming its result by a whole path and its
        # CCS from the root, and the session's working folder moved to notes/
        asked = dict(CALL, result=self.here(RESULT))
        self.started(asked)
        os.chdir("notes")
        # When: turn is called again with the same call
        # Then: it goes on with the run, its CCS read from the root, and keeps the folder the call
        # was first made from
        self.assertEqual(self.started(asked), self.here(RESULT))
        self.assertEqual(self.read_json(self.kept("call.json")), {"call": asked, "root": self.base})

    def test_a_call_again_with_another_call_on_the_same_result_stops(self):
        # Given: a run started on a call whose test is a command
        self.started()
        # When: turn is called again with the same result but another test, or another CCS
        for changed in ({"test": None}, {"ccs": "notes/readme.decisions.md"}):
            with self.subTest(changed=changed):
                out = self.stopped("start", json.dumps(dict(CALL, **changed)))
                # Then: it stops, saying a run of another call is kept for that result, and keeps
                # the call it holds
                self.assertIn("a run of another call is kept", out)
                self.assertEqual(self.read_json(self.kept("call.json"))["call"], CALL)

    def test_a_call_again_on_a_ccs_whose_receiver_then_has_only_the_work_goes_on(self):
        # Given: a run started, and its CCS then moving the only file the receiver has into the
        # work
        self.started()
        ccs = copy.deepcopy(CCS)
        ccs["retrieved_artifacts"].remove({"page": "docs/start.md"})
        ccs["focal_entities"].append({"deliverable": "docs/start.md"})
        self.write_json(CALL["ccs"], ccs)
        # When: turn is called again with the same call
        # Then: it goes on with the run
        self.assertEqual(self.started(), self.here(CALL["result"]))

    def test_a_call_again_on_a_ccs_gone_wrong_stops(self):
        # Given: a run started, and its CCS then naming a checklist that is not there
        self.started()
        ccs = copy.deepcopy(CCS)
        ccs["retrieved_artifacts"][0] = {"checklist": "checklists/gone.md"}
        self.write_json(CALL["ccs"], ccs)
        # When: turn is called again with the same call
        # Then: it stops, naming the checklist
        self.assertIn("checklists/gone.md", self.stopped("start", json.dumps(CALL)))

    def test_a_result_in_a_folder_not_yet_there_starts_its_run(self):
        # Given: a call whose result goes in a folder not yet there
        # When: the run is started
        # Then: the run is kept in turn's folder at the root, named by the result's path from it
        self.started(call_with(result="out/new/result.json"))
        self.assertTrue(os.path.isfile(f".turn/{TODAY}-out%2Fnew%2Fresult.json/call.json"))


class TestStartStops(RepoTest):
    def stops(self, call, *said):
        """The start of the call stops, saying each of the words, and starts no run."""
        code, out = self.turn("start", call if isinstance(call, str) else json.dumps(call))
        self.assertEqual(code, 1)
        for words in said:
            self.assertIn(words, out)
        # No run is started: neither the result nor the run's folder is written.
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
        self.stops(call, '"reader"', '"receiver"', '"has" and "each"')
        call["kind"]["also"] = "audience"
        self.stops(call, 'the kind of "also"')

    def test_a_call_without_a_kind_stops(self):
        # Given: a call that leaves out the kind of the work, the checklist, the receiver, what the
        # receiver uses the work for, what they have with it or the items asked of each part
        # When: the run is started
        # Then: it stops, naming the kind to give
        for kind in ("work", "checklist", "receiver", "use", "has", "each"):
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
        empty = "# Nothing\n"
        for text in (None, empty):
            with self.subTest(text=text):
                ccs = copy.deepcopy(CCS)
                ccs["retrieved_artifacts"][0] = {"checklist": "checklists/other.md"}
                if text is not None:
                    self.write("checklists/other.md", text)
                self.write_json(CALL["ccs"], ccs)
                self.stops(CALL, "checklists/other.md", *(["holds no item"] if text else []))

    def test_the_items_asked_of_each_part_are_those_the_ccs_names(self):
        # Given: a call naming the kind of the items asked of each part, and a CCS naming one of
        # them, its checklist's path written another way, or none
        each = {"each": "./checklists/readme.md B-1"}
        cases = {"one named": ([each], [ITEM_B1]), "none named": ([], [])}
        for name, (named, asked) in cases.items():
            with self.subTest(name=name):
                ccs = copy.deepcopy(CCS)
                ccs["retrieved_artifacts"] += named
                self.write_json(CALL["ccs"], ccs)
                # When: the run is laid out
                # Then: those are the items asked of each part
                self.assertEqual(call.laid_out(CALL)["each"], asked)

    def test_an_item_asked_of_each_part_that_no_checklist_holds_stops(self):
        # Given: a CCS asking of each part an item its checklist does not hold, one of a checklist
        # the call does not name, and one with no ID
        for value in (
            "checklists/readme.md B-9",
            "checklists/other.md B-1",
            "checklists/readme.md",
        ):
            with self.subTest(value=value):
                ccs = copy.deepcopy(CCS)
                ccs["retrieved_artifacts"].append({"each": value})
                self.write_json(CALL["ccs"], ccs)
                # When: the run is started
                # Then: it stops, naming the CCS, the entry and the form to name an item in
                self.stops(
                    CALL,
                    f'{CALL["ccs"]} asks "{value}" of each part',
                    "<checklist path> <ID>, such as `checklists/readme.md Q-3`",
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
