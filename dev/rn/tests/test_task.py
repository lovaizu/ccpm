import contextlib
import io
import os
import runpy
import subprocess
import sys
from unittest import mock

from helpers import SCRIPTS, RepoTest

SESSION = ".rn/20261016-x"
COMMANDS = [
    "up.py checklists <kind>",
    "up.py decisions <session folder> <document>",
    (
        "up.py task <session folder> --deliverable <path> [<path> ...] --receiver <who>"
        " [--use <what for>] --acceptance <what they can do> --checklist <path> [<path> ...]"
        " --decisions <path> [--reference <path> ...] [--opens <path> ...] [--language <language>]"
    ),
    "up.py report <CCS turn wrote back> <judgments>",
]
USAGE = "usage: " + " ".join(COMMANDS)
CHECKLIST = "checklists/usability.md"
DECISIONS = "notes.decisions.md"
REQUIRED = {
    "--deliverable": "docs/setup.md",
    "--receiver": "a developer",
    "--acceptance": "they run the tests",
    "--checklist": CHECKLIST,
    "--decisions": DECISIONS,
}


def usage(run):
    # The content gives each command as one line, and rn wraps the long one for reading, so the
    # usage is compared with its line breaks and indents ignored.
    code, out = run
    return code, " ".join(out.split())


class TestCommand(RepoTest):
    def test_no_command_or_an_unknown_one_prints_the_usage(self):
        # Given: rn run with no command, or with one it does not know
        # When: it is run
        # Then: it prints the usage, which lists every command with every argument, and stops
        for argv in [[], ["tidy"]]:
            with self.subTest(argv=argv):
                self.assertEqual(usage(self.rn(*argv)), (1, USAGE))

    def test_a_command_given_the_wrong_count_of_arguments_prints_the_usage(self):
        # Given: a command given one argument too few or too many
        # When: it is run
        # Then: it prints the usage and stops
        for argv in [
            ["checklists"],
            ["checklists", "usability", "readme"],
            ["decisions", SESSION],
            ["content", SESSION, "a.md", "b.md"],
            ["report", "back.json"],
            ["report", "back.json", "judgments.json", "more.json"],
            ["task"],
        ]:
            with self.subTest(argv=argv):
                self.assertEqual(usage(self.rn(*argv)), (1, USAGE))

    def test_the_script_run_as_a_program_with_no_command_prints_the_usage(self):
        # Given: rn's script run as a program, given no command
        # When: it is run
        # Then: it prints the usage and exits with 1
        out = io.StringIO()
        script = os.path.join(SCRIPTS, "up.py")
        with contextlib.ExitStack() as stack:
            stack.enter_context(mock.patch.object(sys, "argv", [script]))
            stack.enter_context(mock.patch.object(sys, "path", sys.path[:]))
            stack.enter_context(contextlib.redirect_stdout(out))
            end = stack.enter_context(self.assertRaises(SystemExit))
            runpy.run_path(script, run_name="__main__")
        self.assertEqual(usage((end.exception.code, out.getvalue())), (1, USAGE))

    def test_the_script_run_on_its_own_finds_its_commands_and_prints_the_usage(self):
        # Given: rn's script run on its own by Python, in the isolated mode that leaves the
        #   script's folder off the places Python looks for code
        # When: it is run with no command
        # Then: it prints the usage and stops
        run = subprocess.run(
            [sys.executable, "-I", os.path.join(SCRIPTS, "up.py")],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(usage((run.returncode, run.stdout)), (1, USAGE))


class TestContent(RepoTest):
    def test_the_content_file_lies_in_the_session_folder_by_the_documents_path(self):
        # Given: a document at the top of the repository, in a folder, or in a folder whose name
        #   begins with two dots
        # When: rn is asked where its decisions file goes
        # Then: it prints the path under the session folder's decisions folder, the document's path
        #   without its extension and ending .decisions.md, and ends well
        for document, path in [
            ("README.md", SESSION + "/decisions/README.decisions.md"),
            ("turn/README.md", SESSION + "/decisions/turn/README.decisions.md"),
            ("src/tidy.py", SESSION + "/decisions/src/tidy.decisions.md"),
            ("..notes/a.md", SESSION + "/decisions/..notes/a.decisions.md"),
        ]:
            with self.subTest(document=document):
                self.assertEqual(self.rn("decisions", SESSION, document), (0, path + "\n"))

    def test_a_document_outside_the_repository_stops(self):
        # Given: a document named by an absolute path, or by a path that leaves the repository
        # When: rn is asked where its decisions file goes
        # Then: rn stops, naming the path and saying to name it from the top of the repository
        for document in ["/etc/a.md", "../a.md", "docs/../../a.md", ".."]:
            with self.subTest(document=document):
                self.assertEqual(
                    self.rn("decisions", SESSION, document),
                    (1, f"{document} is outside the repository; name a path from its top\n"),
                )


class TestTask(RepoTest):
    def given(self, *paths):
        for path in paths:
            self.write(path, "x\n")

    def task(self, *flags, leave_out=()):
        self.given(CHECKLIST, DECISIONS)
        argv = ["task", SESSION]
        for flag, value in REQUIRED.items():
            if flag not in leave_out:
                argv += [flag, value]
        return self.rn(*argv, *flags)

    def written(self, out):
        return self.read_json(out.split("\n")[0][len("in: ") :])

    def test_a_task_with_every_flag_is_written_as_a_ccs_holding_each_value(self):
        # Given: every flag given once
        # When: rn writes the task
        # Then: the CCS holds each value in its part, and turn's parts empty
        self.given("Makefile", "CONTRIBUTING.md")
        self.task(
            "--use",
            "to run the project",
            "--reference",
            "Makefile",
            "--opens",
            "CONTRIBUTING.md",
            "--language",
            "English",
        )
        self.assertEqual(
            self.read_json(SESSION + "/tasks/setup-1.json"),
            {
                "focal_entities": [{"deliverable": "docs/setup.md"}, {"receiver": "a developer"}],
                "goal_orientation": [
                    {"use": "to run the project"},
                    {"acceptance": "they run the tests"},
                ],
                "retrieved_artifacts": [
                    {"checklist": CHECKLIST},
                    {"decisions": DECISIONS},
                    {"reference": "Makefile"},
                    {"receiver_opens": "CONTRIBUTING.md"},
                ],
                "constraints": [{"language": "English"}],
                "predictive_cue": [],
                "uncertainty_signal": [],
                "semantic_gist": [],
                "relational_map": [],
                "episodic_trace": [],
            },
        )

    def test_a_written_task_prints_where_the_ccs_is_and_where_turn_writes_it_back(self):
        # Given: a task given the flags it needs
        # When: rn writes the task
        # Then: rn prints, as in and out, where the CCS is and where turn writes its CCS back,
        #   and ends well
        self.assertEqual(
            self.task(),
            (0, f"in: {SESSION}/tasks/setup-1.json\nout: {SESSION}/tasks/setup-1.back.json\n"),
        )

    def test_the_ccs_is_json_indented_by_one_keeping_non_ascii_and_ending_in_a_newline(self):
        # Given: a language named in Japanese
        # When: rn writes the task
        # Then: the file is the CCS as JSON indented by one space, the Japanese kept as it is,
        #   ending in a newline
        self.task("--language", "日本語")
        text = self.read_text(SESSION + "/tasks/setup-1.json")
        self.assertIn('\n "constraints": [\n  {\n   "language": "日本語"\n  }\n ],\n', text)
        self.assertTrue(text.endswith("}\n"))

    def test_use_and_language_left_out_leave_no_entry(self):
        # Given: a task given without a use or a language
        # When: rn writes the task
        # Then: the CCS holds the acceptance alone in its goal, and no constraint
        self.task()
        ccs = self.read_json(SESSION + "/tasks/setup-1.json")
        self.assertEqual(ccs["goal_orientation"], [{"acceptance": "they run the tests"}])
        self.assertEqual(ccs["constraints"], [])

    def test_several_deliverables_are_kept_in_order_and_the_first_names_the_task(self):
        # Given: a task given two deliverables after one flag
        # When: rn writes the task
        # Then: the CCS lists both in the order given before the receiver, and the task is named
        #   after the first
        self.task("--deliverable", "src/tidy.py", "tests/test_tidy.py", leave_out=["--deliverable"])
        self.assertEqual(
            self.read_json(SESSION + "/tasks/tidy-1.json")["focal_entities"],
            [
                {"deliverable": "src/tidy.py"},
                {"deliverable": "tests/test_tidy.py"},
                {"receiver": "a developer"},
            ],
        )

    def test_a_flag_given_twice_adds_to_what_it_was_given_before(self):
        # Given: the deliverable, the checklist, the reference or the file the receiver opens
        #   given twice, one path each
        # When: rn writes the task
        # Then: the CCS holds both paths in the order given
        self.given("one.md", "two.md")
        for flag, kind in [
            ("--deliverable", "deliverable"),
            ("--checklist", "checklist"),
            ("--reference", "reference"),
            ("--opens", "receiver_opens"),
        ]:
            with self.subTest(flag=flag):
                _, out = self.task(flag, "one.md", flag, "two.md", leave_out=[flag])
                self.assertEqual(
                    [e[kind] for part in self.written(out).values() for e in part if kind in e],
                    ["one.md", "two.md"],
                )

    def test_a_second_task_takes_the_next_number_and_leaves_the_first(self):
        # Given: a first task and the CCS turn wrote back for it
        # When: rn writes a second task for the same deliverable
        # Then: it is numbered 2, and the first task and turn's CCS are left as they were
        self.task()
        self.write(SESSION + "/tasks/setup-1.back.json", "back\n")
        first = self.read_text(SESSION + "/tasks/setup-1.json")
        _, out = self.task()
        self.assertEqual(
            out, f"in: {SESSION}/tasks/setup-2.json\nout: {SESSION}/tasks/setup-2.back.json\n"
        )
        self.assertEqual(self.read_text(SESSION + "/tasks/setup-1.json"), first)
        self.assertEqual(self.read_text(SESSION + "/tasks/setup-1.back.json"), "back\n")

    def test_a_task_missing_a_required_flag_prints_the_usage(self):
        # Given: a task given without one of the deliverable, the receiver, the acceptance, the
        #   checklist or the decisions
        # When: rn is asked to write it
        # Then: it prints the usage and stops
        for flag in REQUIRED:
            with self.subTest(left_out=flag):
                self.assertEqual(usage(self.task(leave_out=[flag])), (1, USAGE))

    def test_a_named_file_not_there_stops_before_anything_is_written(self):
        # Given: a checklist, the decisions, a reference or a file the receiver opens that does
        #   not exist
        # When: rn is asked to write the task
        # Then: rn stops, naming the path and saying to name it from the top of the repository,
        #   and writes no task
        for flag in ["--checklist", "--decisions", "--reference", "--opens"]:
            with self.subTest(flag=flag):
                self.assertEqual(
                    self.task(flag, "missing.md"),
                    (
                        1,
                        (
                            "missing.md does not exist; name it by its path from the top of the "
                            "repository\n"
                        ),
                    ),
                )
                self.assertFalse(os.path.exists(SESSION + "/tasks"))
