"""Turn the run folders that record.py left into one record for dev/tests/recorded/.

Usage: python3 convert.py <out.jsonl> <setup-event> <what-the-AI-is-asked>
       <run-folder>[:<run-label>] ...

The first line describes the setup: the command, the hooks.json, and each skill and agent of the
plugin. Then each hook payload of each run, in the order it came, is one line, named by what
happened, with each path of the run replaced by <plugin>, <repo>, <transcripts>, <tasks>,
<scratchpad>, or <home>. Where runs are given a label, each event's name ends with it, so that each
name stays unique in its file.
"""

import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
PLUGIN = os.path.join(HERE, "plugin")
HOME = os.path.expanduser("~")
TMP = "/tmp/claude-" + str(os.getuid())
SUMMARY = "<the compaction's summary>"


def slug(path):
    return re.sub(r"[^A-Za-z0-9]", "-", path)


def scrub(text, repo):
    pairs = [
        (os.path.join(HOME, ".claude", "projects", slug(repo)), "<transcripts>"),
        (os.path.join(TMP, slug(repo)), "<tasks>"),
        (repo, "<repo>"),
        (PLUGIN, "<plugin>"),
    ]
    text = re.sub(re.escape(TMP) + r"/[^\s\"`']*?/runs/[\w-]+/repo", "<repo>", text)
    text = re.sub(re.escape(TMP) + r"/[^/\"\s]+/[0-9a-f-]{36}/scratchpad", "<scratchpad>", text)
    for path, name in pairs:
        text = text.replace(path, name)
    return text.replace(HOME, "<home>")


def command(payload):
    return payload["tool_input"].get("command") or payload["tool_input"].get("description")


def label(description):
    """The name of a subagent by the description of its Agent call: sleeper, or sleeper one."""
    return description.lower() if description.startswith("Sleeper ") else "sleeper"


# The name of each event that happens one way, and of each whose name its payload's field picks.
FIXED = {
    "PreCompact": "the person compacts the conversation",
    "PostCompact": "the conversation is compacted",
    "SessionEnd": "the conversation ends",
}
KEYED = {
    "InstructionsLoaded": (
        "load_reason",
        {
            "session_start": "the user's CLAUDE.md loads as the conversation starts",
            "compact": "the user's CLAUDE.md loads again after the compaction",
        },
    ),
    "SessionStart": (
        "source",
        {"startup": "the conversation starts", "compact": "the compacted conversation starts"},
    ),
}


def agent_labels(payloads):
    """The name of each subagent of the run, by its ID, from the PostToolUse of its Agent call."""
    labels = {}
    for each in payloads:
        response = each.get("tool_response")
        if (
            each["hook_event_name"] == "PostToolUse"
            and isinstance(response, dict)
            and "agentId" in response
        ):
            labels[response["agentId"]] = label(each["tool_input"]["description"])
    return labels


class Namer:
    """Names each event of one run, in order, by what happened, as it keeps what was typed last."""

    def __init__(self, payloads, asked):
        self.labels = agent_labels(payloads)
        self.asked = asked
        self.typed = None

    def who(self, agent):
        return self.labels.get(agent, agent)

    def name(self, each):
        kind = each["hook_event_name"]
        if kind in FIXED:
            return FIXED[kind]
        if kind in KEYED:
            field, named = KEYED[kind]
            return named[each[field]]
        if kind == "UserPromptSubmit":
            return self.prompt(each["prompt"])
        if kind == "UserPromptExpansion":
            return f"the typed {each['prompt']} expands"
        if kind in ("PreToolUse", "PostToolUse"):
            return self.tool(kind, each)
        return self.agent_event(kind, each)

    def prompt(self, prompt):
        if prompt.startswith("<task-notification>"):
            done = self.who(re.search(r"<task-id>(\w+)</task-id>", prompt).group(1))
            self.typed = f"the end of {done} reaches it"
            return f"the end of {done} reaches the main conversation"
        if prompt.startswith("/"):
            self.typed = prompt
            return f"the person types {prompt}"
        self.typed = "the request"
        return f"the AI is asked to {self.asked}"

    def tool(self, kind, each):
        if each["tool_name"] == "Agent":
            started = label(each["tool_input"]["description"])
            if kind == "PreToolUse":
                return f"the main conversation starts {started} in the background"
            return f"{started} runs in the background"
        agent = each.get("agent_id")
        who = self.who(agent) if agent else "the main conversation"
        if kind == "PreToolUse":
            return f"{who} runs `{command(each)}`"
        return f"{who}'s `{command(each)}` ran"

    def agent_event(self, kind, each):
        if kind == "SubagentStart":
            return f"{self.who(each['agent_id'])} starts"
        if kind == "SubagentStop" and not each.get("agent_type"):
            return "the compaction's summary ends"
        if kind == "SubagentStop":
            return f"{self.who(each['agent_id'])} ends"
        if kind == "Stop":
            return f"the main conversation stops after {self.typed}"
        return kind


def names(payloads, asked):
    """The name of each event of one run, by what happened, each made unique by its count."""
    namer, found, seen = Namer(payloads, asked), [], {}
    for each in payloads:
        name = namer.name(each)
        seen[name] = seen.get(name, 0) + 1
        found.append(name if seen[name] == 1 else f"{name}, time {seen[name]}")
    return found


def plugin_files():
    found = {}
    for path in sorted(
        glob.glob(os.path.join(PLUGIN, "**", "*"), recursive=True, include_hidden=True)
    ):
        if os.path.isfile(path):
            with open(path) as each:
                text = each.read()
            found[os.path.relpath(path, PLUGIN)] = (
                json.loads(text) if path.endswith(".json") else text
            )
    return found


def main(out, setup, asked, runs):
    with open(os.path.join(runs[0].split(":")[0], "version.txt")) as each:
        version = each.read().strip()
    lines = [
        {
            "event": setup,
            "claude": "claude -p --input-format stream-json --output-format stream-json --verbose"
            " --model haiku --dangerously-skip-permissions --plugin-dir <plugin>",
            "version": version,
            "entry_writes": "each event's one entry runs python3"
            " ${CLAUDE_PLUGIN_ROOT}/hooks/log.py, which appends the payload it reads on stdin to a"
            " file",
            "plugin_files": plugin_files(),
        }
    ]
    for run in runs:
        folder, _, label = run.partition(":")
        repo = os.path.join(folder, "repo")
        with open(os.path.join(folder, "hooks.jsonl")) as log:
            payloads = [json.loads(scrub(text, repo))["payload"] for text in log if text.strip()]
        for payload in payloads:
            if payload["hook_event_name"] == "PostCompact":
                payload["compact_summary"] = SUMMARY
                lines[0]["replaced"] = (
                    "the compaction's summary, which retells the user's own CLAUDE.md and"
                    f" connectors, as {SUMMARY}"
                )
            if payload["hook_event_name"] == "SubagentStop" and not payload.get("agent_type"):
                payload["last_assistant_message"] = SUMMARY
        for name, payload in zip(names(payloads, asked), payloads):
            lines.append({"event": f"{name}, {label}" if label else name, "payload": payload})
    with open(out, "w") as each:
        each.writelines(json.dumps(line, ensure_ascii=False) + "\n" for line in lines)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4:])
