# Research: prompt

Sources for the best practice of a prompt: a skill or a subagent prompt that gives an AI agent a task to do on its own.
The users are the host that chooses the prompt, the AI that runs it, the caller that gets its result, and the person who keeps their own decisions.
Every quote below was copied from the page at its URL, opened on 2026-11-02.

## The host chooses the right prompt from its description

### The description decides whether a skill is used

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills. Your description must provide enough detail for Claude to determine when to select this Skill, whereas the rest of `SKILL.md` provides the implementation details.

- What it says: the description is a part of its own, and its reader is the host choosing among many prompts.

### The key use case goes first in the description

- Source: Anthropic, "Extend Claude with skills", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/skills.md
- Quote:

  > What the skill does and when to use it. Claude uses this to decide when to apply the skill. If omitted, uses the first non-empty line of the markdown content. Put the key use case first: the combined `description` and `when_to_use` text is truncated at 1,536 characters in the skill listing to reduce context usage.

- What it says: the host may see only the start of the description, so the main use case leads.

### A subagent's description routes the task to it

- Source: Anthropic, "Create custom subagents", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/sub-agents.md
- Quote:

  > **Write descriptions that single out one subagent:** Claude uses the description to decide when to delegate. Make each description specific enough to route to the right subagent, and keep the combined set within the [15,000-token description budget](#understand-automatic-delegation)

- What it says: each description must tell its subagent apart from every other one.

### Watch the name and description in real use

- Source: Barry Zhang, Keith Lazuka and Mahesh Murag (Anthropic), "Equipping agents for the real world with Agent Skills", Anthropic Engineering blog, 2025-10-16.
- URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Quote:

  > Pay special attention to the name and description of your skill. Claude will use these when deciding whether to trigger the skill in response to its current task.

- What it says: whether the prompt triggers is checked by watching the host, not by reading the prompt.

## The AI knows what the task is for and when it is done

### Treat the AI as a capable newcomer without context

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > Think of Claude as a brilliant but new employee who lacks context on your norms and workflows. The more precisely you explain what you want, the better the result.

- What it says: the reader is able but knows nothing of this place, so the prompt states what the writer takes for granted.

### Test the prompt on a colleague

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > **Key test:** Show your prompt to a colleague with minimal context on the task and ask them to follow it. If they’d be confused, Claude will be too.

- What it says: a reader with little context is the test of whether the prompt can be followed.

### Give the reason, so the AI can generalize

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > Providing context or motivation behind your instructions, such as explaining to Claude why such behavior is important, can give Claude more information about your goals and help it deliver more targeted responses.

- What it says: a rule with its reason lets the AI act well in cases the rule does not name; the page adds "Claude can generalize from the explanation."

### State the end goal and what counts as success

- Source: OpenAI, "Reasoning best practices", OpenAI API docs, undated web page.
- URL: https://platform.openai.com/docs/guides/reasoning-best-practices
- Quote:

  > Be very specific about your end goal: In your instructions, try to give very specific parameters for a successful response, and encourage the model to keep reasoning and iterating until it matches your success criteria.

- What it says: the goal part names how the AI knows the result is good enough.

### Give the AI a check that comes back pass or fail

- Source: Anthropic, "Best practices for Claude Code", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/best-practices.md
- Quote:

  > Claude stops when the work looks done. If it has nothing to run that tells it whether the work actually *is* done, "looks done" is all it has to go on.

- What it says: "done" needs a check the AI can run, or the AI stops at "looks done".

### Name the stop conditions and when to hand back

- Source: OpenAI, "GPT-5 prompting guide", OpenAI Cookbook, 2025-08-07.
- URL: https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide
- Quote:

  > Generally, it can be helpful to clearly state the stop conditions of the agentic tasks, outline safe versus unsafe actions, and define when, if ever, it’s acceptable for the model to hand back to the user.

- What it says: the prompt says when the task ends and when control goes back to the user.

### Agents check their progress against the environment

- Source: Erik S. and Barry Zhang (Anthropic), "Building effective agents", Anthropic Engineering blog, 2024-12-19.
- URL: https://www.anthropic.com/engineering/building-effective-agents
- Quote:

  > During execution, it's crucial for the agents to gain “ground truth” from the environment at each step (such as tool call results or code execution) to assess its progress. Agents can then pause for human feedback at checkpoints or when encountering blockers.

- What it says: each step is judged by a real result, and the agent stops for a person at checkpoints and blockers.

## The AI gets what it cannot find on its own, and nothing more

### A subagent starts with nothing of the caller's conversation

- Source: Anthropic, "Create custom subagents", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/sub-agents.md
- Quote:

  > Each subagent starts with a fresh, isolated context window. It doesn't see your conversation history, the skills you've already invoked, or the files Claude has already read.

- What it says: whatever the caller knows and the subagent needs must be in the prompt or the delegation message.

### A subagent does not get the host's system prompt

- Source: Anthropic, "Create custom subagents", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/sub-agents.md
- Quote:

  > The frontmatter defines the subagent's metadata and configuration. The body becomes the system prompt that guides the subagent's behavior. Subagents receive only this system prompt plus basic environment details like the working directory, not the Claude Code system prompt.

- What it says: the body is the whole of the subagent's instructions, so it cannot lean on the host's defaults.

### Write down only what the AI cannot find

- Source: Anthropic, "Best practices for Claude Code", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/best-practices.md
- Quote:

  > Only write down what Claude can't find by reading the repo, or what it would otherwise spend time rediscovering every session.

- What it says: the context part holds decisions and facts that are not in the files; the page gives the test "Could it find this by reading the code?" and "Would it actually go and look?"

### Assume the AI is already very smart

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > Only add context Claude doesn’t already have. Challenge each piece of information:

- What it says: each line must earn its place; the page's questions include "Does this paragraph justify its token cost?"

### Make implicit context explicit, as for a new hire

- Source: Ken Aizawa et al. (Anthropic), "Writing effective tools for agents — with agents", Anthropic Engineering blog, 2025-09-11.
- URL: https://www.anthropic.com/engineering/writing-tools-for-agents
- Quote:

  > When writing tool descriptions and specs, think of how you would describe your tool to a new hire on your team. Consider the context that you might implicitly bring—specialized query formats, definitions of niche terminology, relationships between underlying resources—and make it explicit.

- What it says: the writer's unspoken knowledge, such as terms and formats, has to be written out.

### The smallest set of high-signal tokens

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > Given that LLMs are constrained by a finite attention budget, good context engineering means finding the smallest possible set of high-signal tokens that maximize the likelihood of some desired outcome.

- What it says: every token competes for the AI's attention, so the prompt holds only what moves the result.

### Minimal does not mean short

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > Regardless of how you decide to structure your system prompt, you should be striving for the minimal set of information that fully outlines your expected behavior. (Note that minimal does not necessarily mean short; you still need to give the agent sufficient information up front to ensure it adheres to the desired behavior.)

- What it says: cutting stops where the AI would lack what it needs.

### A delegated task needs an objective, a format, tools and boundaries

- Source: Jeremy Hadfield et al. (Anthropic), "How we built our multi-agent research system", Anthropic Engineering blog, 2025-06-13.
- URL: https://www.anthropic.com/engineering/multi-agent-research-system
- Quote:

  > Each subagent needs an objective, an output format, guidance on the tools and sources to use, and clear task boundaries. Without detailed task descriptions, agents duplicate work, leave gaps, or fail to find necessary information.

- What it says: these four things are the minimum parts of a task handed to a subagent.

### Recall falls as the context grows

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > Studies on needle-in-a-haystack style benchmarking have uncovered the concept of context rot: as the number of tokens in the context window increases, the model’s ability to accurately recall information from that context decreases.

- What it says: a longer prompt makes each of its lines less likely to be recalled.

### Information in the middle of a long input is used worst

- Source: Nelson F. Liu et al., "Lost in the Middle: How Language Models Use Long Contexts", arXiv:2307.03172, TACL 2023.
- URL: https://arxiv.org/abs/2307.03172
- Quote:

  > In particular, we observe that performance is often highest when relevant information occurs at the beginning or end of the input context, and significantly degrades when models must access relevant information in the middle of long contexts, even for explicitly long-context models.

- What it says: where a rule sits in a long prompt changes whether the AI uses it.

### Irrelevant text lowers accuracy

- Source: Freda Shi et al., "Large Language Models Can Be Easily Distracted by Irrelevant Context", arXiv:2302.00093, ICML 2023.
- URL: https://arxiv.org/abs/2302.00093
- Quote:

  > We use this benchmark to measure the distractibility of cutting-edge prompting techniques for large language models, and find that the model performance is dramatically decreased when irrelevant information is included.

- What it says: text the task does not need is not harmless; it pulls the AI off the task.

### Reasoning degrades well below the context limit

- Source: Mosh Levy, Alon Jacoby and Yoav Goldberg, "Same Task, More Tokens: the Impact of Input Length on the Reasoning Performance of Large Language Models", arXiv:2402.14848, ACL 2024.
- URL: https://arxiv.org/abs/2402.14848
- Quote:

  > Our findings show a notable degradation in LLMs' reasoning performance at much shorter input lengths than their technical maximum.

- What it says: fitting in the window is not the test; length itself costs reasoning.

### Many instructions at once are followed less well

- Source: Daniel Jaroslawicz et al., "How Many Instructions Can LLMs Follow at Once?", arXiv:2507.11538, 2025.
- URL: https://arxiv.org/abs/2507.11538
- Quote:

  > We evaluate 20 state-of-the-art models across seven major providers and find that even the best frontier models only achieve 68% accuracy at the max density of 500 instructions. Our analysis reveals model size and reasoning capability to correlate with 3 distinct performance degradation patterns, bias towards earlier instructions, and distinct categories of instruction-following errors.

- What it says: each added rule lowers the chance that every rule is followed, and earlier rules are favoured.

## The AI handles cases the writer did not foresee

### Write at the right altitude

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > The optimal altitude strikes a balance: specific enough to guide behavior effectively, yet flexible enough to provide the model with strong heuristics to guide behavior.

- What it says: the two failures are hardcoded brittle logic and vague guidance that "falsely assumes shared context"; the aim lies between them.

### Match freedom to how fragile the task is

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > **Narrow bridge with cliffs on both sides:** There’s only one safe way forward. Provide specific guardrails and exact instructions (low freedom). Example: database migrations that must run in exact sequence.

- What it says: a fragile step gets exact instructions; the next line gives the "Open field with no hazards" case, where general direction is enough.

### Teach heuristics, not rigid rules

- Source: Jeremy Hadfield et al. (Anthropic), "How we built our multi-agent research system", Anthropic Engineering blog, 2025-06-13.
- URL: https://www.anthropic.com/engineering/multi-agent-research-system
- Quote:

  > Our prompting strategy focuses on instilling good heuristics rather than rigid rules. We studied how skilled humans approach research tasks and encoded these strategies in our prompts

- What it says: a prompt that teaches how an expert judges carries over to cases no rule names.

### Let the model decide where the case is in front of it

- Source: Anthropic, "Best practices for Claude Code", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/best-practices.md
- Quote:

  > Most of the time, you want Claude to decide. Almost every guideline has exceptions, and current models are good at reading the code in front of them and judging whether a guideline fits the situation.

- What it says: a guideline is read as advice the AI may judge inapplicable, so a guideline needs its purpose to be judged by.

### Use canonical examples, not a list of edge cases

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > However, teams will often stuff a laundry list of edge cases into a prompt in an attempt to articulate every possible rule the LLM should follow for a particular task. We do not recommend this. Instead, we recommend working to curate a set of diverse, canonical examples that effectively portray the expected behavior of the agent.

- What it says: a few typical examples show the expected behaviour better than an attempt to list every case.

### Examples are relevant, diverse and marked off

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > **Diverse:** Cover edge cases and vary enough that Claude doesn’t pick up unintended patterns.

- What it says: examples that are too alike teach the AI a pattern the writer did not mean.

### An "always" rule can force a bad action

- Source: Noah MacCallum, Julian Lee et al. (OpenAI), "GPT-4.1 Prompting Guide", OpenAI Cookbook, 2025-04-14.
- URL: https://cookbook.openai.com/examples/gpt4-1_prompting_guide
- Quote:

  > Instructing a model to always follow a specific behavior can occasionally induce adverse effects. For instance, if told “you must call a tool before responding to the user,” models may hallucinate tool inputs or call the tool with null values if they do not have enough information.

- What it says: an unconditional rule needs a way out for the case where it cannot be met.

### Sample phrases get copied word for word

- Source: Noah MacCallum, Julian Lee et al. (OpenAI), "GPT-4.1 Prompting Guide", OpenAI Cookbook, 2025-04-14.
- URL: https://cookbook.openai.com/examples/gpt4-1_prompting_guide
- Quote:

  > When provided sample phrases, models can use those quotes verbatim and start to sound repetitive to users. Ensure you instruct the model to vary them as necessary.

- What it says: an example's wording is taken as the thing to produce unless the prompt says otherwise.

## The AI reads each instruction as meant

### Steps go in a numbered list when order matters

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > Provide instructions as sequential steps using numbered lists or bullet points when the order or completeness of steps matters.

- What it says: the form of the steps part follows from whether order and completeness matter.

### Separate the kinds of content with tags or headers

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > XML tags help Claude parse complex prompts unambiguously, especially when your prompt mixes instructions, context, examples, and variable inputs.

- What it says: instructions, context, examples and inputs each get a marked place.

### Organize the prompt into distinct sections

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > We recommend organizing prompts into distinct sections (like <background_information>, <instructions>, ## Tool guidance, ## Output description, etc) and using techniques like XML tagging or Markdown headers to delineate these sections, although the exact formatting of prompts is likely becoming less important as models become more capable.

- What it says: sections with clear bounds are recommended, while their exact format matters less over time.

### A developer message has identity, instructions, examples and context

- Source: OpenAI, "Prompt engineering", OpenAI API docs, undated web page.
- URL: https://platform.openai.com/docs/guides/prompt-engineering
- Quote:

  > In general, a developer message will contain the following sections, usually in this order (though the exact optimal content and order may vary by which model you are using):

- What it says: OpenAI names the parts Identity, Instructions, Examples and Context, with context "usually best positioned near the end of your prompt".

### Use one term for one thing

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > Consistency helps Claude parse and follow instructions.

- What it says: the page's rule is "Choose one term and use it throughout the Skill", with bad examples such as mixing "extract," "pull," "get," "retrieve".

### Contradictions cost more with careful models

- Source: OpenAI, "GPT-5 prompting guide", OpenAI Cookbook, 2025-08-07.
- URL: https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide
- Quote:

  > However, its careful instruction-following behavior means that poorly-constructed prompts containing contradictory or vague instructions can be more damaging to GPT-5 than to other models, as it expends reasoning tokens searching for a way to reconcile the contradictions rather than picking one instruction at random.

- What it says: two rules that conflict make the AI spend its effort reconciling them.

### With conflicting rules, the later one tends to win

- Source: Noah MacCallum, Julian Lee et al. (OpenAI), "GPT-4.1 Prompting Guide", OpenAI Cookbook, 2025-04-14.
- URL: https://cookbook.openai.com/examples/gpt4-1_prompting_guide
- Quote:

  > Check for conflicting, underspecified, or wrong instructions and examples. If there are conflicting instructions, GPT-4.1 tends to follow the one closer to the end of the prompt.

- What it says: a conflict is resolved by position, not by the writer's intent, so it must be removed.

### Models follow instructions literally

- Source: Noah MacCallum, Julian Lee et al. (OpenAI), "GPT-4.1 Prompting Guide", OpenAI Cookbook, 2025-04-14.
- URL: https://cookbook.openai.com/examples/gpt4-1_prompting_guide
- Quote:

  > GPT-4.1 is trained to follow instructions more closely and more literally than its predecessors, which tended to more liberally infer intent from user and system prompts.

- What it says: the AI does what the words say, so the words must say what is meant.

### Emphasis is no longer needed and causes over-application

- Source: Anthropic, "Best practices for Claude Code", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/best-practices.md
- Quote:

  > Older models sometimes needed the emphasis. Current ones follow a plainly worded line, and piling on emphasis mostly makes Claude over-apply the rule.

- What it says: write rules in plain words; the page adds that a line lost in a long file means "the file needs to be shorter".

### Soften aggressive language

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > The fix is to soften any aggressive language. Where you might have said “CRITICAL: You MUST use this tool when...,” you can use more normal prompting such as “Use this tool when...” instead.

- What it says: "CRITICAL" and "MUST" lead current models to overtrigger.

### Say what to do instead of what not to do

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > **Tell Claude what to do instead of what not to do**

- What it says: the page's example replaces "Do not use markdown" with a description of the prose wanted.

### Give one default, not a menu of options

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > Don’t present multiple approaches unless necessary:

- What it says: the good example names one tool and one exception ("Provide a default" "with escape hatch").

### Small format changes can swing results

- Source: Melanie Sclar, Yejin Choi, Yulia Tsvetkov and Alane Suhr, "Quantifying Language Models' Sensitivity to Spurious Features in Prompt Design or: How I learned to start worrying about prompt formatting", arXiv:2310.11324, ICLR 2024.
- URL: https://arxiv.org/abs/2310.11324
- Quote:

  > We find that several widely used open-source LLMs are extremely sensitive to subtle changes in prompt formatting in few-shot settings, with performance differences of up to 76 accuracy points when evaluated using LLaMA-2-13B.

- What it says: a prompt is judged over several runs and forms, not from one run.

## What must happen every time is enforced outside the prompt

### A prompt is followed nearly always, a hook always

- Source: Anthropic, "Best practices for Claude Code", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/best-practices.md
- Quote:

  > You could've written either of these as a line in `CLAUDE.md` or in your prompt, and Claude would follow it nearly every time. But no matter how strongly you word it, whether Claude follows that line on a given turn is still Claude's call.

- What it says: a rule that allows no exception belongs in a hook, a deny rule or a setting, not in prompt text.

### Limit the tools to enforce constraints

- Source: Anthropic, "Create custom subagents", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/sub-agents.md
- Quote:

  > **Limit tool access:** grant only necessary permissions for security and focus

- What it says: the tools field is how the writer makes some actions impossible, whatever the AI decides.

### A script is more reliable than generated code

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > When writing scripts for Skills, handle error conditions rather than deferring to Claude.

- What it says: a step done by a script should deal with its own errors, so the AI is not left to guess.

### Make mistakes hard to make

- Source: Erik S. and Barry Zhang (Anthropic), "Building effective agents", Anthropic Engineering blog, 2024-12-19.
- URL: https://www.anthropic.com/engineering/building-effective-agents
- Quote:

  > Poka-yoke your tools. Change the arguments so that it is harder to make mistakes.

- What it says: the page's example changed a tool to require absolute paths, after which "the model used this method flawlessly".

## The caller gets back what it asked for, in a form it can use

### Be specific about format and constraints

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > Be specific about the output format and constraints you want.

- What it says: the output part names the form the caller will use.

### Only the summary returns to the caller

- Source: Anthropic, "Create custom subagents", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/sub-agents.md
- Quote:

  > By delegating these to a subagent, the verbose output stays in the subagent's context while only the relevant summary returns to your main conversation.

- What it says: the caller sees only what the subagent hands back, so the hand-back must hold everything the caller needs.

### A subagent returns a condensed, distilled summary

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > Each subagent might explore extensively, using tens of thousands of tokens or more, but returns only a condensed, distilled summary of its work (often 1,000-2,000 tokens).

- What it says: the output is a short result, not the record of the work.

### A forked skill needs a task, not only guidelines

- Source: Anthropic, "Extend Claude with skills", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/skills.md
- Quote:

  > `context: fork` only makes sense for skills with explicit instructions. If your skill contains guidelines like "use these API conventions" without a task, the subagent receives the guidelines but no actionable prompt, and returns without meaningful output.

- What it says: a prompt run on its own must state a task and its result, or nothing useful comes back.

## The user keeps the decisions that are theirs

### Ask before hard-to-reverse actions

- Source: Anthropic, "Prompting best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/build-with-claude/prompt-engineering/claude-prompting-best-practices.md
- Quote:

  > Consider the reversibility and potential impact of your actions. You are encouraged to take local, reversible actions like editing files or running tests, but for actions that are hard to reverse, affect shared systems, or could be destructive, ask the user before proceeding.

- What it says: the prompt marks which actions the AI takes alone and which wait for the user.

### Set a lower threshold for asking on risky actions

- Source: OpenAI, "GPT-5 prompting guide", OpenAI Cookbook, 2025-08-07.
- URL: https://cookbook.openai.com/examples/gpt-5/gpt-5_prompting_guide
- Quote:

  > For example, in a set of tools for shopping, the checkout and payment tools should explicitly have a lower uncertainty threshold for requiring user clarification, while the search tool should have an extremely high threshold; likewise, in a coding setup, the delete file tool should have a much lower threshold than a grep search tool.

- What it says: how readily the AI asks the user depends on what the action can break.

## The prompt loads only what a run needs

### Progressive disclosure is the core design principle

- Source: Barry Zhang, Keith Lazuka and Mahesh Murag (Anthropic), "Equipping agents for the real world with Agent Skills", Anthropic Engineering blog, 2025-10-16.
- URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Quote:

  > Progressive disclosure is the core design principle that makes Agent Skills flexible and scalable. Like a well-organized manual that starts with a table of contents, then specific chapters, and finally a detailed appendix, skills let Claude load information only as needed:

- What it says: the description, the body and the reference files are three levels, each read only when needed.

### Every line of a loaded skill is a recurring cost

- Source: Anthropic, "Extend Claude with skills", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/skills.md
- Quote:

  > Keep the body itself concise. Once a skill loads, its content [stays in context across turns](#skill-content-lifecycle), so every line is a recurring token cost. State what to do rather than narrating how or why, and apply the same conciseness test you would for [CLAUDE.md content](https://code.claude.com/docs/en/best-practices.md#keep-claude-md-short).

- What it says: the body states what to do; detail moves to supporting files. This sits in tension with the advice above to give reasons, so a reason stays only where the AI's judgment needs it.

### Keep SKILL.md under 500 lines

- Source: Anthropic, "Extend Claude with skills", Claude Code Docs, undated web page.
- URL: https://code.claude.com/docs/en/skills.md
- Quote:

  > Keep `SKILL.md` under 500 lines. Move detailed reference material to separate files.

- What it says: the body has a size limit, and reference material lives beside it.

### Keep references one level deep

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > **Keep references one level deep from `SKILL.md`**. All reference files should link directly from `SKILL.md` to ensure Claude reads complete files when needed.

- What it says: a chain of references risks the AI reading only part of what it needs.

## How a prompt is made: test it with a fresh agent and iterate

### Build evaluations before writing much

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > **Create evaluations BEFORE writing extensive documentation.** This ensures your Skill solves real problems rather than documenting imagined ones.

- What it says: the steps are to run without the skill, record failures, build three scenarios, measure a baseline, then "Write minimal instructions".

### One agent writes the skill, a fresh one tests it

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > Work with one instance of Claude (“Claude A”) to create a Skill that is used by other instances (“Claude B”). Claude A helps you design and refine instructions, whereas Claude B tests them in real tasks.

- What it says: the tester must not share the writer's context, so it meets the prompt as its real reader does.

### Start from observed gaps

- Source: Barry Zhang, Keith Lazuka and Mahesh Murag (Anthropic), "Equipping agents for the real world with Agent Skills", Anthropic Engineering blog, 2025-10-16.
- URL: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
- Quote:

  > Start with evaluation: Identify specific gaps in your agents’ capabilities by running them on representative tasks and observing where they struggle or require additional context. Then build skills incrementally to address these shortcomings.

- What it says: the prompt's content comes from where the agent actually failed.

### Start minimal and add from failure modes

- Source: Prithvi Rajasekaran et al. (Anthropic), "Effective context engineering for AI agents", Anthropic Engineering blog, 2025-09-29.
- URL: https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- Quote:

  > It’s best to start by testing a minimal prompt with the best model available to see how it performs on your task, and then add clear instructions and examples to improve performance based on failure modes found during initial testing.

- What it says: each line added answers a failure seen in a test.

### Watch the agent work, step by step

- Source: Jeremy Hadfield et al. (Anthropic), "How we built our multi-agent research system", Anthropic Engineering blog, 2025-06-13.
- URL: https://www.anthropic.com/engineering/multi-agent-research-system
- Quote:

  > Think like your agents. To iterate on prompts, you must understand their effects. To help us do this, we built simulations using our Console with the exact prompts and tools from our system, then watched agents work step-by-step.

- What it says: the failures they found were agents going on after enough results, verbose queries and wrong tools.

### Read the transcripts, not only the agent's own account

- Source: Ken Aizawa et al. (Anthropic), "Writing effective tools for agents — with agents", Anthropic Engineering blog, 2025-09-11.
- URL: https://www.anthropic.com/engineering/writing-tools-for-agents
- Quote:

  > However, keep in mind that what agents omit in their feedback and responses can often be more important than what they include. LLMs don’t always say what they mean.

- What it says: the tester reads what the agent did, because its report can leave out what went wrong.

### Hold out test cases to avoid overfitting

- Source: Ken Aizawa et al. (Anthropic), "Writing effective tools for agents — with agents", Anthropic Engineering blog, 2025-09-11.
- URL: https://www.anthropic.com/engineering/writing-tools-for-agents
- Quote:

  > We relied on held-out test sets to ensure we did not overfit to our “training” evaluations.

- What it says: a prompt tuned on the same cases it is tested on may fail in cases the writer did not foresee.

### Test with every model the prompt will run on

- Source: Anthropic, "Skill authoring best practices", Claude Platform Docs, undated web page.
- URL: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices.md
- Quote:

  > What works perfectly for Opus might need more detail for Haiku. If you plan to use your Skill across multiple models, aim for instructions that work well with all of them.

- What it says: the reader is the model that runs the prompt, so the test uses that model.

## Not found

- Anthropic "Prompting best practices" and "Skill authoring best practices" pages show no publication date, so these entries say "undated web page".
- OpenAI "A practical guide to building agents" (PDF): I did not look for it in this run.
- A study of how well a host chooses a skill or subagent from its description: I did not find one.
- The Agent Skills open standard specification: I did not open it in this run.
