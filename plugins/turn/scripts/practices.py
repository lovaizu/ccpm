"""What a person, CI or planner runs on a template, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/
practices.py <command> ...`: `write` and `check` its Markdown and its form, `sources` its grounds'
pages, `standard` the part of it evaluator is given, and `groups` its questions in groups into a
run's run.json. It hands each to templates.py in core/domain/."""

from __future__ import annotations

import json
import os
import sys

# No module before it on the path has the name of Turn's.
sys.path.insert(
    0,  # pragma: no mutate
    os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain"),
)

import files
from templates import faults, groups, markdown, sources, standard

USAGE = (
    "usage: practices.py write|check|sources <best practice json>...\n"
    "       practices.py standard <best practice json> <standard json>\n"
    "       practices.py groups <best practice json> <run json>"
)


def kind_of(path: str) -> str:
    """The kind of the template at the path: its file's name."""
    return os.path.splitext(os.path.basename(path))[0]


def read(path: str) -> dict:
    """The JSON at the path."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def grouped(template: str, run: str) -> int:
    """Writes the template's groups into the run's run.json, under `groups` where it is the run's
    kind and `refactoring_groups` where it is its refactoring; 2 where it is neither or the run
    cannot be read."""
    try:
        made = files.load(run, "run")
    except files.Unreadable as why:
        print(f"practices.py: could not read {run}: {why}", file=sys.stderr)
        return 2
    kind = kind_of(template)
    keys = {made["kind"]: "groups", made["refactoring"]: "refactoring_groups"}
    if kind not in keys:
        print(
            f"practices.py: {template} is neither {made['kind']} nor {made['refactoring']}, the"
            f" templates of {run}",
            file=sys.stderr,
        )
        return 2
    made[keys[kind]] = groups(read(template), kind)
    files.save(run, made)
    return 0


def main(argv: list[str]) -> int:
    """`write <json>...` writes each Markdown beside its JSON; `check <json>...` names each fault
    of a JSON's form and each Markdown not as its JSON makes it; `sources <json>...` opens each
    ground's page and names each that is not the one meant; each fails if it names any.
    `standard <json> <out>` writes the template's standard; `groups <json> <run>` its groups."""
    if argv[:1] == ["standard"] and len(argv) == 3:
        files.save(argv[2], standard(read(argv[1])))
        return 0
    if argv[:1] == ["groups"] and len(argv) == 3:
        return grouped(argv[1], argv[2])
    if len(argv) < 2 or argv[0] not in ("write", "check", "sources"):
        print(USAGE, file=sys.stderr)
        return 2
    failed = False
    for path in argv[1:]:
        data = read(path)
        target = os.path.splitext(path)[0] + ".md"
        text = markdown(kind_of(path), data)
        # The command is write, check or sources, write the last of them in order.
        if argv[0] == "write":  # pragma: no mutate
            with open(target, "w", encoding="utf-8") as f:
                f.write(text)
        # The command is check or sources here, sources the last of them in order.
        elif argv[0] == "sources":  # pragma: no mutate
            for fault in sources(data):
                print(f"practices.py: {path}: {fault}", file=sys.stderr)
                failed = True
        else:
            found = faults(data)
            try:
                with open(target, encoding="utf-8") as f:
                    if f.read() != text:
                        found.append(f"{target} is not as its JSON makes it; run write")
            except FileNotFoundError:
                found.append(f"{target} is missing; run write")
            for fault in found:
                print(f"practices.py: {path}: {fault}", file=sys.stderr)
            failed = failed or bool(found)
    return 1 if failed else 0


# Run as the command, and not when the tests import it under the name practices.
if __name__ == "__main__":  # pragma: no mutate
    sys.exit(main(sys.argv[1:]))
