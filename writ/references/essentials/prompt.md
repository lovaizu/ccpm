# Prompt

The reader is the AI that acts by following the prompt. When it finishes, it can choose for itself a way of acting that achieves the purpose, even in situations the writer did not foresee.

- Can the AI grasp who it acts as, what it is for, and what it does?

    Give the role, then the purpose, then the steps, each under its own heading. The purpose and the steps tell the role what to do, so a role given after them leaves the first orders with no one to carry them out. For the role, write who it reads as, what it decides itself, and what it does not decide but returns to the requester. In the purpose, write the benefit to the product's user and why it is needed, never a summary of the steps. For a role that works for another role, the purpose names the benefit that reaches the product's user through its work, not the handoff to the requester; a role whose purpose ends at the handoff asks only for what the requester can check, not for what the product's user needs. Knowing the benefit, the AI can choose what fits it even in situations the steps do not cover; a purpose that summarises the steps sends the AI back to following them where they do not reach.

- Can the AI follow each step as written without breaking what the product promises its user, and choose everything else itself from the purpose and role?

    Put in the steps only rules that break things when they drift and cannot be derived from the purpose and role, such as the format of a handoff. If the step were removed and the AI, from its role and purpose, would still act rightly, it is not a step. The design's flow of work goes into the role and purpose, so the AI judges each move from them; copied as numbered steps, it is followed in order even where it should not be. Steps are followed exactly as written, so they miss the mark in situations other than the ones expected, and a step phrased as a habit, such as "confirm with the user", overrides the purpose where the two disagree. Write the rules used at each step in that step. A situation that needs other rules, such as fixing rather than first writing, gets its own step, because rules buried in another step's order are not followed there. Where the AI is told to read another document, write only the path and why to read it, without a summary.

- Can a maintainer tell, for each part of a prompt and each mechanism it relies on, which feature in the design it serves?

    Trace each part, and each mechanism such as agent definitions, hooks or a subagent launch, to a feature in the design. What traces to nothing is either left out, or the design is changed first. A means chosen while implementing, with no ground in the design, is kept by habit with no reason anyone can check.

- Can the checking role check as a reader, without being pulled along by the producing role's reasons?

    The producing role and the checking role read the same essentials. The producing role reads them as the shape to aim for, and the checking role reads them as questions. Do not pass the checking role the producing role's reasons for what it did. The checking role answers every question in the essentials with Good, More or both, and returns the answers to the requester. Return Good and More with equal weight. A Good is what serves the purpose, with what the reader gains from it, which a fix must not take away. A More is a shortfall, with what the reader struggles with because of it; how to fix it is the requester's to decide. Attach evidence to both, such as path:line or a command that was run and its output. When a Good says only "easy to understand", whoever fixes it does not know what to keep, and breaks even what is working.

- Is everything one role leaves for another read by a step of that other role, and everything a role reads written by someone?

    A role told that another will see its output stops dealing with it, and when no step of the other role reads that output, it falls through. Likewise, a step that reads something no one writes has nothing to work from.

- Is each role kept from what it must not see?

    Keep from each role what it must not see by what it is handed. What it could still fetch for itself, such as git history, the discussion or earlier versions, the prompt names as not to fetch, with why. The tools a role needs to do its work also reach these, so tools cannot close the boundary; only what the role is handed and what the prompt names can. Knowing why, the role also passes up routes to the same thing that the prompt did not name.

- Does the checking role spend its judgment where only it can judge?

    The checking role judges mainly whether the reader of the work gets the benefit they would choose the work for over what they would use instead. What the reader takes for granted and a script can decide, such as a format holding, nothing being lost or a link resolving, goes to tests or scripts. They are faster and give the same answer every time, and a checking role that spends its attention on them has less left for the judgment only it can make. What the reader takes for granted but no script can decide, such as whether a claim is true, stays with the checking role.

- Can the requester decide its next move itself by weighing the check's results against the purpose, and always bring the cycle of evaluating and fixing to an end?

    The checking role decides neither whether to fix nor what to do next. Acting on the check's results literally means redoing even the parts that serve the purpose. Have a role that did not produce the work evaluate only once. When evaluation runs many times, non-essential remarks keep coming and never settle. After that, the requester weighs each returned More against the purpose one by one and decides whether to fix it, let it go, or hand it to a person, and has the producing role fix the ones to fix. It also doubts each returned Good one by one, and sorts any whose evidence does not hold as a More. The requester judges the fixed result against the reader and purpose, because the only thing a role that did not produce the work can do that others cannot is read without knowing the discussion. Because judgment sits in one place, the cycle always comes out as either "settled" or "cannot proceed". It cannot proceed if any of these happens: the same More keeps coming back, each fix brings a new More, or a fix requires changing the agreed document. The cost is that fixes after the evaluation are not seen by a role that did not produce the work. This is accepted, because handing the person the final Good and More with evidence lets the person check them and, if needed, ask for another evaluation.

- When the AI asks a person something, can the person answer each question with ease, without being asked what is already known?

    Ask one question at a time, and do not ask what an earlier answer already tells. Ask only what the conversation, the documents handed over and the repository do not tell. Asked several at once, the person answers even questions an earlier answer made unnecessary, and loses the chance for one answer to change the next question.

- When a person is asked for a review, can they decide whether to approve or request fixes without rereading the whole text?

    Once the cycle has ended, check the final Good and More for each question. If a More remains that must be fixed to achieve the purpose, and the purpose alone does not tell how to fix it, or if the cycle cannot proceed, do not send it for review. Go back to the stage where things are decided by talking with the person, and make that More the first topic. Otherwise, attach to the review request the final Good and More for each question, with the location in the actual work and the evidence. Each question is put as it is, so the person can tell which question each Good and More answers and that every question was answered. Do not attach remarks or fixes from along the way. The person looks at the final form, so the final Good and More let them state their judgment flatly without rereading the whole text.

- Can the producing role and the checking role, with few questions, catch whole groups of errors that matter to the purpose?

    Do not make the questions a list of prohibitions; make each question catch together the errors that arise from the same cause. Also write them so they can be checked from the state of the finished work, not from whether the steps were followed. When non-essential questions creep in, the producing role's aim drifts, there is more to read, and either fixing never ends or the person's burden grows. If the checking role's answers are shallow, the questions are either too many or too vague, so refine the questions instead of adding roles.

- When the essentials are refined, can every role that uses them read the same essentials right away?

    In other documents, write only that the essentials file exists and who uses it and how; do not copy its content. Copies drift each time the essentials are refined.

- Can the AI take every sentence it reads, as written, as something to do?

    Explanations of things that do not exist, how decisions came about, and rules that concern only the task at hand are not things to do.
