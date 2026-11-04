# prompt

## Goal

Given the prompt for a request it is made for, an AI agent does the task as the prompt's writer means, with only what its run gives it, on every run and in cases the writer did not foresee.

## Parts

- **description**: What the host reads to choose the prompt for a request: a name that says what the prompt does, and a description of what it does and the requests it is used for.
- **tools**: The tools the AI may use, listed where the host reads them and refuses any other, when the host allows such a list.
- **goal**: What the AI reads first in the body: what it is to achieve, for whom, how it knows it is done, and what lies outside its task.
- **context**: What the AI needs and cannot find or know on its own: the situation, its inputs and where they are, and the rules of this place.
- **steps**: The steps in the order the AI takes them, each step the result that holds when it ends, with the rules the step needs, each with its reason, or the script that does it and how to run it.
- **output**: What the AI hands back, in what form, and to whom.
- **trials**: The trials that try the prompt: one case for each class of input and each rule of its steps, where the AI must act and where it must not; the set-up of each case, the stand-ins for the person and for the prompt's neighbours, the judges, and the checks made on each run's record.

## Benefits

- **Q1** (goal): When the AI believes it has finished, can it tell from the prompt whether it has reached what the task is for?
- **Q2** (goal): When the AI meets a choice that is the user's, such as one between options that serve equally or an action hard to undo, does it hand the choice to the user rather than make it?
- **Q3** (context): Given the prompt and only what its run gives it, can the AI do each step without guessing a fact, such as where its inputs are or a rule of the place it works in?
- **Q4** (goal, steps): Taking the steps in order, does the AI arrive at what the goal says the task is for, with no step that leads it elsewhere?
- **Q5** (steps): When the AI meets a case a step's rule does not name, can it decide the case as the writer would, from the reason the rule gives?
- **Q6** (steps): When the AI is run twice on the same input, does each step whose result must not vary, such as a check or a file's form, give the same result both times?
- **Q7** (tools, steps): Can the AI take every action its steps call for with the tools it is allowed?
- **Q8** (tools): When the AI, during a run, reaches for an action that lies outside its task, does the host refuse it?
- **Q9** (steps, output): When the caller, the person or the AI that started the prompt, takes what the AI hands back, can it act on it without asking the AI anything further?
- **Q10** (description): When a request the prompt is made for comes, and a request near it that it is not made for, does the host, such as Claude Code, choose the prompt for the first and pass it over for the second, from the name and the description alone?
- **Q11** (description, goal): Once the host has chosen the prompt by its description, does the AI do the task the description says, all of it and nothing more?
- **Q12** (the whole): When the prompt is run several times on each kind of request it is made for, does the AI reach the result the prompt names on every run?
- **Q13** (the whole): Does every line of the prompt change what the AI does toward the task, so that none draws its attention from the lines that do?
- **Q14** (trials, steps): For each rule of the steps, where the AI must act and where it must not, can the maintainer point to the trial case that tries it, and see from that case's record that the situation it tries arose?
- **Q15** (trials): When a trial fails, can the maintainer tell from its record that the prompt went wrong and not the trial: its set-up, a stand-in, a judge or a check?
- **Q16** (trials, steps): When the maintainer takes out of the prompt what a trial case tries, does that case fail?
- **Q17** (output): When the AI puts a decision, a proposal or a report to the person, can the person approve or decide from its first lines alone, and reach the details only where they ask?

## Practices

### Q1: When the AI believes it has finished, can it tell from the prompt whether it has reached what the task is for?

**Thinking**: The AI stops when its work looks done, so the prompt says what the result is for and gives a check that tells done from looking done.

**Steps**

1. For each thing that holds once the task is met, give the check that shows it: a command to run where one exists, or else what to look up and where.
2. Write when the AI stops: once every check passes, or at a blocker it cannot pass, which it hands back with what it found.

**Grounds**

- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "Claude stops when the work looks done. If it has nothing to run that tells it whether the work actually is done, "looks done" is all it has to go on."
- [Reasoning best practices](https://platform.openai.com/docs/guides/reasoning-best-practices), OpenAI, OpenAI API docs, no date: "Be very specific about your end goal"
- [GPT-5 prompting guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide), OpenAI, OpenAI Cookbook, 2025: "Generally, it can be helpful to clearly state the stop conditions of the agentic tasks, outline safe versus unsafe actions, and define when, if ever, it’s acceptable for the model to hand back to the user."
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Erik S. and Zhang, anthropic.com/engineering, 2024: "During execution, it's crucial for the agents to gain “ground truth” from the environment at each step (such as tool call results or code execution) to assess its progress."

### Q2: When the AI meets a choice that is the user's, such as one between options that serve equally or an action hard to undo, does it hand the choice to the user rather than make it?

**Thinking**: A choice is the user's where the AI has no ground to pick one option over another, or where it is hard to undo, so the prompt names those choices and how the AI asks, and leaves every other choice to the AI.

**Steps**

1. Among the choices the task meets, mark each action that is hard to undo, touches what others share, or destroys something.

**Grounds**

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "for actions that are hard to reverse, affect shared systems, or could be destructive, ask the user before proceeding."
- [GPT-5 prompting guide](https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide), OpenAI, OpenAI Cookbook, 2025: "the checkout and payment tools should explicitly have a lower uncertainty threshold for requiring user clarification, while the search tool should have an extremely high threshold"
- [Building effective agents](https://www.anthropic.com/engineering/building-effective-agents), Erik S. and Zhang, anthropic.com/engineering, 2024: "Agents can then pause for human feedback at checkpoints or when encountering blockers."

### Q3: Given the prompt and only what its run gives it, can the AI do each step without guessing a fact, such as where its inputs are or a rule of the place it works in?

**Thinking**: The AI is able but new to this place, and sees nothing of the conversation that started it, so the prompt gives what it cannot find or know, and where the rest lies.

**Steps**

1. For each step, list the facts it needs: its inputs and where they lie, the terms it uses, the rules of the place, and what the writer knows without saying.
2. Give the prompt to a fresh AI with only what a run gives it, see where it guesses, and add the fact it lacked.

**Grounds**

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Think of Claude as a brilliant but new employee who lacks context on your norms and workflows."
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Key test: Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they’d be confused, Claude will be too."
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "Only write down what Claude can't find by reading the repo, or what it would otherwise spend time rediscovering every session."
- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents), Aizawa, anthropic.com/engineering, 2025: "Consider the context that you might implicitly bring—specialized query formats, definitions of niche terminology, relationships between underlying resources—and make it explicit."
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read."
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "Subagents receive only this system prompt plus basic environment details like the working directory, not the Claude Code system prompt."

### Q4: Taking the steps in order, does the AI arrive at what the goal says the task is for, with no step that leads it elsewhere?

**Thinking**: Each step is a result on the way to the goal, so the AI chooses how to reach it and knows when to go on.

**Steps**

1. Write the steps in the order their results must hold, so the AI sees that order, such as in a numbered list.
2. Check that a later step or the goal uses each step's result, and cut a step whose result nothing uses.
3. Check that the last step leaves what the goal says the task is for.

**Grounds**

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Provide instructions as sequential steps using numbered lists or bullet points when the order or completeness of steps matters."
- [Extend Claude with skills](https://code.claude.com/docs/en/skills), Anthropic, Claude Code Docs, no date: "If your skill contains guidelines like "use these API conventions" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output."

### Q5: When the AI meets a case a step's rule does not name, can it decide the case as the writer would, from the reason the rule gives?

**Thinking**: A rule that says what it is for lets the AI apply it where it was meant and judge a case no rule names, so each rule carries its reason.

**Steps**

1. Write the rule as what to do, in plain words, with no capitals or warnings for emphasis.
2. Where a rule says always or never, say what the AI does when the rule cannot be met.
3. In place of a list of edge cases, give the way of judging and a few typical examples that differ from one another.
4. Think of a case the rule does not name, read only the rule and its reason, and check that they lead where the writer would go; where they do not, mend the reason.

**Grounds**

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can give Claude more information about your goals and help it deliver more targeted responses."
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Claude can generalize from the explanation."
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "Most of the time, you want Claude to decide. Almost every guideline has exceptions, and current models are good at reading the code in front of them and judging whether a guideline fits the situation."
- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Tell Claude what to do instead of what not to do"
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "Older models sometimes needed the emphasis. Current ones follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule."
- [GPT-4.1 Prompting Guide](https://cookbook.openai.com/examples/gpt4-1_prompting_guide), MacCallum, Lee et al., OpenAI Cookbook, 2025: "Instructing a model to always follow a specific behavior can occasionally induce adverse effects."
- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), Hadfield et al., anthropic.com/engineering, 2025: "Our prompting strategy focuses on instilling good heuristics rather than rigid rules."
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Rajasekaran et al., anthropic.com/engineering, 2025: "Instead, we recommend working to curate a set of diverse, canonical examples that effectively portray the expected behavior of the agent."

### Q6: When the AI is run twice on the same input, does each step whose result must not vary, such as a check or a file's form, give the same result both times?

**Thinking**: The AI's judgment varies from run to run, which suits a step with many good ways, so a step with one right result is done by a program that gives it every run and handles its own errors, which the AI runs.

**Steps**

1. Run the prompt twice on one input, and compare what those steps gave.

**Grounds**

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Narrow bridge with cliffs on both sides: There’s only one safe way forward. Provide specific guardrails and exact instructions (low freedom)."
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Are more reliable than generated code"
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "When writing scripts for Skills, handle error conditions rather than deferring to Claude."
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "If something has to happen every time, make it a hook, a deny rule, or a managed setting."

### Q7: Can the AI take every action its steps call for with the tools it is allowed?

**Thinking**: Each action a step calls for needs a tool the AI is allowed, or the step cannot be taken however well it is written.

**Steps**

1. For each step, list each action it takes and the tool that takes it, a script's command among them.
2. Check each tool against those the prompt allows, and add the tool or change the step.
3. Run the prompt, and read the record of the run for a tool call the host refused.

**Grounds**

- [How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system), Hadfield et al., anthropic.com/engineering, 2025: "Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries."

### Q8: When the AI, during a run, reaches for an action that lies outside its task, does the host refuse it?

**Thinking**: A rule in words holds only while the AI follows it, so an action that must never happen is made one the host refuses.

**Steps**

1. List the actions the task must never take, such as writing where it only reads.
2. Allow only the tools Q7's list needs.
3. Where a tool it needs also allows an action it must never take, add a rule the host enforces, such as a deny rule or a hook.
4. Run the prompt on a request that tempts such an action, and check in the record that the host refused it.

**Grounds**

- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "Limit tool access: grant only necessary permissions for security and focus"
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "Enforce constraints by limiting which tools a subagent can use"
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "But no matter how strongly you word it, whether Claude follows that line on a given turn is still Claude's call."
- [Best practices for Claude Code](https://code.claude.com/docs/en/best-practices), Anthropic, Claude Code Docs, no date: "If something has to happen every time, make it a hook, a deny rule, or a managed setting."

### Q9: When the caller, the person or the AI that started the prompt, takes what the AI hands back, can it act on it without asking the AI anything further?

**Thinking**: The caller sees only what comes back, so the prompt says what that is, in what form and to whom, and a step makes each of it.

**Steps**

1. Name the caller, and what it does next with the result.
2. List what it needs for that: the result, what was done, and what was not done and why.
3. Choose the form by who reads it: a fixed form, such as JSON, where a script reads it, and short plain words where a person does.
4. Check that a step makes each thing the output names.
5. Hand the output alone to someone in the caller's place, and see whether they can act without asking.

**Grounds**

- [Prompting best practices](https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices), Anthropic, Claude Platform Docs, no date: "Be specific about the output format and constraints you want."
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "the verbose output stays in the subagent's context while only the relevant summary returns to your main conversation."
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Rajasekaran et al., anthropic.com/engineering, 2025: "returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens)."

### Q10: When a request the prompt is made for comes, and a request near it that it is not made for, does the host, such as Claude Code, choose the prompt for the first and pass it over for the second, from the name and the description alone?

**Thinking**: The host reads the name and the description alone, among many, to pick a prompt for a request, so they say what the prompt does and when it is used, in the words users ask in, and tell it apart from the others.

**Steps**

1. Write down several requests the prompt is made for, in a user's own words, and several near ones it is not made for.
2. Write the description: what the prompt does, then the requests and situations it is used for, the main use first.
3. Give each request written down to a fresh session with the prompt installed, see which prompt the host chooses, and mend the description where it chooses wrongly.

**Grounds**

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills."
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Include both what the Skill does and specific triggers/contexts for when to use it."
- [Extend Claude with skills](https://code.claude.com/docs/en/skills), Anthropic, Claude Code Docs, no date: "Put the key use case first"
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "Claude uses each subagent's description to decide when to delegate tasks."
- [Create custom subagents](https://code.claude.com/docs/en/sub-agents), Anthropic, Claude Code Docs, no date: "Make each description specific enough to route to the right subagent"
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), Zhang, Lazuka and Murag, anthropic.com/engineering, 2025: "Pay special attention to the name and description of your skill. Claude will use these when deciding whether to trigger the skill in response to its current task."

### Q11: Once the host has chosen the prompt by its description, does the AI do the task the description says, all of it and nothing more?

**Thinking**: The description and the body say one task, so what the host chose the prompt for is what the AI does.

**Steps**

1. Set what the description says the prompt does against what the goal and the steps have the AI do, and for each thing in one and not the other, add it to the body or take it out of the description.

**Grounds**

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Your description must provide enough detail for Claude to determine when to select this Skill, whereas the rest of `SKILL.md` provides the implementation details."

### Q12: When the prompt is run several times on each kind of request it is made for, does the AI reach the result the prompt names on every run?

**Thinking**: A prompt is known by what a fresh AI does with it, so it is run on real requests of each kind, several times, and judged from the record of what the AI did.

**Steps**

1. Gather requests of each kind the prompt is made for, and hold some back from its making.
2. Run each with a fresh AI that has only the prompt and what a run gives it, several times, on the model the prompt will run on.
3. Mend the prompt only for a cause seen in a record.
4. Run the requests held back last, to see whether the prompt holds beyond the ones it was mended on.

**Grounds**

- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Create evaluations BEFORE writing extensive documentation. This ensures your Skill solves real problems rather than documenting imagined ones."
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Claude A helps you design and refine instructions, whereas Claude B tests them in real tasks."
- [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), Zhang, Lazuka and Murag, anthropic.com/engineering, 2025: "Identify specific gaps in your agents’ capabilities by running them on representative tasks and observing where they struggle or require additional context."
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Rajasekaran et al., anthropic.com/engineering, 2025: "It’s best to start by testing a minimal prompt with the best model available to see how it performs on your task, and then add clear instructions and examples to improve performance based on failure modes found during initial testing."
- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents), Aizawa, anthropic.com/engineering, 2025: "what agents omit in their feedback and responses can often be more important than what they include. LLMs don’t always say what they mean."
- [Writing effective tools for agents — with agents](https://www.anthropic.com/engineering/writing-tools-for-agents), Aizawa, anthropic.com/engineering, 2025: "We relied on held-out test sets to ensure we did not overfit to our “training” evaluations."
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "What works perfectly for Opus might need more detail for Haiku."
- [Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting](https://arxiv.org/abs/2310.11324), Sclar, Choi, Tsvetkov and Suhr, arXiv:2310.11324, 2023: "with performance differences of up to 76 accuracy points when evaluated using LLaMA-2-13B"

### Q13: Does every line of the prompt change what the AI does toward the task, so that none draws its attention from the lines that do?

**Thinking**: Every line takes some of the AI's attention, so the prompt keeps only the lines that change what it does, and keeps detail it needs only sometimes where the AI reads it only then.

**Steps**

1. Move detail needed only in some runs out of the prompt to where the AI reads it only when it needs it, such as a file the prompt links directly, and say when to read it.
2. Run Q12's trials again after cutting, and put back what a run then lacked.

**Grounds**

- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Rajasekaran et al., anthropic.com/engineering, 2025: "good context engineering means finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome."
- [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents), Rajasekaran et al., anthropic.com/engineering, 2025: "Note that minimal does not necessarily mean short; you still need to give the agent sufficient information up front to ensure it adheres to the desired behavior."
- [Large Language Models Can Be Easily Distracted by Irrelevant Context](https://arxiv.org/abs/2302.00093), Shi et al., arXiv:2302.00093, 2023: "find that the model performance is dramatically decreased when irrelevant information is included."
- [How Many Instructions Can LLMs Follow at Once?](https://arxiv.org/abs/2507.11538), Jaroslawicz et al., arXiv:2507.11538, 2025: "even the best frontier models only achieve 68% accuracy at the max density of 500 instructions."
- [Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models](https://arxiv.org/abs/2402.14848), Levy, Jacoby and Goldberg, arXiv:2402.14848, 2024: "Our findings show a notable degradation in LLMs' reasoning performance at much shorter input lengths than their technical maximum."
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Only add context Claude doesn’t already have."
- [Extend Claude with skills](https://code.claude.com/docs/en/skills), Anthropic, Claude Code Docs, no date: "so every line is a recurring token cost."
- [Skill authoring best practices](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices), Anthropic, Claude Platform Docs, no date: "Keep references one level deep from `SKILL.md`. All reference files should link directly from `SKILL.md` to ensure Claude reads complete files when needed."

### Q14: For each rule of the steps, where the AI must act and where it must not, can the maintainer point to the trial case that tries it, and see from that case's record that the situation it tries arose?

**Thinking**: A trial is drawn from the prompt's steps as a unit test is drawn from a contract, one case for each class and each rule, on both sides of it; and a case counts only where its run met the situation it tries, as an AI may take another good path past it.

**Steps**

1. List each rule of the steps and each class of input it treats alike, and for each, a case where the AI must act and a case where it must not.
2. Set up each case so that the AI cannot pass the situation by, such as by giving the fact it must find only where a search finds it, and write a check on the run's record that the situation arose.
3. Write the cases one at a time: run the new case, read its record whole, and write the next only once the situation arose and the verdict is right.

**Grounds**

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Grace, Hadfield, Olivares and De Jonghe, Anthropic Engineering, 2026: "Test both the cases where a behavior should occur and where it shouldn't."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Grace, Hadfield, Olivares and De Jonghe, Anthropic Engineering, 2026: "Read the transcripts!"
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Grace, Hadfield, Olivares and De Jonghe, Anthropic Engineering, 2026: "it's useful to create a reference solution: a known working output that passes all graders."
- [Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd), Beck, newsletter.kentbeck.com, 2023: "Write a list of the test scenarios you want to cover"
- [Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd), Beck, newsletter.kentbeck.com, 2023: "Turn exactly one item on the list into an actual, concrete, runnable test"

### Q15: When a trial fails, can the maintainer tell from its record that the prompt went wrong and not the trial: its set-up, a stand-in, a judge or a check?

**Thinking**: A trial's own parts, the set-up, the stand-ins, the judges and the checks, are code and prompts of their own, so each is built test first and seen right on a record kept from an earlier run before a whole run trusts it; a whole run then only confirms, and a failure tells of the prompt.

**Steps**

1. Decide by code every point the record decides, such as a tool called, a file's content or a command's output, and leave to a judge only what code cannot decide.
2. Give each judge one point, its definitions and a pass or fail; give it messages whose answer is known, of each kind, and use it only once it judges them right.
3. Give the stand-in for the person only their intent, which the prompt never sees, and the whole of each message it answers; check on kept conversations that it answers from the intent alone and makes nothing up.
4. Build each part alone and run it small on a kept record before any whole run.
5. Change one thing between two runs, the prompt or a part of the trial, never both; where a trial fails, look in its record first at the trial's own parts, and mend the prompt only for a cause in the prompt.

**Grounds**

- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Grace, Hadfield, Olivares and De Jonghe, Anthropic Engineering, 2026: "We recommend choosing deterministic graders where possible, LLM graders where necessary or for additional flexibility"
- [AI Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/), Husain and Shankar, hamel.dev, 2026: "First check whether you can test the condition with code assertions"
- [AI Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/), Husain and Shankar, hamel.dev, 2026: "Binary evaluations force clearer thinking and more consistent labeling"
- [AI Evals: Everything You Need to Know](https://hamel.dev/blog/posts/evals-faq/), Husain and Shankar, hamel.dev, 2026: "For an evaluator that makes judgments, test it against human-labeled examples of the failure you want to detect."
- [𝜏^2-Bench: Evaluating Conversational Agents in a Dual-Control Environment](https://arxiv.org/html/2506.07982), Barres, Dong, Ray, Si and Narasimhan, arXiv:2506.07982, 2025: "Never make up or hallucinate information not provided in the scenario instructions."
- [Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents), Grace, Hadfield, Olivares and De Jonghe, Anthropic Engineering, 2026: "When scores don't climb, we need confidence that it's due to agent performance and not the eval."

### Q16: When the maintainer takes out of the prompt what a trial case tries, does that case fail?

**Thinking**: A trial that passes whatever the prompt says tries nothing, so each case is seen to fail before the prompt holds what it tries, as a test is before its code.

**Steps**

1. Run each new case before writing into the prompt what it tries, and see it fail.
2. Write that into the prompt, and run the case until it passes.

**Grounds**

- [Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd), Beck, newsletter.kentbeck.com, 2023: "Turn exactly one item on the list into an actual, concrete, runnable test"
- [Canon TDD](https://newsletter.kentbeck.com/p/canon-tdd), Beck, newsletter.kentbeck.com, 2023: "Change the code to make the test (& all previous tests) pass (adding items to the list as you discover them)"

### Q17: When the AI puts a decision, a proposal or a report to the person, can the person approve or decide from its first lines alone, and reach the details only where they ask?

**Thinking**: The person approves from the conclusion and its grounds, and reads further only where these leave them unsure, so a message opens with what it asks or reports and why, in plain sentences, and keeps the rest for when it is asked.

**Steps**

1. Write a few plain sentences with no headings or labels, in short paragraphs, one point each: the context and the conclusion; the grounds; the purpose and what it should be.
2. Put what the person is to decide alone on the last line, one decision a message, with one recommendation.
3. Where the person asks for more, add what it is now, with the place it rests on, and the gap between that and what it should be.
4. Use the words the person uses, and say a term of your own in everyday words or leave it out.

**Grounds**

- [AR 25-50, Preparing and Managing Correspondence](https://armypubs.army.mil/epubs/DR_pubs/DR_a/ARN42124-AR_25-50-007-WEB-13.pdf), US Army, armypubs.army.mil, 2020, change 007 of 2024: "Two essential requirements include putting the main point at the beginning of the correspondence (bottom line up front) and using the active voice"
- [Clear and short](https://digital.gov/guides/plain-language/writing/clear-short), GSA, digital.gov, no date: "Limit each paragraph or section to one topic."
- [Headings](https://digital.gov/guides/plain-language/design/headings), GSA, digital.gov, no date: "With rare exceptions, headings should be shorter than the content that follows them."
- [Preparing Decision Memorandums, Policy 670.1](https://dbh.dc.gov/sites/default/files/dc/sites/dmh/publication/attachments/TL62.pdf), DC Department of Mental Health, dbh.dc.gov, 2005: "After reviewing this section, the DMH Director can decide which detailed sections must be reviewed in order to make a decision."
- [Preparing Decision Memorandums, Policy 670.1](https://dbh.dc.gov/sites/default/files/dc/sites/dmh/publication/attachments/TL62.pdf), DC Department of Mental Health, dbh.dc.gov, 2005: "The author should clearly recommend one of the options presented in the previous section"
- [Progressive Disclosure](https://www.nngroup.com/articles/progressive-disclosure/), Nielsen, Nielsen Norman Group, 2006: "Initially, show users only a few of the most important options. Offer a larger set of specialized options upon request."
- [Structuring forms](https://www.gov.uk/service-manual/design/form-structure), Government Digital Service, GOV.UK Service Manual, 2018: "one decision they have to make"
