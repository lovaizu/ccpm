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

To pick a prompt for a request, the host reads only the name and the description of each of many prompts, so the prompt runs only where those two lead the host. Prompt writers write such a description as the [skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) do: what the prompt does, then when to use it, in the third person and in the words users ask in.

1. *While deciding.* Open the architecture's user stories whose sequences the role takes part in, and write down several requests that the prompt is for, each in a user's own words, from the way the story's role meets the product, such as `turn issue 12 into a plan`. Then write down several near requests that it isn't for, each from a story that another part carries. The trace: `{inputs}` read to its end.
2. *While making.* Write the description in the third person: first what the prompt does, then `Use when` with the requests and situations of the first list, the main use first, such as `Extracts text and tables from PDF files. Use when the user mentions PDFs, forms, or document extraction.`
3. *While making.* Open the description of each other prompt that the host chooses among for the near requests: each skill and agent of the product, in the folders that the architecture's Directory structure gives, and each of the host's own that a near request names, such as a built-in command. Where a near request fits the prompt's description as well as another's, add what sets the prompt apart, such as the kind of input it takes.
4. *While making.* Read only the name and the description, as the host does, and check that each request on the first list leads to the prompt and none on the second does.

### N2

Does the body do exactly the task that the description says, which the architecture gives the role?

The caller gets what the description promised, and the product gets what the architecture gives the role, only if the body does that same task.

1. *While deciding.* Take the task from the architecture: the role's line in Components, which says what the role alone decides, and each arrow from or to the role in Sequences, which says each step it takes and the data it hands on.
2. *While making.* Compare what the description says the prompt does with what the goal and the steps have the AI do. For each thing that's in one and not the other, add it to the body or take it out of the description.

### N3

Does the goal say what the task is for, and how the AI checks that it has reached it?

The AI stops when its work looks done, so the prompt must say what the result is for, and give a check that separates done from looking done, as Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#give-claude-a-check-to-run) give the AI something to run that comes back pass or fail.

1. *While deciding.* Write what the task is for in one sentence: whom the result serves, the role of each user story whose sequence the role takes part in, and what they gain by it, the story's benefit, such as `so that the developer gets a plan they can approve in one reading`.
2. *While deciding.* List what holds once the AI has done the task: each thing it hands on at its last arrow in Sequences, and each file or state it leaves, such as a plan written in its form.
3. *While deciding.* For each thing on the list, decide the check that shows it holds: a command that comes back pass or fail where the product has one, such as a schema check or a test, since its result doesn't rest on the AI's reading, or else what to open and what to compare it with, such as the plan against the request.
4. *While deciding.* Decide when the AI stops: once every check passes, or at a blocker it can't pass, which it hands back with what it found.

### N4

Does the prompt give every fact that the AI can't find or know on its own, and say where the rest lies?

The AI is able but new to this place, and gets nothing of the conversation that started it, so a fact the prompt leaves out becomes a guess, and a fact the AI would find anyway takes its attention from the rest.

1. *While deciding.* For each step, list the facts it needs. Take its inputs and where they lie from the arrows to the role in the architecture's Sequences and from its Directory structure, and the terms it uses from the data model. Take the rules of the place from the architecture's Principles and the rules they build on, such as the one folder a role writes in. Add what the writer knows without saying, such as a decision made in a meeting.
2. *While deciding.* For each fact, ask the two questions of Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#tell-claude-what-it-cant-see): could the AI find it by reading what its run gives it, and would it go and look? Where both answers are yes, leave the fact out. Where it could find it but wouldn't look, say where it lies, such as `The plan takes the form of plan.schema.json`. Where it couldn't find it, give the fact.

### N5

Does each step lead toward what the goal says the task is for, with the last step reaching it?

An AI that knows what each step's result is for chooses how to reach it, and follows the purpose where a step doesn't fit the case.

1. *While deciding.* Go through the steps that the role's arrows in the architecture's Sequences give it, and ask of each whether an AI that holds the goal, as N3.1 wrote it, would know how to reach the step's result. Write a step only where it wouldn't, such as a check to run or a form to keep, and leave the rest to the AI.
2. *While deciding.* Give each step the result it leaves and what that result is for, such as `Run check.sh. Its exit code 0 is the check that the goal names.`
3. *While making.* Write the steps in the order their results must hold, such as in a numbered list.
4. *While making.* Check that a later step or the goal uses each step's result, and cut a step whose result nothing uses.
5. *While making.* Check that the last step leaves what the goal says the task is for.

### N6

Does each rule give the reason from which the AI decides a case that the rule doesn't name?

A rule that says what it's for lets the AI apply it where the writer meant it, and judge a case that no rule names, as Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#add-context-to-improve-performance) say: the AI generalizes from the reason.

1. *While making.* Write each rule as what to do, in plain words, with its reason, such as `Your response is read aloud by a text-to-speech engine, so never use ellipses, which it can't pronounce` in place of `NEVER use ellipses`.
2. *While making.* Where a rule says always or never, say what the AI does when it can't keep the rule, such as `Never push to main. Where a push is needed, hand it back as a question.`
3. *While making.* In place of a list of edge cases, give the way of judging and a few examples that are like the real requests and unlike one another.
4. *While making.* Use no capitals or warnings for emphasis, since they make the AI apply the rule too widely.
5. *While making.* Think of a case that the rule doesn't name, read only the rule and its reason, and check that they lead where the writer would go. Where they don't, fix the reason.

### N7

Does the prompt name the choices that are the user's, and how the AI hands them to the user?

The user's purpose and intent stay the user's only if the AI hands them the choices that are theirs.

1. *While deciding.* Go through the steps, and each branch and each question to the role in the architecture's Sequences, and mark each choice that's the user's: each action that's hard to undo, touches what others share, or destroys something, as the list in Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#balancing-autonomy-and-safety) gives, such as a force push, a comment on a pull request, or deleting a branch, and each choice between options that serve the purpose equally, where the AI has no ground to pick one. Leave every other choice to the AI.
2. *While making.* Name each of the user's choices in the step where it comes, with how it reaches the user. A role that runs as a subagent can't talk to the person, so it ends with the result that Sequences give for a question to its caller, with the point, the options, and its recommendation, such as `End with asks, naming the branch to push and your recommendation.` A role that runs in the main conversation asks the person in a message, as N14 says, one choice at a time.

### N8

Does every line change what the AI does toward the task?

Every line takes some of the AI's attention from the lines that matter, so prompt writers keep detail that the AI needs only in some runs in a file that it reads only then, as the [progressive disclosure](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) of the skill authoring best practices does.

1. *While making.* For each line, ask whether removing it would change what the AI does. If not, cut it, such as `Read the files carefully`, which the AI does without the line.
2. *While making.* Move detail that the AI needs only in some runs to a file that the prompt links directly, and say in the prompt when to read it.

### N9

Does a program do each step that has one right result?

The AI's judgment varies from run to run, which suits a step with many good ways and fails a step with one right result, so the skill authoring best practices give such a step to a [utility script](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) that the AI runs.

1. *While deciding.* Read each step and ask whether it has one right result, such as a check or a file's form. If it does, give it to a program that gives that result on every run and handles its own errors, and have the AI run it.

### N10

Can the AI take every action that the steps call for with the tools it may use?

Without the tool that an action needs, the AI can't take the step, however well the writer writes it.

1. *While deciding.* For each step, list each action it takes and the tool that takes it, including a script's command, such as `Bash(sh dev/scripts/check.sh)` for a step that runs the checks.
2. *While deciding.* Check each tool against the list that the prompt allows, such as the `tools` field of an agent's frontmatter. Where a step needs a tool that isn't on it, allow the tool if the action lies inside the task and N11 can keep the tool to the task. Otherwise, change the step so that it needs no such tool, such as having a script that the step runs fetch what the step needs.

### N11

Does the host refuse each action that lies outside the task?

A rule in words holds only while the AI follows it, so a slip of the AI can harm what lies outside the task unless the host refuses the action.

1. *While deciding.* Allow only the tools that N10's list needs, in the list that the host reads, such as the `tools` field of an agent's frontmatter.
2. *While deciding.* Where a tool it needs can also act outside the task, such as writing where the task only reads, add a rule that the host enforces: a deny rule where a permission pattern names the action, such as `Edit(./docs/**)`, or else a hook, as N12 says.

### N12

Does a hook hold each rule that must hold on every run, with a test of the hook both where the AI keeps the rule and where it breaks it?

The AI keeps a rule on most runs, not on every run, while a rule that the host enforces holds on every run, as Claude Code's [best practices](https://code.claude.com/docs/en/best-practices#enforce-the-rules-that-cant-have-exceptions) hold a rule that can't have exceptions with a hook or a deny rule.

1. *While deciding.* List each rule of the steps that has no exception, where a single break would fail the users, such as a file that the AI must not write, and for each, a call where the AI keeps it and a call where it breaks it. Leave a rule with exceptions, such as a preference for a style, to the prompt's words.
2. *While deciding.* Hold each such rule with a deny rule where it limits what the AI may read, write, or run, and a permission pattern names it, such as `Read(./.env)`, since a deny rule holds in every permission mode. Hold it with a command [hook](https://code.claude.com/docs/en/hooks) where it's a step that must happen, or where it turns on more than a pattern names, such as a write allowed only into the run's own file.
3. *While making.* Test the hook on each case alone, with code in the AI's place: pipe the JSON that the host sends for the call into the hook's command, as the [hooks guide](https://code.claude.com/docs/en/hooks-guide) does, and check its exit code or the decision it prints, such as `echo '{"tool_name":"Write","tool_input":{"file_path":"src/gen/a.py"}}' | ./guard.sh` giving 2, which blocks the call, and 0 for a path the AI may write. Such a test runs in seconds without the model.

### N13

Can the caller act on what comes back, in the form that the architecture's sequences hand on, without asking the AI anything further?

The caller gets only what comes back, so a result that needs a follow-up question costs a round trip, and a result in a form the caller doesn't read stops the sequence there.

1. *While deciding.* Open each sequence that the role takes part in, and name the caller: the one whose arrow starts the role and who gets its answer. Write what the caller does with the result at its next arrow.
2. *While deciding.* Take what comes back from the arrow where the role answers the caller, with the data as the data model names it.
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

The caller can't tell a claim that the AI checked from one it guessed, and acts on both alike, so Anthropic's [prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices#minimizing-hallucinations-in-agentic-coding) have the AI open what a claim rests on before it makes the claim.

1. *While making.* Check each claim on the real thing before reporting it: read the file, run the check, open the record. Base it on none of memory, a guess, or another agent's summary.
2. *While making.* Judge a check by a result that comes back pass or fail, such as a command's exit code, not by a few lines of its output.
3. *While making.* Judge another agent's work from the records and files it names, against the task's purpose, not from its summary.
4. *While making.* Check every item that the claim names, not a sample.
5. *While making.* Say what the AI checked and what it didn't, and why, so that the report never reads as covering more than it did.

### N16

Do the prompt's unit tests, each case run k times on the model its users run, and the end-to-end (E2E) tests of the product it's part of show the AI reaching the result on every run?

The writer knows a prompt only by what the AI does with it, where the AI's variance and the faults of the design show, so Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) runs each task k times and counts it passed only where all k runs succeed, its pass^k.

1. *While making.* Run each case of the prompt, in the folders that the architecture's Test strategy names for its test cases, k times on the model its users run, with the k that Test strategy sets. A rule that must hold on every run rests on a hook, as N12 says, so the unit tests try the rest.
2. *While making.* Open the record of each run, as the test's runner keeps it, such as the JSON lines that `claude -p --output-format stream-json --verbose` writes, and check from what the AI did, not from its last message, that every run reached the result.
3. *While making.* Where a run didn't reach the result, find the cause in its record, as N17 says, change the prompt only for a cause in the prompt, and run the case k times again.
4. *While making.* Confirm by the E2E tests that the prompt, among the other parts, reaches the result on requests as big as real ones, since a unit test meets only the cases that its writer set up.

### N17

Can the maintainer tell from a failed test's record whether the prompt or the test went wrong?

A test's own parts, its set-up, its doubles, its judges, and its checks, are code and prompts of their own, and can fail like the prompt. Anthropic's [demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) is how eval writers keep the two apart: they grade by code where they can, check a model grader against people's judgment, and read the records to tell a failure of the agent from a failure of the test.

1. *While deciding.* Decide by code every point that the record shows, such as a tool called, a file's content, or a command's output. Leave to a judge only what code can't decide.
2. *While making.* Build each part of the test alone, test first, and run it on a record kept from an earlier run, such as the JSON lines of one run saved beside the test, before any whole run relies on it, so that a whole run only confirms, and a failure in it points to the prompt.
3. *While making.* Give each judge one point, its definitions, and a pass or fail result. Run it on messages of each kind, kept from earlier runs, that the maintainer has marked pass or fail, and use it only once it gives each message the maintainer's mark.
4. *While making.* Give the stand-in for the person only their intent, which the test case gives and the prompt never gets, and the whole of each message it answers. Run it on conversations kept from earlier runs, and check that each answer comes from the intent alone and invents nothing.
5. *While making.* Between two runs, change one thing, the prompt or a part of the test, never both.
6. *While making.* Where a test fails, open its record and look first at the test's own parts, and change the prompt only for a cause in the prompt.
