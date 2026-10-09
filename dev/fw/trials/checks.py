"""Check fw's flow in a finished run of story.py, by code, from the JSONL of every conversation and
role and from the CCS. Each check prints PASS or FAIL with the JSONL file and entry (line) number
that shows it.

    python3 dev/fw/trials/checks.py <out>      check a run again from what it left
"""
import json
import os
import re
import subprocess
import sys

TRIALS = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(TRIALS))), "fw", "scripts"))

import ccs  # noqa: E402
import talk  # noqa: E402

TASKS = {"greeting": ["make", "use", "learn", "make", "use", "learn"], "farewell": ["make", "use", "learn"]}
NEXT_ROLE = {"fill": "make", "align-make": "make", "make": "make", "align-use": "use", "use": "use",
             "align-recheck": "use", "recheck": "use", "align-learn": "learn", "learn": "learn", "judge": None}
AGENTS = set(ccs.ROLES.values())


def project_dir(repo):
    return os.path.join(os.path.expanduser("~/.claude/projects"), re.sub(r"[^A-Za-z0-9]", "-", os.path.realpath(repo)))


def lines(path):
    with open(path) as f:
        return [(n, json.loads(l)) for n, l in enumerate(f, 1) if l.strip()]


BASE = [os.path.expanduser("~/.claude/projects")]


def short(path):
    """A JSONL's path from the run's own folder under ~/.claude/projects."""
    return os.path.relpath(path, BASE[0])


class Conversation:
    """One conductor conversation: its fw calls, their results, and the replies that came back."""

    def __init__(self, path):
        self.path, self.entries = path, lines(path)
        self.events = []  # (line, timestamp, what, details)
        uses = {}
        for n, e in self.entries:
            ts = e.get("timestamp", "")
            content = (e.get("message") or {}).get("content")
            if talk.notice(e):
                content = talk.notice(e)
                found = talk.NOTICE.search(content)
                if found:
                    result = re.search(r"<result>(.*?)</result>", content, re.S)
                    self.events.append((n, ts, "notice", {"agent": found.group(1), "text": result.group(1) if result else ""}))
                elif e.get("type") == "user" and not content.startswith("<"):
                    self.events.append((n, ts, "user", {"text": content}))
            for b in talk.blocks(e):
                if b.get("type") == "text" and e.get("type") == "assistant":
                    self.events.append((n, ts, "text", {"text": b["text"], "msg": e["message"].get("id")}))
                elif b.get("type") == "tool_use":
                    uses[b["id"]] = (n, ts, b, e["message"].get("id"))
                elif b.get("type") == "tool_result" and b.get("tool_use_id") in uses:
                    un, uts, use, msg = uses.pop(b["tool_use_id"])
                    result = e.get("toolUseResult") if isinstance(e.get("toolUseResult"), dict) else {}
                    text = b.get("content") if isinstance(b.get("content"), str) else json.dumps(b.get("content"))
                    self.events.append((un, uts, "call", {"name": use["name"], "input": use.get("input") or {},
                                                          "error": bool(b.get("is_error")), "result": result,
                                                          "text": text, "msg": msg, "done_line": n}))
        self.events.sort(key=lambda ev: ev[0])

    def calls(self, name=None):
        return [ev for ev in self.events if ev[2] == "call" and (name is None or ev[3]["name"] == name)]

    def fw(self):
        """Each fw step that went through: (line, ts, kind, path, agent, msg)."""
        steps = []
        for n, ts, _, c in self.calls():
            if c["error"]:
                continue
            if c["name"] == "Agent" and c["input"].get("subagent_type") in AGENTS:
                said = talk.header(c["input"].get("prompt"))
                if said:
                    steps.append((n, ts, said[0], said[1], c["result"].get("agentId"), c["msg"],
                                  c["result"].get("status") == "completed"))
            elif c["name"] == "SendMessage":
                said = talk.header(c["input"].get("message"))
                if said and c["result"].get("success", True):
                    steps.append((n, ts, said[0], said[1], c["input"].get("to"), c["msg"], False))
        return steps

    def blocked(self):
        return [(n, c["name"], c["text"][:160]) for n, _, _, c in self.calls()
                if c["error"] and c["name"] in ("Agent", "SendMessage", "Write") and "hook" in c["text"].lower()]


class Run:
    def __init__(self, repo, log):
        self.repo, self.log = repo, log
        self.dir = project_dir(repo)
        BASE[0] = self.dir
        other = f"{log.get('other')}.jsonl"
        files = [os.path.join(self.dir, n) for n in os.listdir(self.dir) if n.endswith(".jsonl") and n != other]
        self.conversations = sorted((Conversation(f) for f in files), key=lambda c: c.entries[0][1].get("timestamp", ""))
        self.other = os.path.join(self.dir, other)
        self.roles = {}  # role JSONL -> (agent type, entries)
        for c in self.conversations:
            sub = os.path.join(c.path[:-6], "subagents")
            for n in sorted(os.listdir(sub)) if os.path.isdir(sub) else []:
                if n.endswith(".jsonl"):
                    with open(os.path.join(sub, n[:-6] + ".meta.json")) as f:
                        kind = json.load(f).get("agentType")
                    self.roles[os.path.join(sub, n)] = kind
        self.record = os.path.join(repo, ".mock")
        self.out = []

    def say(self, ok, name, evidence):
        self.out.append(f"- {'PASS' if ok else 'FAIL'} {name}: {evidence}")

    def turns(self, task):
        """The task's turns from its CCS: [(n, role, worked, made, JSONL)], an abandoned turn dropped
        when the same role starts again."""
        found = ccs.records(os.path.join(self.record, task))
        turns = {}
        for n, role, kind, path in found:
            turns.setdefault(n, {"role": role, "path": path, "kinds": set()})["kinds"].add(kind)
        ordered = [(n, t["role"], "worked" in t["kinds"], "made" in t["kinds"], t["path"]) for n, t in sorted(turns.items())]
        return [t for i, t in enumerate(ordered)
                if t[2] or not any(u[1] == t[1] for u in ordered[i + 1:])]

    def exchange(self, path):
        return talk.exchange(path) if os.path.isfile(path) else []

    # The checks

    def order(self):
        for task, expected in TASKS.items():
            turns = self.turns(task)
            roles = [t[1] for t in turns]
            worked = all(t[2] for t in turns) and all(t[3] for t in turns if t[1] == "make")
            steps = all([k for k, _ in self.exchange(t[4])][:4] == ["request", "reply", "go", "reply"] for t in turns)
            self.say(roles == expected and worked and steps, f"order of states, {task}",
                     f"turns {roles} (expected {expected}); each request→reply→go→reply: {steps}; "
                     + "; ".join(f"#{t[0]} {t[1]} {short(t[4])}" for t in turns))

    def learner_every_turn(self):
        for task in TASKS:
            turns = self.turns(task)
            uses = [i for i, t in enumerate(turns) if t[1] == "use"]
            ok = all(i + 1 < len(turns) and turns[i + 1][1] == "learn" and turns[i + 1][2] for i in uses)
            self.say(ok and uses, f"learner after every use, {task}",
                     ", ".join(f"use #{turns[i][0]} → {'learn #' + str(turns[i + 1][0]) if i + 1 < len(turns) else 'none'}" for i in uses))

    def content_fixed(self):
        turns = self.turns("greeting")
        learn = next((t for t in turns if t[1] == "learn"), None)
        replies = [line for k, line in self.exchange(learn[4])] if learn else []
        text = self.last_text(learn[4]) if learn else ""
        fixed_turn = next((t for t in turns if learn and t[0] > learn[0] and t[1] == "make"), None)
        writes = []
        for c in self.conversations:
            for n, ts, _, call in c.calls():
                body = json.dumps(call["input"])
                if call["name"] in ("Write", "Edit") and call["input"].get("file_path", "").endswith("greeting/make.yaml") and "fix" in body:
                    writes.append(f"{short(c.path)}:{n}")
        with open(os.path.join(self.repo, "greeting.txt")) as f:
            work = f.read()
        recheck = next((t for t in turns if fixed_turn and t[0] > fixed_turn[0] and t[1] == "use"), None)
        recheck_said = self.last_text(recheck[4]) if recheck else ""
        ok = "from" in text and fixed_turn and fixed_turn[3] and writes and "from: mock" in work and "No stumble" in recheck_said
        self.say(bool(ok), "content learning fixed in that turn",
                 f"learner {short(learn[4]) if learn else '-'} said {text[:120]!r}; fix written to make.yaml at {writes}; "
                 f"maker #{fixed_turn[0] if fixed_turn else '-'} made it; greeting.txt {work!r}; recheck said {recheck_said[:80]!r}")

    def last_text(self, path):
        said = ""
        for _, e in lines(path):
            if e.get("type") == "assistant":
                text = "\n".join(b.get("text", "") for b in talk.blocks(e) if b.get("type") == "text")
                said = text or said
        return said

    def process_rule(self):
        with open(os.path.join(self.record, "steering.md")) as f:
            steering = f.read()
        rules = steering.split("Rules", 1)[-1] if "Rules" in steering else ""
        written = None
        for c in self.conversations:
            for n, ts, _, call in c.calls():
                body = json.dumps(call["input"])
                if not written and call["name"] in ("Write", "Edit") and call["input"].get("file_path", "").endswith("steering.md") and "State:" in body:
                    written = (c, n, ts)
        if not written:
            return self.say(False, "process learning in steering's Rules and followed", f"Rules: {rules.strip()[:200]!r}; never written")
        first_learn = min((t for task in TASKS for t in self.turns(task) if t[1] == "learn"), key=lambda t: t[0])
        followed, missed = 0, []
        for c in self.conversations:
            last_boundary = 0
            if c is written[0]:
                last_boundary = written[1]
            elif c.entries[0][1].get("timestamp", "") < written[2]:
                continue
            group = None
            for n, ts, kind, d in c.events:
                if kind != "call" or c is written[0] and n <= written[1]:
                    continue
                said = d["name"] == "Agent" and talk.header(d["input"].get("prompt")) or d["name"] == "SendMessage" and talk.header(d["input"].get("message"))
                if not said or d["error"]:
                    continue
                if d["msg"] == group:
                    followed += 1
                    continue
                texts = [ev for ev in c.events if ev[2] == "text" and last_boundary < ev[0] <= n and "State:" in ev[3]["text"]]
                if texts:
                    followed += 1
                else:
                    missed.append(f"{short(c.path)}:{n}")
                last_boundary, group = n, d["msg"]
        ok = "State:" in rules and not missed and followed
        self.say(bool(ok), "process learning in steering's Rules and followed from the next step",
                 f"written at {short(written[0].path)}:{written[1]} after learner #{first_learn[0]}; "
                 f"{followed} later fw messages preceded by a State: line, missed at {missed}")

    def issue_question(self):
        talk_log = self.log.get("talk", [])
        asked = [i for i, t in enumerate(talk_log) if t["who"] == "conductor" and re.search(r"\bissue", t["text"], re.I)]
        answer = talk_log[asked[-1] + 1]["text"] if asked and asked[-1] + 1 < len(talk_log) else ""
        gh = [f"{short(p)}:{n}" for p in self.all_jsonl() for n, e in lines(p) for b in talk.blocks(e)
              if b.get("type") == "tool_use" and b.get("name") == "Bash" and "gh issue" in (b.get("input") or {}).get("command", "")]
        where = self.find_text(self.conversations[-1], r"\bissue") if self.conversations else None
        self.say(bool(asked) and not gh, "at the end the user is asked whether to send it as an issue",
                 f"asked at {where}; the user answered {answer[:60]!r}; gh issue run: {gh or 'never'}")

    def find_text(self, c, pattern):
        hits = [n for n, _, k, d in c.events if k == "text" and re.search(pattern, d["text"], re.I)]
        return f"{short(c.path)}:{hits[-1]}" if hits else None

    def resume(self):
        cut = self.log.get("cut")
        if not cut or len(self.conversations) < 2:
            return self.say(False, "resume after clearing the conversation", f"cut {cut}, conversations {len(self.conversations)}")
        fresh = self.conversations[1]
        steps = fresh.fw()
        state_run = [n for n, _, _, c in fresh.calls("Bash") if "state.py" in c["input"].get("command", "")]
        users_before = [n for n, _, k, _ in fresh.events if k == "user" and steps and n < steps[0][0]]
        results = []
        for task, state in cut["states"].items():
            first = next((s for s in steps if s[3].startswith(f".mock/{task}/")), None)
            want = NEXT_ROLE.get(state)
            got = first and first[3].rsplit("/", 1)[1][:-5]
            results.append((task, state, want, got, first and f"{short(fresh.path)}:{first[0]}",
                            want == got or want is None and got is None))
        ok = all(r[5] for r in results) and state_run and state_run[0] < steps[0][0] and len(users_before) <= 1
        self.say(bool(ok), "resume after clearing the conversation",
                 f"state.py run at lines {state_run[:3]}; user turns before the first fw step: {len(users_before)}; "
                 + "; ".join(f"{t}: state at cut {s}, expected {w}, first step {g} at {at}" for t, s, w, g, at, _ in results))

    def none_left(self):
        """At a pause or the end, every role the conversation started has replied to its last
        message, as its own JSONL shows, or was stopped."""
        for i, c in enumerate(self.conversations):
            if self.log.get("mode") == "p" and i == 0 and self.log.get("cut"):
                self.say(True, f"no role left working, conversation {i + 1}",
                         "ended by the trial as a vanished conversation, not a pause: not applicable")
                continue
            sub = os.path.join(c.path[:-6], "subagents")
            stopped = {d["input"].get("task_id") for _, _, _, d in c.calls("TaskStop") if not d["error"]}
            left, count = [], 0
            for path, kind in self.roles.items():
                if kind in AGENTS and os.path.dirname(path) == sub:
                    count += 1
                    said = self.exchange(path)
                    agent = os.path.basename(path)[len("agent-"):-6]
                    if said and said[-1][0] != "reply" and agent not in stopped:
                        left.append(f"{short(path)} last sent {said[-1][1]!r}")
            when = "the cut" if i == 0 and self.log.get("cut") else "the end"
            self.say(not left, f"no role left working at {when}, conversation {i + 1}",
                     f"{short(c.path)}: {count} roles, {len(stopped)} stopped; left: {left or 'none'}")

    def headers(self):
        missing, replies, bad = [], 0, []
        for c in self.conversations:
            fw_agents = {s[4] for s in c.fw() if s[2] == "request"}
            for n, _, _, d in c.calls("SendMessage"):
                if d["input"].get("to") in fw_agents and not talk.header(d["input"].get("message")):
                    missing.append(f"{short(c.path)}:{n}")
        for path, kind in self.roles.items():
            if kind not in AGENTS:
                continue
            said = self.exchange(path)
            for (k1, line1), (k2, line2) in zip(said, said[1:]):
                if k1 != "reply" and k2 == "reply":
                    replies += 1
                    path1 = line1.split(" ", 1)[1]
                    if not re.match(rf"\W*reply to {k1} {re.escape(path1)}", line2):
                        bad.append(f"{short(path)}: {line2[:60]!r} to {line1!r}")
        self.say(not missing, "every fw message has its header", f"without: {missing or 'none'}")
        self.say(not bad and replies, "every reply begins with what it answers", f"{replies} replies; off: {bad or 'none'}")

    def waiting(self):
        """Replay each conversation: no second message to a role, and no later step of its task,
        before its reply has come."""
        second, early, notes = [], [], []
        for c in self.conversations:
            wait, task_of = {}, {}
            for n, ts, kind, d in c.events:
                if kind == "notice" and d["agent"] in wait:
                    wait[d["agent"]] = None
                if kind != "call" or d["error"]:
                    continue
                said = (d["name"] == "Agent" and d["input"].get("subagent_type") in AGENTS and talk.header(d["input"].get("prompt"))) \
                    or (d["name"] == "SendMessage" and talk.header(d["input"].get("message")))
                if not said:
                    continue
                task = os.path.dirname(said[1])
                agent = d["result"].get("agentId") if d["name"] == "Agent" else d["input"].get("to")
                if d["name"] == "SendMessage" and wait.get(agent):
                    second.append(f"{short(c.path)}:{n}")
                if d["name"] == "Agent":
                    pending = [a for a, t in task_of.items() if t == task and wait.get(a) in ("request", "go", "check")]
                    if pending:
                        early.append(f"{short(c.path)}:{n} while {pending} still answering")
                    task_of[agent] = task
                wait[agent] = None if d["result"].get("status") == "completed" else said[0]
                notes.append(n)
        blocked = [f"{short(c.path)}:{b[0]}" for c in self.conversations for b in c.blocked()]
        self.say(not second, "no role gets a second message while one is waiting", f"{len(notes)} fw steps; violations {second or 'none'}; hook stops {blocked or 'none'}")
        self.say(not early, "no step goes on before its reply has arrived, per role", f"violations {early or 'none'}")

    def parallel(self):
        spans = {}
        for path, kind in self.roles.items():
            said = self.exchange(path)
            found = said and talk.header(said[0][1])
            if kind in AGENTS and found:
                task = found[1].split("/")[1]
                stamps = [e.get("timestamp") for _, e in lines(path) if e.get("timestamp")]
                spans.setdefault(task, []).append((stamps[0], stamps[-1], short(path)))
        pairs = [(a, b) for a in spans.get("greeting", []) for b in spans.get("farewell", []) if a[0] < b[1] and b[0] < a[1]]
        self.say(bool(pairs), "the two tasks' roles ran at the same time",
                 f"{pairs[0][0][2]} {pairs[0][0][0]}–{pairs[0][0][1]} with {pairs[0][1][2]} {pairs[0][1][0]}–{pairs[0][1][1]}" if pairs else "no overlap")

    def all_jsonl(self):
        files = [c.path for c in self.conversations] + list(self.roles)
        if os.path.isfile(self.other):
            files.append(self.other)
            sub = os.path.join(self.other[:-6], "subagents")
            files += [os.path.join(sub, n) for n in os.listdir(sub) if n.endswith(".jsonl")] if os.path.isdir(sub) else []
        return files

    def isolation(self):
        if not os.path.isfile(self.other):
            return self.say(False, "no effect on another session in the same repository", "the other session left no JSONL")
        other = Conversation(self.other)
        stops = [f"{short(self.other)}:{n}" for n, _, _, d in other.calls() if d["error"] and "hook" in d["text"].lower()]
        wrote = [f"{short(self.other)}:{n}" for n, _, _, d in other.calls("Write") if not d["error"]]
        sends = [f"{short(self.other)}:{n}" for n, _, _, d in other.calls("SendMessage") if not d["error"]]
        mine = os.path.basename(self.other)[:-6]
        touched = [p for t in TASKS for p in self.ccs_files(t) if mine in open(p).read()]
        outside = []
        root = os.path.realpath(self.repo) + os.sep
        for path in self.all_jsonl():
            for n, e in lines(path):
                for b in talk.blocks(e):
                    if b.get("type") == "tool_use" and b.get("name") in ("Write", "Edit", "NotebookEdit"):
                        target = (b.get("input") or {}).get("file_path") or ""
                        if not os.path.realpath(target).startswith(root):
                            outside.append(f"{short(path)}:{n} {target}")
        status = subprocess.run(["git", "status", "--short", "--untracked-files=all"], cwd=self.repo, capture_output=True, text=True).stdout
        changed = sorted({l[3:].split("/")[0] for l in status.splitlines()})
        ok = not stops and wrote and sends and not touched and not outside and set(changed) <= {".mock", "greeting.txt", "farewell.txt", "notes"}
        self.say(bool(ok), "no effect on another session in the same repository, nor outside it",
                 f"other session: hook stops {stops or 'none'}, its Write {wrote}, its SendMessage {sends}; CCS naming it {touched or 'none'}; "
                 f"writes outside the repository {outside or 'none'}; changed in the repository {changed}")

    def ccs_files(self, task):
        folder = os.path.join(self.record, task)
        return [os.path.join(folder, n) for n in os.listdir(folder)] if os.path.isdir(folder) else []

    def run(self):
        for check in (self.order, self.learner_every_turn, self.content_fixed, self.process_rule, self.issue_question,
                      self.resume, self.none_left, self.headers, self.waiting, self.parallel, self.isolation):
            try:
                check()
            except Exception as error:  # a check that cannot run is a failure to report, not a crash
                self.say(False, check.__name__, f"could not be checked: {error!r}")
        head = f"# fw trial, mode {self.log.get('mode')}\n\nConversations: {[short(c.path) for c in self.conversations]}\n\n"
        return head + "\n".join(self.out) + "\n"


def run(repo, log):
    return Run(repo, log).run()


if __name__ == "__main__":
    out = os.path.realpath(sys.argv[1])
    with open(os.path.join(out, "run.json")) as f:
        print(run(os.path.join(out, "repo"), json.load(f)))
