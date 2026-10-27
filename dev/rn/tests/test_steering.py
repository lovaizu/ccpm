"""The tests of the steering's form, its plan in the form of rn's plan checklist's F-1, which a
steering is held to at every keep, and of how it is read."""

from __future__ import annotations

import unittest

from helpers import (
    CRITERIA,
    NEXT,
    PLAN_CHECKLIST,
    STEERED,
    VERSION,
    plan,
    steered,
    steering,
    task,
    template,
)

# An action of turn's of the fixture, and the same as one of the orchestrator's.
ORCHESTRATED = (
    "Make part 1 of T1, `src/t1-1.py` as a code work. turn.",
    "Settle part 1 of T1. The orchestrator, with the user.",
)


class FormTest(unittest.TestCase):
    """What a steering is held to at every keep: its front matter, its plan in the form of rn's plan
    checklist's F-1, headings, IDs and ticks, and Next and Open."""

    def assert_out(self, text: str, point: str) -> None:
        """Asserts the steering's text is out of its form by the point."""
        self.assertEqual(steering.out_of_form(text), point)

    def test_a_steering_in_form_holds(self):
        cases = {
            "the whole": STEERED,
            "the title alone": steered(part="# Add login"),
            "the goal alone": steered(part=plan(criteria="", tasks="")),
            "no goal": steered(part=plan(goal="", tasks="")),
            "a pull request not opened": steered(pr="none"),
            "points open": steered(opened="- One.\n  Still open.\n- Two."),
            "ticks": steered(part=plan(tasks=task(ticks="xxx "))),
            "a task serving the goal": steered(part=plan(tasks=task(serves="G1"))),
            "a task serving two": steered(part=plan(tasks=task(serves="AC1 and AC2"))),
            "a task serving three": steered(part=plan(tasks=task(serves="G1, AC1 and AC2"))),
            "a task serving three, a comma before and": steered(
                part=plan(tasks=task(serves="G1, AC1, and AC2"))
            ),
            "a task's line over two lines": steered(
                part=plan(tasks=task().replace("T1. Serves", "T1.\n  Serves"))
            ),
            "two tasks": steered(part=plan(tasks=f"{task()}\n\n{task('T2', ticks='x ')}")),
            "an action over two lines": steered(
                part=plan(tasks=task().replace("Make part 1 of T1,", "Make part 1\n    of T1,"))
            ),
            "a completion criterion over two lines": steered(
                part=plan(tasks=task().replace("serves, tried", "serves,\n    tried"))
            ),
            "a later action over two lines": steered(
                part=plan(tasks=task().replace("Make part 3 of T1,", "Make part 3\n    of T1,"))
            ),
            "an action of the orchestrator's": steered(
                part=plan(tasks=task().replace(ORCHESTRATED[0], ORCHESTRATED[1]))
            ),
            "a command that checks the result": steered(
                part=plan(tasks=task(test="sh dev/check.sh"))
            ),
            "a kind after an": steered(
                part=plan(tasks=task().replace("as a code work", "as an architecture work"))
            ),
        }
        for name, text in cases.items():
            with self.subTest(name=name):
                # Given: a steering in the form of F-1.
                # When: it is held to its form.
                # Then: it holds.
                self.assert_out(text, "")

    def test_a_front_matter_with_a_comment_holds(self):
        # Given: a steering whose front matter holds a comment, as lane reads it, so its body opens
        # a line later.
        text = STEERED.replace(f"rn: {VERSION}\n", f"rn: {VERSION}\n# kept by rn\n")
        # When: it is held to its form.
        # Then: it holds.
        self.assert_out(text, "")

    def test_each_criterion_is_read_whole(self):
        # Given: a steering whose first criterion runs on to a second line.
        text = steered(part=plan(criteria="- AC1: Sign in\n  by email.\n- AC2: Sign out."))
        # When: its criteria are read.
        # Then: each is given back whole, as one line.
        want = {"AC1": "Sign in by email.", "AC2": "Sign out."}
        found = steering.decided(text.splitlines())
        self.assertEqual({k: v for k, v in found.items() if k != "G1"}, want)

    def test_a_steering_rn_writes_holds_rns_plan_checklists_template(self):
        # Given: a steering rn writes with every part, a task's action ticked, and rn's plan
        # checklist's F-1 template, the first fence under it.
        with open(PLAN_CHECKLIST, encoding="utf-8") as f:
            lines = f.read().splitlines()
        heading = lines.index("### F-1: Shape")
        fences = [n for n in range(heading, len(lines)) if lines[n].startswith("```")]
        asked = template.read("\n".join(lines[fences[0] + 1 : fences[1]]))
        # When: it is held to the template.
        # Then: it holds.
        text = steered(part=plan(tasks=task(ticks="x   ")))
        self.assertEqual(template.held(asked, text), "")

    def test_a_front_matter_out_of_form_is_named(self):
        cases = {
            "x\n": "line 1: expected the front matter opened by `---`, found none",
            "---\nrn: 1\n": 'line 1: expected frontmatter closed by "---", found none',
            STEERED.replace("stage: goal\n", ""): "expected the front matter's keys rn, pr,"
            " stage, signoff, artifact-language, conversation-language in that order, found rn,"
            " pr, signoff, artifact-language, conversation-language",
            STEERED.replace(f"rn: {VERSION}\npr: ", "pr: ").replace("stage:", "rn: 1\nstage:"): (
                "expected the front matter's keys rn, pr, stage, signoff, artifact-language,"
                " conversation-language in that order, found pr, rn, stage, signoff,"
                " artifact-language, conversation-language"
            ),
            STEERED.replace("Japanese\n", "Japanese\nstatus: x\n"): "expected the front matter's"
            " keys rn, pr, stage, signoff, artifact-language, conversation-language in that order,"
            " found rn, pr, stage, signoff, artifact-language, conversation-language, status",
            "---\n---\n# A\n": "expected the front matter's keys rn, pr, stage, signoff,"
            " artifact-language, conversation-language in that order, found none",
            STEERED.replace(f"rn: {VERSION}", "rn:"): "line 2: expected a value for rn, found none",
            steered(stage="done"): "line 4: expected stage to be goal, ux, architecture, build,"
            " deliverable, learnings or finished, found done",
            steered(signoff="build"): "line 5: expected signoff to be none, goal, ux, architecture"
            " or deliverable, found build",
            steered(pr="https://github.com/o/r"): "line 3: expected pr to be the pull"
            " request's URL, or none before it is opened, found https://github.com/o/r",
            steered(pr="pending"): "line 3: expected pr to be the pull request's URL, or none"
            " before it is opened, found pending",
        }
        for text, point in cases.items():
            with self.subTest(point=point):
                # Given: a steering whose front matter is out of its form.
                # When: it is held to its form.
                # Then: the point is named.
                self.assert_out(text, point)

    def test_headings_out_of_form_are_named(self):
        only = (
            "expected only the headings `## Acceptance criteria`, `## Tasks`, `## Next` and"
            " `## Open`, each once and in that order, found"
        )
        cases = {
            STEERED.replace("# Add login\n", ""): "expected the title as `# <the piece of work, in"
            " a few words>` first, found `G1: Users sign in,`",
            STEERED.replace("# Add login", "Words.\n\n# Add login"): "expected the title as"
            " `# <the piece of work, in a few words>` first, found `Words.`",
            STEERED.split("# Add login")[0]: "expected the title as `# <the piece of work, in a"
            " few words>` first, found none",
            STEERED.replace(
                "# Add login\n", "# Add login\n# Login\n"
            ): f"line 11: {only} `# Login`",
            STEERED.replace("## Tasks", "## Notes"): f"line 21: {only} `## Notes`",
            STEERED.replace("## Tasks", "### Tasks"): f"line 21: {only} `### Tasks`",
            STEERED.replace("## Tasks", "# Tasks"): f"line 21: {only} `# Tasks`",
            STEERED.replace("## Next", "## Tasks\n\n## Next"): f"line 32: {only} `## Tasks`",
            STEERED.replace("## Acceptance criteria", "## Next"): f"line 15: {only} `## Next`",
            STEERED.replace("## Next", "## Learnings\n\n- L1: x\n\n## Next"): (
                f"line 32: {only} `## Learnings`"
            ),
            STEERED.replace("## Next\n\n", ""): "expected the heading `## Next`, found none",
            STEERED.replace("## Open\n\n", ""): "expected the heading `## Open`, found none",
        }
        for text, point in cases.items():
            with self.subTest(point=point):
                # Given: a steering whose headings are out of their form.
                # When: it is held to its form.
                # Then: the point is named.
                self.assert_out(text, point)

    def test_ids_and_lists_out_of_form_are_named(self):
        criterion = (
            "an acceptance criterion as `- AC<n>: <one thing the finished work must do for the"
            " goal>`"
        )
        cases = {
            STEERED.replace("G1: ", "Goal: "): "line 12: expected the goal as `G1: <the user's"
            " purpose, with why they want it>`, one paragraph under the title, found `Goal: Users"
            " sign in,`",
            STEERED.replace("theirs.", "theirs.\n\nMore."): "line 12: expected the goal as `G1:"
            " <the user's purpose, with why they want it>`, one paragraph under the title, found"
            " `G1: Users sign in,`",
            STEERED.replace("- AC2", "- AC 2"): f"line 18: expected {criterion}, found `- AC 2:"
            " A signed-in user sees only their cart,`",
            STEERED.replace("- AC2", "- AC1"): "line 18: expected each ID once, found AC1 again",
            STEERED.replace("  on every", "on every"): f"line 19: expected {criterion}, or a"
            " line indented under one, found `on every page.`",
            STEERED.replace(CRITERIA, "Words."): f"line 17: expected {criterion}, or a line"
            " indented under one, found `Words.`",
            steered(part=plan(criteria="None.", tasks="")).replace("None.", ""): (
                f"expected {criterion} under `## Acceptance criteria`, found none"
            ),
            STEERED.replace(NEXT, ""): "expected the step of /rn:up to take next under `## Next`,"
            " found none",
            STEERED.replace("None.", ""): "expected `None.`, or each point open as `- <what is"
            " open>`, under `## Open`, found none",
            STEERED.replace("None.", "Nothing."): "line 38: expected each point open as `- <what"
            " is open>`, or a line indented under one, found `Nothing.`",
            STEERED.replace("None.", "None.\n- One."): "line 38: expected each point open as"
            " `- <what is open>`, or a line indented under one, found `None.`",
            STEERED.replace("None.", "- One.\n- One."): "line 39: expected each ID once, found"
            " One. again",
        }
        for text, point in cases.items():
            with self.subTest(point=point):
                # Given: a steering whose IDs or lists are out of their form.
                # When: it is held to its form.
                # Then: the point is named.
                self.assert_out(text, point)

    def test_tasks_out_of_form_are_named(self):
        actions = (
            "in one of the forms of rn's plan checklist's F-1, `  - [ ] {0}. <what is found out"
            " or settled>. The orchestrator, with the user.` or `  - [ ] {0}. <what is made, from"
            " which works before it>, `<its path>` as a <kind> work. turn.`"
        )
        line = "  - [ ] {0}. Make part {1} of T1, `src/t1-{1}.py` as a code work. turn."
        form = "a task as `- T<n>: <the result it makes>. Serves <G1, or the criteria by ID>.`"
        cases = {
            task().replace("- T1", "- Task 1"): f"line 23: expected {form}, found `- Task 1: Make"
            " the part T1. Serves AC1.`",
            task().replace("- T1", "- [ ] T1"): f"line 23: expected {form}, found `- [ ] T1: Make"
            " the part T1. Serves AC1.`",
            task().replace(" Serves AC1.", ""): "line 23: expected T1 to end `Serves <G1, or the"
            " criteria by ID>.`, found `- T1: Make the part T1.`",
            task(serves="AC1 or AC2"): "line 23: expected T1 to end `Serves <G1, or the criteria"
            " by ID>.`, found `- T1: Make the part T1. Serves AC1 or AC2.`",
            task(
                serves="AC3 and AC4"
            ): "line 23: expected T1 to serve only the goal and the criteria the"
            " steering holds, found AC3",
            task().replace("  Completion", "  The completion"): "line 23: expected `  Completion"
            " criterion: <what its result must do for what it serves, and the check that shows"
            " it>` under T1, found none",
            task(ticks=""): "line 23: expected the actions of T1, found none",
            task().replace("[ ] 1.", "[ ] 2.", 1): f"line 27: expected action 1 of T1"
            f" {actions.format(1)}, found `{line.format(2, 1)}`",
            task().replace("[ ] 2.", "[ ] 1.", 1): f"line 28: expected action 2 of T1"
            f" {actions.format(2)}, found `{line.format(1, 2)}`",
            task().replace("[ ] 3.", "[ ] three."): f"line 29: expected action 3 of T1"
            f" {actions.format(3)}, found `{line.format('three', 3)}`",
            task().replace(" as a code work. turn.", ". turn.", 1): f"line 27: expected action 1"
            f" of T1 {actions.format(1)}, found `  - [ ] 1. Make part 1 of T1, `src/t1-1.py`."
            " turn.`",
            task().replace("as a code work. turn.", "as a code work.", 1): f"line 27: expected"
            f" action 1 of T1 {actions.format(1)}, found `  - [ ] 1. Make part 1 of T1,"
            " `src/t1-1.py` as a code work.`",
            task(test="sh dev/check.sh").replace("`sh dev/check.sh`", "sh dev/check.sh"): (
                "line 27: expected the one command that runs T1's check as `  Test: `<the"
                " command>``, found `  Test: sh dev/check.sh`"
            ),
            task(test="a").replace("  Test: `a`", "  Test: `a`\n\n  Test: `b`"): (
                "line 29: expected the one command that runs T1's check once, found `  Test: `b``"
            ),
            task().replace("Make part 1 of T1, ", "Make part 1 of T1,\n\n    "): f"line 27:"
            f" expected action 1 of T1 {actions.format(1)}, found `  - [ ] 1. Make part 1 of"
            " T1,`",
            task(ticks="xxxx"): "line 23: expected only tasks with an action not ticked, as a"
            " task leaves the steering once all its actions are, found T1 with every action"
            " ticked",
        }
        for tasks, point in cases.items():
            with self.subTest(point=point):
                # Given: a steering whose task is out of its form.
                # When: it is held to its form.
                # Then: the point is named.
                self.assert_out(steered(part=plan(tasks=tasks)), point)

    def test_a_task_serving_the_goal_with_no_goal_is_named(self):
        # Given: a steering with no goal, whose task serves G1.
        text = steered(part=plan(goal="", tasks=task(serves="G1")))
        # When: it is held to its form.
        # Then: the goal is named as one the steering does not hold.
        self.assert_out(
            text,
            "line 20: expected T1 to serve only the goal and the criteria the steering holds,"
            " found G1",
        )


if __name__ == "__main__":
    unittest.main()
