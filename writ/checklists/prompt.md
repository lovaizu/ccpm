---
name: prompt
version: 0.2.0
---

# Prompt

A prompt, such as a skill or an agent, is read by the AI that runs it. It lets the AI:

- tell what is expected of it;
- tell why its work is needed;
- do, on every run, everything that must happen;
- do it in the order it must be done;
- decide for itself how to think within each step;
- do, the same way on every run, what breaks when done a little differently;
- get the same result on every run from each operation that must give it;
- find its slips before it hands its work back;
- fix them before it hands its work back;
- spend its attention only on what it would not know or do without the prompt;
- tell from each instruction the action to take, and why it is there;
- do all its work from a scope of inputs the prompt sets;
- read each detail only on the runs that need it;
- reach each such detail straight from the prompt, and so read it whole;
- learn from each example what the real work asks;
- take from the examples only what they are meant to share;
- fill only the fields that someone uses;
- find what is expected of it and what to do in the same place in every prompt.

It lets the user the AI works for:

- make each decision that is only theirs;
- stop an action that is hard to undo before it is taken;
- see, on every run, what they must see while the AI is still at work.

It lets Claude Code choose the skill or the agent for a task from its name and description, and
lets whoever receives the AI's work, a person, the next step or a script, read it by a form that is
the same on every run.

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

Does the AI do, on every run, everything that must happen, because each such thing is a step?

Look for: what the AI receives and where it reads it, what it hands back and where it writes it, and
each thing it must do in full, such as reading a file whole; one given only as advice, or not at
all, fails. Each is written in the Steps as an instruction to act; one given as a rule or principle
to keep fails.

Why: what is left out of the steps is done on some runs and not on others; a check given only as
advice is the step that gets skipped; a rule says what must hold, not what to do, so the AI judges
when it applies and keeps it on some runs only.

### B-4: Its own judgment within a step

Is the AI left to decide how to think within each step?

Look at: each step says what to do; one that sets out how to reason toward it, where nothing that
follows breaks if the AI reasons another way, fails.

Why: the AI often reasons better than a plan written for it, so a step set down in more detail than
its work needs narrows the AI where it would have done better.

### B-5: Slips found before handing back

Does the AI find its slips before it hands its work back?

Look at: a step, before the one that hands the work back, that has the AI check its work against
what it should be, such as its form, a checklist or a script's result.

Why: a check catches a slip while it is cheap to fix; what is handed back unchecked carries the slip
to whoever receives it.

### B-6: The user's decisions handed back

When the AI meets something only the user decides, does the user make that decision?

Look at: the prompt has the AI hand such a thing to the user rather than settle it.

Why: an AI that decides for the user leaves its guess to be taken as the user's choice.

### B-7: Done in the order it must be

Does the AI do each thing that must happen in the order it must be done?

Look at: the steps, read from the first, against the order the work needs: an input is read before
the step that uses it, and a thing done only when an earlier step calls for it, such as opening a
file the work links, comes after that step; one placed before it fails.

Why: a thing done before what it rests on is done on a guess, and a check done after the work is
handed back catches nothing in time.

### B-8: What breaks, set down exactly

Does the AI do, the same way on every run, each part of a step that breaks when done a little
differently?

Look at: each such part, such as a command, a path, a field name or a form another step or a script
reads, written out exactly in the prompt; one left for the AI to phrase fails.

Why: a part that breaks when done a little differently, left loose, comes out differently on some
run and breaks what reads it.

### B-9: Slips fixed before handing back

Does the AI fix what its check finds before it hands its work back?

Look at: a step that has the AI fix what the check finds and check again, until the check passes.

Why: a check followed by a fix and another check leaves the work as it should be; a check whose
findings are only noted hands the slip on all the same.

### B-10: An action hard to undo, asked first

Can the user stop an action that is hard to undo before the AI takes it?

Look at: the prompt has the AI ask the user before such an action, such as deleting, pushing or
sending.

Why: an action hard to undo cannot be taken back once the user sees it.

### B-11: Only what the AI does not already know

Does the AI spend its attention only on sentences that change what it does?

Look at: for each sentence, whether a run of the prompt without it does what the sentence asks all
the same; one that does fails.

Why: every sentence competes for the AI's attention with the work in front of it, and an
instruction the AI already follows draws attention from the ones it needs.

### B-12: What to do

Can the AI tell from each instruction the action to take?

Look at: each instruction says the action in positive terms; one that says what to avoid, even
beside what to do, fails.

Why: an instruction that names what to avoid leaves the right action to be guessed, and puts what
to avoid in the AI's attention.

### B-13: Details read only when needed

Does the AI read each detail it needs only on some runs on those runs alone?

Look at: each such detail of the prompt's own kept in a file of its own, which the prompt says when
to read; one written in the prompt itself fails. Each input the AI needs only when something in the
run calls for it, such as a file the work links, read where the steps meet that call; one read on
every run, because the prompt names it, fails.

Why: a detail read on every run costs attention on the runs that do not need it, and an input read
on a run that did not call for it shapes the work there, as the AI would not have had it.

### B-14: Detail files named in the prompt

Does the AI reach each file of details straight from the prompt?

Look at: each such file named directly in the prompt; one named only in another file fails.

Why: a file reached only through another file is often read in part.

### B-15: Examples close to the real work

Does the AI learn from each example what the work it will actually be given asks?

Look at: each example, against a task the prompt is actually given: the same kind of input and the
same kind of result.

Why: the AI copies examples closely, and one far from the real work steers it away from that work.

### B-16: Examples alike only on purpose

Does the AI take from the examples only what they are meant to share?

Look at: each thing all the examples share, such as their length, subject, wording or order,
matched to something the prompt asks; a shared thing matched to nothing fails.

Why: the AI takes what its examples share as part of what is asked, so a likeness left by chance is
copied too.

### B-17: Scripts for what must come out the same

Does the AI get the same result on every run from each operation that must give it?

Look at: each such operation done by a script the AI runs; one the AI works out itself fails.

Why: a script gives the same result every time and spends no attention; the same operation worked
out by the AI varies from run to run.

### B-18: Only fields that are used

Does the AI fill only the fields that someone uses?

Look at: each field in the form of what the AI receives and hands back, matched to the AI or to
whoever receives its work, using it toward the purpose; a field matched to no one fails.

Why: a field nobody uses still has to be read and filled on every run, and drifts from what the
work actually is, since nothing checks it.

### B-19: What the user must see, shown by a tool

Does the user see, on every run, each thing they must see while the AI is still at work?

Look at: each such thing shown by a script or a hook; one left to the AI's words between its tool
calls fails.

Why: the AI writes words between its tool calls on some runs and not on others, so what rests on
them reaches the user only sometimes; a hook shows it on every run.

### B-20: The reason for each instruction

Can the AI tell why each instruction is there?

Look at: each instruction whose reason the Role does not already give carries its reason beside it.

Why: an AI that knows why applies the instruction to cases it did not name, and keeps to it where a
bare rule is read narrowly.

### B-21: The scope of its inputs

Does the AI do all its work from a scope of inputs the prompt sets?

Look at: the prompt names the whole of what the AI reads, what it works on and what it consults for
reference, such as other code it follows, and has the AI work from that scope.

Why: what the AI reads outside a set scope shapes its work without anyone having chosen it; what it
is meant to consult, left unnamed, is found on some runs and missed on others.

## Usability

None: each thing that makes a prompt easy for the AI to follow is one the opening names the AI or
its user gets from it, so its item is in Benefit.

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

### F-3: When a place is written

Is each place of the form that the AI may fill or leave, such as one per item, written on the
condition that whoever reads the form takes a written place to mean, because the prompt sets that
condition?

Look at: the prompt's words on when such a place is written, against what the step or script that
reads the form takes a place to mean, such as the receiver getting what the item asks; a prompt that
leaves the condition to the AI, or sets a looser one, such as a part of what the item asks or what
the AI can say about the item, fails.

Why: a place written on a looser condition than its reader counts on is read as what it is not, such
as a note that nothing was found read as a find.
