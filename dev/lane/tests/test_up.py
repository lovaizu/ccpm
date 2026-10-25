"""lane:up held by its own lanes, as lane's hooks/hooks.json lays them on its steps in
agents/up.md: every call its steps make on a run is let through, from `lay.py up` first to
`lay.py write` on the OK; a call made before `lay.py up` is stopped with start_with's sentence, and
a read of anything but what `lay.py up` printed it reads with read_only's."""

from __future__ import annotations

import contextlib
import io
import json
import os
import unittest

import helpers
from helpers import hooks_file, lay
from test_guard import GuardTest

LAY = f"python3 {os.path.join(helpers.SCRIPTS, 'lay.py')}"
LANES_MD = os.path.join(helpers.LANE, "docs", "lanes.md")
# start_with's sentence, as lane:up is told it.
BEGIN = "lane: First run `lay.py up`."


class UpTest(GuardTest):
    """lane:up run on the plugin `notes`, its proposal kept in `base/data`, each call it makes
    checked by the guard on the lanes lane's hooks.json lays, lane:up's record holding the calls
    and messages before it."""

    LAID = ()

    def setUp(self) -> None:
        super().setUp()
        self.data = os.path.join(self.base, "data")
        self.proposal_file = os.path.join(self.data, "notes.json")
        self.made: list = []

    def entry(self, event: str) -> list[str]:
        """The words the command of lane's hook of the event gives the guard."""
        [command] = hooks_file.commands(hooks_file.read(helpers.LANE), event)
        return hooks_file.words(command, event)

    def check(self, tool: str, given: dict) -> tuple:
        """What the guard does on lane:up's call of the tool with the input, after those made."""
        self.record(self.made)
        event = json.dumps(self.called(tool, given, "lane:up"))
        return self.guard(event, self.entry("PreToolUse"), plugin=helpers.LANE)

    def ending(self, reply: str) -> tuple:
        """What the guard does as lane:up is about to end its turn with the reply, after the calls
        made; the reply is then made."""
        self.record(self.made)
        event = json.dumps(self.stopped(reply, agent_type="lane:up"))
        found = self.guard(event, self.entry("SubagentStop"), "subagentstop.py", helpers.LANE)
        self.made.append(helpers.replied(reply))
        return found

    def run_as_made(self, tool: str, given: dict, result: str = "") -> None:
        """Checks that lane:up's call is let through, then makes it, giving back the result."""
        self.assertEqual(self.check(tool, given), ("", ""), given)
        self.made.append((tool, given, result))

    def bash(self, command: str, result: str = "") -> None:
        """Checks that lane:up's Bash call of the command is let through, then makes it."""
        self.run_as_made("Bash", {"command": command}, result)

    def lay_py(self, *argv: str) -> str:
        """What lay.py prints run with the arguments, as lane:up's Bash call gives it back."""
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            lay.main(list(argv))
        return out.getvalue()

    def up_to_step_5(self) -> None:
        """lane:up's steps 1 to 5 made: `lay.py up`, lane's lanes, the plugin's files, and the
        points sent and answered, one checked again against the line it cites."""
        up = self.lay_py("up", self.plugin, self.data)
        self.bash(f"{LAY} up {self.plugin} {self.data}", up)
        self.bash(f"cat -n {LANES_MD}")
        self.bash(f"cat -n {self.plugin}/.claude-plugin/plugin.json")
        self.bash(f"find {self.plugin}/skills {self.plugin}/agents -name '*.md'", self.agent_file)
        self.bash(f"cat -n {self.agent_file}")
        self.run_as_made("Read", {"file_path": self.agent_file, "offset": 23, "limit": 1})
        point = "1. lane:up asks: is `CHANGELOG.md` the only file step 3 writes?"
        self.assertEqual(self.ending(point), ("", ""))
        self.made.append(helpers.from_main("1. Yes."))

    def up_to_step_7(self) -> None:
        """lane:up's steps 1 to 7 made: the proposal, left by a run before, read and written, and
        printed and handed on."""
        self.up_to_step_5()
        proposal = {
            "plugin": self.plugin,
            "subagents": [
                {
                    "name": "changelog-writer",
                    "steps": [{"step": 3, "lanes": [{"lane": "write_only", "takes": ["x"]}]}],
                }
            ],
        }
        self.run_as_made("Read", {"file_path": self.proposal_file})
        self.write_json(self.proposal_file, proposal)
        self.run_as_made("Write", {"file_path": self.proposal_file, "content": "{}"})
        printed = self.lay_py("print", self.proposal_file)
        self.bash(f"{LAY} print {self.proposal_file}", printed)
        heading = "lane:up proposes these lanes; send OK or what to change."
        self.assertEqual(self.ending(f"{heading}\n\n{printed}"), ("", ""))


class TestStepsLetThrough(UpTest):
    def test_each_call_of_a_run_to_the_lanes_written_is_let_through(self):
        # Given: lane:up's steps 1 to 7 made, and the building AI's OK
        self.up_to_step_7()
        self.made.append(helpers.from_main("OK"))
        # When: it runs `lay.py write`, and ends with its print
        # Then: each call goes on, and it ends, nothing said
        self.bash(f"{LAY} write {self.proposal_file}")
        self.assertEqual(self.ending("Wrote step 3 of changelog-writer."), ("", ""))

    def test_a_proposal_declined_is_removed(self):
        # Given: lane:up's steps 1 to 7 made, and the building AI asking for no lanes at all
        self.up_to_step_7()
        self.made.append(helpers.from_main("No lanes at all."))
        # When: it removes the proposal, and ends saying nothing was written
        # Then: the call goes on, and it ends, nothing said
        self.bash(f"rm -f {self.proposal_file}")
        self.assertEqual(self.ending("Nothing was written into the plugin."), ("", ""))


class TestStopped(UpTest):
    def test_a_call_before_lay_py_up_is_stopped(self):
        for tool, given in (
            ("Bash", {"command": f"ls {self.plugin}/.claude-plugin"}),
            ("Read", {"file_path": f"{self.plugin}/.claude-plugin/plugin.json"}),
        ):
            with self.subTest(tool=tool):
                # Given: lane:up having made no call
                # When: it first looks into the plugin
                # Then: the call is stopped with start_with's sentence
                self.assertEqual(self.check(tool, given), ("told", BEGIN))

    def test_a_read_beyond_what_lay_py_up_printed_is_stopped(self):
        # Given: lane:up's steps 1 to 5 made, `lay.py up` having printed what it reads
        self.up_to_step_5()
        reads = [
            f"{self.plugin}/.claude-plugin/plugin.json",
            f"{self.plugin}/skills",
            f"{self.plugin}/agents",
            LANES_MD,
            self.proposal_file,
        ]
        told = "lane: Read only `{reads}`.\n`{reads}` is " + ", ".join(f"`{r}`" for r in reads)
        for tool, given in (
            ("Bash", {"command": f"sed -n 190,203p {helpers.SCRIPTS}/steps.py"}),
            ("Bash", {"command": f'grep -n "def \\|sentence" {helpers.SCRIPTS}/lay.py'}),
            ("Read", {"file_path": os.path.join(helpers.CODE, "guard.py")}),
            ("Grep", {"pattern": "evaluator"}),
            ("Bash", {"command": f"cat -n {self.plugin}/README.md"}),
        ):
            with self.subTest(given=given):
                # When: it reads lane's own code, searches the folder it runs in, or reads a file
                # of the plugin beside its manifest, skills and agents
                # Then: the call is stopped with read_only's sentence and what lane:up reads
                self.assertEqual(self.check(tool, given), ("told", f"{told}."))


if __name__ == "__main__":
    unittest.main()
