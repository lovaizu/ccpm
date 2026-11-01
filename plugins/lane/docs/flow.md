# lane's flow

The form your AI declares a flow in, what your orchestrator is told and when, and how lane reads
what each subagent answered, so your AI can write the flow of your plugin and you can tell what
your orchestrator is told.

A flow is the order in which one subagent of your plugin, the orchestrator, starts the others, with
the answers that send the work back. `lay.py write` lays it as a follow_flow lane on one step of the
orchestrator, as [the lanes](lanes.md) give it. So the step ends with the sentence

```
Take each move lane tells you, until it tells none.
```

lane tells the orchestrator each move as it starts and as each start of a subagent of the flow
comes back. When the orchestrator does anything but the move due, or is about to end while a move
is due, it is told the sentence, headed by your plugin's name, and the move on the next line.

## The flow

Your AI writes the flow under the `flow` key of the proposal, held to this JSON Schema:

```json
{"type": "object", "required": ["orchestrator", "step", "order"], "additionalProperties": false,
 "properties": {
  "orchestrator": {"type": "string", "description": "the subagent that starts the others, as its file's name: field"},
  "step": {"type": "integer", "minimum": 1, "description": "the orchestrator's step the flow is laid on"},
  "order": {"type": "array", "minItems": 1, "items": {"type": "string"},
            "description": "the subagents in the order they start, each as its file's name: field"},
  "back": {"type": "array", "items": {
   "type": "object", "required": ["from", "to", "while"], "additionalProperties": false,
   "properties": {
    "from": {"type": "integer", "minimum": 1, "description": "the position in order, from 1, whose answer sends the work back"},
    "to": {"type": "integer", "minimum": 1, "description": "the position in order, from 1, the work goes back to"},
    "while": {"type": "string", "minLength": 1, "description": "the answer that sends it back"}}}}}}
```

- Each subagent `order` names is one of your plugin's, and not the orchestrator. A subagent may be
  named more than once, as in write, review, polish, review again.
- A `back` names its `from` and its `to` by their positions in `order`, counted from 1, so a
  subagent named twice is told apart. Each position is one `order` has.
- `to` comes before `from`, and one position is the `from` of one `back` at most.

  So each answer leads to one move.
- `while` is one line: it holds no line break.
- The orchestrator starts each subagent with the Agent tool, so where its file names its tools,
  they include Agent, and `lay.py print` refuses a flow whose orchestrator's file names its tools
  without it.
- The step of each `from` subagent says to give the answer on a line of its own, such as
  `` End with `more` on a line of its own when an entry needs the writer again. ``

  lane reads the answer only there, as [How lane reads the answers](#how-lane-reads-the-answers)
  says.
- The orchestrator may also be in the proposal's `subagents`, with lanes on its other steps. The
  follow_flow lane is `lay.py write`'s to lay, and the proposal names no follow_flow lane itself.

`lay.py write` writes the flow into your plugin's `hooks/lanes.json` as the proposal gives it. It
lays a SubagentStart hook on the orchestrator, which tells it its first move, and a PostToolUse
hook on SubagentHandback on each `from` subagent, which keeps the report it hands back.

## What the orchestrator is told

lane tells the orchestrator the move due at two points, as context Claude Code adds for it to read:

- as it starts, through the SubagentStart hook's `additionalContext`, which Claude Code puts in
  before the subagent's first prompt
  ([SubagentStart](https://code.claude.com/docs/en/hooks#subagentstart));
- as each of its Agent calls starting a subagent of the flow comes back, through the PostToolUse
  hook's `additionalContext`, or PostToolUseFailure's where the call failed, which Claude Code puts
  next to the call's result
  ([Add context for Claude](https://code.claude.com/docs/en/hooks#add-context-for-claude)).

lane writes each line as a statement of the run, as Claude Code's docs advise for this context:

| Where the run is | The orchestrator is told |
|---|---|
| no subagent of the flow has come back yet | ``The next move of the flow is move 1: start `<plugin>:<first>` in the foreground.`` |
| the subagent due came back, and is the `from` of a `back` whose `while` it answered | ``<from> answered `<while>`. The next move of the flow is move <to>: start `<plugin>:<name at to>` in the foreground.`` |
| the subagent due came back, and another follows it in `order` | ``The next move of the flow is move <n>: start `<plugin>:<name at n>` in the foreground.`` |
| the last of `order` came back, and no `back` sends the work back | `The flow is done: lane tells no more moves.` |

`<plugin>:<name>` is how Claude Code names a subagent of your plugin. The orchestrator writes the
rest of the call, such as its prompt.

The move is the Agent call starting the subagent due in the foreground. A call starting it with
`run_in_background` set to `true` is not the move. An Agent call comes back from a subagent run in
the background as the subagent starts, with no answer, and with the status `async_launched` in
place of `completed` ([Agent](https://code.claude.com/docs/en/hooks#agent)). So lane counts only a
start that comes back `completed`.

Claude Code moves a start to the background all the same when you press Ctrl+B, or on its own
once the subagent has run about two minutes where automatic backgrounding is on
([environment variables](https://code.claude.com/docs/en/env-vars), `CLAUDE_AUTO_BACKGROUND_TASKS`).
lane cannot read the answer of such a start, so it cannot tell the next move. It tells the
orchestrator and you, as the call comes back, in the form [the lanes](lanes.md) give an error:

```
<plugin>: lane cannot check follow_flow on step <n> of <orchestrator>: `<plugin>:<due>` came back from the background, where lane cannot read its answer. Ask the main conversation for the fix: whoever runs the plugin must set the environment variable `CLAUDE_CODE_DISABLE_BACKGROUND_TASKS` to `1`, with which Claude Code moves no subagent to the background, and run it again. Go on with the rest of your work meanwhile.
```

From then on in the run, each start of a subagent the flow names is stopped and told the same, as
lane cannot tell which move is due. The orchestrator's other calls and its end go on.

A start that comes back with a status other than `completed` and `async_launched`, or with none,
is not as Claude Code hands it. lane tells it in the form [the lanes](lanes.md) give where the event
is what is wrong, and the move stays due.

While a move is due, the orchestrator is told the sentence and the move on the next line:

- at PreToolUse, on a call that is not the move, which is stopped;
- at SubagentStop, as it is about to end, which keeps it going.

Once the flow is done, the orchestrator is free.

## How lane reads the answers

lane reads what the guard, lane's code in your plugin's `hooks/lane/`, keeps of the run, and
nothing the orchestrator writes:

- The guard keeps each call of the orchestrator as it comes back, as it keeps every call of a
  subagent with lanes. Of an Agent call it keeps the status and the answer of the subagent the
  call started: the final text blocks the call gives back in `tool_response.content`
  ([Agent](https://code.claude.com/docs/en/hooks#agent)).
- A subagent in auto mode may hand its report back with the SubagentHandback tool. Its Agent call
  then gives back a short note in place of the report, and the report is the call's
  `tool_input.message` ([Agent](https://code.claude.com/docs/en/hooks#agent)). So `lay.py write`
  lays a PostToolUse hook on SubagentHandback on each `from` subagent, which keeps that call. The
  answer is the last report the subagent handed back, found by the `agentId` its Agent call gives
  back, where it handed one back.

A subagent answers a `while` when a line of its answer is that text exactly, case as written, once
the blanks around the line and the Markdown marks `*`, `_` and `` ` `` at its two ends are left out.
So `more`, `**more**` and `` `more` ``, each on a line of its own, answer `more`, and
`No more entries need the writer.` does not.
