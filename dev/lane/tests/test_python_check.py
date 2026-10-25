"""The Python check each hook's command begins with: where python3 is missing or older than 3.9, the
call is denied with what to install, and at the subagent's end the user is told it and the
subagent let end, each answered in Claude Code's JSON output as the guard answers; with the one in
use, the guard runs."""

import json
import os
import subprocess
import sys
import unittest

import helpers
from helpers import hooks_file

# What the subagent, or the user, is told where python3 cannot run the hooks.
INSTALL = "notes: install Python 3.9 or later, run as python3, for its hooks to run"
# A python3 that is 3.8 to whatever asks its version, standing in for an older Python.
OLDER = f"""#!/bin/sh
shift
exec "{sys.executable}" -c "import sys; sys.version_info = (3, 8, 18, 'final', 0)
$1"
"""


class TestPythonCheck(helpers.PluginTest):
    def setUp(self) -> None:
        super().setUp()
        # The plugin with lane's code linked in, as in the ccpm marketplace, and step 3 as lane:up
        # writes it.
        os.makedirs(os.path.join(self.plugin, "hooks"))
        os.symlink(helpers.CODE, os.path.join(self.plugin, "hooks", "lane"))
        self.write(self.agent_file, helpers.LAID)
        laid = [hooks_file.word(3, "hands_off", ["git commit", "git push"])]
        self.command = hooks_file.command("notes", helpers.AGENT, laid, "PreToolUse")

    def run_hook(self, *folders, command=None, agent_type=helpers.AGENT):
        """The hook's command, or the one given, run by sh with PATH holding the folders, handed a
        commit's event in the subagent of the type, or in the main conversation where it is None;
        what it exits with and the JSON it writes on stdout, None where it writes nothing."""
        env = dict(os.environ, PATH=os.pathsep.join(folders), CLAUDE_PLUGIN_ROOT=self.plugin)
        env.pop("PYTHONPATH", None)
        done = subprocess.run(
            ["/bin/sh", "-c", command or self.command],
            input=self.stream("git commit -m notes", agent_type),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        return done.returncode, json.loads(done.stdout) if done.stdout else None

    def folder_with_python3(self, script):
        """A folder holding a python3 that is the script."""
        folder = os.path.join(self.base, "older")
        self.write(os.path.join(folder, "python3"), script)
        os.chmod(os.path.join(folder, "python3"), 0o755)
        return folder

    def test_without_python3_the_call_is_stopped_with_what_to_install(self):
        # Given: a PATH holding no python3
        # When: the hook's command is run
        # Then: it denies the call, telling the subagent to install Python
        self.assertEqual(
            self.run_hook(os.path.join(self.base, "none")), (0, helpers.denied(INSTALL))
        )

    def test_with_a_python3_older_than_3_9_the_call_is_stopped_with_what_to_install(self):
        # Given: a PATH whose python3 is 3.8
        older = self.folder_with_python3(OLDER)
        # When: the hook's command is run
        # Then: it denies the call, telling the subagent to install Python
        self.assertEqual(self.run_hook(older), (0, helpers.denied(INSTALL)))

    def test_without_python3_a_call_of_another_agent_is_let_through(self):
        # Given: a PATH holding no python3, and a commit of the main conversation, or of another
        # subagent
        none = os.path.join(self.base, "none")
        for agent_type in (None, "notes:other"):
            with self.subTest(agent_type=agent_type):
                # When: the hook's command is run on it
                # Then: it lets the call through, as the lane acts in its subagent alone
                self.assertEqual(self.run_hook(none, agent_type=agent_type), (0, None))

    def test_without_python3_at_the_subagents_end_the_user_is_told_and_it_ends(self):
        # Given: the hook's command for a lane held as the subagent ends, and a PATH holding no
        # python3
        laid = [hooks_file.word(3, "test_after", ["CHANGELOG.md", "python3 check.py"])]
        command = hooks_file.command("notes", helpers.AGENT, laid, "SubagentStop")
        # When: it is run
        # Then: it tells the user to install Python, letting the subagent end
        none = os.path.join(self.base, "none")
        told = (0, {"systemMessage": INSTALL})
        self.assertEqual(self.run_hook(none, command=command), told)

    def test_without_python3_a_call_coming_back_goes_on(self):
        for event in hooks_file.KEPT:
            with self.subTest(event=event):
                # Given: the hook's command keeping the subagent's calls, and a PATH holding no
                # python3
                command = hooks_file.command("notes", helpers.AGENT, [], event)
                # When: it is run as a call comes back
                found = self.run_hook(os.path.join(self.base, "none"), command=command)
                # Then: it answers nothing, as the call has run, and the hook of the next call
                # denies it, saying what to install
                self.assertEqual(found, (0, None))

    def test_with_the_python3_in_use_the_guard_runs(self):
        # Given: a PATH whose python3 is the one in use
        # When: the hook's command is run for a call the lane stops
        # Then: the guard denies it with the lane's sentence
        self.assertEqual(
            self.run_hook(os.path.dirname(sys.executable)),
            (0, helpers.denied("notes: " + helpers.SENTENCE)),
        )


if __name__ == "__main__":
    unittest.main()
