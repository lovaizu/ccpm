# First user's report: the Plan sign-off proposal

Viewpoints answered: the "Proposal" section of
`/Users/kiyo/.claude/plugins/cache/ccpm/rn/0.9.0/references/essentials/conductor.md`.

What I read and used: the proposal (`open/01-notes-proposal.md`, all 63 lines), the plan it proposes
(`steering.md`, all 93 lines), and, to check the plan's cited places, `rn/references/conduct.md:105-109`,
`writ/skills/up/SKILL.md:52-58`, `rn/.claude-plugin/plugin.json`, the listings of `rn/agents`,
`rn/references/essentials` and `writ/skills`, and the headings of `.claude/rules/plugin.md`. I ran
`gh pr view 40` and `gh issue view` for #33, #35, #37 and #44 (read only).

What I did not look at: commit messages, earlier versions of the proposal or plan, the PR conversation,
earlier reports, and the official Claude Code docs behind the two "Fact, official docs" assumptions
(`steering.md:48-53`). I changed nothing in the repository but this file.

## Deciding as the user whether the work has come close enough, what did you learn of how far it now gives each thing you would choose it for, and of what came closer since the last proposal?

From the work I understood this:

- How far each attractive criterion is given: `01-notes-proposal.md:38-39` says for both A1 and A2
  "planned only; nothing is built yet". So nothing is usable yet; what is on the table is the plan.
- What the plan promises for each: A1 (pith alone gives `/pith:up`, checking any work, writing
  viewpoints first for a kind that has none) at `:20-22`, and A2 (one change in pith reaches writ and
  rn) at `:23-25`.
- How sure A2 is: the two Mores at `:55-59` tell me A2 rests on two things not yet known (a plugin
  calling a dependency's skill and agents; pith returning before the caller goes on from the main
  conversation), and `:7-9` says the design starts by trying both on throwaway plugins. I learned
  nothing about what happens to the plan or to A2 if either try fails; neither the proposal nor
  `steering.md` says.
- How the A1/A2 wording came about: `:52-54` says the gains are not in my own words (A1 from issue
  #35 plus writing viewpoints first; A2 the conductor's wording of what was agreed), and that approving
  approves them as written.
- What came closer since the last proposal: `:38-39` says "(the same)" for both. This is the first
  sign-off (`:2`, "#1 Plan sign-off"), and the proposal does not say what the last proposal was or what
  changed in the plan since it, so I learned only that A1 and A2 did not move.
- The must-be criteria M1-M5 (`:26-35`) get no line on how far they are given; only M3 shows up again,
  as what is taken away (`:41`).

## Deciding yes or no as the user, what beyond the proposal did you need?

Doing as written, this happened:

- `:2` told me to read it on the PR; `gh pr view 40` showed a draft PR whose files are exactly
  `steering.md` and this proposal. The move itself (`/rn:ty` or `/rn:gm <feedback>`) and the next step
  (`:7-10`) I took from the proposal alone.
- The six open points: `:10` gives only their count and a pointer. To know whether I am fine leaving
  them to the design, I read `steering.md:84-92` (six items, counted).
- The Rule I approve: `:43-44` says "every check through pith follows the plugin rules on checking".
  What that means (a first user only for the first use and for each fixed attractive More; the result
  file's form checked by script) I found only at `steering.md:72-75`. `:62-63` hints at it through #37.
- A scope limit the proposal does not state: `steering.md:58-59` says rn's own generator and writ
  agents stay outside pith and #44 stays rn's own for them, so this session does not fix #44 for them.
  Nothing in the proposal says so; `:58-59` of the proposal cites #44 only as evidence.
- Issue numbers: the proposal names #35, #37, #44 with a short gloss for #37 (`:62`) and #44 (`:59`,
  "agents ... ran in the background"); I ran `gh issue view 44` to see the title ("rn: agents run in
  the background though started without run_in_background, so the conductor cannot wait for them") and
  that it is open. The gloss matched.
- What happens if either try at `:7-9` fails: I looked for it in `steering.md` and did not find it.

## Using the work where each Good was found, what happened that differs from the Good?

Doing as written, this happened, for each Good at its place:

- Good A2, "the reason (two copies growing apart; checking without writ) is read as meant, at
  steering.md:14-20": `steering.md:17-20` says the skeleton lives in writ and again in rn, "the two
  grow apart", and "anyone can check any work by use without installing a plugin for writing
  documents". It reads as the Good says. I also checked the "lives ... again inside rn" part:
  `rn/agents/first-user.md` and `rn/references/essentials/` exist beside `writ/skills/pith`. Nothing
  differed.
- Good A1, "checking any work without installing writ, at steering.md:26-28": the lines say
  "Installing pith alone, without writ, gives `/pith:up`, which checks any work". Nothing differed.
- Good A2, "one change to checking reaches both writ and rn, at steering.md:29-31": the lines say "a
  change to how work is checked is made in pith once and reaches both". Nothing differed.
- Good A2, "issue #37 ... is closed by applying the plugin rules to every check through pith, at
  steering.md:72-75": the lines say so and cite `.claude/rules/plugin.md` § Check, which exists as
  "## 2. Check" at `.claude/rules/plugin.md:105`, with "Check by script, every time, whatever a script
  can decide" at `:143` and "After an attractive-quality More is fixed, have a new first user check
  that point again" at `:119`. `gh issue view 37` shows it open, titled "one /writ:up call runs pith
  about three times, one only to write the result file", which matches the proposal's gloss. Nothing
  differed. What I could not see from the plan is how many first users a `/writ:up` call will start
  after the change; the Rule bounds it but does not give a number.

The places cited by the Mores also hold: `steering.md:54-55` and `:56-59` are the two Assumptions as
quoted. The plan's repository facts at `steering.md:60-64` held: `rn/references/conduct.md:107` is
"Start a fresh agent ... that runs the `writ:up` skill", `writ/skills/up/SKILL.md:56` begins "Then call
pith with the Skill tool", and `rn/.claude-plugin/plugin.json` lists `"dependencies": ["writ"]` with
version 0.9.0.

## Deciding yes or no as the user, which parts of the proposal did you use and which did you read past?

From the work I understood this:

- Used: `:1-2` (where I am and how to answer), `:5` (the PR), `:7-10` (what happens after yes),
  `:20-25` (only to know what A1 and A2 mean when reading `:38-39`), `:38-39` (how far each is given),
  `:41` (what I lose), `:43-44` (what else yes approves), `:52-59` (the three Mores: the wording
  question and the two unknowns A2 rests on), `:62-63` (#37 closed in this session).
- Read past: `:12-18` (the Goal, the same text as `steering.md:14-20`, which I read on the PR anyway),
  `:26-35` (M1-M5, which no other line of the proposal refers to except M3 at `:41`), and `:46-50`
  (the three Goods saying the plan states A1 and A2 at given lines; they told me nothing that changed
  my yes or no, though I checked them for the question above).

## Conductor

- Good A2: the two unknowns A2 rests on, and that the design tries them first, are learned from the proposal alone, at 01-notes-proposal.md:7-9,55-59
- Good A1, A2: every Good holds at its place, at steering.md:14-31,72-75
- More A2: "(the same)" does not say against what, or what changed in the plan, at 01-notes-proposal.md:38-39
- More A2: what happens if either try fails is not said, at 01-notes-proposal.md:7-9
- More A2: that #44 stays open for rn's generator and writ agents is not said, at 01-notes-proposal.md:58-59
- More goal: the Rule approved is named, not stated, at 01-notes-proposal.md:43-44
- More goal: the six open points are only counted, at 01-notes-proposal.md:10
- More M1: M1-M5 get no line on how far they are given, at 01-notes-proposal.md:26-35
