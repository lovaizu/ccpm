"""The Python check each hook's command begins with: where python3 is missing or older than 3.9, the
call is stopped with what to install; with the one in use, the guard runs."""

import os
import subprocess
import sys

import helpers
from helpers import lanes, lay

# What the subagent is told where the check stops the call.
INSTALL = "notes: install Python 3.9 or later, run as python3, for its hooks to run\n"
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
        laid = [lanes.word(3, "hands_off", ["git commit", "git push"])]
        self.command = lay.command("notes", helpers.AGENT, laid)

    def run_hook(self, *folders):
        """The hook's command run by sh with PATH holding the folders, handed a commit's event in
        the subagent; what it exits with and what it writes on stderr."""
        env = dict(os.environ, PATH=os.pathsep.join(folders), CLAUDE_PLUGIN_ROOT=self.plugin)
        env.pop("PYTHONPATH", None)
        done = subprocess.run(
            ["/bin/sh", "-c", self.command],
            input=self.stream("git commit -m notes"),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        return done.returncode, done.stderr

    def folder_with_python3(self, script):
        """A folder holding a python3 that is the script."""
        folder = os.path.join(self.base, "older")
        self.write(os.path.join(folder, "python3"), script)
        os.chmod(os.path.join(folder, "python3"), 0o755)
        return folder

    def test_without_python3_the_call_is_stopped_with_what_to_install(self):
        # Given: a PATH holding no python3
        # When: the hook's command is run
        # Then: it exits 2, telling the subagent to install Python
        self.assertEqual(self.run_hook(os.path.join(self.base, "none")), (2, INSTALL))

    def test_with_a_python3_older_than_3_9_the_call_is_stopped_with_what_to_install(self):
        # Given: a PATH whose python3 is 3.8
        older = self.folder_with_python3(OLDER)
        # When: the hook's command is run
        # Then: it exits 2, telling the subagent to install Python
        self.assertEqual(self.run_hook(older), (2, INSTALL))

    def test_with_the_python3_in_use_the_guard_runs(self):
        # Given: a PATH whose python3 is the one in use
        # When: the hook's command is run for a call the lane stops
        # Then: the guard stops it with the lane's sentence
        self.assertEqual(
            self.run_hook(os.path.dirname(sys.executable)),
            (2, "notes: " + helpers.SENTENCE + "\n"),
        )
