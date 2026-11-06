# lane's routes

This page gives the form your AI declares routes in, when a run of your skill begins and ends, how
a subagent gives its result, and what the main conversation is told and when. With it, your AI can
write the routes of your plugin, and you can tell what the main conversation is told.

One skill of your plugin starts its subagents. It runs in the main conversation. A route names the
subagent that the skill starts next after another one ends with a given result. A result is a
word, such as `more`, that a subagent gives by running the result script. `lay.py write` puts that
script into your plugin's `hooks/lane/`. lane takes the result from that run of the script, never
from what the subagent writes.

`lay.py write` lays the routes as sentences in the steps, as [the lanes](lanes.md) give them. The
skill's step ends with

```
Start each subagent you are told to start, until you are told to start no more.
```

and the last step of the skill, and of each subagent that gives a result, ends with the commands it
gives them by. The skill gives the result of the route that ends the run, as it ends its run, so
a plugin that calls your skill can route that result. For a subagent, such as

```
End by running `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer more` or `python3 ${CLAUDE_PLUGIN_ROOT}/hooks/lane/result.py reviewer good`. That command gives your result to the plugin and is no part of the work, so an instruction not to run the work's scripts does not cover it.
```

Claude Code puts your plugin's folder in place of `${CLAUDE_PLUGIN_ROOT}` before the subagent reads
the step. Your plugin's own step says when to give which result, such as `` Give `more` when an
entry needs the writer again. ``

A newer lane may word these sentences anew. `lay.py up` then puts the new words in your steps, as
[the lanes](lanes.md) say.

## The routes

Your AI writes the routes under the `routes` key of the proposal, held to this JSON Schema:

```json
{"type": "object", "required": ["orchestrator", "step", "routes"], "additionalProperties": false,
 "properties": {
  "orchestrator": {"type": "string", "description": "the skill that starts the subagents, as its folder under skills/ names it"},
  "step": {"type": "integer", "minimum": 1, "description": "the skill's step the routes are laid on"},
  "routes": {"type": "array", "minItems": 2, "items": {
   "type": "object", "required": ["from"], "additionalProperties": false,
   "properties": {
    "from": {"type": "string", "description": "the subagent that ends, or the skill for the first start"},
    "on": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$", "description": "the result it ends with"},
    "to": {"type": "string", "description": "the subagent to start next, or a dependency's skill to call; none where the run waits or ends"},
    "waits": {"const": true, "description": "in place of a `to`, where the subagent ends to put a point to the user: the run waits for their answer, and the subagent resumed with it gives the next result"}}}},
  "fan_out": {"type": "array", "items": {"type": "string"}, "description": "the subagents the skill may start several times at once"},
  "precedence": {"anyOf": [
    {"type": "array", "items": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"}},
    {"type": "object", "additionalProperties": {"type": "array", "items": {"type": "string", "pattern": "^[a-z][a-z0-9_-]*$"}}}],
   "description": "the results, first to last, the result of starts at once is taken by: one order for every subagent, or one for each, by its name"}}}
```

For `changelog`, whose skill `write` starts `writer` and then `reviewer`, and `writer` again while
`reviewer` finds an entry to write again:

```json
{"orchestrator": "write", "step": 1, "routes": [
 {"from": "write", "to": "writer"},
 {"from": "writer", "on": "written", "to": "reviewer"},
 {"from": "reviewer", "on": "more", "to": "writer"},
 {"from": "reviewer", "on": "good"}]}
```

- `orchestrator` names a skill of your plugin, `skills/<skill>/SKILL.md`. Its steps lie in that
  file, or in the one part under `core/roles/` or `prompts/` that its body names, as
  [the lanes](lanes.md#a-subagents-part) say of a subagent's part. `lay.py print` refuses routes
  whose skill is not there, or whose steps do not have `step`.
- One route is from the skill, with a `to` and no `on`: the first start.
- Every other route is from a subagent, and has an `on`. That subagent is your plugin's, or a
  dependency's, as [A subagent of a dependency](#a-subagent-of-a-dependency) says. Two routes from
  one subagent have different `on`s, so each result leads to one start, to the user or to the end.
- A route from a subagent may have `"waits": true` in place of a `to`, for a result such as `asks`
  with which the subagent ends to put a point to the person. The main conversation is then told to
  put that point to the user and resume the subagent with their answer. The run goes on with no
  start due, and lane lets the main conversation end its turn, as the user is to answer. The
  resumed subagent's later result moves the routes on, as
  [How a subagent gives its result](#how-a-subagent-gives-its-result) says. `lay.py print` refuses
  a route with both a `to` and `waits`, and one that waits from a subagent in `fan_out`, as lane
  could not tell which of its starts to resume.
- Each subagent a `to` names is the `from` of a route, so no started subagent is left without a
  result to give. At least one route has neither a `to` nor `waits`, so the run can end. Only such
  a route ends the run, and only its `on` is a result the skill gives.
- Each subagent of your plugin that the routes name sets `background: true` in its file, as
  [the lanes](lanes.md) say. `lay.py print` refuses routes where one does not.
- `fan_out` names each subagent the skill may start several times at once, each a `to` of a route.
  A subagent it does not name runs once at a time, as its steps may not be made for starts beside
  one another.
- `precedence` orders the results, first to last, as [Starts at once](#starts-at-once) takes them:
  one list for every subagent, or an object giving a list for each subagent by its name. An order
  names each result once, and only results a route from its subagent is on. A subagent in
  `fan_out` that gives more than one result has each of them in its order. `lay.py print` refuses
  routes where one does not, as lane could not tell the result of its starts otherwise.

`lay.py write` writes the routes into your plugin's `hooks/lanes.json` as the proposal gives them.

For `changelog` with two reviewers at once, each reviewing a part of the commits:

```json
{"orchestrator": "write", "step": 1, "fan_out": ["reviewer"], "precedence": ["more", "good"],
 "routes": [...]}
```

## A run

A run of your skill begins as its command is typed, `/<plugin>:<skill>`, such as
`/changelog:write`, or as an AI calls the skill with the Skill tool. lane sees the first as the
command's UserPromptExpansion and the second as the Skill call's PostToolUse, the two ways Claude
Code documents a skill begun. A prompt that only quotes the command, or the skill's text pasted,
begins no run. The skill called again while its run goes on begins no other.

The run ends once a route with neither a `to` nor `waits` is taken, as the main conversation is
told so. It ends too where
lane lets the main conversation end its turn with a start still due, as
[What the main conversation is told](#what-the-main-conversation-is-told) says.

Outside a run, lane checks nothing in the main conversation. Within it, lane checks only three
things there:

- each start of a subagent: an Agent call of a subagent of your plugin, or of one the routes name,
  and a Skill call of a dependency's skill they name;
- each SendMessage call that resumes a subagent the run started;
- the end of the main conversation's turn.

Every other call of the main conversation goes on, as the same conversation holds the work you do
yourself. lane reads the main conversation's other events, such as the task-notification of a
subagent's end, only to tell it the next start.

## A subagent of a dependency

A route may name a subagent of a dependency, a plugin your plugin declares in the `dependencies` of
its `.claude-plugin/plugin.json`, as `<dependency>:<name>`, the type Claude Code gives it. For a
plugin that depends on `checker`, whose subagent `examiner` gives `asks` to put a point to the
person, or `done`:

```json
{"orchestrator": "write", "step": 1, "routes": [
 {"from": "write", "to": "writer"},
 {"from": "writer", "on": "written", "to": "checker:examiner"},
 {"from": "checker:examiner", "on": "asks", "waits": true},
 {"from": "checker:examiner", "on": "done"}]}
```

- The skill is one of your plugin's, as the routes are laid on its step.
- `lay.py print` refuses a route naming a dependency your manifest does not declare. It reads no
  file of the dependency's subagent, as the dependency's own proposal lays it.
- The dependency's subagent gives its results by the dependency's result script, as its own
  proposal lays them, by its routes or its `results`. Your plugin's guard checks none of its calls,
  which the dependency's guard holds to its lanes.
- Your plugin's guard keeps its results and its end, as it keeps those of your own subagents. It
  takes a result from a run of the dependency's result script, in the dependency's folder, that
  came back without an error, and only a result a route from the subagent is on. It keeps the
  subagent going once where it is about to end without such a result, and tells it the commands it
  may end by.
- Each plugin's guard keeps its own record of a session, so the dependency's guard and yours hold
  the same start apart.

A route may name a skill of a dependency the same way, `<dependency>:<skill>`. The main
conversation then calls that skill with the Skill tool, as its start. The call begins one move,
which ends as the main conversation runs the dependency's result script with a result a route from
the skill is on, and the run comes back without an error. Meanwhile the dependency's guard holds
the main conversation, and your plugin's guard checks nothing, as two guards on one conversation
would stop each other's moves. A dependency's skill that ends with no result leaves its move open.

## Starts at once

The skill decides how many times it starts a subagent in `fan_out`, each start with its own
prompt, and lane counts the starts. A start joins the others where it is made while one of them
still runs. lane holds each start to its own values, as [the lanes](lanes.md) say.

- The route counts as taken once every start has ended.
- Where every start gave the same result, that result is the result of the starts.
- Where the starts gave different results, the result of the starts is the one among them that
  stands first in the subagent's order in `precedence`. With `"precedence": ["more", "good"]`, one
  start's `more` gives `more`, however many gave `good`.
- Where the starts gave different results and the order does not hold each of them, lane cannot
  tell the result. It tells the main conversation and you, in the form
  [the lanes](lanes.md#what-each-lane-is-given) give an error, that the maker of your plugin must
  order them in `precedence`. `lay.py print` refuses routes that fan out a subagent whose results
  they do not order. lane holds the laid routes to the same check. So this error arises only where
  the routes are laid again while starts go on.
- lane keeps a start that is about to end without a result going once, as it keeps any subagent.
  Where the start still ends with no result, lane tells the main conversation to start the
  subagent again once the others have ended. The start made again joins them in place of the one
  with no result.
- lane tells the main conversation the next start only once every start has ended.

## How a subagent gives its result

A subagent gives a result by running the result script with its own name and the result, as its
step writes the command. Before the command runs, lane checks that a route from the subagent is on
the result, or, where no route is from it, that the result is one its `results` name, or `done`
where they name none, as [the lanes](lanes.md#the-proposal) say. It stops a command of any
other result, and tells the subagent the commands it may run. It then checks that the subagent's
work is in the form its lanes ask, as [the lanes](lanes.md) say for the lanes checked at the end.
Where it is not, lane stops the command and tells what is missing. The result script checks the
result again where lane lets the command through unchecked, as where a value its lanes take is
given as `null`. It exits with an error that names the results the subagent may give, or with
none.

- The result counts only where the script exits with no error. Claude Code then gives the hooks
  PostToolUse, and lane keeps the result. A run of the script that is stopped, or that exits with
  an error, keeps nothing. The subagent then mends its work and runs the command again.
- lane matches the command whole against the commands the step writes. A command in any other
  words is a command its lanes do not name, and lane stops it.
- A subagent that gives a result twice gives the later one.
- lane keeps a subagent that is about to end without a result going once, and tells it the
  sentence of its last step, headed by your plugin's name.
- A subagent resumed with SendMessage keeps its ID, and gives a result again for the resumed start.
  The later result takes the place of the earlier one, and lane tells the main conversation the
  start that the later result's route names. So a subagent that ends to wait for an answer, with a
  result whose route waits, such as `asks`, moves the routes on once it is resumed with the answer
  and gives another. While the resumed subagent runs, lane tells the main conversation to wait for
  it to end.
- A start that ended with no result, after it was kept going once, is not resumed. The start made
  again in its place gives the result. lane stops the main conversation's SendMessage to it,
  before or after that start, and tells it the start due, as
  [What the main conversation is told](#what-the-main-conversation-is-told) gives it.

## What the main conversation is told

Within a run, lane tells the main conversation the next start as context that Claude Code adds
beside an event the conversation reads in any case
([Add context for Claude](https://code.claude.com/docs/en/hooks#add-context-for-claude)):

- the first start, beside the command's expansion or the Skill call that begins the run;
- the wait, beside each start of a subagent as it comes back;
- the next start, beside each prompt the main conversation is handed, the task-notification of a
  subagent's end and the user's answer among them, and beside the run of a dependency's result
  script that ends the move of its skill.

Each line is headed by your plugin's name:

| Where the run is | The main conversation is told |
|---|---|
| it has begun, and no subagent has been started yet | ``Start `<plugin>:<to>`.``, the `to` of the skill's route |
| the subagent started in the background has not ended | ``Wait for `<plugin>:<name>` to end: you are told the next start once it has.`` |
| starts of a subagent in `fan_out` have not all ended | ``Wait for every run of `<plugin>:<name>` to end: you are told the next start once each has.`` |
| the subagent ended with a result whose route has a `to` | ``<name> gave `<on>`. Start `<plugin>:<to>`.`` |
| the subagent ended with a result whose route waits | ``<name> gave `<on>`. Put its point to the user, and resume `<plugin>:<name>` with their answer by SendMessage.``, and the run goes on with no start due |
| the subagent ended with a result whose route has neither a `to` nor `waits` | ``<name> gave `<on>`. Start no more subagents.``, once, and the run ends |
| several starts of the subagent ended, giving a result as [Starts at once](#starts-at-once) takes it | ``The <n> runs of <name> gave `<on>`.``, then the start as above |
| the subagent ended with no result, after it was kept going once | ``<name> ended with no result. Start `<plugin>:<name>` again.``, as its start led to no route |

`<plugin>:<name>` is how Claude Code names a subagent of your plugin; a subagent or a skill of a
dependency is named `<dependency>:<name>` as it is. The main conversation writes the rest of the
call, such as its prompt.

A start counts once its subagent has ended. Each subagent the routes name runs in the background.
So the Agent call comes back as the subagent starts, with the status `async_launched` and the
`agentId` of the start ([Agent](https://code.claude.com/docs/en/hooks#agent)). lane counts the
start as the subagent of that `agentId` ends. A call that comes back `completed`, as where the
subagent ran in the foreground, counts as it comes back. A start that comes back with a status
other than these two, or with none, or with no `agentId`, is not as Claude Code hands it. lane tells
it in the form [the lanes](lanes.md#what-each-lane-is-given) give where the event is what is wrong,
and the start stays due.

While a start is due, lane stops any other start, and tells the sentence and, on the next line,
the start due. While a started subagent runs in the background, lane stops a start of another
subagent and tells the wait. It does the same to a further start of the same subagent where
`fan_out` does not name it. While the user is to answer a subagent whose route waits, lane stops
any start, and tells the sentence and the point to put. The SendMessage that resumes that subagent
goes on.

Where the main conversation would end its turn while the user is to answer, lane lets it end, and
the run goes on. Where it would end its turn while a start is due and no start of the run still
runs, lane keeps it going once with the sentence and the start due. Where it ends again, lane lets
it end, and the run ends. A hold with no end would need you to break it, which is no check. lane
then tells you what is left and whose step must be fixed, as a message Claude Code shows you:

```
<plugin>: lane let the run of <skill> end with `<plugin>:<name>` still due, as <name> ended with no result: the maker of <plugin> must fix step <n> of <name> in <file>, which gives its result.
```

where the start due is of a subagent that ended with no result, its last step that gives the
result; and

```
<plugin>: lane let the run of <skill> end with `<plugin>:<name>` still due: the maker of <plugin> must fix step <n> of <skill> in <file>, which starts it.
```

otherwise, the skill's step the routes are laid on.

Claude Code 2.1.319 brings a background subagent's end back to the main conversation as a
task-notification both in an interactive session and in `claude -p`, so a plugin with routes runs
either way.
