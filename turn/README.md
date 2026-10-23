# turn

turn has AI work only toward passing your checklist: every agent that makes or reads the work looks
only for each item's Good and works only to give it, and what is to be doubted, such as whether a
reply has its form or an input was read whole, is checked by turn's scripts, not by an agent. It is
a Claude Code plugin for anyone who has AI make documents, code and the like in the steps of their
own plugin. What a step has turn make comes back meeting the step's checklists, read first by AIs
that did not make it, in the place of its reader.

## Example

Say your plugin has a step that writes a project's README to your checklist `checklists/readme.md`.
A checklist lists what the README's reader should get from it, one item each, asked as a question,
such as "On opening it, can the reader tell whether the project is for them?", and says under each
item where it is answered: `Scope: its part`, as here; `each part`, every section on its own; or
`whole`, the README at once.

The step's AI asks the user what the items need for this project, writes what is decided to
`notes/readme.decisions.md`, and writes its task in a CCS, `.tasks/readme.json`. A CCS is a JSON
file of parts, each a list of entries, each entry a kind and its value, the shape
[ACC](https://arxiv.org/abs/2601.11653) gives an AI's state; every name in it is your plugin's:

```json
{"focal_entities": [{"deliverable": "README.md"},
                    {"audience": "a developer meeting the project for the first time"},
                    {"has": "."}],
 "goal_orientation": [{"purpose": "deciding whether to use the project, then installing it"}],
 "retrieved_artifacts": [{"checklist": "checklists/readme.md"},
                         {"decisions": "notes/readme.decisions.md"}]}
```

The step's text then calls turn with the CCS, the kinds in it that hold the work, the checklist, its
reader, what the reader uses it for and has with it, here the whole repository, and where to write
the result:

```
Start the `turn:up` agent in the background with
{"ccs": ".tasks/readme.json", "result": ".tasks/readme-result.json",
 "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience",
          "use": "purpose", "has": "has"}}
Put each question it sends to the user and send it the answer. When it returns, check each Good
against its lines.
```

turn first checks that the CCS holds everything the run needs: that what it and its files say can
give every item its Good, and that the reader has what the developer has, so it can do what they do
with the README. No one had chosen under which license people may use the project, so turn writes
nothing yet and sends the step's AI that one question:

```json
{"questions": [{"question": "Under which license may people use the project?",
                "recommended": "MIT", "items": [{"item": "B-5", ...}]}]}
```

The step's AI asks the user, adds the answer to `notes/readme.decisions.md`, and sends it to turn,
which goes on from there. turn tells the conversation you talk with, even where the step's AI is an
agent below it, before each of its agents starts its work, what it will do, how far and how, and as
each step ends, what is done and what comes next:

```
generator: will write README.md for the seven items, as MIT licensed, and run its install and
usage commands as a developer would
```

This time turn writes README.md and runs what it tells, and two AIs that did not write it, each on
its own, use it as the developer meeting the project would, running what they would run. Each item
is judged from that use: it gets its Good when both find the reader gets what the item asks, with
the lines that give it. Where an item gets none, README.md is made again and read again, and an
item that still gets none comes to the step's AI as a question for the user.

When turn returns, README.md is in place, and the result gives each item's Good with the lines it
rests on, and the README's few core decisions, each with why and its lines:

```json
{"items": [{"item": "B-2", "good": "a developer sees at once that it is for CSV files",
            "lines": ["README.md:3-4"]}, ...],
 "core": [{"decision": "the example comes before installing", "why": "the reader decides first",
           "lines": ["README.md:6-20"]}, ...],
 "lessons": [...]}
```

The step's AI reads lines 3 and 4 and the others it is pointed to, and the step ends. The
lessons are what fell short in turn's run and why, which the step's AI puts to you: one of your
project's own for your checklists or rules, a general one for turn's makers as an issue, opened
once you say yes.

## Why turn

turn gives your plugin's AI what it does not get by making the work and checking it itself.

- The AIs that read the work did not make it, have only what the work's reader has, and use the
  work as they do, each on its own.

  The AI that made a work finds the Good it meant; an AI meeting it for the first time finds only
  the Good its lines give, which is what the work's reader gets.
- Each Good comes with the lines it rests on, so it is checked by reading them, not taken on trust.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
- A run stopped anywhere, by you or by a conversation that ended, goes on from its last step when
  the step calls turn again with the same result.

  turn keeps where the run stands in a file beside the result, not in a conversation.

## Requirements

- Claude Code, in which turn runs.
- Python 3.9 or later, run as `python3`, and git.

  turn's scripts and hooks run on Python, and a run cut off leaves its writing as changes git
  shows.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
/plugin marketplace add lovaizu/ccpm
/plugin install turn@ccpm
```

Then have your plugin's step call `turn:up`, as in the example, from the main conversation or from
an agent the main conversation starts. turn's agents take the two layers of agents below the one
that calls it, and Claude Code starts agents down to three layers below the main conversation.

## Documentation

- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[turn's development folder](../dev/turn/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../LICENSE)
