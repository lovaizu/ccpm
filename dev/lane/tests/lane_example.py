"""The example plugin of Lane's cases, `changelog` of Lane's README walkthrough, in a git repository
of the test's own, with the Proposal that up gives for it and what Lane shows and writes for it,
each taken from the walkthrough, which is Lane's specification. Lane serves any plugin, so the
cases use this plugin of their own and no plugin of the repository."""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from typing import Any

from claude_code import Agent, Answer, Conversation, run_python

TOP = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
LANE = os.path.join(TOP, "plugins", "lane")
LAY = os.path.join(LANE, "scripts", "lay.py")

WRITE = """\
---
name: write
description: Has the CHANGELOG.md entries written and reviewed.
---

## Steps

1. Have the entries written and reviewed.
"""

WRITER = """\
---
name: writer
description: Writes the CHANGELOG.md entries for the commits since its last version.
background: true
---

## Steps

1. Read `CHANGELOG.md` to learn its last version and its form.
2. Read the commits since then with `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`.
4. Reply with the entries you wrote.
"""

REVIEWER = """\
---
name: reviewer
description: Reviews the CHANGELOG.md entries that writer wrote.
background: true
---

## Steps

1. Read the new entries in `CHANGELOG.md` against the commits they name.
2. Give `more` when an entry needs the writer again, and `good` when every entry is right.
"""

# The steps as the walkthrough mends them before the second `/lane:up`.
WRITER_STEP_2_MENDED = (
    "2. Read the commits since then with `git log --oneline`, and then read each one with"
    " `git show {commit}`."
)
REVIEWER_STEP_1_MENDED = (
    "1. Read the new entries in `CHANGELOG.md` against the commits since its last version: list"
    " them with `git log --oneline`, and read each one with `git show {commit}`."
)

# Writer's step 2 as the walkthrough writes it, and as a change the person asks for reads.
WRITER_STEP_2 = "2. Read the commits since then with `git log --oneline`."
WRITER_STEP_2_WITH_SHOW = (
    "2. Read the commits since then with `git log --oneline` and `git show {commit}`."
)

# Each lane type, by its name, as Lane's architecture gives them.
TYPES = ("run_only", "write_only", "read_never", "names_printed", "ends_checked", "gives_result")

RESULT = "python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py"


def route(after: str, *moves: dict[str, str]) -> dict[str, Any]:
    """A Route of a Proposal in the form of proposal.schema.json."""
    return {"after": after, "moves": list(moves)}


def lane(role: str, step: int, type: str, *takes: str) -> dict[str, Any]:
    """A Lane of a Proposal in the form of proposal.schema.json."""
    return {"role": role, "step": step, "type": type, "takes": list(takes)}


def start(role: str, waits_for: str = "") -> dict[str, str]:
    """A move that starts the role, waiting for the command where one is given."""
    return {"kind": "start", "role": role, **({"waits_for": waits_for} if waits_for else {})}


NO_MORE = {"kind": "no_more"}

# The Proposal that up gives for the walkthrough's first `/lane:up changelog`.
PROPOSAL: dict[str, Any] = {
    "plugin": "changelog",
    "skill": "write",
    "lanes": [
        lane("write", 1, "gives_result", "good"),
        lane("writer", 2, "run_only", "git log --oneline"),
        lane("writer", 3, "write_only", "CHANGELOG.md"),
        lane("writer", 4, "gives_result", "written"),
        lane("reviewer", 2, "gives_result", "more", "good"),
    ],
    "routes": [
        route("first", start("writer")),
        route("writer written", start("reviewer")),
        route("reviewer more", start("writer")),
        route("reviewer good", NO_MORE),
    ],
}

# The Proposal that up gives once the steps read as the walkthrough mends them.
PROPOSAL_AGAIN: dict[str, Any] = {
    **PROPOSAL,
    "lanes": [
        lane("write", 1, "gives_result", "good"),
        lane("writer", 2, "run_only", "git log --oneline", "git show {commit}"),
        lane("writer", 3, "write_only", "CHANGELOG.md"),
        lane("writer", 4, "gives_result", "written"),
        lane("reviewer", 1, "run_only", "git log --oneline", "git show {commit}"),
        lane("reviewer", 2, "gives_result", "more", "good"),
    ],
}

# What `lay.py print` shows for PROPOSAL, as the walkthrough shows it, its ID as `{id}`.
SHOWN = """\
Routes of write, laid on its step 1:
  first             start writer
  writer `written`  start reviewer
  reviewer `more`   start writer
  reviewer `good`   start no more

1. Have the entries written and reviewed. Start each subagent you are told to start, until you are \
told to start no more. End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py write \
good`.

Lanes of writer, each checked only in writer:
  step 2  run:   Run only `git log --oneline`.  type run_only
  step 3  write: Write only `CHANGELOG.md`.     type write_only
  step 4  end:   End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`.
  commands: writer may run only `git log --oneline` or `python3 \
${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`

2. Read the commits since then with `git log --oneline`. Run only `git log --oneline`.
3. Write the new entries into `CHANGELOG.md`. Write only `CHANGELOG.md`.
4. Reply with the entries you wrote. End by running `python3 \
${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py writer written`.

Lanes of reviewer, each checked only in reviewer:
  step 2  end: End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` \
or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`.

2. Give `more` when an entry needs the writer again, and `good` when every entry is right. End by \
running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 \
${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`.

ID: {id}
Reply yes to lay these into changelog, or say what to change.
"""

# What laying PROPOSAL wrote, as the walkthrough shows it.
WROTE = """\
Wrote step 1 of write into skills/write/SKILL.md.
Wrote steps 2, 3 and 4 of writer into agents/writer.md.
Wrote step 2 of reviewer into agents/reviewer.md.
Wrote the checks of write, writer and reviewer into hooks/hooks.json.
Wrote the lanes laid and the routes into hooks/lanes.json.
Put lane's code in hooks/lane/.
claude plugin validate passed.
"""

# The line by which `lay.py write` ends once it laid a Proposal, as Claude Code loads the hooks
# that Lane laid only as a session starts or once the person types /reload-plugins, and holds them
# from the next prompt, as the records claude-code-2.1.323-hooks-reload.jsonl and
# claude-code-2.1.325-hooks-self-reload.jsonl in dev/tests/recorded/ show.
RELOAD = "Type /reload-plugins, and the checks hold from your next prompt.\n"

# What `lay.py write` prints for PROPOSAL, as the walkthrough shows it.
LAID = WROTE + RELOAD

# The text of a start where the plugin has no adapter of a start's text.
CARRY_OUT = "Carry out your steps"


@dataclass(frozen=True)
class Repo:
    """The test's repository, `tally`'s, and the folder of its plugin `changelog` in it."""

    root: str
    plugin: str
    temp: str


def git(root: str, *args: str) -> str:
    """Runs git in the repository, with no setting of the machine's, and gives what it printed."""
    env = dict(
        os.environ,
        GIT_CONFIG_GLOBAL=os.devnull,
        GIT_CONFIG_NOSYSTEM="1",
        GIT_AUTHOR_NAME="t",
        GIT_AUTHOR_EMAIL="t@example.com",
        GIT_COMMITTER_NAME="t",
        GIT_COMMITTER_EMAIL="t@example.com",
    )
    done = subprocess.run(
        ["git", "-c", "maintenance.auto=false", "-c", "gc.auto=0", *args],
        cwd=root,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return done.stdout


def put(root: str, path: str, text: str) -> str:
    """Writes the text to the file at the path in the folder, making its folders, and gives its
    whole path."""
    whole = os.path.join(root, path)
    os.makedirs(os.path.dirname(whole), exist_ok=True)
    with open(whole, "w", encoding="utf-8") as f:
        f.write(text)
    return whole


def read(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def make_repo(base: str) -> Repo:
    """The repository of `tally`, version 0.1.0 in its CHANGELOG.md and commits since, with the
    plugin `changelog` as the walkthrough's start shows it, in the folder."""
    root = os.path.join(base, "repo")
    temp = os.path.join(base, "tmp")
    os.makedirs(temp)
    os.makedirs(root)
    git(root, "init", "-q", "-b", "main")
    put(root, "CHANGELOG.md", "# Changelog\n\n## [0.1.0]\n\n### Added\n\n- `tally FILE`.\n")
    put(root, "tally.py", "print(0)\n")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "tally 0.1.0")
    put(root, "tally.py", "print(1)\n")
    git(root, "commit", "-q", "-am", "Add --lines")
    return Repo(root, put_plugin(os.path.join(root, "changelog")), temp)


def put_plugin(plugin: str) -> str:
    """Writes `changelog` as the walkthrough's start shows it into the folder, and gives it."""
    put(plugin, ".claude-plugin/plugin.json", json.dumps({"name": "changelog", "version": "0.1.0"}))
    put(plugin, "skills/write/SKILL.md", WRITE)
    put(plugin, "agents/writer.md", WRITER)
    put(plugin, "agents/reviewer.md", REVIEWER)
    return plugin


def environment(repo: Repo) -> dict[str, str]:
    """The environment of the test's Claude Code, its temporary folder the test's own, as TMPDIR
    moves it."""
    return dict(os.environ, TMPDIR=repo.temp)


def conversation(repo: Repo, *plugins: str) -> Conversation:
    """A conversation of the double of Claude Code at the root of the repository, with the plugins
    in the folders loaded, as `claude --plugin-dir` loads each."""
    return Conversation(repo.root, list(plugins), environment(repo), repo.temp)


def proposal_file(repo: Repo, proposal: dict[str, Any], name: str = "proposal.json") -> str:
    """Writes the Proposal, as up writes it, to a file of the test's temporary folder."""
    return put(repo.temp, name, json.dumps(proposal))


def print_command(repo: Repo, path: str) -> str:
    return f"python3 {LAY} print changelog {path}"


def write_command(id: str) -> str:
    return f"python3 {LAY} write changelog {id}"


def id_of(shown: str) -> str:
    """The ID that `lay.py print` showed, or "" where it showed none."""
    found = re.search(r"^ID: (\S+)$", shown, re.MULTILINE)
    return found[1] if found else ""


def shown(id: str) -> str:
    """What `lay.py print` shows for PROPOSAL under the ID."""
    return SHOWN.replace("{id}", id)


def propose(conv: Conversation, repo: Repo, proposal: dict[str, Any]) -> Answer:
    """Up, as the test plays it: writes the Proposal and runs `lay.py print` on it."""
    path = os.path.join(repo.temp, "proposal.json")
    if os.path.exists(path):
        os.remove(path)
    conv.write(None, path, json.dumps(proposal))
    return conv.bash(print_command(repo, path))


def lay(repo: Repo, proposal: dict[str, Any]) -> None:
    """Lays the Proposal into the plugin as a caller who approved it would, through `lay.py print`
    and `lay.py write`, for a case that starts from a plugin laid. Each runs in the test's process,
    as the double runs a command, so that a part that the fixture `broken` takes out is out of it.
    Raises AssertionError with what lay.py said where either gives other than 0."""
    env = environment(repo)
    code, out, err = run_python(
        LAY, ["print", "changelog", proposal_file(repo, proposal)], "", env, repo.root
    )
    assert code == 0, f"lay.py print gave {code}: {out}{err}"
    code, out, err = run_python(LAY, ["write", "changelog", id_of(out)], "", env, repo.root)
    assert code == 0, f"lay.py write gave {code}: {out}{err}"


def result_command(repo: Repo, role: str, result: str) -> str:
    """The command of the laid result.py by which the role gives the result."""
    return f"python3 {os.path.join(repo.plugin, 'hooks', 'lane', 'result.py')} {role} {result}"


def starts(conv: Conversation, role: str, text: str = CARRY_OUT) -> tuple[Answer, Agent | None]:
    """The main conversation starts the role of `changelog` in the background with the text."""
    return conv.start(f"changelog:{role}", text, role)


def gives(repo: Repo, agent: Agent, result: str) -> Answer:
    """The subagent runs result.py with the result and ends; the answer is what the main
    conversation reads beside its end, or what stopped its end."""
    agent.bash(result_command(repo, agent.type.split(":")[-1], result))
    stopped, reached = agent.end(f"Gave {result}.")
    return reached or stopped


def reviewer_after_written(conv: Conversation, repo: Repo) -> Agent:
    """The person types `/changelog:write`, the main conversation starts writer, which gives
    `written`, and then starts reviewer, which runs; gives reviewer's subagent."""
    conv.type("/changelog:write")
    _, writer = starts(conv, "writer")
    assert writer, "writer didn't start"
    gives(repo, writer, "written")
    _, reviewer = starts(conv, "reviewer")
    assert reviewer, "reviewer didn't start"
    return reviewer
