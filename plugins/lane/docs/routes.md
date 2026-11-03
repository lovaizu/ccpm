# lane's routes

The form your AI declares routes in, how a subagent gives its result, and what your orchestrator is
told and when, so your AI can write the routes of your plugin and you can tell what your
orchestrator is told.

A route names the subagent that one subagent of your plugin, the orchestrator, starts next after
another one ends with a given result. A result is a word, such as `more`, that a subagent gives by
running the result script, which `lay.py write` puts into your plugin's `hooks/lane/`. lane takes
the result from that run, never from what the subagent writes.

`lay.py write` lays the routes as sentences in the steps, as [the lanes](lanes.md) give them. The
orchestrator's step ends with

```
Start each subagent you are told to start, until you are told to start no more.
```

and the last step of each subagent that gives a result ends with the commands it gives them by,
such as

```
End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`.
```

Claude Code puts your plugin's folder in place of `${CLAUDE_PLUGIN_ROOT}` before the subagent reads
the step. Your plugin's own step says when to give which result, such as `` Give `more` when an
entry needs the writer again. ``

## The routes

Your AI writes the routes under the `routes` key of the proposal, held to this JSON Schema:

```json
{"type": "object", "required": ["orchestrator", "step", "routes"], "additionalProperties": false,
 "properties": {
  "orchestrator": {"type": "string", "description": "the subagent that starts the others, as its file's name: field"},
  "step": {"type": "integer", "minimum": 1, "description": "the orchestrator's step the routes are laid on"},
  "routes": {"type": "array", "minItems": 2, "items": {
   "type": "object", "required": ["from"], "additionalProperties": false,
   "properties": {
    "from": {"type": "string", "description": "the subagent that ends, or the orchestrator for the first start"},
    "on": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$", "description": "the result it ends with"},
    "to": {"type": "string", "description": "the subagent to start next; none where the run ends"}}}}}}
```

For `changelog`, whose `lead` starts `writer` and then `reviewer`, and `writer` again while
`reviewer` finds an entry to write again:

```json
{"orchestrator": "lead", "step": 1, "routes": [
 {"from": "lead", "to": "writer"},
 {"from": "writer", "on": "written", "to": "reviewer"},
 {"from": "reviewer", "on": "more", "to": "writer"},
 {"from": "reviewer", "on": "good"}]}
```

- One route is from the orchestrator, with a `to` and no `on`: the first start.
- Every other route is from a subagent of your plugin, not the orchestrator, and has an `on`. Two
  routes from one subagent have different `on`s, so each result leads to one start or to the end.
- Each subagent a `to` names is the `from` of a route, so no started subagent is left without a
  result to give. At least one route has no `to`, so the run can end.
- The orchestrator starts each subagent with the Agent tool, so where its file names its tools,
  they include Agent, and `lay.py print` refuses routes whose orchestrator's file names its tools
  without it.
- The orchestrator may also be in the proposal's `subagents`, with lanes on its other steps.
- Each subagent the routes name, the orchestrator among them, sets `background: true` in its file,
  as [the lanes](lanes.md) say, and `lay.py print` refuses routes where one does not.

`lay.py write` writes the routes into your plugin's `hooks/lanes.json` as the proposal gives them.

## How a subagent gives its result

A subagent gives a result by running the result script with its own name and the result, as its
step writes the command. Before the command runs, lane checks that the subagent's work is in the
form its lanes ask, as [the lanes](lanes.md) say for the lanes checked at the end, and stops the
command with what is missing. The result script checks that a route from the subagent is on the
result, or, where none is from it, that the result is `done`. It exits with an error that names the
results the subagent may give, or with none.

- The run counts only where it exits with none. Claude Code then gives the hooks PostToolUse, and
  lane keeps the result. A run stopped, or that exits with an error, which gives
  PostToolUseFailure, keeps nothing, so the subagent mends its work and runs the command again.
- lane matches the command whole against the commands the step writes. A command in any other words
  is a command its lanes do not name, and is stopped.
- A subagent that gives a result twice gives the later one.
- A subagent that is about to end without a result is kept going once, and told the sentence of its
  last step, headed by your plugin's name.
- A subagent resumed with SendMessage keeps its ID, and gives a result again for the resumed run.

## What the orchestrator is told

lane tells the orchestrator the next start at two points, as context Claude Code adds for it to
read:

- as it starts, through the SubagentStart hook's `additionalContext`, which Claude Code puts in
  before the subagent's first prompt
  ([SubagentStart](https://code.claude.com/docs/en/hooks#subagentstart)), and again as Claude
  Code starts it once more to tell it a subagent it started in the background has ended;
- as each of its Agent calls starting a subagent comes back, through the PostToolUse hook's
  `additionalContext`, or PostToolUseFailure's where the call failed, which Claude Code puts
  next to the call's result
  ([Add context for Claude](https://code.claude.com/docs/en/hooks#add-context-for-claude)).

Each line is headed by your plugin's name:

| Where the run is | The orchestrator is told |
|---|---|
| no subagent has been started yet | ``Start `<plugin>:<to>`.``, the `to` of the orchestrator's route |
| the subagent started in the background has not ended | ``Wait for `<plugin>:<name>` to end: you are told the next start once it has.`` |
| the subagent ended with a result whose route has a `to` | ``<name> gave `<on>`. Start `<plugin>:<to>`.`` |
| the subagent ended with a result whose route has no `to` | ``<name> gave `<on>`. Start no more subagents.`` |
| the subagent ended with no result, after it was kept going once | ``Start `<plugin>:<name>`.``, the same start again, as it led to no route |

`<plugin>:<name>` is how Claude Code names a subagent of your plugin. The orchestrator writes the
rest of the call, such as its prompt.

A start counts once its subagent has ended. Each subagent the routes name runs in the background,
so the orchestrator's Agent call comes back as the subagent starts, with the status
`async_launched` and the `agentId` of its run
([Agent](https://code.claude.com/docs/en/hooks#agent)), and lane counts the start as the subagent
of that `agentId` ends. A call that comes back `completed`, as where the subagent ran in the
foreground, counts as it comes back; its subagent's calls that needed a value given for the run
were stopped meanwhile, as [the lanes](lanes.md) say.

While a started subagent runs in the background, a start of another subagent is stopped and told to
wait, and the orchestrator's other calls and its end go on. Once that subagent has ended, Claude
Code starts the orchestrator again to tell it so, and, as Claude Code 2.1.316 does, may not give it
the line lane's SubagentStart hook tells. The orchestrator then learns the next start where its
next call is not that start: the call is stopped, telling the start.

In `claude -p`, Claude Code 2.1.317 does not start the orchestrator again: the end of the subagent
it started reaches the main conversation instead, and the run stops there. Run a plugin with routes
in an interactive session.

A start that comes back with a status other than `completed` and `async_launched`, or with none,
or with no `agentId`, is not as Claude Code hands it. lane tells it in the form
[the lanes](lanes.md#what-each-lane-is-given) give where the event is what is wrong, and the start
stays due.

While a start is due, the orchestrator is told the sentence and the start on the next line:

- at PreToolUse, on a call that is not that start, which is stopped;
- at SubagentStop, as it is about to end, which keeps it going.

Once no start is left, the orchestrator is free.
