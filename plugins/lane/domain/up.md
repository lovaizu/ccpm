# Lane's up

You propose, from a plugin's steps alone, each step's lane type, each skill's routes, and each
missing result's name, show the caller their steps as they'll read once laid, and have `lay.py` lay
what they approve. You're done when `result.py up laid` or `result.py up left` gives 0, or once
you've told the caller what to fix in a file of their plugin that can't carry the Proposal.

## What you're given

- The plugin's folder, as the caller typed it after `/lane:up` or gave it to the Skill tool.
- What `lay.py types` prints, JSON of the form
  `{"types": [{"name", "sentence", "suits", "allows", "args"}], "proposal": <JSON Schema>}`, each
  lane type with the sentence it lays, the steps it suits, what it allows, and each value it takes
  by name, and the JSON Schema of a Proposal.
- What `lay.py steps <plugin>` prints, JSON of the form
  `{"steps": [{"role", "file", "number", "text"}], "notes": [{"file", "step", "laid", "now"}]}`,
  each Step without the sentences that Lane laid before, and each sentence that the user changed,
  which stays in its Step as theirs.
- What `lay.py print <plugin>` prints: exit 0 with what to show the caller, ending with the
  Proposal's ID; exit 1 with what's wrong in the Proposal; or exit 3 with what's wrong in a file of
  the plugin.
- The caller's reply: yes, a change, or neither.
- What `lay.py write <plugin> <ID>` prints: exit 0 with each file written and to type
  `/reload-plugins`, or exit 1 with why it laid nothing.

## What you give

- A Proposal, JSON in the form of the `proposal` schema that `lay.py types` prints, on the standard
  input of `lay.py print <plugin>`.
- To the caller, what `lay.py print` showed, word for word, and a request for yes or a change; or,
  where a file of the plugin can't carry the Proposal, what to fix in it.
- Each change that the caller asks, written into its Step.
- `lay.py write <plugin> <ID>` once the caller approves, by their reply or, for an AI, by its own
  run of it.
- `result.py up laid` once `lay.py write` gives 0, with what Lane wrote and to type
  `/reload-plugins`; or `result.py up left` where the caller gives neither yes nor a change.

## Steps
