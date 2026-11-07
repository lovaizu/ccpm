"""What tree.py gives for each start of a role, on the repository it runs at: the change the main
conversation hands for the planner's next start, the run the work is at, each role's cut, the
points open for the main conversation, and where the work stands.

A command that finds something wrong raises Stop, with what's wrong and what to do, and tree.py
then gives 1. One that can't read what it needs raises Unreadable, and tree.py then gives 2."""

from __future__ import annotations

import json
import os
from typing import Any, Callable

import files
import practices
import repository
import runs
import trees

ROOT = "${CLAUDE_PLUGIN_ROOT}"
# What a decision of a code deliverable is about where it settles a command a step's trace runs,
# by the start value that takes it.
COMMANDS = {
    "tests": "tests command",
    "coverage": "coverage command",
    "mutation": "mutation command",
}
# What a decision of the user's is about where it keeps a lack of an intent the user accepted.
ACCEPTED = "accepted shortfall"
AT = "at.json"
EDITS = "edits.json"
CUT = "cut.json"


class Stop(Exception):
    """What a command found wrong, with what to do about it."""


def plugin_folder() -> str:
    """rn's folder, which holds the folder of this module."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def command(*words: str) -> str:
    """The command of tree.py with the words, as a role runs it."""
    return " ".join(("python3", f"{plugin_folder()}/scripts/tree.py", *words))


def finder(run: str) -> trees.Finder:
    """What finds, for the run, the IDs of a kind's intents, None where the kind has no best
    practice."""

    def find(kind: str) -> list[str] | None:
        path = practices.found(kind, run)
        return practices.intents(practices.read(path)) if path else None

    return find


def practice_of(run: str, kind: str) -> dict[str, Any]:
    """The kind's best practice for the run; refuses, by Stop, a kind with none."""
    path = practices.found(kind, run)
    if path is None:
        raise Stop(f"the kind {kind} has no best practice yet")
    return practices.read(path)


def questions(run: str) -> Callable[[str], dict[str, str]]:
    """What gives, for the run, each intent's question of a kind, by its ID; none for a kind with
    no best practice."""

    def asked(kind: str) -> dict[str, str]:
        path = practices.found(kind, run)
        return {i["id"]: i["what"] for i in practices.read(path)["intents"]} if path else {}

    return asked


def tree_of(run: str) -> dict[str, Any] | None:
    """The run's design tree; None where it has none yet."""
    path = runs.tree_path(run)
    return trees.load(path) if os.path.exists(path) else None


def the_tree(run: str) -> dict[str, Any]:
    """The run's design tree; refuses, by Stop, a run with none."""
    tree = tree_of(run)
    if tree is None:
        raise Stop(f"{run} has no design tree")
    return tree


def committed_tree(run: str) -> dict[str, Any] | None:
    """The run's design tree as its branch last committed it; None where it hasn't."""
    text = repository.committed(run, runs.tree_path(run))
    return json.loads(text) if text is not None else None


def left(run: str) -> bool:
    """Whether the run has work left: a deliverable not done, or no tree yet."""
    tree = tree_of(run)
    return tree is None or trees.at_hand(tree) is not None


def at_hand() -> str:
    """The run the work is at: the one whose change waits for the planner, else the one last
    cut, else the one run with work left, else the repository's one run. Refuses, by Stop, where
    there's none."""
    run = runs.handed()
    if run is not None:
        return run
    cut = [r for r in runs.listed() if runs.kept(r, AT) is not None]
    if cut:
        return max(cut, key=lambda r: os.path.getmtime(os.path.join(runs.temporary(r), AT)))
    going = [r for r in runs.listed() if left(r)]
    if len(going) == 1:
        return going[0]
    if not going and len(runs.listed()) == 1:
        return runs.listed()[0]
    raise Stop("no run is at hand: type /rn:up alone to pick one up")


def mark(run: str, cut: dict[str, Any]) -> None:
    """Keeps the run as the one the work is at, and the cut last given."""
    runs.keep(run, AT, {})
    runs.keep(run, CUT, cut)


def writing(run: str) -> str:
    """The command by which the planner writes its tree edit into the run's tree."""
    return command("write", run, os.path.join(runs.temporary(run), runs.EDIT))


def line(values: dict[str, Any]) -> str:
    """The run values, as the first line of a cut."""
    return json.dumps(values, ensure_ascii=False)


# The change.


def change(text: str) -> str:
    """Keeps the change for the planner's next start, held to its form, each decision at the node
    it names: the line the main conversation reads. Refuses, by Stop, a change out of form."""
    try:
        data = json.loads(text)
    except ValueError as why:
        raise Stop(f"the change is no JSON: {why}") from None
    try:
        files.held("the change", data, files.form("change"))
    except files.Unreadable as why:
        raise Stop(str(why)) from None
    if "request" in data and ("run" in data or "decisions" in data):
        raise Stop("the change holds a request or a run, not both")
    if "request" in data:
        run = runs.new(data["request"])
        settled: list[dict[str, Any]] = []
    else:
        run = os.path.normpath(data["run"])
        tree = tree_of(run) if os.path.dirname(run) == runs.TOP else None
        if tree is None:
            raise Stop(f"{run} is no run of this repository")
        settled = [placed(tree, d) for d in data.get("decisions", [])]
    runs.keep(run, runs.CHANGE, {"change": data, "decisions": settled})
    return f"rn: the change for {run} is kept. Now run {command('start', 'planner')}."


def placed(tree: dict[str, Any], given: dict[str, Any]) -> dict[str, Any]:
    """The decision given, with the key of the node it settles; refuses, by Stop, one at no
    node, or at an intent with no about."""
    key = trees.where(tree, given["at"])
    if key is None:
        raise Stop(f"{given['at']} is no node of the tree")
    if key[0] == "i":
        if "about" not in given:
            raise Stop(f"the decision at the intent {given['at']} needs its about")
        key = ("x", key[1], key[2], given["about"])
    elif key[0] == "d":
        raise Stop(f"{given['at']} is a deliverable: name the goal, an intent or a decision")
    return {**given, "key": list(key)}


def stands(tree: dict[str, Any], decision: dict[str, Any]) -> bool:
    """Whether the tree holds the decision as the main conversation handed it."""
    key = tuple(decision["key"])
    if key == (trees.GOAL,):
        return tree["goal"] == {"decided": decision["decided"], "by": decision["by"]}
    held = trees.content(tree).get(key)
    return held == (decision["decided"], decision["by"])


# The cuts.


def start(role: str) -> str:
    """The cut for the role's next start, its run values on its first line."""
    if role == "planner":
        return planner_cut()
    if role == "generator":
        return generator_cut(at_hand())
    if role == "evaluator":
        return evaluator_cut(at_hand())
    raise Stop(f"rn has no role {role}: name planner, generator, or evaluator")


def planner_values(run: str | None) -> dict[str, Any]:
    """The planner's run values for the run; none of a run where there's no run at hand."""
    practice = os.path.join(practices.OWN, "plan", practices.PRACTICE)
    if run is None:
        return {"run": None, "tree": None, "edit": None, "practice": practice, "intents": None}
    edit = os.path.join(runs.temporary(run), runs.EDIT)
    return {
        "run": run,
        "tree": runs.tree_path(run),
        "edit": edit,
        "practice": practice,
        "intents": None,
    }


def planner_cut() -> str:
    """The planner's cut: the change handed, else the answers of a turn come back good, else the
    work left to pick up."""
    run = runs.handed()
    if run is not None:
        return handed_cut(run, runs.pending(run) or {})
    going = [r for r in runs.listed() if left(r)]
    for each in going:
        good = turn_good(each)
        if good is not None:
            return turn_cut(each, *good)
    if not going:
        values = planner_values(None)
        return f"{line(values)}\n{GIVE.format(result='done')}: rn has no work left to pick up."
    if len(going) > 1:
        values = planner_values(None)
        listed = "\n".join(f"- {r}: {the_tree(r)['goal']['decided']}" for r in going)
        said = GIVE.format(result="asks")
        return f"{line(values)}\n{said}, each run with work left by its goal:\n{listed}"
    return pickup_cut(going[0])


GIVE = "Give `{result}` by its command, and end with this message"


def handed_cut(run: str, kept: dict[str, Any]) -> str:
    """The planner's cut of the change kept for the run."""
    given = kept.get("change", {})
    if "request" in given:
        os.makedirs(run, exist_ok=True)
        mark(run, {"kind": "request"})
        return (
            f"{line(planner_values(run))}\n# A new run\n\nThe request, as the user typed it:\n\n"
            f"{given['request']}\n\nDraft the goal from it, settled by maker, as Q1 of the plan"
            f" best practice says. Write it with {writing(run)}, then"
            f" commit with {command('commit', run)}, and give the result it names."
        )
    tree = the_tree(run)
    if not kept.get("decisions"):
        mark(run, {"kind": "pickup"})
        return pickup_cut(run)
    mark(run, {"kind": "decisions"})
    ids = {key: node for node, key in trees.nodes(tree)}
    said = []
    for d in kept["decisions"]:
        key = tuple(d["key"])
        where = ids.get(key) or f"{ids[('i', key[1], key[2])]}, a new decision about {key[3]}"
        grounds = f"; grounds: {d['grounds']}" if d.get("grounds") else ""
        said.append(f"- at {where}: {d['decided']} (by {d['by']}{grounds})")
    goal = ""
    if any(tuple(d["key"]) == (trees.GOAL,) and d["by"] == "user" for d in kept["decisions"]):
        goal = (
            "\n\nThe goal is newly the user's: lay out every deliverable it needs back from it,"
            " as Q2 to Q5 of the plan best practice say, and the decisions the deliverable at hand"
            " leaves open, each with decided null."
        )
    return (
        f"{line(planner_values(run))}\n# The decisions settled\n\nWrite each into the tree as it"
        f" is, at its node:\n{chr(10).join(said)}{goal}\n\n# The tree\n\n"
        f"{trees.view(tree, questions(run))}\n\nWrite with {writing(run)},"
        f" answer each node it lists as touched, then commit with {command('commit', run)}, and"
        " give the result it names."
    )


def pickup_cut(run: str) -> str:
    """The planner's cut of the one run with work left, picked up where it stopped."""
    tree = the_tree(run)
    mark(run, {"kind": "pickup"})
    n = trees.at_hand(tree)
    if n is None:
        return f"{line(planner_values(run))}\n{GIVE.format(result='done')}: {run} is done."
    result = "asks" if open_points(run, tree, n) or tree["goal"]["by"] != "user" else "ready"
    d = trees.deliverables(tree)[n - 1]
    return (
        f"{line(planner_values(run))}\n# Picking up\n\n{run} stopped at D{n} {d['path']}, which"
        f" {'has a point open' if result == 'asks' else 'is ready to make'}."
        f" {GIVE.format(result=result)}: rn picks up {run} at D{n} {d['path']}."
    )


def turn_good(run: str) -> tuple[int, bool] | None:
    """The deliverable at hand, by its number, and whether its turn was of how it reads, where that
    turn's last round came back good and the tree doesn't hold it yet; None otherwise."""
    tree = tree_of(run)
    n = trees.at_hand(tree) if tree is not None else None
    if tree is None or n is None:
        return None
    d = trees.deliverables(tree)[n - 1]
    reading = reads(d)
    turn = runs.turn_of(run, d["path"], reading)
    rounds = runs.rounds(turn)
    if not rounds:
        return None
    if runs.outcome(rounds[-1], group_names(run, d, reading)) != "good":
        return None
    return n, reading


def reads(d: dict[str, Any]) -> bool:
    """Whether the deliverable's turn at hand is of how it reads: once each intent is good."""
    return bool(d["intents"]) and all(i["good"] for i in d["intents"])


def turn_kind(d: dict[str, Any], reading: bool) -> str:
    """The kind whose best practice the deliverable's turn makes it by."""
    return practices.reading(d["kind"]) if reading else d["kind"]


def group_names(run: str, d: dict[str, Any], reading: bool) -> list[str]:
    """The names of the groups of the intents of the deliverable's turn, G1 on."""
    found = practices.groups(practice_of(run, turn_kind(d, reading)))
    return [f"G{n}" for n in range(1, len(found) + 1)]


def turn_cut(run: str, n: int, reading: bool) -> str:
    """The planner's cut of a turn come back good."""
    tree = the_tree(run)
    d = trees.deliverables(tree)[n - 1]
    mark(run, {"kind": "turn", "path": d["path"], "reading": reading})
    write = writing(run)
    if reading:
        said = (
            f"The turn of how D{n} {d['path']} reads came back good. Set its status done with"
            f" {write}, answer each node it lists as touched, then commit it with the deliverable"
            f" and push with {command('deliver', run)}, and give the result it names."
        )
    else:
        said = (
            f"The turn of what D{n} {d['path']} says came back good, each intent met. Make each"
            f" intent of D{n} good with {write}, answer each node it lists as touched, then commit"
            f" with {command('commit', run)}, and give the result it names."
        )
    return f"{line(planner_values(run))}\n# A turn come back good\n\n{said}"


def open_points(run: str, tree: dict[str, Any], n: int) -> list[str]:
    """Each point open of the deliverable of the number, as a line the main conversation reads:
    each decision of the tree still open, then each point the turn's last round found that the
    tree doesn't settle yet."""
    asked = questions(run)(trees.deliverables(tree)[n - 1]["kind"])
    found = []
    for node, decision in trees.open_decisions(tree, n):
        intent = node[len(f"D{n}") :].split("-")[0]
        found.append(f"- {node} {decision['about']}: open. {intent}: {asked.get(intent, '')}")
    d = trees.deliverables(tree)[n - 1]
    turn = runs.turn_of(run, d["path"], reads(d))
    rounds = runs.rounds(turn)
    if not rounds:
        return found
    last = rounds[-1]
    if runs.outcome(last, group_names(run, d, reads(d))) != "open":
        return found
    held = trees.content(tree)
    for point in runs.points(last):
        key = ("x", d["path"], point["intent"], point["about"])
        if held.get(key, (None,))[0] is None:
            said = f"{point['about']}: {point['what']}. {point['intent']}"
            found.append(f"- D{n}{point['intent']} {said}: {asked.get(point['intent'], '')}")
    return found


def values_of(run: str, d: dict[str, Any], practice: str, record: str) -> dict[str, Any]:
    """The generator's run values for the deliverable."""
    inputs = [p for p in d["inputs"] if os.path.isfile(p)]
    held = {x["about"]: x["decided"] for i in d["intents"] for x in i["decisions"]}
    name = os.path.basename(os.path.normpath(d["path"]))
    proposal = None
    if d["kind"] == "plugin":
        proposal = os.path.join(".lane", f"{os.path.basename(run)[:8]}-{name}", f"{name}.json")
    found = {k: held.get(about) for k, about in COMMANDS.items()}
    return {
        "run": run,
        "deliverable": d["path"],
        "inputs": inputs or None,
        **found,
        "proposal": proposal,
        "practice": practice,
        "intents": None,
        "record": record,
    }


def generator_cut(run: str) -> str:
    """The generator's cut: the deliverable at hand, its kind and decisions, and the last round's
    shortfalls, for the turn's next round, whose folder it makes."""
    tree = the_tree(run)
    n = trees.at_hand(tree)
    if n is None:
        raise Stop(f"{run} has no deliverable left to make")
    d = trees.deliverables(tree)[n - 1]
    reading = reads(d)
    kind = turn_kind(d, reading)
    practice = practices.found(kind, run)
    if practice is None:
        raise Stop(f"the kind {kind} has no best practice yet")
    turn = runs.turn_of(run, d["path"], reading) or runs.new_turn(run, d["path"], reading)
    before = runs.rounds(turn)
    if before and runs.made_of(before[-1]) is None:
        round_ = before[-1]
    else:
        round_ = runs.next_round(turn)
    os.makedirs(round_, exist_ok=True)
    mark(run, {"kind": "generator", "round": round_})
    record = os.path.join(round_, runs.MADE)
    values = values_of(run, d, practice, record)
    asked = questions(run)(d["kind"])
    decided = []
    for intent in d["intents"]:
        for x in intent["decisions"]:
            if x["decided"] is not None:
                decided.append(f"- {intent['id']} {x['about']}: {x['decided']}")
    out = [line(values), f"# D{n} {d['path']}: {d['name']}", ""]
    if reading:
        out.append(
            f"A turn of how it reads, by the best practice {kind}: change only how it says each"
            " thing, and keep what it says."
        )
    else:
        out.append(f"A turn of what it says, a deliverable of the kind {d['kind']}.")
    out += ["", "## Its decisions", "", *(decided or ["None yet."])]
    if not reading:
        out += ["", "## Its intents", ""]
        out += [f"- {i['id']}: {asked.get(i['id'], '')}" for i in d["intents"]]
    short = runs.shortfalls(before[-1]) if before and round_ != before[-1] else []
    if short:
        out += ["", "## What the people still lacked in the last round", ""]
        out += [f"- {q}: {lacks}" for q, lacks in short]
    return "\n".join(out)


def accepted(d: dict[str, Any], ids: list[str]) -> list[str]:
    """Each lack the user accepted under the intents of the IDs, as a line."""
    return [
        f"- {i['id']}: {x['decided']}"
        for i in d["intents"]
        if i["id"] in ids
        for x in i["decisions"]
        if x["about"] == ACCEPTED and x.get("by") == "user"
    ]


def evaluator_cut(run: str) -> str:
    """An evaluator's cut, for the next group of the intents of the turn's last round: each group
    once in order, then the first without its Answers, as an evaluator that ended with no result
    starts again."""
    tree = the_tree(run)
    n = trees.at_hand(tree)
    if n is None:
        raise Stop(f"{run} has no deliverable left to judge")
    d = trees.deliverables(tree)[n - 1]
    reading = reads(d)
    rounds = runs.rounds(runs.turn_of(run, d["path"], reading))
    made = runs.made_of(rounds[-1]) if rounds else None
    if made is None or made["open"]:
        raise Stop("the round has no Making record that makes every point: start the generator")
    round_ = rounds[-1]
    data = practice_of(run, turn_kind(d, reading))
    groups = practices.groups(data)
    kept = runs.kept(run, CUT) or {}
    cut = kept.get("cut", []) if kept.get("round") == round_ else []
    given = runs.answers_of(round_)
    names = [f"G{k}" for k in range(1, len(groups) + 1)]
    due = [g for g in names if g not in cut] or [g for g in names if g not in given]
    if not due:
        raise Stop("each group of the round has its Answers: start no more evaluators")
    name = due[0]
    ids = groups[names.index(name)]
    mark(run, {"kind": "evaluator", "round": round_, "cut": [*cut, name]})
    files_ = [p for p in made["made"] if os.path.isfile(p)]
    inputs = [p for p in d.get("inputs", []) if os.path.isfile(p)]
    try_ = os.path.join(round_, runs.TRY)
    answers = os.path.join(round_, f"evaluator-{name}.json")
    values = {
        "run": run,
        "files": files_,
        "reads": [*files_, *inputs, try_, answers],
        "try": try_,
        "answers": answers,
    }
    asked = {i["id"]: i["what"] for i in data["intents"]}
    out = [line(values), f"# The intents of {name}, {names.index(name) + 1} of {len(names)}", ""]
    out += [f"The people it's for, and what they're after: {data['goal']}", ""]
    out += [f"- {i}: {asked[i]}" for i in ids]
    taken = accepted(d, ids) if not reading else []
    if taken:
        out += ["", "## Lacks the user accepted, which you answer as met", "", *taken]
    if inputs:
        out += ["", "## What it takes its content from", "", *[f"- {p}" for p in inputs]]
    return "\n".join(out)


# What the main conversation reads.


def points() -> str:
    """The points open of the run at hand, for the main conversation to settle: the goal to confirm
    while it isn't the user's, else the plan and each point open of the deliverable at hand, with
    its kind and what it takes its content from."""
    run = at_hand()
    tree = the_tree(run)
    goal = tree["goal"]
    out = [f"Run: {run}"]
    if goal["by"] != "user":
        out.append(f"The goal, to confirm, at goal: {goal['decided']}")
        return "\n".join(out)
    out += ["", "Plan, back from the goal:"]
    for n, d in enumerate(trees.deliverables(tree), 1):
        done = " (done)" if d["status"] == trees.DONE else ""
        out.append(f"{n}. {d['path']}: {d['name']}{done}")
    n = trees.at_hand(tree)
    if n is None:
        return "\n".join([*out, "", "Every deliverable is done."])
    d = trees.deliverables(tree)[n - 1]
    taken = ", ".join(d["inputs"]) or "nothing"
    out += ["", f"D{n} {d['path']}, of the kind {d['kind']}, takes its content from {taken}."]
    found = open_points(run, tree, n)
    out += ["Its points open:", *found] if found else [f"No point of D{n} is open."]
    return "\n".join(out)


def status() -> str:
    """Where the run at hand stands, the line the user reads as rn picks it up."""
    run = at_hand()
    tree = the_tree(run)
    n = trees.at_hand(tree)
    done = [d["path"] for d in trees.deliverables(tree) if d["status"] == trees.DONE]
    if n is None:
        return f"Done: {tree['goal']['decided']}"
    d = trees.deliverables(tree)[n - 1]
    after = f", {', '.join(done)} done" if done else ""
    return f'Picking up "{tree["goal"]["decided"]}" at {n}. {d["path"]}{after}.'
