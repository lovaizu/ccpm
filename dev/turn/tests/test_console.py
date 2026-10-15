import contextlib
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

import posttooluse
from brief import SCRIPT
from helpers import ROOT, Repo, fill, form, run, started

WORK = "# Note\n\nRun make.\n"
AIM = "a new teammate can start work alone"
PLAN = "Plan: 1 write → 2 read → 3 check"
SECOND = ".turn/out/2"
LICENSE = "Which license is the note under? The notes do not say."
WAY = {
    "aim": "the teammate takes it in at a glance",
    "way": "cut it to one line",
    "reach": "1-3",
    "in": "the work",
    "making": "",
}


def bash(command, stdout=""):
    return {
        "hook_event_name": "PostToolUse",
        "tool_name": "Bash",
        "tool_input": {"command": command},
        "tool_response": {"stdout": stdout, "stderr": ""},
    }


def post(repo, session="s1", **data):
    """Runs the PostToolUse entry as Claude Code does after a Bash call; returns its exit code, the
    lines it showed the user and what it told Claude."""
    data.update(cwd=repo.path, session_id=session)
    out, err = io.StringIO(), io.StringIO()
    with (
        mock.patch("sys.stdin", io.StringIO(json.dumps(data))),
        contextlib.redirect_stdout(out),
        contextlib.redirect_stderr(err),
    ):
        code = posttooluse.main()
    shown = json.loads(out.getvalue())["systemMessage"].splitlines() if out.getvalue() else []
    return code, shown, err.getvalue()


def met(repo, role, f1=True, work=".turn/out"):
    fill(
        repo,
        form(role, work),
        {
            "note B-1": {"met": True, "lines": "3", "note": "the step is given"},
            "note F-1": {"met": True, "lines": "1-3", "note": "three lines"}
            if f1
            else {"met": False},
        },
    )


class Console(unittest.TestCase):
    """The console shows how far a run has come, each line once, by step."""

    def setUp(self):
        self.repo = Repo()
        self.home = tempfile.TemporaryDirectory()
        self.env = mock.patch.dict(os.environ, {"HOME": self.home.name})
        self.env.start()
        started(self.repo)

    def tearDown(self):
        self.env.stop()
        self.repo.close()
        self.home.cleanup()

    def say(self, *args):
        code, out = run(self.repo, *args)
        self.assertEqual(code, 0, out)
        return out.splitlines()

    def shown(self):
        code, lines, told = post(self.repo, **bash("jq . .turn/out/questions.json"))
        self.assertEqual(code, 0, told)
        return lines

    def ran(self, role):
        folder = os.path.join(self.home.name, ".claude/projects/p/s1/subagents")
        os.makedirs(folder, exist_ok=True)
        with open(os.path.join(folder, f"agent-{role}.meta.json"), "w") as f:
            f.write(f'{{"agentType": "turn:{role}"}}')
        open(os.path.join(folder, f"agent-{role}.jsonl"), "w").close()

    def read(self, f1=True, work=".turn/out"):
        """The run's work made, seen given, read and decided, with F-1 met or not."""
        met(self.repo, "hand-on", work=work)
        if not os.path.isfile(os.path.join(self.repo.path, work, "work/docs/note.md")):
            self.repo.write(f"{work}/work/docs/note.md", WORK)
        self.say("brief", work, "first-user")
        self.ran("first-user")
        fill(self.repo, form("first-user", work), {"note B-1": {"took": "run make", "lines": "3"}})
        met(self.repo, "orchestrator", f1, work)

    def test_the_aim_is_shown_with_the_plan_before_anything_is_written(self):
        # Given: a run just started, with a question the sources leave open
        fill(self.repo, ".turn/out/questions.json", [{"question": LICENSE, "ask": True}])
        # When: the orchestrator runs a command before it sets the aim
        # Then: the user is shown the plan
        self.assertEqual(self.shown(), [PLAN])
        # When: the orchestrator sets what the work will let its receiver do
        self.say("aim", ".turn/out", AIM)
        # Then: the user is shown the aim, and not the question, which waits for the end
        self.assertEqual(self.shown(), [f"  1 write   To make: {AIM}"])

    def test_a_question_naming_an_item_is_not_shown(self):
        # Given: a question that names an item of the list
        fill(
            self.repo,
            ".turn/out/questions.json",
            [{"question": f"{LICENSE} (note F-1)", "ask": True}],
        )
        # When: the orchestrator runs its next command
        code, lines, told = post(self.repo, **bash("jq . .turn/out/questions.json"))
        # Then: nothing is shown, and the orchestrator is told to put it in plain words
        self.assertEqual((code, lines), (2, []))
        self.assertIn("turn: question 1: names note F-1", told)

    def test_no_work_is_written_before_its_aim_is_shown(self):
        # Given: a run just started, with no aim set
        # When: the generator's brief is asked for
        code, out = run(self.repo, "brief", ".turn/out", "generator")
        # Then: it is refused, naming the step that sets the aim
        self.assertEqual(code, 1)
        self.assertIn("step 4: set the aim with `up.py aim .turn/out <text>`", out)
        # Given: the aim set
        self.say("aim", ".turn/out", AIM)
        # When: the generator's brief is asked for again
        # Then: it is made
        self.assertEqual(
            self.say("brief", ".turn/out", "generator"), [".turn/out/generator-brief.json"]
        )

    def test_each_line_is_shown_once_as_the_run_reaches_it(self):
        # Given: the aim shown
        self.say("aim", ".turn/out", AIM)
        self.shown()
        # When: the console is asked for with nothing new
        # Then: nothing is shown again
        self.assertEqual(self.shown(), [])
        # When: a question is raised in the making
        fill(self.repo, ".turn/out/questions.json", [{"question": LICENSE, "ask": True}])
        # Then: nothing is shown while the run works
        self.assertEqual(self.shown(), [])
        # When: the work is handed to the first user
        met(self.repo, "hand-on")
        self.repo.write(".turn/out/work/docs/note.md", WORK)
        self.say("brief", ".turn/out", "first-user")
        # Then: the reading is shown
        self.assertEqual(self.shown(), ["  2 read    Read as a new teammate."])
        # When: the first user hands back its reading
        fill(self.repo, form("first-user"), {"note B-1": {"took": "run make", "lines": "3"}})
        # Then: nothing new is shown
        self.assertEqual(self.shown(), [])

    def check_shown(self, f1, learned):
        self.read(f1=f1)
        fill(self.repo, form("learner"), learned)
        return [x for x in self.shown() if x.startswith("  3 check") or "⚠️" in x]

    def test_the_check_shows_nothing_missing_when_every_item_is_met(self):
        # Given: the work read, with every item decided met
        # When: the console is asked for
        # Then: nothing missing is shown
        self.assertEqual(self.check_shown(True, {}), ["  3 check   ✅ Nothing missing."])

    def test_the_check_shows_in_plain_words_what_is_still_to_give_once_learned(self):
        # Given: the work read, with an item not met and no way learned yet
        # When: the console is asked for
        # Then: no check is shown yet
        self.assertEqual(self.check_shown(False, {}), [])
        # Given: the learner's way for it
        fill(self.repo, form("learner"), {"note F-1": WAY})
        # When: the console is asked for
        lines = self.shown()
        # Then: what the work is still to give is shown in the learner's words, with no item named
        self.assertEqual(lines, [f"  3 check   ⚠️ Not yet: {WAY['aim']}"])

    def second(self):
        """The first round ended on a way in the work, its lines shown, and the second begun."""
        self.say("aim", ".turn/out", AIM)
        self.read(f1=False)
        fill(self.repo, form("learner"), {"note F-1": WAY})
        self.shown()
        return self.say("end", ".turn/out")

    def test_the_second_reading_reads_the_work_again(self):
        # Given: the first round ended on a way in the work
        self.second()
        # When: the second round's aim is set, and its work read
        self.say("aim", SECOND, "the same, cut to one line")
        self.read(work=SECOND)
        code, lines, told = post(self.repo, **bash(f"jq . {SECOND}/questions.json"))
        # Then: the user is shown the plan, its aim, and that the work is read again as the same
        # receiver
        self.assertEqual(code, 0, told)
        self.assertEqual(
            lines[:4],
            [
                PLAN,
                "",
                "  1 write   To make: the same, cut to one line",
                "  2 read    Read again, as a new teammate.",
            ],
        )

    def test_the_end_of_the_first_reading_shows_the_second_begin(self):
        # Given: the first round's lines shown, with a way in the work
        # When: the first round ends
        out = "\n".join(self.second())
        command = f'python3 "{SCRIPT}" end .turn/out; echo "EXIT $?"'
        code, lines, told = post(self.repo, **bash(command, out + "\nEXIT 0"))
        # Then: the user is shown the second round's plan, and not where the work is
        self.assertEqual(code, 0, told)
        self.assertEqual(lines, [PLAN])

    def ended(self, *args):
        out = "\n".join(self.say(*args))
        command = f'python3 "{SCRIPT}" {" ".join(args)}; echo "EXIT $?"'
        code, lines, told = post(self.repo, **bash(command, out + "\nEXIT 0"))
        self.assertEqual(code, 0, told)
        again = post(self.repo, **bash(command, out + "\nEXIT 0"))[1]
        self.assertEqual(again, [])
        return lines

    def test_the_end_says_where_the_work_is(self):
        # Given: the work read, with every item decided met
        self.read()
        # When: the run ends
        # Then: the user is shown the next move and where the work is, once, and nothing else the
        # command printed
        self.assertEqual(self.ended("end", ".turn/out"), ["done", "The work is at docs/note.md."])

    def test_the_end_asks_the_user_each_question_left_open(self):
        # Given: the work read with every item met, and a question left open
        fill(self.repo, ".turn/out/questions.json", [{"question": LICENSE, "ask": True}])
        self.read()
        # When: the run ends
        # Then: the user is shown where the work is and the question, once
        self.assertEqual(
            self.ended("end", ".turn/out"),
            ["The work is at docs/note.md, waiting on you for one point.", f"❓ {LICENSE}"],
        )

    def test_the_end_says_where_the_work_is_and_that_the_ccs_holds_what_it_lacks(self):
        # Given: the second round's work read, with an item still without a Good, given a way in
        # the work
        self.second()
        self.say("aim", SECOND, AIM)
        self.read(f1=False, work=SECOND)
        fill(self.repo, form("learner", SECOND), {"note F-1": WAY})
        # When: the run ends
        # Then: the user is shown where the work is, and that the CCS holds what it does not give
        # yet
        self.assertEqual(
            self.ended("end", SECOND),
            ["The work is at docs/note.md, with what it does not give yet in the CCS."],
        )

    def test_a_stop_says_where_the_run_was(self):
        # Given: a run stopped on its aim
        self.say("aim", ".turn/out", AIM)
        # When: the orchestrator stops the run
        # Then: the user is shown where it was and where its CCS is, once
        self.assertEqual(self.ended("stop", ".turn/out"), ["stopped: write — CCS: out.json"])

    def test_nothing_is_shown_outside_the_run(self):
        self.say("aim", ".turn/out", AIM)
        cases = [
            ("another session", "s2", bash("jq . .turn/out/questions.json")),
            ("another tool", "s1", {"tool_name": "Read", "tool_input": {}}),
        ]
        for name, session, data in cases:
            with self.subTest(name):
                # Given: the aim set, and a tool call outside the run's console
                # When: the call is made
                code, lines, _ = post(self.repo, session, **data)
                # Then: nothing is shown
                self.assertEqual((code, lines), (0, []))

    def test_a_command_of_an_agent_shows_it_nothing_and_leaves_the_lines_for_the_user(self):
        # Given: the aim set, and an agent of the run running a shell command
        self.say("aim", ".turn/out", AIM)
        data = dict(
            bash("python3 up.py check .turn/out first-user"),
            agent_id="a1",
            agent_type="turn:first-user",
        )
        # When: the command has run
        code, lines, _ = post(self.repo, **data)
        # Then: the agent is shown nothing, and the user is shown the lines at the orchestrator's next command
        self.assertEqual((code, lines), (0, []))
        self.assertEqual(self.shown(), [PLAN, "", f"  1 write   To make: {AIM}"])

    def test_the_entry_run_as_claude_code_runs_it_shows_the_user_the_new_lines(self):
        # Given: the hook's entry file, and the aim set
        self.say("aim", ".turn/out", AIM)
        entry = os.path.join(ROOT, "turn", "hooks", "posttooluse.py")
        data = dict(bash("jq . .turn/out/questions.json"), cwd=self.repo.path, session_id="s1")
        # When: Claude Code runs it after a Bash call of the orchestrator
        done = subprocess.run(
            [sys.executable, entry],
            check=False,
            input=json.dumps(data),
            capture_output=True,
            text=True,
        )
        # Then: it hands Claude Code the new lines to show the user
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertIn(f"To make: {AIM}", json.loads(done.stdout)["systemMessage"])


if __name__ == "__main__":
    unittest.main()
