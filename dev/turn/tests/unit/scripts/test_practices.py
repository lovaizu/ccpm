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


class Ready(helpers.RunTest):
    def laid(self, template=None, **run):
        """A template of the kind readme at .turn/best-practices/readme.json, as a repository makes
        one, and a run's folder whose run.json names it, with the keys given over its own."""
        path = ".turn/best-practices/readme.json"
        if isinstance(template, str):
            path = template
        else:
            self.write_json(path, template or helpers.TEMPLATE)
        made = {
            "kind": "readme",
            "template": path,
            "refactoring": "refactor-doc",
            **run,
        }
        self.write_json(f"{self.folder}/run.json", made)

    def ran(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = practices.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def test_writes_each_standard_and_each_group_and_says_so(self):
        # Given: a run whose template the repository made, and Turn's refactor-doc
        self.laid()
        # When: the run is made ready
        code, out, err = self.ran("ready", self.folder)
        # Then: both standards, the kind's groups and refactor-doc's are written, and it says so
        self.assertEqual(
            (code, out, err),
            (
                0,
                (
                    f"practices.py: {self.folder} is ready: standard.json and"
                    " refactoring-standard.json written, and 3 groups of readme and 1 of"
                    " refactor-doc in run.json.\n"
                ),
                "",
            ),
        )
        own = os.path.join(practices.OWN, "refactor-doc.json")
        with open(own, encoding="utf-8") as f:
            refactoring = json.load(f)
        self.assertEqual(
            self.read_json(f"{self.folder}/standard.json"),
            helpers.templates.standard(helpers.TEMPLATE),
        )
        self.assertEqual(
            self.read_json(f"{self.folder}/refactoring-standard.json"),
            helpers.templates.standard(refactoring),
        )
        written = self.read_json(f"{self.folder}/run.json")
        self.assertEqual(written["groups"], helpers.RUN["run.json"]["groups"])
        self.assertEqual(
            written["refactoring_groups"],
            helpers.templates.groups(refactoring, "refactor-doc"),
        )

    def test_a_template_the_repository_made_gets_its_markdown_and_turn_s_keep_theirs(self):
        self.laid()
        before = os.path.getmtime(os.path.join(practices.OWN, "refactor-doc.md"))
        self.ran("ready", self.folder)
        self.assertEqual(
            self.read(".turn/best-practices/readme.md"),
            helpers.templates.markdown("readme", helpers.TEMPLATE),
        )
        self.assertEqual(os.path.getmtime(os.path.join(practices.OWN, "refactor-doc.md")), before)

    def test_turn_s_own_template_is_taken_where_it_lies(self):
        self.laid(template=os.path.join(practices.OWN, "readme.json"))
        before = os.path.getmtime(os.path.join(practices.OWN, "readme.md"))
        self.assertEqual(self.ran("ready", self.folder)[0], 0)
        self.assertEqual(os.path.getmtime(os.path.join(practices.OWN, "readme.md")), before)
        self.assertEqual(self.read_json(f"{self.folder}/run.json")["groups"][0]["id"], "G1")

    def test_a_template_out_of_its_form_gives_1_and_each_fault(self):
        broken = copy.deepcopy(helpers.TEMPLATE)
        broken["practices"].pop()
        self.laid(template=broken)
        self.assertEqual(
            self.ran("ready", self.folder),
            (
                1,
                "",
                (
                    "practices.py: .turn/best-practices/readme.json: practices meet Q1, Q2, not"
                    " each question once in its order\n"
                ),
            ),
        )
        self.assertFalse(os.path.exists(f"{self.folder}/standard.json"))

    def test_a_template_that_cannot_be_read_gives_2(self):
        self.laid()
        made = self.read_json(f"{self.folder}/run.json")
        made["template"] = "gone.json"
        self.write_json(f"{self.folder}/run.json", made)
        code, out, err = self.ran("ready", self.folder)
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("practices.py: could not read gone.json: "))
        self.write("gone.json", "{")
        code, out, err = self.ran("ready", self.folder)
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith("practices.py: could not read gone.json: "))

    def test_a_run_out_of_its_form_gives_2(self):
        self.write_json(f"{self.folder}/run.json", {"kind": "readme"})
        code, out, err = self.ran("ready", self.folder)
        self.assertEqual((code, out), (2, ""))
        self.assertTrue(err.startswith(f"practices.py: could not make {self.folder} ready: "))

    def test_ready_takes_one_run(self):
        for argv in (["ready"], ["ready", "a", "b"]):
            with self.subTest(argv=argv):
                self.assertEqual(self.ran(*argv), (2, "", practices.USAGE + "\n"))


if __name__ == "__main__":
    unittest.main()
