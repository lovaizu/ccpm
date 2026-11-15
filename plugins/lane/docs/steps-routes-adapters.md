# Steps, routes, and adapters

This page is for you when your plugin's steps go beyond the [README](../README.md)'s walkthrough.

## Where the steps lie

- Write each role's steps as a numbered list under `## Steps`. The list may lie in the role's own
  file, or in a file of your plugin that the role's body names by `${CLAUDE_PLUGIN_ROOT}/`.
- The skill's steps may also lie in the `SKILL.md` of each command that a route waits for or goes
  after, such as an approval. Lane holds them all as the steps of one conversation.
- Such a command's `SKILL.md` sets `disable-model-invocation: true`, so that only the person runs it.
- Each subagent's file sets `background: true`.

## A step that already says its rule

Where a step already says a rule, word for word, Lane doesn't add the sentence again. The same goes
for a step that names a command of your own that checks how it ends. So the subagent reads each
rule once, with the reason you give it.

## A step that ends on your own check

To judge a step's work, have the step end only once a command of your own gives 0. An example is a
check of a record that the subagent keeps. Lane runs the command as the subagent ends, or as your
skill ends its turn. `{result}` in the command stands for the result given. Lane holds the end until
the command gives 0.

## Routes

- A route can wait until the person who uses your plugin types a command you name, such as an
  approval.
- A route can go after a command that the person types at any moment, such as a pause. The route's
  moves then take the place of those due before. Each subagent that runs goes on, and its result
  moves the run by its route.
- Where your skill's steps choose the next move by their own judgment, the route lists each move
  they choose among. A move is one of these: start a subagent, resume one by SendMessage, wait for
  the person's reply, or start no more by the skill's own result. Lane lets through only those
  moves. It holds the main conversation's stop unless one of them waits for the person.
- Your skill's steps can start subagents side by side. Lane lets a start through beside those that
  run, where your adapter gives it a text other than theirs. It holds each subagent to the values of
  its own start, and keeps the moves after each result due until your steps make them.
- Several skills of your plugin can run side by side in one conversation, such as a second command typed
  while a subagent of the first runs. Lane holds each run to its own routes.
- A move can call another plugin's skill. Lane stands aside until the main conversation makes the
  move after that call, as the other plugin's guard holds it meanwhile.

## Adapters

An adapter is an executable program in your plugin's `hooks/adapters/`. `/lane:up` proposes each
adapter it finds there. Lane runs it in the folder that the conversation works in. That folder is
the root of your repository until the conversation enters a worktree.

### A subagent's text and values

By default, a start goes with Lane's text, `Carry out your steps`, and the words typed after your
command. So a subagent gets nothing of the talk that started it, and reads what it needs by its
steps.

Where your plugin gives a subagent a text of its own, the adapter takes the subagent's name as its
one argument, and prints:

```json
{"text": "<the text>"}
```

The start then goes with that text in place of Lane's.

Where your steps name a run value in braces, such as `` Write only `{deliverable}`. ``, the adapter
can give the subagent's values beside its text:

```json
{"text": "<the text>", "values": {"deliverable": "<the value>"}}
```

Lane then holds each name that the values give to its value alone, so the subagent writes only the
deliverable that its start names. A name that the values don't give stands for any value.

Lane gives your adapter each start that runs, on standard input, so that it gives the text of work
that none of them holds:

```json
{"running": [{"role": "<subagent>", "text": "<its text>", "values": {}}]}
```

### The results your plugin keeps

Lane keeps each run's starts and results in a record in the system's temporary folder. So a run
goes on where it stopped in the same conversation, even after `/compact`.

A new conversation goes on from the results that your plugin keeps, through an adapter of them. The
adapter gets the words typed after your command on standard input, so that it separates a new
request from a run to pick up:

```json
{"words": "<the words typed after your command>"}
```

It prints the results in the order the run gave them:

```json
{"results": [{"role": "<subagent>", "result": "<result>"}]}
```

Without one, a run in a new conversation starts over.
