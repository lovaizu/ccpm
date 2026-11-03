"""scripts/practices.py, the command a person or planner runs on a template: write and check its
Markdown, open its sources, and write its standard and its groups of questions into a run."""

import contextlib
import copy
import io
import json
import os
import runpy
import tempfile
import unittest
import urllib.request
from unittest import mock

import helpers
from helpers import practices

from unit.core.domain.test_templates import DATA, response


class Main(unittest.TestCase):
    def test_check_fails_until_write_makes_the_markdown(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            self.assertEqual(practices.main(["check", path]), 1)
            self.assertEqual(practices.main(["write", path]), 0)
            self.assertEqual(practices.main(["check", path]), 0)

    def test_check_fails_on_a_fault_of_the_form(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            data = copy.deepcopy(DATA)
            data["practices"].pop()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
            practices.main(["write", path])
            self.assertEqual(practices.main(["check", path]), 1)

    def test_check_fails_on_a_markdown_changed_by_hand(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            practices.main(["write", path])
            with open(os.path.join(folder, "kind.md"), "a", encoding="utf-8") as f:
                f.write("More.\n")
            err = io.StringIO()
            with contextlib.redirect_stderr(err):
                self.assertEqual(practices.main(["check", path]), 1)
            self.assertIn("kind.md is not as its JSON makes it; run write", err.getvalue())

    def test_sources_fails_on_a_ground_whose_page_is_not_the_one_meant(self):
        helpers.templates.fetch.cache_clear()
        self.addCleanup(helpers.templates.fetch.cache_clear)
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "kind.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            err = io.StringIO()
            with (
                mock.patch.object(
                    urllib.request, "urlopen", return_value=response("text/html", b"T")
                ),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(practices.main(["sources", path]), 1)
            expected = (
                f"practices.py: {path}: Q1 ground 1 (https://x.example/t) does not hold its quote"
            )
            self.assertEqual(err.getvalue(), expected + "\n")
            helpers.templates.fetch.cache_clear()
            with mock.patch.object(
                urllib.request, "urlopen", return_value=response("text/html", b"T y")
            ):
                self.assertEqual(practices.main(["sources", path]), 0)

    def written(self, folder, *names):
        """The paths of best practices of the names, DATA each, written in the folder."""
        paths = []
        for name in names:
            path = os.path.join(folder, f"{name}.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump(DATA, f)
            paths.append(path)
        return paths

    def test_write_and_check_take_each_best_practice_given(self):
        with tempfile.TemporaryDirectory() as folder:
            paths = self.written(folder, "one", "two")
            self.assertEqual(practices.main(["write", *paths]), 0)
            for name in ("one", "two"):
                with open(os.path.join(folder, f"{name}.md"), encoding="utf-8") as f:
                    self.assertTrue(f.read().startswith(f"# {name}\n"))
            self.assertEqual(practices.main(["check", *paths]), 0)

    def test_check_fails_on_a_markdown_cut_short(self):
        with tempfile.TemporaryDirectory() as folder:
            (path,) = self.written(folder, "kind")
            practices.main(["write", path])
            md = os.path.join(folder, "kind.md")
            with open(md, encoding="utf-8") as f:
                text = f.read()
            with open(md, "w", encoding="utf-8") as f:
                f.write(text[:-2])
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(practices.main(["check", path]), 1)

    def test_sources_takes_each_best_practice_given(self):
        helpers.templates.fetch.cache_clear()
        self.addCleanup(helpers.templates.fetch.cache_clear)
        with tempfile.TemporaryDirectory() as folder:
            paths = self.written(folder, "one", "two")
            err = io.StringIO()
            with (
                mock.patch.object(
                    urllib.request, "urlopen", return_value=response("text/html", b"T")
                ),
                contextlib.redirect_stderr(err),
            ):
                self.assertEqual(practices.main(["sources", *paths]), 1)
            for path in paths:
                self.assertIn(f"practices.py: {path}: ", err.getvalue())

    def test_refuses_an_unknown_command_or_one_given_no_best_practice(self):
        with tempfile.TemporaryDirectory() as folder:
            (path,) = self.written(folder, "kind")
            for argv in (["print"], ["check"], ["print", path]):
                with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                    self.assertEqual(practices.main(argv), 2)

    def test_the_script_takes_the_arguments_after_its_own_path(self):
        with tempfile.TemporaryDirectory() as folder:
            (path,) = self.written(folder, "kind")
            practices.main(["write", path])
            with (
                mock.patch.object(practices.sys, "argv", ["practices.py", "check", path]),
                contextlib.redirect_stderr(io.StringIO()),
                self.assertRaises(SystemExit) as end,
            ):
                runpy.run_path(practices.__file__, run_name="__main__")
        self.assertEqual(end.exception.code, 0)


class StandardAndGroups(helpers.RunTest):
    def written(self):
        """The paths of a template, readme.json, and of a run.json beside it."""
        self.write_json("readme.json", helpers.TEMPLATE)
        made = helpers.run()["run.json"]
        del made["groups"], made["refactoring_groups"]
        self.write_json("run.json", made)
        return "readme.json", "run.json"

    def test_standard_writes_the_goal_parts_and_questions(self):
        template, _ = self.written()
        self.assertEqual(practices.main(["standard", template, "out/standard.json"]), 0)
        self.assertEqual(
            self.read_json("out/standard.json"), helpers.templates.standard(helpers.TEMPLATE)
        )

    def test_groups_writes_the_kind_s_groups_into_the_run(self):
        template, run = self.written()
        self.assertEqual(practices.main(["groups", template, run]), 0)
        self.assertEqual(
            self.read_json(run)["groups"],
            [
                {"id": "G1", "questions": ["readme/Q1"]},
                {"id": "G2", "questions": ["readme/Q2"]},
                {"id": "G3", "questions": ["readme/Q3"]},
            ],
        )

    def test_groups_of_the_refactoring_template_go_under_their_own_key(self):
        _, run = self.written()
        self.write_json("refactor-doc.json", helpers.REFACTORING)
        self.assertEqual(practices.main(["groups", "refactor-doc.json", run]), 0)
        written = self.read_json(run)
        self.assertEqual(
            written["refactoring_groups"], [{"id": "G1", "questions": ["refactor-doc/Q1"]}]
        )
        self.assertNotIn("groups", written)

    def test_groups_of_a_template_that_is_neither_the_run_s_are_refused(self):
        _, run = self.written()
        self.write_json("other.json", helpers.TEMPLATE)
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(practices.main(["groups", "other.json", run]), 2)
        self.assertEqual(
            err.getvalue(),
            "practices.py: other.json is neither readme nor refactor-doc, the templates of"
            " run.json\n",
        )

    def test_groups_of_a_run_out_of_its_form_are_refused(self):
        template, run = self.written()
        self.write_json(run, {"kind": "readme"})
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(practices.main(["groups", template, run]), 2)
        self.assertTrue(
            err.getvalue().startswith(
                "practices.py: could not read run.json: run.json is out of its form"
            )
        )

    def test_standard_and_groups_take_two_paths(self):
        for argv in (["standard", "a.json"], ["groups", "a.json", "b.json", "c.json"]):
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(practices.main(argv), 2)


if __name__ == "__main__":
    unittest.main()
