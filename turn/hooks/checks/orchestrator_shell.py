"""During a run, the orchestrator's shell runs only turn's script, and jq, mv and cd on the run's
files, since its steps need no other command, and any other would read or change what the run was
not given."""

import os
import shlex

from checks.inputs import TURN, readable, role, within
from checks.open_run import open_run

UP = os.path.join(TURN, "scripts", "up.py")
OPERATORS = ";&|<>()\n"
# jq's options that take values: how many, and which of them names a file.
JQ = {"--arg": (2, None), "--argjson": (2, None), "--slurpfile": (2, 1), "--rawfile": (2, 1)}
JQ.update({"--indent": (1, None), "-f": (1, 0), "--from-file": (1, 0)})


def check(data):
    if data.get("tool_name") != "Bash" or role(data) != "orchestrator":
        return []
    run = open_run(data)
    if run is None:
        return []
    command = data["tool_input"].get("command", "")
    work = os.path.realpath(os.path.join(data["cwd"], run["work"]))
    if outside(command, os.path.realpath(data["cwd"]), readable(data, run), [work]):
        return [
            (
                "steps 1 to 14: the orchestrator runs only turn's up.py, and jq, mv and cd on the "
                "run's files, since its steps need no other command and any other would read or "
                f"change what the run was not given; read a file with Read. Not run: {command}"
            )
        ]
    return []


def outside(command, top, reads, writes):
    """Whether the command runs anything but turn's script, or jq, mv and cd on the run's files."""
    # A substitution runs a command of its own.
    if "$(" in command or "`" in command:
        return True
    lexer = shlex.shlex(command, posix=True, punctuation_chars=OPERATORS)
    lexer.whitespace = " \t\r"
    try:
        tokens = list(lexer)
    except ValueError:
        return True
    here = top
    for words, redirects in commands(tokens):
        for op, target in redirects:
            if not within(
                os.path.realpath(os.path.join(here, target)), writes if ">" in op else reads
            ):
                return True
        if not words:
            continue
        word, args = words[0], words[1:]
        if word == "cd" and len(args) == 1:
            here = os.path.realpath(os.path.join(here, args[0]))
            files, places = ([] if here == top else [here]), reads
        elif word == "python3" and args[:1] and os.path.realpath(args[0]) == UP:
            files, places = [], reads
        elif word == "jq":
            files, places = jq_files(args), reads
        elif word == "mv":
            files, places = [a for a in args if not a.startswith("-")], writes
        else:
            return True
        if files is None or not all(
            within(os.path.realpath(os.path.join(here, f)), places) for f in files
        ):
            return True
    return False


def commands(tokens):
    """Each command of the line: its words, and each redirect with its target."""
    words, redirects, it = [], [], iter(tokens)
    for token in it:
        if not set(token) <= set(OPERATORS):
            words.append(token)
        elif "<" in token or ">" in token:
            redirects.append((token, next(it, "")))
        else:
            yield words, redirects
            words, redirects = [], []
    yield words, redirects


def jq_files(args):
    """The files jq reads, or None when its arguments cannot be read."""
    files, given, i = [], False, 0
    while i < len(args):
        count, named = JQ.get(args[i], (0, None))
        values = args[i + 1 : i + 1 + count]
        if len(values) < count:
            return None
        if named is not None:
            files.append(values[named])
            given = given or args[i] in ("-f", "--from-file")
        elif args[i].startswith("-") and args[i] != "-":
            pass
        elif given:
            files.append(args[i])
        else:
            given = True
        i += 1 + count
    return files
