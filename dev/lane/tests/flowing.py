"""What the tests of the flow stand on: the README's plugin `notes`, with its orchestrator
`notes-lead` and the reviewer `changelog-reviewer` beside changelog-writer, the README's flow of
them, and the proposal laying it."""

from __future__ import annotations

import os

from helpers import LAID as LAID_STEPS
from helpers import STEPS
from laying import LANES, LayTest

# The orchestrator's file before the flow is laid, its step 1 the README's.
LEAD = """---
name: notes-lead
description: Leads the work on a project's changelog.
tools: Agent, Bash
---

## Role

You lead the work.

## Steps

1. Start the subagents of the work.
2. Reply with the reviewed entries.
"""
# The line the layer writes into the orchestrator's file, saying where flow.py lies.
LIES = '`flow.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/flow.py"`.'
# The sentence of the flow's lane.
FOLLOW = "Take each move `flow.py` prints, until it prints none."
# The orchestrator's file as the layer writes it with the flow laid on step 1.
LEAD_LAID = LEAD.replace("---\n\n## Role", f"---\n\n{LIES}\n\n## Role").replace(
    "work.\n2.", f"work. {FOLLOW}\n2."
)
# The reviewer's file, whose answer of `more` sends the work back to the writer.
REVIEWER = """---
name: changelog-reviewer
description: Reviews the new entries of a project's changelog.
tools: Read, Bash
---

## Steps

1. Read the new entries against the commits.
2. End with `more` on a line of its own when an entry needs the writer again.
"""
# A subagent named after notes-lead in order, its steps changelog-writer's, before and after
# hands_off is laid on step 3.
SUMMARIZER = STEPS.replace("name: changelog-writer", "name: summarizer")
SUMMARIZER_LAID = LAID_STEPS.replace("name: changelog-writer", "name: summarizer")
# The README's flow.
FLOW = {
    "orchestrator": "notes-lead",
    "step": 1,
    "order": ["changelog-writer", "changelog-reviewer"],
    "back": [{"from": "changelog-reviewer", "to": "changelog-writer", "while": "more"}],
}
# The lane the flow is laid as, on the orchestrator's step.
FLOW_LANE = {"lane": "follow_next", "takes": ["flow.py"]}
# The lanes laid of the README's proposal, as hooks/lanes.json holds them.
LAID = {
    "flow": FLOW,
    "subagents": [
        {"name": "notes-lead", "steps": [{"step": 1, "lanes": [FLOW_LANE]}]},
        {"name": "changelog-writer", "steps": [{"step": 3, "lanes": LANES}]},
    ],
}


class FlowTest(LayTest):
    """A test of the layer on the plugin `notes` with notes-lead and changelog-reviewer beside
    changelog-writer, the proposal the README's flow with hands_off on step 3 of the writer."""

    def setUp(self) -> None:
        super().setUp()
        self.lead = os.path.join(self.plugin, "agents", "notes-lead.md")
        self.reviewer = os.path.join(self.plugin, "agents", "changelog-reviewer.md")
        self.summarizer = os.path.join(self.plugin, "agents", "summarizer.md")
        self.write(self.lead, LEAD)
        self.write(self.reviewer, REVIEWER)
        self.propose({**self.proposal(), "flow": FLOW})

    def flowed(self, flow: dict, **given: object) -> None:
        """Writes the proposal of the flow, with the keys given beside it, and the plugin's."""
        self.propose({"plugin": self.plugin, "flow": flow, **given})

    def written(self) -> str:
        """What `lay.py write` of the proposal says; it exits 0."""
        code, said = self.lay("write", self.proposal_file)
        self.assertEqual(code, 0, said)
        return said
