"""The flow as the layer lays it: printed as the README shows it, each subagent by its position,
its follow_flow lane on the orchestrator's step; written into hooks/lanes.json, with the hook
telling the orchestrator its first move as it starts and the hook keeping the report each `from`
subagent hands back; carried over by `up`; and a flow that cannot be laid refused before anything
is written."""

from __future__ import annotations

import json
import os
import unittest

import helpers
from flowing import (
    FLOW,
    FLOW_LANE,
    FOLLOW,
    LAID,
    LEAD,
    LEAD_LAID,
    SUMMARIZER,
    SUMMARIZER_LAID,
    FlowTest,
)
from laying import AGAIN, END_ENTRY, ENTRY, KEPT, LANES, PRINTED, PUSH

# What `print` shows of the README's flow, before the steps of the lanes.
FLOWN = f"""Flow of notes-lead, laid on its step 1:
  1. changelog-writer
  2. changelog-reviewer, back to 1 while it answers more
  then notes-lead ends
Lanes on step 1 of notes-lead, each hook acting in notes-lead alone:
  follow: {FOLLOW}  hook follow_flow

1. Start the subagents of the work. {FOLLOW}
"""
# What `write` says of the README's proposal before lane's code is put in.
WROTE = (
    "Wrote step 1 of notes-lead into agents/notes-lead.md.\n"
    "Wrote step 3 of changelog-writer into agents/writer.md.\n"
    "Wrote the hooks of notes-lead, changelog-writer and changelog-reviewer into"
    " hooks/hooks.json.\n"
    "Wrote the flow and the lanes laid into hooks/lanes.json.\n"
)


def entry_of(given: dict, agent: str, matcher: str | None = None) -> dict:
    """The entry given, of changelog-writer, as it is for the subagent named, matching what is
    given, or its own matcher."""
    text = json.dumps(given).replace("changelog-writer", agent)
    made = json.loads(text)
    return made if matcher is None else {**made, "matcher": matcher}


# The entries of notes-lead, whose follow_flow lane watches every tool and its end, and which is
# told its first move as it starts, the hook letting it start where Python is missing; and of
# changelog-reviewer, the `from` of the flow's back, whose SubagentHandback call is kept.
LEAD_TOOL = entry_of(ENTRY, "notes-lead", ".*")
LEAD_END = entry_of(END_ENTRY, "notes-lead")
LEAD_START = {
    "matcher": "notes:notes-lead",
    "hooks": [
        {
            "type": "command",
            "timeout": 10,
            "command": KEPT["PostToolUse"][0]["hooks"][0]["command"]
            .replace("posttooluse.py", "subagentstart.py")
            .replace("changelog-writer", "notes-lead"),
        }
    ],
}
REVIEWER_BACK = entry_of(KEPT["PostToolUse"][0], "changelog-reviewer", "SubagentHandback")
HOOKS = {
    "hooks": {
        "SubagentStart": [LEAD_START],
        "PreToolUse": [LEAD_TOOL, ENTRY],
        "SubagentStop": [LEAD_END],
        "PostToolUse": [
            entry_of(KEPT["PostToolUse"][0], "notes-lead"),
            KEPT["PostToolUse"][0],
            REVIEWER_BACK,
        ],
        "PostToolUseFailure": [
            entry_of(KEPT["PostToolUseFailure"][0], "notes-lead"),
            KEPT["PostToolUseFailure"][0],
        ],
    }
}


class TestPrint(FlowTest):
    def test_the_flow_is_printed_before_the_step_it_is_laid_on(self):
        # Given: the README's proposal, the flow laid on step 1 of notes-lead beside hands_off on
        # step 3 of changelog-writer
        # When: it is printed
        # Then: the flow is shown, then the orchestrator's step with its lane, then the writer's
        self.assertEqual(self.lay("print", self.proposal_file), (0, FLOWN + "\n" + PRINTED))

    def test_a_flow_alone_is_printed(self):
        again = {"from": 4, "to": 3, "while": "again"}
        for what, flow, shown in (
            (
                "with no back",
                {**FLOW, "back": []},
                "  1. changelog-writer\n  2. changelog-reviewer\n",
            ),
            (
                "with a subagent twice and two backs",
                {
                    **FLOW,
                    "order": [*FLOW["order"], "summarizer", "changelog-reviewer"],
                    "back": [*FLOW["back"], again],
                },
                (
                    "  1. changelog-writer\n"
                    "  2. changelog-reviewer, back to 1 while it answers more\n"
                    "  3. summarizer\n"
                    "  4. changelog-reviewer, back to 3 while it answers again\n"
                ),
            ),
        ):
            with self.subTest(what=what):
                # Given: a proposal of a flow alone
                second = helpers.STEPS.replace("name: changelog-writer", "name: summarizer")
                self.write(os.path.join(self.plugin, "agents", "summarizer.md"), second)
                self.flowed(flow)
                # When: it is printed
                # Then: the flow is shown, its order, then each back on a line, then the
                # orchestrator's step
                expected = FLOWN.replace(FLOWN.split("\n", 1)[1].split("  then")[0], shown)
                self.assertEqual(self.lay("print", self.proposal_file), (0, expected))

    def test_the_flow_is_printed_before_its_step_alone(self):
        # Given: the flow beside hands_off on step 2 of notes-lead, given first
        push = {"lane": "hands_off", "takes": ["git push"]}
        lead = {"name": "notes-lead", "steps": [{"step": 2, "lanes": [push]}]}
        self.flowed(FLOW, subagents=[lead])
        # When: it is printed
        # Then: step 2 is shown with its lane, then the flow before step 1
        step_2 = (
            "Lanes on step 2 of notes-lead, each hook acting in notes-lead alone:\n"
            "  run: Do not run `git push`.  hook hands_off\n"
            "\n"
            "2. Reply with the reviewed entries. Do not run `git push`.\n"
        )
        self.assertEqual(self.lay("print", self.proposal_file), (0, step_2 + "\n" + FLOWN))


class TestWrite(FlowTest):
    def test_the_flow_is_written_with_the_lanes(self):
        # Given: the README's proposal
        # When: it is written
        said = self.written()
        # Then: notes-lead's step 1 says the flow's sentence, the flow and the lanes are in
        # hooks/lanes.json, each subagent has its hooks, and what was written
        # is said
        self.assertEqual(self.read(self.lead), LEAD_LAID)
        self.assertEqual(self.read(self.agent_file), helpers.LAID)
        self.assertEqual(self.laid(), LAID)
        self.assertEqual(self.hooks(), HOOKS)
        self.assertTrue(said.startswith(WROTE + "Put lane's code in hooks/lane/.\n"), said)

    def test_written_again_the_orchestrators_file_is_as_written_the_first_time(self):
        # Given: the README's proposal written
        self.written()
        # When: the same flow is written again
        self.flowed(FLOW)
        said = self.written()
        # Then: notes-lead's file is as written the first time
        self.assertEqual(self.read(self.lead), LEAD_LAID)
        self.assertIn("Wrote step 1 of notes-lead into agents/notes-lead.md.\n", said)
        self.assertEqual(self.laid(), {"flow": FLOW, "subagents": [*LAID["subagents"]]})

    def test_a_flow_alone_keeps_the_lanes_laid_before(self):
        # Given: hands_off laid before in changelog-writer
        self.propose(self.proposal())
        self.written()
        # When: a proposal of the flow alone is written
        self.flowed(FLOW)
        said = self.written()
        # Then: the writer's lanes are kept, after the flow's, and notes-lead alone is written
        self.assertEqual(
            self.laid(), {"flow": FLOW, "subagents": [LAID["subagents"][1], LAID["subagents"][0]]}
        )
        self.assertTrue(
            said.startswith(
                "Wrote step 1 of notes-lead into agents/notes-lead.md.\n"
                "Wrote the hooks of notes-lead and changelog-reviewer into hooks/hooks.json.\n"
            ),
            said,
        )

    def test_the_orchestrator_in_the_proposal_has_its_lanes_and_the_flows(self):
        push = {"lane": "hands_off", "takes": ["git push"]}
        for what, steps, laid in (
            (
                "on the flow's step",
                [{"step": 1, "lanes": [push]}],
                [{"step": 1, "lanes": [push, FLOW_LANE]}],
            ),
            (
                "on another step",
                [{"step": 2, "lanes": [push]}],
                [{"step": 2, "lanes": [push]}, {"step": 1, "lanes": [FLOW_LANE]}],
            ),
        ):
            with self.subTest(what=what):
                # Given: notes-lead in the proposal with a lane of its own, beside the flow,
                # between summarizer, named after it in order, and changelog-writer, named before
                self.write(self.lead, LEAD)
                self.write(self.agent_file, helpers.STEPS)
                self.write(self.summarizer, SUMMARIZER)
                writer = {"name": "changelog-writer", "steps": [{"step": 3, "lanes": LANES}]}
                summarizer = {"name": "summarizer", "steps": [{"step": 3, "lanes": LANES}]}
                lead = {"name": "notes-lead", "steps": steps}
                self.flowed(FLOW, subagents=[summarizer, lead, writer])
                # When: it is written
                self.written()
                # Then: notes-lead's lanes are its own and the flow's, in its place
                self.assertEqual(
                    self.laid()["subagents"],
                    [summarizer, {"name": "notes-lead", "steps": laid}, writer],
                )
                self.assertIn(FOLLOW, self.read(self.lead))
                self.assertIn("Do not run `git push`.", self.read(self.lead))
                self.assertEqual(self.read(self.agent_file), helpers.LAID)
                self.assertEqual(self.read(self.summarizer), SUMMARIZER_LAID)

    def test_the_orchestrator_given_without_a_flow_keeps_the_flow_laid_before(self):
        # Given: the README's proposal written
        self.written()
        # When: a proposal of notes-lead's lanes alone is written, the flow not given
        push = {"lane": "hands_off", "takes": ["git push"]}
        self.propose(self.proposal([push], "notes-lead", 2))
        said = self.lay("print", self.proposal_file)[1]
        self.written()
        # Then: the flow is kept, its lane on notes-lead beside the lane given, printed so
        self.assertEqual(self.laid()["flow"], FLOW)
        lead = self.laid()["subagents"][0]
        self.assertEqual(
            lead,
            {
                "name": "notes-lead",
                "steps": [{"step": 2, "lanes": [push]}, {"step": 1, "lanes": [FLOW_LANE]}],
            },
        )
        self.assertNotIn("Flow of", said)
        self.assertIn(f"  follow: {FOLLOW}  hook follow_flow\n", said)
        self.assertEqual(self.read(self.lead).count(FOLLOW), 1)
        self.assertEqual(self.hooks()["hooks"]["PostToolUse"][-1], REVIEWER_BACK)

    def test_the_flow_moved_to_another_step_is_taken_out_of_the_first(self):
        # Given: the README's proposal written
        self.written()
        # When: the flow is written laid on step 2
        self.flowed({**FLOW, "step": 2})
        self.written()
        # Then: step 1 no longer says its sentence, and step 2 does
        lead = self.read(self.lead)
        self.assertIn("1. Start the subagents of the work.\n", lead)
        self.assertIn(f"2. Reply with the reviewed entries. {FOLLOW}\n", lead)
        self.assertEqual(
            self.laid()["subagents"][0],
            {"name": "notes-lead", "steps": [{"step": 2, "lanes": [FLOW_LANE]}]},
        )

    def test_a_from_no_longer_a_from_has_its_hooks_taken_out(self):
        # Given: the README's proposal written, changelog-reviewer the from of its back
        self.written()
        # When: the flow is written with no back
        self.flowed({**FLOW, "back": []})
        said = self.written()
        # Then: changelog-reviewer has no hooks, and is not said
        commands = json.dumps(self.hooks())
        self.assertNotIn("notes:changelog-reviewer", commands)
        self.assertIn("Wrote the hooks of notes-lead into hooks/hooks.json.\n", said)

    def test_an_orchestrator_with_a_part_has_the_step_in_its_part(self):
        # Given: notes-lead's file an entry naming its part, prompts/lead.md
        part = os.path.join(self.plugin, "prompts", "lead.md")
        first = "Read `${CLAUDE_PLUGIN_ROOT}/prompts/lead.md` whole first, and take its steps."
        entry = f"---\nname: notes-lead\n---\n\n{first}\n"
        self.write(self.lead, entry)
        self.write(part, LEAD.split("---\n", 2)[2])
        self.flowed(FLOW)
        # When: the flow is written
        said = self.written()
        # Then: the part's step says the sentence, the entry is as it was, and the part is said
        self.assertEqual(self.read(self.lead), entry)
        self.assertIn(f"1. Start the subagents of the work. {FOLLOW}\n", self.read(part))
        self.assertTrue(said.startswith("Wrote step 1 of notes-lead into prompts/lead.md.\n"), said)

    def test_a_proposal_of_other_subagents_keeps_the_flow_laid_before(self):
        # Given: the README's proposal written
        self.written()
        lead = self.read(self.lead)
        # When: a proposal of changelog-writer's lanes alone is printed and written
        self.propose(self.proposal(PUSH))
        said = self.lay("print", self.proposal_file)[1]
        wrote = self.written()
        # Then: the flow and notes-lead's lanes are kept, and neither is printed or written
        self.assertEqual(self.laid()["flow"], FLOW)
        self.assertEqual(self.laid()["subagents"][0], LAID["subagents"][0])
        self.assertNotIn("notes-lead", said)
        self.assertEqual(self.read(self.lead), lead)
        self.assertIn("Wrote the hooks of changelog-writer and changelog-reviewer", wrote)
        self.assertEqual(self.hooks()["hooks"]["SubagentStop"], [LEAD_END])
        self.assertEqual(self.hooks()["hooks"]["SubagentStart"], [LEAD_START])

    def test_a_flow_given_alone_keeps_the_orchestrators_other_lanes(self):
        # Given: notes-lead laid with hands_off on step 2 beside the flow, after summarizer, named
        # after it in order
        push = {"lane": "hands_off", "takes": ["git push"]}
        self.write(self.summarizer, SUMMARIZER)
        summarizer = {"name": "summarizer", "steps": [{"step": 3, "lanes": LANES}]}
        lead = {"name": "notes-lead", "steps": [{"step": 2, "lanes": [push]}]}
        self.flowed(FLOW, subagents=[summarizer, lead])
        self.written()
        # When: the flow is written alone
        self.flowed(FLOW)
        self.written()
        # Then: notes-lead keeps hands_off on step 2, and the flow's lane on step 1
        self.assertEqual(
            self.laid()["subagents"][1],
            {
                "name": "notes-lead",
                "steps": [{"step": 2, "lanes": [push]}, {"step": 1, "lanes": [FLOW_LANE]}],
            },
        )
        self.assertIn(
            "2. Reply with the reviewed entries. Do not run `git push`.", self.read(self.lead)
        )

    def test_a_from_gone_from_agents_has_its_hooks_taken_out(self):
        # Given: the README's proposal written, then changelog-reviewer's file taken out
        self.written()
        os.remove(self.reviewer)
        # When: the flow is written with changelog-writer alone in its order
        self.flowed({**FLOW, "order": ["changelog-writer"], "back": []})
        said = self.written()
        # Then: changelog-reviewer's hooks are taken out, and that is said
        self.assertNotIn("notes:changelog-reviewer", json.dumps(self.hooks()))
        self.assertIn(
            "Took out the hooks of changelog-reviewer, which agents/ no longer has.", said
        )


class TestUp(FlowTest):
    def test_up_carries_the_flow_over_and_does_not_say_its_lane(self):
        # Given: the README's proposal written, then left with an older copy of lane's code and
        # hooks in an older form
        self.written()
        laid = self.laid()
        self.write(os.path.join(self.plugin, "hooks", "lane", "VERSION"), "0.0.1\n")
        older = 'python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/subagentstart.py" notes:notes-lead'
        hooks = {"hooks": {"SubagentStart": [{"matcher": "x", "hooks": [{"command": older}]}]}}
        self.write_json(os.path.join(self.plugin, "hooks", "hooks.json"), hooks)
        # When: it is brought up
        code, said = self.lay("up", self.plugin)
        # Then: the flow and the lanes are as they were, each subagent's hooks as written, and
        # the lane of the flow is not said as one laid before
        self.assertEqual(code, 0, said)
        self.assertEqual(self.laid(), laid)
        self.assertEqual(self.hooks(), HOOKS)
        self.assertNotIn("follow_flow", said)
        self.assertIn("Laid before on step 3 of changelog-writer:", said)

    def test_up_says_each_lane_of_the_orchestrator_but_the_flows(self):
        # Given: the README's proposal written, then notes-lead given hands_off after the flow's
        # lane on step 1 in hooks/lanes.json
        self.written()
        laid = self.laid()
        push = {"lane": "hands_off", "takes": ["git push"]}
        laid["subagents"][0]["steps"][0]["lanes"].append(push)
        self.write_json(os.path.join(self.plugin, "hooks", "lanes.json"), laid)
        # When: it is brought up
        said = self.lay("up", self.plugin)[1]
        # Then: hands_off is said, laid before, and the flow's lane is not
        self.assertIn("Laid before on step 1 of notes-lead, whose step no longer says", said)
        self.assertIn(json.dumps(push), said)
        self.assertNotIn("follow_flow", said)


class TestRefused(FlowTest):
    def stops(self, named: str) -> None:
        """Checks that the proposal, printed or written, exits 1 naming what is wrong, with nothing
        written."""
        for action in ("print", "write"):
            code, said = self.lay(action, self.proposal_file)
            self.assertEqual(code, 1, said)
            self.assertIn(named, said)
            self.assertTrue(said.endswith(f"; {AGAIN}.\n"), said)
        self.assertEqual(self.read(self.lead), LEAD)
        self.assertFalse(os.path.exists(os.path.join(self.plugin, "hooks", "lanes.json")))

    def test_a_flow_that_cannot_be_laid_stops(self):
        back = FLOW["back"][0]
        for what, flow, named in (
            ("out of its schema", {**FLOW, "step": 0}, "$.flow.step: expected a number"),
            (
                "the orchestrator in its order",
                {**FLOW, "order": ["notes-lead"], "back": []},
                "gives a flow whose order names its orchestrator notes-lead",
            ),
            (
                "a to after its from",
                {**FLOW, "back": [{**back, "to": 2}]},
                "gives a flow whose back from position 2 goes to position 2",
            ),
            (
                "an orchestrator not in the plugin",
                {**FLOW, "orchestrator": "lead"},
                "gives a flow naming lead, which no file in agents/ names",
            ),
            (
                "a subagent of its order not in the plugin",
                {**FLOW, "order": ["changelog-writer", "x"], "back": []},
                "gives a flow naming x, which no file in agents/ names",
            ),
            (
                "a name a hook cannot carry",
                {**FLOW, "order": ["changelog writer"], "back": []},
                "gives a flow naming changelog writer, which no file in agents/ names",
            ),
            (
                "a step the orchestrator has not",
                {**FLOW, "step": 9},
                "gives step 9, which the Steps of notes-lead do not have",
            ),
        ):
            with self.subTest(what=what):
                # Given: a proposal of a flow that cannot be laid
                self.flowed(flow)
                # When: it is printed or written
                # Then: it exits 1 naming what is wrong, nothing written
                self.stops(named)

    def test_a_proposal_of_no_subagents_and_no_flow_stops(self):
        # Given: a proposal of the plugin alone
        self.propose({"plugin": self.plugin})
        # When: it is printed or written
        # Then: it exits 1 saying it holds neither
        self.stops("$: expected a value of one of its anyOf choices")

    def test_a_proposal_laying_the_flows_lane_itself_stops(self):
        # Given: a proposal laying follow_flow on changelog-writer, after another lane on its step
        lane = {"lane": "follow_flow", "takes": []}
        self.propose(self.proposal([PUSH[0], lane]))
        # When: it is printed or written
        # Then: it exits 1, as follow_flow is no lane the proposal names, lay.py laying it
        self.stops('$.subagents[0].steps[0].lanes[1].lane: expected one of "start_with"')

    def test_follow_next_of_any_script_is_laid(self):
        for what, lane in (
            ("of a script", {"lane": "follow_next", "takes": ["bin/next.py"]}),
            ("of a script named flow.py", {"lane": "follow_next", "takes": ["flow.py"]}),
        ):
            with self.subTest(what=what):
                # Given: a proposal laying the lane on changelog-writer
                self.propose(self.proposal([lane]))
                # When: it is printed
                # Then: it is printed
                code, said = self.lay("print", self.proposal_file)
                self.assertEqual(code, 0, said)

    def test_an_orchestrator_naming_its_tools_without_agent_stops(self):
        for tools in ("Bash, Read", "Bash, Agents", "AgentTool"):
            with self.subTest(tools=tools):
                # Given: notes-lead's file naming its tools, Agent not among them
                self.write(self.lead, LEAD.replace("tools: Agent, Bash", f"tools: {tools}"))
                # When: the flow is printed or written
                # Then: it exits 1 saying to add Agent, nothing written
                said = (
                    f"lay.py: {self.lead} names the tools of notes-lead, `{tools}`, without Agent,"
                    " with which it starts the subagents of the flow; add Agent to them, and run"
                    " again.\n"
                )
                for action in ("print", "write"):
                    self.assertEqual(self.lay(action, self.proposal_file), (1, said))
                self.assertFalse(os.path.exists(os.path.join(self.plugin, "hooks", "lanes.json")))

    def test_an_orchestrator_naming_agent_among_its_tools_or_no_tools_is_laid(self):
        for what, tools in (
            ("Agent first", "tools: Agent, Bash"),
            ("Agent last, unspaced", "tools: Bash,Agent"),
            ("Agent alone", "tools: Agent"),
            ("no tools named, so all of them", ""),
        ):
            with self.subTest(what=what):
                # Given: notes-lead's file naming Agent among its tools, or no tools
                self.write(self.lead, LEAD.replace("tools: Agent, Bash\n", tools and f"{tools}\n"))
                # When: the flow is printed
                # Then: it is printed
                code, said = self.lay("print", self.proposal_file)
                self.assertEqual(code, 0, said)


if __name__ == "__main__":
    unittest.main()
