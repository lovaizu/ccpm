# Report: plan, attractive criteria A1 and A2

## What I read and used

- The plan, `.rn/20261006-split-pith/steering.md` (all 83 lines), which is also what the user agreed.
  Used: "# Goal" (lines 12-19), "## Attractive quality" (lines 23-30), "# Not yet specified"
  (lines 72-83), and the fourth Assumption (lines 54-58) for what rn uses today.
- The viewpoint file `rn/0.9.0/references/essentials/plan.md`, lines 1-26: its preamble and the two
  questions I was asked to answer. Its other questions I did not answer.
- Issue #35, which the Goal names (`steering.md:14`), read with
  `gh issue view 35 --repo lovaizu/ccpm --json title,body,comments,author`. It printed the body and
  no comments; its author is `kiyobot`, the same login as this repository's git user. Nothing in the
  plan says whether its text is the user's own words.
- Not looked at: the repository's code (writ, rn, pith), the commit history, the pull request, and
  any earlier report.

## Reading the attractive criteria beside the reason the user wants the goal, what of that reason do they leave out?

From the work I understood this. The reason the plan gives (`steering.md:15-19`) has three parts:

1. Today the same skeleton lives twice, in writ as pith and again inside rn, "and the two grow
   apart".
2. "with one home, an improvement to how work is checked is made once and reaches both".
3. "anyone can check any work by use without installing a plugin for writing documents".

Laid beside A1 and A2 (`steering.md:25-30`):

- Part 2 is A2 nearly word for word: "a change to how work is checked is made in pith once and
  reaches both" (`steering.md:28-29`).
- Part 3 is A1: "Installing pith alone, without writ, gives `/pith:up`, which checks any work"
  (`steering.md:25-26`).
- Part 1, the two copies growing apart, appears in neither A1 nor A2 as a gain. A2 says a future
  change reaches both. It does not say that the check writ gives and the check rn gives become the
  same one. A2's words "check their work through pith" can be read that way. The plan says nothing
  about how the two copies that have already grown apart are joined, or which one's behaviour is
  kept. The parts that make the end state "one home" are in M4 (`steering.md:39`), a must-be
  criterion, and in "Not yet specified" (`steering.md:76-77`: "Which of rn's parts move to pith, and
  which stay rn's own (such as its viewpoints for a plan, a design, and a task result)"). If rn's
  viewpoints for a plan, a design and a task result stay rn's own, part of what rn checks by stays
  outside pith. Neither A2 nor the Goal says whether that still counts as "the one place".
- The "anyone" in part 3 is met in A1 by a person installing pith. The issue the Goal names says
  more: "rn can call pith to check its work without depending on writ" (issue #35, Desired State).
  This is not in the plan's stated reason or in A1/A2. The plan lists it as open: "Whether rn
  depends on pith directly or through writ" (`steering.md:80`). Under A1 and A2 as written, rn
  reaching pith only through writ would satisfy both.

## Reading each attractive criterion beside what the user said, which of what it says they gain did the user not say?

From the work I understood this.

A2 (`steering.md:28-30`): the gain it states is "a change to how work is checked is made in pith once
and reaches both". The plan records the user's words as "pith is the most basic function of an AI
agent, and rn moves onto it in this session". It says the gain itself "is put in the conductor's
words, agreed in conversation". By the plan's own record, the user did not say this gain. The plan
records only that the user agreed to it. The user's recorded words name a standing ("the most basic
function of an AI agent") and a timing ("in this session", also in the Assumptions at
`steering.md:59`). They name no gain.

A1 (`steering.md:25-27`): the plan records no words from the user for A1, either in the criterion or
elsewhere in the plan. A1 states these gains:

- (a) pith installed alone, without writ, gives `/pith:up`;
- (b) it checks any work, "a document, a prompt, code, tests";
- (c) it writes the result file;
- (d) it first writes the viewpoints for a kind of work that has none, "such as code or tests".

Issue #35 (named at `steering.md:15`) has text for (a): "installing it does not install writ". It
has text for (b): "pith checks prompts, code and tests as well as documents". For (d), its nearest
words are that pith "also writes essentials files worked back from a purpose". That describes what
pith does today, and it is not a gain stated for the split. The issue does not say "first writing
the viewpoints for a kind of work that has none, such as code or tests". Nothing in the issue speaks
to (c) as a gain. The issue's author is `kiyobot`, and the plan does not record the issue's text as
the user's words. So from the plan alone, none of A1's four gains is shown to be something the user
said. Weighed against the issue, (c) and (d) as worded in A1 are not in it.

Neither A1 nor A2 says only what must not happen. Both state a gain.

## Conductor

- Good A2: carries "an improvement is made once and reaches both" nearly word for word, at steering.md:28-29
- Good A1: carries "anyone can check any work without installing writ", at steering.md:25-26
- More A2: whether rn's own viewpoints staying in rn still counts as "the one place" is not said, at steering.md:15-19
- More A1: "writes the result file" is a means, not a gain, at steering.md:26
- More A1, A2: their gains are not the user's own words, at steering.md:25-30
- More goal: issue #35's "rn can call pith without depending on writ" is in neither the reason nor A1/A2, at steering.md:80
