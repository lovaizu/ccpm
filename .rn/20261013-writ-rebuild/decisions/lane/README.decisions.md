# What lane's README says

The README is read by people deciding whether to use lane: anyone who builds a Claude Code plugin
whose work an AI does in several steps. It is remade on dev/architecture.md, as agreed at 62f0861;
what the agreed lane/README.md (6069bd1) says of lanes holds unless a line here changes it.

## readme

### B-9: The idea it rests on
- lane lets an AI run the course a plugin sets, to the end and at full speed: the flow holds the
  course of the whole work, its phases, the steps of each piece of work and the caller's approvals;
  a lane holds each step that alone is not sure to hold, a sentence of the step with a hook that
  notices a drift from it and tells the AI the sentence again (the user, 2026-10-21: one idea for
  both, said by what it does).

### B-2: Who it is for, B-1: What they gain
- Anyone who builds a Claude Code plugin whose work an AI does in several steps.
- They answer and approve; lane writes the plugin's flow definition and its lanes, and its code
  holds both on every run.

### B-4: Using it on their own work
- The plugin `notes`, whose skill `/notes:changelog` runs its orchestrator in the main conversation
  and starts the subagent `changelog-writer`, whose step 3 writes `CHANGELOG.md`.
- The builder asks Claude in their conversation to lay lanes on `notes`; Claude starts the agent
  `lane:up`, as lane is called by an AI (dev/architecture.md, Where the orchestrator runs).
- `lane:up` reads the plugin's skills and agents, and sends Claude, one at a time, each point the
  files do not settle and each fact it found that the proposal rests on; Claude puts each to the
  builder and sends the answer back.
- It proposes the flow, the phases and the steps of the work with the approval the builder gives
  before the commit, and the lanes on the steps that alone are not sure to hold, each with the step
  as it would read and its hooks.
- On the builder's OK, it writes the flow definition, the steps and the hooks, and lane's code into
  the plugin.
- In a run, the flow refuses the orchestrator's commit before the builder's OK on the changelog, and
  a hook stops `changelog-writer`'s `git commit`; each tells its sentence, prefixed by the plugin's
  name, and the run goes on as its steps say.

### B-3: Why this one
- Each hook tells the step's own sentence, not only a refusal; the lanes stay few, laid only where a
  step alone is not sure to hold; each lane acts only in its subagent; what must hold whatever the AI
  writes is held by branch protection, the sandbox or permission rules (as in 6069bd1).
- The course is held in code, the same on every run: the flow refuses a move that breaks the
  plugin's rules, such as going on before an approval or making a work again past its limit.
- An approval counts only as the OK the caller chose from Claude Code's AskUserQuestion, recorded
  by lane's hook, which refuses a call whose answers an AI filled in (UX.decisions.md, 6a).
- The plan is data the flow walks, which the orchestrator changes as facts come in, each change with
  its reason.
- A run stopped anywhere goes on from its last move in a new conversation, as the flow keeps it in a
  file.
- The builder writes no check and no flow: each is written and tested once, in lane.

### B-5: Started from the README alone, B-8: Getting ready their own way
- Python 3.9 or later, run as `python3`; without it the hooks stop the calls they watch and ask for
  Python to be installed (as in 6069bd1).
- `claude plugin install lane@ccpm`, then ask Claude to lay lanes on the plugin with `lane:up`.
- `lane:up` is called from the main conversation or from an agent it starts, as its own agents take
  the layers below it (subagents docs, Let subagents spawn their own subagents).
- lane's code goes into the plugin's `hooks/lane/`, a link in a plugin of the ccpm marketplace and a
  copy with its version elsewhere, brought up by the next `lane:up` (as in 6069bd1).

### B-6: Where to go next
- The lanes page, each lane under its action and what its hook notices; the flow page, each key of a
  flow definition and what it does; the changelog.
