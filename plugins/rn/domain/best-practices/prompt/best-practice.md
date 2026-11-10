# `prompt`

## Goal

An AI agent that gets the prompt for a request it's meant for does the task as the writer means, with only what its run gives it, on every run, and in cases the writer didn't foresee.

## Inputs

- [architecture](../architecture/best-practice.md)

## Parts

- **description**: what the host reads to choose the prompt for a request: a name that says what the prompt does, and a description of what it does and the requests to use it for.
- **tools**: the tools the AI may use. The prompt lists them where the host reads them, when the host allows such a list. The host refuses any tool not on it.
- **goal**: what the AI reads first in the body: what it's to achieve, for whom, how it knows it has finished, and what lies outside its task.
- **context**: what the AI needs and can't find or know on its own: the situation, its inputs and where they lie, and the rules of this place.
- **steps**: the steps, in the order the AI takes them. Each step names the result that holds when it ends. It gives either the rules the step needs, each with its reason, or the script that does the step and how to run it.
- **output**: what the AI hands back, in what form, and to whom.
- **trials**: the trials that try the prompt in real use: runs of the whole that the prompt is part of, on requests as big as real ones. They also hold the stand-ins that play the person the AI talks with and the parts the prompt works with, the judges, each an AI that gives pass or fail on one point, and the checks on each run's record.

## Critical success factors

| ID | Factor |
| --- | --- |
| C1 | The host runs the prompt for exactly the requests it's for. |
| C2 | The AI knows what the task is for, and has every fact it needs. |
| C3 | The AI's steps lead to the task's purpose, also in cases that the writer didn't foresee. |
| C4 | What must hold holds on every run, whatever the AI's variance. |
| C5 | The caller can act on what the AI hands back. |
| C6 | The writer knows from real use that the prompt works. |

## Necessary conditions

| ID | Factor | Condition | Parts |
| --- | --- | --- | --- |
| N1 | C1 | Do the name and the description let the host choose the prompt for each request it's for, and pass it over for a near request it isn't for? | description |
| N2 | C1 | Does the body do exactly the task that the description says, which the architecture gives the role? | description, goal |
| N3 | C2 | Does the goal say what the task is for, and how the AI checks that it has reached it? | goal |
| N4 | C2 | Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies? | context |
| N5 | C3 | Does each step lead toward what the goal says the task is for, with the last step reaching it? | goal, steps |
| N6 | C3 | Does each rule give the reason from which the AI decides a case that the rule doesn't name? | steps |
| N7 | C3 | Does the prompt name the choices that are the user's, and how the AI hands them to the user? | goal |
| N8 | C3 | Does every line change what the AI does toward the task? | the whole |
| N9 | C4 | Does a program do each step that has one right result? | steps |
| N10 | C4 | Can the AI take every action that the steps call for with the tools it may use? | tools, steps |
| N11 | C4 | Does the host refuse each action that lies outside the task? | tools |
| N12 | C4 | Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it? | steps |
| N13 | C5 | Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further? | steps, output |
| N14 | C5 | Can the person decide from the first lines of each message that the AI writes to them? | output |
| N15 | C5 | Does each claim that the AI reports rest on a check it ran on the real thing, with what it didn't check stated? | output |
| N16 | C6 | Do trials on each kind of request the prompt is for, each run several times on the model its users run, show the AI reaching the result on every run? | the whole |
| N17 | C6 | Can the maintainer tell from a failed trial's record whether the prompt or the trial went wrong? | trials |

## Practices

### N1

Do the name and the description let the host choose the prompt for each request it's for, and pass it over for a near request it isn't for?

**Thinking**

To pick a prompt for a request, the host reads only the name and the description of each of many prompts, so the prompt runs only where those two lead the host. The [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) give the method for writing effective descriptions. Decide them in order. First, write down several requests that the prompt is for, in a user's own words, and several near ones that it isn't for. Second, write the description: what the prompt does, then the requests and situations to use it for, with the main use first, in the words users ask in. Third, add what sets it apart from the other prompts, so that the host passes it over for the near requests. Check each request on both lists against the name and the description alone.

### N2

Does the body do exactly the task that the description says, which the architecture gives the role?

**Thinking**

The caller gets what the description promised only if the body does that same task. Take the task from the architecture: what the role's line in Components says it alone decides, and each step that the sequences give it. Compare what the description says the prompt does with what the goal and the steps have the AI do. For each thing that's in one and not the other, add it to the body or take it out of the description.

### N3

Does the goal say what the task is for, and how the AI checks that it has reached it?

**Thinking**

The AI stops when its work looks done, so the prompt must say what the result is for, and give a check that separates done from looking done. For each thing that holds once the AI has met the task, decide the check that shows it: a command to run where one exists, or else what to look up and where. Then decide when the AI stops: once every check passes, or at a blocker it can't pass, which it hands back with what it found.

### N4

Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies?

**Thinking**

The AI is able but new to this place, and gets nothing of the conversation that started it, so a fact the prompt leaves out becomes a guess. Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) call this adding context. For each step, list the facts it needs: its inputs and where they lie, the terms it uses, the rules of the place, and what the writer knows without saying. For each fact, ask whether the AI can find it on its own. If it can, say where it lies. If it can't, give it.

### N5

Does each step lead toward what the goal says the task is for, with the last step reaching it?

**Thinking**

An AI that knows what each step is for chooses how to reach it, and follows the purpose where a step doesn't fit the case. Write first what the task is for, for whom, and why. Then decide the steps by asking where an AI that holds that intent would still not know what to do, such as a check to run or a form to keep, and write a step only there. Give each step the result it leaves and what that result is for. Write the steps in the order their results must hold, such as in a numbered list.

**Steps**

1. Check that a later step or the goal uses each step's result, and cut a step whose result nothing uses.
2. Check that the last step leaves what the goal says the task is for.

### N6

Does each rule give the reason from which the AI decides a case that the rule doesn't name?

**Thinking**

A rule that says what it's for lets the AI apply it where the writer meant it, and judge a case that no rule names, as Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) say. Write each rule as what to do, in plain words, with its reason. Where a rule says always or never, say what the AI does when it can't keep the rule. In place of a list of edge cases, give the way of judging and a few typical examples that differ from one another. Use no capitals or warnings for emphasis, since they make the AI apply the rule too widely.

**Steps**

1. Think of a case that the rule doesn't name, read only the rule and its reason, and check that they lead where the writer would go. Where they don't, fix the reason.

### N7

Does the prompt name the choices that are the user's, and how the AI hands them to the user?

**Thinking**

The user's purpose and intent stay the user's only if the AI hands them the choices that are theirs. A choice is the user's where the AI has no ground to pick one option over another, or where the choice is hard to undo. Among the choices the task meets, mark each action that's hard to undo, touches what others share, or destroys something, and each choice between options that serve equally. Name those in the prompt, with how the AI asks about them. Leave every other choice to the AI.

### N8

Does every line change what the AI does toward the task?

**Thinking**

Every line takes some of the AI's attention from the lines that matter. For each line, ask whether removing it would change what the AI does. If not, cut it. Keep detail that the AI needs only in some runs in a place that it reads only then, by [progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices).

**Steps**

1. Move detail that only some runs need to a file that the prompt links directly, and say in the prompt when to read it.

### N9

Does a program do each step that has one right result?

**Thinking**

The AI's judgment varies from run to run, which suits a step with many good ways and fails a step with one right result. Read each step and ask whether it has one right result, such as a check or a file's form. Give each such step to a program that gives that result on every run and handles its own errors, and have the AI run it, as the [utility scripts](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) of the skill authoring best practices do.

### N10

Can the AI take every action that the steps call for with the tools it may use?

**Thinking**

Without the tool that an action needs, the AI can't take the step, however well the writer writes it. For each step, list each action it takes and the tool that takes it, including a script's command. Check each tool against those the prompt allows. Where a step needs a tool that the prompt doesn't allow, allow the tool, or change the step so that it needs none.

### N11

Does the host refuse each action that lies outside the task?

**Thinking**

A rule in words holds only while the AI follows it, so a slip of the AI can harm what lies outside the task unless the host refuses the action, by the principle of [least privilege](https://doi.org/10.1109/PROC.1975.9939). Allow only the tools that N10's list needs. Where a tool it needs can also act outside the task, such as writing where the task only reads, add a rule that the host enforces, such as a hook.

### N12

Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it?

**Thinking**

The AI keeps a rule on most runs, not on every run. A [hook](https://code.claude.com/docs/en/hooks) runs on every call, so it holds a rule that must hold, such as a file that the AI must not write. A test that puts code in the AI's place tries the hook in seconds without the model, so checking the rule needs no trial of the prompt. List each rule of the steps that must hold on every run, and for each, a case where the AI keeps it and a case where it breaks it. Hold each such rule with a hook or a deny rule, not with the prompt's words alone.

**Steps**

1. Test the hook on each case, one case at a time.

### N13

Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further?

**Thinking**

The caller gets only what comes back, so a result that needs a follow-up question costs a round trip. Name the caller and what it does next with the result. Take what comes back from the step of the architecture's sequences where the role answers, with the data as the data model names it. List what it needs for that: the result, what the AI did, and what it didn't do and why. Choose the form by who reads it: a fixed form, such as JSON, where a script reads it, and short plain words where a person does.

**Steps**

1. Check that a step makes each thing that the output names.

### N14

Can the person decide from the first lines of each message that the AI writes to them?

**Thinking**

The person approves from the conclusion and its grounds, and reads further only where these leave them unsure. The [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts the conclusion first. Open each message with what it asks or reports and why, in plain sentences, and keep the rest until the person asks for it. Use the words the person uses, and say a term of your own in everyday words or leave it out.

**Steps**

1. Write a few plain sentences with no headings or labels, in short paragraphs, one point each: first the context and the conclusion, then the grounds, then the purpose and what it should be.
2. Put what the person is to decide alone on the last line, with one recommendation. Ask for one decision in each message.
3. Where the person asks for more, add the current state, with the place it rests on, and the gap between that and what it should be.

### N15

Does each claim that the AI reports rest on a check it ran on the real thing, with what it didn't check stated?

**Thinking**

The caller can't tell a claim that the AI checked from one it guessed, and acts on both alike. So base each claim on a check that the AI ran on the real thing, on every item that the claim names, and say what it left unchecked.

**Steps**

1. Check each claim on the real thing before reporting it: read the file, run the check, open the record. Base it on none of memory, a guess, or another agent's summary.
2. Judge a check by a result that comes back pass or fail, such as a command's exit code, not by a few lines of its output.
3. Judge another agent's work from the records and files it names, against the task's purpose, not from its summary.
4. Check every item that the claim names, not a sample.
5. Say what the AI checked and what it didn't, and why, so that the report never reads as covering more than it did.

### N16

Do trials on each kind of request the prompt is for, each run several times on the model its users run, show the AI reaching the result on every run?

**Thinking**

The writer knows a prompt only by what the AI does with it in real use. A rule that must hold on every run rests on a hook, as N12 says. The rest, the AI's variance and the faults of the design, shows only when the product runs on real requests. So the product vision trial runs each kind of request that the prompt is for several times, on the model its users run, and the writer judges it from the record of what the AI did.

**Steps**

1. Change the prompt only for a cause that a record of the product vision trial shows, as N17 says.

### N17

Can the maintainer tell from a failed trial's record whether the prompt or the trial went wrong?

**Thinking**

A trial's own parts, its set-up, its stand-ins, its judges, and its checks, are code and prompts of their own, and can fail like the prompt. So build each part test first, and check it on a record kept from an earlier run before a whole run relies on it. A whole run then only confirms, and a failure in it points to the prompt.

**Steps**

1. Decide by code every point that the record shows, such as a tool called, a file's content, or a command's output. Leave to a judge only what code can't decide.
2. Give each judge one point, its definitions, and a pass or fail result. Give it messages of each kind whose answer the maintainer knows, and use it only once it judges them right.
3. Give the stand-in for the person only their intent, which the prompt never gets, and the whole of each message it answers. Check on kept conversations that it answers from the intent alone and invents nothing.
4. Build each part alone and run it small on a kept record before any whole run.
5. Between two runs, change one thing, the prompt or a part of the trial, never both. Where a trial fails, look first in its record at the trial's own parts. Change the prompt only for a cause in the prompt.
