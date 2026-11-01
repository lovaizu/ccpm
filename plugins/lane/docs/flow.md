# lane's flow

The form your AI declares a flow in, what `flow.py` prints and when, and how it reads what each
subagent answered, so your AI can write the flow of your plugin and you can tell what your
orchestrator is told.

A flow is the order in which one subagent of your plugin, the orchestrator, starts the others, with
the answers that send the work back. `lay.py write` lays it as a follow_next lane, as
[the lanes](lanes.md) give it, on one step of the orchestrator, taking `flow.py`, lane's script. So
the step ends with the sentence

```
Take each move `flow.py` prints, until it prints none.
```

and the orchestrator is told it, headed by your plugin's name, when it drifts from the moves
`flow.py` prints.

## The flow

Your AI writes the flow under the `flow` key of the proposal, held to this JSON Schema:

```json
{"type": "object", "required": ["orchestrator", "step", "order"], "additionalProperties": false,
 "properties": {
  "orchestrator": {"type": "string", "description": "the subagent that starts the others, as its file's name: field"},
  "step": {"type": "integer", "minimum": 1, "description": "the orchestrator's step the flow is laid on"},
  "order": {"type": "array", "minItems": 1, "uniqueItems": true, "items": {"type": "string"},
            "description": "the subagents in the order they start, each as its file's name: field"},
  "back": {"type": "array", "items": {
   "type": "object", "required": ["from", "to", "while"], "additionalProperties": false,
   "properties": {
    "from": {"type": "string", "description": "the subagent whose answer sends the work back"},
    "to": {"type": "string", "description": "the subagent the work goes back to"},
    "while": {"type": "string", "minLength": 1, "description": "the answer that sends it back"}}}}}}
```

- Each subagent `order` names is one of your plugin's, and not the orchestrator. Each subagent
  `back` names is in `order`.
- `to` comes before `from` in `order`, and one subagent is the `from` of one `back` at most.

  So each answer leads to one move.
- `while` is one line: it holds no line break.
- The orchestrator starts each subagent with the Agent tool, so where its file names its tools,
  they include Agent.
- The step of each `from` subagent says to give the answer on a line of its own, such as
  `` End with `more` on a line of its own when an entry needs the writer again. ``

  `flow.py` reads the answer only there, as
  [How flow.py reads the answers](#how-flowpy-reads-the-answers) says.
- The orchestrator may also be in the proposal's `subagents`, with lanes on its other steps. The
  follow_next lane taking `flow.py` is `lay.py write`'s to lay, and `lay.py print` refuses a
  proposal that lays it itself.

`lay.py write` writes the flow into your plugin's `hooks/lanes.json` as the proposal gives it, and
puts into the orchestrator's file where `flow.py` lies, as
[a subagent's part](lanes.md#a-subagents-part) says:

```markdown
`flow.py` below is `python3 "${CLAUDE_PLUGIN_ROOT}/hooks/lane/flow.py"`.
```

## What flow.py prints

The orchestrator runs `flow.py` with no arguments, as a command of its own. `flow.py` prints a line
for the orchestrator to read and, where there is a move, one JSON line after it, the move form
follow_next reads:

```
Start `changelog-reviewer`.
{"tool": "Agent", "input": {"subagent_type": "notes:changelog-reviewer"}}
```

The move holds only the subagent, as Claude Code names a plugin's subagent, `<plugin>:<name>`. The
orchestrator writes the rest of the call, such as its prompt, and follow_next holds only the field
printed.

`flow.py` goes by the subagent of the flow that the orchestrator started last, in a call that came
back:

| Where the run is | `flow.py` prints | Move |
|---|---|---|
| no subagent of the flow started yet | ``Start `<first of order>`.`` | start the first of `order` |
| the last started is the `from` of a `back`, and answered its `while` | ``<from> answered `<while>`: start `<to>` again.`` | start `to` |
| the last started is the `from` of a `back`, and its answer is not kept yet | ``<from> has not answered yet. Run `flow.py` again once its answer has come.`` | none |
| the last started is followed by another in `order` | ``Start `<next in order>`.`` | start the next |
| the last started is the last of `order` | `The flow is done.` | none |

Each row before another wins over it.

An answer not kept yet comes from a subagent started in the background. A subagent that starts
background subagents waits for their results before it finishes in an interactive session, but in
`claude -p` with fork mode off it does not wait
([Let subagents spawn their own subagents](https://code.claude.com/docs/en/sub-agents#let-subagents-spawn-their-own-subagents)).
So in such a run, the orchestrator may end before the answer comes.

Where `flow.py` cannot tell the run, it prints no move. It prints on stderr, and exits 1:

```
<plugin>: lane cannot check the flow of <orchestrator>: <what is wrong>. Ask the main conversation for the fix: <who must fix it>. Go on with the rest of your work meanwhile.
```

It cannot tell the run where the guard, lane's code in your plugin's `hooks/lane/`, has not given
it the run, as [How flow.py reads the answers](#how-flowpy-reads-the-answers) says. Nor can it
where `hooks/lanes.json` holds no flow or is out of its form, or where the calls the guard kept are
not found. follow_next counts
such a run as no run of the script, so what was due before it stays due.

## How flow.py reads the answers

`flow.py` reads what the guard keeps of the run, and nothing the orchestrator writes:

- The guard gives `flow.py` the run. On the orchestrator's call that runs `flow.py` as a command of
  its own, its PreToolUse hook lets the call through with Claude Code's `updatedInput`, the command
  with the session's ID and the orchestrator's ID put before it, as
  `LANE_SESSION=<session_id> LANE_AGENT=<agent_id>`.

  A hook is handed both IDs
  ([Common input fields](https://code.claude.com/docs/en/hooks#common-input-fields)). A command
  the Bash tool runs is handed the session's ID as `CLAUDE_CODE_SESSION_ID`, but not the ID of the
  subagent that runs it
  ([Environment variables](https://code.claude.com/docs/en/env-vars)). `updatedInput` replaces the
  call's input before it runs, combined with `"allow"`
  ([PreToolUse decision control](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)).
  Both IDs come from the event of the call itself, so they cannot belong to another run.
- The guard stops a call that runs `flow.py` together with other commands, and tells the
  orchestrator the sentence and, on the next line, to run `flow.py` as a command of its own.

  `"allow"` skips the permission prompt for the whole command
  ([PreToolUse decision control](https://code.claude.com/docs/en/hooks#pretooluse-decision-control)),
  so it is given to lane's script alone.
- The guard keeps each call of the orchestrator as it comes back, as it keeps every call of a
  subagent with lanes. For an Agent call it keeps the subagent the call started and the `agentId`
  Claude Code gives back in `tool_response`, both for a subagent run in the foreground and for one
  started in the background
  ([Agent](https://code.claude.com/docs/en/hooks#agent)).
- The guard keeps the answer of each `from` subagent, by its ID, as it ends: the `message` of its
  call of SubagentHandback, the tool a subagent in auto mode may hand its report back with, where it
  made one, and else its `last_assistant_message` at its SubagentStop
  ([SubagentStop input](https://code.claude.com/docs/en/hooks#subagentstop-input)).
  Each time it ends, the answer kept before is replaced, so the answer kept is the one it ended
  with. `lay.py write` lays those two hooks on each `from` subagent.

  An Agent call of a background subagent comes back when the subagent starts, and the call of a
  subagent reporting through SubagentHandback gives back a note in place of its report
  ([Agent](https://code.claude.com/docs/en/hooks#agent)). So the answer is taken at the subagent's
  own end. A SubagentStop hook can keep the subagent going
  ([Stop decision control](https://code.claude.com/docs/en/hooks#stop-decision-control)), so its
  answer is kept before the orchestrator is handed it.

A subagent answers a `while` when a line of its answer is that text exactly, case as written, once
the blanks around the line and the Markdown marks `*`, `_` and `` ` `` at its two ends are left out.
So `more`, `**more**` and `` `more` ``, each on a line of its own, answer `more`, and
`No more entries need the writer.` does not.
