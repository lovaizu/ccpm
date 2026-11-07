"""test_after: the subagent gives its result only with each change of an output its step names
passed: a test's command came back without an error after the change. A change is a Write or Edit
of the output, or of a file under it where it is a folder; a test passed is a Bash call of a test's
command, whole, each value it holds the run's own, kept as it came back, as a call that failed is
not kept."""

from __future__ import annotations

from lanes import run_only
from lanes.done import Done, under, written

ACTION = "test"
WORDING = "After changing `<output>`, pass `<test>`."
CALLS = True


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What is missing: that the last change of an output was not passed after, naming the output
    it was a change of; "" where none was made, or a test passed after the last."""
    outputs = [(named, done.full(named)) for named in given["output"]]
    last, changed = None, ""
    for at, c in enumerate(done.calls):
        for named, output in outputs:
            if any(under(f, output) for f in written(done, [c])):
                last, changed = at, named
    if last is None:
        return ""
    # The call at last is a write, which passes no test, so the calls after it begin with it or not
    # alike.
    for c in done.calls[last + 1 :]:  # pragma: no mutate
        command = str(c.get("input", {}).get("command", ""))
        tested = run_only.allows(command, given["test"], done.root, done.cwd, done.values)
        if c.get("tool") == "Bash" and tested:
            return ""
    return f"`{changed}` changed with no test passed after"
