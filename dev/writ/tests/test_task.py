import os
import unittest

from helpers import CHECKLISTS, Repo, run

DOC = os.path.join(CHECKLISTS, "doc.md")
README = os.path.join(CHECKLISTS, "readme.md")


def task(repo, *args):
    return run(
        repo,
        "task",
        "--deliverable",
        "README.md",
        "--receiver",
        "a developer who finds the tool on GitHub",
        "--use",
        "to decide whether to use it",
        "--acceptance",
        "they can install it and run it once",
        "--checklist",
        DOC,
        README,
        "--content",
        ".writ/content/README.content.md",
        *args,
    )


class Content(unittest.TestCase):
    def test_the_content_file_is_named_from_the_document_s_path(self):
        cases = [
            ("turn/README.md", ".writ/content/turn/README.content.md"),
            ("README.md", ".writ/content/README.content.md"),
            ("src/tidy.py", ".writ/content/src/tidy.content.md"),
        ]
        repo = Repo()
        for document, content in cases:
            with self.subTest(document):
                # Given: a document's path
                # When: its content file is asked for
                code, out = run(repo, "content", document)
                # Then: it is under .writ/content, by the document's folder and name
                self.assertEqual((code, out.strip()), (0, content))
        repo.close()

    def test_a_document_outside_the_repository_is_stopped(self):
        # Given: a document's path that leaves the repository
        repo = Repo()
        # When: its content file is asked for
        code, out = run(repo, "content", "../README.md")
        # Then: it is stopped, saying the path must be inside the repository
        self.assertEqual(code, 1)
        self.assertIn("../README.md is outside the repository", out)
        repo.close()


class Task(unittest.TestCase):
    def setUp(self):
        self.repo = Repo()
        self.repo.write(".writ/content/README.content.md", "# What README.md says\n")

    def tearDown(self):
        self.repo.close()

    def test_the_task_is_written_in_turn_s_form_and_the_two_lines_to_call_it_are_printed(self):
        # Given: a document, its reader, use and acceptance, its checklists, content, a reference,
        # what the reader opens and the language
        self.repo.write("docs/notes.md", "notes\n")
        self.repo.write("LICENSE", "MIT\n")
        # When: the task is written
        code, out = task(
            self.repo,
            "--reference",
            "docs/notes.md",
            "--opens",
            "LICENSE",
            "--language",
            "English",
        )
        # Then: the two lines name the task and where turn writes back, and the task holds each
        # input under turn's kind for it, with turn's five parts empty
        self.assertEqual(code, 0)
        self.assertEqual(
            out.splitlines(),
            ["in: .writ/tasks/README-1.json", "out: .writ/tasks/README-1.back.json"],
        )
        self.assertEqual(
            self.repo.json(".writ/tasks/README-1.json"),
            {
                "focal_entities": [
                    {"deliverable": "README.md"},
                    {"receiver": "a developer who finds the tool on GitHub"},
                ],
                "goal_orientation": [
                    {"use": "to decide whether to use it"},
                    {"acceptance": "they can install it and run it once"},
                ],
                "retrieved_artifacts": [
                    {"checklist": DOC},
                    {"checklist": README},
                    {"content": ".writ/content/README.content.md"},
                    {"reference": "docs/notes.md"},
                    {"receiver_opens": "LICENSE"},
                ],
                "constraints": [{"language": "English"}],
                "predictive_cue": [],
                "uncertainty_signal": [],
                "semantic_gist": [],
                "relational_map": [],
                "episodic_trace": [],
            },
        )
        self.assertFalse(self.repo.exists(".writ/tasks/README-1.back.json"))

    def test_a_second_task_for_the_same_document_takes_the_next_number(self):
        # Given: a task already written for the document, and turn's answer to it
        task(self.repo)
        self.repo.write(".writ/tasks/README-1.back.json", "{}")
        # When: another task is written
        code, out = task(self.repo)
        # Then: it takes the next number, leaving the first and its answer as they are
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[0], "in: .writ/tasks/README-2.json")
        self.assertEqual(self.repo.read(".writ/tasks/README-1.back.json"), "{}")

    def test_a_task_with_several_files_names_each(self):
        # Given: a work of code and its tests
        self.repo.write(".writ/content/src/tidy.content.md", "# What src/tidy.py says\n")
        # When: the task is written
        code, out = run(
            self.repo,
            "task",
            "--deliverable",
            "src/tidy.py",
            "tests/test_tidy.py",
            "--receiver",
            "the maintainer",
            "--acceptance",
            "they can change it",
            "--checklist",
            os.path.join(CHECKLISTS, "code.md"),
            "--content",
            ".writ/content/src/tidy.content.md",
        )
        # Then: the task names each file as a deliverable, in order, and is named by the first
        self.assertEqual(code, 0)
        self.assertEqual(out.splitlines()[0], "in: .writ/tasks/tidy-1.json")
        self.assertEqual(
            self.repo.json(".writ/tasks/tidy-1.json")["focal_entities"],
            [
                {"deliverable": "src/tidy.py"},
                {"deliverable": "tests/test_tidy.py"},
                {"receiver": "the maintainer"},
            ],
        )

    def test_a_task_without_a_use_or_a_language_leaves_them_out(self):
        # Given: a task with no use and no language given
        # When: it is written
        code, out = run(
            self.repo,
            "task",
            "--deliverable",
            "README.md",
            "--receiver",
            "r",
            "--acceptance",
            "a",
            "--checklist",
            DOC,
            "--content",
            ".writ/content/README.content.md",
        )
        # Then: the task holds neither
        self.assertEqual(code, 0, out)
        written = self.repo.json(".writ/tasks/README-1.json")
        self.assertEqual(written["goal_orientation"], [{"acceptance": "a"}])
        self.assertEqual(written["constraints"], [])

    def test_a_task_naming_a_file_that_is_not_there_is_stopped_before_it_is_written(self):
        cases = [
            (["--reference", "docs/gone.md"], "docs/gone.md does not exist"),
            (["--opens", "LICENSE"], "LICENSE does not exist"),
            (["--content", "gone.md"], "gone.md does not exist"),
            (["--checklist", "x.md"], "x.md does not exist"),
        ]
        for args, said in cases:
            with self.subTest(said):
                # Given: a task naming a file that is not there
                # When: it is written
                code, out = task(self.repo, *args)
                # Then: it is stopped, naming the file, and no task is written
                self.assertEqual(code, 1)
                self.assertIn(said, out)
                self.assertFalse(self.repo.exists(".writ/tasks"))

    def test_a_task_missing_what_turn_needs_says_how_to_call(self):
        # Given: a call with no deliverable
        # When: the task is written
        code, out = run(self.repo, "task", "--receiver", "r")
        # Then: it is stopped with how to call it
        self.assertEqual(code, 1)
        self.assertIn("usage:", out)
        self.assertIn("--deliverable", out)


if __name__ == "__main__":
    unittest.main()
