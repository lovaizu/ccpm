"""What rn's conductor runs for what must come out the same on every run, so that a rule a machine
can judge holds at the moment of the move: the session found and started, the state replaced and
every change kept on the session's branch, a kind's checklists, the CCS each work is made from, the
proposal at a sign-off made from what is pushed alone, and the records of the session shown to rn's
learner and its lessons kept.

The conductor is the AI that runs rn's commands `/rn:up`, `/rn:ty` and `/rn:gm` with the user. A
session is one piece of work from `/rn:up` to the merge, on a branch of its own; its record is the
folder `.rn/<yyyymmdd>-<slug>/` on that branch, the slug a short name for the piece of work, holding
the plan `steering.md`, each work's decisions `decisions/<work>.decisions.md`, each work's CCS and
turn's result for it under `ccs/`, and `state.json`, the conductor's state. A CCS is the shape ACC
gives an AI's state: a JSON object of parts, each a list of entries, each entry a kind and its
value as text. A work, such as the plan, a document or a task's result, is made by turn, a plugin rn
depends on, from such a CCS. A kind, such as readme or code, has rn's own checklist, and may have
the user's addition `.rn/checklists/<kind>.md`. At a sign-off, plan, design or deliverable, the
conductor shows the user a proposal and waits for `/rn:ty` or `/rn:gm`.

Once the user approves the finished work, rn's learner reads the session's record whole, its history
on the branch and its files, and searches the conductor's conversations, as Claude Code keeps them,
for what only they show; each is shown as text in the repository's git folder, where nothing is
committed, and its lessons, each resting on words quoted from a text, are kept in the session as
`learnt.json`.

Keeping a move is a commit of every change on the session's branch and a push of it, so a fresh
conversation, or another machine, goes on from it; the plan is held to the template of rn's plan
checklist before it is kept, and a work is handed to turn only once everything is pushed.

Run from the top of the user's repository as `python3 "${CLAUDE_PLUGIN_ROOT}/scripts/rn.py"
<subcommand> ...`, with Python 3.9 or later and the standard library alone. It prints JSON, or the
proposal as text for the conductor to show, and on a stop exits 1 with what went wrong and what to
do.
"""

from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
from collections.abc import Callable
from typing import Any, NoReturn

# turn's reader of a CCS, of Claude Code's records and of the learner's reply, and lane's of a
# Markdown template, each taken through a link.
import call
import forms
import records
import template

# The plugin's own folder, which holds rn's checklists.
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# The folder in the user's repository holding every session's record and the user's checklists.
RECORD = ".rn"
# A slug, a kind or a work is a name that goes into a path, so it holds nothing that leads out of
# the folder it is meant for.
NAME = re.compile(r"[a-z0-9-]+")
SESSION_NAME = re.compile(r"[0-9]{8}-[a-z0-9-]+")
# For each role turn reads from a CCS, the key of the CCS entries that hold it; the call to turn:up
# hands this table to turn.
ENTRIES = {
    "work": "deliverable",
    "checklist": "checklist",
    "receiver": "audience",
    "use": "purpose",
    "has": "has",
}
# The kind of a checklist, which rn's checklist for checklists makes from rn's `usability.md`, what
# any reader needs, as well.
CHECKLIST = "checklist"
# The plan's front matter keys for the languages, which go into every CCS.
LANGUAGES = ("artifact-language", "conversation-language")
# The plan is the work of this name, its kind the same, as rn's plan checklist names its decisions
# `decisions/plan.decisions.md`.
PLAN = "plan"
# The IDs of rn's plan checklist, F-1: the goal on a line of its own above the criteria, and each
# criterion and each task an item of its section's list, the lines indented under an item its own.
GOAL = "G1: "
GOAL_FORM = "`G1: <the user's purpose, with why they want it>`"
CRITERIA = "Acceptance criteria"
CRITERION = re.compile(r"- (AC\d+): \S.*")
CRITERION_FORM = "`- AC<n>: <one thing the finished work must do for the goal>`"
TASKS = "Tasks"
TASK = re.compile(r"- \[[ x]\] (T\d+): \S.*")
TASK_FORM = "`- [ ] T<n>: <the part of the piece of work>`"
# The parts of the plan a proposal shows, by the heading each is under, "" for the part above the
# first, with how each line holding an ID in it begins.
SHOWS = {"": GOAL, CRITERIA: "- "}
# The sign-offs a proposal is made at from the plan alone, each with the words naming where the work
# is and the parts of the plan it shows: the goal and the criteria at the plan's, as the user
# approves what the finished work will do and why, and the criteria at the deliverable's, as the
# finished work is checked against them.
SIGNOFFS = {
    "plan": ("The plan is on the draft pull request", ("", CRITERIA)),
    "deliverable": ("The finished work is on the pull request", (CRITERIA,)),
}
# The trailer marking the commit of a proposal shown, with its sign-off.
SHOWN = "Rn-Sign-off: "
ANSWER = "/rn:ty to approve, /rn:gm <feedback> to ask for a change."
# The folder in the repository's git folder where the learner is shown the records and replies, so
# nothing of it shows as a change to keep.
LEARNING = "rn"
# The learner's reply, in the git folder.
LEARNT = "learnt.json"
# The folder in the session where the lessons of each stretch are kept, as `<n>.json`, n counting
# the stretches from 1.
LESSONS = "learnt"
KEPT = re.compile(r"([0-9]+)\.json")
# Claude Code names the folder of a project's records by the project's path, each character that is
# not a letter or digit as `-`, counted as JavaScript counts, a character beyond the basic plane as
# two; a name longer than this is cut to it and a hash of the path put after, which rn does not make
# again, so it finds that folder by what goes before the hash.
NAME_LENGTH = 200
# What a stop whose git command failed says to do where only git's own words tell what is wrong.
AS_GIT_SAYS = "fix it as git says, then run this again"


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


def git(args: list[str], failed: str, fed: str | None = None) -> str:
    """What git prints for the arguments, with the text fed to its input; stops with what git said
    and the action given."""
    done = subprocess.run(["git"] + args, check=False, capture_output=True, text=True, input=fed)
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
    """The remote's default branch, as git knows it, such as origin/main."""
    ref = git(
        ["symbolic-ref", "--short", "refs/remotes/origin/HEAD"],
        "run `git remote set-head origin --auto` so git knows the default branch, then run this"
        " again",
    )
    return ref.strip()


def base() -> str:
    """The commit the checked-out branch left the default branch at."""
    branch = default_branch()
    return git(
        ["merge-base", branch, "HEAD"],
        f"the checked-out branch shares no history with {branch}; fetch it whole with"
        " `git fetch --unshallow origin` where the clone is shallow, or check out the session's"
        " branch",
    ).strip()


def changed() -> list[str]:
    """Each path of the working tree changed since the last commit, every file of a folder not
    yet added among them."""
    listed = git(["status", "--porcelain", "-uall"], AS_GIT_SAYS)
    return [line[3:] for line in listed.splitlines()]


def front_matter(path: str) -> dict[str, str]:
    """The `key: value` lines of the front matter the file opens with, as lane reads them; none
    where the file is not there, opens with no front matter, or holds one lane cannot read, as
    nothing it says can be told."""
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as f:
        lines = f.read().splitlines()
    try:
        found = template.keys(lines) or {}
    except ValueError:
        return {}
    return {key: value for key, (_, value) in found.items()}


def plan(folder: str) -> str:
    """The path of the session's plan."""
    return os.path.join(folder, "steering.md")


def session() -> str | None:
    """The session the checked-out branch is in: the folder under `.rn/` the branch changed from
    the default branch whose plan is not finished; None where there is none, and a stop where there
    are more than one."""
    at_top()
    paths = git(["diff", "--name-only", base(), "HEAD", "--", RECORD], AS_GIT_SAYS)
    folders = sorted(
        {
            os.path.join(RECORD, parts[1])
            for parts in (path.split("/") for path in paths.splitlines())
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
        )
    return found


def write_json(path: str, data: Any) -> None:
    """Writes the data as JSON at the path, making its folder where it is not there."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        # One key or value to a line, so the user can read it on the pull request.
        json.dump(data, f, ensure_ascii=False, indent=1)
        f.write("\n")


def dumped(data: Any) -> str:
    """The data as JSON on one line, with text beyond ASCII as it is, for the conductor to read."""
    return json.dumps(data, ensure_ascii=False)


def state_path(folder: str) -> str:
    """The path of the session's state."""
    return os.path.join(folder, "state.json")


def read_state(folder: str, failed: str) -> dict[str, list[dict[str, str]]]:
    """The session's state, read as turn reads a CCS; stops where it is no CCS, with the action
    given."""
    try:
        return call.read_ccs(state_path(folder))
    except call.Stop as stop:
        said = str(stop)[len("turn: ") :]
        raise Stop(f"rn: {said}; {failed}") from None


def run_session(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """The session the checked-out branch is in, with its state, empty where it has no
    `state.json`, as a session rn 0.9.0 left; None for both where there is none. Stops where rn is
    not at the top of a repository, git cannot tell the branch's changes, the branch changed more
    than one session not finished, or the state is no CCS."""
    found = session()
    if found is None:
        return {"session": None, "state": None}
    path = state_path(found)
    restore = f"restore the state kept with `git checkout HEAD -- {path}`, or write it again as one"
    state = read_state(found, restore) if os.path.isfile(path) else {}
    return {"session": found, "state": state}


def given(value: str, what: str) -> str:
    """The value, when it holds some text; stops otherwise."""
    if not value.strip():
        raise Stop(f"rn: the {what} is empty; give it in words")
    return value


def own(kind: str, root: str) -> list[str]:
    """rn's own checklist for the kind, in any folder of rn's checklists; none where rn has none."""
    return sorted(glob.glob(os.path.join(root, "checklists", "**", f"{kind}.md"), recursive=True))


def template_of(root: str) -> tuple[str, template.Template]:
    """rn's plan checklist, with its template, the fence under its F-1, as lane reads it; stops
    where rn's checklist or its template is not there, or lane cannot read it."""
    for path in own(PLAN, root):
        with open(path, encoding="utf-8") as f:
            lines = f.read().splitlines()
        heading = next((n for n, line in enumerate(lines) if line.startswith("### F-1: ")), None)
        fences = (
            [] if heading is None else [n for n in range(heading, len(lines)) if fence(lines[n])]
        )
        if len(fences) < 2:
            raise Stop(f"rn: {path} holds no template under its F-1; install rn again")
        opening, closing, *_ = fences
        try:
            return path, template.read("\n".join(lines[opening + 1 : closing]))
        except ValueError as why:
            raise Stop(f"rn: {path} F-1 is no template rn reads: {why}; install rn again") from None
    raise Stop(
        f"rn: rn has no checklist for plans in {os.path.join(root, 'checklists')}; install rn again"
    )


def fence(line: str) -> bool:
    """Whether the line opens or closes a fence of a checklist, as rn's checklists write them."""
    return line.startswith("```")


def sections(lines: list[str]) -> dict[str, list[tuple[int, str]]]:
    """Each part of the plan's body under a `##` heading, by the heading's text, and the part above
    the first under "", each as its lines with their numbers, counted from 1."""
    start = template.body(lines)
    heads = {n: said for n, level, said in template.headings(lines, start) if level in (2,)}
    part = ""
    found: dict[str, list[tuple[int, str]]] = {part: []}
    for n, line in enumerate(lines[start:], start + 1):
        if n in heads:
            part = heads[n]
            found[part] = []
        else:
            found[part].append((n, line))
    return found


# For each list of the plan whose items have IDs: its heading, the form of an item, and the item in
# words, as the stop names it.
LISTS = (
    (CRITERIA, CRITERION, f"an acceptance criterion as {CRITERION_FORM}"),
    (TASKS, TASK, f"a task as {TASK_FORM}"),
)


def ids_out(lines: list[str]) -> str:
    """The point the plan's goal, criteria and tasks are out of their IDs by, at its line; "" where
    they hold."""
    parts = sections(lines)
    if not any(line.startswith(GOAL) for _, line in parts[""]):
        return f"expected the goal as {GOAL_FORM} above `## {CRITERIA}`, found none"
    for part, form, words in LISTS:
        seen: list[str] = []
        for n, line in parts.get(part, []):
            if not line.startswith("- "):
                continue
            item = form.fullmatch(line)
            if item is None:
                return f"line {n}: expected {words}, found `{line}`"
            if item.group(1) in seen:
                return f"line {n}: expected each ID once, found {item.group(1)} again"
            seen.append(item.group(1))
        if part in (CRITERIA,) and not seen:
            return f"expected {words} under `## {CRITERIA}`, found none"
    return ""


def out_of_form(path: str, root: str) -> str:
    """What the plan at the path is out of the form of rn's plan checklist by, its F-1's front
    matter, headings and IDs, with the checklist and the point; "" where it holds."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    checklist, asked = template_of(root)
    point = template.held(asked, text) or ids_out(text.splitlines())
    return point and f"{path} is out of the form of rn's plan checklist ({checklist} F-1): {point}"


def keep(folder: str, message: str, root: str) -> str:
    """Keeps the move on the session's branch: every change committed with the message, once the
    plan holds its form and the state is a CCS replaced by this move, then pushed; gives the commit.
    Stops, keeping nothing, where the plan is out of its form, the state is not there or no CCS,
    other changes come with the state as kept last, or the message is empty; and where git fails."""
    steering = plan(folder)
    said = out_of_form(steering, root) if os.path.isfile(steering) else ""
    if said:
        kept = git(["ls-files", "--", steering], AS_GIT_SAYS)
        undo = (
            f"restore the one kept with `git checkout HEAD -- {steering}`"
            if kept
            else f"remove it with `rm {steering}`"
        )
        raise Stop(
            f"rn: {said}; the plan is not kept: {undo}, replace the state, and have turn make the"
            " plan again"
        )
    path = state_path(folder)
    if not os.path.isfile(path):
        raise Stop(f"rn: {path} is not there; write the state there, as a CCS, then run this again")
    read_state(folder, "write the state again as one, then run this again")
    paths = changed()
    if paths and path not in paths:
        raise Stop(
            f"rn: the move changed {', '.join(paths)}, but {path} is as kept last; replace it whole"
            " with the facts this move brought, then run this again"
        )
    if paths:
        git(["add", "-A"], AS_GIT_SAYS)
        git(["commit", "-q", "-F", "-"], AS_GIT_SAYS, given(message, "message"))
    push()
    return git(["rev-parse", "HEAD"], AS_GIT_SAYS).strip()


def push() -> None:
    """Pushes the checked-out branch to the remote's branch of its name, tracking it; stops with
    what git said and how to push once it is fixed."""
    git(
        ["push", "-q", "-u", "origin", "HEAD"],
        "fix it as git says, then push with `git push -u origin HEAD`",
    )


def pushed() -> None:
    """Returns when every change is committed and pushed, so what rn goes on from is what a fresh
    conversation would find; stops otherwise, saying how to keep or push it."""
    paths = changed()
    if paths:
        raise Stop(
            f"rn: the record has changes not kept, {', '.join(paths)}; rn goes on only from what is"
            " pushed, so keep the move with `rn.py state --message <what it brought>` first, then"
            " run this again"
        )
    ahead = git(
        ["rev-list", "--count", "@{upstream}..HEAD"],
        "push the branch with `git push -u origin HEAD`, then run this again",
    ).strip()
    if int(ahead):
        raise Stop(
            f"rn: the branch has {ahead} commit(s) not pushed; push with `git push`, then run this"
            " again"
        )


def run_start(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Starts a session on a branch of its own named by the slug, made from the remote's default
    branch as it is now, with its folder and an empty state, kept with the message; gives the
    folder, the branch and the branch a pull request of it goes to. Stops, leaving the checked-out
    branch as it is, where the slug is not a name, rn is not at the top of a repository, the working
    tree has changes not committed, the folder or the branch is there already, or the message is
    empty; and where git fails."""
    slug = named(args.slug, "slug")
    message = given(args.message, "message")
    at_top()
    paths = changed()
    if paths:
        raise Stop(
            f"rn: the working tree has changes not committed: {', '.join(paths)}; rn leaves them as"
            " they are, and starts from the default branch: commit or stash them, then run this"
            " again"
        )
    git(["fetch", "-q", "origin"], AS_GIT_SAYS)
    branch = default_branch()
    folder = os.path.join(RECORD, f"{today:%Y%m%d}-{slug}")
    if git(["ls-tree", "--name-only", branch, "--", folder], AS_GIT_SAYS):
        raise Stop(f"rn: {folder} is on {branch} already; give another slug")
    git(["checkout", "-q", "--no-track", "-b", slug, branch], "give another slug")
    write_json(state_path(folder), {})
    keep(folder, message, root)
    return {"session": folder, "branch": slug, "base": branch.partition("/")[2]}


def run_state(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the move: the state the conductor wrote whole into `state.json`, with every other
    change of the move, committed with the message and pushed; gives the commit. Stops where the
    branch holds no session, or as keeping a move stops."""
    folder = current()
    return {"kept": keep(folder, args.message, root)}


def checklists(kind: str, root: str) -> list[str]:
    """The checklists for the kind: rn's own, then the user's addition; stops where neither is
    there."""
    found = own(kind, root)
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


def held(path: str) -> str:
    """The path of what the receiver has with the work, when a file or folder is there; stops
    otherwise, as turn stops a call naming one that is not."""
    if not os.path.exists(path):
        raise Stop(
            f"rn: what the receiver has, {path}, is not there; give the path of a file or folder"
            " they have with the work, from the top"
        )
    return path


def ccs_path(folder: str, work: str, suffix: str = "") -> str:
    """The path in the session's `ccs/` folder of the work's CCS, or, with the suffix `-result`, of
    the result turn writes for it."""
    return os.path.join(folder, "ccs", f"{work}{suffix}.json")


def run_ccs(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Writes the work's CCS into the session and gives the call that hands it to turn:up, once
    every change is pushed, so the work is made from decisions a fresh conversation also has.
    Stops where a name, a text or a path given is wrong, the work's decisions are not there, the
    branch holds no session, or a change is not kept or pushed."""
    work = named(args.work, "work")
    kind = named(args.kind, "kind")
    receiver = given(args.receiver, "receiver")
    use = given(args.use, "use")
    # The session is found first, which stops below the top of the repository, since each path
    # given is read from the top.
    folder = current()
    pushed()
    has = [held(p) for p in args.has]
    decisions = os.path.join(folder, "decisions", f"{work}.decisions.md")
    if not os.path.isfile(decisions):
        raise Stop(
            f"rn: the work's decisions {decisions} are not there; write there what the work is"
            " made from, keep it, then run this again"
        )
    # A CCS holds its entries in four parts, the shape turn takes: focal_entities, what the work is
    # about, the work, its receiver and what they have with it; goal_orientation, what the work is
    # for; retrieved_artifacts, the files it is made from, the kind's checklists, rn's
    # `usability.md` where the work is a checklist, and its decisions; and constraints, the bounds
    # it is made in: the languages, and rn's checklist for a fix, which turn's generator holds
    # whenever it changes a work already there, sent back or in a later round as well. turn finds
    # each entry by its key, whichever part holds it.
    usability = os.path.join(root, "checklists", "usability.md")
    sources = [{"source": usability}] if kind in (CHECKLIST,) else []
    ccs = {
        "focal_entities": [
            {ENTRIES["work"]: given(args.path, "path of the work")},
            {ENTRIES["receiver"]: receiver},
        ]
        + [{ENTRIES["has"]: p} for p in has],
        "goal_orientation": [{ENTRIES["use"]: use}],
        "retrieved_artifacts": [{ENTRIES["checklist"]: p} for p in checklists(kind, root)]
        + sources
        + [{"decisions": decisions}],
    }
    # The plan is the first work, made before it can say the languages; its own decisions do.
    languages = front_matter(plan(folder))
    ccs["constraints"] = [{k: languages[k]} for k in LANGUAGES if k in languages]
    ccs["constraints"].append({"fix": os.path.join(root, "checklists", "fix.md")})
    path = ccs_path(folder, work)
    write_json(path, ccs)
    # turn's call takes the table of keys under "kind", a field name of turn's own that is no kind
    # of work.
    return {"ccs": path, "kind": ENTRIES, "result": ccs_path(folder, work, "-result")}


def item(lines: list[tuple[int, str]], at: int) -> str:
    """The text of the line at the index and the lines it runs on to, until a blank line or the
    next item of a list, as one line."""
    words = [lines[at][1]]
    for _, line in lines[at + 1 :]:
        if not line.strip() or line.startswith("- "):
            break
        words.append(line.strip())
    return " ".join(words)


def decided(lines: list[str], shown: tuple[str, ...]) -> dict[str, str]:
    """What the plan says under each ID in the parts shown, such as the goal and each acceptance
    criterion, by its ID, in the order of the plan, each as one line; read from a plan that holds
    its form."""
    parts = sections(lines)
    found: dict[str, str] = {}
    for part in shown:
        held_lines = parts.get(part, [])
        for k, (_, line) in enumerate(held_lines):
            if line.startswith(SHOWS[part]):
                said = item(held_lines, k).removeprefix("- ")
                key, _, rest = said.partition(": ")
                found[key] = rest
    return found


def joined(ids: list[str]) -> str:
    """The IDs in words, the last after "and"."""
    *rest, last = ids
    return f"{', '.join(rest)} and {last}" if rest else last


def changes(before: dict[str, str] | None, now: dict[str, str]) -> list[str]:
    """The lines the proposal shows of the plan's IDs: each as it is, at the first proposal; then
    each changed or added, each removed, and the rest named as before."""
    if before is None:
        return [f"{key}: {said}" for key, said in now.items()]
    same = [key for key, said in now.items() if before.get(key) == said]
    return (
        [f"Changed: {key}: {said}" for key, said in now.items() if key not in same]
        + [f"Removed: {key}" for key in before if key not in now]
        + ([f"({joined(same)} as before)"] if same else [])
    )


def run_proposal(args: argparse.Namespace, root: str, today: datetime.date) -> str:
    """The proposal at the sign-off, made from what is pushed alone: the pull request's link and
    the plan's goal and acceptance criteria at the plan sign-off, the criteria alone at the
    deliverable's, with what changed since the last proposal at the same sign-off; kept as a commit
    marked with its sign-off. The same proposal again where the plan is as it was then. Stops where
    turn has not returned the plan, a change is not kept or pushed, or the plan is not there or out
    of its form."""
    signoff = args.signoff
    where, shown = SIGNOFFS[signoff]
    folder = current()
    # Asked before what is pushed, as turn's run keeps its own files beside the result until it
    # returns, which would read as changes not kept.
    result = ccs_path(folder, PLAN, "-result")
    if signoff in (PLAN,) and not os.path.isfile(result):
        raise Stop(
            f"rn: turn has not returned the plan: {result} is not there; have turn:up make it with"
            f" the call `rn.py ccs {PLAN} ...` printed, then run this again"
        )
    pushed()
    steering = plan(folder)
    if not os.path.isfile(steering):
        raise Stop(f"rn: the plan {steering} is not there; have turn make it, then run this again")
    said = out_of_form(steering, root)
    if said:
        raise Stop(
            f"rn: {said}; have turn make the plan again in that form, keep it with `rn.py state`,"
            " then run this again"
        )
    with open(steering, encoding="utf-8") as f:
        text = f.read()
    last = git(
        ["log", "-1", "--format=%H", "-E", f"--grep=^{SHOWN}{signoff}$", f"{base()}..HEAD"],
        AS_GIT_SAYS,
    ).strip()
    before = git(["show", f"{last}:{steering}"], AS_GIT_SAYS) if last else None
    if before == text:
        message = git(["log", "-1", "--format=%B", last], AS_GIT_SAYS)
        return message.rpartition(f"\n\n{SHOWN}")[0]
    then = None if before is None else decided(before.splitlines(), shown)
    proposal = "\n".join(
        [
            f"{signoff.capitalize()} sign-off",
            f"{where}: {front_matter(steering)['pr']}",
            *changes(then, decided(text.splitlines(), shown)),
            ANSWER,
        ]
    )
    fed = f"{proposal}\n\n{SHOWN}{signoff}"
    git(["commit", "-q", "--allow-empty", "-F", "-"], AS_GIT_SAYS, fed)
    push()
    return proposal


def learning() -> str:
    """The folder where the learner is shown the records and replies, in the repository's git
    folder, as a whole path."""
    return os.path.join(git(["rev-parse", "--absolute-git-dir"], AS_GIT_SAYS).strip(), LEARNING)


def project_folders(top: str) -> list[str]:
    """The folders where Claude Code keeps the records of conversations run at the path: the one
    named by it, or, where the name is longer than Claude Code keeps, each there named by its
    beginning and a hash."""
    name = "".join(
        c if c.isascii() and c.isalnum() else "-" * (len(c.encode("utf-16-le")) // 2) for c in top
    )
    kept = records.kept()
    if len(name) <= NAME_LENGTH:
        return [os.path.join(kept, name)]
    return sorted(
        glob.glob(os.path.join(glob.escape(kept), glob.escape(name[:NAME_LENGTH]) + "-*"))
    )


def lines(path: str) -> list[dict[str, Any]]:
    """Each entry of a record, as Claude Code keeps it, one JSON object to a line."""
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def begun(path: str) -> tuple[str, str]:
    """When the record began, its earliest entry's time, Claude Code writing each in one form; and
    its path, so records begun at once come in one order."""
    times = [e["timestamp"] for e in lines(path) if "timestamp" in e]
    return min(times, default=""), path


def conversations(top: str, branch: str) -> list[str]:
    """The record of each conversation run at the top of the repository that was on the branch at
    some entry, in the order they began."""
    found = [
        path
        for folder in project_folders(top)
        for path in glob.glob(os.path.join(glob.escape(folder), "*.jsonl"))
        if any(e.get("cwd") == top and e.get("gitBranch") == branch for e in lines(path))
    ]
    return sorted(found, key=begun)


def stretch(folder: str) -> str:
    """The commit the stretch the learner reads starts after: the last that kept the lessons of a
    stretch, or, where none did, the one the branch left the default branch at."""
    start = base()
    kept = git(
        ["log", "-1", "--format=%H", f"{start}..HEAD", "--", os.path.join(folder, LESSONS)],
        AS_GIT_SAYS,
    )
    return kept.strip() or start


def history(folder: str, start: str) -> str:
    """The session's history on the branch since the start, each command before what it printed:
    each commit, oldest first, with its message, which holds each feedback, answer and proposal
    shown, and the files it changed, so a change to the work made outside turn shows, without their
    lines, as the record gives the session's files as they are now; then each change to the state,
    under the commit that made it, which shows what each move rested on."""
    asked = [
        ["log", "--reverse", "--stat", f"{start}..HEAD"],
        ["log", "--reverse", "-p", "--format=%h", f"{start}..HEAD", "--", state_path(folder)],
    ]
    return "".join(f"$ {shlex.join(['git', *a])}\n{git(a, AS_GIT_SAYS)}\n" for a in asked)


def session_files(folder: str) -> list[str]:
    """The session's files the learner reads as they are now: the plan, each work's decisions and
    each result turn returned, each where it is there."""
    found = [plan(folder)] + sorted(
        glob.glob(os.path.join(glob.escape(folder), "decisions", "*.md"))
    )
    found += sorted(glob.glob(os.path.join(glob.escape(folder), "ccs", "*-result.json")))
    return [p for p in found if os.path.isfile(p)]


def since(entry: dict[str, Any], start: float) -> bool:
    """Whether the entry was kept at or after the time, in seconds since 1970; not where it has no
    time."""
    at = entry.get("timestamp")
    # Python 3.9 reads no `Z` for UTC, which Claude Code writes.
    return (
        at is not None
        and datetime.datetime.fromisoformat(at.replace("Z", "+00:00")).timestamp() >= start
    )


def told(path: str, start: float) -> str:
    """A conversation of the conductor as the learner searches it, from the time, in seconds since
    1970: the user's words, each skill's text, the conductor's words and each tool it called, one to
    a line; what each tool gave back is left out, as the record shows what was kept, and it is most
    of the conversation; "" where it holds none of them from the time."""
    said: list[str] = []
    for entry in (e for e in records.entries(path) if since(e, start)):
        content = entry.get("message", {}).get("content")
        if isinstance(content, str):
            said.append(f"[{entry.get('type')}] {content}")
        for part in content if isinstance(content, list) else []:
            if part.get("type") in ("text", "tool_use"):
                said.append(records.said(part))
    return "".join(f"{line}\n" for line in said)


def run_records(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Shows rn's learner one stretch of the session, from the sign-off before to the one the user
    just answered, once every change is pushed: its record, the history on the branch since the
    lessons of the stretch before were kept and the session's files as they are now, to read whole;
    then each conversation of the conductor, run at the top of the repository on the session's
    branch, from the time the stretch began, to search for what only it shows, none where Claude
    Code keeps none here, as when the session ran on another machine. Each is written as text in the
    git folder, made afresh, numbered in one list, the record first; what each stands for is kept
    there for the reply; and gives the learner's prompt. Stops where the branch holds no session, or
    a change is not kept or pushed."""
    folder = current()
    pushed()
    start = stretch(folder)
    began = float(git(["log", "-1", "--format=%ct", start], AS_GIT_SAYS))
    head = git(["rev-parse", "HEAD"], AS_GIT_SAYS).strip()
    top = git(["rev-parse", "--show-toplevel"], AS_GIT_SAYS).strip()
    branch = git(["branch", "--show-current"], AS_GIT_SAYS).strip()
    place = learning()
    shutil.rmtree(place, ignore_errors=True)
    # Each text shown, by where it is written, with what it stands for and its text.
    shown = [
        (os.path.join("record", "history.txt"), f"git log {start}..{head}", history(folder, start))
    ]
    shown += [(os.path.join("record", p), p, read_text(p)) for p in session_files(folder)]
    whole = len(shown)
    for path in conversations(top, branch):
        name = os.path.basename(path)[: -len(".jsonl")] + ".txt"
        text = told(path, began)
        if text:
            shown.append((os.path.join("conversations", name), path, text))
    for name, _, text in shown:
        os.makedirs(os.path.dirname(os.path.join(place, name)), exist_ok=True)
        with open(os.path.join(place, name), "w", encoding="utf-8") as f:
            f.write(records.wrapped(text))
    texts = [os.path.join(place, name) for name, _, _ in shown]
    write_json(
        os.path.join(place, "records.json"), {"texts": texts, "sources": [s for _, s, _ in shown]}
    )
    return {
        "record": texts[:whole],
        "conversations": texts[whole:],
        "reply": os.path.join(place, LEARNT),
    }


def run_learnt(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Keeps the learner's lessons on the stretch in the session, as the next stretch's number,
    a stretch of no lesson as well, so the next starts after it; each ground naming what its
    text stands for, a file of the session by its path, the history by its range of commits and
    a conversation by its record, as the texts it read by number go; removes what the learner
    was shown; and gives the lessons, with what it checked, for the conductor to put to the
    user. Stops where the branch holds no session, the session was not shown, the reply is not
    there, or the reply is out of its form, each quote found in the text it numbers, which is
    then removed, with the message that has the learner write it again."""
    folder = current()
    place = learning()
    kept = os.path.join(place, "records.json")
    if not os.path.isfile(kept):
        raise Stop(
            "rn: the session was not shown to the learner; run `rn.py records` first, start"
            " rn:learner with the prompt it prints, then run this again"
        )
    with open(kept, encoding="utf-8") as f:
        shown = json.load(f)
    reply = os.path.join(place, LEARNT)
    if not os.path.isfile(reply):
        raise Stop(
            f"rn: the learner's reply {reply} is not there; start rn:learner with the prompt"
            " `rn.py records` printed and wait for it to end, then run this again"
        )
    with open(reply, encoding="utf-8") as f:
        text = f.read()
    said = forms.check(text, [], [], forms.LEARNT, records=tuple(shown["texts"]), read=read_text)
    if said:
        os.remove(reply)
        fix = f"Write your reply to {reply} again in your form, filled:\n" + "\n".join(said)
        raise Stop(
            "rn: the learner's reply is out of its form; send rn:learner by SendMessage this"
            f" message as it is, wait for it to end, then run this again:\n{fix}"
        )
    data = json.loads(forms.unfenced(text))
    sources = shown["sources"]
    learnt = {
        "lessons": [
            dict(n, grounds=[dict(g, record=sources[g["record"] - 1]) for g in n["grounds"]])
            for n in data["lessons"]
        ],
        "checked": data["checked"],
    }
    numbers = [int(n) for n in kept_numbers(folder)]
    write_json(os.path.join(folder, LESSONS, f"{max(numbers, default=0) + 1}.json"), learnt)
    shutil.rmtree(place)
    return learnt


def kept_numbers(folder: str) -> list[str]:
    """The number of each stretch whose lessons the session keeps, in order."""
    names = (
        os.listdir(os.path.join(folder, LESSONS))
        if os.path.isdir(os.path.join(folder, LESSONS))
        else []
    )
    found = [m.group(1) for m in map(KEPT.fullmatch, names) if m]
    return sorted(found, key=int)


def run_lessons(args: argparse.Namespace, root: str, today: datetime.date) -> Any:
    """Every lesson the session keeps, stretch by stretch in their order, for the conductor to put
    to the user one per message once the finished work is approved. Stops where the branch holds no
    session, or no stretch's lessons are kept."""
    folder = current()
    numbers = kept_numbers(folder)
    if not numbers:
        raise Stop(
            f"rn: no lessons are kept in {os.path.join(folder, LESSONS)}; at each sign-off the user"
            " answered, run `rn.py records`, have rn:learner reply, run `rn.py learnt` and keep it"
            " with `rn.py state --message`"
        )
    lessons = []
    for n in numbers:
        with open(os.path.join(folder, LESSONS, f"{n}.json"), encoding="utf-8") as f:
            lessons += json.load(f)["lessons"]
    return {"lessons": lessons}


def read_text(path: str) -> str:
    """The text at the path, as the learner was shown it."""
    with open(path, encoding="utf-8") as f:
        return f.read()


class Parser(argparse.ArgumentParser):
    """argparse, stopping as rn stops rather than exiting with its own code."""

    def error(self, message: str) -> NoReturn:
        # The usage on one line, as argparse breaks a long one where a terminal would.
        usage = " ".join(self.format_usage().split()[1:])
        raise Stop(f"rn: {message}; give it as {usage}")


def parser() -> Parser:
    """The subcommands, each with what it takes and the function that runs it."""
    top = Parser(prog="rn.py")
    sub = top.add_subparsers(dest="subcommand", required=True)
    sub.add_parser("session").set_defaults(run=run_session)
    start = sub.add_parser("start")
    start.set_defaults(run=run_start)
    start.add_argument("slug")
    start.add_argument("--message", required=True)
    state = sub.add_parser("state")
    state.set_defaults(run=run_state)
    state.add_argument("--message", required=True)
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
    ccs.add_argument("--has", required=True, action="append")
    proposal = sub.add_parser("proposal")
    proposal.set_defaults(run=run_proposal)
    proposal.add_argument("signoff", choices=list(SIGNOFFS))
    sub.add_parser("records").set_defaults(run=run_records)
    sub.add_parser("learnt").set_defaults(run=run_learnt)
    sub.add_parser("lessons").set_defaults(run=run_lessons)
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
