# Calling Turn

What a plugin gives Turn, how it hands on Turn's questions to the person, and what it gets back, so
you can write the step of your plugin that calls it.

## The call

List Turn in the `dependencies` of your plugin's `.claude-plugin/plugin.json`, as
`"dependencies": ["turn"]`, so installing your plugin installs Turn, and pin with it.

Start the agent `turn:up` in the background, with the request in plain words, such as "the README
of this repository". Turn needs nothing more: it asks the person the kind of work and this work's
purpose.

Where your step has already settled points with the person, add them as one JSON line after the
request, so Turn does not ask them again:

```json
{"request": "the README of this repository",
 "given": {"kind": "readme",
           "goal": {"what": "<who uses the work, and for what>", "grounds": ["the person, 2026-11-03"]},
           "decisions": [{"id": "D1", "what": "<what is decided>", "contributes_to": [],
                          "builds_on": [], "decided": "<what was decided>", "settled_by": "user",
                          "grounds": ["the person, 2026-11-03"]}],
           "work": ["README.md"],
           "run": ".turn/20261103-readme"}}
```

Each key of `given` is optional.

- `kind`: the kind of work, such as `readme`, or one Turn has no template for yet, such as
  `man-page`. Turn takes it without asking.
- `goal`: this work's purpose, in the form of pin's design tree. Turn takes it without asking.
- `decisions`: each other point settled, in the form of pin's design tree. Turn joins each to the
  questions it serves, and builds the rest of the design on it. Leave `contributes_to` empty where
  you do not know the template's questions: Turn joins it.
- `work`: the paths the work is to lie at.
- `run`: the folder Turn keeps the run in, under `.turn/` or where your plugin keeps its own.

## Each message of Turn

Turn's roles run in the background, so `turn:up` ends each time it needs something, and you are
told. Its last message is headed by what to do:

| Headed | Do |
|---|---|
| `For the person:` | Put the rest to the person as it is, and resume `turn:up` by SendMessage with their answer, word for word. |
| `Turn is working:` | Nothing: you are told when `turn:up` ends again. |
| `Done:` | Take the work: the message names its paths, and the run's folder. |
| `For the maker of Turn:` | Turn stopped on a fault of its own. Tell the person, with the message as it is. |

A question is one point, worded so that "yes" takes Turn's recommendation. Put it to the person as
it is: a question changed on the way is answered for something Turn did not ask.

## What comes back

The work's files lie at the paths `Done:` names, not committed. The run's folder holds the design
tree, `design-tree.json`, with each decision and who settled it, and each check, as
`verification/`, so your plugin can show the person what was decided.

## Depth

Claude Code lets subagents start subagents down to three layers below the main conversation.
Turn's roles stand one layer below `turn:up`, and their researchers one more. So start `turn:up`
from the main conversation, or from a subagent one layer below it at most.
