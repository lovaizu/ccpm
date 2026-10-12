# turn

turn has Claude Code make a document or a prompt, such as a README, a design document or a skill,
and gives it back already read by someone in the place of the person it is for, made again where
that reading could not take what it needed, with only the questions you alone can answer. It is for
anyone who has Claude Code write such work, by asking in a conversation or from the steps of their
own plugin. It does not make code, which is checked by running its tests rather than by reading.

What only turn gives is a reading by an AI that did not write the work, in a fresh copy of your
repository that holds only what the person the work is for would have, against a checklist you
choose for that kind of work; and each thing the checklist asks counts as met only where the lines
of the work show it. When Claude checks what it has just written, it checks as the writer, who knows
what each line means, and is likely to pass what a newcomer would miss, as a person reviewing their
own writing does; turn is built on that assumption.

## Example

### Asking in a conversation

You want the README of a small command-line tool. You have notes on it, and a checklist for READMEs.
In Claude Code you ask:

```console
> With turn, write the README of this tool for developers who find it on GitHub,
  from docs/notes.md, against checklists/readme.md.
```

Claude writes your request into a CCS, a JSON file that holds the task: where the work goes, who it
is for, what they use it for, and which notes and checklist to work from. It starts turn with it,
and turn shows:

```console
Plan: 1 write → 2 read → 3 check   (once more if something is missing; two rounds at most)

Round 1
  1 write   To make: developers who find the tool on GitHub can tell what it saves them
            and run it on their own files.
            .turn/readme/1/README.md
  2 read    Read as a developer who finds the tool on GitHub.
            .turn/readme/1/reading.json
  3 check   ⚠️ The reader could not tell which Python version the tool needs.
            ⚠️ The reader could not picture the result on their own files.
Round 2
  1 write   To make: the same, made again from why each was missing.
            .turn/readme/2/README.md
  2 read    Read again, as the same developer.
            .turn/readme/2/reading.json
  3 check   ✅ Nothing missing.

The README is at README.md.
❓ Which license is the tool under? Your notes do not say, so the README leaves it out.
```

The paths are where turn keeps each round's work and its reading, in `.turn/` in your repository.
turn leaves them there for you to open.

### What happens in a run

A checklist is a list of items, each asking one thing such work must give the person it is for. A
run of turn goes from the CCS it is given to the one it writes back, in one round or two, each
writing, reading and checking the work once. turn's conductor runs it in your conversation, writes
the console and decides each move. It has four agents do the work, each given only what its part
needs:

- The maker writes the work from the CCS, your notes and the checklist, and gives, for each item,
  the lines of the work that meet it, with their words.
- The reader reads the work in a fresh copy of your repository, as the person the CCS says it is
  for, reading it for what they use it for, with the checklist, and says for each item what it took
  and where.
- The judge reads the work, the reading and the records Claude Code keeps of every agent, and gives
  a Good for each item the work meets: the item, with the lines it rests on.
- The learner, for each item left without a Good, finds why none came out.

```mermaid
sequenceDiagram
  actor You
  participant C as Claude
  participant T as Conductor
  participant M as Maker
  participant R as Reader
  participant J as Judge
  participant L as Learner
  You->>C: what you want, from which notes, against which checklist
  C->>T: the CCS
  T-->>You: the plan
  loop round 1; round 2 only if an item is left without a Good
    T-->>You: what it means to make
    T->>M: the CCS, your notes, the checklist (round 2: the learner's causes)
    M-->>T: the work, and the lines that meet each item
    T->>R: the work, who it is for, what they use it for, the checklist, in a fresh copy
    R-->>T: for each item, what it took and where
    T->>J: the work, the reading, the records
    J-->>T: a Good, with its lines, for each item the work meets
    T-->>You: what the reader could not take
    opt an item without a Good
      T->>L: those items, the work, the reading, the records
      L-->>T: why no Good came out
    end
  end
  T-->>C: a new CCS: where the work is, the questions, any item still without a Good
  C-->>You: the questions only you can answer
```

A run goes forward by Goods. Before anyone reads the work, a script finds the lines of it that the
maker gave for no item, as test coverage finds the lines no test runs. Such a line either does
nothing for the person the work is for or holds a slip. The conductor sends the work back to the
maker with those lines, and with each item it does not yet see met, until there are none. The same
count runs on the judge's Goods. The conductor counts a Good only once it has seen, in the lines the
Good rests on, that the item is met.

An item with no counted Good is made again in round 2 from the learner's cause, not patched where it
showed, and read and judged again. What round 2 still leaves without a Good comes back to you as it
is, with why, for you to decide.

For each item, `.turn/` keeps the lines its Good rests on, or why it has none, and the version of
the checklist it was made and judged by.

### Stopping and answering

If the line after `To make:` is not what you want, press Esc and say what you want instead. turn
hands Claude back the CCS, marked as stopped; Claude adds your words to it and starts turn again,
from the work as it stands.

Answer the question marked ❓ the same way: Claude adds your answer to the CCS and starts a new run,
which has the changed work read again before you get it. Work that came back with an item still
without a Good can be run again the same way, if you choose.

### From your plugin

A step of your plugin takes Claude's place: it writes the CCS, calls turn, and decides its next move
from the CCS turn writes back. The step reads:

````markdown
Write this CCS to .setup/task-1.json, and call the `turn:up` skill with these two lines as its
arguments:

```
in: .setup/task-1.json
out: .setup/task-2.json
```

```json
{
  "focal_entities": [{"deliverable": "docs/setup.md"},
                     {"receiver": "a developer who has just cloned the project"}],
  "goal_orientation": [{"use": "to get the project running on their machine"},
                       {"acceptance": "they can run the tests without asking anyone"}],
  "retrieved_artifacts": [{"viewpoint": "checklists/doc.md"}, {"source": "notes/setup.md"}],
  "constraints": [{"language": "English"}],
  "predictive_cue": [], "uncertainty_signal": [], "semantic_gist": [],
  "relational_map": [], "episodic_trace": []
}
```
````

A CCS has these nine parts, each a list of entries, and each entry one kind and its value as a
string. `out` must not exist yet; turn reads `in` and writes only `out`.

| Part | What you write in it | Needed |
|---|---|---|
| `focal_entities` | `deliverable`: where the work goes, a path in the repository; `receiver`: who it is for | both |
| `goal_orientation` | `use`: what they use it for; `acceptance`: what they must be able to do with it | `acceptance` |
| `retrieved_artifacts` | `viewpoint`: a checklist to measure the work by; `source`: a file to make it from | `viewpoint` |
| `constraints` | `language`; `rule`: a rule the work or its making follows; `answer`: the user's answer or words, added for a new run | none |
| `predictive_cue`, `uncertainty_signal`, `semantic_gist`, `relational_map`, `episodic_trace` | nothing; turn writes them, as below | none |

In the CCS turn writes back, the step reads these kinds:

- `next`, in `predictive_cue`: what to do next, below.
- `gap`, in `uncertainty_signal`: each question for the user.
- `difference`, in `semantic_gist`: each item still without a Good, with its cause.
- `evidence`, in `episodic_trace`: where turn keeps what each item rests on.

The other entries are turn's own; the step need not read them. The values of `next`:

- `done`: the work is in place and nothing is left for the user.
- `ask the user`: put each `gap` and each `difference` to the user, add their answers as `answer`,
  and call turn again.
- `to the caller: <reason>`: the CCS cannot be run, or a cause lies in what the step wrote the work
  should be, which turn never rewrites; the reason says which, and the step settles it.
- `stopped: <where>`: the user pressed Esc; add their words as `answer` and call turn again.

turn adds the rules it learned about making such work as `rule` entries after yours in
`constraints`; carry them into the CCS of the step's later tasks.

## Requirements

- Claude Code: turn runs inside it.
- A git repository: the reader's fresh copy is made from it.
- Python 3.9 or later, as `python3`, with nothing beyond what comes with it: turn's scripts make the
  list of items from your checklists, find the lines of the work no item rests on, and check each
  CCS turn takes and writes back.
- jq: turn, and whoever writes the CCS, Claude in your conversation or your plugin's step, read and
  change parts of the CCS with it.
- A checklist for each kind of work, since the work is measured by its items: a Markdown file that
  opens with what such work is for, followed by each item under a heading `### <ID>: <title>`. The
  [writ checklists](../writ/references/essentials/) cover documents, READMEs, design documents and
  prompts, and can be used as they are.

## Installation

In Claude Code, add the marketplace once, then install turn:

```console
> /plugin marketplace add lovaizu/ccpm
> /plugin install turn@ccpm
```

Then ask as in the [Example](#asking-in-a-conversation), with your own notes and checklist. A plugin
that calls turn also names it in `dependencies` in its `.claude-plugin/plugin.json`, so that
installing the plugin installs turn.

## Documentation

All of turn's use is in this README. What changed in each version is in
[CHANGELOG.md](CHANGELOG.md).

## License

[MIT](../LICENSE)
