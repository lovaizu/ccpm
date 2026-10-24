"""rn's lanes: what hooks/hooks.json lays on each agent is what its steps say, read by lane's own
code, which rn takes through a link."""

from __future__ import annotations

import os
import sys
import unittest

RN = os.path.normpath(
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "rn")
)
sys.path.insert(0, os.path.join(RN, "..", "dev", "lane"))

import testing

lanes, step = testing.lane_code(RN, "lanes", "step")

# The lanes each agent's steps call for, as the architecture gives them: its values as the prompt
# `rn.py records` prints gives them.
LAID = {"rn:learner": {"read_only", "read_whole", "write_only", "in_form", "end_when"}}


class TestLanes(unittest.TestCase):
    def test_each_agent_has_the_lanes_its_steps_call_for(self):
        # Given: rn's hooks
        # When: the lanes on each agent are read
        # Then: each agent has the lanes the architecture lays on it
        on: dict[str, set[str]] = {}
        for agent, _, lane, _ in testing.laid(RN):
            on.setdefault(agent, set()).add(lane)
        self.assertEqual(on, LAID)

    def test_each_step_says_the_sentence_of_each_lane_laid_on_it(self):
        # Given: rn's hooks and agents
        # When: each lane's step is read
        # Then: it says the lane's sentence word for word
        for agent, number, lane, takes in testing.laid(RN):
            with self.subTest(agent=agent, lane=lane):
                name = agent.partition(":")[2]
                said = lanes.sentence(lane, takes)
                self.assertTrue(step.holds(RN, name, number, said), said)
