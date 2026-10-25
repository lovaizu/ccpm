# lane UX

lane lets a plugin's subagents notice when they drift from the steps the building AI set, and tells
them the right way, with lanes. Build and change every part of lane so that the building AI gets
what this UX says, and judge each change by its key result.

A lane is laid on one step of a subagent, one numbered item of its Steps. It is a sentence of that
step with a hook that notices when the subagent drifts from it and tells it the sentence again.

## Users and goals

- G1: The building AI, an AI building a Claude Code plugin whose work an AI does in several steps,
  wants each subagent of that plugin, on every run, to notice when it drifts from one of its steps
  and be told the right way, without writing the checks.

  The building AI, the main conversation or a step of another plugin, calls lane by running its
  layer, `lay.py`, on the lanes it proposes, and approves them itself; no person takes part.

## Key results

There is one key result, so none is traded against another. It has no target value: each version
is judged by how close it brings the building AI to the goal.

- KR1.1: The defects the building AI meets using lane as it is; fewer is better, and none once the
  goal is reached.

  Each of these counts as one defect:

  - a hook lets through a call that drifts from its sentence, in a form its step names, or stops a
    call the sentence allows;
  - something lane writes into the plugin must be changed or worked around by the building AI: a
    step, a setting such as an entry in the plugin's hooks file, or the copy of lane's code it puts
    there.

  Each is work the building AI does in lane's place, and one it misses is a run that drifts from the
  steps it set.

## Scenes

The building AI, `lay.py` and a subagent of the building AI's plugin take part; the proposal is the
file the building AI writes the lanes it proposes in, and the subagent is one with lanes laid in it.

### From proposing lanes to a run that drifts

```mermaid
sequenceDiagram
  participant A as building AI<br/>#lt;AI#gt;
  participant L as lay.py<br/>#lt;script#gt;
  participant S as subagent<br/>#lt;AI, with its hooks#gt;
  Note over A: writes the proposal
  A->>L: print the proposal
  L->>A: the lanes as they would be laid
  A->>L: write the proposal, approved
  Note over L: writes the steps and the hooks, and puts lane's code in the plugin
  Note over S: on a later run of the plugin
  S->>S: a call that drifts from a lane, stopped and told the lane's sentence
```

### Laying lanes

```mermaid
sequenceDiagram
  participant A as building AI<br/>#lt;AI#gt;
  participant L as lay.py<br/>#lt;script#gt;
  opt the plugin has lanes laid before
    A->>L: up on the plugin
    L->>A: the lanes laid before, and lane's code brought up where it was older
  end
  Note over A: writes the proposal
  loop until the building AI approves it
    A->>L: print the proposal
    L->>A: the lanes, each under the action it watches, with the step as it would read and its hooks
    Note over A: changes the proposal, or approves it
  end
  A->>L: write the proposal
  Note over L: writes the steps and the hooks, and puts lane's code in the plugin
```

- Lane's code is put in the plugin once for all its subagents: a link to it in a plugin of the ccpm
  marketplace, a copy with its version anywhere else. Where an older copy is, `lay.py up` brings
  the copy and the hooks to lane's version with the same lanes.

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
  Python to be installed, and at a subagent's end tell the user so and let it end.

### A lane lane cannot check

```mermaid
sequenceDiagram
  participant S as subagent<br/>#lt;AI#gt;
  participant H as hook<br/>#lt;lane's#gt;
  participant A as building AI<br/>#lt;AI, the plugin's maker#gt;
  S->>H: a call a lane holds, where what the lane is given is not as laid
  H-->>S: stopped, the user told the same, with #lt;plugin#gt;: lane cannot check ...: #lt;what is wrong#gt;. Stop here and reply that #lt;who must fix it#gt;.
  S->>A: replies it
  Note over A: fixes the plugin and lays its lanes again with lay.py write
```

- What lane cannot check is never let through: the subagent can only report it, and the plugin's
  maker, or Claude Code where the event is what is wrong, puts it right.

## Benefits

- The building AI proposes and approves lanes instead of writing checks; noticing a drift and
  telling the sentence are lane's, and already tested.
- Hooks stay few, laid only where a step alone is not sure to hold.
