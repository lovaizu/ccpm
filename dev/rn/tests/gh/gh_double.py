"""The double of `gh` that rn's tests put first on the PATH, as `gh` beside this file, in place of
GitHub's command line, as rn's Test strategy says: each result comes from a line of a record in
recorded/, as the plugin guide's Each result of a double from a record says. gh-2.102.1-auth.jsonl
and gh-2.102.1-pr-view.jsonl are records of runs of gh 2.102.1, its account given as `<account>`;
gh-manual.jsonl takes from gh's manual what no run that changes GitHub could be recorded for. The
double keeps what GitHub would hold, the login, each pull request with its comments, and each issue,
in the JSON file that `RN_GH_STATE` names, which the test sets up, and takes only the commands that
tree.py runs."""

from __future__ import annotations

import json
import os
import sys
from collections.abc import Mapping
from typing import Any

RECORDED = os.path.join(os.path.dirname(os.path.abspath(__file__)), "recorded")
AUTH = "gh-2.102.1-auth.jsonl"
PR_VIEW = "gh-2.102.1-pr-view.jsonl"
MANUAL = "gh-manual.jsonl"
# The branch that the record of a pull request not found names, which the double gives as the
# branch asked for.
RECORDED_BRANCH = "no-such-branch-rn"


def line(record: str, event: str) -> dict[str, Any]:
    """The line of the record in recorded/ that the event names."""
    with open(os.path.join(RECORDED, record), encoding="utf-8") as f:
        return next(each for each in map(json.loads, f) if each["event"] == event)


def state(environ: Mapping[str, str]) -> dict[str, Any]:
    """What GitHub holds for the test, as the file that `RN_GH_STATE` names keeps it: `logged_in`,
    `pulls` by branch, each with its `number`, `draft`, and `comments`, each comment `body` and
    `createdAt`, and `issues`, each `repository`, `title`, and `body`."""
    with open(environ["RN_GH_STATE"], encoding="utf-8") as f:
        return json.load(f)


def keep(environ: Mapping[str, str], held: dict[str, Any]) -> None:
    with open(environ["RN_GH_STATE"], "w", encoding="utf-8") as f:
        json.dump(held, f)


def given(argv: list[str], flag: str) -> str:
    """The value that follows the flag in the arguments, "" where it's absent."""
    return argv[argv.index(flag) + 1] if flag in argv[:-1] else ""


def auth_status(held: dict[str, Any]) -> tuple[int, str, str]:
    """`gh auth status`, with the login that the state holds or without one."""
    if held["logged_in"]:
        ran = line(AUTH, "gh auth status finds the login")
    else:
        ran = line(AUTH, "gh auth status finds no login")
    return ran["exit"], ran["stdout"], ran["stderr"]


def pr_view(argv: list[str], held: dict[str, Any]) -> tuple[int, str, str]:
    """`gh pr view <branch> --json <fields>`, of the pull request that the state holds for the
    branch, in the form of the recorded pull request, its comments in the form of its comment."""
    branch = argv[2]
    pull = held["pulls"].get(branch)
    if pull is None:
        ran = line(PR_VIEW, "gh pr view finds no pull request for the branch")
        return ran["exit"], ran["stdout"], ran["stderr"].replace(RECORDED_BRANCH, branch)
    ran = line(PR_VIEW, "gh pr view gives the pull request with its comments")
    shown = json.loads(ran["stdout"])
    form = shown["comments"][0]
    shown["url"] = pull_url(pull["number"])
    shown["isDraft"] = pull["draft"]
    shown["comments"] = [dict(form, **each) for each in pull["comments"]]
    fields = given(argv, "--json").split(",")
    return ran["exit"], json.dumps({key: shown[key] for key in fields}) + "\n", ""


def pull_url(number: int) -> str:
    """The URL of the pull request of the number, in the form that the manual shows."""
    shown = line(MANUAL, "gh pr create prints the URL of the pull request")["stdout"].strip()
    return shown.rsplit("/", 1)[0] + f"/{number}"


def pr_create(argv: list[str], held: dict[str, Any]) -> tuple[int, str, str]:
    """`gh pr create --draft --head <branch> --title <title> --body <body>`."""
    ran = line(MANUAL, "gh pr create prints the URL of the pull request")
    number = len(held["pulls"]) + 1
    held["pulls"][given(argv, "--head")] = {"number": number, "draft": True, "comments": []}
    return ran["exit"], pull_url(number) + "\n", ""


def pr_ready(argv: list[str], held: dict[str, Any]) -> tuple[int, str, str]:
    """`gh pr ready <branch>`, or `gh pr ready <branch> --undo`, which marks it a draft again."""
    if "--undo" in argv:
        ran = line(MANUAL, "gh pr ready --undo marks the pull request a draft")
    else:
        ran = line(MANUAL, "gh pr ready marks the pull request ready")
    held["pulls"][argv[2]]["draft"] = "--undo" in argv
    return ran["exit"], "", ""


def issue_create(argv: list[str], held: dict[str, Any]) -> tuple[int, str, str]:
    """`gh issue create --repo <repository> --title <title> --body <body>`."""
    ran = line(MANUAL, "gh issue create prints the URL of the issue")
    issue = {"repository": given(argv, "--repo"), "title": given(argv, "--title")}
    held["issues"].append(dict(issue, body=given(argv, "--body")))
    url = ran["stdout"].strip().rsplit("/", 1)[0] + f"/{len(held['issues'])}"
    return ran["exit"], url + "\n", ""


COMMANDS = {
    ("pr", "view"): pr_view,
    ("pr", "create"): pr_create,
    ("pr", "ready"): pr_ready,
    ("issue", "create"): issue_create,
}


def main(argv: list[str], environ: Mapping[str, str]) -> tuple[int, str, str]:
    """The exit code, stdout, and stderr of `gh` with the arguments, as the records show it, the
    state kept after each command that changes it. A command that tree.py doesn't run, and one that
    changes GitHub without a login, fail the test, as no record shows what gh gives for them."""
    held = state(environ)
    if argv[:2] == ["auth", "status"]:
        return auth_status(held)
    command = COMMANDS.get((argv[0], argv[1]) if len(argv) > 1 else ("", ""))
    if command is None:
        raise AssertionError(f"the double of gh takes no such command: gh {' '.join(argv)}")
    assert held["logged_in"], "tree.py runs gh auth status before it changes GitHub"
    done = command(argv, held)
    keep(environ, held)
    return done


if __name__ == "__main__":
    exit_code, printed, said = main(sys.argv[1:], os.environ)
    sys.stdout.write(printed)
    sys.stderr.write(said)
    raise SystemExit(exit_code)
