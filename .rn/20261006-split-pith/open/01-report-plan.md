# Report: the plan (`.rn/20261006-split-pith/steering.md`) by `plan.md`

## What I read and used, and what I did not look at

Read and used:

- The plan: `.rn/20261006-split-pith/steering.md`, all 72 lines.
- The viewpoint file: `rn/0.9.0/references/essentials/plan.md`, and `report.md` for the form of this report.
- To check the plan's facts at their sources: `rn/.claude-plugin/plugin.json`, `writ/.claude-plugin/plugin.json`,
  `.claude-plugin/marketplace.json`, root `README.md`, `.claude/rules/plugin.md`, `.github/workflows/tests.yml`,
  `.coveragerc`, `rn/agents/first-user.md`, `rn/references/conduct.md`, `rn/references/steering.md`,
  `rn/references/essentials/` (listing), `writ/agents/first-user.md`, `writ/skills/pith/SKILL.md`,
  `writ/skills/pith/result-form.md`, `writ/skills/up/SKILL.md` (lines that name pith), `writ/docs/design.md`
  lines 1-30, `writ/README.md` (lines naming `/writ:pith`), the hook files that name agent types
  (`writ/hooks/checks/*.py`, `rn/hooks/*.py`), the file listings of `writ/`, `rn/`, `dev/`.
- Issue #35 (`gh issue view 35`), since the plan says "split out of writ into a plugin of its own (issue #35)".
- Official docs: `https://code.claude.com/docs/en/plugins-reference` and
  `https://code.claude.com/docs/en/plugins/dependencies`.

Not looked at: commit messages and diffs, the pull request (#40) and its conversation, any earlier report,
`rn/docs/design.md`, `rn/docs/verification.md`, `writ/docs/design.md` past line 30, the tests and trials
themselves. I ran nothing that changes the repository.

I had no record of the user's own words apart from `steering.md` itself (it is also what I was given as "what
the user agreed"), and issue #35, whose author is `kiyobot`, the same name as this repository's git user.

## Reading the plan once, what did you take as the reason the user wants the goal?

From the work I understood this. The reason is at `steering.md:15-19`: the same skeleton ("a first user who
does not know how the work was made, viewpoint files, Good and More against the aim") exists twice, in writ as
pith and inside rn, "and the two grow apart"; with one home, "an improvement to how work is checked is made
once and reaches both", and "anyone can check any work by use without installing a plugin for writing
documents". I took two reasons: (1) stop the two copies drifting, so a check improvement is made once; (2) let
anyone check work by use without installing writ.

## Reading the attractive criteria beside the reason the user wants the goal, what of that reason do they leave out?

From the work I understood this. A1 (`steering.md:25-26`) carries reason (2): installing pith alone gives
`/pith:up` that checks any work. A2 (`steering.md:27-28`) carries reason (1) in nearly the goal's words: "a
change to how work is checked is made in pith once and reaches both". The part "the two grow apart" (that
today they diverge) appears as a criterion only in M3 (`steering.md:36`, "No copy of pith's parts remains in
writ or rn"), a must-be criterion. I found no part of the reason at `steering.md:14-19` that neither A1 nor A2
speaks of.

Beside the reason, one point from issue #35 is in neither the goal nor the criteria: its Desired State says
"rn can call pith to check its work without depending on writ" (issue #35, Desired State, third bullet). The
plan says rn checks "through" pith (A2) but says nothing about whether rn still depends on writ; rn today
does (`rn/.claude-plugin/plugin.json`, `"dependencies": ["writ"]`).

## Reading each attractive criterion beside what the user said, which of what it says they gain did the user not say?

I stopped part way. The only record of what the user said is `steering.md` itself and issue #35; the plan does
not mark which words are the user's. Setting the criteria beside issue #35:

- A1: issue #35 says "pith is its own plugin ... called as `/pith:up`, and installing it does not install
  writ" and "pith checks prompts, code and tests as well as documents". A1's gain matches those words. "and
  writes the result file" is not a gain the issue states as one, though the issue describes the result file.
- A2: issue #35 says writ "uses pith to check documents through a plugin dependency" and "rn can call pith to
  check its work". The gain "a change to how work is checked is made in pith once and reaches both" is not in
  issue #35; it is in the plan's Goal (`steering.md:17-18`), which I cannot tell apart as the user's words or
  the conductor's.

## Checking each fact the plan rests on at its source, which did not hold?

Doing as written, this happened, fact by fact (`steering.md:43-51`, plus the Goal's statement of today's state).

- `steering.md:43-45`, dependencies. At `plugins-reference`, "dependencies": "Bare names resolve against this
  plugin's own marketplace" — holds. At `plugins/dependencies`: "installing it installs every dependency" —
  holds. "pick the highest `<plugin>--v<version>` tag in the range": the docs say "The dependency installs at
  the highest git tag that satisfies this range" for an entry with a `version` field; for a bare string, "your
  plugin depends on whatever version that plugin's marketplace provides". So tags are used only when a range is
  declared, which the plan's sentence does not say. "with no matching tag, the marketplace's current copy is
  used": the docs say this holds for a "Plugin referenced by a relative path", while a "Plugin with its own
  repository" fails with `has no git tag satisfying`. This marketplace uses relative paths (`"source": "./rn"`,
  `"./writ"` in `.claude-plugin/marketplace.json`), so it holds here.
- `steering.md:46-48`, the Assumption. "the official docs give no path variable for a dependency's directory":
  holds; `plugins-reference` lists only `${CLAUDE_PLUGIN_ROOT}`, `${CLAUDE_PLUGIN_DATA}`, `${CLAUDE_PROJECT_DIR}`,
  and says they are not in the Bash tool's environment. "do not document calling another plugin's skill or
  agent": did not fully hold. `plugins/dependencies` opens: "A plugin dependency is another plugin that your
  plugin relies on, such as one whose MCP server or skill it calls." `plugins-reference` documents that
  components are namespaced ("an agent `reviewer` in plugin `deploy-tools` appears as `deploy-tools:reviewer`").
  Neither page shows how the call is made.
- `steering.md:49-50`, rn 0.9.0. `grep -rn pith rn` printed nothing — "does not call pith" holds as written.
  `rn/agents/first-user.md` and `rn/references/essentials/` (conductor, deliverable, design, plan, report,
  task-result) exist; `rn/.claude-plugin/plugin.json` has `"dependencies": ["writ"]` — both hold. Beside it:
  `rn/references/conduct.md:107-108` has each document written by an agent "that runs the `writ:up` skill", and
  `writ/skills/up/SKILL.md:56` says "Then call pith with the Skill tool". So rn's README, design and
  verification documents are already checked by pith, through writ; the plan's fact does not say this.
  `writ/docs/design.md:3` says "rn does not call writ or pith anywhere in this repository yet", which does not
  match `rn/references/conduct.md:107`.
- `steering.md:51`, decided by the user: not checkable from the repository.
- `steering.md:15-16`, the skeleton lives twice: holds. `writ/agents/first-user.md` and `rn/agents/first-user.md`
  both exist; the result forms differ (`writ/skills/pith/result-form.md` vs `rn/references/steering.md:97-108`).
- `steering.md:37-39`, M4's rule: `.claude/rules/plugin.md` holds each item named; CI fails on any unrun line
  (`.coveragerc`: `fail_under = 100`; `.github/workflows/tests.yml` runs `dev/*/tests`).
- Front matter `steering.md:7-9`: `pith/README.md`, `pith/docs/design.md`, `pith/docs/verification.md` do not
  exist yet (`ls pith`: "No such file or directory"); the plan names them as where the documents will be.

## Acting on the plan, which fact you relied on can neither the repository nor any documentation show, yet is recorded neither as told by the user nor as an Assumption?

From the work I understood this. Acting on M1 and M2 (`steering.md:32-35`), I relied on what users of writ 0.1.0
and rn 0.9.0 have where they run them, which neither the repository nor the docs show:

- Users who call `/writ:pith` directly. `writ/README.md:124`, `:131`, `:154`, `:191` tell users to call
  `/writ:pith`. Whether anyone does, and what they meet when it moves to `/pith:up`, is not recorded. M1 names
  only `/writ:up`'s golden paths.
- Result files and rn sessions already in users' repositories (`.writ/open/...`, `.rn/.../open/...`) in today's
  forms. `rn/references/steering.md:4-5` says "every later version of `rn` goes on from these alone". Whether
  such files exist where the product runs and must still be read is not recorded.

## Reading the criteria, which kind of input they speak of, such as "a user with no name", has forms where the product runs that neither the repository shows nor the user told, or was tried today on only some of its forms?

From the work I understood this. A1 (`steering.md:25-26`) speaks of "any work (a document, a prompt, code,
tests)". Today the check has viewpoints only for documents, prompts and essentials files
(`writ/references/essentials/`: doc, readme, design, prompt, essentials); for code or tests
`writ/skills/pith/SKILL.md:28` says "return saying one must be made first", and `writ/README.md:176` says "There
are no essentials for code or tests". The trials in `dev/writ/trials/fixture/` hold a prompt, docs, JS code and
diffs. A2 speaks of the work rn checks: plan, design, task result, deliverable (`rn/references/conduct.md:167-171`),
whose forms depend on each user's product; the plan does not say which of these forms pith must check.

## Acting on the plan, which point you relied on is a decision only the user can make, yet is not recorded as theirs?

From the work I understood this. The plan records four open points under Not yet specified (`steering.md:66-72`).
Acting on it, I also relied on these, which are not recorded as decided by the user nor listed as open:

- Whether `/writ:pith` goes away, stays as a way into pith, or is kept for a while (`writ/README.md:124`).
- Whether rn keeps depending on writ once it checks through pith (issue #35 asks "without depending on writ";
  the plan is silent; rn uses `writ:up` for documents, `rn/references/conduct.md:107`).
- Whether writ and rn declare a version range on pith (issue #35: "resolved against `pith--v<version>` tags") or
  a bare name, which per the docs tracks the marketplace's current copy; and, with the Rule at `steering.md:55-56`
  that release waits for an instruction, whether a first `pith--v...` tag exists before writ depends on it.
- Whether pith's "Make an essentials file" (`writ/skills/pith/SKILL.md:66`) is part of `/pith:up`; A1 names only
  checking.

## Following the tasks in order, which acceptance criterion did no task bring to hold?

Not asked: the only tasks are `#1: Plan sign-off` and `#2: Design sign-off` (`steering.md:61-62`); the tasks that
make the deliverable are not planned yet (`plan.md:6-7`).

## Reading a task's Completion criteria as its generator, what of the task's purpose toward the attractive criteria do they leave out?

Not asked, for the same reason (`steering.md:61-62`).

## Following the tasks in order, which work on must-be quality comes before the attractive criteria are nearly met?

Not asked, for the same reason (`steering.md:61-62`).

## Carrying the work on from the plan, which parts did you use and which did you pass over?

From the work I understood this.

- Used: the Goal (`:14-19`), every criterion (`:25-39`), every Assumption (`:43-51`), both Rules (`:55-57`, the
  release rule when weighing a pith version range, the `git mv` rule as how files move), Not yet specified
  (`:66-72`), front matter `readme`/`design`/`verification` (`:7-9`) and `artifact-language` (`:5`).
- Passed over: `pr` (`:3`), which I did not open; `status` and `conversation-language` (`:4`, `:6`); the Tasks
  section beyond seeing that it holds only the two sign-offs.

## Conductor

- Good goal: the reason (two copies drift apart; anyone can check without writ) is read as meant, at steering.md:14-19
- Good A1: carries "check without installing writ", at steering.md:25-26
- More A1: "any work (… code, tests)" while pith has no viewpoints for code or tests and stops there; writing them first is pith's own "make an essentials file", which A1 does not name, at steering.md:25-26
- More A2: its gain "made in pith once and reaches both" is the conductor's wording the user agreed to in conversation, not marked as such, at steering.md:27-28
- More goal: the dependency fact misstates when tags are used (only with a declared version range; a bare name tracks the marketplace copy), at steering.md:43-45
- More goal: the Assumption says the docs do not document calling a dependency's skill; they name it ("one whose MCP server or skill it calls") without showing how, at steering.md:46-48
- More A2: the rn fact leaves out that rn's documents are already checked by pith through writ:up, so what moves is only rn's own checks of plan, design, task result and deliverable, at steering.md:49-50
- More goal: what becomes of /writ:pith, whether rn keeps writ, and whether the dependency on pith is a version range are relied on but not listed as open, at steering.md:64-72
- More M1: users who call /writ:pith directly are not covered, at steering.md:32-33
- More M2: result files and rn sessions already in users' repositories in today's forms, at steering.md:34-35
- More M2: the forms of the work rn checks are not stated, at steering.md:34-35
