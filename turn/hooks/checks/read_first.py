"""Keep the generator, the learner and the evaluator to reading, searching and listing until they have read whole
what they decide from. A command can change the deliverable without naming it, so what is held is every action
but reading, not a path; and checked only when it finishes, a read made after the work could not be told from one
that shaped it."""
from checks import read_whole

HELD = ("turn:generator", "turn:learner", "turn:evaluator")
READING = ("Read", "Grep", "Glob")


def check(data, t):
    if data.get("agent_type") not in HELD or data.get("tool_name") in READING:
        return []
    return read_whole.check(data, t)
