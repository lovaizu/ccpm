#!/usr/bin/env python3
"""What turn:up needs to come out the same on every run: the CCS checked, the list and the forms
laid out, each form checked, the first user's copy, and the work and the CCS written back."""

import glob
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile

PARTS = {
    "focal_entities": {"deliverable", "receiver"},
    "goal_orientation": {"use", "acceptance"},
    "retrieved_artifacts": {"viewpoint", "source"},
    "constraints": {"language", "rule", "answer"},
    "predictive_cue": {"next"},
    "uncertainty_signal": {"gap"},
    "semantic_gist": {"difference"},
    "relational_map": None,
    "episodic_trace": None,
}
ROLES = ("generator", "hand-on", "first-user", "evaluator", "orchestrator", "learner")
PLACES = ("the work", "what the work should be")
AGENTS = {"generator": 4, "first-user": 9, "evaluator": 10, "learner": 12}
SCRIPT = os.path.abspath(__file__)
DECIDING = ("hand-on", "orchestrator")
RUN = os.path.join(".turn", "run.json")
NAMES_LINES = re.compile(r"\blines?\s*\d|\b\d+\s*-\s*\d+\b")
LINES = re.compile(r"\s*\d+(\s*-\s*\d+)?(\s*,\s*\d+(\s*-\s*\d+)?)*\s*$")
USAGE = """usage: up.py start <in> <out> <session>
       up.py brief <work folder> <round> <generator|first-user|evaluator|learner>
       up.py coverage <work folder> <round> <generator|evaluator>
       up.py check <work folder> <round> <generator|hand-on|first-user|evaluator|orchestrator|learner>
       up.py round <work folder>
       up.py end <work folder> <round>"""


class Stop(Exception):
    """Ends the command, saying why."""


def read_json(path, name):
    try:
        with open(path) as f:
            return json.load(f)
    except ValueError:
        raise Stop(f"{name} is not JSON")


def write_json(path, value):
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    with open(path, "w") as f:
        json.dump(value, f, indent=1, ensure_ascii=False)
        f.write("\n")


def entries(ccs, part, kind):
    return [v for e in ccs[part] for k, v in e.items() if k == kind]


def faults(ccs):
    """Says each way the CCS does not match the form the callers' page gives."""
    found = []
    for part, kinds in PARTS.items():
        if part not in ccs:
            found.append(f"{part} is missing")
        elif not isinstance(ccs[part], list):
            found.append(f"{part} is not a list")
        else:
            for e in ccs[part]:
                if not (isinstance(e, dict) and len(e) == 1 and isinstance(next(iter(e.values())), str)):
                    found.append(f"{part} has an entry that is not one kind and a string")
                elif kinds is not None and next(iter(e)) not in kinds:
                    found.append(f"{part} has a kind it cannot hold: {next(iter(e))}")
    if found:
        return found
    if len(entries(ccs, "focal_entities", "deliverable")) != 1:
        found.append("focal_entities needs one deliverable")
    for part, kind in (("focal_entities", "receiver"), ("goal_orientation", "acceptance"),
                       ("retrieved_artifacts", "viewpoint")):
        if not entries(ccs, part, kind):
            found.append(f"{part} needs {'an' if kind[0] in 'aeiou' else 'a'} {kind}")
    for kind in ("viewpoint", "source"):
        found += [f"{p} does not exist" for p in entries(ccs, "retrieved_artifacts", kind)
                  if not os.path.isfile(p)]
    for p in entries(ccs, "focal_entities", "deliverable"):
        if os.path.isabs(p) or os.path.normpath(p).startswith(".."):
            found.append(f"{p} is outside the repository")
    return found


def checklist(path):
    """Reads a checklist: its opening, and each item with its whole text."""
    name = os.path.splitext(os.path.basename(path))[0]
    opening, items, item, fence, seen = [], [], None, False, False
    with open(path) as f:
        for line in f:
            if line.startswith("```"):
                fence = not fence
            heading = None if fence else re.match(r"(#{1,3}) (?:([A-Z]-\d+): )?(.+)", line)
            if heading:
                seen = seen or heading.group(1) == "##"
                item = None
                if heading.group(2):
                    item = {"id": f"{name} {heading.group(2)}", "title": heading.group(3).strip(),
                            "text": ""}
                    items.append(item)
            elif item is not None:
                item["text"] += line
            elif not seen:
                opening.append(line)
    for i in items:
        i["text"] = i["text"].strip()
    return {"checklist": name, "opening": "".join(opening).strip()}, items


def forms(ids):
    return {
        "generator": {i: {"lines": ""} for i in ids},
        "first-user": {},
        "evaluator": {},
        "hand-on": {i: {"met": None, "lines": "", "note": ""} for i in ids},
        "orchestrator": {i: {"met": None, "lines": "", "note": ""} for i in ids},
        "learner": {},
    }


def start(src, out, session):
    if os.path.exists(out):
        raise Stop(f"{out} already exists; turn never writes over a file, so name a new out")
    ccs = read_json(src, src)
    found = faults(ccs)
    if found:
        raise Stop("\n".join(found))
    work = os.path.join(".turn", os.path.splitext(os.path.basename(out))[0])
    lists = [checklist(p) for p in entries(ccs, "retrieved_artifacts", "viewpoint")]
    listed = {"checklists": [c for c, _ in lists], "items": [i for _, items in lists for i in items]}
    write_json(os.path.join(work, "list.json"), listed)
    laid = forms([i["id"] for i in listed["items"]])
    lay(work, 1, laid)
    write_json(os.path.join(work, "questions.json"), [])
    deliverable = entries(ccs, "focal_entities", "deliverable")[0]
    write_json(RUN, {"session": session, "work": work, "in": src, "out": out, "round": 1})
    print(json.dumps({
        "folder": work,
        "list": os.path.join(work, "list.json"),
        "round": 1,
        "work": os.path.join(work, "1", os.path.basename(deliverable)),
        "hand-on": os.path.join(work, "1", "hand-on.json"),
        "orchestrator": os.path.join(work, "1", "orchestrator.json"),
        "questions": os.path.join(work, "questions.json"),
        "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
        "use": "; ".join(entries(ccs, "goal_orientation", "use")),
        "acceptance": entries(ccs, "goal_orientation", "acceptance"),
        "sources": entries(ccs, "retrieved_artifacts", "source"),
        "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()],
    }, indent=1, ensure_ascii=False))


def lay(work, n, laid):
    for role in ROLES:
        write_json(os.path.join(work, str(n), f"{role}.json"), laid[role])


def the_work(work, n, written=True):
    """The run's CCS as received, and the path of the work made in round n."""
    run = read_json(RUN, RUN)
    ccs = read_json(run["in"], run["in"])
    deliverable = entries(ccs, "focal_entities", "deliverable")[0]
    path = os.path.join(work, str(n), os.path.basename(deliverable))
    if written and not os.path.isfile(path):
        raise Stop(f"{path} is not written")
    return run, ccs, deliverable, path


def bad_lines(given, count):
    if not LINES.match(given):
        return True
    return any(not 1 <= int(a) <= int(b or a) <= count
               for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", given))


def check(work, n, role):
    """Says each place of the role's form that is left or wrong; nothing when every place is filled."""
    _, _, _, path = the_work(work, n)
    with open(path) as f:
        count = len(f.read().splitlines())
    ids = [i["id"] for i in read_json(os.path.join(work, "list.json"), "the list")["items"]]
    form = read_json(os.path.join(work, str(n), f"{role}.json"), "the form")
    found = [f"{i}: not an item of the list" for i in form if i not in ids]
    if role == "learner":
        return found + learner_faults(form, without_good(work, n), count) + question_faults(work, decided=False)
    if role in ("generator", "hand-on"):
        found += question_faults(work, decided=role == "hand-on")
    for i in ids if role not in ("first-user", "evaluator") else [i for i in ids if i in form]:
        place = form.get(i)
        if place is None:
            found.append(f"{i}: not filled")
            continue
        lines = place.get("lines", "")
        needed = role in ("generator", "first-user", "evaluator") or (role in DECIDING and place.get("met"))
        if role == "first-user" and not place.get("took"):
            found.append(f"{i}: what was taken is not given")
        if role == "evaluator" and not place.get("grounds"):
            found.append(f"{i}: grounds are not given")
        if role in DECIDING and not isinstance(place.get("met"), bool):
            found.append(f"{i}: not decided")
        if role in DECIDING and place.get("met") and not place.get("note"):
            found.append(f"{i}: the note is not given")
        if role == "hand-on" and place.get("met") is False:
            found += aim_faults(i, place, count)
        if needed and not lines:
            found.append(f"{i}: lines are not given")
        elif lines and bad_lines(lines, count):
            found.append(f"{i}: lines {lines} are not in the work")
        if role == "hand-on" and "question" in place and place["question"] not in asked_numbers(work):
            found.append(f"{i}: question {place['question']} is not asked")
    return found


def asked(work):
    return read_json(os.path.join(work, "questions.json"), "the questions")


def asked_numbers(work):
    return [k for k, q in enumerate(asked(work), 1) if q.get("ask")]


def unanswered(work):
    return [k for k, q in enumerate(asked(work), 1) if q.get("ask") and "answer" not in q and not q.get("left")]


def waiting(work, n):
    """The items of round n's work that wait on a question the user left, so go on without a Good."""
    left = [k for k, q in enumerate(asked(work), 1) if q.get("left")]
    return [i for i, p in read_json(os.path.join(work, str(n), "hand-on.json"), "the form").items()
            if p.get("question") in left]


def question_faults(work, decided):
    """Says each question left without its words, or, once decided, neither asked nor shown answered."""
    questions = asked(work)
    if not isinstance(questions, list):
        return ["the questions are not a list"]
    found = []
    for k, q in enumerate(questions, 1):
        if not (isinstance(q, dict) and q.get("question")):
            found.append(f"question {k}: the question is not given")
        elif decided and not isinstance(q.get("ask"), bool):
            found.append(f"question {k}: not decided")
        elif decided and not q["ask"] and not q.get("answered"):
            found.append(f"question {k}: where it is answered is not given")
    return found


def without_good(work, n):
    return [i for i, p in read_json(os.path.join(work, str(n), "orchestrator.json"), "the form").items()
            if p.get("met") is not True and i not in waiting(work, n)]


def aim_faults(i, place, count):
    """Says where a way to a Good is not made from the aim: the aim and the way said of the whole work,
    and the reach, every line the same shape reaches."""
    found = []
    for key, said in (("aim", "say it of the whole work"), ("way", "say it from the aim")):
        if not place.get(key):
            found.append(f"{i}: the {key} is not given")
        elif NAMES_LINES.search(place[key]):
            found.append(f"{i}: the {key} names lines; {said}")
    reach = place.get("reach", "")
    if not reach:
        found.append(f"{i}: reach is not given")
    elif bad_lines(reach, count):
        found.append(f"{i}: reach {reach} is not in the work")
    return found


def learner_faults(form, left, count):
    found = [f"{i}: has a Good, so needs no way" for i in form if i not in left]
    for i in left:
        place = form.get(i)
        if place is None:
            found.append(f"{i}: not filled")
            continue
        found += aim_faults(i, place, count)
        if place.get("in") not in PLACES:
            found.append(f"{i}: in must be one of: {', '.join(PLACES)}")
        if not isinstance(place.get("making"), str):
            found.append(f"{i}: making is not given; write \"\" where nothing is learned of making")
    return found


def learned(work, n):
    """The ways the learner gave in round n, each once with the items it serves, and what it learned
    of making such work."""
    found = check(work, n, "orchestrator") or check(work, n, "learner")
    if found:
        raise Stop("\n".join(found))
    grouped, rules = {}, []
    for i, p in read_json(os.path.join(work, str(n), "learner.json"), "the form").items():
        grouped.setdefault((p["way"], p["in"]), []).append(p)
        p["item"] = i
        if p["making"] and p["making"] not in rules:
            rules.append(p["making"])
    return [dict(serves(places, w), **{"in": where}) for (w, where), places in grouped.items()], rules


def serves(places, way):
    """One way with the items it serves, their aims and every line it reaches, each said once."""
    aims, reach = (list(dict.fromkeys(p[key] for p in places)) for key in ("aim", "reach"))
    return {"way": way, "items": sorted(p["item"] for p in places), "aims": aims, "reach": reach}


def round_two(work):
    run = read_json(RUN, RUN)
    if run["round"] != 1:
        raise Stop("a run has two rounds at most")
    given, _ = learned(work, 1)
    found = question_faults(work, decided=True)
    if found:
        raise Stop("\n".join(found))
    if not any(w["in"] == PLACES[0] for w in given):
        raise Stop("no way for the generator to take, so the run ends after round 1")
    _, _, _, path = the_work(work, 1)
    lay(work, 2, forms([i["id"] for i in read_json(os.path.join(work, "list.json"), "the list")["items"]]))
    made = os.path.join(work, "2", os.path.basename(path))
    shutil.copyfile(path, made)
    run["round"] = 2
    write_json(RUN, run)
    print(json.dumps({"round": 2, "work": made}))


def coverage(work, n, role):
    _, _, _, path = the_work(work, n)
    with open(path) as f:
        text = [k for k, line in enumerate(f.read().splitlines(), 1) if line.strip()]
    named = set()
    for place in read_json(os.path.join(work, str(n), f"{role}.json"), "the form").values():
        for a, b in re.findall(r"(\d+)(?:\s*-\s*(\d+))?", place.get("lines", "")):
            named.update(range(int(a), int(b or a) + 1))
    left = [k for k in text if k not in named]
    print(f"lines no item names: {', '.join(map(str, left))}" if left else "every line is named")


def records(role):
    """The records Claude Code keeps of the run's last agent of the role."""
    session = read_json(RUN, RUN)["session"]
    found = []
    for meta in glob.glob(os.path.join(os.path.expanduser("~"), ".claude", "projects", "*", session,
                                       "subagents", "agent-*.meta.json")):
        path = meta[:-len(".meta.json")] + ".jsonl"
        if read_json(meta, meta).get("agentType") == f"turn:{role}" and os.path.isfile(path):
            found.append((os.path.getmtime(path), path))
    if not found:
        raise Stop(f"no records of the {role.replace('-', ' ')} in session {session}")
    return max(found)[1]


def at_rest(run):
    """Why the orchestrator may stop with the run open: it waits for the user or for the generator."""
    work, n = run["work"], str(run["round"])
    if unanswered(work):
        return "waiting for the user"
    brief = os.path.join(work, n, "generator-brief.json")
    if os.path.isfile(brief) and os.path.getmtime(brief) > os.path.getmtime(os.path.join(work, n, "generator.json")):
        return "waiting for the generator"
    return None


def drop(place):
    if not os.path.basename(place).startswith("turn-copy-") or \
            os.path.dirname(os.path.realpath(place)) != os.path.realpath(tempfile.gettempdir()):
        raise Stop(f"{place} is not a copy turn made")
    shutil.rmtree(place)


def brief(work, n, role):
    """Writes what the agent of the role is handed, once the steps before it are done."""
    if role not in AGENTS:
        raise Stop(f"no brief for {role}; briefs are for {', '.join(AGENTS)}")
    run = read_json(RUN, RUN)
    if int(n) != run["round"]:
        raise Stop(f"round {run['round']} is running")
    n = int(n)
    _, ccs, deliverable, path = the_work(work, n, written=role != "generator")
    here = os.path.join(work, str(n))
    should = {
        "receiver": "; ".join(entries(ccs, "focal_entities", "receiver")),
        "use": "; ".join(entries(ccs, "goal_orientation", "use")),
        "acceptance": entries(ccs, "goal_orientation", "acceptance"),
        "sources": entries(ccs, "retrieved_artifacts", "source"),
        "constraints": [f"{k}: {v}" for e in ccs["constraints"] for k, v in e.items()] +
                       [f"answer: {q['question']} {q['answer']}" for q in asked(work) if "answer" in q],
    }
    given = {"list": os.path.join(work, "list.json"), "work": path, "form": os.path.join(here, f"{role}.json"),
             "check": f'cd "{os.getcwd()}" && python3 "{SCRIPT}" check {work} {n} {role}'}
    hand_on = read_json(os.path.join(here, "hand-on.json"), "the form")
    if role == "generator":
        sent = [serves([dict(p, item=i)], p["way"]) for i, p in hand_on.items() if p.get("met") is False]
        if sent or n == 1:
            ways = sent
        else:
            ways = [{k: v for k, v in w.items() if k != "in"} for w in learned(work, 1)[0] if w["in"] == PLACES[0]]
            should["constraints"] += [f"rule: {r}" for r in learned(work, 1)[1]]
        given.update(should, ways=ways, questions=os.path.join(work, "questions.json"))
    elif role == "first-user":
        unseen = [i for i, p in hand_on.items() if p.get("met") is not True and i not in waiting(work, n)]
        if unanswered(work):
            raise Stop("step 8: wait for the user: " + ", ".join(f"question {k} is not answered"
                                                                 for k in unanswered(work)))
        if unseen:
            raise Stop("step 8: the work goes back to the generator until every item is seen given; "
                       "not yet: " + ", ".join(unseen))
        place = tempfile.mkdtemp(prefix="turn-copy-")
        subprocess.run(["git", "clone", "-q", ".", place], check=True)
        os.makedirs(os.path.dirname(os.path.join(place, deliverable)), exist_ok=True)
        shutil.copyfile(path, os.path.join(place, deliverable))
        given = {"copy": place, "deliverable": deliverable, "receiver": should["receiver"], "use": should["use"],
                 "list": os.path.abspath(given["list"]), "form": given["form"], "check": given["check"]}
    elif role == "evaluator":
        first = os.path.join(here, "first-user-brief.json")
        if not os.path.isfile(first):
            raise Stop("step 9: the first user has not been handed the work")
        read = records("first-user")
        found = check(work, n, "first-user")
        if found:
            raise Stop("\n".join(found))
        place = read_json(first, "the first user's brief")["copy"]
        if os.path.exists(place):
            drop(place)
        given.update({k: should[k] for k in ("receiver", "use", "acceptance")},
                     reading=os.path.join(here, "first-user.json"), records=read)
    else:
        found = check(work, n, "orchestrator")
        if found:
            raise Stop("\n".join(found))
        if not without_good(work, n):
            raise Stop("every item is met, so there is nothing to learn")
        given.update(should, questions=os.path.join(work, "questions.json"),
                     reading=os.path.join(here, "first-user.json"),
                     decisions=os.path.join(here, "orchestrator.json"),
                     records={"first user": records("first-user"), "generator": records("generator")})
    out = os.path.join(here, f"{role}-brief.json")
    write_json(out, given)
    print(out)


def end(work, n):
    n = int(n)
    left, _ = learned(work, n)
    found = question_faults(work, decided=True) + [f"question {k} is not answered" for k in unanswered(work)]
    if found:
        raise Stop("\n".join(found))
    gaps = [q["question"] for q in asked(work) if q.get("left")]
    if n == 1 and any(w["in"] == PLACES[0] for w in left):
        raise Stop("a way lies with the generator: start the second round")
    run, ccs, deliverable, path = the_work(work, n)
    items = {i["id"]: i for i in read_json(os.path.join(work, "list.json"), "the list")["items"]}
    differences = [{"difference": f"{i} ({items[i]['text'].splitlines()[0]}): {w['way']}"}
                   for w in left for i in w["items"]]
    caller = [f"{i}: {w['way']}" for w in left if w["in"] == PLACES[1] for i in w["items"]]
    nxt = f"to the caller: {'; '.join(caller)}" if caller else "ask the user" if differences or gaps else "done"
    ccs["constraints"] += [{"answer": f"{q['question']} {q['answer']}"} for q in asked(work) if "answer" in q]
    for k in range(1, n + 1):
        for rule in learned(work, k)[1]:
            if {"rule": rule} not in ccs["constraints"]:
                ccs["constraints"].append({"rule": rule})
    evidence = ["orchestrator.json"] + (["learner.json"] if left else [])
    os.makedirs(os.path.dirname(deliverable) or ".", exist_ok=True)
    shutil.copyfile(path, deliverable)
    ccs.update(predictive_cue=[{"next": nxt}], uncertainty_signal=[{"gap": q} for q in gaps],
               semantic_gist=differences,
               episodic_trace=[{"evidence": os.path.join(work, str(n), e)} for e in evidence])
    write_json(run["out"], ccs)
    os.remove(RUN)
    print("\n".join([nxt] + [f"❓ {q}" for q in gaps]))


COMMANDS = {"start": (start, 3), "brief": (brief, 3), "coverage": (coverage, 3), "round": (round_two, 1),
            "end": (end, 2)}


def main(argv):
    try:
        if argv[:1] == ["check"] and len(argv) == 4:
            found = check(*argv[1:])
            print("\n".join(found) or "filled")
            return 1 if found else 0
        command, count = COMMANDS.get(argv[0] if argv else "", (None, -1))
        if command is None or len(argv) - 1 != count:
            raise Stop(USAGE)
        command(*argv[1:])
        return 0
    except Stop as stop:
        print(stop)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
