# lane design

lane is built on [how a plugin works](../architecture.md): `/lane:up` is a front that only talks, an
orchestrator that does what lane's flow prints, and one role, the reader, that reads the subagents
and proposes the lanes; a script writes what the builder approved, and the code it lays into the
builder's plugin is the guard of each subagent there. The goal and the key result are in
[lane's UX](ux.md).

## User stories

- As the builder, I want to type `/lane:up`, answer one point at a time, approve the lanes proposed,
  and find the steps and the hooks written into my plugin.
- As the builder, I want `/lane:up`, run where an older copy of lane's code is, to bring the copy
  and the hooks to its own version.
- As the builder, I want my subagent, when a call drifts from a lane, to be stopped and told the
  lane's sentence headed by my plugin's name, and every call the sentence allows let through.
- As the builder, I want the hooks, on a machine without Python 3.9 or later, to stop the calls they
  watch and say to install it.

## Architecture

### Logical view

```mermaid
flowchart TB
  builder["builder<br/>#lt;person#gt;"]
  front["front"]
  orch["orchestrator"]
  flow["flow"]
  state["state"]
  reader["reader"]
  layer["layer"]
  guard["guard"]
  subagent["builder's subagent"]
  builder -->|calls, answers, approves| front
  front -->|asks, shows the proposal| builder
  front -->|starts with the plugin, answers| orch
  orch -->|asks by message, returns what was written| front
  orch -->|asks for the next step| flow
  flow -->|keeps the run in| state
  orch -->|starts with the prompt the flow gave, sends the answers| reader
  reader -->|replies with points, then a proposal| orch
  flow -->|has the approved proposal written by| layer
  layer -->|writes the steps, the hooks and the guard| subagent
  guard -.->|stops a drift, tells the sentence| subagent
```

- The front starts the orchestrator with the plugin the builder is in, and the flow starts a run
  in the state, or goes on with the one there for that plugin.
- The reader reads the plugin's subagents, offers first those changed last, and replies with
  the points the files leave open, each a question with its recommendation or a fact it found with
  where it found it.

  A fact found is shown as a point too, since the proposal rests on it, and a fact the builder
  reads otherwise is assumed in their place.
- The orchestrator sends each point to the front by message, the front puts it to the builder and
  sends back the answer, one point at a time, and the flow keeps each answer in the state.
- With every point settled, the reader proposes, for each step, the lanes it would lay, each under
  its action, with the step as it would read and the hooks; the front shows the proposal, and a
  change the builder asks goes back to the reader.

  A lane is proposed for each sentence of a step whose drift shows in a tool call, such as what
  the subagent reads, writes, runs, hands on or ends with; what shows in no call, such as what it
  weighs, has no lane, since no hook can see it. The builder drops a lane they do not want from
  the proposal.
- On the builder's OK, the layer writes, from the approved proposal alone, each step into its
  subagent's file and each hook into the plugin's hook settings, and puts the guard in the
  plugin; then it checks that the plugin loads.

  What is written must be what was approved, word for word, so code writes it, not an AI.
- Run where the guard in the plugin is older, the flow has the layer replace it and write each hook
  again in the current form, keeping each lane and its sentence.
- In a run of the builder's subagent, the guard reads each tool call as a read, a write, a run, a
  hand on or an end, holds it to that subagent's lanes alone, and stops a drift with
  `<plugin>: <sentence>`.

  Each hook is told which subagent it runs in, so it acts in that subagent alone. A lane on the
  order of steps, such as reading an input whole before writing, is held from what the subagent
  did before in this run, read from its own record.

### Physical view

```
lane/                          the plugin, installed by Claude Code
├── skills/up/SKILL.md         the front <skill>
├── agents/
│   ├── orchestrator.md        <agent>
│   └── reader.md              <agent>
├── scripts/lane.py            the flow and the layer <Python 3>
├── hooks/
│   ├── hooks.json             the lanes on lane's own agents
│   └── lane/                  the guard, laid into each plugin <Python 3>
│       ├── VERSION
│       ├── pretooluse.py      one entry per event
│       ├── subagentstop.py
│       ├── call.py            a tool call read as read, write, run, hand on or end
│       ├── record.py          what the subagent did before, from its record
│       └── lanes/<lane>.py    one check per lane
└── lanes.md                   each lane, under its action, and what its hook notices
```

- lane runs on Claude Code, python3 3.9 or later, git and jq; the reader finds the subagents
  changed last from git, and the layer checks the plugin with `claude plugin validate`.
- The state is a JSON file per plugin in `${CLAUDE_PLUGIN_DATA}/runs/`, which Claude Code keeps
  across lane's updates, so a run stopped anywhere goes on with `/lane:up` in a new conversation.
- The reader replies in a JSON form of its own; the flow keeps it in the state and prints what the
  orchestrator sends next.
- In the builder's plugin, the layer writes one entry for each subagent and event into
  `hooks/hooks.json`, its matcher the tools that subagent's lanes watch, and gives the guard the
  subagent's name, each lane, what it takes and its sentence as the command's arguments; every
  other entry of the file is left as it was.

  The hooks of a plugin's subagent are read only from `hooks/hooks.json`, as Claude Code ignores
  `hooks` in a plugin subagent's own file; a tool event's matcher filters by tool, not by agent, so
  the guard acts only where the event's `agent_type` is `<plugin>:<subagent>`.
- The guard goes into `<plugin>/hooks/lane/`: in a plugin of the ccpm marketplace a relative link
  to lane's, which installing copies into the plugin; anywhere else a copy with its `VERSION`.
- Each entry is a shell command that stops the call, saying to install Python 3.9 or later, where
  `python3` is not there or older.
- A subagent's record is Claude Code's file at the event's `agent_transcript_path`, not a
  documented shape, so the guard's tests hold its shape, as turn's do.
- lane's own agents are kept by lanes too: the reader reads only the plugin's skills, agents and
  hooks and writes nothing, and the orchestrator starts and messages only what the flow printed.

## Verification

### Units

- The guard: each lane stops a drift from its sentence in the forms the steps tell, and lets
  through every call its sentence allows.
  - Flow: unittest in `dev/lane/tests/`, fed the events and records each lane receives, with
    Hypothesis on how a call is read, run by [`dev/check.sh`](../check.sh) with lines and branches
    100% covered and by [`dev/mutate.sh`](../mutate.sh) with no mutant surviving.
- The flow and the layer: each step comes in this design's order, and what is written is the
  approved proposal, with every other entry of `hooks/hooks.json` as it was.
  - Flow: unittest in `dev/lane/tests/` on a plugin made for each test: a new plugin, one with
    hooks of its own, one with an older copy, one in the ccpm marketplace.
- The front, the orchestrator and the reader: each takes its steps in this design's order.
  - Flow: on a plugin with one subagent of three steps, with the builder stood in for by answers
    set beforehand and the reader by replies set beforehand, on Opus 5.5; passes when the JSONL
    shows one point per message, each fact found shown to confirm, and the layer run only after the
    OK.
  - Content: the reader on turn's agents; passes when each proposed lane is one of `lanes.md` and
    each step's drift that shows in a tool call has its lane.

### Acceptance

Each trial runs in a clone of `lovaizu/playground` of its own, on a branch of its own, pushing
nothing, removed after, and is judged from the JSONL of every agent it started.

- Flow: a stand-in for the builder types `/lane:up` on the README's `notes` plugin, answers and
  says OK; the step and the hooks are written and `claude plugin validate --strict` passes.
- Writing the lanes: the files hold the approved steps and hooks word for word.
  - Read from the files against the proposal in the JSONL.
- A drift stopped: `changelog-writer`, given a task that invites a commit, is stopped with
  `notes: Do not commit the OUT.` and ends with the changelog written and uncommitted, and none of
  its other calls is stopped.
  - Read from its JSONL.
- Bringing an older copy up: on the same plugin with the guard of an older version, `/lane:up`
  leaves the current guard and the same lanes in the current form.
  - Read from the files.
- KR1.1: the defects of the UX's KR1.1 met on the README's plugin and on turn's agents.
  - Counted from the JSONL of each trial and the files; this first version sets the measure later
    versions are compared with on the same plugins.

A change is taken when every story is still achieved and KR1.1 does not grow.
