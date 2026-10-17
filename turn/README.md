# turn

turn is a Claude Code plugin for anyone who has AI make documents, code and the like in the steps of
their own plugin. Each call is one turn of [ACC](https://arxiv.org/abs/2601.11653), which carries a
long AI task from turn to turn in a small state, the CCS, instead of the whole conversation: a step
hands turn a CCS and goes on from the new CCS turn returns. What the turn makes, the work, comes
back meeting your checklist, a file of items that each ask one thing the work must give, since a
reader that did not make the work reads it in the place of the person it is for, and what falls
short is made again before it comes back.

## Example

Say your plugin has a step that writes a project's README to your checklist `checklists/readme.md`.

The step's AI first asks the user, one point at a time, what each item of the checklist needs for
this project, such as whom the project is for and what example to show, and writes what is decided
to `notes/readme.decisions.md`.

Then it hands turn the task in a CCS, a JSON file of the nine parts ACC gives the state. The step
writes the parts that say the task: what is made, who reads it and for what, the checklists and
decisions, and rules such as the language. The parts that say how the task stands after a turn,
such as what to do next and what is not settled, are empty, since no turn has run yet.

```json
{
  "focal_entities": [{"deliverable": "README.md"},
                     {"receiver": "a developer meeting the project for the first time"}],
  "goal_orientation": [{"use": "to decide whether to use the project"},
                       {"acceptance": "they can tell whether the project is for them"}],
  "retrieved_artifacts": [{"checklist": "checklists/readme.md"},
                          {"decisions": "notes/readme.decisions.md"}],
  "constraints": [{"language": "English"}],
  "predictive_cue": [], "uncertainty_signal": [], "semantic_gist": [],
  "relational_map": [], "episodic_trace": []
}
```

What ACC is for and how each part is written are in the
[`turn:acc` skill](skills/acc/SKILL.md), which your plugin's AI also reads when it writes a CCS. So
the step's text for handing it over is short:

```
Write this CCS to .tasks/readme.json, and start the `turn:up` agent in the background
with these two lines:

    in: .tasks/readme.json
    out: .tasks/readme-back.json

When it returns, check README.md against what the new CCS in .tasks/readme-back.json
says for each item, fix what you find, and do what its `next` says.
```

While the step waits, a reader that did not write README.md reads it as the developer meeting the
project would, each item of the checklist is judged from that reading, and what falls short is made
again. The user sees turn's agents at work in the panel below the prompt input.

When turn returns, README.md is in place, and the new CCS says for each item whether README.md meets
it and which lines do. Its `next` is `ask the user`, with a question asking under which license
people may use the project, since the user had not chosen one; README.md leaves the license out
until it is answered.

The step's AI checks each answer against README.md, puts the question to the user, writes the
answer into README.md, and the step ends.

## Why turn

turn gives your plugin's AI what it does not get by doing the work and checking it itself.

- turn's reader did not make the work, and opens only what the person it is for opens.

  The AI that made a work knows what each line means, and misses where the person it is for,
  meeting it for the first time, would stop.
- The work is made from the decisions and checklists handed over alone, so it does not stray from
  what was decided.
- An item counts as met only where named lines give it, so each judgment can be checked instead of
  taken on trust.
- What falls short is made again from what the work should give, not patched where it showed, so
  every item already met stays met.
