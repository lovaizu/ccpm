# Prompt

A prompt, a skill or an agent, is read by an AI. From it alone, the AI meets the responsibility the
prompt gives it on every run, and hands back to the user what only the user can decide. Claude Code
reads its description to choose when to use it.

The AI already reasons well and knows common practice, so a prompt gives it only what it would not
know or do without it. The Role says what the AI is responsible for, the conditions that show it is
met, and what lies outside it. Each step says the result it brings, not the means, so the AI chooses
how. What must come out the same on every run is done by a script, as an AI's work varies from run
to run (Anthropic, "Skill authoring best practices", "Set appropriate degrees of freedom"). A rule
is given in the step it bears on, with its reason, as a rule read far from where it applies is
followed less (Chroma, "Context Rot", 2025), and a rule with its reason is followed where it was not
foreseen (Anthropic, "Prompting best practices"). A role is split off from another only for a
constraint, such as work run in parallel or a context kept apart (the same).

## Format

```markdown
---
name: <name>
description: <What it achieves, and when it is used, in the third person>
---

## Role

<In one sentence, what the AI is responsible for, the conditions that show it is met, and what lies
outside it, such as what the user decides. For a role split off from another: which part of that
one's responsibility it takes, and the constraint it was split for>

## Steps

1. <The result that holds when the step ends>

   <What the result serves and how it is seen, in a sentence>

   <Where a script does the step: its command alone>

   - <A rule the AI's judgment needs in this step>

     <Why>
```

## Questions

### Q-1: Chosen when it is needed

From the `description` alone, can Claude Code tell the requests the skill or agent is for?

Why: Claude Code chooses a skill or an agent by its description alone. One that does not say when
it is used is not chosen where it is needed, or is chosen where it is not.

### Q-2: The responsibility

From the Role, can the AI tell what it is responsible for, the conditions that show it is met, and
what lies outside it?

Why: the AI spends its judgment on what it is responsible for and checks its work against the
conditions. Where the steps run out, it goes on by them. A role with no bounds takes on what is the
user's or another role's.

### Q-3: A split role's part

Where the role is split off from another, can the AI tell which part of that one's responsibility it
takes and the constraint it was split for?

Why: a role that does not know its part does the other role's work too, or leaves a gap between
them. The constraint tells it why it works apart, such as keeping a context of its own.

### Q-4: Each condition met by the steps

Is each condition of the Role met by some step, and does each step serve some condition?

Why: a condition no step meets is left to chance, and a step that serves none is work the
responsibility does not ask.

### Q-5: Each step a result

Does each step say the result it brings and how that result is seen, leaving the means to the AI?

Why: a step written as what to do fixes means the AI would choose better for the case in front of
it, and makes the prompt long. A result that can be seen is one the AI checks before it goes on.

### Q-6: What must come out the same, done by a script

Is each step whose result must come out the same on every run done by a script, with the step giving
the script's command alone?

Why: an AI given a clear step still does it another way on some run, with a result that looks
right. Words in the step that say again what the script does come to differ from it.

### Q-7: What is read set exactly

Is each part that a script, a hook or another step reads, such as a command, a path or a field,
written exactly?

Why: a part left loose is written one way on some runs and another way on others, and breaks
whatever reads it.

### Q-8: Each rule in its step

Is each rule the AI's judgment needs given in the step it bears on, with its reason?

Why: a rule read far from where it applies is followed less, and a rule with no reason is followed
by its letter, also where it does not fit.

### Q-9: A rule across steps held by a hook

Is each rule that bears on several steps held by a hook, which tells it to the AI at the tool call
it bears on, such as a lane laid with ccpm's lane plugin?

Why: a rule written once for several steps is far from each of them, and an AI that drifts from it
does so in its tool calls, where a hook sees every one.

### Q-10: Each sentence gives what the AI lacks

Does each sentence give the AI something it would not know or do without it?

Why: every sentence competes for the AI's attention with the work in front of it. One it does not
need draws attention from those it does. A detail needed only on some runs belongs in a file the
step names, read on those runs.

### Q-11: What is the user's, decided by the user

Does each thing only the user can decide, such as an action hard to undo, reach the user before it
is acted on?

Why: an AI that decides for the user leaves its guess to be taken as the user's choice, and an
action such as deleting, merging or sending cannot be taken back once the user sees it.

### Q-12: What the user must see, shown to them

Does each thing the user must see while the AI works reach them on every run?

Why: the AI's words between its tool calls are written on some runs only, so what the user must see
is shown by a script or a hook.
