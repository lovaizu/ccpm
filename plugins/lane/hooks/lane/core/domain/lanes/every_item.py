"""every_item: the subagent gives its result only once it has answered every item of an input its
step names, read at the items port, each by its ID, such as `B-1`, `R33` or `KR1.1`: an item is
answered where its ID stands as a word of its own in a file the subagent wrote in this run, the
input left out, as rewriting the input keeps every ID in it. An item with no ID is not counted, as
no text tells an answer to it from any other."""

from __future__ import annotations

import re

from done import Done, text, written

ACTION = "end"
WORDING = "Answer every item of `<input>`."
CALLS = True


def missing(given: dict[str, list[str]], done: Done) -> str:
    """What is missing: each input that is no file to read, and each ID answered in no file the
    subagent wrote in this run; "" where every item is answered."""
    inputs = {done.full(i): i for i in given["input"]}
    files = list(dict.fromkeys(f for f in written(done, done.run) if f not in inputs))
    answers = [t for t in map(text, files) if t is not None]
    found = []
    for file, named in inputs.items():
        said = text(file)
        if said is None:
            found.append(f"`{named}` is no file to read")
            continue
        left = [k for k in done.items(named, said) if not any(stands(k, a) for a in answers)]
        if left:
            found.append(f"{', '.join(left)} of `{named}` unanswered")
    return "; ".join(found)


def stands(key: str, answer: str) -> bool:
    """Whether the key stands in the answer as a word of its own, so `B-1` is not found in `B-12`,
    `B-1.2` or `AB-1`."""
    return (
        re.search(rf"(?<![A-Za-z0-9-]){re.escape(key)}(?![A-Za-z0-9]|[.-][0-9])", answer)
        is not None
    )
