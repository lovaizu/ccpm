# Calling turn from a plugin's step

A step of your plugin can hand turn one task: it writes the task in a CCS, a JSON file, calls turn,
and decides its next move from the CCS turn writes back. It works like a function call: the CCS you
write is the arguments, the CCS turn writes back is the return value, and its `next` says what to
do with it. This page gives the call, the CCS you write, and what to read in the one turn writes
back. What turn does with the task, and what it needs installed, are in the
[README](../../README.md).

## A step that calls turn

```markdown
Write this CCS to .tasks/setup.json, and call the `turn:up` skill with these two lines as its
arguments:

    in: .tasks/setup.json
    out: .tasks/setup-back.json

Then do what `next` in .tasks/setup-back.json asks.
```

```json
{
  "focal_entities": [{"deliverable": "docs/setup.md"},
                     {"receiver": "a developer who has just cloned the project"}],
  "goal_orientation": [{"use": "to get the project running on their machine"},
                       {"acceptance": "they can run the tests without asking anyone"}],
  "retrieved_artifacts": [{"viewpoint": "checklists/doc.md"}, {"source": "notes/setup.md"}],
  "constraints": [{"language": "English"}],
  "predictive_cue": [], "uncertainty_signal": [], "semantic_gist": [],
  "relational_map": [], "episodic_trace": []
}
```

What happens, in order:

1. The step writes the CCS to `in` and calls `turn:up` with `in` and `out`.
2. turn runs in the same conversation. The user sees its progress there and may stop it with Esc
   and say what they want instead.
3. turn writes the work where `deliverable` says, once it has been read, and its CCS to `out`. It
   never writes `in`.
4. The step reads `next` in `out` and does what it asks. To run turn again, the step adds to the
   CCS turn wrote and calls turn with it as `in` and a new `out`.

## The call

- `in`: the CCS the step wrote.
- `out`: where turn writes its CCS back. It must not exist yet: if it does, turn writes nothing,
  ends before any work and says why, since it never writes over a file.

Call turn from the main conversation, not from inside a subagent. turn starts agents of its own, and
a subagent cannot start other subagents (Claude Code's documentation on subagents).

Name `turn` in `dependencies` in your plugin's `.claude-plugin/plugin.json`, so that installing your
plugin installs turn.

## The CCS you write

A CCS has nine parts, and all nine are present, each as a list of entries. Each entry is one kind
and its value as a string: `{"kind": "value"}`. A part may hold several entries, of one kind or of
several. Paths are from the top of the repository.

The first four parts are yours:

| Part | Kinds | Needed |
|---|---|---|
| `focal_entities` | `deliverable`: where the work goes, a path inside the repository; a file already there is written over, and must have no change git does not hold; name it as a `source` too to make the work from it; `receiver`: who the work is for | both |
| `goal_orientation` | `use`: what the receiver uses the work for; `acceptance`: what the receiver must be able to do with it | `acceptance` |
| `retrieved_artifacts` | `viewpoint`: a checklist to make and check the work by, a file that must exist; `source`: a file to make the work from, which must exist | `viewpoint` |
| `constraints` | `language`: the language to write in; `rule`: a rule the work or its making follows; `answer`: what the user said, to a question or when stopping a run | none |

The other five parts are turn's: write each as an empty list.

| Part | Kinds turn writes |
|---|---|
| `predictive_cue` | `next` |
| `uncertainty_signal` | `gap` |
| `semantic_gist` | `difference` |
| `relational_map` | turn's own entries |
| `episodic_trace` | `evidence`, among turn's own entries |

turn never changes `focal_entities`, `goal_orientation` or `retrieved_artifacts`, and keeps your
entries first in `constraints`.

## The CCS turn writes back

The step reads four kinds:

- `next`, in `predictive_cue`: always one; what the step does next, below.
- `gap`, in `uncertainty_signal`: one for each question only the user can answer.
- `difference`, in `semantic_gist`: one for each item still More, that is, an item of the
  checklists the work does not yet meet, with why.
- `evidence`, in `episodic_trace`: where in `.turn/` turn keeps, for each item, the lines of the
  work that show it met or why none do.

The other entries are turn's own; the step need not read them, and hands them on as they are when
it calls turn again.

### What `next` asks of the step

- `done`: the work is where `deliverable` says, and nothing is left for the user. The step moves
  on.
- `ask the user`: the work is where `deliverable` says. Put each `gap` and each `difference` to the
  user, add their answers as `answer` entries in `constraints`, and call turn again. If the user
  takes the work as it is, the step moves on.
- `to the caller: <reason>`: the CCS cannot be run, or a cause lies in what the step wrote the work
  should be, which turn never rewrites. The reason says which. The step corrects its own parts and
  calls turn again, or puts the reason to the user.
- `stopped: <where>`: the user pressed Esc and said what they want instead; `<where>` is where the
  run was. Add their words as an `answer` entry and call turn again; the new run starts from the
  work as it stood.

### Rules to carry on

When turn finds a cause in how such work is made, it adds a `rule` entry after yours in
`constraints`. Copy these entries into the CCS of the step's later tasks, so that they are made with
what turn has learned.
