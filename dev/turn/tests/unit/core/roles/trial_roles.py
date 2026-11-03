"""The prompt tests of Turn's roles, each run alone as dev/architecture.md's Unit: prompts says:
Claude Code on Opus, with copies of Turn and pin, Lane laid; the main conversation starts the role
with its run values on tidy's repository, its run's folder laid as the roles before it would lay
it, and hands back what it gave. The person, where the role asks, is stood in for as in the E2E
tests.

Each run passes where the role's files are in form, Turn's checks give 0 on them, the role gave
the result its files call for, and evaluator and proofreader read nothing of the run beside their
standard. Run as `python3 dev/turn/tests/unit/core/roles/trial_roles.py <role> [runs] [first]`,
the role one of planner, designer, builder, evaluator, refactorer and proofreader."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from typing import Any

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.normpath(os.path.join(HERE, "..", "..", "..", "e2e")))

import trial_readme
import turning

RUN = ".turn/20261104-tidy-readme"
# A design of tidy's README, every decision settled, each question of the readme template served.
DECISIONS = [
    (
        "D1",
        "The first sentence",
        ["Q1", "Q10"],
        "tidy moves each file of a folder into a folder named after its kind.",
    ),
    (
        "D2",
        "Whom it is for",
        ["Q2", "Q3"],
        "people with a cluttered Downloads folder who can type a command",
    ),
    (
        "D3",
        "What it does not do",
        ["Q4"],
        "it does not delete, look inside folders, or move a file of no extension",
    ),
    (
        "D4",
        "The walkthrough",
        ["Q5", "Q6"],
        (
            "python3 tidy.py --dry-run on a practice folder in the temporary folder, then without"
            " --dry-run"
        ),
    ),
    (
        "D5",
        "The figure",
        ["Q7"],
        "a text figure: the folder, tidy's table of extensions, the folders made",
    ),
    ("D6", "Where to read next", ["Q8"], "tidy.py --help, and tidy.py itself"),
    ("D7", "The licence", ["Q9"], "MIT, linked to LICENSE"),
]
WORK = {
    "paths": ["README.md"],
    "commands": [
        "python3 tidy.py --help",
        "mkdir -p /tmp/tidy-trial",
        "touch /tmp/tidy-trial/photo.jpg /tmp/tidy-trial/Makefile",
        "python3 tidy.py --dry-run /tmp/tidy-trial",
    ],
}
README = """# tidy

tidy moves each file of a folder into a folder named after its kind.

## Walkthrough

Run `python3 tidy.py ~/Downloads`.
"""


def tree(template: dict[str, Any]) -> dict[str, Any]:
    """The design tree of DECISIONS, its questions the template's."""
    return {
        "goal": {
            "what": "A newcomer sorts their Downloads folder with tidy.",
            "grounds": ["the person"],
        },
        "questions": [{"id": f"readme/{q['id']}", "what": q["what"]} for q in template["benefits"]],
        "decisions": [
            {
                "id": i,
                "what": w,
                "contributes_to": [f"readme/{q}" for q in qs],
                "builds_on": [],
                "decided": d,
                "settled_by": "reasoning",
                "grounds": ["the goal"],
            }
            for i, w, qs, d in DECISIONS
        ],
    }


def laid(place: str, role: str) -> tuple[str, dict[str, str], dict[str, Any]]:
    """tidy's repository with the run's folder as the roles before the role lay it, and the role's
    run values."""
    repo, copies = turning.made(place)
    run = os.path.join(repo, RUN)
    template = os.path.join(copies["turn"], "core", "domain", "best-practices", "readme.json")
    values: dict[str, Any] = {"run": RUN}
    if role == "planner":
        return repo, copies, {**values, "request": "a README for tidy", "given": {}}
    os.makedirs(run)
    with open(os.path.join(run, "run.json"), "w", encoding="utf-8") as f:
        json.dump({"kind": "readme", "template": template, "refactoring": "refactor-doc"}, f)
    script = os.path.join(copies["turn"], "scripts", "practices.py")
    subprocess.run(
        [sys.executable, script, "ready", RUN], cwd=repo, check=True, capture_output=True
    )
    if role == "designer":
        return (
            repo,
            copies,
            {**values, "request": "a README for tidy", "given": {}, "returns": None},
        )
    with open(template, encoding="utf-8") as f:
        made = tree(json.load(f))
    parts = [{"id": "P1", "decisions": [d[0] for d in DECISIONS], "paths": ["README.md"]}]
    for name, data in (("design-tree.json", made), ("work.json", {**WORK, "parts": parts})):
        with open(os.path.join(run, name), "w", encoding="utf-8") as f:
            json.dump(data, f)
    common = {**values, "work": WORK["paths"], "commands": WORK["commands"]}
    if role == "builder":
        return (
            repo,
            copies,
            {
                **common,
                "decisions": parts[0]["decisions"],
                "answers": f"{RUN}/self-check/P1.json",
                "open": f"{RUN}/open/P1.json",
            },
        )
    with open(os.path.join(repo, "README.md"), "w", encoding="utf-8") as f:
        f.write(README)
    with open(os.path.join(run, "run.json"), encoding="utf-8") as f:
        planned = json.load(f)
    # The group of the walkthrough's questions, and the refactoring template's only group.
    if role == "evaluator":
        group = next(g for g in planned["groups"] if "readme/Q5" in g["questions"])
        return (
            repo,
            copies,
            {
                **common,
                "questions": group["questions"],
                "standard": f"{RUN}/standard.json",
                "answers": f"{RUN}/verification/{group['id']}.json",
            },
        )
    if role == "refactorer":
        return repo, copies, {**common, "answers": f"{RUN}/refactor-check.json"}
    group = planned["refactoring_groups"][0]
    return (
        repo,
        copies,
        {
            **common,
            "questions": group["questions"],
            "standard": f"{RUN}/refactoring-standard.json",
            "answers": f"{RUN}/proofreading/{group['id']}.json",
        },
    )


def results(session: str, role: str) -> list[str]:
    """Each result the role's runs gave by a result command that went through."""
    found = []
    for file in turning.trying.agents(session):
        if turning.trying.record.agent_type(file) != f"turn:{role}":
            continue
        for d in turning.trying.record.done(turning.trying.record.read(file) or [], ""):
            command = str(d.given.get("command", ""))
            if d.tool == "Bash" and "/hooks/lane/result.py" in command and not d.failed:
                found.append(command.split()[-1])
    return found


def reads(session: str, role: str) -> list[str]:
    """Each path the role's runs read."""
    return [
        str(d.given.get("file_path", ""))
        for file in turning.trying.agents(session)
        if turning.trying.record.agent_type(file) == f"turn:{role}"
        for d in turning.trying.record.done(turning.trying.record.read(file) or [], "")
        if d.tool == "Read"
    ]


def run(role: str, number: int) -> bool:
    """One run of the role's prompt test; prints what it found, and gives whether it passed."""
    place = turning.trying.folder("turn", f"trial-{role}-{number}")
    repo, copies, values = laid(place, role)
    first = (
        f"Start the subagent turn:{role} in the background with this prompt, word for word, its"
        " first line the JSON and its second the sentence after it, on lines of their own:\n\n"
        + json.dumps(values)
        + "\nDo the work these values give you.\n\nWhenever it ends with a message headed `For the"
        " person:`, give me that message word for word as your whole reply. When I answer, resume"
        f" it with SendMessage, its message `{turning.trying.ANSWERED}` and my answer"
        " on the next line. Do nothing else yourself. When it ends with no message for the"
        " person, say that the work is done."
    )
    session, turns = turning.talked(
        first, [copies["turn"], copies["pin"]], repo, place, trial_readme.INTENT, 60
    )
    wrong = turning.asked_wrong(turns)
    given = results(session, role)
    print(f"  results: {given}")
    if not given:
        wrong.append(f"{role} gave no result")
    turn = os.path.join(copies["turn"], "scripts")
    checks = {
        "planner": [["practices.py", "ready", RUN]],
        "designer": [["tree.py", "check", RUN]],
    }.get(role, [["answers.py", "check", RUN, values.get("answers", "")]])
    for check in checks:
        done = subprocess.run(
            [sys.executable, os.path.join(turn, check[0]), *check[1:]],
            cwd=repo,
            capture_output=True,
            text=True,
            check=False,
        )
        if done.returncode:
            wrong.append(f"{' '.join(check)} gave {done.returncode}: {done.stdout}{done.stderr}")
    if role in ("evaluator", "proofreader"):
        seen = [p for p in reads(session, role) if RUN in p and values["standard"] not in p]
        wrong += [f"{role} read {p}" for p in seen if "/forms/" not in p]
    if role == "evaluator" and given[-1:] != ["more"]:
        wrong.append("evaluator found good a walkthrough that moves the reader's own files")
    return turning.verdict([], wrong)


def main() -> None:
    """Runs the role's prompt test as the command line gives."""
    role = sys.argv[1]
    runs = int(sys.argv[2]) if len(sys.argv) > 2 else 3
    first = int(sys.argv[3]) if len(sys.argv) > 3 else 1
    passed = [run(role, n) for n in range(first, first + runs)]
    print(f"{sum(passed)} of {runs} runs passed")
    sys.exit(0 if all(passed) else 1)


if __name__ == "__main__":
    main()
