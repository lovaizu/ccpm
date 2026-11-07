"""domain/files.py, a file rn reads held to its form, or refused with why."""

from __future__ import annotations

import helpers
from helpers import files


class Files(helpers.testing.FolderTest):
    def test_json_in_its_form_is_read(self):
        self.write_json("c.json", {"request": "r"})
        self.assertEqual(files.load("c.json", "change"), {"request": "r"})

    def test_a_file_missing_or_holding_no_json_or_out_of_form_is_refused(self):
        self.write("bad.json", "{")
        self.write_json("out.json", {"request": 1})
        for path, said in (
            ("gone.json", "there is no file gone.json"),
            (
                "bad.json",
                "bad.json is not JSON: Expecting property name enclosed in double quotes at line 1",
            ),
            ("out.json", "out.json is out of its form: $.request"),
        ):
            with self.subTest(path=path):
                with self.assertRaises(files.Unreadable) as stop:
                    files.load(path, "change")
                self.assertIn(said, str(stop.exception))

    def test_data_is_saved_as_json_a_person_reads_its_folder_made(self):
        files.save("a/b.json", {"k": "é"})
        self.assertEqual(self.read("a/b.json"), '{\n "k": "é"\n}\n')
        files.save("c.json", [])
        self.assertEqual(self.read("c.json"), "[]\n")
