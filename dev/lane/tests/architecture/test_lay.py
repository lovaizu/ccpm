"""lay.py run as the developer AI runs it, on a copy of the README's plugin `changelog` taken from
the README's walkthrough, with a stand-in for Claude Code's `claude` on PATH: what `lay.py print`
and `lay.py write` print, set beside what the walkthrough shows, and the files written."""

import json
import os
import re
import subprocess
import sys
import unittest

import helpers
from helpers import testing

LAY = os.path.join(helpers.SCRIPTS, "lay.py")
with open(os.path.join(helpers.LANE, "README.md"), encoding="utf-8") as f:
    README = f.read().split("\n## Walkthrough")[1].split("\n## How it works")[0]
# The walkthrough's blocks, in order: the manifest, writer, the proposal, and the two runs.
BLOCKS = re.findall(r"```[a-z]+\n(.*?)```", README, re.DOTALL)
MANIFEST, WRITER, PROPOSAL, PRINTED, WROTE = BLOCKS
# A stand-in for `claude`, whose `plugin validate` passes.
CLAUDE = "#!/bin/sh\necho '✔ Validation passed'\n"


def shown(block: str) -> str:
    """What the walkthrough shows a run printing, the line of the command left out."""
    return block.split("\n", 1)[1]


class TestLay(testing.FolderTest):
    def setUp(self) -> None:
        super().setUp()
        self.write(os.path.join("changelog", ".claude-plugin", "plugin.json"), MANIFEST)
        self.write(os.path.join("changelog", "agents", "writer.md"), WRITER)
        self.write(helpers.PROPOSED, PROPOSAL)
        self.write(os.path.join("bin", "claude"), CLAUDE)
        os.chmod(os.path.join("bin", "claude"), 0o755)
        self.env = {
            **os.environ,
            "PATH": os.path.join(self.base, "bin") + os.pathsep + os.environ["PATH"],
        }

    def lay(self, action: str, path: str) -> subprocess.CompletedProcess:
        """lay.py run with the action on the path at the root of the repository, base."""
        return subprocess.run(
            [sys.executable, LAY, action, path],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )

    def test_print_prints_what_the_walkthrough_shows(self):
        # Given: the walkthrough's plugin and proposal
        # When: lay.py print is run on the proposal
        done = self.lay("print", helpers.PROPOSED)
        # Then: it prints what the walkthrough shows, and exits 0
        self.assertEqual((done.returncode, done.stdout), (0, shown(PRINTED)))

    def test_write_prints_what_the_walkthrough_shows_and_writes_steps_as_printed(self):
        # Given: the walkthrough's plugin and proposal
        # When: lay.py write is run on the proposal
        done = self.lay("write", helpers.PROPOSED)
        # Then: it prints what the walkthrough shows, the repository's folder put in, and exits 0
        said = shown(WROTE).replace("<the repository>", self.base)
        self.assertEqual((done.returncode, done.stdout), (0, said))
        # And: steps 2 and 3 read as print showed them, and the hook and the lanes are written
        steps = shown(PRINTED).split("\n\n", 1)[1]
        self.assertIn(steps, self.read(os.path.join("changelog", "agents", "writer.md")))
        hooks = self.read_json(os.path.join("changelog", "hooks", "hooks.json"))
        self.assertEqual(hooks, helpers.HOOKS)
        self.assertEqual(
            self.read_json(os.path.join("changelog", "hooks", "lanes.json")), helpers.RULES
        )

    def test_a_stop_is_printed_and_exits_1(self):
        # Given: no claude on PATH
        self.env["PATH"] = os.path.dirname(sys.executable)
        # When: lay.py write is run on the proposal
        done = self.lay("write", helpers.PROPOSED)
        # Then: it says so, and exits 1
        self.assertEqual(
            (done.returncode, done.stdout),
            (1, "lay.py: claude is not on PATH; install Claude Code and run again.\n"),
        )

    def test_an_adapter_beside_the_proposal_is_run_printed_and_written(self):
        # Given: the walkthrough's proposal with writer's values read by an adapter kept beside it
        beside = os.path.join(os.path.dirname(helpers.PROPOSED), "changelog", "adapters")
        self.write(os.path.join(beside, "values-w.py"), helpers.VALUES_ADAPTER)
        self.write(os.path.join(beside, "values-w.json"), json.dumps(helpers.VALUES_CASES))
        given = json.loads(PROPOSAL)
        given["subagents"][0]["adapter"] = "hooks/adapters/values-w.py"
        self.write(helpers.PROPOSED, json.dumps(given))
        # When: lay.py print, then lay.py write, is run on it
        printed = self.lay("print", helpers.PROPOSED)
        wrote = self.lay("write", helpers.PROPOSED)
        # Then: print shows the adapter run on its cases, and write puts it into the plugin
        self.assertIn(
            "  adapter hooks/adapters/values-w.py: its 2 cases given as they say\n", printed.stdout
        )
        self.assertEqual(wrote.returncode, 0, wrote.stdout)
        written = os.path.join("changelog", "hooks", "adapters", "values-w.py")
        self.assertEqual(self.read(written), helpers.VALUES_ADAPTER)
        self.assertFalse(os.path.exists(beside))

    def test_a_proposal_that_cannot_be_laid_is_printed_as_what_is_wrong_and_exits_1(self):
        # Given: the walkthrough's proposal with a lane on a step writer does not have
        given = json.loads(PROPOSAL)
        given["subagents"][0]["steps"][0]["step"] = 9
        self.write(helpers.PROPOSED, json.dumps(given))
        # When: lay.py print is run on it
        done = self.lay("print", helpers.PROPOSED)
        # Then: it prints what is wrong and how to fix it, and exits 1
        self.assertEqual(done.returncode, 1)
        self.assertTrue(
            done.stdout.startswith(
                "lay.py: the proposal gives step 9, which the Steps of writer do not have;"
            ),
            done.stdout,
        )

    def test_a_proposal_that_cannot_be_laid_writes_nothing_and_exits_1(self):
        # Given: the walkthrough's proposal with a lane on a step writer does not have
        given = json.loads(PROPOSAL)
        given["subagents"][0]["steps"][0]["step"] = 9
        self.write(helpers.PROPOSED, json.dumps(given))
        # When: lay.py write is run on it
        done = self.lay("write", helpers.PROPOSED)
        # Then: it prints what is wrong, exits 1, and writes nothing, the proposal kept
        self.assertEqual(done.returncode, 1)
        self.assertTrue(done.stdout.startswith("lay.py: the proposal gives step 9"), done.stdout)
        self.assertEqual(self.read(os.path.join("changelog", "agents", "writer.md")), WRITER)
        self.assertFalse(os.path.exists(os.path.join("changelog", "hooks")))
        self.assertTrue(os.path.exists(helpers.PROPOSED))

    def test_a_plugin_claude_finds_malformed_keeps_the_proposal_and_exits_1(self):
        # Given: a claude whose plugin validate finds the plugin malformed
        self.write(os.path.join("bin", "claude"), "#!/bin/sh\necho '✘ Found 1 error'\nexit 1\n")
        # When: lay.py write is run on the proposal
        done = self.lay("write", helpers.PROPOSED)
        # Then: it says what claude found and to run it again once fixed, keeps the proposal, and
        # exits 1
        said = (
            "lay.py: claude plugin validate found changelog malformed:\n✘ Found 1 error\n"
            f"fix what it names, then run `lay.py write {helpers.PROPOSED}` again.\n"
        )
        self.assertEqual((done.returncode, done.stdout), (1, said))
        self.assertTrue(os.path.exists(helpers.PROPOSED))


class TestLayUp(helpers.RunTest):
    """lay.py up run as the developer AI runs it after lane is updated, on a copy of `changelog`
    laid by `lay.py write` with the README's proposal."""

    def setUp(self) -> None:
        super().setUp()
        self.lay(self.ux_proposal("changelog.json"))
        self.hooks = os.path.join(self.plugin, "hooks", "hooks.json")
        self.laid = self.read(self.hooks)
        self.version = os.path.join(self.plugin, "hooks", "lane", "VERSION")

    def up(self, folder: str) -> subprocess.CompletedProcess:
        """lay.py up run on the folder."""
        return subprocess.run(
            [sys.executable, LAY, "up", folder],
            capture_output=True,
            text=True,
            env=self.env,
            check=False,
        )

    def test_a_folder_with_no_manifest_brings_nothing_up_and_exits_1(self):
        # Given: a folder that holds no plugin's manifest
        os.makedirs("notes")
        # When: lay.py up is run on it
        done = self.up("notes")
        # Then: it says it is no plugin's folder, and exits 1
        said = (
            "lay.py: notes holds no .claude-plugin/plugin.json, so it is no plugin's folder; name"
            " the folder of the plugin to lay lanes on.\n"
        )
        self.assertEqual((done.returncode, done.stdout), (1, said))

    def test_older_code_and_hooks_in_another_form_are_brought_up_and_lanes_laid_before_said(self):
        # Given: the plugin's copy of lane's code at 0.0.1, its hook entry in an old form, and
        # step 2 of writer no longer saying its lane's sentence
        self.write(self.version, "0.0.1\n")
        old = {
            "matcher": "Bash",
            "hooks": [{"type": "command", "command": "python3 x/hooks/lane/hook.py"}],
        }
        self.write_json(self.hooks, {"hooks": {"PreToolUse": [old]}})
        agent = os.path.join(self.plugin, "agents", "writer.md")
        self.write(agent, self.read(agent).replace(" Run only `git log --oneline`.", ""))
        # When: lay.py up is run on the plugin
        done = self.up("changelog")
        # Then: it brings the code up to lane's version and writes the hooks as lay.py write wrote
        # them, saying so and each lane laid before, marking the one its step no longer says
        version = self.read_json(os.path.join(helpers.LANE, ".claude-plugin", "plugin.json"))
        version = version["version"]
        said = (
            f"Brought lane's code in hooks/lane/ up from 0.0.1 to {version}.\n"
            "Wrote the hooks of writer into hooks/hooks.json.\n"
            'Laid before on step 2 of writer, whose step no longer says "Run only `git log'
            ' --oneline`.": {"lane": "run_only", "takes": ["git log --oneline"]}\n'
            'Laid before on step 3 of writer: {"lane": "write_only", "takes": ["CHANGELOG.md"]}\n'
        )
        self.assertEqual((done.returncode, done.stdout), (0, said))
        self.assertEqual(self.read(self.version), f"{version}\n")
        self.assertEqual(self.read(self.hooks), self.laid)

    def test_a_plugin_laid_at_lanes_version_has_nothing_brought_up(self):
        # Given: the plugin just laid, its code at lane's version and its hooks in lane's form
        # When: lay.py up is run on it
        done = self.up("changelog")
        # Then: it says no older copy is there and each lane laid before, changing nothing
        said = (
            "hooks/lane/ holds no older copy of lane's code.\n"
            'Laid before on step 2 of writer: {"lane": "run_only", "takes": ["git log'
            ' --oneline"]}\n'
            'Laid before on step 3 of writer: {"lane": "write_only", "takes": ["CHANGELOG.md"]}\n'
        )
        self.assertEqual((done.returncode, done.stdout), (0, said))
        self.assertEqual(self.read(self.hooks), self.laid)


if __name__ == "__main__":
    unittest.main()
