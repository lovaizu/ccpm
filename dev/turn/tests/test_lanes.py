"""turn's lanes: what hooks/lanes.json lays on each agent is what its steps say, read by lane's own
code, which turn takes through a link."""

import unittest

from helpers import TURN, testing

lanes, step, hooks_file = testing.lane_code(TURN, "lanes", "step", "hooks_file")

# The lanes each agent's steps call for, taking its run's values as the flow gives them in the
# agent's prompt, or as turn.py start prints them.
LAID = {
    "turn:up": {"start_with", "follow_next", "hands_off", "read_only", "read_whole", "as_printed"},
    "turn:generator": {
        "read_only",
        "read_whole",
        "write_only",
        "hands_off",
        "test_after",
        "in_form",
        "end_when",
    },
    "turn:first-user": {
        "read_only",
        "read_whole",
        "write_only",
        "hands_off",
        "in_form",
        "end_when",
        "every_item",
    },
    "turn:learner": {"read_only", "read_whole", "write_only", "in_form", "end_when"},
}


class TestLanes(unittest.TestCase):
    def test_each_agent_has_the_lanes_its_steps_call_for(self):
        # Given: turn's hooks
        # When: the lanes on each agent are read
        # Then: each agent has the lanes its steps call for
        on = {}
        for agent, _, lane, _ in testing.laid(TURN):
            on.setdefault(agent, set()).add(lane)
        self.assertEqual(on, LAID)

    def test_each_step_says_the_sentence_of_each_lane_laid_on_it(self):
        # Given: turn's hooks and agents
        # When: each lane's step is read
        # Then: it says the lane's sentence word for word
        for agent, number, lane, takes in testing.laid(TURN):
            with self.subTest(agent=agent, lane=lane):
                name = agent.partition(":")[2]
                said = lanes.sentence(lane, takes)
                self.assertTrue(step.holds(TURN, name, number, said), said)
