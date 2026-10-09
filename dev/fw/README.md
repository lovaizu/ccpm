# fw: developer guide

How to build a plugin on fw, and how to run fw's tests and trials. Why fw is shaped this way is in
[design.md](design.md).

## Building a plugin on fw

A plugin built on fw writes only its domain parts.

1. Depend on fw in `.claude-plugin/plugin.json`: `"dependencies": ["fw"]`.
2. Write an entry skill that calls the `fw:flow` skill with four lines as its arguments:

    ```
    record: .<plugin>
    domain: ${CLAUDE_PLUGIN_ROOT}/fw
    issues: <owner>/<repository>
    request: $ARGUMENTS
    ```

    `record` is where the steering and each task's CCS are kept and committed in the user's
    repository; `issues` is where the session's process learnings go, once the user agrees.
3. Write the domain folder, `<plugin>/fw/`:

    | File | What it holds |
    |---|---|
    | `conductor.md` | What the plugin makes, the tasks, the receiver and the acceptance, and how to fill and judge; optional |
    | `make.md`, `use.md`, `learn.md` | The instructions each role reads first: what the maker makes, how the work is used, what to learn |
    | `make.json`, `use.json`, `learn.json` | The CCS entries each role needs before it starts, beyond fw's own in `fw/references/`: a list of `{"component", "type", "from"}`, `from` saying where the entry comes from |

`dev/fw/trials/mock/` is a whole plugin built this way, with fixed domain parts.

## Tests

```
python3 -m unittest discover -s dev/fw/tests
```

CI runs them on every push and fails on any line of `fw/scripts/` they do not run.

## Trials

`dev/fw/trials/story.py` runs the mock plugin as its user would, with a stand-in user: the two
cards are made in parallel, the greeting stumbles once and is fixed and rechecked, the conversation
is cleared partway and resumed, and another session works in the same repository meanwhile. It then
checks fw's flow by code (`checks.py`) from the JSONL of every conversation and role and from the
CCS, and prints PASS or FAIL for each check with the JSONL file and entry that shows it.

```
python3 dev/fw/trials/story.py --mode p --out <new directory outside the repository>
python3 dev/fw/trials/story.py --mode pty --out <new directory outside the repository>
python3 dev/fw/trials/checks.py <that directory>      check a finished run again
```

`--mode p` runs each user turn with `claude -p` and clears the conversation by ending it;
`--mode pty` drives a real interactive session (`session.py`), where the user pauses and types
`/clear`. Runs use `--model opus` and a settings file that allows only the tools the run needs.
Delete the output directory, and `~/.claude/projects/<its repository, encoded>/`, when done.
