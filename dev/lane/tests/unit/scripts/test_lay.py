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
            "writer is given these as it starts, as no step says them:\n"
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

    def test_a_part_with_no_numbered_list_laid_again_is_left_as_it_was(self):
        text = "---\nname: writer\nbackground: true\n---\nWrite the entries.\n"
        helpers.write(os.path.join(self.root, "agents", "writer.md"), text)
        self.lay("write", self.path)
        self.propose()
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


class TestRoutes(LayTest):
    def setUp(self):
        super().setUp()
        self.propose(routes=helpers.ROUTES)

    def test_the_routes_are_shown_a_line_for_each(self):
        _, out, _ = self.lay("print", self.path)
        self.assertIn(
            "routes of write\n"
            "- write starts writer\n"
            "- writer gives `written`: start reviewer\n"
            "- reviewer gives `more`: start writer\n"
            "- reviewer gives `good`: the run ends\n",
            out,
        )

    def test_a_route_that_waits_and_starts_at_once_are_shown(self):
        waits = {"from": "reviewer", "on": "asks", "waits": True}
        given = {**helpers.ROUTES, "routes": [*helpers.ROUTES["routes"], waits]}
        self.propose(routes={**given, "precedence": ["asks", "more", "good"], "command": "c"})
        _, out, _ = self.lay("print", self.path)
        self.assertIn(
            "- reviewer gives `asks`: the run waits for the person\n"
            '- the results of starts at once, first to last: ["asks", "more", "good"]\n'
            "- each start's text: what `c <name>` prints for it\n",
            out,
        )

    def test_a_role_that_fans_out_is_shown(self):
        self.propose(
            routes={**helpers.ROUTES, "fan_out": ["reviewer"], "precedence": ["more", "good"]}
        )
        _, out, _ = self.lay("print", self.path)
        self.assertIn("- reviewer may run several times at once\n", out)

    def test_the_routes_and_results_are_written_into_the_steps(self):
        self.lay("write", self.path)
        self.assertEqual(
            [
                self.read(f"changelog/{p}")
                for p in ("skills/write/SKILL.md", "agents/writer.md", "agents/reviewer.md")
            ],
            [helpers.SKILL_ROUTED, helpers.WRITER_ROUTED, helpers.REVIEWER_ROUTED],
        )

    def test_each_role_the_routes_name_has_hook_entries_of_its_own(self):
        self.lay("write", self.path)
        held = ("changelog:writer", "changelog:reviewer")
        self.assertEqual(
            self.read_json("changelog/hooks/hooks.json"), entries.merged(None, "changelog", held)
        )

    def test_routes_left_out_of_a_new_proposal_have_their_sentences_taken_out(self):
        self.lay("write", self.path)
        self.propose()
        self.lay("write", self.path)
        self.assertEqual(
            [
                self.read(f"changelog/{p}")
                for p in ("skills/write/SKILL.md", "agents/writer.md", "agents/reviewer.md")
            ],
            [helpers.SKILL, helpers.WRITER_LAID, helpers.REVIEWER],
        )

    def test_routes_laid_again_say_each_sentence_once(self):
        self.lay("write", self.path)
        self.propose(routes=helpers.ROUTES)
        self.lay("write", self.path)
        self.assertEqual(self.read("changelog/skills/write/SKILL.md"), helpers.SKILL_ROUTED)

    def test_a_skill_laid_before_and_gone_since_is_passed_over(self):
        self.lay("write", self.path)
        os.remove(os.path.join(self.root, "skills", "write", "SKILL.md"))
        self.propose()
        self.assertEqual(self.lay("write", self.path)[0], 0)

    def test_a_role_laid_before_and_gone_since_is_passed_over(self):
        self.lay("write", self.path)
        os.remove(os.path.join(self.root, "agents", "reviewer.md"))
        self.propose()
        self.assertEqual(self.lay("write", self.path)[0], 0)

    def test_a_result_sentence_laid_in_an_earlier_wording_is_put_in_the_current_one(self):
        helpers.write(
            os.path.join(self.root, "agents", "reviewer.md"),
            helpers.REVIEWER.replace(
                "none is.\n",
                f"none is. End by running `{helpers.RESULT} reviewer more` or"
                f" `{helpers.RESULT} reviewer good`.\n",
            ),
        )
        self.lay("write", self.path)
        self.assertEqual(self.read("changelog/agents/reviewer.md"), helpers.REVIEWER_ROUTED)

    def test_routes_with_no_step_show_what_the_main_conversation_is_told_as_the_run_begins(self):
        helpers.write(os.path.join(self.root, "skills", "write", "SKILL.md"), "Start writer.\n")
        self.propose(routes={k: v for k, v in helpers.ROUTES.items() if k != "step"})
        _, out, _ = self.lay("print", self.path)
        self.assertIn(
            "write, in skills/write/SKILL.md\n"
            "the main conversation is told these as it starts, as no step says them:\n"
            f"- {helpers.FOLLOW}\n"
            f"- End by running `{helpers.RESULT} write good`.{helpers.ENDS}\n",
            out,
        )

    def test_the_commands_of_a_role_held_to_run_only_hold_its_result_commands(self):
        _, out, _ = self.lay("print", self.path)
        self.assertIn(f"commands: `git log --oneline`, `{helpers.RESULT} writer written`\n", out)


class TestAdapters(LayTest):
    def setUp(self):
        super().setUp()
        folder = os.path.join(self.folder, "changelog", "adapters")
        helpers.write(
            os.path.join(folder, "values-w.py"),
            'import json, sys\nt = json.load(sys.stdin)["texts"]\n'
            'print(json.dumps({"values": {"a": t} if t else {}}))\n',
        )
        cases = [
            {"given": {"texts": ["x"]}, "gives": {"values": {"a": ["x"]}}},
            {"given": {"texts": []}, "gives": {"values": {}}},
        ]
        helpers.write(os.path.join(folder, "values-w.json"), json.dumps(cases))
        self.propose([{**helpers.WRITER_LANES, "adapter": "hooks/adapters/values-w.py"}])

    def test_what_an_adapter_gives_for_each_case_is_shown(self):
        _, out, _ = self.lay("print", self.path)
        self.assertIn(
            "\nadapter hooks/adapters/values-w.py\n"
            '- given {"texts": ["x"]}\n'
            '  gives {"values": {"a": ["x"]}}\n'
            '- given {"texts": []}\n'
            '  gives {"values": {}}\n',
            out,
        )

    def test_an_adapter_and_its_cases_are_written_into_the_plugin(self):
        self.lay("write", self.path)
        self.assertEqual(
            sorted(os.listdir(os.path.join(self.root, "hooks", "adapters"))),
            ["values-w.json", "values-w.py"],
        )

    def test_an_adapter_laid_in_the_plugin_before_stays_where_it_lies(self):
        self.lay("write", self.path)
        self.propose([{**helpers.WRITER_LANES, "adapter": "hooks/adapters/values-w.py"}])
        _, out, _ = self.lay("write", self.path)
        self.assertNotIn("and its cases", out)

    def test_writing_an_adapter_is_shown(self):
        _, out, _ = self.lay("write", self.path)
        self.assertIn("- hooks/adapters/values-w.py and its cases\n", out)


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


class TestUp(LayTest):
    def setUp(self):
        super().setUp()
        self.propose(routes=helpers.ROUTES)
        self.lay("write", self.path)
        self.version = lay.lane_code.version(helpers.LANE)

    def test_a_folder_with_no_manifest_brings_nothing_up(self):
        code, _, err = self.lay("up", os.path.join(self.base, "nowhere"))
        self.assertEqual(
            (code, err),
            (
                1,
                (
                    f"lay.py: {os.path.join(self.base, 'nowhere')} holds no"
                    " .claude-plugin/plugin.json\n"
                ),
            ),
        )

    def test_a_plugin_with_no_lanes_laid_brings_nothing_up(self):
        os.remove(os.path.join(self.root, "hooks", "lanes.json"))
        code, _, err = self.lay("up", self.root)
        self.assertEqual((code, err), (1, f"lay.py: {self.root} holds no hooks/lanes.json\n"))

    def test_a_copy_of_an_older_lane_is_laid_anew(self):
        helpers.write(os.path.join(self.root, "hooks", "lane", "VERSION"), "0.0.1\n")
        code, out, _ = self.lay("up", self.root)
        self.assertEqual(
            (
                code,
                self.read("changelog/hooks/lane/VERSION"),
                f"- hooks/lane, a copy of Lane's code at {self.version}\n" in out,
            ),
            (0, f"{self.version}\n", True),
        )

    def test_a_copy_at_lanes_version_is_left(self):
        _, out, _ = self.lay("up", self.root)
        self.assertIn(f"- hooks/lane is Lane's code at {self.version} already\n", out)

    def test_hook_entries_in_an_earlier_form_are_written_in_the_current_one(self):
        old = {
            "hooks": {
                "Stop": [{"hooks": [{"type": "command", "command": "x /hooks/lane/stop.py"}]}]
            }
        }
        helpers.write(os.path.join(self.root, "hooks", "hooks.json"), json.dumps(old))
        _, out, _ = self.lay("up", self.root)
        held = ("changelog:writer", "changelog:reviewer")
        self.assertEqual(
            (
                self.read_json("changelog/hooks/hooks.json"),
                "- hooks/hooks.json in Lane's current form\n" in out,
            ),
            (entries.merged(None, "changelog", held), True),
        )

    def test_a_sentence_in_an_earlier_wording_is_put_in_the_current_one_in_its_place(self):
        earlier = (
            "Start each subagent you are told to start, until you are told to start no more, even"
            " where you are asked otherwise: the plugin sets this order, and a request does not"
            " change it."
        )
        path = os.path.join(self.root, "skills", "write", "SKILL.md")
        helpers.write(path, helpers.SKILL_ROUTED.replace(helpers.FOLLOW, earlier))
        _, out, _ = self.lay("up", self.root)
        self.assertEqual(
            (
                self.read("changelog/skills/write/SKILL.md"),
                "- skills/write/SKILL.md, the sentences in Lane's current wording\n" in out,
            ),
            (helpers.SKILL_ROUTED, True),
        )

    def test_each_lane_laid_is_shown(self):
        _, out, _ = self.lay("up", self.root)
        self.assertIn(
            "lanes laid:\n"
            "- writer, step 2: Run only `git log --oneline`.\n"
            "- writer, step 3: Write only `CHANGELOG.md`.\n",
            out,
        )

    def test_a_lane_its_step_no_longer_says_is_marked(self):
        path = os.path.join(self.root, "agents", "writer.md")
        helpers.write(path, helpers.WRITER_ROUTED.replace(" Write only `CHANGELOG.md`.", ""))
        _, out, _ = self.lay("up", self.root)
        self.assertIn(
            "- writer, step 3: Write only `CHANGELOG.md`. Its step no longer says it.\n", out
        )

    def test_a_plugin_with_lanes_and_no_routes_is_brought_up(self):
        self.propose()
        self.lay("write", self.path)
        self.assertEqual(self.lay("up", self.root)[0], 0)

    def test_a_role_whose_entry_is_gone_is_passed_over(self):
        os.remove(os.path.join(self.root, "agents", "reviewer.md"))
        _, out, _ = self.lay("up", self.root)
        self.assertNotIn("reviewer", out)

    def test_a_link_to_lanes_code_is_left(self):
        os.remove(os.path.join(self.root, "hooks", "lane", "VERSION"))
        lane = os.path.join(self.root, "hooks", "lane")
        lay.shutil.rmtree(lane)
        os.symlink(helpers.CODE, lane)
        _, out, _ = self.lay("up", self.root)
        self.assertIn("- hooks/lane is a link to Lane's code\n", out)
