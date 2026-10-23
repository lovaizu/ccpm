"""turn's lanes: what hooks/hooks.json lays on each agent is what its steps say, read by lane's own
code, which turn takes through a link."""

import importlib
import json
import os
import shlex
import sys
import unittest

from helpers import TURN


def lane_code():
    """lane's lanes and its reading of a step, imported from the link in turn's hooks: lane's code
    and turn's scripts share module names, such as call, so lane's are imported apart and turn's
    put back after."""
    shared = ("call", "forms")
    turns = {n: sys.modules.pop(n) for n in shared if n in sys.modules}
    sys.path.insert(0, os.path.join(TURN, "hooks", "lane"))
    try:
        return importlib.import_module("lanes"), importlib.import_module("step")
    finally:
        sys.path.pop(0)
        sys.modules.update(turns)


lanes, step = lane_code()

# The lanes each agent's steps call for, as the architecture gives them: its run's values as the flow
# gives them in the agent's prompt, or as turn.py start prints them.
LAID = {
    "turn:up": {"start_with", "follow_next", "hands_off", "as_printed"},
    "turn:generator": {"read_only", "read_whole", "write_only", "hands_off", "in_form", "end_when"},
    "turn:first-user": {
        "read_only",
        "read_whole",
        "write_only",
        "hands_off",
        "in_form",
        "end_when",
    },
    "turn:evaluator": {"read_only", "read_whole", "write_only", "hands_off", "in_form", "end_when"},
    "turn:learner": {"read_only", "read_whole", "write_only", "in_form", "end_when"},
}


def laid():
    """Each lane hooks/hooks.json lays, as (agent, step, lane, takes)."""
    with open(os.path.join(TURN, "hooks", "hooks.json"), encoding="utf-8") as f:
        hooks = json.load(f)["hooks"]
    found = []
    for entries in hooks.values():
        for entry in entries:
            words = shlex.split(entry["hooks"][0]["command"].rpartition("; exec ")[2])
            agent, *held = words[2:]
            for one in held:
                number, lane, takes = one.split(":", 2)
                found.append((agent, int(number), lane, takes.split(",")))
    return found


class TestLanes(unittest.TestCase):
    def test_each_agent_has_the_lanes_its_steps_call_for(self):
        # Given: turn's hooks
        # When: the lanes on each agent are read
        # Then: each agent has the lanes the architecture lays on it
        on = {}
        for agent, _, lane, _ in laid():
            on.setdefault(agent, set()).add(lane)
        self.assertEqual(on, LAID)

    def test_each_step_says_the_sentence_of_each_lane_laid_on_it(self):
        # Given: turn's hooks and agents
        # When: each lane's step is read
        # Then: it says the lane's sentence word for word
        for agent, number, lane, takes in laid():
            with self.subTest(agent=agent, lane=lane):
                name = agent.partition(":")[2]
                said = lanes.sentence(lane, takes)
                self.assertTrue(step.holds(TURN, name, number, said), said)
