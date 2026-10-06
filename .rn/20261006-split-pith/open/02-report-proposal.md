# Report: the Plan sign-off proposal, taken up as the user

Read and used: the proposal (`open/01-notes-proposal.md`), the plan it proposes (`steering.md`), the
viewpoints (`rn/0.9.0/references/essentials/conductor.md` § Proposal) and the report form (`report.md`).
To check the proposal's Goods and facts at their places I also read `.claude/rules/plugin.md` § 2
Check, `rn/references/conduct.md:100-110`, `writ/skills/up/SKILL.md:54-58`, `writ/README.md` (grep for
`writ:pith`), `rn/.claude-plugin/plugin.json`, the file lists of `rn/agents/` and
`rn/references/essentials/`, and ran `gh pr view 40` (title, state, draft, files only) and
`gh issue view 35` / `37` (title, state only).
Not looked at: commit messages, diffs, the PR's conversation, earlier reports, the design or
verification documents named in the front matter.

## Deciding as the user whether the work has come close enough, what did you learn of how far it now gives each thing you would choose it for, and of what came closer since the last proposal?

From the work I understood this: nothing is built; both attractive qualities are "planned only;
nothing is built yet (first proposal)" (`01-notes-proposal.md:35-37`), so there is no earlier proposal
to have come closer than. What I am choosing at this sign-off is the plan itself: the Goal and A1/A2
(`01-notes-proposal.md:12-24`, matching `steering.md:14-31`). The proposal also told me the one thing
that could stop A2: whether a plugin can call a dependency's skill and start its agents is unknown,
and the design starts by trying it on a throwaway pair of plugins (`01-notes-proposal.md:7-10, 49-50`;
`steering.md:53-54`). So from the proposal I learned how far the plan is from being usable (all of it)
and where its main risk sits, which is what a plan sign-off can show.

## Deciding yes or no as the user, what beyond the proposal did you need?

From the work I understood this, at four places:

1. "Taken away: `/writ:pith`, replaced by `/pith:up` (M3)" (`01-notes-proposal.md:39`). To see what
   I give up I had to read M3 (`steering.md:39`): "Whoever calls `/writ:pith` today finds the same
   check as `/pith:up`, installed with writ." I could read M3 two ways: `/writ:pith` stays and gives
   the same check as `/pith:up`, or `/writ:pith` is gone and the caller finds `/pith:up` installed
   alongside writ. The proposal settles it as removal; M3's wording alone does not. `writ/README.md`
   today tells users to call `/writ:pith` (lines 124, 131, 154, 176, 191).
2. The More on A1/A2's wording (`01-notes-proposal.md:47-48`) says their gains are "worded by me from
   our conversation, not in your own words". The proposal's copy of A2 (`01-notes-proposal.md:23-24`)
   leaves out the parenthetical in `steering.md:30-31`, which says part of A2 *is* the user's words
   ("pith is the most basic function of an AI agent, and rn moves onto it in this session") and only
   the gain is in the conductor's words. I needed the steering file to see which part of A2 I am being
   asked to confirm. For A1 the steering file carries no such note, so I could not tell from the work
   where A1's wording came from.
3. The plan leaves six points open (`steering.md:79-88`); the proposal's "Next" names three of them
   (`01-notes-proposal.md:7-8`). The other three, whether rn depends on pith directly or through
   writ, whether a version range or a bare name is declared, and how writ's and rn's designs point to
   pith's, appear only in `steering.md:85-88`.
4. The Rules (`steering.md:64-66`: releases wait for an instruction; files moved with `git mv`) and
   the Assumptions' facts (`steering.md:47-52, 55-60`) are not in the proposal. I did not need them to
   say yes, but approving the plan approves them, and the proposal does not say so.

Otherwise the proposal gave me the action (`/rn:ty` or `/rn:gm <feedback>`, line 2), what happens
next and why (lines 7-10), and the criteria in full (lines 12-33).

## Using the work where each Good was found, what happened that differs from the Good?

Doing as written, this happened, for each Good:

- Good goal, `steering.md:14-20`: the lines hold the Goal, including both reasons (two copies grow
  apart, line 17-18; checking without a writing plugin, lines 19-20). Nothing differs.
- Good A1, `steering.md:26-28`: the lines hold A1 as quoted. `writ/README.md:176` ("There are no
  essentials for code or tests. To check them, first write essentials with `/writ:pith`") shows the
  "first writing the viewpoints" part reflects today's behaviour. Nothing differs.
- Good A2, `steering.md:29-30`: A2 runs to line 31; the cited span cuts off the end of its
  parenthetical. The content matches. `rn/.claude-plugin/plugin.json:8-10` (depends on `writ`) and
  `rn/agents/first-user.md`, `rn/references/essentials/` exist as `steering.md:55-59` says, and
  `rn/references/conduct.md:107` and `writ/skills/up/SKILL.md:56` say what the Assumption cites them
  for (rn hands documents to `writ:up`; writ:up calls pith).
- Good "What this session also does", #37 closed, `steering.md:67-70`: the Rule is there.
  `.claude/rules/plugin.md:113-121` says not to have a first user recheck a must-be fix and to have a
  new first user recheck each fixed attractive-quality More, and line 144 says "Check by script,
  every time, whatever a script can decide." `gh issue view 37` printed "writ: one /writ:up call runs
  pith about three times, one only to write the result file | OPEN", matching the proposal's
  description. What the Rule does not show is how it removes the third run in practice; the plan
  states it as a rule, and the mechanism is left to the design.

Also checked: line 2's "read it on the PR": `gh pr view 40` printed a draft, open PR titled "Make
pith the one place to check work: split it out of writ, with writ and rn on it (#35)" whose files are
`steering.md` and `01-notes-proposal.md`. `gh issue view 35` printed "Split pith out of writ into a
plugin of its own | OPEN".

## Deciding yes or no as the user, which parts of the proposal did you use and which did you read past?

From the work I understood this:

- Used: the status line and its two commands (line 2), "Next" (lines 7-10), "Toward what you would
  choose it for" (lines 35-37), "Taken away" (line 39), both Mores (lines 47-50), and the A1/A2 text
  (lines 20-24), which the first More asks me to confirm.
- Read past: the Goal paragraph (lines 12-18) after the first sentence, since the Good on it
  (line 42) told me it was read as meant; M1-M5 (lines 25-33), which hold no choice at a plan
  sign-off beyond M3, reached through "Taken away"; the three Goods (lines 42, 45-46, 53-54), which I
  checked at their places only for this report; the Draft PR link (line 5).
- The header line and "#2 Design sign-off" (lines 1, 3) I glanced at for where I am.

## Conductor

- Good goal: nothing built and the main risk (calling a dependency's skill) are learned from the proposal alone, at 01-notes-proposal.md:7-10,49-50
- Good A1, A2: every Good holds at its place, at steering.md:14-31,67-70
- More M3: reads two ways (/writ:pith stays, or is removed), at steering.md:39
- More A1, A2: the More on wording does not say which part is the user's; A2's note is dropped from the proposal's copy, at 01-notes-proposal.md:23-24,47-48
- More goal: "Next" names three of the six open points, at 01-notes-proposal.md:7-8
- More goal: the Rules and Assumptions approved with the plan are not in the proposal, at 01-notes-proposal.md
- More A2: the cited span stops one line short, at 01-notes-proposal.md:46
