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
    "to": {"type": "string", "description": "the subagent to start next; none where the run ends"}}}},
  "fan_out": {"type": "array", "items": {"type": "string"}, "description": "the subagents the orchestrator may start several runs of at once"},
  "precedence": {"anyOf": [
    {"type": "array", "items": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"}},
    {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"}}}],
   "description": "the results, first to last, the result of runs at once is taken by: one order for every subagent, or one for each, by its name"}}}
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
- `fan_out` names each subagent the orchestrator may start several runs of at once, each a `to` of
  a route. A subagent it does not name runs once at a time, as its steps may not be made for runs
  beside one another.
- `precedence` orders the results, first to last, as [Runs at once](#runs-at-once) takes them: one
  list for every subagent, or an object giving a list for each subagent by its name. An order names
  each result once, and only results a route from its subagent is on. A subagent in `fan_out` that
  gives more than one result has each of them in its order, and `lay.py print` refuses routes where
  one does not, as the result of its runs could not be told otherwise.

`lay.py write` writes the routes into your plugin's `hooks/lanes.json` as the proposal gives them.

For `changelog` with two reviewers at once, each reviewing a part of the commits:

```json
{"orchestrator": "lead", "step": 1, "fan_out": ["reviewer"], "precedence": ["more", "good"],
 "routes": [...]}
```

## Runs at once

The orchestrator decides how many runs of a subagent in `fan_out` it starts, each with its own
prompt, and lane counts the runs it started. A run joins the others where it starts while one of
them still runs. Each run is held to its own values, as [the lanes](lanes.md) say.

- The route counts as taken once every run has ended.
- Where every run gave the same result, that result is the result of the runs.
- Where the runs gave different results, the result of the runs is the one among them that stands
  first in the subagent's order in `precedence`. With `"precedence": ["more", "good"]`, one run's
  `more` gives `more`, however many gave `good`.
- Where the runs gave different results and the order does not hold each of them, lane cannot tell
  the result. It tells the orchestrator and you, as [the lanes](lanes.md#what-each-lane-is-given)
  give an error, that the maker of your plugin must order them in `precedence`. `lay.py print`
  refuses routes that fan out a subagent whose results they do not order, and lane holds the
  routes laid to the same check, so this is met only where the routes are laid again while runs go
  on.
- A run about to end without a result is kept going once, as any subagent is. Where it ends with
  no result still, the orchestrator is told to start the subagent again once the others have
  ended, and the run it starts joins them in place of the one with no result. lane stops a
  message the orchestrator sends to the run with no result, as
  [How a subagent gives its result](#how-a-subagent-gives-its-result) says. A result that run
  gives once resumed by anyone else is kept, but does not count toward the start.
- The orchestrator is told the next start only once every run has ended.

## How a subagent gives its result

A subagent gives a result by running the result script with its own name and the result, as its
step writes the command. Before the command runs, lane checks that a route from the subagent is on
the result, or, where none is from it, that the result is `done`, and stops a command of any other
result with the commands the subagent may run. It then checks that the subagent's work is in the
form its lanes ask, as [the lanes](lanes.md) say for the lanes checked at the end, and stops the
command with what is missing. The result script checks the result again where lane lets the command
through unchecked, as where a value its lanes take is given as `null`. It exits with an error that
names the results the subagent may give, or with none.

- The run counts only where it exits with none. Claude Code then gives the hooks PostToolUse, and
  lane keeps the result. A run stopped, or that exits with an error, which gives
  PostToolUseFailure, keeps nothing, so the subagent mends its work and runs the command again.
- lane matches the command whole against the commands the step writes. A command in any other words
  is a command its lanes do not name, and is stopped.
- A subagent that gives a result twice gives the later one.
- A subagent that is about to end without a result is kept going once, and told the sentence of its
  last step, headed by your plugin's name.
- A subagent resumed with SendMessage keeps its ID, and gives a result again for the resumed run.
- A run that ended with no result, after it was kept going once, is not resumed: the run started
  again in its place gives the result, and a result it gives once resumed by the main conversation
  or another subagent does not count. lane stops the orchestrator's SendMessage to it, before or
  after that start, and tells it the start due, as [What the orchestrator is told](#what-the-orchestrator-is-told)
  gives it.

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
| runs of a subagent in `fan_out` have not all ended | ``Wait for every run of `<plugin>:<name>` to end: you are told the next start once each has.`` |
| the subagent ended with a result whose route has a `to` | ``<name> gave `<on>`. Start `<plugin>:<to>`.`` |
| the subagent ended with a result whose route has no `to` | ``<name> gave `<on>`. Start no more subagents.`` |
| several runs of the subagent ended, giving a result as [Runs at once](#runs-at-once) takes it | ``The <n> runs of <name> gave `<on>`.``, then the start as above |
| the subagent ended with no result, after it was kept going once | ``<name> ended with no result. Start `<plugin>:<name>` again.``, as its start led to no route |

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
wait, and so is a further run of the same subagent where `fan_out` does not name it. The
orchestrator's other calls and its end go on. Once that subagent has ended, Claude
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
- at SubagentStop, as it is about to end, which keeps it going once.

Once kept going, the orchestrator that is about to end again is let end, as a subagent with no
result is. A run held there would go round until a person broke it, which is no check. lane then
tells you, the operator, what is left and whose step must be fixed, as a message Claude Code shows
you:

```
<plugin>: lane let <orchestrator> end with `<plugin>:<name>` still due, as <name> ended with no result: the maker of <plugin> must fix step <n> of <name> in <file>, which gives its result.
```

where the start due is of a subagent that ended with no result, its last step that gives the
result; and

```
<plugin>: lane let <orchestrator> end with `<plugin>:<name>` still due: the maker of <plugin> must fix step <n> of <orchestrator> in <file>, which starts it.
```

otherwise, the orchestrator's step the routes are laid on.

Once no start is left, the orchestrator is free.
