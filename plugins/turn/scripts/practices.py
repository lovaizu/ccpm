"""What a person, CI or planner runs on a template, as `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/
practices.py <command> ...`: `write` and `check` its Markdown and its form, `sources` its grounds'
pages; and `ready` a run's folder, its templates checked and the part of each evaluator and
proofreader are given written into it. It hands each to templates.py in core/domain/."""

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

# Turn's own templates, the refactoring ones among them.
OWN = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "core", "domain", "best-practices"
)
USAGE = (
    "usage: practices.py write|check|sources <best practice json>...\n"
    "       practices.py ready <run>"
)


def kind_of(path: str) -> str:
    """The kind of the template at the path: its file's name."""
    return os.path.splitext(os.path.basename(path))[0]


def read(path: str) -> dict:
    """The JSON at the path."""
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def ready(run: str) -> int:
    """Makes the run's folder ready for designer, evaluator and proofreader: holds the kind's
    template and the refactoring template to their form, writes the Markdown beside a template the
    repository made, writes each template's standard into the run, and each one's groups into its
    run.json; gives 0, 1 with each fault of a template, or 2 where a file cannot be read."""
    path = os.path.join(run, "run.json")
    try:
        made = files.load(path, "run")
    except files.Unreadable as why:
        print(f"practices.py: could not make {run} ready: {why}", file=sys.stderr)
        return 2
    refactoring = os.path.join(OWN, f"{made['refactoring']}.json")
    for template, kind, key, out in (
        (made["template"], made["kind"], "groups", "standard.json"),
        (refactoring, made["refactoring"], "refactoring_groups", "refactoring-standard.json"),
    ):
        try:
            data = read(template)
        except (OSError, ValueError) as why:
            print(f"practices.py: could not read {template}: {why}", file=sys.stderr)
            return 2
        found = faults(data)
        for fault in found:
            print(f"practices.py: {template}: {fault}", file=sys.stderr)
        if found:
            return 1
        if not os.path.samefile(os.path.dirname(os.path.abspath(template)), OWN):
            with open(os.path.splitext(template)[0] + ".md", "w", encoding="utf-8") as f:
                f.write(markdown(kind, data))
        made[key] = groups(data, kind)
        files.save(os.path.join(run, out), standard(data))
    files.save(path, made)
    print(
        f"practices.py: {run} is ready: standard.json and refactoring-standard.json written, and"
        f" {len(made['groups'])} groups of {made['kind']} and {len(made['refactoring_groups'])} of"
        f" {made['refactoring']} in run.json."
    )
    return 0


def main(argv: list[str]) -> int:
    """`write <json>...` writes each Markdown beside its JSON; `check <json>...` names each fault
    of a JSON's form and each Markdown not as its JSON makes it; `sources <json>...` opens each
    ground's page and names each that is not the one meant; each fails if it names any.
    `ready <run>` makes a run's folder ready, as `ready` says."""
    if argv[:1] == ["ready"] and len(argv) == 2:
        return ready(argv[1])
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
