"""The cases of lay.py's contract: `print` shows a proposal's steps as they'll read, and `write`
lays them into the plugin, as the architecture's sequences "S1: lay.py print" and "S2: lay.py
write" draw them."""

import io
import json
import os
import subprocess
import sys
from unittest import mock

import helpers
from helpers import entries, lay, testing


class LayTest(testing.FolderTest):
    def setUp(self):
        super().setUp()
        self.root = os.path.join(self.base, "changelog")
        helpers.changelog(self.root, with_lanes=False)
        self.folder = os.path.join(self.base, ".lane", "20261108-changelog")
        self.path = os.path.join(self.folder, "changelog.json")
        self.propose()
        # A stand-in for Claude Code's `claude`, which passes the plugin unless told otherwise.
        self.claude("echo passed")

    def propose(self, roles=None, **more):
        roles = [helpers.WRITER_LANES] if roles is None else roles
        helpers.write(self.path, json.dumps({"plugin": "changelog", "subagents": roles, **more}))

    def claude(self, body):
        helpers.write(os.path.join(self.base, "bin", "claude"), f"#!/bin/sh\n{body}\n")
        os.chmod(os.path.join(self.base, "bin", "claude"), 0o755)

    def lay(self, *argv, path=None):
        out, err = io.StringIO(), io.StringIO()
        env = {"PATH": f"{self.base}/bin:/usr/bin:/bin"} if path is None else {"PATH": path}
        with mock.patch.dict(os.environ, env):
            code = lay.main(["lay.py", *argv], out, err, helpers.LANE)
        return code, out.getvalue(), err.getvalue()


class TestPrint(LayTest):
    def test_each_step_is_shown_as_it_will_read(self):
        code, out, _ = self.lay("print", self.path)
        self.assertEqual(
            (code, out),
            (
                0,
                (
                    f"changelog: the lanes of {self.root}, as lay.py write would lay them\n"
                    "\n"
                    "writer, in agents/writer.md\n"
                    "commands: `git log --oneline`\n"
                    "1. Read `CHANGELOG.md` to learn its last version and its form.\n"
                    "2. Read the commits since then with `git log --oneline`. Run only"
                    " `git log --oneline`.\n"
                    "3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.\n"
                    "4. Reply with the entries you wrote.\n"
                ),
            ),
        )

    def test_print_writes_nothing(self):
        self.lay("print", self.path)
        self.assertEqual(self.read("changelog/agents/writer.md"), helpers.WRITER)

    def test_a_step_naming_a_command_its_role_may_not_run_is_marked(self):
        helpers.write(
            os.path.join(self.root, "agents", "writer.md"),
            helpers.WRITER.replace("4. Reply", "4. Check with `git status`, then reply"),
        )
        _, out, _ = self.lay("print", self.path)
        self.assertIn("step 4 names `git status`, which writer may not run\n", out)

    def test_a_step_naming_a_command_by_its_last_words_is_not_marked(self):
        lanes = [{"lane": "run_only", "takes": ["python3 ${CLAUDE_PLUGIN_ROOT}/s/tree.py write x"]}]
        helpers.write(
            os.path.join(self.root, "agents", "writer.md"),
            helpers.WRITER.replace("4. Reply", "4. Run `tree.py write x`, then reply"),
        )
        self.propose([{"name": "writer", "steps": [{"step": 2, "lanes": lanes}]}])
        _, out, _ = self.lay("print", self.path)
        self.assertNotIn("names `tree.py write x`", out)

    def test_a_role_with_no_run_only_lane_has_no_commands_line(self):
        lanes = [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]
        self.propose([{"name": "writer", "steps": [{"step": 3, "lanes": lanes}]}])
        _, out, _ = self.lay("print", self.path)
        self.assertNotIn("commands:", out)

    def test_a_part_with_no_numbered_list_shows_the_sentences_given_as_the_role_starts(self):
        helpers.write(
            os.path.join(self.root, "agents", "writer.md"),
            "---\nname: writer\nbackground: true\n---\nWrite the entries.\n",
        )
        _, out, _ = self.lay("print", self.path)
        self.assertIn(
            "writer, in agents/writer.md, which holds no numbered list, so writer is given these"
            " as it starts:\n"
            "- Run only `git log --oneline`.\n"
            "- Write only `CHANGELOG.md`.\n",
            out,
        )

    def test_a_proposal_that_cannot_stand_shows_whats_wrong_and_exits_1(self):
        self.propose([{**helpers.WRITER_LANES, "name": "noter"}])
        code, out, err = self.lay("print", self.path)
        self.assertEqual(
            (code, out, err), (1, "", f"lay.py: no agents/*.md names `noter` in {self.root}\n")
        )


class TestWrite(LayTest):
    def test_the_sentences_are_written_into_the_steps(self):
        self.lay("write", self.path)
        self.assertEqual(self.read("changelog/agents/writer.md"), helpers.WRITER_LAID)

    def test_the_lanes_are_written_into_hooks_lanes_json(self):
        self.lay("write", self.path)
        self.assertEqual(
            self.read_json("changelog/hooks/lanes.json"), {"subagents": [helpers.WRITER_LANES]}
        )

    def test_the_hook_entries_are_written_beside_the_plugins_own(self):
        own = {"hooks": {"Notification": [{"hooks": [{"type": "command", "command": "x"}]}]}}
        helpers.write(os.path.join(self.root, "hooks", "hooks.json"), json.dumps(own))
        self.lay("write", self.path)
        self.assertEqual(
            self.read_json("changelog/hooks/hooks.json"),
            entries.merged(own, "changelog", ("changelog:writer",)),
        )

    def test_lanes_code_is_laid(self):
        self.lay("write", self.path)
        self.assertTrue(os.path.isfile(os.path.join(self.root, "hooks", "lane", "hook.py")))

    def test_the_proposal_and_its_folder_are_removed_once_written(self):
        self.lay("write", self.path)
        self.assertFalse(os.path.exists(self.folder))

    def test_what_was_written_is_shown(self):
        code, out, _ = self.lay("write", self.path)
        self.assertEqual(
            (code, out),
            (
                0,
                (
                    f"changelog: lay.py wrote into {self.root}:\n"
                    "- agents/writer.md, the sentences of its lanes\n"
                    "- hooks/lanes.json\n"
                    "- hooks/hooks.json\n"
                    "- hooks/lane, a copy of Lane's code at"
                    f" {lay.lane_code.version(helpers.LANE)}\n"
                    "claude plugin validate passed it, so lay.py removed"
                    f" {self.folder}.\n"
                ),
            ),
        )

    def test_a_proposal_that_cannot_stand_writes_nothing(self):
        self.propose([{**helpers.WRITER_LANES, "name": "noter"}])
        code, _, _ = self.lay("write", self.path)
        self.assertEqual((code, os.path.exists(os.path.join(self.root, "hooks"))), (1, False))

    def test_a_plugin_claude_finds_malformed_keeps_the_proposal_and_exits_1(self):
        self.claude("echo 'manifest: bad'; exit 1")
        code, _, err = self.lay("write", self.path)
        self.assertEqual(
            (code, err, os.path.exists(self.path)),
            (
                1,
                (
                    "lay.py: claude plugin validate found the plugin malformed:\nmanifest: bad\n"
                    f"Fix it, then run lay.py write {self.path} again: the proposal is kept.\n"
                ),
                True,
            ),
        )

    def test_no_claude_on_the_path_keeps_the_proposal_and_exits_1(self):
        code, _, err = self.lay("write", self.path, path="/nowhere")
        self.assertEqual(
            (code, err, os.path.exists(self.path)),
            (
                1,
                (
                    "lay.py: claude isn't on PATH, so claude plugin validate couldn't check the"
                    f" plugin. Install Claude Code, then run lay.py write {self.path} again: the"
                    " proposal is kept.\n"
                ),
                True,
            ),
        )

    def test_a_lane_left_out_of_a_new_proposal_has_its_sentence_taken_out(self):
        self.lay("write", self.path)
        lanes = [{"lane": "write_only", "takes": ["CHANGELOG.md"]}]
        self.propose([{"name": "writer", "steps": [{"step": 3, "lanes": lanes}]}])
        self.lay("write", self.path)
        self.assertEqual(
            self.read("changelog/agents/writer.md"),
            helpers.WRITER_LAID.replace(" Run only `git log --oneline`.", ""),
        )

    def test_a_part_with_no_numbered_list_is_left_as_it_was(self):
        text = "---\nname: writer\nbackground: true\n---\nWrite the entries.\n"
        helpers.write(os.path.join(self.root, "agents", "writer.md"), text)
        self.lay("write", self.path)
        self.assertEqual(self.read("changelog/agents/writer.md"), text)

    def test_a_part_shared_by_two_roles_gets_its_sentences_once(self):
        helpers.share_part(self.root)
        lanes = [{"lane": "write_only", "takes": ["a"]}]
        self.propose(
            [{"name": n, "steps": [{"step": 2, "lanes": lanes}]} for n in ("writer", "drafter")]
        )
        self.lay("write", self.path)
        self.assertEqual(
            self.read("changelog/domain/writer.md"), "1. Read.\n2. Write. Write only `a`.\n"
        )


class TestUsage(LayTest):
    def test_run_as_a_script_it_exits_with_its_code(self):
        script = os.path.join(helpers.SCRIPTS, "lay.py")
        done = subprocess.run([sys.executable, "-B", script], capture_output=True, check=False)
        self.assertEqual(done.returncode, 2)

    def test_no_command_shows_how_to_run_it_and_exits_2(self):
        code, _, err = self.lay()
        self.assertEqual(
            (code, err),
            (
                2,
                (
                    "lay.py: run it as `lay.py print <proposal>`, `lay.py write <proposal>` or"
                    " `lay.py up <plugin folder>`\n"
                ),
            ),
        )

    def test_an_unknown_command_shows_how_to_run_it_and_exits_2(self):
        self.assertEqual(self.lay("show", self.path)[0], 2)
