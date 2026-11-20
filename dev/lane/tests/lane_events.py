"""How Lane's unit cases make each hook event that Claude Code sends, from the line of a record in
dev/tests/recorded/ that shows it, as dev/lane/claude-code-states.md lists them, made one
conversation's by its session, its folder, its transcript, and the fields of the move; and the
transcript's line that names a skill's base directory, in the form of the transcripts that rn's
E2E runs kept of Claude Code 2.1.327."""

from __future__ import annotations

import json
import os
import re
from typing import Any

from claude_code import (
    AGENT_UNKNOWN_TYPE,
    COMPACT,
    READ,
    REFERENCE,
    RUN,
    SEARCH,
    SEND_MESSAGE,
    SKILL,
    SUBAGENT_OF_SUBAGENT,
    TASK_STOP,
    line,
)

Event = dict[str, Any]


def base_directory(transcript: str, plugin_root: str, skill: str) -> None:
    """Adds to the transcript the user message that Claude Code writes once the skill expands,
    naming its base directory in the plugin's folder."""
    message = {
        "type": "user",
        "isMeta": True,
        "message": {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": f"Base directory for this skill: {plugin_root}/skills/{skill}\n\n"
                    "Start each subagent that Lane gives as due.",
                }
            ],
        },
    }
    os.makedirs(os.path.dirname(transcript), exist_ok=True)
    with open(transcript, "a", encoding="utf-8") as f:
        f.write(json.dumps(message) + "\n")


class Subagent:
    """A subagent of the conversation, by its ID and its agent type."""

    def __init__(self, agent_id: str, agent_type: str):
        self.id = agent_id
        self.type = agent_type

    def fields(self) -> dict[str, str]:
        return {"agent_id": self.id, "agent_type": self.type}


class Events:
    """The hook events of one conversation, in its folder, with its transcript."""

    def __init__(self, cwd: str, transcript: str, session_id: str = "session-1"):
        self.cwd = cwd
        self.transcript = transcript
        self.session_id = session_id

    def made(self, record: str, event: str, fields: dict[str, Any], main: bool = False) -> Event:
        """The recorded payload made this conversation's, with the fields, and with no agent where
        `main` says it's the main conversation's."""
        payload = line(record, event)["payload"]
        payload.update(session_id=self.session_id, cwd=self.cwd, transcript_path=self.transcript)
        if main:
            payload.pop("agent_id", None)
            payload.pop("agent_type", None)
        payload.update(fields)
        return payload

    def by(self, agent: Subagent | None) -> dict[str, str]:
        return agent.fields() if agent else {}

    # The person.

    def typed(self, skill: str, words: str = "") -> Event:
        """The UserPromptExpansion of the skill's command, typed with the words."""
        prompt = f"/{skill} {words}".strip()
        fields = {"prompt": prompt, "command_name": skill, "command_args": words}
        return self.made(RUN, "the typed /lane:up expands", fields)

    def prompt(self, text: str) -> Event:
        """The UserPromptSubmit of what the person types."""
        return self.made(RUN, "a person types /lane:up changelog", {"prompt": text})

    # The main conversation and its subagents.

    def skill_pre(self, skill: str, args: str) -> Event:
        """The PreToolUse of the main conversation's Skill call."""
        use = {"tool_input": {"skill": skill, "args": args}}
        return self.made(SKILL, "the main conversation calls lane:up by the Skill tool", use)

    def skill_post(self, skill: str, args: str) -> Event:
        """The PostToolUse of the main conversation's Skill call."""
        ran = line(SKILL, "the Skill call of lane:up ran")["payload"]["tool_response"]
        use = {"tool_input": {"skill": skill, "args": args}, "tool_response": ran}
        use["tool_response"]["commandName"] = skill
        return self.made(SKILL, "the Skill call of lane:up ran", use)

    def bash(self, command: str, agent: Subagent | None = None) -> Event:
        """The PreToolUse of a Bash call."""
        use = {"tool_input": {"command": command, "description": "Run"}, **self.by(agent)}
        if agent:
            return self.made(RUN, "writer runs git log", use)
        return self.made(RUN, "the main conversation runs lay.py print", use)

    def bash_ran(self, command: str, stdout: str, agent: Subagent | None = None) -> Event:
        """The PostToolUse of a Bash call that printed the output."""
        response = {"stdout": stdout, "stderr": "", "interrupted": False, "isImage": False}
        use = {"tool_input": {"command": command}, "tool_response": response}
        if agent:
            return self.made(RUN, "git log ran", {**use, **agent.fields()})
        return self.made(RUN, "lay.py print ran", use)

    def write(self, path: str, agent: Subagent | None = None, tool: str = "Write") -> Event:
        """The PreToolUse of a Write, or of an Edit, of the file at the path."""
        if tool == "Edit":
            given = line(REFERENCE, "an Edit call's input")["tool_input"]
            tool_input = dict(given, file_path=path)
        else:
            tool_input = {"file_path": path, "content": "x\n"}
        use = {"tool_name": tool, "tool_input": tool_input, **self.by(agent)}
        if agent:
            return self.made(RUN, "writer writes CHANGELOG.md", use)
        return self.made(RUN, "the main conversation runs lay.py print", use)

    def read(self, path: str, agent: Subagent | None = None) -> Event:
        """The PreToolUse of a Read of the file at the path."""
        use = {"tool_input": {"file_path": path}, **self.by(agent)}
        return self.made(READ, "the main conversation runs `Read long.txt`", use)

    def notebook(self, path: str, agent: Subagent | None = None) -> Event:
        """The PreToolUse of a NotebookEdit of the notebook at the path, its `tool_input` naming
        `notebook_path` and `new_source` as Claude Code's tools reference gives them, as no record
        shows a NotebookEdit."""
        tool_input = {"notebook_path": path, "new_source": "x"}
        use = {"tool_name": "NotebookEdit", "tool_input": tool_input, **self.by(agent)}
        if agent:
            return self.made(RUN, "writer writes CHANGELOG.md", use)
        return self.made(RUN, "the main conversation runs lay.py print", use)

    def search(self, tool: str, path: str | None, agent: Subagent | None = None) -> Event:
        """The PreToolUse of a Grep or a Glob, its `tool_input` naming `pattern`, and `path` only
        where the call gives one, as the call gives it, a relative path unresolved."""
        words = "Grep beta path notes" if tool == "Grep" else "Glob *.md path notes"
        if agent:
            event = f"searcher runs `{words}`, in the default tools"
        else:
            event = f"the main conversation runs `{words}`, with the tools named"
        tool_input = {"pattern": "beta" if tool == "Grep" else "*.md"}
        if path is not None:
            tool_input["path"] = path
        use = {"tool_input": tool_input, **self.by(agent)}
        return self.made(SEARCH, event, use, main=not agent)

    def search_ran(self, tool: str, path: str | None, found: list[str], agent: Subagent) -> Event:
        """The PostToolUse of the agent's Grep or Glob, which found the files, by their paths from
        `cwd`."""
        words = "Grep beta path notes" if tool == "Grep" else "Glob *.md path notes"
        event = f"searcher's `{words}` ran, in the default tools"
        ran = line(SEARCH, event)["payload"]
        ran["tool_response"].update(filenames=found, numFiles=len(found))
        tool_input = self.search(tool, path, agent)["tool_input"]
        use = {"tool_input": tool_input, "tool_response": ran["tool_response"], **agent.fields()}
        return self.made(SEARCH, event, use)

    def read_ran(self, path: str, first: int, count: int, total: int, agent: Subagent) -> Event:
        """The PostToolUse of the agent's Read of the file at the path, which read `count` lines
        from the line `first` of its `total`."""
        ran = line(READ, "the main conversation's `Read long.txt` ran")["payload"]
        response = ran["tool_response"]
        response["file"].update(filePath=path, startLine=first, numLines=count, totalLines=total)
        use = {"tool_input": {"file_path": path}, "tool_response": response, **agent.fields()}
        return self.made(READ, "the main conversation's `Read long.txt` ran", use)

    def start(
        self, role: str, use: str, by: Subagent | None = None, prompt: str | None = None
    ) -> Event:
        """The PreToolUse of an Agent call that starts the role in the background, with the prompt
        given, else one that names the role."""
        tool_input = {
            "description": f"Run {role}",
            "prompt": prompt or f"You are {role}.",
            "subagent_type": role,
            "run_in_background": True,
        }
        fields = {"tool_input": tool_input, "tool_use_id": use, **self.by(by)}
        if by:
            return self.made(
                SUBAGENT_OF_SUBAGENT, "writer starts a writer in the background", fields
            )
        return self.made(RUN, "the main conversation starts writer in the background", fields)

    def started(self, agent: Subagent, use: str) -> Event:
        """The PostToolUse of the Agent call that started the agent in the background."""
        ran = line(RUN, "writer runs in the background")["payload"]
        ran["tool_input"]["subagent_type"] = agent.type
        ran["tool_response"]["agentId"] = agent.id
        fields = {"tool_input": ran["tool_input"], "tool_response": ran["tool_response"]}
        return self.made(RUN, "writer runs in the background", {**fields, "tool_use_id": use})

    def start_failed(self, role: str, use: str) -> Event:
        """The PostToolUseFailure of an Agent call that names a subagent type that doesn't
        exist."""
        tool_input = {"subagent_type": role, "run_in_background": True}
        fields = {"tool_input": tool_input, "tool_use_id": use}
        return self.made(AGENT_UNKNOWN_TYPE, "PostToolUseFailure", fields)

    def send(self, to: Subagent, use: str, by: Subagent | None = None) -> Event:
        """The PreToolUse of a SendMessage to the agent."""
        tool_input = {"to": to.id, "summary": "Again", "message": "Again."}
        fields = {"tool_input": tool_input, "tool_use_id": use, **self.by(by)}
        if by:
            event = "writer sends the writer it started a message while it runs"
            return self.made(SUBAGENT_OF_SUBAGENT, event, fields)
        return self.made(
            SEND_MESSAGE, "the main conversation resumes helper by SendMessage", fields
        )

    def resumed(self, to: Subagent, use: str) -> Event:
        """The PostToolUse of a SendMessage that resumed the agent, whose end had come."""
        response = line(SEND_MESSAGE, "the SendMessage call ran")["payload"]["tool_response"]
        response.update(resumedAgentId=to.id, revivedAgentId=to.id)
        fields = {"tool_input": {"to": to.id}, "tool_use_id": use, "tool_response": response}
        return self.made(SEND_MESSAGE, "the SendMessage call ran", fields)

    def queued(self, to: Subagent, use: str) -> Event:
        """The PostToolUse of the main conversation's SendMessage that queued the message to the
        agent, which runs."""
        event = "the message to the running writer is queued"
        response = line(SUBAGENT_OF_SUBAGENT, event)["payload"]["tool_response"]
        response["message"] = response["message"].replace(response["pin"]["id"], to.id)
        response["pin"].update(id=to.id, name=to.id)
        fields = {"tool_input": {"to": to.id}, "tool_use_id": use, "tool_response": response}
        return self.made(SUBAGENT_OF_SUBAGENT, event, fields, main=True)

    def ended(self, agent: Subagent) -> Event:
        """The agent's SubagentStop."""
        fields = {**agent.fields(), "last_assistant_message": "Done.", "stop_hook_active": False}
        return self.made(RUN, "writer ends", fields)

    def summary_ended(self, agent_id: str) -> Event:
        """The SubagentStop of the summary that /compact writes."""
        return self.made(COMPACT, "the compaction's summary ends", {"agent_id": agent_id})

    def stop(self) -> Event:
        """The main conversation's Stop."""
        return self.made(SEND_MESSAGE, "the main conversation stops", {"stop_hook_active": False})

    def reached(self, agent: Subagent, use: str, reply: str = "Done.") -> Event:
        """The UserPromptSubmit of the task-notification of the agent's end, with its reply."""
        prompt = line(RUN, "writer's end reaches the main conversation")["payload"]["prompt"]
        prompt = re.sub(
            r"<result>.*?</result>", f"<result>{reply}</result>", prompt, flags=re.DOTALL
        )
        fields = {"prompt": told(prompt, agent, use)}
        return self.made(RUN, "writer's end reaches the main conversation", fields)

    def killed(self, agent: Subagent, use: str) -> Event:
        """The UserPromptSubmit of the task-notification of the agent stopped by TaskStop."""
        event = "the stopped sleeper's notification reaches the main conversation"
        prompt = line(TASK_STOP, event)["payload"]["prompt"]
        return self.made(TASK_STOP, event, {"prompt": told(prompt, agent, use)})


def told(prompt: str, agent: Subagent, use: str) -> str:
    """The task-notification told of the agent and the Agent call of its start."""
    for tag, value in (("task-id", agent.id), ("tool-use-id", use)):
        prompt = re.sub(rf"<{tag}>.*?</{tag}>", f"<{tag}>{value}</{tag}>", prompt)
    return prompt
