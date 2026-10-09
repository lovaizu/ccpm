"""What fw's tests share: a repository with a task folder, the hooks run as Claude Code runs them,
and the JSONL files of a conductor and its roles, written as Claude Code writes them."""

import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest import mock

FW = os.path.realpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "..", "fw"))
sys.path.insert(0, os.path.join(FW, "scripts"))

import ccs  # noqa: E402

TASK = ".mock/greeting"
WORK = "greeting.txt"
WRAP = "The coordinator sent a message while you were working:\n{}\n\nAddress this before completing your current task."


def path(role):
    return f"{TASK}/{role}.yaml"


class Repo(unittest.TestCase):
    """A repository with a plugin's domain folder and one task's folder."""

    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.root = os.path.realpath(self.dir.name)
        self.domain = os.path.join(self.root, "domain")
        os.makedirs(os.path.join(self.root, TASK))
        os.makedirs(self.domain)
        for role in ccs.ROLES:
            with open(os.path.join(self.domain, f"{role}.json"), "w") as f:
                json.dump([{"component": "constraints", "type": "language", "from": "steering"}], f)
        self.conductor = os.path.join(self.root, "conductor.jsonl")
        self.lines = []
        self.agents = 0

    def tearDown(self):
        self.dir.cleanup()

    # The CCS

    def ready(self, role, *more):
        """A CCS holding everything fw and the domain require of the role, and what the hooks wrote
        into the role's CCS before, kept as the conductor keeps it."""
        with open(os.path.join(FW, "references", f"{role}.json")) as f:
            entries = json.load(f)
        state = {c: [] for c in ccs.COMPONENTS}
        for r in entries:
            value = {"work": WORK, "domain": self.domain}.get(r["type"], f"the {r['type']}")
            state[r["component"]].append((r["type"], value))
        state["constraints"].append(("language", "English"))
        for component, kind, value in more:
            state[component].append((kind, value))
        old = os.path.join(self.root, path(role))
        if os.path.isfile(old):
            for component, entries in ccs.load(old).items():
                state[component] += [e for e in entries if e[0] in ccs.RECORDS + ("work_before", "conductor")]
        return state

    def write(self, role, state):
        ccs.dump(state, os.path.join(self.root, path(role)))

    def load(self, role):
        return ccs.load(os.path.join(self.root, path(role)))

    def update(self, role, component, entry, drop=None):
        state = self.load(role)
        state[component] = [e for e in state[component] if e[0] != (drop or entry[0])] + [entry]
        self.write(role, state)

    def make_work(self, text):
        with open(os.path.join(self.root, WORK), "w") as f:
            f.write(text)

    # The hooks

    def hook(self, script, event):
        """Run a hook's script as Claude Code runs it: its exit status, stdout and stderr."""
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdin", io.StringIO(json.dumps(event))), redirect_stdout(out), redirect_stderr(err):
            try:
                runpy.run_path(os.path.join(FW, "scripts", script), run_name="__main__")
            except SystemExit as stop:
                return stop.code or 0, out.getvalue(), err.getvalue()
        return 0, out.getvalue(), err.getvalue()

    def pre(self, tool, call):
        self.flush()
        return self.hook("check_in.py", {"hook_event_name": "PreToolUse", "tool_name": tool, "tool_input": call,
                                         "cwd": self.root, "transcript_path": self.conductor})

    def stop(self, agent, transcript):
        return self.hook("facts.py", {"hook_event_name": "SubagentStop", "agent_type": agent,
                                      "agent_transcript_path": transcript, "cwd": self.root})

    # The conductor's JSONL

    def flush(self):
        with open(self.conductor, "w") as f:
            f.writelines(json.dumps(e) + "\n" for e in self.lines)

    def launch(self, role, prompt=None, background=True, agent_type=None):
        """The conductor starts a role; returns its agent id. A foreground role's reply comes back at once."""
        self.agents += 1
        agent, uid = f"a{self.agents}", f"u{len(self.lines)}"
        call = {"subagent_type": agent_type or ccs.ROLES[role], "prompt": prompt or f"request {path(role)}",
                "run_in_background": background}
        self.lines.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": uid, "name": "Agent", "input": call}]}})
        status = "async_launched" if background else "completed"
        self.lines.append({"type": "user", "toolUseResult": {"status": status, "agentId": agent},
                           "message": {"content": [{"type": "tool_result", "tool_use_id": uid, "content": "ok"}]}})
        return agent

    def message(self, to, text, success=True):
        uid = f"u{len(self.lines)}"
        self.lines.append({"type": "assistant", "message": {"content": [
            {"type": "tool_use", "id": uid, "name": "SendMessage", "input": {"to": to, "message": text}}]}})
        self.lines.append({"type": "user", "toolUseResult": {"success": success},
                           "message": {"content": [{"type": "tool_result", "tool_use_id": uid, "content": "ok"}]}})

    def notice(self, agent):
        self.lines.append({"type": "user", "message": {"content": f"<task-notification>\n<task-id>{agent}</task-id>\n"
                                                                  "<status>completed</status>\n</task-notification>"}})

    def queued(self, agent):
        """A reply that came while the conductor was busy: queued, and handed to it with its next step."""
        self.lines.append({"type": "queue-operation", "operation": "enqueue",
                           "content": f"<task-notification>\n<task-id>{agent}</task-id>\n</task-notification>"})

    # A role's own JSONL

    def role_jsonl(self, name, said, tools=()):
        """A role's JSONL: the messages it was sent and its replies, in order, and its tool calls."""
        file = os.path.join(self.root, f"{name}.jsonl")
        entries = []
        for i, (who, text) in enumerate(said):
            if who == "conductor":
                entries.append({"type": "user", "message": {"content": text if i == 0 else WRAP.format(text)}})
                for uid, (tool, args, result) in enumerate(tools if i == 0 else ()):
                    entries.append({"type": "assistant", "message": {"content": [
                        {"type": "tool_use", "id": f"t{uid}", "name": tool, "input": args}]}})
                    entries.append({"type": "user", "message": {"content": [
                        {"type": "tool_result", "tool_use_id": f"t{uid}", **result}]}})
            else:
                entries.append({"type": "assistant", "message": {"content": [{"type": "text", "text": text}]}})
        with open(file, "w") as f:
            f.writelines(json.dumps(e) + "\n" for e in entries)
        return file

    def turn(self, role, made=None, go=True):
        """A whole turn of a role, as the hooks see it, each step let through: request, its reply,
        agreed, go, the work, its reply, ok. Returns the role's JSONL."""
        p = path(role)
        self.assertEqual(self.pre("Agent", {"subagent_type": ccs.ROLES[role], "prompt": f"request {p}"})[0], 0)
        agent = self.launch(role)
        said = [("conductor", f"request {p}"), ("role", f"reply to request {p}\nI will do it.")]
        name = f"{role}{self.agents}"
        self.stop(ccs.ROLES[role], self.role_jsonl(name, said))
        self.notice(agent)
        if not go:
            return agent
        self.update(role, "goal_orientation", ("agreed", "as you said"))
        self.assertEqual(self.pre("SendMessage", {"to": agent, "message": f"go {p}"})[0], 0)
        self.message(agent, f"go {p}")
        if made is not None:
            self.make_work(made)
        said += [("conductor", f"go {p}"), ("role", f"reply to go {p}\ndone")]
        self.stop(ccs.ROLES[role], self.role_jsonl(name, said))
        self.notice(agent)
        self.assertEqual(self.pre("SendMessage", {"to": agent, "message": f"ok {p}"})[0], 0)
        return agent
