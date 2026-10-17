# turn

turn is a Claude Code plugin for anyone who has AI make documents, code and the like in the steps of
their own plugin. What a step has turn make, the work, comes back with its Good for each item of
your checklists, what it gives the one it is for, its receiver, with the lines that give it.

## Example

Say your plugin has a step that writes a project's README to your checklist `checklists/readme.md`,
a file of items that each ask one thing the README must give its receiver.

The step's AI first asks the user, one point at a time, what each item of the checklist needs for
this project, such as whom the project is for and what example to show, and writes what is decided
to `notes/readme.decisions.md`.

The step then writes its task in a CCS, a JSON file. CCS is the small state that
[ACC](https://arxiv.org/abs/2601.11653), a method for long AI tasks, carries from step to step in
place of the whole conversation. Its shape is fixed, parts, each a list of entries, each entry a
kind and its value, and every name in it is your plugin's. This step's CCS, `.tasks/readme.json`:

```json
{
  "focal_entities": [{"deliverable": "README.md"},
                     {"audience": "a developer meeting the project for the first time"}],
  "goal_orientation": [{"purpose": "to decide whether to use the project"}],
  "retrieved_artifacts": [{"checklist": "checklists/readme.md"},
                          {"decisions": "notes/readme.decisions.md"},
                          {"read_with": "CONTRIBUTING.md"}],
  "constraints": [{"language": "English"}]
}
```

The step tells turn which of its kinds hold where the work goes, the checklists, the receiver, what
the receiver reads the work for and what they open with it, and where to write the result. turn
reads the rest of the CCS, such as the decisions and the language, as the task's own.

```json
{"ccs": ".tasks/readme.json",
 "kind": {"work": "deliverable", "checklist": "checklist", "receiver": "audience",
          "use": "purpose", "opens": "read_with"},
 "result": ".tasks/readme-result.json"}
```

So the step's text for calling turn is short:

```
Start the `turn:up` agent in the background with the JSON above. When it returns,
check each Good in .tasks/readme-result.json against its lines in README.md, fix
each item in not_good, and put each question to the user.
```

While the step waits, turn writes README.md, and turn's reader, an agent that did not write it,
reads it as the developer meeting the project would, with CONTRIBUTING.md beside it. Where that
reading finds no Good for an item, turn makes README.md again and reads it once more. The user sees turn's agents
at work in the panel below the prompt input.

When turn returns, README.md is in place, and the result gives each item's Good and its lines. Any
item still without Good after the second reading would be in `not_good`, with what the receiver
gets once it is Good; here there is none. One question is left, under which license people may use
the project, since the user had not chosen one, and README.md leaves the license out until it is
answered:

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

- turn's reader did not make the work, and opens only what the receiver opens.

  The AI that made a work knows what each line means, and misses where the receiver, meeting it for
  the first time, would stop.
- The work is made from the CCS and the files it names alone, so it does not stray from what was
  decided.
- Each Good comes with the lines that give it, so it can be checked instead of taken on trust.
- turn takes the CCS your step already keeps, as it is, and names none of its parts or kinds itself.
- What gives no Good is made again from what the receiver should get, not patched where it showed,
  and what each Good rests on is kept.
