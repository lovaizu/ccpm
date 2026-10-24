"""Tries rn's learner on its own: the real agent and its lanes, started by a stand-in for the
conductor with the prompt `rn.py records` prints, on a session set beforehand that holds two slips
of the conductor's steps. One the record shows: after the user sent the deliverable back with
`/rn:gm`, the README is changed by a commit of the conductor's own, where the skill's steps have the
change written into the work's decisions and turn make the work again. One only a conversation
shows: the conductor asks the user two points in one message. Passes when each is a lesson resting
on its words. Prints the size of each text shown, the stand-in's session, from whose record and its
agent's the trial is judged, the minutes and cost, each tool the learner used, each stop, what
`rn.py learnt` printed, and the quotes of each slip.

    python3 dev/rn/trials/learner/learner.py <new folder>

The folder holds the user's repository with the session on its branch, its remote, and Claude
Code's records for the repository, read by rn.py through CLAUDE_CONFIG_DIR; it is removed with the
copies of rn and turn when the run ends, and the stand-in's records stay in Claude Code's own
folder of its session.
"""

import json
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
)
sys.path.insert(0, os.path.join(ROOT, "dev", "lane"))
sys.path.insert(0, os.path.join(ROOT, "turn", "scripts"))

import records
import trying

BRANCH = "license"
SESSION = ".rn/20261020-license"
FEEDBACK = "The README should say the license is MIT."
# The slip only the conversation shows: two points in one message.
TWO_POINTS = (
    "Two points to decide. 1. Which license should the README name: MIT (recommended, as LICENSE"
    " holds it) or Apache-2.0? 2. Should the README also name who holds the copyright?"
)
# The slip the record shows: the conductor's own commit of the work, after the feedback.
OWN_COMMIT = "README: say MIT, as the user asked"
# The skill text the conductor was given, as Claude Code keeps it where the skill began: the steps
# the slips go against.
SKILL = """Base directory for this skill: {plugin}/skills/up

## Role

You are rn's conductor, the AI in the user's Claude Code conversation that runs rn's commands with
them. Every work is made by turn and read by its first user before the user sees it. You talk with
the user and decide; you fix no work turn returns: a change the user asks for at a sign-off goes
into the work's decisions, and turn goes on from its last step.

## Steps

2. Ask each point to decide in a message of its own, the recommended option first, and keep the
   answer in the decisions before the next.
6. At a sign-off with the user's feedback in the state:
   - Write the change it asks for into `<session>/decisions/<work>.decisions.md`.
   - Keep the move with `rn.py state --message <what it brought>`.
   - Have turn make the work again: run `rn.py ccs <work> ...` and start `turn:up` with the call
     it prints.
"""


def git(*args: str, cwd: str, fed: "str | None" = None) -> str:
    # A machine with no git identity of its own still commits.
    who = ["-c", "user.name=trial", "-c", "user.email=trial@example.invalid"]
    done = subprocess.run(
        ["git", *who, *args], cwd=cwd, check=True, capture_output=True, text=True, input=fed
    )
    return done.stdout


def kept(top: str, message: str, files: dict) -> None:
    """A move kept: the files written, every change committed with the message, and pushed."""
    for name, text in files.items():
        path = os.path.join(top, name)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text if isinstance(text, str) else json.dumps(text, indent=1) + "\n")
    git("add", "-A", cwd=top)
    git("commit", "-q", "--allow-empty", "-F", "-", cwd=top, fed=message)
    git("push", "-q", "-u", "origin", "HEAD", cwd=top)


def state(*facts: dict) -> dict:
    return {"focal_entities": [{"session": SESSION}], "episodic_trace": list(facts)}


def repository(place: str) -> str:
    """The user's repository at place/repo, its remote place/origin.git, with the session on its
    branch: asked, planned, the README made by turn, sent back at the deliverable sign-off, and
    then changed by the conductor's own commit; gives its top."""
    top = os.path.join(place, "repo")
    os.makedirs(top)
    git("init", "-q", "--bare", os.path.join(place, "origin.git"), cwd=place)
    git("init", "-q", "-b", "main", cwd=top)
    git("remote", "add", "origin", os.path.join(place, "origin.git"), cwd=top)
    kept(top, "demo", {"README.md": "# demo\n\ndemo prints a greeting.\n", "LICENSE": "MIT\n"})
    git("remote", "set-head", "origin", "main", cwd=top)
    git("checkout", "-q", "-b", BRANCH, cwd=top)
    s = SESSION
    kept(top, "start: the README names its license", {f"{s}/state.json": {}})
    kept(
        top,
        "asking: the license is MIT; the copyright holder is not named",
        {
            f"{s}/decisions/plan.decisions.md": "# Plan\n\n- The README names the license, MIT.\n"
            "- The copyright holder is not named.\n",
            f"{s}/state.json": state({"answer": "MIT, no copyright holder"}),
        },
    )
    kept(
        top,
        "plan: kept as turn returned it",
        {
            f"{s}/steering.md": "---\npr: https://github.com/o/r/pull/1\nstatus: running\n---\n\n"
            "# License\n\nG1: The README names the license, so users know they may use it.\n\n"
            "## Acceptance criteria\n\n- AC1: The README names the license.\n\n## Tasks\n\n"
            "- [x] T1: The README's license section.\n",
            f"{s}/state.json": state({"signoff": "plan approved"}),
        },
    )
    kept(
        top,
        "readme: turn returned the README",
        {
            "README.md": "# demo\n\ndemo prints a greeting.\n\n## License\n\nSee LICENSE.\n",
            f"{s}/decisions/readme.decisions.md": "# README\n\n- A section `License` points to"
            " LICENSE.\n",
            f"{s}/ccs/readme-result.json": {
                "work": ["README.md"],
                "items": [{"checklist": "readme.md", "item": "B-1", "good": "names LICENSE"}],
                "lessons": [],
                "checked": "every agent of the run",
            },
            f"{s}/state.json": state({"turn": "README returned, every item Good"}),
        },
    )
    proposal = (
        "Deliverable sign-off\nThe finished work is on the pull request:"
        " https://github.com/o/r/pull/1\nAC1: The README names the license.\n"
        "/rn:ty to approve, /rn:gm <feedback> to ask for a change."
    )
    kept(top, f"{proposal}\n\nRn-Sign-off: deliverable", {})
    kept(
        top,
        f"deliverable sent back: {FEEDBACK}",
        {f"{s}/state.json": state({"signoff": "deliverable"}, {"feedback": FEEDBACK})},
    )
    kept(
        top,
        OWN_COMMIT,
        {
            "README.md": "# demo\n\ndemo prints a greeting.\n\n## License\n\nMIT; see LICENSE.\n",
            f"{s}/state.json": state({"signoff": "deliverable"}, {"fixed": "README says MIT"}),
        },
    )
    kept(top, f"{proposal}\n\nRn-Sign-off: deliverable", {})
    return os.path.realpath(top)


def conversation(top: str, plugin: str) -> list:
    """The conductor's conversation, as Claude Code keeps it: asking, then at the deliverable sign-off
    sent back."""

    def entry(kind: str, at: str, content) -> dict:
        return {
            "type": kind,
            "timestamp": f"2026-10-20T10:{at}Z",
            "cwd": top,
            "gitBranch": BRANCH,
            "message": {"role": kind, "content": content},
        }

    def used(at: str, n: int, name: str, given: dict) -> dict:
        use = {"type": "tool_use", "id": f"toolu_{n}", "name": name, "input": given}
        return entry("assistant", at, [use])

    def back(at: str, n: int, text: str) -> dict:
        result = {"type": "tool_result", "tool_use_id": f"toolu_{n}", "content": text}
        return entry("user", at, [result])

    def says(at: str, text: str) -> dict:
        return entry("assistant", at, [{"type": "text", "text": text}])

    rn = f'python3 "{plugin}/scripts/rn.py"'
    skill = SKILL.format(plugin=plugin)
    return [
        {"type": "mode", "mode": "normal"},
        entry(
            "user",
            "00:00.000",
            "<command-name>/rn:up</command-name>\n"
            "<command-args>Put the license in the README</command-args>",
        ),
        {**entry("user", "00:00.010", [{"type": "text", "text": skill}]), "isMeta": True},
        used(
            "00:05.000",
            1,
            "Bash",
            {"command": f"{rn} start license --message 'start: the README names its license'"},
        ),
        back("00:06.000", 1, json.dumps({"session": SESSION, "branch": BRANCH, "base": "main"})),
        says("00:10.000", TWO_POINTS),
        entry("user", "01:00.000", "MIT. No copyright holder."),
        used(
            "01:05.000",
            2,
            "Bash",
            {"command": f"{rn} state --message 'asking: the license is MIT'"},
        ),
        back("01:06.000", 2, json.dumps({"kept": "1a2b3c4"})),
        entry(
            "user",
            "30:00.000",
            f"<command-name>/rn:gm</command-name>\n<command-args>{FEEDBACK}</command-args>",
        ),
        entry(
            "user",
            "31:00.000",
            "<command-name>/rn:up</command-name>\n<command-args></command-args>",
        ),
        {**entry("user", "31:00.010", [{"type": "text", "text": skill}]), "isMeta": True},
        says("31:10.000", "The feedback is one line, so I fix the README myself."),
        used(
            "31:11.000",
            3,
            "Edit",
            {
                "file_path": "README.md",
                "old_string": "See LICENSE.",
                "new_string": "MIT; see LICENSE.",
            },
        ),
        back("31:12.000", 3, "The file README.md has been updated successfully."),
        used("31:15.000", 4, "Bash", {"command": f"{rn} state --message '{OWN_COMMIT}'"}),
        back("31:17.000", 4, json.dumps({"kept": "4f2c9a1"})),
        used("31:20.000", 5, "Bash", {"command": f"{rn} proposal deliverable"}),
        back("31:22.000", 5, "Deliverable sign-off ..."),
    ]


def rn(plugin: str, top: str, env: dict, *args: str) -> str:
    done = subprocess.run(
        ["python3", os.path.join(plugin, "scripts", "rn.py"), *args],
        cwd=top,
        env={**os.environ, **env},
        capture_output=True,
        text=True,
        check=False,
    )
    print(f"rn.py {' '.join(args)} exit {done.returncode}:", done.stdout.strip()[:3000])
    return done.stdout


def size(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        text = f.read()
    return f"{os.path.basename(path)}: {len(text)} characters, {text.count(chr(10))} lines"


place = os.path.abspath(sys.argv[1])
os.makedirs(place)
top = repository(place)
# The copies stand in for the installed plugins, each link as the file it points to, as installing
# does.
plugins = {}
for name in ("turn", "rn"):
    plugins[name] = os.path.join(place, name)
    ignored = shutil.ignore_patterns("__pycache__")
    shutil.copytree(os.path.join(ROOT, name), plugins[name], ignore=ignored)
# Claude Code's records for the repository, in a folder of their own, which rn.py alone is pointed
# at: the stand-in's Claude Code keeps its own where it always does.
config = {"CLAUDE_CONFIG_DIR": os.path.join(place, "config")}
# The folder of the repository's records, named by its path as rn.py finds it.
sys.path.insert(0, os.path.join(plugins["rn"], "scripts"))
import rn as rn_script

os.environ.update(config)
folder = rn_script.project_folders(top)[0]
os.environ.pop("CLAUDE_CONFIG_DIR")
record = os.path.join(folder, "5f0e3c2a-0000-4000-8000-000000000001.jsonl")
os.makedirs(folder)
with open(record, "w", encoding="utf-8") as f:
    f.write("".join(json.dumps(e) + "\n" for e in conversation(top, plugins["rn"])))

prompt = json.loads(rn(plugins["rn"], top, config, "records"))
for path in prompt["record"] + prompt["conversations"]:
    print("size:", size(path))
ask = f"""Start the `rn:learner` agent with the JSON on the line below as its whole prompt, exactly
as it is, and wait for its reply. Then reply with its reply as it is.
{json.dumps(prompt, ensure_ascii=False)}"""
start = time.time()
end = trying.claude(ask, [plugins["turn"], plugins["rn"]], cwd=top, wait=30)
print("minutes:", round((time.time() - start) / 60, 1))
print("session:", end["session_id"], "cost:", end.get("total_cost_usd"))
for path in sorted(trying.agents(end["session_id"])):
    trying.show(path)
out = rn(plugins["rn"], top, config, "learnt")
try:
    learnt = json.loads(out)
except ValueError:
    learnt = {"lessons": []}
quotes = [" ".join(g["quote"].split()) for n in learnt["lessons"] for g in n["grounds"]]
# Each slip as the learner was shown it, the words its quotes are looked for in.
slips = {
    "work changed outside turn": [
        OWN_COMMIT,
        "The feedback is one line, so I fix the README myself.",
    ],
    "two points in one message": [records.said({"type": "text", "text": TWO_POINTS})],
}
for slip, words in slips.items():
    found = [q for q in quotes if any(q in w or w in q for w in words)]
    print(f"{slip}:", found or "no lesson quotes it")
shutil.rmtree(place)
