import contextlib
import io
import json
import os
import unittest
from unittest import mock

import pretooluse
from helpers import ROOT, Repo, ccs, fill, started

UP = os.path.join(ROOT, "turn", "scripts", "up.py")


class Session:
    """What Claude Code hands turn's PreToolUse hook in the session of an open run."""

    def __init__(self, repo, session="s1"):
        self.repo = repo
        self.session = session
        self.transcript = os.path.join(repo.path, "projects", session + ".jsonl")

    def pre(self, tool, given, agent=None):
        """Runs the PreToolUse entry before a tool call of the orchestrator, or of the agent named;
        returns its exit code and what it told Claude."""
        data = {
            "cwd": self.repo.path,
            "session_id": self.session,
            "transcript_path": self.transcript,
            "hook_event_name": "PreToolUse",
            "tool_name": tool,
            "tool_input": given,
        }
        if agent:
            data.update(agent_id="a1", agent_type=agent)
        err = io.StringIO()
        with (
            mock.patch("sys.stdin", io.StringIO(json.dumps(data))),
            contextlib.redirect_stderr(err),
        ):
            code = pretooluse.main()
        return code, err.getvalue()


def opened(repo):
    """An open run whose CCS also names a reference folder and a page the receiver opens."""
    repo.write("docs/guide/a.md", "A\n")
    repo.write("CONTRIBUTING.md", "Ask first.\n")
    repo.write("README.md", "# Other\n")
    c = ccs()
    c["retrieved_artifacts"] += [{"reference": "docs/guide"}, {"receiver_opens": "CONTRIBUTING.md"}]
    started(repo, c)


class OrchestratorReadsItsInputs(unittest.TestCase):
    """The orchestrator reads only the run's inputs, turn's own files and the run's evidence."""

    def setUp(self):
        self.repo = Repo()
        opened(self.repo)
        self.claude = Session(self.repo)

    def tearDown(self):
        self.repo.close()

    def at(self, rel):
        return os.path.join(self.repo.path, rel)

    def test_a_read_of_an_input_turn_s_files_or_the_evidence_goes_on(self):
        cases = [
            ("the CCS", "Read", {"file_path": self.at("in.json")}),
            ("the checklist", "Read", {"file_path": self.at("checklists/note.md")}),
            ("the content", "Read", {"file_path": "notes.md"}),
            ("a file in a reference folder", "Read", {"file_path": self.at("docs/guide/a.md")}),
            ("the work", "Read", {"file_path": self.at(".turn/out/work/docs/note.md")}),
            ("turn's own file", "Read", {"file_path": UP}),
            (
                "a tool's output Claude Code kept",
                "Read",
                {"file_path": self.at("projects/s1/tool-results/b1.txt")},
            ),
            ("a search in a reference", "Grep", {"pattern": "A", "path": self.at("docs/guide")}),
            ("a search in the evidence", "Glob", {"pattern": "*.json", "path": ".turn/out"}),
        ]
        for name, tool, given in cases:
            with self.subTest(name):
                # Given: an open run
                # When: the orchestrator reads or searches there
                code, said = self.claude.pre(tool, given)
                # Then: it goes on
                self.assertEqual((code, said), (0, ""))

    def test_a_read_outside_the_inputs_is_stopped_saying_why_and_what_may_be_read(self):
        cases = [
            ("a file not given", "Read", {"file_path": self.at("README.md")}),
            ("where the work goes", "Read", {"file_path": self.at("docs/note.md")}),
            ("a page the receiver opens", "Read", {"file_path": self.at("CONTRIBUTING.md")}),
            ("a search over the repository", "Grep", {"pattern": "x"}),
            ("a search over the repository", "Glob", {"pattern": "**/*.md"}),
            ("beside the run's evidence", "Read", {"file_path": self.at(".turn/old/note.md")}),
        ]
        for name, tool, given in cases:
            with self.subTest(name):
                # Given: an open run
                # When: the orchestrator reads or searches elsewhere
                code, said = self.claude.pre(tool, given)
                # Then: it is stopped, told which steps, that it works from its inputs alone, and
                # which they are
                self.assertEqual(code, 2)
                self.assertIn("steps 2 to 12: the orchestrator reads only its inputs", said)
                self.assertIn("so the work is made without bias from what was not given", said)
                self.assertIn("in.json, checklists/note.md, notes.md, docs/guide, .turn/out", said)

    def test_nothing_is_stopped_in_another_session(self):
        # Given: an open run, and another session in the same repository
        other = Session(self.repo, "s2")
        # When: that session reads a file the run was not given
        done = other.pre("Read", {"file_path": self.at("README.md")})
        # Then: it goes on
        self.assertEqual(done, (0, ""))


class AgentReadsItsBrief(unittest.TestCase):
    """Each agent of a run reads only what its brief names, but where the work goes, and the
    brief."""

    def setUp(self):
        self.repo = Repo()
        opened(self.repo)
        self.claude = Session(self.repo)
        fill(
            self.repo,
            ".turn/out/first-user-brief.json",
            {
                "work": [".turn/out/work/docs/note.md"],
                "deliverable": ["docs/note.md"],
                "opens": ["CONTRIBUTING.md"],
                "list": self.at(".turn/out/list.json"),
                "form": ".turn/out/first-user.json",
            },
        )

    def tearDown(self):
        self.repo.close()

    def at(self, rel):
        return os.path.join(self.repo.path, rel)

    def test_a_read_of_what_the_brief_names_goes_on(self):
        for path in (
            ".turn/out/first-user-brief.json",
            ".turn/out/work/docs/note.md",
            "CONTRIBUTING.md",
            ".turn/out/list.json",
        ):
            with self.subTest(path):
                # Given: the first user's brief
                # When: the first user reads a file it names
                code, said = self.claude.pre(
                    "Read", {"file_path": self.at(path)}, agent="turn:first-user"
                )
                # Then: it goes on
                self.assertEqual((code, said), (0, ""))

    def test_a_read_of_what_the_brief_does_not_name_is_stopped_saying_what_may_be_read(self):
        for path in ("docs/note.md", "notes.md", ".turn/out/generator.json", "README.md"):
            with self.subTest(path):
                # Given: the first user's brief, which does not name the file
                # When: the first user reads it
                code, said = self.claude.pre(
                    "Read", {"file_path": self.at(path)}, agent="turn:first-user"
                )
                # Then: it is stopped, told why and what its brief lets it read
                self.assertEqual(code, 2)
                self.assertIn("step 9: the first user reads only its inputs", said)
                self.assertIn("so the work is made without bias from what was not given", said)
                self.assertIn(".turn/out/work/docs/note.md, CONTRIBUTING.md", said)
                self.assertNotIn(" docs/note.md,", said)

    def test_an_agent_without_a_brief_reads_only_turn_s_files(self):
        # Given: no brief written for the learner
        # When: the learner reads the work, and turn's script
        done = [
            self.claude.pre("Read", {"file_path": self.at(p)}, agent="turn:learner")[0]
            for p in (".turn/out/work/docs/note.md", UP)
        ]
        # Then: the work is stopped, and turn's script goes on
        self.assertEqual(done, [2, 0])

    def test_an_agent_s_shell_stays_open(self):
        # Given: an open run
        # When: the generator runs any shell command
        done = self.claude.pre("Bash", {"command": "cat README.md && make test"}, "turn:generator")
        # Then: it goes on
        self.assertEqual(done, (0, ""))


class OrchestratorShell(unittest.TestCase):
    """The orchestrator's shell runs only turn's script, and jq, mv and cd on the run's files."""

    def setUp(self):
        self.repo = Repo()
        opened(self.repo)
        self.claude = Session(self.repo)

    def tearDown(self):
        self.repo.close()

    def test_turn_s_script_and_jq_on_the_run_s_files_go_on(self):
        for command in (
            f'python3 "{UP}" brief .turn/out generator',
            f'python3 {UP} aim .turn/out "the reader starts alone"',
            (
                "jq '.\"note B-1\".met = true' .turn/out/hand-on.json > .turn/out/h.tmp"
                " && mv .turn/out/h.tmp .turn/out/hand-on.json"
            ),
            (
                "cd .turn/out && jq --arg q 'why?' '. + [{question: $q,\n ask: true}]' questions.json"
                " > q.tmp && mv q.tmp questions.json"
            ),
            "jq -n --slurpfile g .turn/out/generator.json '$g[0]' > .turn/out/o.tmp",
            "jq . in.json notes.md docs/guide/a.md",
            f'cd "{self.repo.path}" && jq -f .turn/out/f.jq .turn/out/list.json',
        ):
            with self.subTest(command):
                # Given: an open run
                # When: the orchestrator runs the command
                code, said = self.claude.pre("Bash", {"command": command})
                # Then: it goes on
                self.assertEqual((code, said), (0, ""))

    def test_any_other_command_is_stopped_saying_what_the_orchestrator_runs(self):
        for command in (
            "cat .turn/out/note.md",
            "sed -n 1,9p notes.md",
            "jq . README.md",
            "jq . .turn/out/list.json 2>/dev/null",
            "jq --rawfile r README.md -n '$r'",
            "jq . notes.md > notes.md",
            "mv .turn/out/note.md docs/note.md",
            "cd .. && jq . x.json",
            f'python3 "{UP}" console .turn/out\ncat README.md',
            "jq -f README.md in.json",
            "jq -f .turn/out/f.jq README.md",
            'jq "$(cat README.md)" in.json',
            f'U="python3 {UP}"; $U brief .turn/out generator',
            "python3 other.py",
            "(cat README.md)",
            "jq . in.json --arg q",
            f'python3 "{UP}" end .turn/out; echo "exit=$?"',
            "jq '.a",
        ):
            with self.subTest(command):
                # Given: an open run
                # When: the orchestrator runs the command
                code, said = self.claude.pre("Bash", {"command": command})
                # Then: it is stopped, told what it may run and to read files with Read
                self.assertEqual(code, 2)
                self.assertIn(
                    "steps 1 to 14: the orchestrator runs only turn's up.py, and jq, mv and cd on "
                    "the run's files",
                    said,
                )
                self.assertIn("read a file with Read", said)

    def test_the_hook_is_called_before_every_read_and_search(self):
        # Given: the hooks Claude Code runs for turn
        with open(os.path.join(ROOT, "turn", "hooks", "hooks.json")) as f:
            matcher = json.load(f)["hooks"]["PreToolUse"][0]["matcher"].split("|")
        # When: a file is read or searched
        # Then: the PreToolUse entry is run before it
        for tool in ("Read", "Grep", "Glob"):
            self.assertIn(tool, matcher)


if __name__ == "__main__":
    unittest.main()
