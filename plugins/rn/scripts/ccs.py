"""What a work's CCS holds, its decisions with the rest, so the work is made from the session's
record alone, by turn or, for the plan and the learnings, by the orchestrator: each decision kept,
the checklists of its kind, before the build without the questions judged on the built product, and
the questions asked of each part of the work, what its receiver has, the goal and the criteria it
serves, the finished work's files, and for the plan what each task done served, decided and made;
and the CCS written and handed to its maker."""

from __future__ import annotations

import glob
import os
import shlex
from typing import Any, NamedTuple

import call
import items
import repo
import session
import steering
import stop
import template

# For each role turn reads from a CCS, the key of the CCS entries that hold it; the call to turn:up
# hands this table to turn.
ENTRIES = {
    "work": "path",
    "checklist": "checklist",
    "receiver": "audience",
    "use": "purpose",
    "has": "has",
    "each": "each",
}
# The key of the CCS entries each holding a goal or a criterion the work serves.
SERVES = "serves"
# The key of the CCS entry naming the kind of the work, whose checklists it is made with.
KIND = "kind"
# How rn uses each of its own checklists, which it tells turn as their caller, as a checklist holds
# its questions alone (rn's checklist for checklists): rn's checklist of every document, given
# beside the checklist of each kind of document, those kinds of rn's own checklists that are
# documents, the plan's left out until its checklist is made again without what doc.md asks; the
# questions of each checklist that can be judged only on the built product, and those asked of each
# part of the work, by the checklist's path in rn's checklists.
DOC = "doc.md"
DOCUMENTS = (
    "architecture",
    "checklist",
    "issue",
    "learnings",
    "prompt",
    "readme",
    "research",
    "trial",
    "ux",
)
BUILT: dict[str, tuple[str, ...]] = {"product/readme.md": ("Q-4", "Q-5", "Q-6")}
EACH: dict[str, tuple[str, ...]] = {
    DOC: ("Q-3", "Q-6", "Q-7", "Q-8", "Q-10"),
    "product/code.md": ("Q-4", "Q-5"),
    "product/prompt.md": ("Q-10",),
    "product/ux.md": ("Q-6",),
    "session/research.md": ("Q-3",),
}
# The stages before the build, whose works are made before the product is there to judge them on;
# the headings that end an item, those of its level and above; and the name of a call's copy of the
# k-th checklist of its kind.
BEFORE_BUILD = (steering.GOAL, steering.UX, steering.ARCHITECTURE)
ITEM = 3
COPY = "checklist-{}.md"
# The kind of a checklist, and rn's own checklist for it, its checklist for checklists.
CHECKLIST = "checklist"
META = "meta.md"
# The works rn makes the same way every time, each with its kind, its receiver and their use: the
# plan, the learnings and the finished work.
OWN = {
    steering.PLAN: (
        "plan",
        (
            "the user at the goal sign-off, approving what the finished work will do and why, and"
            " rn's orchestrator in any later conversation, carrying the work on without asking"
            " them again"
        ),
        "approving the goal and the acceptance criteria, then carrying each later work to them",
    ),
    steering.LEARNINGS: (
        "learnings",
        "the user deciding each learning once the finished work is approved",
        (
            "deciding where each learning goes: their checklists, an issue to rn's makers, both,"
            " or neither"
        ),
    ),
    steering.DELIVERABLE: (
        "deliverable",
        "the user at the deliverable sign-off",
        "checking that the finished work does each acceptance criterion",
    ),
}


class Made(NamedTuple):
    """How a work is made, as far as rn knows it before the orchestrator gives the rest: the kind,
    its receiver and their use, the paths it is, and what the receiver has; None, or none, for each
    rn does not know."""

    kind: str | None
    receiver: str | None
    use: str | None
    paths: list[str]
    has: list[str]


def made_as(work: str, steered: steering.Steering) -> Made:
    """How rn makes the work every time: one of its own as OWN and `checklist-<kind>` have it, what
    the receiver has the whole repository; a task's work of the kind, at the path, its action
    names, the rest given or kept; the paths of the plan, the learnings and the finished work are
    found as their CCS is written."""
    if work in OWN:
        kind, receiver, use = OWN[work]
        return Made(kind, receiver, use, [], ["."])
    if session.CHECKLIST_WORK.fullmatch(work):
        made = work.partition("-")[2]
        a = "an" if made.startswith(tuple("aeiou")) else "a"
        return Made(
            CHECKLIST,
            f"whoever makes {a} {made} work in this repository and whoever judges it",
            f"making and judging each {made} work",
            [os.path.join(session.RECORD, "checklists", f"{made}.md")],
            ["."],
        )
    action = session.made_by(steered, work)
    return Made(action.kind, None, None, [action.path or ""], [])


def kept_as(last: session.Call | None) -> Made:
    """How the work was made in its latest call, as its CCS names it; none of it where it has
    none."""
    ccs = {} if last is None else last.ccs
    first = {name: next(iter(call.entries(ccs, key)), None) for name, key in ENTRIES.items()}
    return Made(
        next(iter(call.entries(ccs, KIND)), None),
        first["receiver"],
        first["use"],
        call.entries(ccs, ENTRIES["work"]),
        call.entries(ccs, ENTRIES["has"]),
    )


def rns_own(kind: str, root: str) -> list[str]:
    """rn's own checklist for the kind, in any folder of rn's checklists, its checklist for
    checklists for a checklist; none where rn has none."""
    name = META if kind == CHECKLIST else f"{kind}.md"
    return sorted(glob.glob(os.path.join(root, "checklists", "**", name), recursive=True))


def checklists(kind: str, root: str) -> list[str]:
    """The checklists for the kind: rn's own, then rn's checklist of every document where the kind
    is one of rn's kinds of document, then the user's addition; stops where neither rn's own nor the
    addition is there."""
    own = rns_own(kind, root)
    added = os.path.join(session.RECORD, "checklists", f"{kind}.md")
    addition = [added] if os.path.isfile(added) else []
    if not own + addition:
        raise stop.Stop(
            f"rn: there is no checklist for the kind {kind}, neither rn's nor {added}; make"
            f" {added} first, as a work of its own to rn's checklist for checklists"
        )
    doc = [os.path.join(root, "checklists", DOC)] if kind in DOCUMENTS else []
    return own + doc + addition


def asked(path: str, root: str, told: dict[str, tuple[str, ...]]) -> tuple[str, ...]:
    """The questions the table tells of the checklist at the path, by its path in rn's checklists,
    rn installed at root; none for any other checklist, such as the user's addition."""
    return told.get(os.path.relpath(path, os.path.join(root, "checklists")), ())


def unbuilt(text: str, built: tuple[str, ...]) -> str:
    """The checklist's text without each question of the IDs, judged on the built product, from its
    heading to the next heading of its level or above outside a code fence, or the end."""
    lines = text.splitlines()
    cut = {n for n, found in items.items(text) if found in built}
    heads = {n for n, level, _ in template.headings(lines, template.body(lines)) if level <= ITEM}
    kept, cutting = [], False
    for number, line in enumerate(lines, 1):
        cutting = number in cut if number in heads else cutting
        if not cutting:
            kept.append(line)
    return "\n".join(kept).rstrip() + "\n"


def judged(
    lists: list[str], stage: str, folder: str, number: str, root: str
) -> list[tuple[str, str | None, list[str]]]:
    """Each checklist the call of the number names, made at the stage, with the text to write there,
    and the questions of it asked of each part of the work, each as `<path> <ID>`, the CCS entry
    turn reads them by: before the build, a copy of each whose questions BUILT tells of, judged on
    the built product, without those questions, beside the call's CCS, as COPY names it by its place
    among the kind's checklists; each other checklist, and every one from the build on, as it is,
    with no text. rn is installed at root."""
    found: list[tuple[str, str | None, list[str]]] = []
    for place, path in enumerate(lists, 1):
        built = asked(path, root, BUILT) if stage in BEFORE_BUILD else ()
        cut = unbuilt(repo.read_text(path), built) if built else None
        named = path if cut is None else session.call_path(folder, number, COPY.format(place))
        found.append((named, cut, [f"{named} {q}" for q in asked(path, root, EACH)]))
    return found


def has_path(path: str) -> str:
    """The path of what the receiver has with the work, when a file or folder is there; stops
    otherwise, as turn stops a call naming one that is not."""
    if not os.path.exists(path):
        raise stop.Stop(
            f"rn: what the receiver has, {path}, is not there; give the path of a file or folder"
            " they have with the work, from the top"
        )
    return path


def finished_work() -> list[str]:
    """Each file the branch changed since it left the default branch outside `.rn/`, in the order
    of their paths, which is the finished work; a file it removed is not, as it is not there to
    use. Stops where there is none."""
    paths = repo.git(
        [
            "diff",
            "--name-only",
            "--diff-filter=d",
            repo.base(),
            "HEAD",
            "--",
            f":(exclude){session.RECORD}",
        ],
        repo.AS_GIT_SAYS,
    ).splitlines()
    if not paths:
        raise stop.Stop(
            f"rn: the branch changed no file outside {session.RECORD}/ since it left"
            f" {repo.default_branch()}, so there is no finished work to name; have each task made"
            " and kept, or give the work's paths, then run this again"
        )
    return paths


def served(steered: steering.Steering, work: str) -> dict[str, str]:
    """The goal and each criterion the work serves, by ID, as the steering says each on one line:
    those its task's line names for a task's work; the goal and every criterion for the finished
    work, which is checked for each; none for any other, the plan making them, and the learnings
    and a checklist serving none of the user's work. Stops where the steering holds no task of a
    task's work."""
    said = steering.decided(steered.plan)
    if work == steering.DELIVERABLE:
        return said
    if not session.TASK_WORK.fullmatch(work):
        return {}
    session.made_by(steered, work)
    task = {t.id: t for t in steering.tasks_of(steered.plan)}[session.task_of(work)]
    return {key: text for key, text in said.items() if key in (task.serves or [])}


def test_of(steered: steering.Steering, work: str, number: str, root: str) -> str | None:
    """The command that checks the work, for the call of the number that makes it: for a part the
    orchestrator writes, the plan or the learnings, rn.py's check of it as `state --put` holds it,
    run by rn where it is installed at root, as no task's command is for those; the one the
    completion criterion of the work's task names, where it is one, for the task's last action of
    turn's, which makes its result, the actions of turn's before it making the check and seeing it
    fail; None for any other work."""
    if work in session.PARTS:
        return f"python3 {shlex.quote(os.path.join(root, 'scripts', 'rn.py'))} check {number}"
    task = {t.id: t for t in steering.tasks_of(steered.plan)}.get(session.task_of(work))
    if task is None or not task.tests:
        return None
    # The form holds one command at most, and the work, of an action of turn's, one action at least.
    [(_, _, command)] = task.tests
    *_, last = [a.number for _, _, a in task.actions if a is not None and a.path is not None]
    return {f"{task.id.lower()}.{last}": command}.get(work)


def done_made(folder: str, found: list[session.Call], plan: list[str]) -> list[str]:
    """The CCS of the latest call of each work of a task the plan no longer holds, done, in the
    order those calls were made: what the task served and decided, and the files it made, which
    is what the plan is made again from; turn's results are left out, as what they hold beside the
    work, the lines of each item's Good, changes no task."""
    left = [task.id for task in steering.tasks_of(plan)]
    last = {c.work: c.number for c in found}
    return [
        session.call_path(folder, number, session.CCS)
        for work, number in sorted(last.items(), key=lambda item: item[1])
        if session.task_of(work) and session.task_of(work) not in left
    ]


def choice(given: str) -> str:
    """The choice the orchestrator gives, `<what it chose>: <why>`; stops where either is
    missing."""
    what, colon, why = given.partition(": ")
    if not (colon and what.strip() and why.strip()):
        raise stop.Stop(
            f'rn: the choice {given!r} is not "<what you chose>: <why>"; give what you chose, then'
            " `: `, then why"
        )
    return given


def chosen_with(kept: list[str], given: list[str]) -> list[str]:
    """The choices a call keeps: those its work's latest call kept, each one given of the same what
    replacing it where it stands, then the others given."""
    found = {c.partition(": ")[0]: c for c in kept}
    found.update({c.partition(": ")[0]: c for c in given})
    return list(found.values())


def needed(value: Any, what: str, work: str) -> Any:
    """The value, when the work has it; stops where it has none, saying how to give it."""
    if not value:
        raise stop.Stop(
            f"rn: no {what} of the work {work} is given, and no call on it names one; give it with"
            f" --{what}"
        )
    return value


def written(
    work: str,
    steered: steering.Steering,
    made: Made,
    serving: dict[str, str],
    checklists: list[str],
    each: list[str],
    decisions: list[str],
    chosen: list[str],
    root: str,
) -> dict[str, list[dict[str, str]]]:
    """The work's CCS, in four parts, the shape turn takes: focal_entities, what the work is about,
    the work by its name, the stage it is made in, its kind, its paths, its receiver and what they
    have with it; goal_orientation, what the work is for, its use and what it serves as text, as its
    maker makes the work from the CCS and the files it names alone; retrieved_artifacts, the kind's
    checklists and the questions of them asked of each part of the work; and constraints, the bounds
    it is made in: its decisions, the orchestrator's choices, the languages, and rn's checklist for
    a fix, which its maker is given to read, as each file a CCS names is, for a work made again.
    turn finds each entry by its key, whichever part holds it."""
    return {
        "focal_entities": [
            {session.WORK: work},
            {steering.STAGE: steered.keys[steering.STAGE]},
            {KIND: made.kind or ""},
        ]
        + [{ENTRIES["work"]: p} for p in made.paths]
        + [{ENTRIES["receiver"]: made.receiver or ""}]
        + [{ENTRIES["has"]: p} for p in made.has],
        "goal_orientation": [{ENTRIES["use"]: made.use or ""}]
        + [{SERVES: f"{key}: {text}"} for key, text in serving.items()],
        "retrieved_artifacts": [{ENTRIES["checklist"]: p} for p in checklists]
        + [{ENTRIES["each"]: e} for e in each],
        "constraints": [{session.DECISION: d} for d in decisions]
        + [{session.CHOSEN: c} for c in chosen]
        + [{key: steered.keys[key]} for key in steering.LANGUAGES]
        + [{"fix": os.path.join(root, "checklists", "fix.md")}],
    }


def told(work: str, steered: steering.Steering) -> str:
    """The line telling the user what turn makes, and that it is used in their place before it
    comes back, which they can stop: every work but the plan and the learnings, which the
    orchestrator writes."""
    if work == steering.DELIVERABLE:
        words = "the use of the finished work for each acceptance criterion"
    elif session.CHECKLIST_WORK.fullmatch(work):
        words = f"your checklist for {work.partition('-')[2]}"
    else:
        words = f"{work.upper()}, {steering.lowered(session.made_by(steered, work).what)}"
    return (
        f"turn makes {words}, and an AI that did not make it uses it in your place before it comes"
        " back; say stop to stop it."
    )


def decide(work: str, title: str, says: str, message: str) -> dict[str, str]:
    """Writes a decision of the work, `<title>: <what it says>`, in the constraints of its latest
    call where that call takes more, else of a new call carrying its decisions, one of the same
    title replaced where it stands, as session.Call says, and, where its words change, added to the
    session's record of decisions replaced; kept as a move its step goes on after, as
    session.written says, the step's commit taking it. Gives the call's number. Stops where the
    branch holds no session, the steering differs
    from what the last keep left, the steering holds no action of turn's of a task's work, or a CCS
    is no JSON object; and where git fails."""
    folder = session.current()
    steered = session.kept_steering(folder)
    if session.task_of(work):
        session.made_by(steered, work)
    found = session.calls(folder)
    last = session.latest(found, work)
    if last is not None and not last.closed:
        number, ccs = last.number, last.ccs
    else:
        number = session.next_number(found)
        carried = [] if last is None else session.decisions_of(last)
        ccs = {
            "focal_entities": [
                {session.WORK: work},
                {steering.STAGE: steered.keys[steering.STAGE]},
            ],
            "constraints": [{session.DECISION: d} for d in carried]
            + [{session.CHOSEN: c} for c in session.choices_of(last)],
        }
    constraints = ccs.setdefault("constraints", [])
    decision = {session.DECISION: f"{title}: {says}"}
    same = next(
        (
            k
            for k, e in enumerate(constraints)
            if e.get(session.DECISION, "").startswith(f"{title}: ")
        ),
        None,
    )
    if same is None:
        constraints.append(decision)
    else:
        was = constraints[same][session.DECISION]
        if was != decision[session.DECISION]:
            changed = {"work": work, "was": was, "now": decision[session.DECISION]}
            repo.add_line(session.replaced_path(folder), changed)
        constraints[same] = decision
    repo.write_json(session.call_path(folder, number, session.CCS), ccs)
    session.written(folder, steered, message)
    return {"call": number}


def handed(
    work: str,
    paths: list[str],
    receiver: str | None,
    use: str | None,
    given_has: list[str],
    chosen: list[str],
    root: str,
) -> dict[str, Any] | str:
    """Writes the work's CCS into the session, kept as a move its step goes on after, as
    session.written says, so the work is made from decisions a fresh conversation also has: in the
    work's latest call where that call takes more, else in a new one carrying its decisions, as
    session.Call says. For the plan and the
    learnings, which the orchestrator writes, the part is cut into the call, and gives the part, the
    CCS, the checklists it names and the command that checks the part; for every other work, the
    call that hands it to turn:up, so a conversation cut while turn runs goes on from it, and the
    line telling the user what turn makes. The CCS names the kind's checklists as judged gives them,
    before the build each holding a question judged on the built product by a copy written beside
    it, and the questions of them asked of each part of the work.
    What is given makes the work, each choice of the orchestrator's given kept with those of the
    latest call, one of the same what replaced; what is not, rn's own way of making it, or what the
    work's latest call named, as made_as and kept_as say: for the plan, its part of the steering,
    with what each task done served and made after what the receiver has; for the learnings, an
    empty part, as those kept are not made again; for the finished work given none, every file it
    is. rn is installed at root. Stops, writing nothing, where a path of what the receiver has is
    not there, the branch holds no session, the steering differs
    from what the last keep left, the steering holds no action of turn's of a task's work, the
    receiver, their use or what they have is neither given nor kept, the kind has no checklist, or
    the finished work is not there."""
    # The session is found first, which stops below the top of the repository, since each path
    # given is read from the top.
    folder = session.current()
    has = [has_path(p) for p in given_has]
    steered = session.kept_steering(folder)
    serving = served(steered, work)
    found = session.calls(folder)
    last = session.latest(found, work)
    number = last.number if last is not None and not last.closed else session.next_number(found)
    made, kept = made_as(work, steered), kept_as(last)
    receiver = needed(receiver or made.receiver or kept.receiver, "receiver", work)
    use = needed(use or made.use or kept.use, "use", work)
    has = needed(has or made.has or kept.has, "has", work)
    kind = made.kind or ""
    named = judged(checklists(kind, root), steered.keys[steering.STAGE], folder, number, root)
    lists = [path for path, _, _ in named]
    part = session.call_path(folder, number, session.PART[work]) if work in session.PARTS else ""
    paths = ([part] if part else paths) or made.paths or finished_work()
    if work == steering.PLAN:
        has += done_made(folder, found, steered.plan)
    # Every check is made above, so a stop leaves nothing written.
    if part:
        repo.write_text(part, session.cut(work, steered))
    for path, text, _ in named:
        if text is not None:
            repo.write_text(path, text)
    ccs = written(
        work,
        steered,
        Made(kind, receiver, use, paths, has),
        serving,
        lists,
        [one for _, _, each in named for one in each],
        [] if last is None else session.decisions_of(last),
        chosen_with(session.choices_of(last), chosen),
        root,
    )
    path = session.call_path(folder, number, session.CCS)
    repo.write_json(path, ccs)
    test = test_of(steered, work, number, root)
    if part:
        said = f"Call {number} on {work}: its part cut for the orchestrator to write"
        session.written(folder, steered, said)
        return {"part": part, "ccs": path, "checklists": lists, "check": test}
    session.written(folder, steered, f"Call {number} on {work}: handed to turn")
    # turn's call takes the table of keys under "kind", a field name of turn's own that is no kind
    # of work; and the command that checks the work under "test", null where there is none.
    result = session.call_path(folder, number, session.RESULT)
    call_line = {"ccs": path, "kind": ENTRIES, "result": result, "test": test}
    return f"{repo.dumped(call_line)}\n{told(work, steered)}"


def decisions(work: str, root: str) -> dict[str, Any]:
    """Each decision of the work, as its latest call keeps it, with that call's number; none, and no
    call, where it has none; and the checklists of its kind whole, as its CCS names them from the
    build on, so the hearing reads each question before the work is made; rn is installed at root.
    Stops where the branch holds no session, the steering differs from what the last keep left, the
    steering holds no action of turn's of a task's work, or the kind has no checklist."""
    folder = session.current()
    steered = session.kept_steering(folder)
    last = session.latest(session.calls(folder), work)
    return {
        "work": work,
        "call": None if last is None else last.number,
        "decisions": [] if last is None else session.decisions_of(last),
        "checklists": checklists(made_as(work, steered).kind or "", root),
    }
