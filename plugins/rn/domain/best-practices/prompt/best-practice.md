# `prompt`

## Goal tree

- An AI agent that gets the prompt for a request it's meant for does the task as the writer means, with only what its run gives it, on every run, and in cases the writer didn't foresee.
  - **C1** The host runs the prompt for exactly the requests it's for.
    - **N1** Do the name and the description let the host choose the prompt for each request it's for, and pass it over for a near request it isn't for? (Description)
    - **N2** Does the body do exactly the task that the description says, which the architecture gives the role? (Description, Goal)
  - **C2** The AI knows what the task is for, and has every fact it needs.
    - **N3** Does the goal say what the task is for, and how the AI checks that it has reached it? (Goal)
    - **N4** Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies? (Context)
  - **C3** The AI's steps lead to the task's purpose, also in cases that the writer didn't foresee.
    - **N5** Does each step lead toward what the goal says the task is for, with the last step reaching it? (Goal, Steps)
    - **N6** Does each rule give the reason from which the AI decides a case that the rule doesn't name? (Steps)
    - **N7** Does the prompt name the choices that are the user's, and how the AI hands them to the user? (Goal)
    - **N8** Does every line change what the AI does toward the task? (the whole)
  - **C4** What must hold holds on every run, whatever the AI's variance.
    - **N9** Does a program do each step that has one right result? (Steps)
    - **N10** Can the AI take every action that the steps call for with the tools it may use? (Tools, Steps)
    - **N11** Does the host refuse each action that lies outside the task? (Tools)
    - **N12** Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it? (Steps)
  - **C5** The caller can act on what the AI hands back.
    - **N13** Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further? (Steps, Output)
    - **N14** Can the person decide from the first lines of each message that the AI writes to them? (Output)
    - **N15** Does each claim that the AI reports rest on a check it ran on the real thing, with what it didn't check stated? (Output)
  - **C6** The writer knows from tests that the prompt works on every run and in real use.
    - **N16** Do the prompt's unit tests, each case run k times on the model its users run, and the end-to-end (E2E) tests of the product it's part of show the AI reaching the result on every run? (the whole)
    - **N17** Can the maintainer tell from a failed test's record whether the prompt or the test went wrong? (the whole)

## Template

[template.md](template.md)

## Inputs

- [architecture](../architecture/best-practice.md)

## Preconditions

- [architecture](../architecture/best-practice.md)

## Practices

### N1

Do the name and the description let the host choose the prompt for each request it's for, and pass it over for a near request it isn't for?

To pick a prompt for a request, the host reads only the name and the description of each of many prompts, so the prompt runs only where those two lead the host. The [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) give the method for writing effective descriptions.

1. *While deciding.* Write down several requests that the prompt is for, in a user's own words, and several near ones that it isn't for.
2. *While making.* Write the description: what the prompt does, then the requests and situations to use it for, with the main use first, in the words users ask in.
3. *While making.* Add what sets it apart from the other prompts, so that the host passes it over for the near requests.
4. *While making.* Read only the name and the description, as the host does, and check that each request on the first list leads to the prompt and none on the second does.

### N2

Does the body do exactly the task that the description says, which the architecture gives the role?

The caller gets what the description promised only if the body does that same task. The method is requirements traceability, as Orlena Gotel and Anthony Finkelstein [analyze it](https://doi.org/10.1109/ICRE.1994.292398), which follows each requirement backward to its source and forward to what carries it.

1. *While deciding.* Take the task from the architecture: what the role's line in Components says it alone decides, and each step that the sequences give it. The trace: `{inputs}` read to its end.
2. *While making.* Compare what the description says the prompt does with what the goal and the steps have the AI do. For each thing that's in one and not the other, add it to the body or take it out of the description.

### N3

Does the goal say what the task is for, and how the AI checks that it has reached it?

The AI stops when its work looks done, so the prompt must say what the result is for, and give a check that separates done from looking done. The method is Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run), which give the AI a check to run before anything counts as done.

1. *While deciding.* For each thing that holds once the AI has met the task, decide the check that shows it: a command to run where one exists, or else what to look up and where.
2. *While deciding.* Then decide when the AI stops: once every check passes, or at a blocker it can't pass, which it hands back with what it found.

### N4

Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies?

The AI is able but new to this place, and gets nothing of the conversation that started it, so a fact the prompt leaves out becomes a guess. Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) call this adding context.

1. *While deciding.* For each step, list the facts it needs: its inputs and where they lie, the terms it uses, the rules of the place, and what the writer knows without saying.
2. *While deciding.* For each fact, ask whether the AI can find it on its own. If it can, say where it lies. If it can't, give it.

### N5

Does each step lead toward what the goal says the task is for, with the last step reaching it?

An AI that knows what each step is for chooses how to reach it, and follows the purpose where a step doesn't fit the case. The method is the commander's intent of mission command, as the doctrine of the United States Army on mission command sets it out.

1. *While deciding.* Write first what the task is for, for whom, and why.
2. *While deciding.* Then decide the steps by asking where an AI that holds that intent would still not know what to do, such as a check to run or a form to keep, and write a step only there.
3. *While deciding.* Give each step the result it leaves and what that result is for.
4. *While making.* Write the steps in the order their results must hold, such as in a numbered list.
5. *While making.* Check that a later step or the goal uses each step's result, and cut a step whose result nothing uses.
6. *While making.* Check that the last step leaves what the goal says the task is for.

### N6

Does each rule give the reason from which the AI decides a case that the rule doesn't name?

A rule that says what it's for lets the AI apply it where the writer meant it, and judge a case that no rule names, as Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) say.

1. *While making.* Write each rule as what to do, in plain words, with its reason.
2. *While making.* Where a rule says always or never, say what the AI does when it can't keep the rule.
3. *While making.* In place of a list of edge cases, give the way of judging and a few typical examples that differ from one another.
4. *While making.* Use no capitals or warnings for emphasis, since they make the AI apply the rule too widely.
5. *While making.* Think of a case that the rule doesn't name, read only the rule and its reason, and check that they lead where the writer would go. Where they don't, fix the reason.

### N7

Does the prompt name the choices that are the user's, and how the AI hands them to the user?

The user's purpose and intent stay the user's only if the AI hands them the choices that are theirs. The method is the guidance of Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#balancing-autonomy-and-safety) on balancing autonomy and safety, under which the AI asks before an action that's hard to reverse, affects shared systems, or could be destructive.

1. *While deciding.* Among the choices the task meets, mark each that's the user's: each action that's hard to undo, touches what others share, or destroys something, and each choice between options that serve equally, where the AI has no ground to pick one over another. Leave every other choice to the AI.
2. *While making.* Name the user's choices in the prompt, with how the AI asks about them.

### N8

Does every line change what the AI does toward the task?

Every line takes some of the AI's attention from the lines that matter. The method is the [progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) of the skill authoring best practices, which keeps detail that the AI needs only in some runs in a place that it reads only then.

1. *While making.* For each line, ask whether removing it would change what the AI does. If not, cut it.
2. *While making.* Move detail that the AI needs only in some runs to a file that the prompt links directly, and say in the prompt when to read it.

### N9

Does a program do each step that has one right result?

The AI's judgment varies from run to run, which suits a step with many good ways and fails a step with one right result. The method is the [utility scripts](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) of the skill authoring best practices.

1. *While deciding.* Read each step and ask whether it has one right result, such as a check or a file's form. If it does, give it to a program that gives that result on every run and handles its own errors, and have the AI run it.

### N10

Can the AI take every action that the steps call for with the tools it may use?

Without the tool that an action needs, the AI can't take the step, however well the writer writes it.

1. *While deciding.* For each step, list each action it takes and the tool that takes it, including a script's command.
2. *While deciding.* Check each tool against those the prompt allows. Where a step needs a tool that the prompt doesn't allow, allow the tool, or change the step so that it needs none.

### N11

Does the host refuse each action that lies outside the task?

A rule in words holds only while the AI follows it, so a slip of the AI can harm what lies outside the task unless the host refuses the action, by the principle of [least privilege](https://doi.org/10.1109/PROC.1975.9939).

1. *While deciding.* Allow only the tools that N10's list needs.
2. *While deciding.* Where a tool it needs can also act outside the task, such as writing where the task only reads, add a rule that the host enforces, such as a hook.

### N12

Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it?

The AI keeps a rule on most runs, not on every run. The method is Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#enforce-the-rules-that-cant-have-exceptions), which hold a rule that can't have exceptions with a hook or a deny rule.

1. *While deciding.* List each rule of the steps that must hold on every run, and for each, a case where the AI keeps it and a case where it breaks it.
2. *While deciding.* Hold each such rule with a hook or a deny rule, not with the prompt's words alone, since a [hook](https://code.claude.com/docs/en/hooks) runs on every call, so it holds a rule that must hold, such as a file that the AI must not write.
3. *While making.* Test the hook on each case, one case at a time, with code in the AI's place, which tries the hook in seconds without the model, so that checking the rule needs no run of the model.

### N13

Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further?

The caller gets only what comes back, so a result that needs a follow-up question costs a round trip. The method is Ian Robinson's [consumer-driven contracts](https://martinfowler.com/articles/consumerDrivenContracts.html), under which what a provider gives comes from what its consumers need for their next move.

1. *While deciding.* Name the caller and what it does next with the result.
2. *While deciding.* Take what comes back from the step of the architecture's sequences where the role answers, with the data as the data model names it.
3. *While deciding.* List what the caller needs for its next move: the result, what the AI did, and what it didn't do and why.
4. *While deciding.* Choose the form by who reads it: a fixed form, such as JSON, where a script reads it, and short plain words where a person does.
5. *While making.* Check that a step makes each thing that the output names.

### N14

Can the person decide from the first lines of each message that the AI writes to them?

The person approves from the conclusion and its grounds, and reads further only where these leave them unsure. The [inverted pyramid](https://www.nngroup.com/articles/inverted-pyramid/) puts the conclusion first.

1. *While making.* Write each message in a few plain sentences with no headings or labels, in short paragraphs of one point each.
2. *While making.* Put first the context and the conclusion, what the message asks or reports and why, then the grounds, then the purpose and what it should be, and keep the rest until the person asks for it.
3. *While making.* Use the words the person uses, and say a term of your own in everyday words or leave it out.
4. *While making.* Put what the person is to decide alone on the last line, with one recommendation.
5. *While making.* Ask for one decision in each message.
6. *While making.* Where the person asks for more, add the current state, with the place it rests on, and the gap between that and what it should be.

### N15

Does each claim that the AI reports rest on a check it ran on the real thing, with what it didn't check stated?

The caller can't tell a claim that the AI checked from one it guessed, and acts on both alike. The method is the guidance of Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#minimizing-hallucinations-in-agentic-coding) on minimizing hallucinations, under which the AI opens what a claim rests on before it makes the claim.

1. *While making.* Check each claim on the real thing before reporting it: read the file, run the check, open the record. Base it on none of memory, a guess, or another agent's summary.
2. *While making.* Judge a check by a result that comes back pass or fail, such as a command's exit code, not by a few lines of its output.
3. *While making.* Judge another agent's work from the records and files it names, against the task's purpose, not from its summary.
4. *While making.* Check every item that the claim names, not a sample.
5. *While making.* Say what the AI checked and what it didn't, and why, so that the report never reads as covering more than it did.

### N16

Do the prompt's unit tests, each case run k times on the model its users run, and the end-to-end (E2E) tests of the product it's part of show the AI reaching the result on every run?

The writer knows a prompt only by what the AI does with it, where the AI's variance and the faults of the design show. The method is the repeated runs of Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), whose pass^k is the chance that all k runs succeed.

1. *While making.* Run each case that the architecture's test cases hold for the prompt k times on the model its users run, with the k that the architecture's Test strategy sets. A rule that must hold on every run rests on a hook, as N12 says, so the unit tests try the rest.
2. *While making.* Where a run doesn't reach the result, change the prompt only for a cause that its record shows, as N17 says, and run the case k times again.
3. *While making.* Judge the prompt from the record of what the AI did on each run, and check that every run reached the result.
4. *While making.* Confirm by the E2E tests that the prompt, among the other parts, reaches the result on requests as big as real ones, since a unit test meets only the cases that its writer set up.

### N17

Can the maintainer tell from a failed test's record whether the prompt or the test went wrong?

A test's own parts, its set-up, its doubles, its judges, and its checks, are code and prompts of their own, and can fail like the prompt. The method is Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), which takes code over a model to grade where it can, calibrates a model grader against human judgment, and reads the records to tell a failure of the agent from a failure of the test.

1. *While deciding.* Decide by code every point that the record shows, such as a tool called, a file's content, or a command's output. Leave to a judge only what code can't decide.
2. *While making.* Build each part alone, test first, and run it small on a record kept from an earlier run before any whole run relies on it, so that a whole run only confirms, and a failure in it points to the prompt.
3. *While making.* Give each judge one point, its definitions, and a pass or fail result. Give it messages of each kind whose answer the maintainer knows, and use it only once it judges them right.
4. *While making.* Give the stand-in for the person only their intent, which the prompt never gets, and the whole of each message it answers. Check on kept conversations that it answers from the intent alone and invents nothing.
5. *While making.* Between two runs, change one thing, the prompt or a part of the test, never both.
6. *While making.* Where a test fails, look first in its record at the test's own parts, and change the prompt only for a cause in the prompt.
