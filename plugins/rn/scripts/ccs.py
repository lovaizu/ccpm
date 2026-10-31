"""What a work's CCS holds, so the work is made from the session's record alone, by turn or, for the
plan and the learnings, by the orchestrator: what the record settles, copied by rn's scripts, each
decision kept, what the work serves, the results it builds on, the checklists of its kind, before
the build without the questions judged on the built product, and the questions asked of each part
of the work, the stage and the languages; for a task's result, what needs judgment, given by the
compressor with why, held to its form; and the CCS written and handed to its maker."""

from __future__ import annotations

import glob
import json
import os
import shlex
from typing import Any, NamedTuple

import call
import items
import repo
import schema
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
# The keys of the CCS entries holding what the work serves: its task and each completion criterion,
# for a task's result, and each goal or criterion it serves.
TASK = "task"
COMPLETION = "completion_criterion"
SERVES = "serves"
# The key of the CCS entry naming the kind of the work, whose checklists it is made with, and of the
# one holding the command that checks it, where there is one.
KIND = "kind"
TEST = "test"
# How rn uses each of its own checklists, which it tells turn as their caller, as a checklist holds
# its questions alone (rn's checklist for checklists): rn's checklist of every document, given
# beside the checklist of each kind of document, those kinds of rn's own checklists that are
# documents; the questions of each checklist that can be judged only on the built product, and
# those asked of each part of the work, by the checklist's path in rn's checklists.
DOC = "doc.md"
DOCUMENTS = (
    "architecture",
    "checklist",
    "issue",
    "learnings",
    "plan",
    "prompt",
    "readme",
    "research",
    "trial",
    "ux",
)
BUILT: dict[str, tuple[str, ...]] = {"product/readme.md": ("Q-4", "Q-6", "Q-7")}
EACH: dict[str, tuple[str, ...]] = {
    DOC: ("Q-3", "Q-6", "Q-7", "Q-8", "Q-10", "Q-14"),
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
# The receiver of a task's result before the build, and their use, as rn's scripts name them: the
# user approving it at the stage's sign-off and whoever builds to it, who have the plan and the
# documents made before it.
BEFORE_RECEIVER = (
    "the user approving it at the {} sign-off, and whoever builds the later works to it"
)
BEFORE_USE = "approving it, then building each later work to it"
# The compressor's reply, held to its form, and the roles it gives of a task's CCS: before the
# build, where the result goes, its kind, any other file the receiver has, and the command that
# checks it; from the build on, the receiver and their use too.
COMPRESSOR_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "forms", "compressor.json"
)
with open(COMPRESSOR_PATH, encoding="utf-8") as _f:
    COMPRESSOR: dict[str, Any] = json.load(_f)
GIVEN_BEFORE = ("work", "kind", "has", "test")
GIVEN_BUILT = ("work", "kind", "receiver", "use", "has", "test")
# The roles the reply may give more than once, a path each, the others once; and those it may leave
# out, has, where what the record settles is all the receiver has.
MANY = ("work", "has")
HAS = "has"
OPTIONAL = (HAS,)
# How each choice of the compressor's is kept in the CCS, for the sign-off to show it with why.
SAID = {
    "work": "The result is made at {}",
    "kind": "It is made as a {} work",
    "receiver": "Its receiver is {}",
    "use": "They use it for {}",
    "has": "The receiver has {}",
    "test": "The command `{}` checks it",
}
NO_TEST = "No command of the project checks it"
# The roles of a reply, as reply_of gives them: each role given with each value and why.
Roles = dict[str, list[tuple[Any, str]]]


class Made(NamedTuple):
    """How a work is made: the kind, its receiver and their use, the paths it is, what the receiver
    has and the command that checks it; None, or none, for each not known yet."""

    kind: str | None
    receiver: str | None
    use: str | None
    paths: list[str]
    has: list[str]
    test: str | None = None


def results_of(found: list[session.Call], task_ids: list[str]) -> list[str]:
    """The paths of the result of each task of the IDs, as its latest call names them, in the order
    of the IDs."""
    paths: list[str] = []
    for task_id in task_ids:
        last = session.latest(found, task_id.lower())
        paths += [] if last is None else call.entries(last.ccs, ENTRIES["work"])
    return paths


def settled_as(work: str, steered: dict[str, Any], folder: str, found: list[session.Call]) -> Made:
    """How the record settles the work: one of rn's own as OWN and `checklist-<kind>` have it, what
    the receiver has the whole repository; a task's result, before the build, with its receiver,
    their use and what they have, the plan's Markdown and the result of each task done, as rn's
    scripts name them, and from the build on, the result of each task it builds on; the rest given
    by the compressor. Stops where the plan holds no task of a task's result, or a task it builds on
    is not done."""
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
    task = session.task_in(steered, work)
    done = session.done_tasks(folder, steered["plan"], found)
    left = [i for i in task["builds_on"] if i not in done]
    if left:
        raise stop.Stop(
            f"rn: {task['id']} builds on {stop.joined(left)}, which turn has not yet made and the"
            f" plan still holds; carry out {stop.joined(left)} first, then run this again"
        )
    stage = steered["status"]["stage"]
    if stage in BEFORE_BUILD:
        made_before = list(
            dict.fromkeys(session.task_of(c.work) for c in found if session.task_of(c.work) in done)
        )
        has = [session.markdown_path(folder), *results_of(found, made_before)]
        return Made(None, BEFORE_RECEIVER.format(stage), BEFORE_USE, [], has)
    return Made(None, None, None, [], results_of(found, task["builds_on"]))


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
            f"rn: what the receiver has, {path}, is not there; have the compressor give the path of"
            " a file or folder they have with the work, from the top"
        )
    return path


def work_path(path: str) -> str:
    """The path a result is made at, when it lies inside the repository, given from its top; stops
    otherwise, as turn writes only within the paths the CCS names."""
    if os.path.isabs(path) or os.path.normpath(path).split(os.sep)[0] == os.pardir:
        raise stop.Stop(
            f"rn: the result's path {path} leads out of the repository; have the compressor give a"
            " path inside it, from the top"
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
            " and kept, then run this again"
        )
    return paths


def served(steered: dict[str, Any], work: str) -> list[dict[str, str]]:
    """What the work serves, as CCS entries: for a task's result, its task, each completion
    criterion, and each criterion those serve, as the plan says it; each goal and every criterion
    for the finished work, which is checked for each; none for any other, the plan making them,
    and the learnings and a checklist serving none of the user's work. Stops where the plan holds
    no task of a task's result."""
    said = steering.decided(steered["plan"])
    if work == steering.DELIVERABLE:
        return [{SERVES: f"{key}: {text}"} for key, text in said.items()]
    if not session.TASK_WORK.fullmatch(work):
        return []
    task = session.task_in(steered, work)
    criteria = task["completion_criteria"]
    ids = list(dict.fromkeys(i for c in criteria for i in c["contributes_to"]))
    return (
        [{TASK: f"{task['id']}: {task['what']}"}]
        + [{COMPLETION: c["what"]} for c in criteria]
        + [{SERVES: f"{i}: {said[i]}"} for i in ids]
    )


def done_made(folder: str, found: list[session.Call], plan: dict[str, Any]) -> list[str]:
    """The CCS of the latest call of each task done, in the order those calls were made: what the
    task served and decided, and the files it made, which is what the plan is made again from;
    turn's results are left out, as what they hold beside the work, the lines of each item's Good,
    changes no task."""
    done = session.done_tasks(folder, plan, found)
    last = {c.work: c.number for c in found}
    return [
        session.call_path(folder, number, session.CCS)
        for work, number in sorted(last.items(), key=lambda item: item[1])
        if session.task_of(work) in done
    ]


def reply_of(text: str, give: tuple[str, ...]) -> dict[str, Any]:
    """The compressor's reply, held to forms/compressor.json: the point it returns, as it gave it;
    or each role it gave with each value and why, every role of those to give, has where it gives
    one, each of those given once once, no other, and test alone null. Stops otherwise, saying to
    start the compressor again."""
    again = "; start the compressor again with what `rn.py ccs <work>` printed, telling it so"
    try:
        data = json.loads(text)
    except ValueError:
        raise stop.Stop(f"rn: the compressor's reply is no JSON{again}") from None
    found = schema.held(COMPRESSOR, data)
    if found:
        raise stop.Stop(f"rn: the compressor's reply is out of its form: {found.told()}{again}")
    if "point" in data:
        return data
    roles: Roles = {}
    for choice in data["given"]:
        roles.setdefault(choice["role"], []).append((choice["value"], choice["why"]))
    for role, values in roles.items():
        if role not in give:
            raise stop.Stop(
                f"rn: the compressor gave {role}, which the record settles for this work; it gives"
                f" {stop.joined(list(give))} alone{again}"
            )
        if role not in MANY and values[1:]:
            raise stop.Stop(
                f"rn: the compressor gave {role} more than once, a role it gives once{again}"
            )
        if role != TEST and any(value is None for value, _ in values):
            raise stop.Stop(
                f"rn: the compressor gave {role} as null, which test alone may be; give it{again}"
            )
    left = [role for role in give if role not in roles and role not in OPTIONAL]
    if left:
        raise stop.Stop(f"rn: the compressor gave no {stop.joined(left)}{again}")
    return roles


def chosen_of(roles: Roles) -> list[str]:
    """Each choice of the compressor's as the CCS keeps it, `<what was chosen>: <why>`, in the order
    of the roles."""
    return [
        f"{NO_TEST if value is None else SAID[role].format(value)}: {why}"
        for role in GIVEN_BUILT
        for value, why in roles.get(role, [])
    ]


def given_made(settled: Made, roles: Roles) -> Made:
    """How a task's result is made: what the record settles, and what the compressor gave, each
    path and the kind checked as it comes in. Stops where a path leads out of the repository, what
    the receiver has is not there or none is, or the kind is not a name."""
    first = {role: next(iter(values))[0] for role, values in roles.items() if role not in MANY}
    has = [*settled.has, *(has_path(value) for value, _ in roles.get(HAS, []))]
    if not has:
        raise stop.Stop(
            "rn: no file the receiver has is named, by the record or by the compressor; start the"
            " compressor again with what `rn.py ccs <work>` printed, telling it to give each file"
            " the receiver has as has"
        )
    return Made(
        stop.named(first["kind"], "kind"),
        first.get("receiver", settled.receiver),
        first.get("use", settled.use),
        [work_path(value) for value, _ in roles["work"]],
        list(dict.fromkeys(has)),
        first["test"],
    )


def written(
    work: str,
    steered: dict[str, Any],
    made: Made,
    serving: list[dict[str, str]],
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
    it is made in: its decisions, the choices made for it with why, the command that checks it, the
    languages, and rn's checklist for a fix, which its maker is given to read, as each file a CCS
    names is, for a work made again. turn finds each entry by its key, whichever part holds it."""
    languages = steered["session"]["languages"]
    return {
        "focal_entities": [
            {session.WORK: work},
            {session.STAGE: steered["status"]["stage"]},
            {KIND: made.kind or ""},
        ]
        + [{ENTRIES["work"]: p} for p in made.paths]
        + [{ENTRIES["receiver"]: made.receiver or ""}]
        + [{ENTRIES["has"]: p} for p in made.has],
        "goal_orientation": [{ENTRIES["use"]: made.use or ""}, *serving],
        "retrieved_artifacts": [{ENTRIES["checklist"]: p} for p in checklists]
        + [{ENTRIES["each"]: e} for e in each],
        "constraints": [{session.DECISION: d} for d in decisions]
        + [{session.CHOSEN: c} for c in chosen]
        + ([] if made.test is None else [{TEST: made.test}])
        + [
            {"artifact-language": languages["artifact"]},
            {"conversation-language": languages["conversation"]},
            {"fix": os.path.join(root, "checklists", "fix.md")},
        ],
    }


def told(work: str, steered: dict[str, Any]) -> str:
    """The line telling the user what turn makes, and that it is used in their place before it
    comes back, which they can stop: every work but the plan and the learnings, which the
    orchestrator writes."""
    if work == steering.DELIVERABLE:
        words = "the use of the finished work for each acceptance criterion"
    elif session.CHECKLIST_WORK.fullmatch(work):
        words = f"your checklist for {work.partition('-')[2]}"
    else:
        task = session.task_in(steered, work)
        words = f"{task['id']}, {steering.lowered(steering.clause(task['what']))}"
    return (
        f"turn makes {words}, and an AI that did not make it uses it in your place before it comes"
        " back; say stop to stop it."
    )


def decide(work: str, title: str, says: str, message: str) -> dict[str, str]:
    """Writes a decision of the work, `<title>: <what it says>`, in the constraints of its latest
    call where that call takes more, else of a new call carrying its decisions and choices, one of
    the same title replaced where it stands, as session.Call says, and, where its words change,
    added to the session's record of decisions replaced; kept as a move its step goes on after, as
    session.written says, the step's commit taking it. Gives the call's number. Stops where the
    branch holds no session, the steering differs from what the last keep left, the plan holds no
    task of a task's result, or a CCS is no JSON object; and where git fails."""
    folder = session.current()
    steered = session.kept_steering(folder)
    if session.task_of(work):
        session.task_in(steered, work)
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
                {session.STAGE: steered["status"]["stage"]},
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


def settled_print(
    work: str,
    steered: dict[str, Any],
    folder: str,
    found: list[session.Call],
    ccs: dict[str, list[dict[str, str]]],
) -> dict[str, Any]:
    """What the compressor is started with for a task's result: the work, what the record settles
    of its CCS, the roles it gives, and the files it reads them from beside the repository, the
    steering, the plan's latest call, holding the decisions asked while planning, the latest call
    of each task done, and the work's own latest call, null for each not there."""
    stage = steered["status"]["stage"]
    planned = session.latest(found, steering.PLAN)
    last = session.latest(found, work)
    return {
        "work": work,
        "settled": ccs,
        "give": list(GIVEN_BEFORE if stage in BEFORE_BUILD else GIVEN_BUILT),
        "steering": session.steering_path(folder),
        "plan": None if planned is None else session.call_path(folder, planned.number, session.CCS),
        "made": done_made(folder, found, steered["plan"]),
        "latest": None if last is None else session.call_path(folder, last.number, session.CCS),
    }


def handed(work: str, reply: str | None, root: str) -> dict[str, Any] | str:
    """Writes the work's CCS into the session, kept as a move its step goes on after, as
    session.written says, so the work is made from what a fresh conversation also has: in the
    work's latest call where that call takes more, else in a new one carrying its decisions, as
    session.Call says. For the plan and the learnings, which the orchestrator writes, the part is
    cut into the call, the plan as JSON in the steering's form, and gives the part, the CCS, the
    checklists it names and the command that checks the part; the plan's CCS names what each task
    done served, decided and made after what the receiver has. For a task's result given no reply,
    what settled_print gives, writing nothing; given the compressor's point, the point and why,
    writing nothing; given what it chose, and for the finished work and a checklist, the call that
    hands the work to turn:up, so a conversation cut while turn runs goes on from it, and the line
    telling the user what turn makes. The CCS names the kind's checklists as judged gives them, and
    the questions of them asked of each part of the work. rn is installed at root. Stops, writing
    nothing, where the branch holds no session, the steering differs from what the last keep left,
    the plan holds no task of a task's result, a task it builds on is not done, a reply is given for
    a work rn makes alone or is out of its form, a path given leads out of the repository or is not
    there, the kind has no checklist, or the finished work is not there."""
    folder = session.current()
    steered = session.kept_steering(folder)
    found = session.calls(folder)
    serving = served(steered, work)
    settled = settled_as(work, steered, folder, found)
    last = session.latest(found, work)
    number = last.number if last is not None and not last.closed else session.next_number(found)
    decisions = [] if last is None else session.decisions_of(last)
    chosen: list[str] = []
    if not session.task_of(work) and reply is not None:
        raise stop.Stop(
            f"rn: the work {work} is made as rn makes it every time, with no compressor; run"
            f" `rn.py ccs {work}` without --reply"
        )
    if session.task_of(work):
        if reply is None:
            ccs = written(work, steered, settled, serving, [], [], decisions, [], root)
            return settled_print(work, steered, folder, found, ccs)
        stage = steered["status"]["stage"]
        roles = reply_of(reply, GIVEN_BEFORE if stage in BEFORE_BUILD else GIVEN_BUILT)
        if "point" in roles:
            return {"point": roles["point"], "why": roles["why"]}
        settled = given_made(settled, roles)
        chosen = chosen_of(roles)
    named = judged(
        checklists(settled.kind or "", root), steered["status"]["stage"], folder, number, root
    )
    lists = [path for path, _, _ in named]
    part = session.call_path(folder, number, session.PART[work]) if work in session.PARTS else ""
    paths = ([part] if part else []) or settled.paths or finished_work()
    has = list(settled.has)
    if work == steering.PLAN:
        has += done_made(folder, found, steered["plan"])
    # Every check is made above, so a stop leaves nothing written.
    if part:
        repo.write_text(part, session.cut(work, steered))
    for path, text, _ in named:
        if text is not None:
            repo.write_text(path, text)
    ccs = written(
        work,
        steered,
        settled._replace(paths=paths, has=has),
        serving,
        lists,
        [one for _, _, each in named for one in each],
        decisions,
        chosen,
        root,
    )
    path = session.call_path(folder, number, session.CCS)
    repo.write_json(path, ccs)
    if part:
        test = f"python3 {shlex.quote(os.path.join(root, 'scripts', 'rn.py'))} check {number}"
        said = f"Call {number} on {work}: its part cut for the orchestrator to write"
        session.written(folder, steered, said)
        return {"part": part, "ccs": path, "checklists": lists, "check": test}
    session.written(folder, steered, f"Call {number} on {work}: handed to turn")
    # turn's call takes the table of keys under "kind", a field name of turn's own that is no kind
    # of work; and the command that checks the work under "test", null where there is none.
    result = session.call_path(folder, number, session.RESULT)
    call_line = {"ccs": path, "kind": ENTRIES, "result": result, "test": settled.test}
    return f"{repo.dumped(call_line)}\n{told(work, steered)}"


def decisions(work: str, root: str) -> dict[str, Any]:
    """Each decision of the work, as its latest call keeps it, with that call's number; none, and no
    call, where it has none; and the checklists of its kind whole, as its CCS names them from the
    build on, so the hearing reads each question before the work is made: for a task's result, the
    kind of its latest call naming one, none where no call does yet, as the compressor gives it; rn
    is installed at root. Stops where
    the branch holds no session, the steering differs from what the last keep left, the plan holds
    no task of a task's result, or the kind has no checklist."""
    folder = session.current()
    steered = session.kept_steering(folder)
    found = session.calls(folder)
    last = session.latest(found, work)
    if session.task_of(work):
        session.task_in(steered, work)
        named = [k for c in found if c.work == work for k in call.entries(c.ccs, KIND) if k]
        kind = next(reversed(named), "")
    else:
        kind = settled_as(work, steered, folder, []).kind or ""
    return {
        "work": work,
        "call": None if last is None else last.number,
        "decisions": [] if last is None else session.decisions_of(last),
        "checklists": checklists(kind, root) if kind else [],
    }
