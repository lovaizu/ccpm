"""What Lane's unit cases share: Lane's data as the walkthrough holds it, made by its types, so that
each case names only what sets it apart."""

from __future__ import annotations

import json
from collections.abc import Mapping
from typing import Any

from events import Event
from form import Adapters, After, Laid, LaidSentence, Lane, LanesFile, Move, Proposal, Route
from place import Call
from run_record import Marked, Read
from runs import Conversation, Due, Run, Start

SESSION = "4f7c1d2e-0000-4000-8000-000000000001"
REPO = "/home/you/tally"
RESULT = "python3 /home/you/tally/changelog/hooks/lane/result.py"
LOG = "git log --oneline"
# changelog's folder, which `${CLAUDE_PLUGIN_ROOT}` names, and the number of each role's last Step.
ROOT = "/home/you/tally/changelog"
LAST = {"write": 1, "writer": 4, "reviewer": 3, "up": 1}


def lane(role: str, file: str, step: int, kind: str, **args: Any) -> Lane:
    return Lane(role=role, file=file, step=step, type=kind, args=args)


def run_only(*commands: str) -> Lane:
    """writer's Lane on its step 2, which lets it run only the commands."""
    return lane("writer", "agents/writer.md", 2, "run_only", commands=list(commands or (LOG,)))


def write_only(*paths: str) -> Lane:
    """writer's Lane on its step 3, which lets it write only the paths."""
    given = list(paths or ("CHANGELOG.md",))
    return lane("writer", "agents/writer.md", 3, "write_only", paths=given)


ROUTES = lane("write", "skills/write/SKILL.md", 1, "routes")
# reviewer's Lane on its step 2, which lets it write only REVIEW.md.
REVIEW_ONLY = lane("reviewer", "agents/reviewer.md", 2, "write_only", paths=["REVIEW.md"])
# The Lane on each role's last Step, by which it ends by the result script.
WRITE_END = lane("write", "skills/write/SKILL.md", 1, "ends_by_result")
WRITER_END = lane("writer", "agents/writer.md", 4, "ends_by_result")
REVIEWER_END = lane("reviewer", "agents/reviewer.md", 3, "ends_by_result")


def route(after: After, *moves: Move) -> Route:
    return Route(skill="write", after=after, moves=moves)


ROUTES_OF_WRITE = (
    route(After("first"), Move("start", role="writer")),
    route(After("result", role="writer", result="written"), Move("start", role="reviewer")),
    route(After("result", role="reviewer", result="more"), Move("start", role="writer")),
    route(After("result", role="reviewer", result="good"), Move("no_more", result="good")),
)
# The command by which a role gives a Result, as a Lane's sentence names it.
GIVES = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"
LAID = Laid(
    version="0.1.0",
    sentences=(
        LaidSentence("agents/writer.md", 2, "Run only `git log --oneline`."),
        LaidSentence("agents/writer.md", 3, "Write only `CHANGELOG.md`."),
        LaidSentence("agents/writer.md", 4, f"End by running `{GIVES} writer written`, as a command of its own."),
    ),
)


def proposal() -> Proposal:
    """The walkthrough's Proposal."""
    lanes = (ROUTES, WRITE_END, run_only(), write_only(), WRITER_END, REVIEW_ONLY, REVIEWER_END)
    return Proposal(lanes=lanes, routes=ROUTES_OF_WRITE, adapters=Adapters(None, None))


def lanes_file() -> LanesFile:
    """The walkthrough's lanes.json, once laid."""
    return LanesFile(proposal=proposal(), laid=LAID)


def proposal_json() -> dict[str, Any]:
    """The walkthrough's Proposal as up writes it, with write's Lanes on its step 1 and the first
    and last of its Routes."""
    return {
        "lanes": [
            {
                "role": "write",
                "file": "skills/write/SKILL.md",
                "step": 1,
                "type": "routes",
                "args": {},
            },
            {
                "role": "write",
                "file": "skills/write/SKILL.md",
                "step": 1,
                "type": "ends_by_result",
                "args": {},
            },
        ],
        "routes": [
            {"skill": "write", "after": {"first": True}, "moves": [{"start": "writer"}]},
            {
                "skill": "write",
                "after": {"role": "reviewer", "result": "good"},
                "moves": [{"no_more": "good"}],
            },
        ],
        "adapters": {},
    }


def start(
    role: str = "writer", agent_id: str | None = "a01", results: tuple[str, ...] = ()
) -> Start:
    return Start(
        role=role,
        text="Carry out your steps",
        values={},
        tool_use_id=f"toolu_{role}",
        agent_id=agent_id,
        results=results,
        ended=False,
    )


def run(
    starts: tuple[Start, ...] = (),
    due: tuple[Move, ...] = (Move("start", role="writer"),),
    skill: str = "write",
    by: str = "person",
    **fields: Any,
) -> Run:
    values: dict[str, Any] = {
        "id": "r1",
        "skill": skill,
        "by": by,
        "words": "",
        "starts": starts,
        "results": (),
        "shown": (),
        "approvals": (),
        "due": due,
        "aside": False,
        "ended": False,
    }
    values.update(fields)
    return Run(**values)


def conversation(*runs: Run) -> Conversation:
    return Conversation(session_id=SESSION, runs=runs)


def due_start(role: str, text: str = "Carry out your steps") -> Due:
    return Due(move=Move("start", role=role), text=text, values={})


def event(name: str, **fields: Any) -> Event:
    values: dict[str, Any] = {"name": name, "session_id": SESSION, "cwd": REPO}
    for field in ("agent_id", "agent_type", "tool_name", "tool_input", "tool_use_id"):
        values[field] = None
    for field in ("tool_response", "prompt", "command_name", "command_args", "last_message"):
        values[field] = None
    values.update(fields)
    return Event(**values)


def payload(name: str, **fields: Any) -> str:
    """A hook event's standard input, as Claude Code hands it."""
    return json.dumps(dict({"hook_event_name": name, "session_id": SESSION, "cwd": REPO}, **fields))


def bash(command: str, cwd: str = REPO) -> Call:
    return Call(tool="Bash", input={"command": command}, cwd=cwd, top=REPO)


def write(path: str, tool: str = "Write") -> Call:
    return Call(tool=tool, input={"file_path": path}, cwd=REPO, top=REPO)


def values(**given: str) -> Mapping[str, str]:
    return given


# writer's Lanes that hold its Steps: its step 1 read whole, tally.py never read, the checklist of
# its step 3, and its Steps marked done in order, by the Lane on its last Step.
READS_WHOLE = lane("writer", "agents/writer.md", 1, "reads_whole", paths=["CHANGELOG.md"])
READS_NONE = lane("writer", "agents/writer.md", 2, "reads_none", paths=["tally.py"])
KEEPS_ITEMS = lane("writer", "agents/writer.md", 3, "keeps_items")
KEEPS_STEPS = lane("writer", "agents/writer.md", 4, "keeps_steps")
# The commands by which a role marks a Step or an Item done, as a Lane's sentence names them.
STEP = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/step.py"
ITEM = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/item.py"


def marked(step: int, item: str | None = None, agent: str | None = "a01") -> Marked:
    """writer's Mark of the Step, or of the Item of that Step, in write's Run."""
    return Marked(run="r1", role="writer", step=step, item=item, agent_id=agent)


def read(first: int, last: int, path: str = "CHANGELOG.md", agent: str | None = "a01") -> Read:
    """writer's Read of the lines of the path, as reads_whole names it, in write's Run."""
    return Read(run="r1", role="writer", path=path, first=first, last=last, agent_id=agent)


def tool(name: str, top: str = REPO, **given: Any) -> Call:
    """A Call of the tool, such as Read, Grep, or Glob, with its input, in the worktree whose top is
    given."""
    return Call(tool=name, input=given, cwd=top, top=top)
