"""`lay.py print`: a proposal that can stand shown as `lay.py write` would lay it, with nothing
written, and one that can't refused."""

from __future__ import annotations

import os

from lanetest import WRITER_RUN_ONLY, RepositoryTest

WRITER_SHOWN = (
    "Lanes of writer, each checked only in writer:\n"
    "  step 2  run: Run only `git log --oneline`.  type run_only\n"
    "  commands: writer may run only `git log --oneline`\n"
    "\n"
    "2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.\n"
)


def run_only(role: str, *steps: tuple[int, list[str]]) -> dict:
    """A subagent of the proposal with a run_only rule on each step, taking the commands given."""
    return {
        "name": role,
        "steps": [
            {"step": n, "lanes": [{"lane": "run_only", "takes": takes}]} for n, takes in steps
        ],
    }


class Shows(RepositoryTest):
    def test_it_shows_the_rules_the_commands_and_the_steps_as_laid(self) -> None:
        ran = self.lay("print", self.propose(WRITER_RUN_ONLY))
        self.assertEqual((ran.returncode, ran.stdout, ran.stderr), (0, WRITER_SHOWN, ""))

    def test_it_writes_nothing(self) -> None:
        path = self.propose(WRITER_RUN_ONLY)
        before = self.read("changelog", "agents", "writer.md")
        self.assertEqual(self.lay("print", path).returncode, 0)
        self.assertEqual(self.read("changelog", "agents", "writer.md"), before)
        self.assertFalse(os.path.exists(self.path("changelog", "hooks")))
        self.assertTrue(os.path.exists(path))

    def test_a_step_that_names_a_command_the_subagent_may_not_run(self) -> None:
        text = self.read("changelog", "agents", "writer.md").replace(
            "into `CHANGELOG.md`.", "into `CHANGELOG.md`, and check them with `git status`."
        )
        self.write(text, "changelog", "agents", "writer.md")
        out = self.lay("print", self.propose(WRITER_RUN_ONLY)).stdout
        self.assertIn("  step 3  names `git status`, which writer may not run\n", out)

    def test_a_span_with_no_blank_is_no_command(self) -> None:
        out = self.lay("print", self.propose(WRITER_RUN_ONLY)).stdout
        self.assertIn("Lanes of writer", out)
        self.assertNotIn("names `CHANGELOG.md`", out)

    def test_the_commands_of_every_step_are_named_once(self) -> None:
        role = run_only(
            "writer", (2, ["git log --oneline", "git diff"]), (3, ["git diff", "ls -a"])
        )
        out = self.lay("print", self.propose({"plugin": "changelog", "subagents": [role]})).stdout
        self.assertIn(
            "  commands: writer may run only `git log --oneline`, `git diff` or `ls -a`\n", out
        )

    def test_the_sentences_line_up_in_one_column(self) -> None:
        role = run_only("writer", (2, ["git log --oneline"]), (3, ["ls"]))
        out = self.lay("print", self.propose({"plugin": "changelog", "subagents": [role]})).stdout
        self.assertIn(
            "  step 2  run: Run only `git log --oneline`.  type run_only\n"
            "  step 3  run: Run only `ls`.                 type run_only\n",
            out,
        )

    def test_the_step_numbers_line_up_in_one_column(self) -> None:
        text = self.read("changelog", "agents", "writer.md") + "".join(
            f"{n}. Go on.\n" for n in range(5, 11)
        )
        self.write(text, "changelog", "agents", "writer.md")
        role = run_only("writer", (2, ["git log --oneline"]), (10, ["git log --oneline"]))
        out = self.lay("print", self.propose({"plugin": "changelog", "subagents": [role]})).stdout
        self.assertIn(
            "  step 2   run: Run only `git log --oneline`.  type run_only\n"
            "  step 10  run: Run only `git log --oneline`.  type run_only\n",
            out,
        )

    def test_each_subagent_is_shown_after_a_blank_line(self) -> None:
        proposal = {
            "plugin": "changelog",
            "subagents": [
                WRITER_RUN_ONLY["subagents"][0],
                run_only("reviewer", (1, ["git log --oneline"])),
            ],
        }
        out = self.lay("print", self.propose(proposal)).stdout
        self.assertIn(WRITER_SHOWN + "\nLanes of reviewer, each checked only in reviewer:\n", out)

    def test_a_rule_laid_before_shows_in_its_new_words(self) -> None:
        self.lay("write", self.propose(WRITER_RUN_ONLY))
        role = run_only("writer", (2, ["git log"]))
        out = self.lay("print", self.propose({"plugin": "changelog", "subagents": [role]})).stdout
        self.assertIn(
            "2. Read the commits since then with `git log --oneline`. Run only `git log`.\n", out
        )


class Refuses(RepositoryTest):
    def test_a_proposal_that_cant_stand_is_refused(self) -> None:
        lane = {"lane": "run_only", "takes": ["git diff"]}
        proposal = {
            "plugin": "changelog",
            "subagents": [{"name": "writer", "steps": [{"step": 9, "lanes": [lane]}]}],
        }
        path = self.propose(proposal)
        ran = self.lay("print", path)
        self.assertEqual(
            (ran.returncode, ran.stdout, ran.stderr),
            (1, "", f"lay.py: {path}: agents/writer.md: no step 9\n"),
        )

    def test_a_proposal_that_isnt_json_is_refused(self) -> None:
        ran = self.lay("print", self.propose("{"))
        self.assertEqual(ran.returncode, 1)
        self.assertIn("isn't JSON", ran.stderr)


class Usage(RepositoryTest):
    def test_print_with_no_proposal_shows_the_usage(self) -> None:
        ran = self.lay("print")
        self.assertEqual((ran.returncode, ran.stdout), (2, ""))
