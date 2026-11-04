"""S7 of dev/lane/architecture.md, `lay.py up`, one test for each of its paths: lay.py run as the
developer AI runs it after Lane is updated, on a copy of `changelog` laid by `lay.py write` with the
README's proposal, and lay.py and the files it lays real."""

import os
import subprocess
import sys
import unittest

import helpers


class TestUp(helpers.RunTest):
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
            [sys.executable, helpers.LAY, "up", folder],
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
