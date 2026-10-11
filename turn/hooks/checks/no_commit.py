"""Keep turn's agents from committing or pushing; whether to commit is the calling plugin's to decide."""
import re
import shlex

SEPARATORS = re.compile(r"&&|\|\||[;|&\n()`]|\$\(")
OPTIONS_WITH_VALUE = {"-C", "-c", "--git-dir", "--work-tree", "--namespace", "--config-env", "--exec-path"}


def commits(command):
    for segment in SEPARATORS.split(command):
        try:
            words = shlex.split(segment)
        except ValueError:
            words = segment.split()
        for i, word in enumerate(words):
            if word != "git" and not word.endswith("/git"):
                continue
            rest = words[i + 1:]
            while rest and rest[0].startswith("-"):
                option = rest.pop(0)
                if option in OPTIONS_WITH_VALUE and rest:
                    rest.pop(0)
            if rest[:1] in (["commit"], ["push"]):
                return True
    return False


def check(data, t):
    if not data.get("agent_type", "").startswith("turn:") or data.get("tool_name") != "Bash":
        return []
    if commits((data.get("tool_input") or {}).get("command", "")):
        return ["turn's agents do not commit or push; the calling plugin decides that"]
    return []
