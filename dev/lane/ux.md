# lane UX

lane keeps a plugin's runs on the course its builder set, with two things of its own: the flow and
the lanes. Build and change every part of lane so that the builder gets what this UX says, and judge
each change by its key result.

The plugin's flow definition, a file of its own, sets the course. The course runs through phases,
such as hearing the caller, whoever calls the plugin, and then making the work. Each type of work
goes through its steps in order, such as a subagent making it and then an approval. At an approval,
the run waits until the caller approves something, such as the work before its commit. The rules
every run keeps are part of the course too, such as making a work again three times at most. The
plugin's orchestrator, the AI that runs its work, tells the flow, lane's script, each move before
making it, such as starting a job or going on to the next phase; the flow holds the plugin to the
course by refusing a move that breaks it, and sees no move it is not told. A lane holds one step of
a subagent, one line of its Steps. It is a sentence of that step with a hook that notices when the
AI drifts from it and tells the AI the sentence again.

## Users and goals

- G1: The builder, whoever builds a Claude Code plugin whose work an AI does in several steps, wants
  every run of it to go the course they set, its steps that alone are not sure to hold kept by
  hooks, without writing code that holds the course or checks.

  An AI calls lane for the builder, the builder's Claude or a step of another plugin, by starting
  `lane:up`, lane's agent. A subagent cannot ask a person, so that AI puts
  `lane:up`'s questions to the builder and sends the answers back (dev/architecture.md, Where the
  orchestrator runs).

## Key results

There is one key result, so none is traded against another. It is judged against the version in
use, on the same plugins, with no target value.

- KR1.1: The defects the builder meets using lane as it is; fewer is better, and none once the goal
  is reached.

  Each of these counts as one defect:

  - the flow lets through a move that breaks the plugin's rules, or refuses one they allow;
  - a hook lets through a call that drifts from its sentence, in a form its step names, or stops a
    call the sentence allows;
  - something lane writes into the plugin must be changed or worked around by the builder: the flow
    definition, a step, a setting such as an entry in the plugin's hooks file, or the copy of lane's
    code it puts there.

  Each is work the builder does in lane's place, and one they miss is a run that leaves the course
  they set.

## Scenes

- The builder asks Claude to lay lanes on their plugin; Claude starts `lane:up`.
- `lane:up` reads the plugin's skills and agents, and sends Claude, one at a time, each point the
  files do not settle, such as which files a step alone writes, and each fact it found that the
  proposal rests on; Claude puts each to the builder and sends the answer back.
- `lane:up` proposes the flow definition, its phases, the steps of each type of work and the
  approvals, the orchestrator's steps that tell the flow each move, and the lanes, each under the
  action it keeps, such as run, with the step as it would read and its hooks; the builder chooses OK
  from Claude's question, or says what to change.
- On the OK, `lane:up` writes the flow definition, the orchestrator's steps, the steps the lanes
  hold and the hooks, and puts lane's code in the plugin, once for all its subagents: a link to it
  in a plugin of the ccpm marketplace, a copy with its version anywhere else.
- Run again where an older copy is, `lane:up` brings the copy, the flow definition's form and the
  hooks to its own version.
- In a run, the flow refuses a move that breaks the plugin's rules.

  The flow tells the orchestrator the rule's sentence, prefixed by the plugin's name, and the
  orchestrator goes on as its steps say.
- At an approval, the orchestrator asks the caller with Claude Code's question, AskUserQuestion,
  and the flow goes on only once lane's hook records the OK the caller chose; a question asked in
  plain words, or an answer an AI filled in, leaves no record, and the flow refuses to go on.
  AskUserQuestion is Claude Code's own; lane holds the hook that records the answer and the flow
  that waits for it.
- In a subagent a lane is laid in, a hook stops a call that drifts from the lane before Claude Code
  runs it, and the subagent reads the lane's sentence, prefixed by the plugin's name, and goes on as
  its steps say.

  A hook acts only in the subagent its lane is laid in, so an orchestrator in the main conversation
  is held by the flow and not by hooks; what must hold whatever the AI does, such as a merge, is
  held by GitHub's branch protection or Claude Code's permission rules, not by lane.
- A run stopped anywhere goes on from its last move in a new conversation, as the flow keeps it in a
  file.
- On a machine without Python 3.9 or later, the flow stops the run at its first move and the hooks
  stop the calls they watch, each asking for Python to be installed.

## Benefits

- The builder answers and approves instead of writing code that holds the course or checks;
  holding the course, noticing a drift and telling the sentence are lane's, and already tested.
- Each move the orchestrator tells the flow is held to the same course on every run, and the flow
  passes no approval the caller never chose.
- Hooks stay few, laid only where a step alone is not sure to hold.
