# turn

turn has AI work only toward passing your checklist: every agent that makes or reads the work looks
only for each item's Good, that the work's reader gets from it what the item asks, and works only to
give it, and what a machine can judge, such as whether a reply has its form or an input was read
whole, is checked by turn's scripts, not by an agent. It is a Claude Code plugin for anyone who has
AI make documents, code and the like in the steps of their own plugin. What a step has turn make
comes back meeting the step's checklists, read first by an AI that did not make it, in the place of
its reader.

## Example

Say your plugin has a step that writes a project's README to your checklist `checklists/readme.md`.
A checklist lists what the README's reader should get from it, one item each, asked as a question,
such as "On opening it, can the reader tell whether the project is for them?".

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
reader, what the reader uses it for and has with it, here the whole repository, the items asked of
each part of the work, none here, where to write the result, and the one command that checks the
work, such as `make check` for code, or `null`, as here, where the work has none:

```
Start the `turn:up` agent in the background with
{"ccs": ".tasks/readme.json", "result": ".tasks/readme-result.json",
 "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience",
          "use": "purpose", "has": "has", "each": "each"},
 "test": null}
```

As soon as the AI writing README.md meets a point the CCS leaves open that only the user can
decide, it sends it to the main conversation, the one you talk with, even where the step's AI is an
agent below it, and goes on with the rest. It settles every other point itself, naming each choice
with why in the result. No one had chosen under which license people may use the project, so the
main conversation gets that one question as a message:

```json
{"question": "Under which license may people use the project?",
 "recommended": "MIT, as the decisions say the project is for anyone to use",
 "items": [{"checklist": "checklists/readme.md", "item": "Q-5"}]}
```

The main conversation asks you, adds your answer to `notes/readme.decisions.md`, and sends it back
to the agent that asked with SendMessage. That AI writes the license section from it. You see each
of turn's agents in Claude Code's panel of agents while it runs.

An AI that did not write README.md then uses it as the developer meeting the project would,
running what they would run. Each item is judged from that use, and gets its Good at the lines that
give it. Where an item gets none, the reader tells the AI that wrote README.md, in one sentence,
what the developer would need to get it. That AI mends README.md for it, and README.md is read
again.

When turn returns, README.md is in place. The result gives the lines each item's Good rests on,
each item still without Good with what the developer would need, and each choice the AI that made
README.md took on its own, one the CCS and its files leave open, with why:

```json
{"work": ["README.md"],
 "items": [{"checklist": "checklists/readme.md", "item": "Q-2", "lines": ["README.md:3-4"]}, ...],
 "left": [],
 "chosen": [{"chosen": "the example tidies a file named people.csv",
             "why": "no decision names one, and a list of people shows each column tidied"}]}
```

The step's AI reads lines 3 and 4 and the others it is pointed to, makes any item left itself,
shows the user the choice made without asking them, and the step ends.

## Why turn

turn gives your plugin's AI what it does not get by making the work and checking it itself.

- The AI that reads the work did not make it, has only what the work's reader has, and uses the
  work as they do, running what they would run.

  The AI that made a work finds the Good it meant; an AI meeting it for the first time finds only
  the Good its lines give, which is what the work's reader gets.
- Each Good comes with the lines it rests on, so it is checked by reading them, not taken on trust.
- Each choice the work rests on that no one gave its maker comes back with why, so nothing is
  decided where no one sees it.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
- A run stopped anywhere, by you or by a conversation that ended, goes on from what it had made
  when the step calls turn again with the same call.

  turn keeps the work at its paths and its agents' last replies in `.turn/` at the top of your
  repository, not in a conversation.

## Requirements

- Claude Code, in which turn runs.
- Python 3.9 or later, run as `python3`.

  turn's scripts and hooks run on Python.

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

- [Calling turn](docs/calling.md) gives the checklist's form, the CCS, the call, the questions and
  the result in full.
- [The changelog](CHANGELOG.md) says what changed in each version.

## Development

[turn's development folder](../../dev/turn/README.md) leads to its UX, its design and how it is
checked.

## License

[MIT License](../../LICENSE)
