"""read_whole: the subagent gives its result only once it has read each input its step names to its
end: its Read calls, by their offset and limit, have covered every line of it, a Read naming no
limit covering as many lines as the Read tool gives by default."""

from __future__ import annotations

from done import Done, lines_read, text

from lanes.write_only import in_plugin

ACTION = "read"
WORDING = "Read `<input>` to its end."
CALLS = True


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What is missing: each input not there, or with a line no Read covered, by the first line
    left unread; "" where each was read to its end."""
    found = []
    for named in given["input"]:
        file = done.full(in_plugin(named, done.root))
        said = text(file)
        if said is None:
            found.append(f"`{named}` is no file to read")
            continue
        count = len(said.splitlines())
        read = lines_read(done, file)
        left = [n for n in range(1, count + 1) if n not in read]
        if left or not read:
            found.append(f"`{named}` unread from line {left[0] if left else 1}")
    return "; ".join(found)
