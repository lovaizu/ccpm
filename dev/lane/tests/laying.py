"""What the tests of the layer stand on: the plugin `notes` with a proposal of lanes on step 3 of
changelog-writer, kept where lane:up keeps it, the hook lane:up writes for it, and a stand-in for
Claude Code's command."""

import contextlib
import io
import os
from unittest import mock

import helpers
from helpers import lay

# hands_off of the README's proposal, on step 3 of changelog-writer.
LANES = [{"lane": "hands_off", "takes": ["git commit", "git push"]}]
# The hook's command lane:up writes for it.
COMMAND = (
    'python3 -c "import sys; sys.exit(sys.version_info < (3, 9))" 2>/dev/null'
    ' || { e=; while IFS= read -r l || [ -n "$l" ]; do e="$e$l"; l=; done; case "$e" in'
    """ *'"agent_type":"notes:changelog-writer"'*|*'"agent_type": "notes:changelog-writer"'*)"""
    ' echo "notes: install Python 3.9 or later, run as python3, for its hooks to run" >&2;'
    ' exit 2;; esac; exit 0; }; exec python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/pretooluse.py"'
    " notes:changelog-writer '3:hands_off:git commit,git push'"
)
ENTRY = {"matcher": "Bash", "hooks": [{"type": "command", "timeout": 10, "command": COMMAND}]}
# test_after on step 3, held as the subagent is about to end, and its entry of SubagentStop, which
# matches the subagent, exits 1 where Python is missing, and runs that event's entry.
TESTED = {"lane": "test_after", "takes": ["CHANGELOG.md", "python3 check.py"]}
END_COMMAND = (
    COMMAND.replace("pretooluse.py", "subagentstop.py")
    .replace("exit 2;", "exit 1;")
    .replace("'3:hands_off:git commit,git push'", "'3:test_after:CHANGELOG.md,python3 check.py'")
)
END_ENTRY = {
    "matcher": "notes:changelog-writer",
    "hooks": [{"type": "command", "timeout": 10, "command": END_COMMAND}],
}
# The entries of the events a call is kept on, PostToolUse and PostToolUseFailure, for the subagent
# lanes are laid in, each matching every tool, exiting 0 where Python is missing, and running its
# event's entry with the subagent alone.
KEPT = {
    event: [
        {
            "matcher": ".*",
            "hooks": [
                {
                    "type": "command",
                    "timeout": 10,
                    "command": COMMAND.replace("exit 2;", "exit 0;")
                    .replace("pretooluse.py", f"{event.lower()}.py")
                    .replace(" '3:hands_off:git commit,git push'", ""),
                }
            ],
        }
    ]
    for event in ("PostToolUse", "PostToolUseFailure")
}
# What `print` shows the building AI for it.
PRINTED = """Lanes on step 3 of changelog-writer, each hook acting in changelog-writer alone:
  run: Do not run `git commit` or `git push`.  hook hands_off

3. Write the new entries into `CHANGELOG.md`. Do not run `git commit` or `git push`.
"""
# hands_off on step 3 taking `git push` alone, and its sentence.
PUSH = [{"lane": "hands_off", "takes": ["git push"]}]
PUSHED = "Do not run `git push`."
# A stand-in for Claude Code's command, which keeps what it was asked and exits as the test sets.
CLAUDE = """#!/bin/sh
echo "$@" > "$(dirname "$0")/asked"
echo "validated"
exit "${CLAUDE_EXIT:-0}"
"""


class LayTest(helpers.PluginTest):
    """A test of the layer on the plugin `notes`, the proposal kept in `base/data/notes.json` and a
    stand-in for Claude Code's command first on PATH."""

    def setUp(self) -> None:
        super().setUp()
        self.proposal_file = os.path.join(self.base, "data", "notes.json")
        self.propose(self.proposal())
        self.bin = os.path.join(self.base, "bin")
        self.write(os.path.join(self.bin, "claude"), CLAUDE)
        os.chmod(os.path.join(self.bin, "claude"), 0o755)
        path = mock.patch.dict(os.environ, {"PATH": self.bin + os.pathsep + os.environ["PATH"]})
        path.start()
        self.addCleanup(path.stop)

    def proposal(self, lanes=LANES, name="changelog-writer", number=3) -> dict:
        """A proposal of the lanes on the step of the number of the subagent of the name."""
        return {
            "plugin": self.plugin,
            "subagents": [{"name": name, "steps": [{"step": number, "lanes": lanes}]}],
        }

    def propose(self, proposal) -> None:
        """Writes the proposal where lane:up keeps it."""
        self.write_json(self.proposal_file, proposal)

    def lay(self, *argv) -> tuple:
        """lay.py run with the arguments; what it exits with and what it prints."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            code = lay.main(list(argv))
        return code, out.getvalue()

    def hooks(self) -> dict:
        """The plugin's hooks.json."""
        return self.read_json(os.path.join(self.plugin, "hooks", "hooks.json"))
