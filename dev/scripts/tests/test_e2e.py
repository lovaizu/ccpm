"""The tests of dev/scripts/e2e.py: it reads an E2E test file, runs the test in a fresh clone of
the test's repository with the plugins under test, plays the person with a stand-in that holds the
test's intent and reads only the screen, keeps the run's records, and removes what it made. Each
test runs it with claude_double.py on the PATH as `claude` and a local repository in place of
GitHub's."""

from __future__ import annotations

import contextlib
import io
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import tempfile
from typing import Any
from unittest import mock

from helpers import GIT_ENV, FolderTest, without

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

import e2e

DOUBLE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "claude_double.py")
TOKEN = "sk-ant-oat01-e2e-token"
INTENT = "You want the entries of CHANGELOG.md written."
COMMITS = [
    {"message": "Add tally", "files": {"tally.py": "print(1)\n"}},
    {"message": "Add the plugin", "files": {"p/plugin.json": {"from": "src/plugin.json"}}},
]


def said(text: str) -> dict[str, Any]:
    """A line of stream-json in which the main conversation writes the text."""
    content = [{"type": "text", "text": text}]
    return {"type": "assistant", "parent_tool_use_id": None, "message": {"content": content}}


def used(tool: str, tool_input: dict[str, Any], parent: str | None = None) -> dict[str, Any]:
    """A line of stream-json in which the main conversation, or the subagent of the parent's
    start, calls the tool."""
    content = [{"type": "tool_use", "id": "toolu_1", "name": tool, "input": tool_input}]
    return {"type": "assistant", "parent_tool_use_id": parent, "message": {"content": content}}


def refused(text: Any) -> dict[str, Any]:
    """A line of stream-json that gives the main conversation's call an error."""
    content = [{"type": "tool_result", "tool_use_id": "toolu_1", "is_error": True, "content": text}]
    return {"type": "user", "parent_tool_use_id": None, "message": {"content": content}}


class E2ERunnerTest(FolderTest):
    def setUp(self) -> None:
        super().setUp()
        self.remote = os.path.join(self.base, "remote.git")
        env = dict(os.environ, **GIT_ENV)
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", self.remote], check=True)
        seed = os.path.join(self.base, "seed")
        subprocess.run(["git", "clone", "-q", self.remote, seed], env=env, check=True)
        self.write(os.path.join(seed, "README.md"), "# Playground\n")
        for args in (["add", "-A"], ["commit", "-q", "-m", "Initial commit"], ["push", "-q"]):
            subprocess.run(["git", *args], cwd=seed, env=env, check=True)
        shutil.rmtree(seed)
        self.write("src/plugin.json", '{"name": "p"}\n')
        self.write_json("dev/e2e/commits.json", COMMITS)
        self.fields: dict[str, Any] = {
            "intent": INTENT,
            "repository": self.remote,
            "commits": "dev/e2e/commits.json",
            "plugin_dirs": ["{top}/plugins/lane", "{clone}/p"],
            "turns": 3,
            "records": "records",
            "push": False,
        }
        # The PATH holds the double as `claude`, and no other, so no test reaches the real one.
        path = without(os.environ["PATH"], "claude", os.path.join(self.base, "path"))
        self.bin = os.path.join(self.base, "bin")
        os.makedirs(self.bin)
        os.symlink(DOUBLE, os.path.join(self.bin, "claude"))
        self.temp = os.path.join(self.base, "temp")
        os.makedirs(self.temp)
        self.env = {
            **GIT_ENV,
            "PATH": self.bin + os.pathsep + path,
            "CLAUDE_CODE_OAUTH_TOKEN": TOKEN,
            "CLAUDE_CODE_SESSION_ID": "the-callers-session",
            "DOUBLE_PLAN": os.path.join(self.base, "plan.json"),
        }
        patched = mock.patch.dict(os.environ, self.env)
        patched.start()
        self.addCleanup(patched.stop)
        os.environ.pop("CLAUDE_CONFIG_DIR", None)
        self.addCleanup(setattr, tempfile, "tempdir", tempfile.tempdir)
        tempfile.tempdir = self.temp

    def plan(self, stand_in: list[Any], turns: list[dict[str, Any]]) -> None:
        self.write_json("plan.json", {"stand_in": stand_in, "turns": turns})

    def run_test(self) -> tuple[int, str, str]:
        self.write_json("dev/e2e/main.json", self.fields)
        return self.main("run", "dev/e2e/main.json")

    def main(self, *argv: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = e2e.main(list(argv))
        return code, out.getvalue(), err.getvalue()

    def calls(self, stand_in: bool) -> list[dict[str, Any]]:
        with open("calls.jsonl", encoding="utf-8") as f:
            calls = [json.loads(line) for line in f]
        return [call for call in calls if call["stand_in"] == stand_in]

    def records(self) -> str:
        (name,) = os.listdir("records/main")
        return os.path.join("records", "main", name)

    def kept(self, name: str) -> list[dict[str, Any]]:
        with open(os.path.join(self.records(), name), encoding="utf-8") as f:
            return [json.loads(line) for line in f]

    def refuses(self, why: str) -> None:
        code, _, err = self.run_test()
        self.assertEqual(code, 1, err)
        self.assertIn(why, err)
        self.assertEqual(os.listdir(self.temp), [], "the test left its temporary folder")

    # Refusals

    def test_a_test_without_the_developers_login_is_refused(self):
        del os.environ["CLAUDE_CODE_OAUTH_TOKEN"]
        self.refuses("CLAUDE_CODE_OAUTH_TOKEN")

    def test_a_test_file_that_isnt_json_is_refused(self):
        self.write("dev/e2e/main.json", "{")
        code, _, err = self.main("run", "dev/e2e/main.json")
        self.assertEqual(code, 1)
        self.assertIn("dev/e2e/main.json", err)

    def test_a_test_file_that_isnt_an_object_is_refused(self):
        self.write_json("dev/e2e/main.json", [self.fields])
        code, _, err = self.main("run", "dev/e2e/main.json")
        self.assertEqual(code, 1)
        self.assertIn("isn't a JSON object", err)

    def test_a_test_file_missing_a_field_is_refused(self):
        del self.fields["intent"]
        self.refuses("`intent`")

    def test_a_field_of_the_wrong_type_is_refused(self):
        self.fields["plugin_dirs"] = "{top}/plugins/lane"
        self.refuses("`plugin_dirs`")

    def test_a_plugin_dir_that_isnt_text_is_refused(self):
        self.fields["plugin_dirs"] = ["{top}/plugins/lane", 1]
        self.refuses("`plugin_dirs` as a list of text")

    def test_a_push_that_isnt_true_or_false_is_refused(self):
        self.fields["push"] = "yes"
        self.refuses("`push`")

    def test_a_test_of_one_turn_runs(self):
        self.fields["turns"] = 1
        self.plan([{"done": False, "prompt": "go"}], [{}])
        code, _, err = self.run_test()
        self.assertEqual(code, 0, err)

    def test_a_test_of_no_turn_is_refused(self):
        self.fields["turns"] = 0
        self.refuses("`turns`")

    def test_a_commits_file_out_of_form_is_refused(self):
        self.write_json("dev/e2e/commits.json", [{"message": "Add tally", "files": {"a": 1}}])
        self.refuses("dev/e2e/commits.json")

    def test_commits_that_arent_a_list_are_refused(self):
        self.write_json("dev/e2e/commits.json", COMMITS[0])
        self.refuses("dev/e2e/commits.json")

    def test_a_commit_without_a_message_is_refused(self):
        self.write_json("dev/e2e/commits.json", [{"files": {}}])
        self.refuses("dev/e2e/commits.json")

    def test_a_repository_that_cant_be_cloned_is_refused(self):
        self.fields["repository"] = os.path.join(self.base, "none.git")
        self.refuses("none.git")

    def test_a_stand_in_reply_out_of_form_is_refused(self):
        self.plan(["not json"], [])
        self.refuses("stand-in")

    def test_wrong_words_give_2(self):
        code, _, err = self.main("go")
        self.assertEqual(code, 2)
        self.assertIn("e2e.py run <E2E test file>", err)

    # The clone and the plugins

    def test_the_test_runs_in_a_clone_with_the_tests_commits(self):
        self.plan([{"done": False, "prompt": "/lane:up p"}, {"done": True}], [{}])
        self.run_test()
        (turn,) = self.calls(stand_in=False)
        self.assertEqual(turn["log"], ["Add the plugin", "Add tally", "Initial commit"])

    def test_a_file_of_a_commit_can_be_copied_from_the_repository(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{"show": ["p/plugin.json"]}])
        self.run_test()
        (turn,) = self.calls(stand_in=False)
        self.assertEqual(turn["shown"], {"p/plugin.json": '{"name": "p"}\n'})

    def remote_branches(self) -> str:
        return subprocess.run(
            ["git", "branch", "--list"], cwd=self.remote, capture_output=True, text=True, check=True
        ).stdout

    def test_a_push_from_the_clone_fails(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        self.run_test()
        (turn,) = self.calls(stand_in=False)
        self.assertFalse(turn["pushed"])
        self.assertNotIn("pushed", self.remote_branches())

    def test_a_test_that_pushes_reaches_the_repository_and_removes_its_branches_after(self):
        # Given a test whose plugin pushes its branch, as rn pushes its work for a pull request,
        # When the run pushes a branch and the test ends,
        # Then the push went through, and the repository holds only the branches it held before.
        self.fields["push"] = True
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        code, _, err = self.run_test()
        self.assertEqual(code, 0, err)
        (turn,) = self.calls(stand_in=False)
        self.assertTrue(turn["pushed"])
        self.assertEqual(self.remote_branches(), "* main\n")

    def test_a_test_that_pushes_leaves_a_branch_the_repository_held_before(self):
        subprocess.run(["git", "branch", "pushed", "main"], cwd=self.remote, check=True)
        self.fields["push"] = True
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        self.run_test()
        self.assertIn("pushed", self.remote_branches())

    def test_each_turn_runs_claude_on_opus_with_the_plugins_under_test(self):
        self.plan([{"done": False, "prompt": "/lane:up p"}, {"done": True}], [{}])
        self.run_test()
        (turn,) = self.calls(stand_in=False)
        argv = turn["argv"]
        self.assertEqual(argv[:3], ["-p", "--model", "opus"])
        dirs = [argv[i + 1] for i, word in enumerate(argv) if word == "--plugin-dir"]
        self.assertEqual(dirs, [os.path.join(self.base, "plugins/lane"), turn["cwd"] + "/p"])
        self.assertEqual(argv[argv.index("--permission-mode") + 1], "bypassPermissions")
        self.assertEqual(argv[-1], "/lane:up p")

    def test_the_first_turn_sets_the_session_and_each_later_one_resumes_it(self):
        replies = [{"done": False, "prompt": "one"}, {"done": False, "prompt": "two"}]
        self.plan([*replies, {"done": True}], [{}, {}])
        self.run_test()
        first, second = (call["argv"] for call in self.calls(stand_in=False))
        session = first[first.index("--session-id") + 1]
        self.assertNotIn("--resume", first)
        self.assertEqual(second[second.index("--resume") + 1], session)

    def test_a_turn_that_starts_a_new_conversation_is_followed_by_the_next(self):
        replies = [{"done": False, "prompt": "/clear"}, {"done": False, "prompt": "two"}]
        self.plan([*replies, {"done": True}], [{"session": "the-new-one"}, {}])
        self.run_test()
        second = self.calls(stand_in=False)[1]["argv"]
        self.assertEqual(second[second.index("--resume") + 1], "the-new-one")

    def test_claude_runs_on_a_config_of_its_own_with_none_of_the_callers_settings(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        self.run_test()
        (turn,) = self.calls(stand_in=False)
        env = turn["env"]
        self.assertEqual(env["CLAUDE_CODE_OAUTH_TOKEN"], TOKEN)
        self.assertNotIn("CLAUDE_CODE_SESSION_ID", env)
        self.assertTrue(env["CLAUDE_CONFIG_DIR"].startswith(self.temp))
        self.assertTrue(env["TMPDIR"].startswith(self.temp))
        self.assertNotEqual(env["TMPDIR"], self.temp)

    def test_the_temporary_folder_is_removed(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        code, out, err = self.run_test()
        self.assertEqual(code, 0, err)
        self.assertEqual(os.listdir(self.temp), [])
        self.assertEqual(out.strip(), self.records())

    # The stand-in

    def test_the_stand_in_holds_the_intent_with_no_tool_outside_the_clone(self):
        self.plan([{"done": True}], [])
        self.run_test()
        (stand_in,) = self.calls(stand_in=True)
        argv = stand_in["argv"]
        self.assertIn(INTENT, argv[argv.index("--system-prompt") + 1])
        self.assertEqual(argv[:3], ["-p", "--model", "opus"])
        self.assertEqual(argv[argv.index("--tools") + 1], "")
        self.assertNotIn("--plugin-dir", argv)
        self.assertTrue(stand_in["env"]["CLAUDE_CONFIG_DIR"].startswith(self.temp))
        self.assertFalse(os.path.exists(os.path.join(stand_in["cwd"], ".git")))

    def test_claude_is_told_to_install_and_send_nothing_as_dev_md_says(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        self.run_test()
        for call in self.calls(stand_in=False) + self.calls(stand_in=True):
            argv = call["argv"]
            self.assertIn("Install nothing", argv[argv.index("--append-system-prompt") + 1])

    def test_the_test_ends_when_the_stand_in_is_done(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        self.run_test()
        self.assertEqual(len(self.calls(stand_in=False)), 1)
        self.assertEqual(len(self.calls(stand_in=True)), 2)

    def test_the_test_ends_at_its_turn_limit(self):
        self.fields["turns"] = 1
        self.plan([{"done": False, "prompt": "go"}], [{}])
        self.run_test()
        self.assertEqual(len(self.calls(stand_in=False)), 1)
        self.assertEqual(len(self.calls(stand_in=True)), 1)

    def test_a_reply_that_isnt_done_without_a_prompt_is_refused(self):
        self.plan([{"done": False}], [])
        self.refuses("stand-in")

    def test_a_reply_that_isnt_done_with_an_empty_prompt_is_refused(self):
        self.plan([{"done": False, "prompt": ""}], [])
        self.refuses("stand-in")

    def test_a_turn_past_its_time_is_kept_and_ends_the_test(self):
        self.plan(
            [{"done": False, "prompt": "go"}, {"done": False, "prompt": "again"}], [{"sleep": 3}]
        )
        with mock.patch.object(e2e, "TURN_SECONDS", 1):
            code, _, err = self.run_test()
        self.assertEqual(code, 0, err)
        (turn,) = self.kept("turns.jsonl")
        self.assertIsNone(turn["exit"])
        self.assertIn("stopped the turn after 1 s", turn["screen"])

    # The screen the stand-in reads

    def stand_in_read(self, stream: list[Any]) -> str:
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{"stream": stream}])
        self.run_test()
        argv = self.calls(stand_in=True)[1]["argv"]
        return argv[-1]

    def test_the_screen_shows_the_prompt_and_the_main_conversations_text(self):
        screen = self.stand_in_read([said("Here is the proposal.")])
        self.assertIn("> go", screen)
        self.assertIn("Here is the proposal.", screen)

    def test_the_screen_shows_each_call_by_what_it_runs(self):
        stream = [
            used("Bash", {"command": "git log --oneline"}),
            used("Write", {"file_path": "/r/CHANGELOG.md", "content": "x"}),
            used("Agent", {"subagent_type": "p:writer", "prompt": "go"}),
            used("Skill", {"skill": "p:write"}),
            used("TodoWrite", {"todos": []}),
        ]
        screen = self.stand_in_read(stream)
        for line in (
            "● Bash(git log --oneline)",
            "● Write(/r/CHANGELOG.md)",
            "● Agent(p:writer)",
            "● Skill(p:write)",
            "● TodoWrite",
        ):
            self.assertIn(line, screen)

    def test_the_screen_shows_a_stopped_call_with_why(self):
        screen = self.stand_in_read([used("Bash", {"command": "git commit"}), refused("p: no")])
        self.assertIn("  ⎿  p: no", screen)

    def test_the_screen_shows_each_line_of_why_given_as_blocks(self):
        blocks = [{"type": "text", "text": "p: no\nRun only `git log`."}]
        screen = self.stand_in_read([refused(blocks)])
        self.assertIn("  ⎿  p: no\n     Run only `git log`.", screen)

    def test_the_screen_leaves_out_a_call_that_went_through(self):
        content = [{"type": "tool_result", "tool_use_id": "toolu_1", "content": "a1b2 Add tally"}]
        line = {"type": "user", "parent_tool_use_id": None, "message": {"content": content}}
        screen = self.stand_in_read([line])
        self.assertNotIn("Add tally", screen)

    def test_the_screen_skips_a_line_that_isnt_json(self):
        screen = self.stand_in_read(["not json", said("Hi.")])
        self.assertIn("Hi.", screen)

    def test_the_screen_leaves_out_what_a_subagent_does(self):
        screen = self.stand_in_read([used("Bash", {"command": "git log"}, parent="toolu_0")])
        self.assertNotIn("git log", screen)

    def test_the_screen_shows_a_turn_that_failed(self):
        screen = self.stand_in_read([{"type": "result", "is_error": True, "result": "API down"}])
        self.assertIn("API down", screen)

    # The records

    def test_the_records_lie_under_the_tests_name_and_its_utc_time(self):
        self.plan([{"done": True}], [])
        self.run_test()
        self.assertRegex(os.path.basename(self.records()), r"\A\d{8}T\d{6}Z\Z")

    def test_the_records_keep_each_turn_with_its_screen(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{"stream": [said("Hi.")]}])
        self.run_test()
        (turn,) = self.kept("turns.jsonl")
        self.assertEqual((turn["turn"], turn["prompt"], turn["exit"]), (1, "go", 0))
        self.assertIn("Hi.", turn["screen"])
        self.assertLessEqual(turn["started"], turn["ended"])

    def test_a_turn_that_fails_is_kept_with_its_exit_code(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{"exit": 1}])
        code, _, _ = self.run_test()
        self.assertEqual(code, 0)
        self.assertEqual(self.kept("turns.jsonl")[0]["exit"], 1)

    def test_a_turn_that_sent_no_hook_event_is_resumed_as_it_was(self):
        replies = [{"done": False, "prompt": "one"}, {"done": False, "prompt": "two"}]
        self.plan([*replies, {"done": True}], [{"hooks": False, "exit": 1}, {}])
        self.run_test()
        first, second = (call["argv"] for call in self.calls(stand_in=False))
        self.assertEqual(
            second[second.index("--resume") + 1], first[first.index("--session-id") + 1]
        )

    def test_the_records_keep_each_hook_event_with_its_time(self):
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{}])
        self.run_test()
        _, event = self.kept("hooks.jsonl")
        self.assertEqual(event["payload"]["prompt"], "go")
        self.assertRegex(event["time"], r"\A\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\.\d+Z\Z")

    def test_the_records_keep_the_transcripts_without_the_login_or_an_email(self):
        transcript = [
            {"type": "user", "message": {"content": f"token {TOKEN} of someone@example.com"}},
            {"type": "attachment", "attachment": {"type": "session_context", "context": {}}},
            {"type": "api-request-blob", "message": {}},
            {"type": "session-owner", "accountUuid": "u"},
        ]
        subagent = [{"type": "assistant", "message": {"content": "done"}}]
        turn = {"transcript": transcript, "subagents": {"agent-a1.jsonl": subagent}}
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [turn])
        self.run_test()
        (session,) = (
            n for n in os.listdir(os.path.join(self.records(), "transcripts")) if "." in n
        )
        lines = self.kept(os.path.join("transcripts", session))
        self.assertEqual(
            lines, [{"type": "user", "message": {"content": "token <token> of <email>"}}]
        )
        name = session.split(".")[0]
        kept = self.kept(os.path.join("transcripts", name, "subagents", "agent-a1.jsonl"))
        self.assertEqual(kept, subagent)

    def test_the_records_name_the_top_and_the_clone_by_no_path_of_the_machine(self):
        line = {"type": "user", "message": {"content": f"{self.base}/plugins/lane"}}
        turn = {"transcript": [line], "stream": [said("in the clone")], "show": []}
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [turn])
        self.run_test()
        (clone,) = {call["cwd"] for call in self.calls(stand_in=False)}
        (session,) = (
            n for n in os.listdir(os.path.join(self.records(), "transcripts")) if "." in n
        )
        (kept,) = self.kept(os.path.join("transcripts", session))
        self.assertEqual(kept["message"]["content"], "<top>/plugins/lane")
        hooks = self.read(os.path.join(self.records(), "hooks.jsonl"))
        self.assertNotIn(os.path.dirname(clone), hooks)

    def test_the_records_keep_the_run_records_in_the_temporary_folder_and_not_claudes_own(self):
        tmp = {"lane/20261112-p/proposal.json": "{}", "claude-1000/x/tasks/a.output": "x"}
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{"tmp": tmp}])
        self.run_test()
        self.assertTrue(
            os.path.isfile(os.path.join(self.records(), "tmp/lane/20261112-p/proposal.json"))
        )
        self.assertFalse(os.path.exists(os.path.join(self.records(), "tmp/claude-1000")))

    def test_the_records_keep_what_the_run_changed_in_the_clone(self):
        turn = {"files": {"CHANGELOG.md": "## 0.2.0\n", "p/hooks/hooks.json": "{}\n"}}
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [turn])
        self.run_test()
        diff = self.read(os.path.join(self.records(), "run.diff"))
        self.assertIn("+## 0.2.0", diff)
        self.assertIn("p/hooks/hooks.json", diff)

    def test_the_records_keep_what_the_run_committed_on_each_branch_it_made(self):
        # Given a run that commits on a branch of its own in a worktree, as rn does,
        # When the test keeps its records,
        # Then they hold the branch's change since the test's commits, by the branch's name.
        branches = {"rn-20261114-csv": {"tally.py": "print('a,b')\n"}}
        self.plan([{"done": False, "prompt": "go"}, {"done": True}], [{"branches": branches}])
        self.run_test()
        diff = self.read(os.path.join(self.records(), "branches", "rn-20261114-csv.diff"))
        self.assertIn("+print('a,b')", diff)
        self.assertEqual(
            os.listdir(os.path.join(self.records(), "branches")), ["rn-20261114-csv.diff"]
        )

    # The hook that keeps each event

    def test_the_hook_keeps_the_event_with_its_time_and_prints_nothing(self):
        with mock.patch("sys.stdin", io.StringIO('{"hook_event_name": "Stop"}')):
            code, out, _ = self.main("hook", "events.jsonl")
        self.assertEqual((code, out), (0, ""))
        (event,) = (json.loads(line) for line in self.read("events.jsonl").splitlines())
        self.assertEqual(event["payload"], {"hook_event_name": "Stop"})
        self.assertTrue(re.match(r"\d{4}-", event["time"]))

    def test_the_hook_runs_as_claude_codes_command(self):
        argv = ["e2e.py", "hook", "events.jsonl"]
        stdin = mock.patch("sys.stdin", io.StringIO("{}"))
        with mock.patch("sys.argv", argv), stdin, self.assertRaises(SystemExit) as ended:
            runpy.run_path(e2e.__file__, run_name="__main__")
        self.assertEqual(ended.exception.code, 0)
        self.assertEqual(json.loads(self.read("events.jsonl"))["payload"], {})

    def test_the_hook_keeps_an_event_that_isnt_json_as_unread(self):
        with mock.patch("sys.stdin", io.StringIO("{")):
            code, _, _ = self.main("hook", "events.jsonl")
        self.assertEqual(code, 0)
        self.assertEqual(json.loads(self.read("events.jsonl"))["unread"], "{")
