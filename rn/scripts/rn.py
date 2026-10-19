"""What rn's conductor runs for what must come out the same on every run: where the session stands,
which checklists a kind of work has, the CCS each work is made from, and the proposal at a sign-off.

The conductor is the AI that runs rn's commands `/rn:up`, `/rn:ty` and `/rn:gm` with the user. A
session is one piece of work from `/rn:up` to the merge, on a branch of its own; its record is the
folder `.rn/<yyyymmdd>-<slug>/` on that branch, the slug a short name for the piece of work, holding
the plan `steering.md` and `state.json`, where the session stands. A work, such as the plan, a
document or the finished work, is made by turn, a plugin rn depends on, from a CCS: a JSON file
naming the work, its receiver, what they use it for, the checklists of its kind and its decisions.
A kind, such as readme or code, has rn's own checklists and may have the user's addition, each item
of a checklist asking what the receiver of a work of that kind should get. turn writes, for each
item, its Good, what the receiver gets for what the item asks, with the lines of the work that give
it. At each of the three sign-offs, plan, design and deliverable, the conductor stops, shows the
user a proposal, and waits for `/rn:ty`.

Run from the top of the user's repository as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"
<subcommand> ...`, with Python 3.9 or later and the standard library alone. It prints JSON, or the
proposal as text for the conductor to show, and on a stop exits 1 with what went wrong and what to
do. It never commits or pushes: the conductor alone does.
"""

from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import subprocess
import sys
from typing import Any, Callable, NoReturn

# The plugin's own folder, which holds rn's checklists.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The folder in the user's repository holding every session's record and the user's checklists.
RECORD = ".rn"
# A slug, a kind or a work is a name that goes into a path, so it holds nothing that leads out of
# the folder it is meant for.
NAME = re.compile(r"[a-z0-9-]+")
SESSION_NAME = re.compile(r"[0-9]{8}-[a-z0-9-]+")
STAGES = ("asking", "plan", "documents", "tasks", "deliverable", "lessons", "ready")
SIGNOFFS = ("plan", "design", "deliverable")
# The keys of state.json the conductor sets, with the values each takes; None takes any text.
SETTABLE = {"stage": STAGES, "signoff": SIGNOFFS, "feedback": None}
# The keys an empty value clears; the stage is not among them, as a session always stands somewhere.
CLEARABLE = ("signoff", "feedback")
# For each role turn reads from a CCS, the key of the CCS entries that hold it; the call to turn:up
# hands this table to turn under its own key "kind".
ENTRIES = {
    "work": "deliverable",
    "checklist": "checklist",
    "receiver": "audience",
    "use": "purpose",
}
# The plan's front matter keys for the languages, which go into every CCS.
LANGUAGES = ("artifact-language", "conversation-language")


class Stop(Exception):
    """What went wrong, and what to do about it."""


def named(value: str, what: str) -> str:
    """The value, when it is a name; stops otherwise."""
    if not NAME.fullmatch(value):
        raise Stop(
            f"rn: the {what} {value!r} is not lowercase letters, digits and hyphens alone;"
            f" give it as such, such as add-login"
        )
    return value


def git(args: list[str], failed: str) -> str:
    """What git prints for the arguments; stops with what git said and the action given."""
    done = subprocess.run(["git"] + args, check=False, capture_output=True, text=True)
    if done.returncode:
        said = done.stderr.strip()
        raise Stop(f"rn: git {' '.join(args)} failed{': ' + said if said else ''}; {failed}")
    return done.stdout


def at_top() -> None:
    """Returns when rn runs at the top of a git repository; stops otherwise."""
    below = git(["rev-parse", "--show-prefix"], "run rn inside the user's repository").strip()
    if below:
        raise Stop(
            f"rn: this runs in {below} below the top of the repository; run it from the top,"
            ' after `cd "$(git rev-parse --show-toplevel)"`'
        )


def default_branch() -> str:
    """The remote's default branch, as git knows it."""
    ref = git(
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        "run `git remote set-head origin --auto` so git knows the default branch, then run this"
        " again",
    )
    return ref.strip()


def front_matter(path: str) -> dict[str, str]:
    """The `key: value` lines between the `---` lines that open the file; none where the file or
    its front matter is not there."""
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    if not lines or lines[0] != "---":
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        return {}
    found = {}
    # The opening `---` is read with the rest, and passed over as it holds no colon.
    for line in lines[:end]:
        key, colon, value = line.partition(":")
        if colon:
            found[key.strip()] = value.strip()
    return found


def plan(folder: str) -> str:
    """The path of the session's plan."""
    return os.path.join(folder, "steering.md")


def session() -> str | None:
    """The session the checked-out branch is in: the folder under `.rn/` the branch changed from
    the default branch whose plan is not finished; None where there is none, and a stop where there
    are more than one."""
    at_top()
    branch = default_branch()
    base = git(
        ["merge-base", branch, "HEAD"],
        f"the checked-out branch shares no history with {branch}; fetch it whole with"
        " `git fetch --unshallow origin` where the clone is shallow, or check out the session's"
        " branch",
    ).strip()
    changed = git(
        ["diff", "--name-only", base, "HEAD", "--", RECORD],
        "fix the repository as git says above, then run this again",
    )
    folders = sorted(
        {
            os.path.join(RECORD, parts[1])
            for parts in (path.split("/") for path in changed.splitlines())
            if SESSION_NAME.fullmatch(parts[1])
        }
    )
    going = [
        f for f in folders if os.path.isdir(f) and front_matter(plan(f)).get("status") != "finished"
    ]
    if len(going) > 1:
        raise Stop(
            f"rn: this branch changed more than one session not finished: {', '.join(going)};"
            " set `status: finished` in the plan of each that is over, or check out the branch"
            " of the one to go on with"
        )
    return next(iter(going), None)


def current() -> str:
    """The session the checked-out branch is in; stops where there is none."""
    found = session()
    if found is None:
        raise Stop(
            "rn: the checked-out branch holds no session; start one with `rn.py start <slug>`"
            " and commit its folder on the branch"
        )
    return found


def read_json(path: str, what: str) -> Any:
    """The JSON at the path; stops where it is not JSON, with what the file should be."""
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except ValueError:
        raise Stop(f"rn: {path} is not JSON; make it again as {what}") from None


def dumped(data: Any) -> str:
    """The data as JSON on one line, with text beyond ASCII as it is, for the conductor to read."""
    return json.dumps(data, ensure_ascii=False)


def write_json(path: str, data: Any) -> None:
    """Writes the data as JSON at the path, making its folder where it is not there."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        # One key or value to a line, so the user can read it on the pull request.
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


def state_path(folder: str) -> str:
    """The path of the session's state."""
    return os.path.join(folder, "state.json")


def read_state(folder: str) -> dict[str, Any]:
    """Where the session stands; empty where it has no `state.json`, as a session rn 0.9.0 left."""
    path = state_path(folder)
    if not os.path.isfile(path):
        return {}
    kept = read_json(path, "a JSON object, or restore it with `git checkout -- <path>`")
    if not isinstance(kept, dict):
        raise Stop(f"rn: {path} is not a JSON object; restore it with `git checkout -- {path}`")
    return kept


def run_session(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session the checked-out branch is in, with its state; None for both where there is
    none. Stops where rn is not at the top of a repository, git cannot tell the branch's changes,
    the branch changed more than one session not finished, or state.json is not a JSON object."""
    found = session()
    return {"session": found, "state": read_state(found) if found is not None else None}


def run_start(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Makes the session's folder and its state, for the conductor to commit; stops where the slug
    is not a name or the folder is there."""
    slug = named(args.slug, "slug")
    at_top()
    folder = os.path.join(RECORD, f"{today:%Y%m%d}-{slug}")
    if os.path.exists(folder):
        raise Stop(f"rn: {folder} is there already; give another slug")
    kept = {"stage": STAGES[0]}
    write_json(state_path(folder), kept)
    return {"session": folder, "state": kept}


def checklists(kind: str, root: str) -> list[str]:
    """The checklists for the kind: rn's own, then the user's addition; stops where neither is
    there."""
    found = sorted(glob.glob(os.path.join(root, "checklists", "**", f"{kind}.md"), recursive=True))
    added = os.path.join(RECORD, "checklists", f"{kind}.md")
    if os.path.isfile(added):
        found.append(added)
    if not found:
        raise Stop(
            f"rn: there is no checklist for the kind {kind}, neither rn's nor {added}; make"
            f" {added} first, as a work of its own to rn's checklist for checklists"
        )
    return found


def run_checklists(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The paths of the kind's checklists; stops where the kind is not a name or has none."""
    return checklists(named(args.kind, "kind"), root)


def given(value: str, what: str) -> str:
    """The value, when it holds some text; stops otherwise."""
    if not value.strip():
        raise Stop(f"rn: the {what} is empty; give it in words")
    return value


def there(path: str, what: str) -> str:
    """The path, when a file is there; stops otherwise."""
    if not os.path.isfile(path):
        raise Stop(f"rn: the {what} {path} is not there; give the path of a file, from the top")
    return path


def ccs_path(folder: str, work: str, suffix: str = "") -> str:
    """The path in the session's `ccs/` folder of the work's CCS, or, with the suffix `-result`, of
    the result turn writes for it."""
    return os.path.join(folder, "ccs", f"{work}{suffix}.json")


def run_ccs(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Writes the work's CCS into the session and gives the call that hands it to turn:up; stops
    where a name, a text or a file given is wrong, or the branch holds no session."""
    work = named(args.work, "work")
    ccs = {
        "focal_entities": [
            {ENTRIES["work"]: given(args.path, "path of the work")},
            {ENTRIES["receiver"]: given(args.receiver, "receiver")},
        ],
        "goal_orientation": [{ENTRIES["use"]: given(args.use, "use")}],
        "retrieved_artifacts": [
            {ENTRIES["checklist"]: path} for path in checklists(named(args.kind, "kind"), root)
        ]
        + [
            {"decisions": there(p, "decisions")}
            for p in ([args.decisions] if args.decisions else [])
        ]
        + [{"reference": there(p, "reference")} for p in args.reference],
    }
    folder = current()
    # The plan is the first work, made before it can say the languages; its own decisions do.
    languages = front_matter(plan(folder))
    ccs["constraints"] = [{k: languages[k]} for k in LANGUAGES if k in languages]
    path = ccs_path(folder, work)
    write_json(path, ccs)
    return {"ccs": path, "kind": ENTRIES, "result": ccs_path(folder, work, "-result")}


def settings(pairs: list[str]) -> dict[str, str]:
    """Each `key=value` as the key and its value; stops at a key rn does not keep or a value the
    key does not take."""
    found = {}
    for pair in pairs:
        key, equals, value = pair.partition("=")
        if not equals:
            raise Stop(f"rn: {pair!r} has no `=`; give each setting as `<key>=<value>`")
        if key not in SETTABLE:
            raise Stop(f"rn: {key!r} is no key rn keeps; give one of {', '.join(SETTABLE)}")
        takes = SETTABLE[key]
        clears = key in CLEARABLE
        if takes is not None and value not in takes and not (clears and not value):
            clear = ", or nothing to clear it" if clears else ""
            raise Stop(
                f"rn: {key} takes one of {', '.join(takes)}{clear}; {value!r} is none of them"
            )
        found[key] = value
    return found


def run_state(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Where the session stands, after setting each key given; an empty value clears its key.
    Stops where a setting is not one rn keeps, the branch holds no session, or state.json is not a
    JSON object."""
    sets = settings(args.pairs)
    folder = current()
    kept = read_state(folder)
    if not sets:
        return kept
    for key, value in sets.items():
        if value:
            kept[key] = value
        else:
            kept.pop(key, None)
    write_json(state_path(folder), kept)
    return kept


def broken(path: str, what: str) -> NoReturn:
    """Stops, saying what in turn's result at the path is not as turn writes it."""
    raise Stop(f"rn: {path} is not a result turn writes: {what}; have turn:up make the work again")


def group(holder: dict[str, Any], key: str, path: str) -> list[Any]:
    """The list under the key of an object in turn's result, empty where the key is not there;
    stops where it is not a list."""
    found = holder.get(key, [])
    if not isinstance(found, list):
        broken(path, f'"{key}" is not a list')
    return found


def entry(value: Any, keys: tuple[str, ...], path: str) -> dict[str, Any]:
    """The entry of turn's result, when it is an object holding each key; stops otherwise, showing
    the entry."""
    if not isinstance(value, dict) or any(k not in value for k in keys):
        broken(path, f"the entry {dumped(value)} is not an object holding {', '.join(keys)}")
    return value


def listed(value: Any, path: str) -> str:
    """The texts of a list in turn's result, such as an item's lines, joined; stops where it is
    not a list of texts."""
    if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
        broken(path, f"{dumped(value)} is not a list of texts")
    return ", ".join(value)


def shown(result: Any, path: str) -> dict[str, str]:
    """Each item of the work's checklists, by its checklist and ID, as the proposal shows it: its
    Good with its lines, what it lacks with where it is not found, or the question it waits on.
    Stops where turn has not returned, as turn keeps its run under "running" in the result file
    until it returns, and where the result is not in the form turn writes."""
    if not isinstance(result, dict):
        broken(path, "it is not a JSON object")
    if "running" in result:
        raise Stop(
            f"rn: turn has not returned its result at {path}; wait for turn:up to end, then run"
            " this again"
        )
    lines: dict[str, str] = {}
    for found in group(result, "items", path):
        i = entry(found, ("checklist", "item"), path)
        if "parts" in i:
            parts = [entry(p, ("part", "good", "lines"), path) for p in group(i, "parts", path)]
            each = "; ".join(
                f"{p['part']}: {p['good']} ({listed(p['lines'], path)})" for p in parts
            )
            lines[f"{i['checklist']} {i['item']}"] = f"Good in each part: {each}"
        else:
            i = entry(found, ("checklist", "item", "good", "lines"), path)
            lines[f"{i['checklist']} {i['item']}"] = (
                f"Good: {i['good']} ({listed(i['lines'], path)})"
            )
    for found in group(result, "not_good", path):
        i = entry(found, ("checklist", "item", "gets", "places"), path)
        places = listed(i["places"], path)
        lines[f"{i['checklist']} {i['item']}"] = f"lacks: {i['gets']} (not found at {places})"
    for found in group(result, "questions", path):
        q = entry(found, ("question", "items"), path)
        for waiting in group(q, "items", path):
            i = entry(waiting, ("checklist", "item"), path)
            lines[f"{i['checklist']} {i['item']}"] = f"waits on: {q['question']}"
    return lines


def signoff_at(kept: dict[str, Any], folder: str) -> str:
    """The sign-off the session waits at; stops where state.json names none."""
    signoff = kept.get("signoff")
    if signoff not in SIGNOFFS:
        raise Stop(
            f"rn: {state_path(folder)} names no sign-off the session waits at; set it with"
            f" `rn.py state signoff=<{'|'.join(SIGNOFFS)}>`"
        )
    return signoff


def changes(before: dict[str, str] | None, now: dict[str, str]) -> list[str]:
    """What changed since the last proposal at this sign-off, as lines."""
    if before is None:
        return ["- The first proposal at this sign-off."]
    changed = [f"- {key}: {line}" for key, line in now.items() if before.get(key) != line]
    return changed or ["- No item changed since the last proposal at this sign-off."]


def run_proposal(args: argparse.Namespace, root: str, today: datetime.date) -> str:
    """The proposal at the sign-off the session waits at, from turn's result, the plan and the
    state; keeps the items it shows in the state, for the next proposal's "what changed"."""
    work = named(args.work, "work")
    folder = current()
    path = ccs_path(folder, work, "-result")
    if not os.path.isfile(path):
        raise Stop(
            f"rn: {path} is not there; run turn:up with the call `rn.py ccs {work} ...` printed,"
            " then this again"
        )
    now = shown(read_json(path, "turn:up writes it"), path)
    kept = read_state(folder)
    signoff = signoff_at(kept, folder)
    pr = front_matter(plan(folder)).get("pr")
    if not pr:
        raise Stop(
            f"rn: the plan {plan(folder)} has no `pr` in its front matter; put the pull request's"
            " URL there"
        )
    at = SIGNOFFS.index(signoff)
    stands = (
        [f"- {s.capitalize()} sign-off: done" for s in SIGNOFFS[:at]]
        + [f"- {signoff.capitalize()} sign-off: now"]
        + [f"- {s.capitalize()} sign-off: ahead" for s in SIGNOFFS[at + 1 :]]
    )
    feedback = [f"- Sent back with: {kept['feedback']}"] if kept.get("feedback") else []
    text = [
        f"# The {signoff} sign-off: {work}",
        "",
        "## Sign-offs",
        "",
        *stands,
        "",
        "## What changed",
        "",
        *feedback,
        *changes(kept.get("shown", {}).get(signoff), now),
        "",
        "## Pull request",
        "",
        pr,
        "",
        "## Checklists",
        "",
        *(f"- {key}: {line}" for key, line in now.items()),
    ]
    kept.setdefault("shown", {})[signoff] = now
    write_json(state_path(folder), kept)
    return "\n".join(text)


class Parser(argparse.ArgumentParser):
    """argparse, stopping as rn stops rather than exiting with its own code."""

    def error(self, message: str) -> NoReturn:
        raise Stop(f"rn: {message}; give it as {self.format_usage().strip()[len('usage: ') :]}")


def parser() -> Parser:
    """The subcommands, each with what it takes and the function that runs it."""
    top = Parser(prog="rn.py")
    sub = top.add_subparsers(dest="subcommand", required=True)
    sub.add_parser("session").set_defaults(run=run_session)
    start = sub.add_parser("start")
    start.set_defaults(run=run_start)
    start.add_argument("slug")
    lists = sub.add_parser("checklists")
    lists.set_defaults(run=run_checklists)
    lists.add_argument("kind")
    ccs = sub.add_parser("ccs")
    ccs.set_defaults(run=run_ccs)
    ccs.add_argument("work")
    ccs.add_argument("path")
    ccs.add_argument("--kind", required=True)
    ccs.add_argument("--receiver", required=True)
    ccs.add_argument("--use", required=True)
    ccs.add_argument("--decisions")
    ccs.add_argument("--reference", action="append", default=[])
    state = sub.add_parser("state")
    state.set_defaults(run=run_state)
    state.add_argument("pairs", nargs="*", metavar="<key>=<value>")
    proposal = sub.add_parser("proposal")
    proposal.set_defaults(run=run_proposal)
    proposal.add_argument("work")
    return top


def main(argv: list[str], root: str, today: datetime.date) -> int:
    """Runs the subcommand and prints what it gives, JSON or the proposal's text; 1 on a stop."""
    try:
        args = parser().parse_args(argv)
        run: Callable[..., Any] = args.run
        out = run(args, root, today)
    except Stop as stop:
        print(stop)
        return 1
    print(out if isinstance(out, str) else dumped(out))
    return 0


# Run as the command, and not when the tests import it under the name rn. It is written as
# membership rather than `==`, since an order comparison such as `<=` would also tell "__main__"
# from "rn", and a mutant making it one would pass every test.
if __name__ in ("__main__",):
    sys.exit(main(sys.argv[1:], ROOT, datetime.date.today()))
