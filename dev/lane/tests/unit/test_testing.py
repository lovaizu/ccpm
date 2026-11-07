"""The double of Claude Code in testing.py: each hook's entry, and each script of a plugin enabled
that a Bash call runs, called in the test's own process as a new process of Python would run it,
nothing of one call reaching the next or the test; and any other command run in sh."""

import io
import os
import sys
import tempfile
from typing import Any
from unittest import mock

import helpers
from helpers import testing

# An entry that answers its event where the plugin's own `hook` module, beside it, says it answers
# it, with what it was handed and where it ran, and counts its calls in the module, so a module
# kept from an earlier call shows.
ENTRY = """import json, os, sys, tempfile
import hook
hook.CALLS += 1
event = json.load(sys.stdin)
if event["hook_event_name"] == hook.ANSWERS:
    said = {
        "argv": sys.argv[1:],
        "root": os.environ["CLAUDE_PLUGIN_ROOT"],
        "cwd": os.getcwd(),
        "tmp": tempfile.gettempdir(),
        "calls": hook.CALLS,
        "pid": os.getpid(),
        "path": sys.path[0],
        "file": __file__,
        "tool": event.get("tool_name"),
    }
    print(json.dumps({"hookSpecificOutput": {"additionalContext": json.dumps(said)}}))
"""
# A script of the plugin, which prints what it was given and where it ran, and exits as its first
# word says: by the value main gives back, by SystemExit, or by an error.
SCRIPT = """import json, os, sys

def main(argv):
    said = {"argv": argv, "cwd": os.getcwd(), "pid": os.getpid(), "env": os.environ.get("MARK")}
    print(json.dumps(said))
    if argv[:1] == ["two"]:
        print("why", file=sys.stderr)
        return 2
    if argv[:1] == ["words"]:
        sys.exit("what is wrong")
    if argv[:1] == ["error"]:
        raise ValueError("broken")
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
"""


class DoubleTest(testing.FolderTest):
    """A test of the double on plugins made in `base`: `a` by default, answering at PreToolUse, its
    hooks laid as `lay.py write` lays them; a session working in `work`, which holds `f`."""

    def setUp(self) -> None:
        super().setUp()
        self.work = os.path.join(self.base, "work")
        self.write(os.path.join(self.work, "f"), "")
        self.env = {**os.environ, "TMPDIR": self.base, "MARK": "m"}

    def plugin(
        self, name: str, answers: str = "PreToolUse", entry: str = ENTRY, **hook: Any
    ) -> str:
        """A plugin of the name in `base`, whose hooks give each event lane acts on to its entry,
        which answers the event `answers`; the hook's fields given replace those lay.py writes."""
        root = os.path.join(self.base, name)
        lane = os.path.join(root, "hooks", "lane")
        for event in helpers.HOOKS["hooks"]:
            self.write(os.path.join(lane, f"{event.lower()}.py"), entry)
        self.write(os.path.join(lane, "hook.py"), f"ANSWERS = {answers!r}\nCALLS = 0\n")
        laid: dict[str, Any] = helpers.HOOKS["hooks"]
        hooks = {
            "hooks": {
                event: [{**e, "hooks": [{**h, **hook} for h in e["hooks"]]} for e in entries]
                for event, entries in laid.items()
            }
        }
        self.write_json(os.path.join(root, "hooks", "hooks.json"), hooks)
        self.write(os.path.join(root, "scripts", "x.py"), SCRIPT)
        return root

    def claude(self, *roots: str) -> testing.ClaudeCode:
        """The double with the plugins at the roots enabled, the first its own."""
        return testing.ClaudeCode(roots[0], self.work, self.env, others=roots[1:])

    def bash(self, claude: testing.ClaudeCode, command: str) -> tuple[Any, Any]:
        """What the double's Bash call of the command gives back, and its error."""
        return claude.made("Bash", {"command": command, "description": "d"})


class TestHook(DoubleTest):
    def test_the_entry_is_called_in_the_tests_process_with_the_event_and_its_command_words(self):
        # Given: plugin a, its hooks as lay.py writes them
        root = self.plugin("a")
        # When: a call of a subagent is sent
        told = self.claude(root).call(testing.Run("a:w", "w1"), "Read", {"file_path": "f"})
        # Then: the entry ran in this process, handed the event, the command's words, the plugin's
        # folder, the session's folder and the temporary folder of the session's environment,
        # with its own folder first on the path and its path as the command names it
        said = helpers.answer(told.said["hookSpecificOutput"]["additionalContext"])
        lane = os.path.join(root, "hooks", "lane")
        self.assertEqual(
            said,
            {
                "argv": ["changelog"],
                "root": root,
                "cwd": self.work,
                "tmp": self.base,
                "calls": 1,
                "pid": os.getpid(),
                "path": lane,
                "file": os.path.join(lane, "pretooluse.py"),
                "tool": "Read",
            },
        )

    def test_nothing_of_a_call_reaches_the_next_or_the_test(self):
        # Given: plugin a, and the test's own module `hook`, lane's, named as the entry's own
        root = self.plugin("a")
        own = sys.modules["hook"]
        before = self.state()
        # When: two calls are sent
        claude = self.claude(root)
        told = [claude.call(None, "Read", {"file_path": "f"}) for _ in range(2)]
        # Then: the entry imported its own module afresh at each, and the test's module is back,
        # as is everything else the calls changed
        for t in told:
            said = helpers.answer(t.said["hookSpecificOutput"]["additionalContext"])
            self.assertEqual(said["calls"], 1)
        self.assertIs(sys.modules["hook"], own)
        self.assertEqual(self.state(), before)

    @staticmethod
    def state() -> tuple:
        """What of the test's process a call may change."""
        return (
            dict(os.environ),
            list(sys.path),
            list(sys.argv),
            os.getcwd(),
            tempfile.tempdir,
            sys.dont_write_bytecode,
            (sys.stdin, sys.stdout, sys.stderr),
        )

    def test_two_plugins_with_modules_of_one_name_each_use_their_own(self):
        # Given: plugins a and b, each with its own module `hook`, a answering at PreToolUse and b
        # at PostToolUse
        a, b = self.plugin("a"), self.plugin("b", "PostToolUse")
        # When: a call is made
        told = self.claude(a, b).call(None, "Read", {"file_path": "f"})
        # Then: a answered its event alone and b its own, each from its own folder
        before = helpers.answer(told.said["hookSpecificOutput"]["additionalContext"])
        after = helpers.answer(told.context[0])
        self.assertEqual((before["root"], after["root"]), (a, b))

    def test_two_plugins_answering_one_event_fail_the_test(self):
        # Given: plugins a and b both answering at PreToolUse
        a, b = self.plugin("a"), self.plugin("b")
        # When: a call is made
        # Then: the test fails
        with self.assertRaisesRegex(AssertionError, "two plugins' hooks answered PreToolUse"):
            self.claude(a, b).call(None, "Read", {"file_path": "f"})

    def test_an_entry_that_fails_fails_the_test_with_what_it_said(self):
        for n, (code, said) in enumerate(
            (
                ("raise ValueError('broken')", "ValueError: broken"),
                ("import sys; sys.exit(3)", "PreToolUse failed: $"),
                ("import sys; sys.exit('what is wrong')", "what is wrong"),
                ("import sys; print('why', file=sys.stderr)", "why"),
            )
        ):
            with self.subTest(code=code):
                # Given: plugin a, whose entry fails
                root = self.plugin(f"a{n}", entry=code)
                # When: a call is sent
                # Then: the test fails with what the entry said
                with self.assertRaisesRegex(AssertionError, said):
                    self.claude(root).call(None, "Read", {"file_path": "f"})

    def test_an_entry_that_ends_with_no_error_lets_the_call_go_on(self):
        # Given: plugin a, whose entry exits 0, and one whose entry exits with None
        for n, code in enumerate(("import sys; sys.exit(0)", "import sys; sys.exit()")):
            with self.subTest(code=code):
                root = self.plugin(f"a{n}", entry=code)
                # When: a call is made
                told = self.claude(root).call(None, "Read", {"file_path": "f"})
                # Then: it is made, nothing said
                self.assertEqual((told.made, told.said), (True, {}))

    def test_an_entry_still_running_at_its_timeout_fails_the_test(self):
        # Given: plugin a, whose entry runs past the hook's timeout
        root = self.plugin("a", entry="import time; time.sleep(5)", timeout=0.05)
        # When: a call is sent
        # Then: the test fails, the entry stopped at its timeout
        with self.assertRaisesRegex(AssertionError, "did not end within 0.05 seconds"):
            self.claude(root).call(None, "Read", {"file_path": "f"})

    def test_a_command_not_as_lay_py_writes_it_fails_the_test(self):
        # Given: plugin a, whose hook's command runs no entry of lane's
        root = self.plugin("a", command="echo '{}'")
        # When: a call is sent
        # Then: the test fails, naming the command
        with self.assertRaisesRegex(AssertionError, "calls no entry of the command `echo '{}'`"):
            self.claude(root).call(None, "Read", {"file_path": "f"})

    def test_an_entry_whose_matcher_is_not_the_tool_is_not_called(self):
        # Given: plugin a, its entries matching Bash alone
        root = self.plugin("a")
        hooks = self.read_json(os.path.join(root, "hooks", "hooks.json"))
        for entries in hooks["hooks"].values():
            entries[0]["matcher"] = "Bash"
        self.write_json(os.path.join(root, "hooks", "hooks.json"), hooks)
        # When: a Read is made
        told = self.claude(root).call(None, "Read", {"file_path": "f"})
        # Then: no entry answered
        self.assertEqual(told.said, {})


class TestBash(DoubleTest):
    def test_a_plugins_script_is_called_in_the_tests_process(self):
        root = self.plugin("a")
        script = os.path.join(root, "scripts", "x.py")
        for command in (
            f"python3 {script} one 'b c'",
            f"python3 -B {script} one 'b c'",
            "python3 ../a/scripts/x.py one 'b c'",
        ):
            with self.subTest(command=command):
                # Given: plugin a with its script
                # When: a Bash call runs the script, by its path or one from the session's folder
                response, error = self.bash(self.claude(root), command)
                # Then: it ran in this process, in the session's folder and environment, given
                # its words, and its print is the call's
                said = {
                    "argv": ["one", "b c"],
                    "cwd": self.work,
                    "pid": os.getpid(),
                    "env": "m",
                }
                self.assertIsNone(error)
                self.assertEqual(helpers.answer(response["stdout"]), said)
                self.assertEqual((response["stderr"], response["interrupted"]), ("", False))

    def test_a_script_that_fails_gives_its_exit_code_and_what_it_said(self):
        root = self.plugin("a")
        script = os.path.join(root, "scripts", "x.py")
        for word, start, end in (
            ("two", "Exit code 2\n", "\nwhy\n"),
            ("words", "Exit code 1\n", "\nwhat is wrong\n"),
            ("error", "Exit code 1\nTraceback", "\nValueError: broken\n"),
        ):
            with self.subTest(word=word):
                # Given: plugin a with its script
                # When: a Bash call runs it on a word that makes it fail
                response, error = self.bash(self.claude(root), f"python3 {script} {word}")
                # Then: the call fails with the exit code and what the script said
                self.assertIsNone(response)
                self.assertTrue(str(error).startswith(start), error)
                self.assertTrue(str(error).endswith(end), error)

    def test_a_command_that_runs_no_plugins_script_alone_is_none_to_call(self):
        root = self.plugin("a")
        outside = os.path.join(self.base, "outside.py")
        script = os.path.join(root, "scripts", "x.py")
        for command in (
            f"python3 {outside} one",
            f"python3 {script} one && true",
            f"python3 $HOME/{script} one",
            "python3 -c 'import os'",
            f"python3 {os.path.join(root, 'scripts', 'x.txt')}",
            "python3",
            "true 'open",
            "echo hi",
        ):
            with self.subTest(command=command):
                # Given: a command that runs no script of a plugin enabled alone, by a path, or
                # one sh reads apart
                # When: the double looks for the script it runs
                # Then: it finds none
                self.assertIsNone(self.claude(root).script(command))

    def test_any_other_command_runs_in_sh(self):
        # Given: a command that runs no script of a plugin
        root = self.plugin("a")
        # When: a Bash call runs it
        response, error = self.bash(self.claude(root), "echo $$")
        # Then: it ran in sh, in a process of its own
        self.assertIsNone(error)
        self.assertNotEqual(response["stdout"], f"{os.getpid()}\n")
        self.assertRegex(response["stdout"], r"^\d+\n$")


class TestInside(DoubleTest):
    def test_a_script_reads_its_stdin_and_writes_bytecode_only_without_dash_b(self):
        # Given: a script that prints what it reads and whether it may write bytecode
        path = os.path.join(self.base, "s.py")
        self.write(path, "import sys; print(sys.stdin.read(), sys.dont_write_bytecode)")
        for bytecode in (True, False):
            with self.subTest(bytecode=bytecode):
                # When: it is called with text on stdin
                done = testing.inside(path, [], "in", self.env, self.work, None, bytecode)
                # Then: it read the text, and writes bytecode as told
                self.assertEqual(done, (0, f"in {not bytecode}\n", ""))

    def test_the_streams_are_the_calls_own(self):
        # Given: a script that writes on both streams
        path = os.path.join(self.base, "s.py")
        self.write(path, "import sys; print('out'); print('err', file=sys.stderr)")
        # When: it is called
        stdout = io.StringIO()
        with mock.patch.object(sys, "stdout", stdout):
            done = testing.inside(path, [], "", self.env, self.work)
        # Then: what it wrote is the call's, none of it the test's
        self.assertEqual((done, stdout.getvalue()), ((0, "out\n", "err\n"), ""))
