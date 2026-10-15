# What turn/calling-from-a-plugin.md says

## doc

### B-9: The point from the opening
- A step of a plugin hands turn one task: it writes the task in a CCS (Compressed Cognitive State), a
  JSON file, calls turn, and decides its next move from the CCS turn writes back.
- It works like a function call: the CCS the step writes is the arguments, the CCS turn writes back
  is the return value, and its `next` says what to do with it.
- What turn does with the task, and what it needs installed, are in turn's README (`README.md`).

### B-2: The picture as meant
- A step that calls turn, as the step's own text:
  ```
  Write this CCS to .tasks/setup.json, and call the `turn:up` skill with these two lines as its
  arguments:

      in: .tasks/setup.json
      out: .tasks/setup-back.json

  Then do what `next` in .tasks/setup-back.json asks.
  ```
- The CCS in that example:
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
- What happens: the step writes the CCS to `in` and calls `turn:up` with `in` and `out`; turn runs
  in the same conversation and asks nothing while it works; the user sees its progress there, and
  may stop it with Esc and say what they want instead; turn writes the work where `deliverable`
  says, once it has been read, and its CCS to `out`, and never writes `in`; the step reads `next` in
  `out` and does what it asks.

### B-3: Each idea taken in whole
- `in`: the CCS the step wrote.
- `out`: where turn writes its CCS back. It must not exist yet: if it does, turn writes nothing,
  ends before any work and says why, since it never writes over a file.
- turn runs the same from the main conversation or from inside a subagent: it asks nothing while it
  works, and a subagent can start the agents turn starts (Claude Code's documentation on subagents).
- The step's plugin names `turn` in `dependencies` in its `.claude-plugin/plugin.json`, so that
  installing the plugin installs turn.
- A CCS has nine parts, and all nine are present, each as a list of entries. Each entry is one kind
  and its value as a string: `{"kind": "value"}`. A part may hold several entries, of one kind or of
  several. Paths are from the top of the repository.
- The first four parts are the step's:
  - `focal_entities`: `deliverable`, where the work goes, a path inside the repository, needed;
    `receiver`, who the work is for, needed.
  - `goal_orientation`: `use`, what the receiver uses the work for; `acceptance`, what the receiver
    must be able to do with it, needed.
  - `retrieved_artifacts`: `checklist`, a checklist the work is made and checked by, in the form
    turn's README gives under Requirements: a file that opens with front matter giving its `name`
    and `version`, and holds items, each one thing the work must give; at least one; `content`, a file of what
    the work says or does, item by item of the checklists; `reference`, a file or a folder the work
    follows or draws on, such as code it describes or a page whose form it follows;
    `receiver_opens`, a file or a folder the receiver opens with the work, such as a page it links.
    Each must exist.
  - `constraints`: `language`, the language to write in; `rule`, a rule the work or its making
    follows.
- The other five parts are turn's, each written as an empty list: `predictive_cue` holds `next`;
  `semantic_gist` holds `question`, `unmet` and `rule`; `episodic_trace` holds `evidence` among
  turn's own entries; `uncertainty_signal` and `relational_map` hold turn's own entries.
- turn never changes the step's four parts.
- `next`, in `predictive_cue`: always one; what the step does next.
- `question`, in `semantic_gist`: one for each question only the user can decide, which the work
  leaves out until it is answered.
- `unmet`, in `semantic_gist`: one for each item of the checklists the work does not yet meet, with
  what the work would need to meet it.
- `rule`, in `semantic_gist`: a change in how such work is made that turn found would meet an item.
- `evidence`, in `episodic_trace`: where in `.turn/` turn keeps, for each item, the lines of the work
  that show it met or what the work would need to meet it, and each checklist's name and version.
- turn's other entries are its own; the step need not read them.
- `done`: the work is where `deliverable` says, and nothing is left for the user. The step moves on.
- `ask the user`: the work is where `deliverable` says, with each `question` and `unmet`. The step
  judges the work by its purpose. Where the step can make the work serve the purpose by changing it,
  such as putting in a user's answer of a few lines or taking out a part the receiver does not need,
  it changes it and moves on. Where serving the purpose needs a large change in what turn was given,
  such as a gap or a mistake in the content file, the step corrects its own parts or its files and
  calls turn again. Each question the purpose needs goes to the user first.
- `to the caller: <reason>`: the CCS cannot be run, or an item would be met only by a change in what
  the step wrote, which turn never rewrites. The reason says which; in the second case the work is
  where `deliverable` says. The step corrects its own parts and calls turn again, or puts the reason
  to the user.
- `stopped: <where>`: the user pressed Esc and said what they want instead; `<where>` is where the
  run was, and where the work goes is as it was before the run. The step rewrites its own parts from
  their words, as if the user had asked so from the start, and calls turn again.
- Calling turn again: the step writes a new CCS with its own parts as they now stand, turn's parts
  empty, and a new `out`. turn makes the work anew from it; a file already where the work goes is
  not one of its inputs.
- The step calls turn again only when what it gives turn has changed: turn works from those inputs
  alone, so a call on the same ones repeats its judgment rather than adding to it.
- When turn ends before any work, because `out` already exists, python3 or jq is missing, or the
  file at `deliverable` has changes git does not hold, it writes neither the work nor a CCS, and says
  why in the conversation; the step puts that to the user.
- Each `rule` turn returns is the step's to judge: it may put it into its later tasks as a `rule` in
  `constraints`, into its checklist, or leave it.

### B-5: How far to rely
- That a subagent can start the agents turn starts rests on Claude Code's documentation on subagents.

### B-6: Still true later
- A file already where the work goes is written over only when git holds every change to it, or when
  it is the work turn returned in the step's last call, unchanged since.

### B-11: Read once from the top
- turn and each of its roles read only the files and folders the CCS names, and stop a read outside
  them, saying it is to make the work without bias. So everything the work follows or draws on is
  named as `content` or `reference`, and everything the receiver opens with the work as
  `receiver_opens`.
- The step checks each `receiver_opens` before calling: that it exists and is what the receiver
  opens with the work. turn reads the work as the receiver with these alone.
