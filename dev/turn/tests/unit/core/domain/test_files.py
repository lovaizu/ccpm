"""files.py: a run's file read and held to its form in core/domain/forms/, or refused with why."""

import json
import os
import unittest

import helpers
from helpers import files


class TestLoad(helpers.testing.FolderTest):
    def test_a_file_in_its_form_is_given_as_written(self):
        # Given: a run.json in its form
        self.write_json("run.json", helpers.RUN["run.json"])
        # When: it is loaded to the run form
        # Then: it is given as written
        self.assertEqual(files.load("run.json", "run"), helpers.RUN["run.json"])

    def test_a_missing_file_is_refused(self):
        with self.assertRaises(files.Unreadable) as refused:
            files.load("run.json", "run")
        self.assertEqual(str(refused.exception), "there is no file run.json")

    def test_a_file_that_is_no_json_is_refused_with_where(self):
        self.write("run.json", '{"kind":\n')
        with self.assertRaises(files.Unreadable) as refused:
            files.load("run.json", "run")
        self.assertEqual(
            str(refused.exception),
            "run.json is not JSON: Expecting value at line 2 column 1",
        )

    def test_a_file_out_of_its_form_is_refused_with_the_point(self):
        self.write_json("run.json", {"kind": "readme", "template": "t.json"})
        with self.assertRaises(files.Unreadable) as refused:
            files.load("run.json", "run")
        self.assertEqual(
            str(refused.exception),
            'run.json is out of its form: $: expected the key "refactoring", found an object'
            " without it",
        )

    def test_each_form_is_one_structured_outputs_take(self):
        # Given: every form Turn holds a file to
        for name in sorted(os.listdir(files.FORMS)):
            # Then: Lane's schema reads it whole
            with (
                self.subTest(form=name),
                open(os.path.join(files.FORMS, name), encoding="utf-8") as f,
            ):
                files.schema.checked(json.load(f))

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
