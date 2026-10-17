# turn

turn is a Claude Code plugin for anyone who has AI make documents, code and the like in the steps of
their own plugin. What a step has turn make, the work, comes back with its Good for each item of
your checklist, what it gives the person it is for, and the lines that give it: a reader that did
not make the work reads it in that person's place, and what gives no Good is made again before it
comes back.

## Example

Say your plugin has a step that writes a project's README to your checklist `checklists/readme.md`,
a file of items that each ask one thing the README must give its reader.

The step's AI first asks the user, one point at a time, what each item of the checklist needs for
this project, such as whom the project is for and what example to show, and writes what is decided
to `notes/readme.decisions.md`.

The step keeps its task in a CCS, a JSON file in the shape your plugin chooses. CCS is the small
state that [ACC](https://arxiv.org/abs/2601.11653) carries from step to step of a long AI task in
place of the whole conversation: parts, each a list of entries, each entry a kind and its value.
This step's CCS, `.tasks/readme.json`, holds:

```json
{
  "focal_entities": [{"deliverable": "README.md"},
                     {"receiver": "a developer meeting the project for the first time"}],
  "goal_orientation": [{"use": "to decide whether to use the project"}],
  "retrieved_artifacts": [{"checklist": "checklists/readme.md"},
                          {"decisions": "notes/readme.decisions.md"},
                          {"receiver_opens": "CONTRIBUTING.md"}],
  "constraints": [{"language": "English"}]
}
```

turn names nothing in it. The step tells turn which kinds hold what turn needs, and where to write
its result:

```json
{"ccs": ".tasks/readme.json",
 "kind": {"work": "deliverable", "checklist": "checklist", "reader": "receiver",
          "use": "use", "opens": "receiver_opens"},
 "result": ".tasks/readme-result.json"}
```

So the step's text for calling turn is short:

```
Start the `turn:up` agent in the background with the JSON above. When it returns,
check each Good in .tasks/readme-result.json against its lines in README.md, fix
what falls short, and put each question to the user.
```

While the step waits, a reader that did not write README.md reads it as the developer meeting the
project would, with CONTRIBUTING.md beside it, each item's Good is taken from that reading, and what gives no Good is made
again. The user sees turn's agents at work in the panel below the prompt input.

When turn returns, README.md is in place, and the result gives, for each item, its Good and the
lines that give it. One question is left, under which license people may use the project, since the
user had not chosen one; README.md leaves the license out until it is answered:

```json
{"items": [{"item": "B-2", "good": "a developer sees at once that it is for CSV files",
            "lines": ["README.md:3-4"]}, ...],
 "questions": [{"question": "Under which license may people use the project?",
                "recommended": "MIT"}],
 "not_good": []}
```

The step's AI checks each Good against its lines, puts the question to the user, writes the answer
into README.md, and the step ends.

## Why turn

turn gives your plugin's AI what it does not get by doing the work and checking it itself.

- turn's reader did not make the work, and opens only what the person it is for opens.

  The AI that made a work knows what each line means, and misses where the person it is for,
  meeting it for the first time, would stop.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
- Each Good comes with the lines that give it, so it can be checked instead of taken on trust.
- turn takes the CCS your step already keeps, as it is, and names none of its parts or kinds itself.
- What gives no Good is made again from what the person it is for should get, not patched where it
  showed, and what each Good rests on is kept.
