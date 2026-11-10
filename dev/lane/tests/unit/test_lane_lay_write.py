"""`lay.py write`: a proposal that can stand laid into the plugin, and one that can't refused with
nothing written."""

from __future__ import annotations

import filecmp
import json
import os

from lanetest import FAILED, LANE, WRITER_RUN_ONLY, RepositoryTest

ENTRY = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/hook.py" changelog'


def with_takes(*takes: str) -> dict:
    """The proposal of the README's run_only rule on writer's step 2, with other takes."""
    lane = {"lane": "run_only", "takes": list(takes)}
    return {
        **WRITER_RUN_ONLY,
        "subagents": [{"name": "writer", "steps": [{"step": 2, "lanes": [lane]}]}],
    }


class Writes(RepositoryTest):
    def test_the_sentence_ends_its_step(self) -> None:
        self.assertEqual(self.lay("write", self.propose(WRITER_RUN_ONLY)).returncode, 0)
        self.assertIn(
            "2. Read the commits since then with `git log --oneline`."
            " Run only `git log --oneline`.\n",
            self.read("changelog", "agents", "writer.md"),
        )

    def test_the_rules_go_into_lanes_json(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        self.assertEqual(
            json.loads(self.read("changelog", "hooks", "lanes.json")),
            {
                "plugin": "changelog",
                "subagents": {"writer": {"steps": WRITER_RUN_ONLY["subagents"][0]["steps"]}},
            },
        )

    def test_the_hook_entry_runs_the_guard_on_each_tool_call(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        hooks = json.loads(self.read("changelog", "hooks", "hooks.json"))
        self.assertEqual(
            hooks["hooks"]["PreToolUse"],
            [{"matcher": "*", "hooks": [{"type": "command", "command": ENTRY}]}],
        )

    def test_the_plugins_own_hook_entries_stay(self) -> None:
        own = {"matcher": "Write", "hooks": [{"type": "command", "command": "echo own"}]}
        self.write(json.dumps({"hooks": {"PreToolUse": [own]}}), "changelog", "hooks", "hooks.json")
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        entries = json.loads(self.read("changelog", "hooks", "hooks.json"))["hooks"]["PreToolUse"]
        self.assertEqual(entries[0], own)
        self.assertEqual(len(entries), 2)

    def test_lanes_code_is_laid_into_the_plugin(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        laid = self.path("changelog", "hooks", "lane")
        compared = filecmp.dircmp(os.path.join(LANE, "hooks", "lane"), laid, ignore=["__pycache__"])
        self.assertEqual(
            (compared.left_only, compared.right_only, compared.diff_files), ([], [], [])
        )
        self.assertFalse(os.path.exists(os.path.join(laid, "__pycache__")))

    def test_the_proposal_and_its_folder_go(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        self.assertFalse(os.path.exists(self.path(".lane", "20261110-changelog")))

    def test_it_says_what_it_wrote(self) -> None:
        out = self.lay("write", self.propose(WRITER_RUN_ONLY)).stdout
        self.assertEqual(
            out,
            "Wrote step 2 of writer into agents/writer.md.\n"
            "Wrote the checks of writer into hooks/hooks.json.\n"
            "Wrote the lanes laid into hooks/lanes.json.\n"
            "Put lane's code in hooks/lane/.\n"
            "claude plugin validate passed.\n"
            "Removed the proposal .lane/20261110-changelog/changelog.json.\n"
            f"Removed its folder {self.path('.lane', '20261110-changelog')}.\n",
        )

    def test_steps_are_named_in_one_line(self) -> None:
        lane = {"lane": "run_only", "takes": ["git diff"]}
        proposal = {
            **WRITER_RUN_ONLY,
            "subagents": [
                {"name": "writer", "steps": [{"step": n, "lanes": [lane]} for n in (1, 2, 3)]}
            ],
        }
        out = self.lay("write", self.propose(proposal)).stdout
        self.assertIn("Wrote steps 1, 2 and 3 of writer into agents/writer.md.\n", out)

    def test_a_rule_written_again_takes_the_place_of_the_one_before(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        self.lay("write", self.propose(with_takes("git log")))
        self.assertIn(
            "with `git log --oneline`. Run only `git log`.\n",
            self.read("changelog", "agents", "writer.md"),
        )

    def test_the_hook_entry_is_written_once_however_often_it_writes(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        entries = json.loads(self.read("changelog", "hooks", "hooks.json"))["hooks"]["PreToolUse"]
        self.assertEqual(len(entries), 1)


class Validates(RepositoryTest):
    def test_a_plugin_claude_code_refuses_keeps_the_proposal(self) -> None:
        self.claude(FAILED, 1)
        ran = self.lay("write", self.propose(WRITER_RUN_ONLY))
        self.assertEqual(ran.returncode, 1)
        self.assertIn(FAILED, ran.stdout)
        self.assertIn(
            "Fix what claude plugin validate found, and run lay.py write again.", ran.stdout
        )
        self.assertTrue(os.path.exists(self.path(".lane", "20261110-changelog", "changelog.json")))

    def test_a_validation_that_cant_run_keeps_the_proposal(self) -> None:
        os.remove(os.path.join(self.bin, "claude"))
        self.env["PATH"] = self.bin
        ran = self.lay("write", self.propose(WRITER_RUN_ONLY))
        self.assertEqual(ran.returncode, 1)
        self.assertIn("claude plugin validate couldn't run, as claude isn't on PATH.", ran.stdout)
        self.assertTrue(os.path.exists(self.path(".lane", "20261110-changelog", "changelog.json")))


class Refuses(RepositoryTest):
    def refused(self, proposal: object, *, path: str = "") -> str:
        """What lay.py write says of a proposal it refuses, checking it exits 1 with nothing
        written."""
        before = self.read("changelog", "agents", "writer.md")
        ran = self.lay("write", path or self.propose(proposal))
        self.assertEqual(ran.returncode, 1)
        self.assertEqual(self.read("changelog", "agents", "writer.md"), before)
        self.assertFalse(os.path.exists(self.path("changelog", "hooks")))
        return ran.stderr

    def test_a_proposal_that_isnt_json(self) -> None:
        self.assertIn("isn't JSON", self.refused("{"))

    def test_a_proposal_out_of_its_folder(self) -> None:
        self.write(json.dumps(WRITER_RUN_ONLY), "changelog.json")
        said = self.refused(None, path=self.path("changelog.json"))
        self.assertIn("keep the proposal as .lane/<yyyymmdd>-<plugin>/<plugin>.json", said)

    def test_a_proposal_out_of_its_form(self) -> None:
        self.assertIn(
            "$.subagents: expected a list", self.refused({**WRITER_RUN_ONLY, "subagents": {}})
        )

    def test_a_plugin_folder_with_no_manifest(self) -> None:
        said = self.refused({**WRITER_RUN_ONLY, "plugin": "missing"})
        self.assertIn("missing/.claude-plugin/plugin.json isn't there", said)

    def test_a_subagent_with_no_file(self) -> None:
        proposal = {
            **WRITER_RUN_ONLY,
            "subagents": [{**WRITER_RUN_ONLY["subagents"][0], "name": "drafter"}],
        }
        self.assertIn("agents/drafter.md isn't there", self.refused(proposal))

    def test_a_subagent_that_doesnt_run_in_the_background(self) -> None:
        text = self.read("changelog", "agents", "writer.md").replace("background: true\n", "")
        self.write(text, "changelog", "agents", "writer.md")
        self.assertIn(
            "agents/writer.md doesn't set `background: true`", self.refused(WRITER_RUN_ONLY)
        )

    def test_a_step_the_subagent_lacks(self) -> None:
        lane = {"lane": "run_only", "takes": ["git diff"]}
        proposal = {
            **WRITER_RUN_ONLY,
            "subagents": [{"name": "writer", "steps": [{"step": 9, "lanes": [lane]}]}],
        }
        self.assertIn("agents/writer.md: no step 9", self.refused(proposal))

    def test_a_type_lane_doesnt_know(self) -> None:
        lane = {"lane": "run_never", "takes": ["git push"]}
        proposal = {
            **WRITER_RUN_ONLY,
            "subagents": [{"name": "writer", "steps": [{"step": 2, "lanes": [lane]}]}],
        }
        self.assertIn(
            "writer step 2: no type run_never; the types are run_only", self.refused(proposal)
        )

    def test_takes_the_type_refuses(self) -> None:
        self.assertIn(
            "writer step 2: run_only takes at least one command", self.refused(with_takes())
        )


class Usage(RepositoryTest):
    def test_no_command_shows_the_usage(self) -> None:
        ran = self.lay()
        self.assertEqual(ran.returncode, 2)
        self.assertIn("usage: lay.py write <proposal>", ran.stderr)
