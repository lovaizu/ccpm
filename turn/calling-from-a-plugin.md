# Calling turn from a plugin's step

A step of a plugin hands turn one task: it writes the task in a CCS (Compressed Cognitive State), a
JSON file, calls turn, and decides its next move from the CCS turn writes back. It works like a
function call: the CCS the step writes is the arguments, the CCS turn writes back is the return
value, and its `next` says what to do with it.

This page gives the CCS the step writes, the call, and what to read in the CCS turn writes back,
with the step's move on each `next`. What turn does with the task, and what it needs installed, are
in [turn's README](README.md).

## The CCS the step writes

A CCS has nine parts, and all nine are present, each as a list of entries. Each entry is one kind
and its value as a string: `{"kind": "value"}`. A part may hold several entries, of one kind or of
several. Paths are from the top of the repository.

The first four parts are the step's:

- `focal_entities`:
  - `deliverable`, needed, one or more: where each file of the work goes, a path inside the
    repository. A work is one purpose with one or more files, such as code and its tests, written,
    read and checked together.
  - `receiver`, needed: who the work is for.
- `goal_orientation`:
  - `use`: what the receiver uses the work for.
  - `acceptance`, needed: what the receiver must be able to do with the work.
- `retrieved_artifacts`, each of which must exist:
  - `checklist`, at least one: a checklist the work is made and checked by, in the form turn's
    README gives under Requirements: a file that opens with front matter giving its `name` and
    `version`, and holds items, each one thing the work must give.
  - `content`: a file of what the work says or does, item by item of the checklists.
  - `reference`: a file or a folder the work follows or draws on, such as code it describes or a
    page whose form it follows.
  - `receiver_opens`: a file or a folder the receiver opens with the work, such as a page it links.
- `constraints`:
  - `language`: the language to write in.
  - `rule`: a rule the work or its making follows.

turn and each agent it starts read only the files and folders the CCS names, and stop a read outside
them, so that the work is made without bias. So name everything the work follows or draws on as
`content` or `reference`, and everything the receiver opens with the work as `receiver_opens`.
Before calling, check each `receiver_opens`: that it exists and is what the receiver opens with the
work, since turn reads the work as the receiver with these alone.

A file already at a `deliverable` is written over only when git holds every change to it, or when
it is the work turn returned in the step's last call, unchanged since.

The other five parts are turn's, and the step writes each as an empty list: `predictive_cue`,
`uncertainty_signal`, `semantic_gist`, `relational_map` and `episodic_trace`. turn fills them in the
CCS it writes back, and never changes the step's four.

## The call

The step calls the `turn:up` skill with two lines as its arguments:

- `in: <path>`: the CCS the step wrote.
- `out: <path>`: where turn writes its CCS back. It must not exist yet: turn never writes over a
  file, so if `out` exists, turn writes nothing, ends before any work and says why.

turn runs the same from the main conversation or from inside a subagent: it asks nothing while it
works, and a subagent can start the agents turn starts, as Claude Code's documentation on subagents
says.

turn makes the work in a copy of the repository as it is committed, under `.turn/`, so the tests
and builds the work needs run there as they would where the work goes; the work reaches
`deliverable` when the run returns, and the copy is gone by then.

The step's plugin names `turn` in `dependencies` in its `.claude-plugin/plugin.json`, so that
installing the plugin installs turn.

## A step that calls turn

The step's own text:

```
Write this CCS to .tasks/setup.json, and call the `turn:up` skill with these two lines as its
arguments:

    in: .tasks/setup.json
    out: .tasks/setup-back.json

Then do what `next` in .tasks/setup-back.json asks.
```

The CCS in that example:

```json
{
  "focal_entities": [{"deliverable": "docs/setup.md"},
                     {"receiver": "a developer who has just cloned the project"}],
  "goal_orientation": [{"use": "to get the project running on their machine"},
                       {"acceptance": "they can run the tests without asking anyone"}],
  "retrieved_artifacts": [{"checklist": "checklists/doc.md"},
                          {"content": "notes/setup.content.md"},
                          {"reference": "Makefile"},
                          {"receiver_opens": "CONTRIBUTING.md"}],
  "constraints": [{"language": "English"}],
  "predictive_cue": [], "uncertainty_signal": [], "semantic_gist": [],
  "relational_map": [], "episodic_trace": []
}
```

What happens, in order:

| Who | Does |
|---|---|
| The step | Writes the CCS to `in`, and calls `turn:up` with `in` and `out`. |
| turn | Runs in the same conversation and asks nothing while it works. The user sees its progress there, and may stop it with Esc and say what they want instead. |
| turn | Writes each file of the work where its `deliverable` says, when the run returns, and its CCS to `out`. It never writes `in`. |
| The step | Reads `next` in `out` and does what it asks. |

## What to read in the CCS turn writes back

- `next`, in `predictive_cue`: always one; what the step does next.
- `question`, in `semantic_gist`: one for each question only the user can decide, which the work
  leaves out until it is answered.
- `unmet`, in `semantic_gist`: one for each item of the checklists the work does not yet meet, with
  what the work would need to meet it.
- `rule`, in `semantic_gist`: a change in how such work is made that turn found would meet an item.
- `evidence`, in `episodic_trace`: where in `.turn/` turn keeps, for each item, the lines of the
  work that show it met or what the work would need to meet it, and each checklist's name and
  version.

Every other entry in turn's parts, including all of `uncertainty_signal` and `relational_map`, is
turn's own; the step need not read it.

## What the step does on each `next`

- `done`: the work is where `deliverable` says, and nothing is left for the user. The step moves
  on.
- `ask the user`: the work is where `deliverable` says, with each `question` and `unmet`. The step
  judges the work by its purpose, and puts each question the purpose needs to the user first. Then:
  - where the step can make the work serve the purpose by changing it, such as putting in a user's
    answer of a few lines or taking out a part the receiver does not need, it changes the work and
    moves on;
  - where serving the purpose needs a large change in what turn was given, such as a gap or a
    mistake in the content file, it corrects its own parts or its files and calls turn again.
- `to the caller: <reason>`: an item would be met only by a change in what the step wrote, which
  turn never rewrites. The reason names each such item and the change; the work is where
  `deliverable` says. The step corrects its own parts and calls turn again, or puts the reason to
  the user.
- `stopped: <where>`: the user pressed Esc and said what they want instead. `<where>` is where the
  run was, and what is at `deliverable` is as it was before the run. The step rewrites its own parts
  from the user's words, as if the user had asked so from the start, and calls turn again.

When turn ends before any work, because `out` already exists, python3 or jq is missing, the CCS
cannot be run, or a file at a `deliverable` has changes git does not hold, there is no `next` to
read: turn writes neither the work nor a CCS, and says why in the conversation. The step puts that to
the user.

Each `rule` turn returns is the step's to judge: it may put it into its later tasks as a `rule` in
`constraints`, into its checklist, or leave it.

## Calling turn again

The step writes a new CCS with its own four parts as they now stand, turn's five parts empty, and a
new `out`. turn makes the work anew from it; a file already at `deliverable` is not one of its
inputs. The step calls turn again only when what it gives turn has changed: turn works from those
inputs alone, so a call on the same ones repeats its judgment rather than adding to it.
