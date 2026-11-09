# `prompt`

## Goal

When an AI agent gets the prompt for a request that the prompt is for, it does the task as the prompt's writer means. It does so with only what its run gives it, on every run, and in cases that the writer didn't foresee.

## Inputs

- [architecture](../architecture/best-practice.md)

## Parts

- **description**: what the host reads to choose the prompt for a request: a name that says what the prompt does, and a description of what it does and the requests to use it for.
- **tools**: the tools the AI may use. The prompt lists them where the host reads them, when the host allows such a list. The host refuses any tool not on it.
- **goal**: what the AI reads first in the body: what it's to achieve, for whom, how it knows it has finished, and what lies outside its task.
- **context**: what the AI needs and can't find or know on its own: the situation, its inputs and where they lie, and the rules of this place.
- **steps**: the steps, in the order the AI takes them. Each step names the result that holds when it ends. It gives either the rules the step needs, each with its reason, or the script that does the step and how to run it.
- **output**: what the AI hands back, in what form, and to whom.
- **trials**: the trials that try the prompt in real use: runs of the whole that the prompt is part of, on requests as big as real ones. They also hold the stand-ins that play the person and the parts the prompt works with, the judges, each an AI that gives pass or fail on one point, and the checks on each run's record.

## Necessary conditions

| ID | Condition | Parts |
| --- | --- | --- |
| N1 | When the AI believes it has finished, can it tell from the prompt whether it has reached what the task is for, so that it stops at that purpose and not at the last step? | goal |
| N2 | When the AI meets a choice that's the user's, such as one between options that serve equally or an action hard to undo, does it hand the choice to the user rather than make it, so that the user's purpose and intent stay the user's? | goal |
| N3 | Given the prompt and only what its run gives it, can the AI do each step without guessing a fact, such as where its inputs are or a rule of the place it works in, so that its result rests on facts, not on guesses? | context |
| N4 | Taking the steps in order, does the AI arrive at what the goal says the task is for, with no step that leads it elsewhere, so that following the prompt is the way to its purpose? | goal, steps |
| N5 | When the AI meets a case a step's rule doesn't name, can it decide the case as the writer would, from the reason the rule gives, so that the rules hold where their words don't reach? | steps |
| N6 | When the AI runs twice on the same input, does each step whose result must not vary, such as a check or a file's form, give the same result both times, so that what must hold doesn't hang on chance? | steps |
| N7 | Can the AI take every action its steps call for with the tools it may use, so that the run never stalls on a missing tool? | tools, steps |
| N8 | When the AI, during a run, reaches for an action that lies outside its task, does the host refuse it, so that a slip of the AI can't harm what lies outside the task? | tools |
| N9 | When the caller, the person or the AI that started the prompt, takes what the AI hands back, can it act on it without asking the AI anything further, so that the work goes on without a round trip? | steps, output |
| N10 | When a request the prompt is for comes, and a request near it that it isn't for, does the host, such as Claude Code, choose the prompt for the first and pass it over for the second, from the name and the description alone, so that the prompt runs where its writer means it to and nowhere else? | description |
| N11 | Once the host has chosen the prompt by its description, does the AI do the task the description says, all of it and nothing more, so that the caller gets what the description promised? | description, goal |
| N12 | When the prompt runs several times on each kind of request it's for, does the AI reach the result the prompt names on every run, so that the user can count on it? | the whole |
| N13 | Does every line of the prompt change what the AI does toward the task, so that none draws its attention from the lines that do? | the whole |
| N14 | For each rule of the steps that must hold on every run, does a hook hold it, and does a test try the hook both where the AI keeps the rule and where it breaks it, so that a rule that must hold doesn't rest on the AI's attention? | steps |
| N15 | When a trial fails, can the maintainer tell from its record that the prompt went wrong and not the trial: its set-up, a stand-in, a judge or a check, so that they mend the prompt only for a cause the record shows? | trials |
| N16 | When the AI puts a decision, a proposal or a report to the person, can the person approve or decide from its first lines alone, and reach the details only where they ask, so that the person spends their attention only on what's theirs? | output |
| N17 | When the caller acts on what the AI reports it did or found, does each claim hold as far as the report says the AI checked it, so that the caller acts only on what holds? | output |

## Practices

### N1

When the AI believes it has finished, can it tell from the prompt whether it has reached what the task is for, so that it stops at that purpose and not at the last step?

**Thinking**

The AI stops when its work looks done. So the prompt says what the result is for, and gives a check that sets done apart from looking done.

**Steps**

1. For each thing that holds once the AI has met the task, give the check that shows it: a command to run where one exists, or else what to look up and where.
2. Write when the AI stops: once every check passes, or at a blocker it can't pass. At a blocker, the AI hands it back with what it found.

### N2

When the AI meets a choice that's the user's, such as one between options that serve equally or an action hard to undo, does it hand the choice to the user rather than make it, so that the user's purpose and intent stay the user's?

**Thinking**

A choice is the user's where the AI has no ground to pick one option over another, or where the choice is hard to undo. The prompt names those choices and how the AI asks about them. It leaves every other choice to the AI.

**Steps**

1. Among the choices the task meets, mark each action that's hard to undo, touches what others share, or destroys something.

### N3

Given the prompt and only what its run gives it, can the AI do each step without guessing a fact, such as where its inputs are or a rule of the place it works in, so that its result rests on facts, not on guesses?

**Thinking**

The AI is able but new to this place. It gets nothing of the conversation that started it. So the prompt gives what the AI can't find or know, and says where the rest lies, as [add context](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) says.

**Steps**

1. For each step, list the facts it needs: its inputs and where they lie, the terms it uses, the rules of the place, and what the writer knows without saying.

### N4

Taking the steps in order, does the AI arrive at what the goal says the task is for, with no step that leads it elsewhere, so that following the prompt is the way to its purpose?

**Thinking**

The prompt says first what the task is for, for whom, and why. Each step then follows as a result on the way there, with what that result is for. The AI chooses how to reach each result and knows when to go on. Where a step doesn't fit the case, the AI follows what the step is for. The AI follows steps given without their intent off the mark.

**Steps**

1. Write a step only where an AI that holds the task's intent would still not know what to do, such as a check to run or a form to keep.
2. Write the steps in the order their results must hold, so the AI reads that order, such as in a numbered list.
3. Check that a later step or the goal uses each step's result, and cut a step whose result nothing uses.
4. Check that the last step leaves what the goal says the task is for.

### N5

When the AI meets a case a step's rule doesn't name, can it decide the case as the writer would, from the reason the rule gives, so that the rules hold where their words don't reach?

**Thinking**

A rule that says what it's for lets the AI apply it where the writer meant it. It also lets the AI judge a case that no rule names. So each rule carries its reason, as [add context](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) says.

**Steps**

1. Write the rule as what to do, in plain words, and use no capitals or warnings for emphasis.
2. Where a rule says always or never, say what the AI does when it can't keep the rule.
3. In place of a list of edge cases, give the way of judging and a few typical examples that differ from one another.
4. Think of a case the rule doesn't name, read only the rule and its reason, and check that they lead where the writer would go. Where they don't, mend the reason.

### N6

When the AI runs twice on the same input, does each step whose result must not vary, such as a check or a file's form, give the same result both times, so that what must hold doesn't hang on chance?

**Thinking**

The AI's judgment varies from run to run. That suits a step that has many good ways. So a program does a step that has one right result. The program gives that result on every run and handles its own errors. The AI runs the program, as [utility scripts](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) in the skill authoring best practices say.

**Steps**

1. Read each step and mark each one with one right result, such as a check or a file's form, and give each to a program.

### N7

Can the AI take every action its steps call for with the tools it may use, so that the run never stalls on a missing tool?

**Thinking**

Each action that a step calls for needs a tool that the AI may use. Without that tool, the AI can't take the step, however well the writer writes it.

**Steps**

1. For each step, list each action it takes and the tool that takes it, a script's command among them.
2. Check each tool against those the prompt allows. Where the prompt doesn't allow a tool, either add the tool or change the step.

### N8

When the AI, during a run, reaches for an action that lies outside its task, does the host refuse it, so that a slip of the AI can't harm what lies outside the task?

**Thinking**

A rule in words holds only while the AI follows it. So the writer makes the host refuse each action that must never happen, as [least privilege](https://doi.org/10.1109/PROC.1975.9939) says.

**Steps**

1. List the actions the task must never take, such as writing where it only reads.
2. Allow only the tools N7's list needs.
3. Where a tool it needs also allows an action it must never take, add a rule the host enforces such as a deny rule or a hook.

### N9

When the caller, the person or the AI that started the prompt, takes what the AI hands back, can it act on it without asking the AI anything further, so that the work goes on without a round trip?

**Thinking**

The caller gets only what comes back. So the prompt says what the AI hands back, in what form, and to whom. A step makes each thing in it.

**Steps**

1. Name the caller, and what it does next with the result.
2. List what it needs for that: the result, what the AI did, and what it didn't do and why.
3. Choose the form by who reads it: a fixed form, such as JSON, where a script reads it, and short plain words where a person does.
4. Check that a step makes each thing the output names.

### N10

When a request the prompt is for comes, and a request near it that it isn't for, does the host, such as Claude Code, choose the prompt for the first and pass it over for the second, from the name and the description alone, so that the prompt runs where its writer means it to and nowhere else?

**Thinking**

To pick a prompt for a request, the host reads only the name and the description of each of many prompts. So the name and the description say what the prompt does and when to use it, in the words users ask in. They also tell the prompt apart from the others, as [writing effective descriptions](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) in the skill authoring best practices says.

**Steps**

1. Write down several requests the prompt is for, in a user's own words, and several near ones it isn't for.
2. Write the description: what the prompt does, then the requests and situations to use it for, the main use first.

### N11

Once the host has chosen the prompt by its description, does the AI do the task the description says, all of it and nothing more, so that the caller gets what the description promised?

**Thinking**

The description and the body say the same one task. The AI then does the task that the host chose the prompt for.

**Steps**

1. Set what the description says the prompt does against what the goal and the steps have the AI do. For each thing in one and not the other, add it to the body or take it out of the description.

### N12

When the prompt runs several times on each kind of request it's for, does the AI reach the result the prompt names on every run, so that the user can count on it?

**Thinking**

The writer knows a prompt by what the AI does with it in real use. A rule that must hold on every run rests on a hook, as N14 says, not on runs that happened to keep it. The rest, the AI's variance and the faults of the design, shows only when the product runs on real requests, so the product vision trial runs each kind of request the prompt is for several times, on the model its users run, and the writer judges it from the record of what the AI did.

**Steps**

1. Mend the prompt only for a cause that a record of the product vision trial shows, as N15 says.

### N13

Does every line of the prompt change what the AI does toward the task, so that none draws its attention from the lines that do?

**Thinking**

Every line takes some of the AI's attention. So the prompt keeps only the lines that change what the AI does. It keeps detail that the AI needs only sometimes in a place that the AI reads only then, by [progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

**Steps**

1. Move detail that only some runs need out of the prompt, to a place the AI reads only when it needs the detail, such as a file the prompt links directly. Say in the prompt when to read it.

### N14

For each rule of the steps that must hold on every run, does a hook hold it, and does a test try the hook both where the AI keeps the rule and where it breaks it, so that a rule that must hold doesn't rest on the AI's attention?

**Thinking**

The AI keeps a rule on most runs, not on every run. A [hook](https://code.claude.com/docs/en/hooks) runs on every call, so it holds a rule that must hold, such as a file the AI must not write. A test that puts code in the AI's place tries the hook in seconds, without the model. So no trial runs the prompt alone. What the prompt's words leave is the AI's variance and the faults of the design, and only the trials in real use bring those out.

**Steps**

1. List each rule of the steps that must hold on every run, and for each, a case where the AI keeps it and a case where it breaks it.
2. Hold each such rule with a hook or a deny rule, not with the prompt's words alone.
3. Test the hook on each case, one case at a time.

### N15

When a trial fails, can the maintainer tell from its record that the prompt went wrong and not the trial: its set-up, a stand-in, a judge or a check, so that they mend the prompt only for a cause the record shows?

**Thinking**

A trial's own parts are the set-up, the stand-ins, the judges, and the checks. These parts are code and prompts of their own. So the maintainer builds each part test first. Before a whole run trusts a part, the maintainer checks that the part works right on a record kept from an earlier run. A whole run then only confirms, and a failure in it points to the prompt.

**Steps**

1. Decide by code every point that the record shows, such as a tool called, a file's content or a command's output. Leave to a judge only what code can't decide.
2. Give each judge one point, its definitions, and a pass or fail. Give it messages of each kind whose answer the maintainer knows, and use it only once it judges them right.
3. Give the stand-in for the person only their intent, which the prompt never gets, and the whole of each message it answers. Check on kept conversations that it answers from the intent alone and makes nothing up.
4. Build each part alone and run it small on a kept record before any whole run.
5. Between two runs, change one thing, the prompt or a part of the trial, never both. Where a trial fails, look in its record first at the trial's own parts. Mend the prompt only for a cause in the prompt.

### N16

When the AI puts a decision, a proposal or a report to the person, can the person approve or decide from its first lines alone, and reach the details only where they ask, so that the person spends their attention only on what's theirs?

**Thinking**

The person approves from the conclusion and its grounds. They read further only where these leave them unsure. So a message opens with what it asks or reports and why, in plain sentences. It keeps the rest until the person asks for it, as the [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts the conclusion first.

**Steps**

1. Write a few plain sentences with no headings or labels, in short paragraphs, one point each: first the context and the conclusion, then the grounds, then the purpose and what it should be.
2. Put what the person is to decide alone on the last line, with one recommendation. Ask for one decision in each message.
3. Where the person asks for more, add the state it's in now, with the place it rests on, and the gap between that and what it should be.
4. Use the words the person uses, and say a term of your own in everyday words or leave it out.

### N17

When the caller acts on what the AI reports it did or found, does each claim hold as far as the report says the AI checked it, so that the caller acts only on what holds?

**Thinking**

The caller can't tell a claim the AI checked from one it guessed. So each claim rests on a check that the AI ran on the real thing, on every item the claim names. The report says what the AI left unchecked.

**Steps**

1. Check each claim on the real thing before reporting it: read the file, run the check, open the record. Never rest it on memory, a guess, or what another agent's summary says.
2. Judge a check by a result that comes back pass or fail, such as a command's exit code, not by a few lines of its output.
3. Judge another agent's work from the records and files it names, set against the task's purpose, not from its summary.
4. Check every item the claim names, not a sample.
5. Say what the AI checked and what it didn't, and why, so the report never reads as covering more than it did.
