"""files.py: a run's file read and held to its form in core/domain/forms/, or refused with why."""

import json
import os
import unittest
from typing import Any

import helpers
from helpers import files


class TestLoad(helpers.testing.FolderTest):
    def test_a_file_in_its_form_is_given_as_written(self):
        # Given: a run.json in its form
        data = {"works": [helpers.work()]}
        self.write_json("run.json", data)
        # When: it is loaded to the run form
        # Then: it is given as written
        self.assertEqual(files.load("run.json", "run"), data)

    def test_a_missing_file_is_refused(self):
        with self.assertRaises(files.Unreadable) as refused:
            files.load("run.json", "run")
        self.assertEqual(str(refused.exception), "there is no file run.json")

    def test_a_file_that_is_no_json_is_refused_with_where(self):
        self.write("run.json", '{"works":\n')
        with self.assertRaises(files.Unreadable) as refused:
            files.load("run.json", "run")
        self.assertEqual(
            str(refused.exception),
            "run.json is not JSON: Expecting value at line 2 column 1",
        )

    def test_a_file_out_of_its_form_is_refused_with_the_point(self):
        self.write_json("run.json", {"kind": "readme"})
        with self.assertRaises(files.Unreadable) as refused:
            files.load("run.json", "run")
        self.assertEqual(
            str(refused.exception),
            'run.json is out of its form: $: expected the key "works", found an object without it',
        )

    def test_read_gives_the_json_as_it_is_or_refuses_it(self):
        self.write_json("tree.json", {"any": ["form"]})
        self.write("bad.json", "[")
        self.assertEqual(files.read("tree.json"), {"any": ["form"]})
        for path, said in (
            ("gone.json", "there is no file gone.json"),
            ("bad.json", "bad.json is not JSON"),
        ):
            with self.subTest(path=path), self.assertRaises(files.Unreadable) as refused:
                files.read(path)
            self.assertIn(said, str(refused.exception))

    def test_each_form_is_one_structured_outputs_take(self):
        # Given: every form Turn holds a file to
        for name in sorted(os.listdir(files.FORMS)):
            # Then: Lane's schema reads it whole
            with (
                self.subTest(form=name),
                open(os.path.join(files.FORMS, name), encoding="utf-8") as f,
            ):
                files.schema.checked(json.load(f))

    def test_a_step_s_trace_is_held_to_lane_s_actions_and_its_calls(self):
        # Given: a best practice whose step has a trace
        def practice(trace) -> dict[str, Any]:
            step = {"text": "Do.", **({"trace": trace} if trace is not None else {})}
            return {
                "goal": "G.",
                "inputs": [],
                "preconditions": [],
                "intents": [{"id": "Q1", "about": "the whole", "what": "Q?"}],
                "practices": [{"intent": "Q1", "thinking": "T.", "steps": [step]}],
            }

        # Then: one of a command run, a file read or a file made, with a call or more, holds,
        # as does a step with none
        for trace in (None, *({"action": a, "takes": ["x"]} for a in ("run", "read", "write"))):
            with self.subTest(trace=trace):
                self.write_json("best-practice.json", practice(trace))
                self.assertEqual(files.load("best-practice.json", "best-practice"), practice(trace))
        # Then: any other action, no call, or another key is refused
        for trace in (
            {"action": "open", "takes": ["x"]},
            {"action": "run", "takes": []},
            {"action": "run"},
            {"action": "run", "takes": ["x"], "lane": "run_step"},
        ):
            with self.subTest(trace=trace), self.assertRaises(files.Unreadable):
                self.write_json("best-practice.json", practice(trace))
                files.load("best-practice.json", "best-practice")
        # Then: a step that is a bare text is refused
        bare = practice(None)
        bare["practices"][0]["steps"] = ["Do."]
        self.write_json("best-practice.json", bare)
        with self.assertRaises(files.Unreadable):
            files.load("best-practice.json", "best-practice")

    def test_save_writes_json_a_person_reads_in_a_folder_made_for_it(self):
        files.save("a/b/run.json", {"kind": "é"})
        self.assertEqual(self.read("a/b/run.json"), '{\n "kind": "é"\n}\n')

    def test_save_in_the_folder_it_runs_in(self):
        files.save("run.json", {})
        self.assertEqual(self.read("run.json"), "{}\n")

    def test_a_form_is_read_once(self):
        self.assertIs(files.form("run"), files.form("run"))


if __name__ == "__main__":
    unittest.main()
