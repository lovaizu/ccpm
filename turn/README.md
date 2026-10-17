# turn

turn is a Claude Code plugin for anyone who has AI make documents, code and the like in the steps of
their own plugin. What a step has turn make comes back meeting the step's checklists, read first by
an AI that did not make it, in the place of its reader.

## Example

Say your plugin has a step that writes a project's README to your checklist `checklists/readme.md`.
A checklist lists what the README's reader should get from it, one item each, asked as a question,
such as "On opening it, can the reader tell whether the project is for them?"

The step's AI asks the user what the items need for this project, writes what is decided to
`notes/readme.decisions.md`, and writes its task in a CCS, `.tasks/readme.json`. A CCS is a JSON
file of parts, each a list of entries, each entry a kind and its value, the shape
[ACC](https://arxiv.org/abs/2601.11653) gives an AI's state; every name in it is your plugin's:

```json
{"focal_entities": [{"deliverable": "README.md"},
                    {"audience": "a developer meeting the project for the first time"}],
 "retrieved_artifacts": [{"checklist": "checklists/readme.md"},
                         {"decisions": "notes/readme.decisions.md"}]}
```

The step's text then calls turn with the CCS, the kinds in it that hold the work, the checklist and
its reader, and where to write the result:

```
Start the `turn:up` agent in the background with
{"ccs": ".tasks/readme.json", "result": ".tasks/readme-result.json",
 "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience"}}
When it returns, check each Good against its lines, and put each question to the user.
```

While the step waits, turn writes README.md, and an AI that did not write it reads it as the
developer meeting the project would. Each item is judged from that reading: it gets its Good when
the reader gets what the item asks, with the lines that give it. Where an item gets none, README.md
is made again and read once more, and an item still without Good comes back with what the reader
would get once it has one.

When turn returns, README.md is in place, and the result gives each item's Good with the lines it
rests on, and one question, under which license people may use the project, since no one had
chosen one:

```json
{"items": [{"item": "B-2", "good": "a developer sees at once that it is for CSV files",
            "lines": ["README.md:3-4"]}, ...],
 "questions": [{"question": "Under which license may people use the project?",
                "recommended": "MIT"}]}
```

The step's AI reads lines 3 and 4 and the others it is pointed to, asks the user the question, adds
the license, and the step ends.

## Why turn

turn gives your plugin's AI what it does not get by making the work and checking it itself.

- The AI that reads the work did not make it, and opens only what the work's reader opens.

  The AI that made a work knows what each line means, and misses where a reader meeting it for the
  first time would stop.
- Each Good comes with the lines it rests on, so it is checked by reading them, not taken on trust.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
