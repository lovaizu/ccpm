"""Which git commands a shell command runs, and where. Only git run as a command counts, and only on
the session's repository: an agent may try the work in a clone of its own, and text such as
`grep 'git push'` runs no git."""
import os
import re
import shlex

from record import root

HEREDOC = re.compile(r"<<-?\s*(['\"]?)([A-Za-z_][A-Za-z0-9_]*)\1")
PREFIX = ("env", "command", "exec", "time", "nohup", "sudo")


def without_heredocs(cmd):
    out, end = [], None
    for line in cmd.split("\n"):
        if end is not None:
            if line.strip() == end:
                end = None
            continue
        out.append(line)
        m = HEREDOC.search(line)
        if m:
            end = m.group(2)
    return "\n".join(out)


def git_runs(cmd, cwd):
    """Each git command the shell command runs, as (subcommand, the directory it acts in)."""
    text = without_heredocs(cmd).replace("\n", " ; ")
    try:
        lex = shlex.shlex(text, posix=True, punctuation_chars=True)
        lex.whitespace_split = True
        tokens = list(lex)
    except ValueError:
        # Quoting the shell takes but shlex does not, such as $'it\'s', is split by hand.
        tokens = re.findall(r"[;&|()]+|[^\s;&|()]+", text)
    runs, dirs, here, words = [], [], cwd, []

    def flush():
        nonlocal here
        w = list(words)
        words.clear()
        while w and (re.match(r"^[A-Za-z_][A-Za-z0-9_]*=", w[0]) or w[0] in PREFIX):
            w.pop(0)
        if not w:
            return
        if w[0] == "cd":
            target = w[1] if len(w) > 1 else "~"
            here = os.path.join(here, os.path.expanduser(target))
        elif os.path.basename(w[0]) == "git":
            d, i = here, 1
            while i < len(w) and w[i].startswith("-"):
                if w[i] == "-C" and i + 1 < len(w):
                    d = os.path.join(d, os.path.expanduser(w[i + 1]))
                    i += 1
                elif w[i] in ("-c", "--git-dir", "--work-tree", "--namespace") and i + 1 < len(w):
                    i += 1
                i += 1
            if i < len(w):
                runs.append((w[i], d))

    for t in tokens:
        if t and set(t) <= set(";&|()<>"):
            flush()
            if "(" in t:
                dirs.append(here)
            if ")" in t and dirs:
                here = dirs.pop()
        else:
            words.append(t)
    flush()
    return runs


def on_repo(runs, subs, top):
    """The subcommands among subs that run on the session's repository."""
    return [s for s, d in runs if s in subs and os.path.isdir(d) and root(d) == top]


def runs_of(data, cwd):
    """The git commands the tool call runs: only a Bash call runs any."""
    if data.get("tool_name") != "Bash":
        return []
    return git_runs((data.get("tool_input") or {}).get("command", ""), cwd)
