# Calling Turn

What a plugin gives Turn and what it gets back, so you can write the step of your plugin that
calls it.

## The call

List Turn in the `dependencies` of your plugin's `.claude-plugin/plugin.json`, as
`"dependencies": ["turn"]`, so installing your plugin installs Turn.

Call the skill `turn:up` with the Skill tool, with the request in plain words, such as "the README
of this repository". Turn needs nothing more: it asks the person this work's purpose, and the kind of
work where the request does not name it.

Where your step has already settled points with the person, add them as one JSON line after the
request, so Turn does not ask them again:

```json
{"request": "the README of this repository",
 "given": {"kind": "readme",
           "goal": {"what": "<who uses the work, and for what>", "grounds": ["the person, 2026-11-03"]},
           "decisions": [{"id": "D1", "what": "<what is decided>", "contributes_to": [],
                          "builds_on": [], "decided": "<what was decided>", "settled_by": "maker",
                          "grounds": ["the person, 2026-11-03"]}],
           "work": ["README.md"],
           "run": ".turn/20261103-readme"}}
```

Each key of `given` is optional.

- `kind`: the kind of work, such as `readme`, or one Turn has no best practice for yet, such as
  `man-page`. Turn takes it without asking.
- `goal`: this work's purpose, its `what` and its `grounds`. Turn takes it without asking.
- `decisions`: each other point settled, each with its `decided` and with `settled_by` `maker`, so
  Turn's designer keeps it as given and never asks it again. `contributes_to` names the questions
  or decisions it serves, and `builds_on` the decisions it builds on. Turn writes each into the
  design tree word for word, and the designer builds the rest of the design on it. Leave
  `contributes_to` empty where you do not know the questions of the kind's best practice: the
  designer joins it. Each text is
  one line; a `what` holds no `**`, and a `decided` is not `open`, as the design tree's lines
  cannot hold them, so Turn refuses the call.
- `work`: the paths the work is to lie at.
- `run`: the folder Turn keeps the run in, under `.turn/` or where your plugin keeps its own.

## While Turn runs

Turn runs in the same conversation as your step. It puts each of its points to the person itself,
one at a time, and passes their answers to its roles, so your step passes nothing on. Turn's guard
holds the conversation to Turn's course until Turn hands the work back, so count the call as one
move of your own course, and let your guard hold nothing meanwhile.

Turn ends with a message whose heading says what to do:

| Headed | Do |
|---|---|
| `Done:` | Take the work: the message names its paths, and the run's folder. |
| `For the maker of Turn:` | Turn stopped on a fault of its own. Tell the person, with the message as it is. |

## What comes back

The work's files lie at the paths `Done:` names, and Turn does not commit them. The run's folder
holds the design tree, `design-tree.md`, with each decision and who settled it. It also holds
each check, as `verification/`. So your plugin can show the person what was decided.

## Where to call it

Call Turn from the main conversation, the conversation the person talks in. Only it can put Turn's
points to the person, and Turn's roles then stand one layer below it.
