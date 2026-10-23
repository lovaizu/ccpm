# lane UX

lane lets a plugin's subagents notice when they drift from the steps their builder set, and tells
them the right way, with lanes. Build and change every part of lane so that the builder gets what
this UX says, and judge each change by its key result.

A lane is laid on one step of a subagent, one line of its Steps. It is a sentence of that step with
a hook that notices when the AI drifts from it and tells the AI the sentence again.

## Users and goals

- G1: The builder, whoever builds a Claude Code plugin whose work an AI does in several steps, wants
  each subagent, on every run, to notice when it drifts from one of its steps and be told the right
  way, without writing the checks.

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

  - a hook lets through a call that drifts from its sentence, in a form its step names, or stops a
    call the sentence allows;
  - something lane writes into the plugin must be changed or worked around by the builder: a step, a
    setting such as an entry in the plugin's hooks file, or the copy of lane's code it puts there.

  Each is work the builder does in lane's place, and one they miss is a run that drifts from the
  steps they set.

## Scenes

The builder, Claude, `lane:up` and a subagent of the builder's plugin take part. Claude is the AI
that calls `lane:up` for the builder; the subagent is one with lanes laid in it.

### From asking to a run that drifts

```mermaid
sequenceDiagram
  participant B as builder<br/>#lt;person#gt;
  participant C as Claude<br/>#lt;AI#gt;
  participant L as lane:up<br/>#lt;agent#gt;
  participant S as subagent<br/>#lt;AI, with its hooks#gt;
  B->>C: asks to lay lanes on their plugin
  C->>L: starts it
  L->>C: the points to decide, one at a time
  L->>C: the lanes proposed
  C->>B: asks for the OK
  B->>C: types /lane:ok
  C->>L: OK
  Note over L: writes the steps and the hooks, and puts lane's code in the plugin
  Note over S: on a later run of the plugin
  S->>S: a call that drifts from a lane, stopped and told the lane's sentence
```

### Laying lanes

```mermaid
sequenceDiagram
  participant B as builder<br/>#lt;person#gt;
  participant C as Claude<br/>#lt;AI#gt;
  participant L as lane:up<br/>#lt;agent#gt;
  C->>L: starts it
  Note over L: reads the plugin's skills and agents
  loop one at a time
    L->>C: a point the files do not settle, or a fact the proposal rests on
    C->>B: puts it to the builder
    B->>C: answer
    C->>L: sends the answer back
  end
  L->>C: the lanes, each under the action it watches, with the step as it would read and its hooks
  C->>B: asks for the OK
  alt OK
    B->>C: types /lane:ok
    C->>L: OK
    Note over L: writes the steps and the hooks, and puts lane's code in the plugin
  else a change asked
    B->>C: what to change
    C->>L: what to change, and the lanes are proposed again
  end
```

- Lane's code is put in the plugin once for all its subagents: a link to it in a plugin of the ccpm
  marketplace, a copy with its version anywhere else. Run again where an older copy is, `lane:up`
  brings the copy and the hooks to its own version.

### A run that drifts

```mermaid
sequenceDiagram
  participant S as subagent<br/>#lt;AI#gt;
  participant H as hook<br/>#lt;lane's#gt;
  S->>H: a call that drifts from a lane
  H-->>S: stopped before Claude Code runs it, and the lane's sentence told again
  S->>H: the call its step says
  H-->>S: let through
```

- The sentence the hook tells is prefixed by the plugin's name.
- A hook acts only in the subagent its lane is laid in; what must hold whatever the AI does, such as
  a merge, is held by GitHub's branch protection or Claude Code's permission rules, not by lane.
- On a machine without Python 3.9 or later, the hooks stop the calls they watch, each asking for
  Python to be installed.

## Benefits

- The builder answers and approves instead of writing checks; noticing a drift and telling the
  sentence are lane's, and already tested.
- Hooks stay few, laid only where a step alone is not sure to hold.
