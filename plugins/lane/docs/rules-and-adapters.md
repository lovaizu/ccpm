# Lane's rules and adapters

This page defines what your plugin gives Lane, and what Lane gives your plugin's AI. Read it when
you write your plugin's `lane/rules.json`, an adapter, or a step that runs one of Lane's
reporters. The examples extend `log`, the plugin of the [README](../README.md#walkthrough).

## What your plugin gives Lane

```text
<your plugin>/
├── agents/              each role's subagent, with background: true
└── lane/
    ├── rules.json       the rules, and the routes of a fixed order
    └── adapters/
        ├── starts_due.py    the starts due of an order decided as it runs
        └── rules.py         the rules of each start of a role whose steps change
```

Lane leaves alone a plugin with no `lane/rules.json`. Each adapter is optional.

Lane follows only a subagent started in the background, so each role's agent definition sets
`background: true`. Lane can't tie a subagent started in the foreground to its start while it
works, and so holds none of its calls.

## Runs and commands

A run starts when a command of your plugin, typed by the person or called by the Skill tool,
calls its skill while no run of your plugin stands in the conversation. While a run stands, each
further command of your plugin is a move of that run, not a new run. The run ends when its order
says so, as [the starts due](#the-starts-due) defines.

Lane reads `lane/rules.json` and runs your adapters only once Claude Code gives it your plugin's
folder, at the main conversation's first event after the skill's call.

## The rule file

`lane/rules.json` holds each role's steps and, where your plugin fixes its order, its routes. Lane
holds the file to [rules.schema.json](../hooks/lane/rules.schema.json). While the file breaks that
form, Lane can't check your run's moves, so it lets each through and tells the AI what it couldn't
check and why:

```text
Lane couldn't check this move by the plugin's rules: /plugins/log/lane/rules.json leaves the form of Lane's hooks/lane/rules.schema.json, at the top: lacks roles
```

### Roles and steps

Each key of `roles` names a role:

- A subagent by its agent type, such as `log:writer`.
- The main conversation, in a run of a skill, by the skill's name, such as `log:up`. After a
  further command of the plugin whose skill has steps, the main conversation follows that skill's
  steps.

Each role lists its `steps` in their order, each with a `name` and its `rules`. A step's rules are
of the types under [Rule types](#rule-types). A step is at hand from the role's start until the
AI marks it done with `lane-step`, and then the next step not marked done is at hand. Where a
later step shows an earlier one short, the AI goes back to the earlier step with `lane-back`. That
step and each step after it are then undone, and the AI takes each again in order, the items of
their checklists too. Reads stay counted, as the file was read.

A subagent's role named with no `steps` takes its steps from
[the adapter of the rules](#the-rules-of-each-start) at each start:

```json
"roles": { "log:writer": {} }
```

The main conversation's role named with no `steps` takes its steps from the same adapter at each
turn of the run. A turn runs from the run's start, or from the first prompt after a turn's end that
Lane let through, the person's or a subagent's end, to the next turn's end that Lane lets through,
so a turn's end that Lane stops goes on in the same turn. Each turn's steps start afresh, so a main conversation that answers each event in its own
turn is held to that event's steps:

```json
"roles": { "log:up": {} }
```

### Routes

Each route says which roles start after a command or after a role's result:

```json
"routes": [
  { "after": { "command": "log:up" }, "start": ["log:writer", "log:writer"] },
  { "after": { "role": "log:writer", "result": "written" }, "start": ["log:reviewer"] }
]
```

- `after` names a command by its skill's name, or a role and one of its results.
- `start` names each role to start. A role named twice starts twice at once.

The route after the run's latest command makes its roles due, and so does the route after each
result since, once for each such result. Two writers' `written` make the reviewer due twice. Each
start made since counts against its role. The command that called the run, typed again, such as
after `/compact`, leaves the starts due as they stand. Once no start is due, the run waits while
a start still runs, and ends once none does.

[routes.py](../hooks/lane/routes.py) holds this order.

## Rule types

Each rule has a `type` and that type's values. Lane checks the rule and, when the AI breaks it,
stops the AI's call or end with the step's sentence. The sentences below come from the rule types'
code, for the role `log:writer` at its step `write`.

Paths are relative to the folder that the conversation works in, and a path that ends with `/`
names a folder and each file under it.

### `writes`

The files the step writes. Lane judges each Write, Edit, and NotebookEdit at the step, by the file
that its `file_path`, or a NotebookEdit's `notebook_path`, names, and stops one whose file the rule
doesn't name.

```json
{ "type": "writes", "paths": ["CHANGELOG.md", "docs/changes/"] }
```

```text
You're at the step `write` of log:writer, which writes only CHANGELOG.md and docs/changes/.
Write there instead of notes.md.
```

A rule that names no path holds a step that writes nothing:

```json
{ "type": "writes", "paths": [] }
```

```text
You're at the step `write` of log:writer, which writes nothing.
Leave notes.md unwritten.
```

### `reads_none`

The files the step never reads. Lane judges each Read and Grep at the step. It stops a Read whose
file the rule names. It stops a Grep whose search reaches such a file: where its `path`, taken from
the folder that the conversation works in, or that folder where the Grep names no `path`, is a path
of the rule, lies under a folder of the rule, or is a folder that holds a path of the rule. A Glob
goes through, as it reads no file's content. The [`commands`](#commands) rule holds a Bash command
that reads such a file.

```json
{ "type": "reads_none", "paths": ["docs/old/"] }
```

At a Read of `docs/old/1.1.0.md`:

```text
You're at the step `write` of log:writer, which never reads docs/old/.
Leave docs/old/1.1.0.md unread.
```

At a Grep in `docs`, a folder that holds `docs/old/`, the sentence names the path searched from the
folder that the conversation works in, and that folder itself as `.`:

```text
You're at the step `write` of log:writer, which never reads docs/old/.
Give Grep a path outside those files instead of docs.
```

### `reads_whole`

The files the step reads whole before it's done. Each path names a file, and Lane holds a rule
whose path ends with `/` out of form, as a folder has no lines to read. Lane counts each line
that a Read of the same start reads, including a Read made at an earlier step. It stops a
`lane-step` mark of the step while a line is unread. A file that can't be read, such as one that
isn't there, is one that Lane [can't check](#when-lane-cant-check-a-rule).

```json
{ "type": "reads_whole", "paths": ["docs/style.md"] }
```

```text
You're at the step `write` of log:writer, which reads whole docs/style.md.
Read docs/style.md from its line 3, then record the step with lane-step write.
```

### `commands`

The commands the step runs. Lane splits each Bash command at `|`, `&&`, `||`, `;`, and each
newline outside quotes, and stops the call where a part begins with the words of no named command.
A quoted word that holds one, such as `git commit -m "Fix; test"`, stays in its command. `git log` lets
through `git log --oneline`. A blank part, such as a blank line or a closing `;`, is no command and
goes through. Lane's reporters always go through. A step with no `commands` rule runs
any command.

```json
{ "type": "commands", "commands": ["git log"] }
```

```text
You're at the step `write` of log:writer, which runs only git log.
Run only those here, and the rest at a step that names them.
```

An empty list lets no command but Lane's reporters through:

```json
{ "type": "commands", "commands": [] }
```

```text
You're at the step `write` of log:writer, which runs no command.
Run it at a step that names it.
```

### `order`

The step comes after each step before it is done. Lane checks it twice:

- At a `lane-step` mark of the step, it stops the mark while a step before it isn't marked done.
- At the start's end, it stops the end while the step itself isn't marked done.

To hold each step in order, give each step an `order` rule.

```json
{ "type": "order" }
```

At a mark of `write` before `read` is done:

```text
You're at the step `read` of log:writer, which comes before `write`.
Make its result, then record it with lane-step read.
```

At an end before the result of `write` is made:

```text
You end before the result of the step `write` of log:writer is made.
Make it, then record it with lane-step write.
```

### `checklist`

The items done before the step. Lane stops a `lane-step` mark of the step while an item has no
`lane-item` mark.

```json
{ "type": "checklist", "items": ["date", "links"] }
```

Where the step's own work decides the items, such as each part that a change reaches, the rule
names a `command` in place of `items`. Lane runs it at the mark, in the folder that the
conversation works in, and takes each line of its output as an item, an empty output as none. Each
item is one word, as `lane-item` takes it. A command that exits other than 0, prints a line that
isn't one word, or can't be run gives no items, so Lane [can't check](#when-lane-cant-check-a-rule)
the checklist:

```json
{ "type": "checklist", "command": "python3 scripts/changed.py" }
```

```text
Lane couldn't check the checklist of the step `write` of log:writer: python3 scripts/changed.py exits 1:
scripts/changed.py: no changes file
```

```text
You're at the step `write` of log:writer, whose checklist isn't done: links.
Take each, then record it with lane-item write <item>.
```

### `result`

The results the role may give, by which the run moves on. `results` names the results of a start
that has done its steps. `ends` names the results that end the start at this step, its later steps
not done, such as when only the person can settle a point. A rule names `results`, `ends`, or
both.

```json
{ "type": "result", "results": ["written"], "ends": ["blocked"] }
```

At the start's end, Lane judges the result rule of the first step not marked done, where that
step has one, or else of the last step. It stops an end with no result that the rule names, offering
each result it may give, the last two joined by `or`:

```text
You end the step `write` of log:writer with no result it may give.
Give written or blocked with lane-result first.
```

For a rule that names only `ends`:

```text
You're at the step `write` of log:writer, whose result isn't made.
Make it, then record it with lane-step write; give blocked with lane-result only where you can't go on.
```

Lane gives the main conversation the start's latest result, and the run moves on by it.

### `check`

Your plugin's own check of the step, a shell command that passes on exit 0 and fails on exit 1.
Lane runs it at the start's end, in the folder that the conversation works in, and stops the end
where it fails. The sentence ends with what the check printed.

```json
{ "type": "check", "check": "python3 scripts/check_changelog.py" }
```

```text
You end the step `write` of log:writer, which its check doesn't pass:
CHANGELOG.md: no entry for 1.2.0
```

A check that exits with any other code, such as 2 where it can't read what it checks, or 127 where
the shell doesn't find it, or that can't be run, is one that Lane
[can't check](#when-lane-cant-check-a-rule):

```text
Lane couldn't check the step `write` of log:writer by its check: python3 scripts/check_changelog.py exits 2:
scripts/check_changelog.py: CHANGELOG.md can't be read
```

### When Lane judges each rule

| Move | Rule types, in the order Lane asks them |
|---|---|
| A Write, Edit, or NotebookEdit | `writes` |
| A Read or Grep | `reads_none` |
| A Bash call | `commands` |
| A `lane-step` mark | `order`, `reads_whole`, `checklist` |
| A subagent's end, or the main conversation's turn's end | `result`, then `order`, then `check` |

Lane judges a call by the rules of the step at hand, and a mark by the rules of the step it marks.
It stops at the first rule broken.

At an end where the start gave a result that a step's `ends` names, Lane judges `order` and
`check` only for the steps before that step. Otherwise, it judges them for each step.

The main conversation's turn's end is then held to the starts due: Lane stops it while a start is
due. A turn that ends on a result that its step's `ends` names goes through, as that result says
the AI can't go on, which no start mends.

### When Lane can't check a rule

A rule that Lane can't check, as a file or a command that the rule needs gives no answer, stops
nothing. Lane judges the move by its other rules, stops it at a rule that it breaks, and else lets
it through. The AI then reads what Lane couldn't check and why, as the examples under each rule
type show. A mark that goes through counts as done.

## Adapters

An adapter gives Lane what only your plugin knows as the run goes on.

### How Lane runs an adapter

Lane runs each adapter as a Python file, with the `python3` that runs Lane:

1. It runs the file in the folder that the conversation works in, with its input as JSON on
   standard input.
1. It reads the adapter's output as JSON on standard output, and holds it to the adapter's output
   schema.
1. Where the adapter can't be run, exits other than 0, prints no JSON, or gives output out of its
   form, Lane can't check what it asked. It stops nothing for that, and tells the AI what it
   couldn't check, with the adapter's path and what went wrong.

At a turn's end, for example:

```text
Lane couldn't check which starts are due: /plugins/log/lane/adapters/starts_due.py failed: no version found
```

Without the starts due, Lane lets each start of your plugin's subagents by the main conversation
through, a turn's end through without ending the run, and a command or a result through. Without
the steps of a start or a turn, Lane holds it to no step. Lane asks the adapter again at the next
move that needs it, and says so again while it fails.

### The starts due

`lane/adapters/starts_due.py` gives each role to start now, or that the run ends. Give it where
your plugin decides its order as it runs. Where it's present, Lane ignores the routes.

Lane asks it at each move that needs the starts due: once Lane reads the rules, at each start and
resume, at each further command, at each result that reaches the main conversation, and at each
end of the main conversation's turn.

Its input is the run as it stands, in the form of
[starts_due.in.schema.json](../hooks/lane/starts_due.in.schema.json): the skill that called the
run, the words typed after its command, and each command, start with its prompt, and result, in
their order. Lane leaves out a start whose call failed, or that ended with no result, so its role
is due again.

```json
{
  "run": {
    "skill": "log:up",
    "words": "1.2.0",
    "moves": [
      { "kind": "command", "command": "log:up" },
      { "kind": "start", "role": "log:writer", "prompt": "Write the entry of 1.2.0." },
      { "kind": "result", "role": "log:writer", "result": "written" }
    ]
  }
}
```

Its output, in the form of [starts_due.out.schema.json](../hooks/lane/starts_due.out.schema.json),
is either the starts due, none while the run waits, or the run's end:

```json
{ "starts": [{ "role": "log:reviewer", "count": 1 }] }
```

```json
{ "ends": true }
```

In a new conversation, the run's moves start over, so the adapter reads where the run stands from
your plugin's own files.

A plugin that gives neither this adapter nor routes has no starts due. Its run holds the main
conversation to its skill's steps alone, and ends at the turn's end that those steps let through.

### The rules of each start

`lane/adapters/rules.py` gives the steps and rules of a start of a role that `lane/rules.json`
names with no steps, and of each turn of a main conversation that it names with no steps. Give it
where a role works on another deliverable at each start, such as a writer whose files differ by the
prompt, or where the main conversation answers another event at each turn.

Lane asks it when the main conversation starts the role, and again at each resume of the start,
with the prompt of the start, so that the steps follow what an answer changed. Each step marked
done and each read stay as they stood. For the main conversation, Lane asks it at each turn's first call or end, and keeps
the steps for that turn. Its `role` is the skill of the run's latest command then, and a command
that the Skill tool calls later in the turn leaves the turn's steps as they stand. Its `prompt` is
the prompt that started the turn, as Claude Code gives it, and empty for the run's first turn, whose
command and words `run` holds.
Its `turns` holds each earlier turn of the run, oldest first, with its `role` and `prompt`,
so that a turn's steps can turn on the turns before it, such as an answer to the question the
last turn asked. A start's `turns` is empty.

Its input, in the form of [rules.in.schema.json](../hooks/lane/rules.in.schema.json):

```json
{
  "run": { "skill": "log:up", "words": "1.2.0" },
  "role": "log:writer",
  "prompt": "Write the entry of 1.2.0 in docs/changes/1.2.0.md.",
  "turns": []
}
```

Its output, in the form of [rules.out.schema.json](../hooks/lane/rules.out.schema.json), is the
start's steps, each rule as in `lane/rules.json`:

```json
{
  "steps": [
    { "name": "write", "rules": [
      { "type": "writes", "paths": ["docs/changes/1.2.0.md"] },
      { "type": "result", "results": ["written"] }
    ] }
  ]
}
```

## Reporters

Your steps name Lane's reporters, which carry what the AI did to Lane as its own call. Claude Code
puts them on the AI's path.

| Reporter | Reports |
|---|---|
| `lane-step <step>` | The step done. |
| `lane-item <step> <item>` | The item of the step's checklist done. |
| `lane-result <result>` | The start's result. |
| `lane-back <step>` | The step gone back to, a step marked done, which undoes it and each step after it. |

Each prints its report as one line of JSON, and Lane reads it back from the Bash call's output. A
call that prints anything more counts as no report, so run each reporter as a Bash call of its
own. A reporter given the wrong number of words exits 2, saying what it takes:

```text
lane-item takes <step> <item>
```

Lane stops a `lane-back` to a step that isn't marked done, and undoes nothing:

```text
You're at the step `report` of log:writer, and `report` isn't marked done.
Go back only to a step marked done, with lane-back <step>.
```

## What Lane gives out

| When | What the AI reads |
|---|---|
| A call, a mark, or an end breaks a rule | The step's sentence, from [Rule types](#rule-types), as the reason Lane stops it. |
| The run's first event after the skill's call, and each further command | The starts due, such as `Due: log:writer.` or `Due: log:writer 2 times at once.` |
| A subagent's end reaches the main conversation | Its result and the starts due, such as `log:reviewer gave more. Due: log:writer.` A subagent stopped by TaskStop gives `log:writer stopped with no result.`, and its role is due again. |
| The main conversation starts a role not due, or ends its turn while a start is due | The starts due, as the reason Lane stops it, or, for a start while none is due, the sentence below. |
| Lane can't check a move, as `lane/rules.json` breaks its form, an adapter fails, or a rule [can't be checked](#when-lane-cant-check-a-rule) | What Lane couldn't check and why, beside the move it lets through. |

Lane stops any start that a subagent makes, in the same words. It leaves alone a start of another
plugin's subagent.

A start of your plugin's subagents while no start is due:

```text
No start of log's subagents is due now.
Go on without it, and start one once Lane says it's due.
```
