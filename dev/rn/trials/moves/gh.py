"""Stands in for GitHub's `gh` in rn's move trials, for the commands rn and its orchestrator run: the
repository's URL, the pull request created, viewed, edited and marked ready, and the issues created
on lovaizu/ccpm. It keeps the pull request, the issues and every command it was given
in `gh.json`, in the case's folder above its own, and prints what gh would; a command it does not
stand in for it names, exiting 1, as gh does on a failure.

The trial copies it into `<case>/bin/`, beside a `gh` that runs it, first on the PATH Claude Code
runs with."""

import json
import os
import sys

STATE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "gh.json")
REPOSITORY = "https://github.com/trial/demo"
ISSUES = "https://github.com/lovaizu/ccpm/issues"
# The options that take no value.
FLAGS = ("--draft",)


def parsed(args: list) -> tuple:
    """The words of the command that are not options, and each option by its name with its value,
    True for a flag."""
    words, options = [], {}
    k = 0
    while k < len(args):
        arg = args[k]
        if arg.startswith("--") and arg not in FLAGS and k + 1 < len(args):
            options[arg], k = args[k + 1], k + 2
        elif arg.startswith("--"):
            options[arg], k = True, k + 1
        else:
            words.append(arg)
            k += 1
    return words, options


def shown(data, options: dict) -> str:
    """What gh prints of the data for `--json` and `--jq`: the fields asked, or the one field a
    `.field` query names."""
    fields = options.get("--json")
    if isinstance(fields, str):
        names = fields.split(",")

        def pick(d: dict) -> dict:
            return {n: d.get(n) for n in names}

        data = [pick(d) for d in data] if isinstance(data, list) else pick(data)
    query = options.get("--jq")
    if isinstance(query, str):
        value = data.get(query[1:]) if isinstance(data, dict) and query.startswith(".") else None
        return value if isinstance(value, str) else json.dumps(value)
    return json.dumps(data, ensure_ascii=False)


def found(state: dict, words: list) -> dict:
    """The pull request a command names, by number, URL or branch, or the one there is; stops where
    there is none."""
    named = words[2] if len(words) > 2 else None
    for pr in state["prs"]:
        if named is None or named in (str(pr["number"]), pr["url"], pr["headRefName"]):
            return pr
    sys.exit(f"no pull requests found{' for ' + named if named else ''}")


def answer(state: dict, args: list) -> str:
    """What gh prints for the command, the state changed as gh would change GitHub."""
    words, options = parsed(args)
    command = " ".join(words[:2])
    if command == "repo view":
        # The trial's repository takes issues, as rn asks before a work tells a reader to open one.
        return shown({"url": REPOSITORY, "hasIssuesEnabled": True}, options)
    if command == "pr create":
        number = len(state["prs"]) + 1
        state["prs"].append(
            {
                "number": number,
                "url": f"{REPOSITORY}/pull/{number}",
                "headRefName": options.get("--head"),
                "baseRefName": options.get("--base"),
                "title": options.get("--title"),
                "body": options.get("--body"),
                "isDraft": options.get("--draft") is True,
                "state": "OPEN",
            }
        )
        return state["prs"][-1]["url"]
    if command == "pr view":
        return shown(found(state, words), options)
    if command == "pr list":
        head = options.get("--head")
        return shown([p for p in state["prs"] if head in (None, p["headRefName"])], options)
    if command == "pr edit":
        pr = found(state, words)
        pr.update({k[2:]: v for k, v in options.items() if k in ("--title", "--body")})
        return pr["url"]
    if command == "pr ready":
        pr = found(state, words)
        pr["isDraft"] = False
        return f'Pull request trial/demo#{pr["number"]} is marked as "ready for review"'
    if command == "issue create":
        state["issues"].append(
            {k[2:]: options.get(k) for k in ("--repo", "--title", "--body")},
        )
        return f"{ISSUES}/{len(state['issues'])}"
    sys.exit(f"gh stand-in: `gh {' '.join(args)}` is not stood in for")


def main() -> None:
    """Runs the command given, keeping every command and what it changed in gh.json."""
    with open(STATE, encoding="utf-8") as f:
        state = json.load(f)
    state["calls"].append(sys.argv[1:])
    try:
        print(answer(state, sys.argv[1:]))
    finally:
        with open(STATE, "w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
