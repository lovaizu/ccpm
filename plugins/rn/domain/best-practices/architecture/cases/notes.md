# Notes, a fail on most questions

A design of a Claude Code plugin, made as the baseline's designs were. It's a kept case of the
[architecture best practice](../best-practice.md): a deliverable with the verdict on each question
that someone who knows the developer's work gives, so that an evaluator proves itself on it before
anyone trusts its verdicts.

## The deliverable

````markdown
# `notes` architecture

This document says how the parts of notes give [its product vision](product-vision.md). The
user's skill, `/notes:write`, starts the writer, an agent that turns a meeting's transcript into
notes. A hook script, `check.py`, runs on each Write of the writer and stops a note whose form is
wrong.

## User stories

- **S1**: the user wants to type `/notes:write <transcript>` and get the meeting's notes in
  `notes/<date>.md`. It carries the README's walkthrough.

## Components

```text
user -> /notes:write -> writer -> Write -> check.py -> rules.py, settings.py, hook.py, notes/
```

- **user**: the transcript, and whether to keep the notes.
- **writer**: the notes.
- **check.py**: which checks run on a Write, whether the note's form holds, the user's settings,
  and what the writer hears when a check fails.
- **rules.py**, **settings.py**, **hook.py**: code that check.py uses.
- **notes/**: the notes written.

- **A hook script** over an instruction in the writer's prompt: a hook holds on every run, which
  KR1.1 counts. It costs a process for each Write.

## Data model

- **Note**: a meeting's notes. **Check**: one rule of a note's form.

The fields of each data lie where the code builds it.

## Sequences

### S1: a note written

```text
user -> skill: /notes:write <transcript>
skill -> writer: the transcript
writer -> check.py: Write notes/<date>.md
  check.py reads ~/.notes.json, waits 2 seconds for a lock on it, and tries 3 times
  alt a check fails: check.py -> writer: what's wrong, and the writer writes again
  else: check.py -> writer: allowed
writer -> user: the notes
```

## Deployment

The user's computer gives Claude Code and Python 3.9, and Claude Code runs check.py through the
plugin's `hooks/hooks.json`. The user installs notes as the README says.

## Tests

| Process | Unit | Architecture | Product vision |
| --- | --- | --- | --- |
| check.py | `FULL` | `FULL` | `SMOKE` |
| writer | none, a prompt | a double of the writer | `HAPPY`, on the model the users run |

- **`test_s1_written`**: a note whose checks pass, in S1.
- **`test_s1_rewritten`**: a check that fails once, and the writer writing again, in S1.
````

## Verdicts

| Question | Verdict | Why |
| --- | --- | --- |
| Q1 | no | No quality has a scenario. The one choice argues from a key result, and nothing asks that a check change or run in a test on its own. |
| Q2 | no | One line sets a person, a skill, an agent, a process, its modules, and a folder side by side, and `check.py` holds four unrelated decisions. |
| Q3 | no | No line says which element may depend on which, and `check.py` reads the user's settings file itself, so no test runs its rules without the user's computer. |
| Q4 | no | The Write that crosses from the writer to `check.py` and the hook's reply have no named form or contract, and every field lies "where the code builds it." |
| Q5 | yes | S1 draws each step from the user's request to the notes, with the branch where a check fails and the writer writes again. |
| Q6 | yes | It names the computer, what it gives, how Claude Code runs the hook script, and points to the README for the setup. |
| Q7 | yes | The opening gives the idea, and the one choice gives the option it beat, why, and its cost. |
| Q8 | no | The 2 seconds and the 3 tries of the lock are how `check.py` works inside, and the next change to them makes the line untrue. |
| Q9 | no | The tests try `check.py` `FULL` at unit and again at architecture, so the slower level repeats each case, and no line says how the writer's double stays true to the writer. |
| Q10 | yes | Each path of S1, the note that passes and the one written again, has its test. |
| Q11 | no | A new developer can't tell from it where the code of a check lies or how to test one apart from the settings file. |
