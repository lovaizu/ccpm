# `prompt`

## Goal

The AI that runs the prompt does the task as the one who asked for it means, in every case it meets and on every run.

## Inputs

- [architecture](../architecture/best-practice.md)

## Parts

- **description**: The name and the description by which a host chooses the prompt for a request, or its caller knows it: what the prompt does and the requests it's for, the main use first.
- **tools**: The tools the AI may use, set where the host reads and enforces them, such as a subagent's tools field: each tool an action of the task needs, and none other.
- **guards**: What holds each rule that must hold on every run outside the AI's judgment, such as a permission rule, a hook, or the program that calls the model, with the tests that show it holding.
- **body**: The text the AI reads when it runs the prompt.
  - **goal**: What the task is for and for whom, what lies outside it, and the checks that tell done from looking done.
  - **context**: Each fact the AI needs and can't find or know on its own, such as what someone decided before the run, and where to find the rest, such as its inputs' paths.
  - **rules**: How the AI judges the cases the task meets, each rule with its reason, and the choices it hands back.
  - **steps**: The actions whose order or completeness the result depends on, in their order, each one action with what shows it done, and the programs a step runs.
  - **examples**: A few cases that differ, each with the result the writer means, set apart from the instructions.
  - **output**: What the AI hands back, to whom, and in what form, with what it checked and what it didn't.
- **references**: The detail only some runs need, in files the body links once and says when to read.
- **evals**: The tasks that try the prompt, drawn from real cases with the result each should reach, some held back from its making, with the graders that judge each run and the kept records that proved them.

## Intents

| ID | About | Question |
| --- | --- | --- |
| Q1 | goal | Reading the goal, does the AI see the end its task serves, what lies outside it, and the checks that tell done from looking done, so that it stops once it meets the end, and not at its last step or before? |
| Q2 | context | Starting with only the prompt and what its run gives it, does the AI find in the prompt each fact it can't find or know on its own, and where to look for the rest, so that it acts on facts and not on guesses? |
| Q3 | rules | Meeting a case that the words of any of its rules don't reach, can the AI decide it as the writer would, from the reason that rule gives, so that the rules hold where their words stop? |
| Q4 | examples | Where a case shows the result's form or judgment better than words, does the AI see in the examples the pattern the writer means across cases that differ, so that it follows the intent in the case before it and copies no one case's particulars? |
| Q5 | steps | Following the prompt, does the AI meet a step wherever skipping an action or taking it out of order breaks the result, and only there, each one action with what shows it done, and its own judgment everywhere else, so that it keeps the order that matters and reasons freely in the rest? |
| Q6 | steps | Where a step has one right result, such as a check, a count, or a file's form, does the AI run a program that gives it and act on what the program reports, so that what must be right doesn't hang on the AI's judgment from run to run? |
| Q7 | tools | Taking each action its task calls for, does the AI find the tool it needs allowed, and each tool its task doesn't need withheld by the host, so that the run never stalls on a missing tool and a slip can't reach what lies outside the task? |
| Q8 | guards | For each rule that must hold on every run, such as a file never written or a step never skipped, does something outside the AI hold it, and does a test show it holding both where the AI keeps the rule and where it breaks it, so that what must hold doesn't rest on the AI's attention? |
| Q9 | rules, output | Meeting a choice that isn't its own, such as an action hard to undo, one that others share, or one between ways the caller's intent leaves open, does the AI hand it back, and settle every other choice itself, so that the caller keeps their intent and answers only what the AI can't settle? |
| Q10 | output | Taking what the AI hands back, can the caller act on it without asking anything further, a program by a fixed form and a person by plain words, with what the AI did and what it didn't, so that the work goes on without a round trip? |
| Q11 | output | Where the AI puts a decision, a proposal, or a report to a person, can the person decide from its first lines, and reach the details only where they ask, so that they spend their attention only on what's theirs? |
| Q12 | output | Acting on what the AI reports it did or found, does the caller meet each claim backed by a check the AI ran on the real thing, and learn what it left unchecked, so that they act only on what holds? |
| Q13 | description | Choosing among many prompts by name and description alone, does the host pick this one for each request it's for and pass it over for a near one it isn't for, and does the body then do what the description promises, so that the prompt runs where it's meant and its caller gets what it promised? |
| Q14 | body, references | Reading the prompt once, does the AI meet each instruction in one place, each thing under one term, and no two instructions that pull apart, so that it spends no reasoning on reconciling them and never follows the wrong one? |
| Q15 | body, references | Reading the prompt, does the AI meet only lines that change what it does, with the detail that only some runs need in a file it reads then, so that its attention goes to what counts in its case? |
| Q16 | evals | Trying a prompt that runs more than once, does the maintainer have tasks drawn from real failures, where a behavior should happen and where it shouldn't, each run graded by code where code can tell and by a judge proven on kept records where it can't, so that a failing eval points at the prompt and not at the eval? |
| Q17 | the whole | Trying a prompt that runs more than once, on requests held back from its making, of each kind it's for, several times on each model it runs on, does the AI do the task as the one who asked for it means on every run? |

## Practices

### Q1

Reading the goal, does the AI see the end its task serves, what lies outside it, and the checks that tell done from looking done, so that it stops once it meets the end, and not at its last step or before?

**Name**

Success criteria, also known as definition of done and stop conditions

**Thinking**

Write first what the task is for and for whom, as a model that knows the end behind a request connects it to what it finds and doesn't infer the end on its own. Then name each condition that holds once the AI meets the end, each with the check that shows it: a command to run where one exists, else what to look at and where. An agent stops once its work looks done, and a check that its environment gives back, such as a test's result, is what tells it the work has reached its end. Write what lies outside the task, as a capable model widens a narrow task with steps no one asked for. Say where the AI stops short of the end: at a blocker it can't pass, or at a choice that isn't its own, which Q9 names, handing back what it found. Say too what isn't a stop, such as a subagent or a command it started that still runs, as a model can end its turn on a summary that announces its next step instead of taking it.

**Applies**

Every prompt for a task with an end, and most where the AI runs many steps or runs unattended.

**Excludes**

A prompt for one answer, such as a label for a ticket, ends with its answer, and its output form says when it's done, as Q10 says. Leave out a check the model makes unasked, such as a final review of its own code on a model whose guide says it verifies its work on its own, as one written in makes it check twice.

**Cost**

The writer settles the end and a check for each condition before writing the rest, and a condition with no check leaves the AI to judge it, which Q12 then holds to what it checked.

**Sources**

- [Anthropic, Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic, Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Anthropic, Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- [Anthropic, Prompting Claude Opus 5.5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5-5)
- [OpenAI, GPT-5 prompting guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)

### Q2

Starting with only the prompt and what its run gives it, does the AI find in the prompt each fact it can't find or know on its own, and where to look for the rest, so that it acts on facts and not on guesses?

**Name**

Context engineering, also known as just-in-time context and the colleague test

**Thinking**

The AI that runs the prompt is able but new to the place, like a brilliant employee on their first day. A subagent starts with none of the conversation that started it, none of the files read there, and none of what someone decided there, so a brief holds whatever its writer knows and the subagent doesn't. Write each fact the AI can't find or know on its own: what someone decided before the run, the terms of the place, its rules, and what the writer knows without saying it. For what it can find, give where to look, such as a path, a command, or an identifier, and let it load what it needs as it goes, as a prompt that holds everything spends attention on what most runs don't need. A pointer to a document gives the AI that document only where it reads it whole and knows what to take from it, so say what the AI takes from it, and where an order or a check from it must hold, write it into the prompt as Q5 and Q8 say. Try the prompt on someone with none of your context, such as a fresh AI given only what a run gives it. Where they'd stop or guess, the AI does too, so add the fact they lacked.

**Applies**

Every prompt, and most a brief that one AI writes for another, which starts with nothing but the brief.

**Excludes**

What a capable model already knows, such as what a test is, needs no line, as Q15 says. A fact that changes from run to run goes in what the run gives, such as its inputs, not in the prompt's text.

**Cost**

The writer names what they know without saying it, which takes a reading by someone without their context, and the AI reads each fact added on every run.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Claude Code, Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)

**Steps**

1. Read each input whole before you write the prompt. The trace: `{inputs}` read to its end.

### Q3

Meeting a case that the words of any of its rules don't reach, can the AI decide it as the writer would, from the reason that rule gives, so that the rules hold where their words stop?

**Name**

Explain the why, also known as the right altitude and heuristics over rigid rules

**Thinking**

Give each rule with the reason it serves, as a model generalizes from the reason to cases the rule doesn't name, such as never using ellipses because a text-to-speech engine reads the reply aloud. Write the rule at the right altitude: specific enough to guide what the AI does, and general enough to leave it a heuristic. Hard-coded if-else logic breaks on the first case its writer didn't foresee, and vague guidance leaves the AI to guess what the writer assumed. Say what to do, not what to avoid, as a model told what not to do still has to guess the alternative. Write plainly, with no capitals or warnings for weight, as a current model follows a plain instruction, and one written as CRITICAL or MUST overtriggers. Where a rule says always or never, say what the AI does when it can't keep it. In place of a list of edge cases, give the way to judge them and a few examples that differ, as Q4 says.

**Applies**

Every rule of a prompt that the AI applies by judgment.

**Excludes**

A rule that must hold on every run rests on a guard as well, as Q8 says. The prompt still gives its reason, so that the AI keeps it and the guard rarely has to stop it.

**Cost**

A reason lengthens the rule, so give each reason once, where the rule stands, as Q14 says.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic, Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)

### Q4

Where a case shows the result's form or judgment better than words, does the AI see in the examples the pattern the writer means across cases that differ, so that it follows the intent in the case before it and copies no one case's particulars?

**Name**

Few-shot prompting, also known as multishot prompting and diverse, canonical examples

**Thinking**

Where the result's form, tone, or judgment shows better than it's told, give a few examples, such as three to five, as examples steer a model's output more reliably than a description. Make them relevant to the real cases, and different from one another where the cases differ, so that the AI takes what stays the same across them and no one case's particulars. Keep their format the same, as the AI copies a difference of format too. Set them apart from the instructions, such as in tags of their own, so that the AI tells an example from a rule. For a judgment, show each as the case, the way of judging, and the result. Draw them from real cases, and keep them apart from the evals' tasks, as an example that's also a task makes its eval pass by copying.

**Applies**

A prompt whose result has a form, a tone, or a judgment that words state less exactly than a case shows.

**Excludes**

Where a schema or a fixed form states the result whole, give the schema, as Q10 says. A prompt whose task has no pattern to show, such as a brief whose specification holds the cases, needs no examples.

**Cost**

The AI reads each example on every run, and too many lead the model to fit them and not the task.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [OpenAI, Prompt engineering](https://platform.openai.com/docs/guides/prompt-engineering)

### Q5

Following the prompt, does the AI meet a step wherever skipping an action or taking it out of order breaks the result, and only there, each one action with what shows it done, and its own judgment everywhere else, so that it keeps the order that matters and reasons freely in the rest?

**Name**

Degrees of freedom, also known as low and high freedom and workflow checklists

**Thinking**

Match how closely the prompt leads to how fragile the task is. Where only one way is safe, such as a migration that must run in sequence, give numbered steps, each one action with the result or the call that shows it done. Where many ways lead to the result, such as a review, give the end and the heuristics, and let the AI find its way, as a model told to think thoroughly often reasons past a plan written by hand. Keep standing rules, such as what never to read, apart from the steps, as a step that bundles them hides which action it asks for. Where a step's order must hold on every run, such as the tests run before the code, write it as a step and have a guard hold it, as Q8 says. A pointer to another document's order holds nothing. Grade the result, not the path, as Q16 says, so that the AI keeps to no path but the steps.

**Applies**

Every prompt with actions whose order or completeness the result depends on.

**Excludes**

A task with many valid paths and no fragile action needs no steps. Its prompt gives the end, the rules, and the checks.

**Cost**

A step binds every run to it, and steps written for an earlier model often lead a newer one worse than its own reasoning, so each one stands only where its order matters.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

### Q6

Where a step has one right result, such as a check, a count, or a file's form, does the AI run a program that gives it and act on what the program reports, so that what must be right doesn't hang on the AI's judgment from run to run?

**Name**

Utility scripts and feedback loops, also known as solve, don't defer and plan-validate-execute

**Thinking**

A program gives one result on every run, and the AI's judgment varies from run to run, so a step that has one right result, such as a check, a count, or a file's form, is a program the AI runs. Say whether the AI runs the program or reads it, as running it costs only its output. Have the program handle its own errors and say what to put right, such as which field is missing and which fields exist, so that the AI mends what it names. Close the loop: the AI runs the check, mends what it reports, and runs it again until it passes. Before a batch or a change hard to undo, have the AI write its plan in a form a program checks, and check it before acting. Where the AI writes a file, a tool that takes it whole or a narrow interface keeps it from errors that a hand-made format invites, such as a count of lines.

**Applies**

Each step with one right result, and each change hard to undo or made to many things at once.

**Excludes**

A step of judgment with many good results stays the AI's, judged by the evals.

**Cost**

The program is code of its own, made and tested by the code best practice before anyone tries the prompt that runs it.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic, Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)

### Q7

Taking each action its task calls for, does the AI find the tool it needs allowed, and each tool its task doesn't need withheld by the host, so that the run never stalls on a missing tool and a slip can't reach what lies outside the task?

**Name**

Least privilege, also known as Excessive Agency, OWASP LLM06 and a minimal viable set of tools

**Thinking**

List each action the task takes and the tool that takes it, and allow those tools alone, where the host enforces the list, such as a subagent's tools field. An agent can take a damaging action from a confused or manipulated output whatever the cause, and it can't misuse a tool it doesn't have. Prefer a narrow tool to an open-ended one, such as a tool that writes one file over a shell, as a shell allows every command. Give each tool one purpose that no other overlaps, as a model, like an engineer, can't choose well between two tools that do the same. Know what the host's fields do: some grant, and some restrict, such as Claude Code's allowed-tools on a skill, which only approves tools ahead and withholds none, beside its disallowed-tools, which removes them. Where a tool the task needs also allows an action it must never take, add a guard, as Q8 says.

**Applies**

Every prompt the host runs with tools.

**Excludes**

A prompt that runs with no tools, such as a single call that only answers, has no list to set.

**Cost**

Each tool left off stalls a run that needs it, which only a run shows, so read the evals' records for a tool the host refused.

**Sources**

- [OWASP, LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Anthropic, Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Claude Code, Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Claude Code, Extend Claude with skills](https://code.claude.com/docs/en/skills)

### Q8

For each rule that must hold on every run, such as a file never written or a step never skipped, does something outside the AI hold it, and does a test show it holding both where the AI keeps the rule and where it breaks it, so that what must hold doesn't rest on the AI's attention?

**Name**

Deterministic guardrails, also known as complete mediation and enforcement outside the model

**Thinking**

The AI keeps a rule on most runs, not on every run. A guard outside it runs on every call, such as a host's permission rule, a hook, or the program that calls the model and checks what comes back, so a rule that must hold on every run rests on one, such as a file never written, a command never run, or a step never skipped. A guard holds an order by the call that shows a step done, such as the tests run before anyone writes the code. Test each guard with code in the AI's place, once keeping the rule and once breaking it, as such a test runs in seconds with no model, and a guard never seen to stop a break may stop nothing. Have the guard's message say what to do instead, so that the AI goes on from it. The prompt still says the rule and its reason, as Q3 says.

**Applies**

Each rule whose break harms what lies outside the task or breaks its result, on any run.

**Excludes**

A rule of judgment that no call shows, such as whether a name is clear, has no guard. The evals check it. A rule that holds only in some cases stops the runs outside them, so it stays a rule of the prompt.

**Cost**

Each guard is code to build and test, and a guard on a rule that needn't always hold stops the runs that rightly break it.

**Sources**

- [Claude Code, Automate actions with hooks](https://code.claude.com/docs/en/hooks-guide)
- [OWASP, LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)
- [Anthropic, Building effective agents](https://www.anthropic.com/engineering/building-effective-agents)
- [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)

### Q9

Meeting a choice that isn't its own, such as an action hard to undo, one that others share, or one between ways the caller's intent leaves open, does the AI hand it back, and settle every other choice itself, so that the caller keeps their intent and answers only what the AI can't settle?

**Name**

Human-in-the-loop checkpoints, also known as agentic eagerness and ambiguity and permission handling

**Thinking**

Name the kinds of choice that go back to the caller: an action that destroys something or is hard to undo, one that others see or share, such as a push or a message sent, a change of the task's scope, and input that only the caller has. Say that the AI settles every other choice itself, from the facts it finds, the goal, and what the caller said, and writes what it settled and why, as a model left unsure stops to ask what it could settle, and each needless question costs the caller a round trip. Tie the threshold to the action's risk: low for a tool that deletes or pays, high for one that only reads. At a choice that goes back, the AI asks and ends its turn, rather than ending on a promise.

**Applies**

Every prompt whose AI acts for a caller who can answer.

**Excludes**

A run with no one to answer, such as one that runs unattended, can't hand a choice back. Its prompt says what the AI does instead, such as taking the safe default or stopping with what it found.

**Cost**

Each choice handed back stops the work until the caller answers, and the writer weighs that against the cost of a wrong choice.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [OpenAI, GPT-5 prompting guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [OWASP, LLM06:2025 Excessive Agency](https://genai.owasp.org/llmrisk/llm062025-excessive-agency/)

### Q10

Taking what the AI hands back, can the caller act on it without asking anything further, a program by a fixed form and a person by plain words, with what the AI did and what it didn't, so that the work goes on without a round trip?

**Name**

Structured outputs, also known as an output contract and a handoff by reference

**Thinking**

Name the caller, the person or the program that takes what the AI hands back, and what it does next. List what it needs for that: the result, what the AI did, and what it didn't and why. Choose the form by who reads it. Where a program reads it, give a schema the program checks, such as a host's structured outputs or a tool whose field takes only the allowed values, as a model told the form matches it on most runs and a schema holds it on all. Where a person reads it, write plain words, as Q11 says. Where the result is large, such as code or a report, have the AI write it to a file and hand back the path, as each copy through another AI loses detail and costs its tokens again.

**Applies**

Every prompt, as each hands something back to a caller.

**Excludes**

How a report puts a decision to a person is Q11's. What the report claims is Q12's.

**Cost**

A fixed form changes with each reader that takes it, and the program that reads it changes with it.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [OpenAI, Prompt engineering](https://platform.openai.com/docs/guides/prompt-engineering)
- [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)

### Q11

Where the AI puts a decision, a proposal, or a report to a person, can the person decide from its first lines, and reach the details only where they ask, so that they spend their attention only on what's theirs?

**Name**

Bottom line up front, also known as BLUF and the inverted pyramid

**Thinking**

Have the AI open with what it asks or reports, and why, as a person approves from the conclusion and its grounds and reads further only where these leave them unsure. Then the grounds, in plain sentences, in the words the person uses, with no term of the AI's own. Put one decision to the person in each message, with the one the AI recommends, worded so that yes takes it, as a message that asks several things at once gets several half answers. Keep the details until the person asks, and leave out what wouldn't change what they do next. Short isn't the aim: readable sentences, not fragments, abbreviations, or chains of arrows.

**Applies**

Every prompt whose AI puts a decision, a proposal, or a report to a person.

**Excludes**

What a program reads takes its fixed form, as Q10 says. A person who asks for the whole, such as a full log, gets it.

**Cost**

The AI holds back detail, so a person who wanted it asks once more.

**Sources**

- [Army Regulation 25-50, as Wikipedia's BLUF (communication) sums it up](https://en.wikipedia.org/wiki/BLUF_(communication)), secondary, as the maker read only a summary of it
- [Google, Technical Writing One, Paragraphs](https://developers.google.com/tech-writing/one/paragraphs)
- [Anthropic, Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)

### Q12

Acting on what the AI reports it did or found, does the caller meet each claim backed by a check the AI ran on the real thing, and learn what it left unchecked, so that they act only on what holds?

**Name**

Grounded claims, also known as investigate before answering and outcome verification

**Thinking**

The caller can't tell a claim the AI checked from one it guessed, so have each claim rest on a check the AI ran on the real thing in this run: the file read, the command run, the record opened, never memory, a guess, or another AI's summary. An agent can say it booked a flight while no booking exists, so the claim names the outcome it checked, not the action it took. Judge a check by a result that comes back pass or fail, such as a command's exit code, not by a few lines of its output. Check every item a claim names, not a sample. Have the report say what the AI checked and what it didn't, and why, so that it never reads as covering more than it does. On a long run, have the AI audit each claim against a tool result before it reports, as that nearly ends made-up reports of progress.

**Applies**

Every prompt whose AI reports what it did or found.

**Excludes**

An answer from what the model knows, with nothing in the run to check it on, says so. Ask for grounded claims, not for checks the model makes unasked, as a check written in on top of its own costs tokens and adds nothing.

**Cost**

Each claim waits for its check, and a report says less than the AI believes.

**Sources**

- [Anthropic, Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices)
- [Anthropic, Prompting Claude Fable 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-fable-5)
- [Anthropic, Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)
- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

### Q13

Choosing among many prompts by name and description alone, does the host pick this one for each request it's for and pass it over for a near one it isn't for, and does the body then do what the description promises, so that the prompt runs where it's meant and its caller gets what it promised?

**Name**

Discovery by description, also known as trigger evals and balanced problem sets

**Thinking**

A host chooses among many prompts by their names and descriptions alone, which it holds in context while the bodies stay unread. So the description says what the prompt does and when to use it, in the words a request uses, the main use first, as a host may cut a long description short. Write it in the third person, as the host puts it into its own prompt. Tell the prompt apart from its neighbors, as two that claim the same requests split them by chance. Have the body do what the description promises, all of it and nothing more, so that the caller gets the task the host chose it for. Write requests the prompt is for and near ones it isn't, and try both on the host, as a description tried only on its own requests comes to claim every request near them.

**Applies**

Every prompt a host or a caller chooses by its description, such as a skill or a subagent.

**Excludes**

A prompt that its caller starts by name alone, such as a system prompt a program sends or a brief written for one run, needs no choosing. Its description, where it has one, only names it for its reader.

**Cost**

Trying the choice takes many requests on the host, again whenever a neighbor's description changes.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Claude Code, Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code, Create custom subagents](https://code.claude.com/docs/en/sub-agents)
- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)

### Q14

Reading the prompt once, does the AI meet each instruction in one place, each thing under one term, and no two instructions that pull apart, so that it spends no reasoning on reconciling them and never follows the wrong one?

**Name**

Single source of truth, also known as consistent terminology and no contradictory instructions

**Thinking**

Write each instruction in one place, and call each thing by one term throughout, such as always field and never box or element, as the AI reads two terms as two things and two places as two rules. Check each instruction against each other, the exceptions most, and write an exception where its rule stands. A model that follows instructions closely spends its reasoning on reconciling two that pull apart, rather than picking one, and a prompt freed of them runs better. A sentence that explains why one instruction doesn't cover another marks such a pair: settle it at its source, so that the two say one thing.

**Applies**

Every prompt, and every set of prompts and files a run reads together.

**Excludes**

A short reminder of one rule near the end of a long prompt, where a model's guide advises one, is no second source, as it restates the rule and adds none.

**Cost**

A check of every pair of instructions, again after each change.

**Sources**

- [OpenAI, GPT-5 prompting guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Google, Prompt design strategies](https://ai.google.dev/gemini-api/docs/prompting-strategies)
- [Anthropic, Prompting Claude Opus 5](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/prompting-claude-opus-5)

### Q15

Reading the prompt, does the AI meet only lines that change what it does, with the detail that only some runs need in a file it reads then, so that its attention goes to what counts in its case?

**Name**

Progressive disclosure, also known as context budget and the smallest set of high-signal tokens

**Thinking**

Every line takes some of the AI's attention, and its recall falls as its context grows, so keep only the lines that change what the AI does. Leave out what a capable model already knows. Move what only some runs need to a file the body links, with when to read it, such as for a form only some requests fill, as a file costs nothing until it's read. Link each such file from the body, one level deep, as a model may read only the head of a file that another file links. Give a long reference a list of its contents at its top, such as past 100 lines, so that a partial read still shows what it holds. Keep within the size the host documents, such as a skill's body under 500 lines. Cut a line, run the evals, and put back only what a run then lacked.

**Applies**

Every prompt, and most one a host loads beside many others.

**Excludes**

Minimal isn't short: the facts of Q2 and the reasons of Q3 stay, as a prompt cut below them leaves the AI to guess.

**Cost**

A file read only when needed may go unread when it's needed, so the line that links it says when.

**Sources**

- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
- [Claude Code, Extend Claude with skills](https://code.claude.com/docs/en/skills)

### Q16

Trying a prompt that runs more than once, does the maintainer have tasks drawn from real failures, where a behavior should happen and where it shouldn't, each run graded by code where code can tell and by a judge proven on kept records where it can't, so that a failing eval points at the prompt and not at the eval?

**Name**

Evaluation-driven development, also known as evals first and LLM-as-a-judge calibration

**Thinking**

Write the evals before the prompt. Run the task without the prompt, or without the change, and keep each way it fails, so that the prompt solves real failures, not imagined ones. A few tasks, such as 20 to 50, drawn from real failures are a start. Write each task so that two who know the work would give it the same verdict, and so that an AI that follows the prompt can pass it. Take cases where a behavior should happen and cases where it shouldn't, as an eval of one side makes the prompt do the thing everywhere. Start each run from a clean place, run it as the prompt runs in use, with the parts it works with, as an agent is its harness and its model together, and grade what it made, not the path it took. Grade by code wherever code can tell, such as a test, a file's state, or a tool called. Leave a judge only what code can't, one point to each judge, answered yes or no, with a way to answer that it can't tell. Use a judge, and a stand-in that plays the person with only their intent, only once each has shown it right on kept records whose verdicts someone who knows the work gave. Read the records, not only the scores. Where a run fails, look first at the eval: its task, its graders, and its harness. Change one thing between two runs, and change the prompt only for a cause a record shows.

**Applies**

Every prompt that runs more than once, before its first use and after each change to it or to the model it runs on.

**Excludes**

A brief written for one run, such as a task handed to one subagent, has no suite. Its caller checks the result it hands back against the purpose, as Q12 says.

**Cost**

The evals take more work than the first prompt, and each judge needs its own kept records with known verdicts before it's used.

**Sources**

- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic, Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Prompt engineering overview](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/overview)
- [Anthropic, How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)
- [OpenAI, Prompt engineering](https://platform.openai.com/docs/guides/prompt-engineering)

**Steps**

1. Run the evals before you write or change the prompt, and see the tasks it's for fail. The trace: `{tests}` run.

### Q17

Trying a prompt that runs more than once, on requests held back from its making, of each kind it's for, several times on each model it runs on, does the AI do the task as the one who asked for it means on every run?

**Name**

Held-out evaluation, also known as pass^k and regression evals

**Thinking**

Hold some real requests back from the making, as the writer mends the prompt on the requests they see, and only requests it hasn't met show whether it holds beyond them. Run each with a fresh AI given only the prompt and what a run gives it, several times, on each model the prompt runs on, as a prompt that leads one model well can leave a smaller one short and over-explain to a larger one. Count a task passed only where every run passes, such as by pass^k, where the caller counts on the result each time, and by pass@k only where one success among tries is enough. Read the records of the runs, not only their counts. Trace each shortfall to the goal, a question, or a practice, mend it there, and run again on new requests held back. Keep the tasks that pass as regression evals, run on each change to the prompt or to the model.

**Applies**

Every prompt that runs more than once, before its first use and again after each change to it or to the model it runs on.

**Excludes**

A brief written for one run, such as a task handed to one subagent, has no requests to hold back, as its one run is its use. Its caller checks the result it hands back against the purpose, as Q12 says. A trial shows whether the whole works, not whether each grader judges right, which the kept records of Q16 show.

**Cost**

Requests held back can't shape the prompt, so the writer needs more real requests than they write from, and each trial runs the prompt several times on each model.

**Sources**

- [Anthropic, Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [Anthropic, Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)
- [Anthropic, Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [Anthropic, Define success criteria and build evaluations](https://platform.claude.com/docs/en/test-and-evaluate/develop-tests)
