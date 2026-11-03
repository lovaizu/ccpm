"""turn's lanes: what hooks/lanes.json lays on each agent is what its steps say, read by lane's own
code, which turn takes through a link."""

import unittest

from helpers import TURN, testing

# Skipped until T41, so the tests CI runs show new failures while these stay in sight.
raise unittest.SkipTest(
    "lane's lanes, step and lanes_json, which these old tests read,"
    " moved to hooks/lane/core/domain/;"
    " they go when turn is rebuilt in T41 (.rn/20261013-rebuild/steering.md)"
)
lanes, step, lanes_json = testing.lane_code(TURN, "lanes", "step", "lanes_json")

# The lanes each agent's steps call for, taking its run's values as the agent's prompt gives them,
# or as the script it first runs prints them.
LAID = {
    "turn:up": {"start_with", "read_only", "hands_off", "as_printed"},
    "turn:generator": {
        "start_with",
        "read_only",
        "read_whole",
        "write_only",
        "hands_off",
        "test_after",
        "in_form",
        "end_when",
    },
    "turn:first-user": {
        "start_with",
        "read_only",
        "read_whole",
        "write_only",
        "hands_off",
        "test_after",
        "in_form",
        "end_when",
        "every_item",
    },
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
