# Prompt

A prompt, such as a skill or an agent, is read by the AI that runs it. It lets the AI:

- tell what is expected of it, and why;
- go through the same steps, in the same order and in full, on every run;
- decide for itself how to think within each step;
- check its work, and fix it, before handing it back;
- hand back to the user what only the user decides;
- read only what it needs, when it needs it.

How a prompt is made, judged and tried is not for this reader. Each item of `doc.md` also applies to
a prompt.

## Benefit

### B-1: What is expected

From the Role, can the AI tell what is expected of it?

Why: what is expected is what the AI spends its judgment on and checks its work against; without it,
the AI spends that judgment working out what the prompt is for.

### B-2: Why it is needed

From the Role, can the AI tell why its work is needed?

Why: an AI that knows why chooses, where the steps run out, the action that fits the purpose; given
only what to do, it stops at the end of the steps or goes on by guessing.

### B-3: Everything that must happen every time

Do the Steps say, in the order it is done, everything that must happen on every run?

Look for: what the AI receives and where it reads it, what it hands back and where it writes it, and
each thing it must do in full, such as reading a file whole.

Why: what is left out of the steps is done on some runs and not on others; a check given only as
advice is the step that gets skipped.

### B-4: Its own judgment within a step

Is the AI left to decide how to think within each step, with only what is fragile, or must come out
the same on every run, set down exactly?

Why: the AI often reasons better than a plan written for it, so a step set down in more detail than
its work needs narrows the AI where it would have done better; a fragile step left loose breaks.

### B-5: Checked before handed back

Do the Steps have the AI check its work against what it should be, and fix what falls short, before
handing it back?

Why: a check followed by a fix and another check catches a slip while it is cheap to fix; what is
handed back unchecked carries the slip to whoever receives it.

### B-6: The user's decisions handed back

When the AI meets something only the user decides, or an action that is hard to undo, can it tell
from the prompt that it hands that to the user?

Why: an AI that decides for the user leaves its guess to be taken as the user's choice, and an action
hard to undo cannot be taken back once the user sees it.

## Usability

### U-1: Only what the AI does not already know

Does each sentence give the AI something it would not know or do without it?

Why: every sentence competes for the AI's attention with the work in front of it, and an
instruction the AI already follows draws attention from the ones it needs.

### U-2: What to do

Is each instruction written as what to do, rather than what to avoid?

Why: an instruction that names what to avoid leaves the right action to be guessed.

### U-3: Details read when needed

Can the AI find each detail it needs only on some runs in a file it reads then, named directly in
the prompt?

Why: a detail read on every run costs attention on the runs that do not need it, and a file reached
only through another file is often read in part.

### U-4: Examples close to the real work

Does each example look like the work the AI will actually be given?

Why: the AI copies examples closely, and one far from the real work steers it away from that work.

### U-5: Examples alike only on purpose

Do the examples differ from each other in everything they are not meant to share?

Why: the AI takes what its examples share as part of what is asked, so a likeness left by chance is
copied too.

### U-6: Scripts for what must come out the same

Is each operation that must give the same result on every run done by a script the AI runs?

Why: a script gives the same result every time and spends no attention; the same operation worked
out by the AI varies from run to run.

### U-7: Only what is used

Is each field in the form of what the AI receives and hands back used, by the AI or by whoever
receives its work, toward the purpose?

Why: a field nobody uses still has to be read and filled on every run, and drifts from what the
work actually is, since nothing checks it.

### U-8: What the user must see, shown by a tool

Is each thing the user must see on every run, while the AI is still at work, shown by a script or a
hook rather than by the AI's words between its tool calls?

Why: the AI writes words between its tool calls on some runs and not on others, so what rests on
them reaches the user only sometimes; a hook shows it on every run.

## Format

### F-1: Shape

Does the prompt follow this template, headings included?

```markdown
---
name: <name>
description: <What it does, and when to use it, in the third person>
---

## Role

<What is expected of the AI, and why>

## Steps

1. <What to do>
```

- `name` and `description` are what Claude Code reads to choose a skill or an agent; the
  description says when to use it, since that is what the choice is made on.
- Every step is numbered in the order it is done.

Why: the AI finds what is expected and what to do in the same place in every prompt, and a reader
checks a prompt against its design by these two parts.

### F-2: Form of what goes in and out

Is the form of what the AI receives and of what it hands back set, in the prompt or in a template
or schema the prompt names?

Why: whoever receives the work, a person, the next step or a script, reads it by its form; a form
the AI chooses afresh on each run breaks them.
